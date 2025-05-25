import camelot
import pdfplumber
import pandas as pd
import re
from io import BytesIO
import requests
import tempfile
import os
from concurrent.futures import ThreadPoolExecutor
import hashlib
import logging

class SwedishPDFExtractor:
    """Extractor for PDF documents containing Swedish municipal fees"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Optimized Camelot settings for Swedish municipal PDFs
        self.camelot_configs = {
            'default': {
                'flavor': 'lattice',
                'edge_tol': 50,
                'row_tol': 10,
                'column_tol': 5
            },
            'stream': {
                'flavor': 'stream',
                'edge_tol': 50,
                'row_tol': 10,
                'column_tol': 5
            }
        }
        
        # Swedish table headers (from 100 municipality analysis)
        self.fee_table_headers = [
            r'åtgärd.*avgift',
            r'verksamhet.*taxa',
            r'typ.*ärende.*avgift',
            r'handläggning.*kostnad',
            r'prövning.*avgift',
            r'service.*pris',
            r'tjänst.*taxa',
            r'beskrivning.*kronor',
            r'ärende.*belopp',
            r'handläggningsavgift',
            r'timavgift',
            r'grundavgift'
        ]
        
        # PDF cache to avoid re-downloading
        self.pdf_cache_dir = 'data/cache/pdfs'
        os.makedirs(self.pdf_cache_dir, exist_ok=True)
    
    def extract_fees_from_pdf_url(self, pdf_url):
        """Extract fees from PDF URL with caching"""
        try:
            # Check cache first
            pdf_hash = hashlib.md5(pdf_url.encode()).hexdigest()
            cache_path = os.path.join(self.pdf_cache_dir, f"{pdf_hash}.pdf")
            
            if os.path.exists(cache_path):
                self.logger.info(f"Using cached PDF: {pdf_url}")
                with open(cache_path, 'rb') as f:
                    pdf_bytes = BytesIO(f.read())
            else:
                # Download PDF
                response = requests.get(pdf_url, timeout=30, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                response.raise_for_status()
                
                if len(response.content) > 10 * 1024 * 1024:  # Skip PDFs > 10MB
                    self.logger.warning(f"PDF too large: {pdf_url}")
                    return []
                
                # Save to cache
                with open(cache_path, 'wb') as f:
                    f.write(response.content)
                
                pdf_bytes = BytesIO(response.content)
            
            # Try multiple extraction methods
            all_fees = []
            
            # Method 1: Camelot lattice (best for tables with borders)
            lattice_fees = self._extract_with_camelot(pdf_bytes, pdf_url, 'default')
            all_fees.extend(lattice_fees)
            
            # Method 2: Camelot stream (for tables without borders)
            if not lattice_fees:
                stream_fees = self._extract_with_camelot(pdf_bytes, pdf_url, 'stream')
                all_fees.extend(stream_fees)
            
            # Method 3: pdfplumber (fallback for text extraction)
            if not all_fees:
                text_fees = self._extract_with_pdfplumber(pdf_bytes, pdf_url)
                all_fees.extend(text_fees)
            
            # Deduplicate fees
            return self._deduplicate_fees(all_fees)
            
        except Exception as e:
            self.logger.error(f"PDF extraction failed for {pdf_url}: {str(e)}")
            return []
    
    def _extract_with_camelot(self, pdf_bytes, source_url, config_name='default'):
        """Extract structured tables using Camelot"""
        try:
            # Reset BytesIO position
            pdf_bytes.seek(0)
            
            # Save temporarily for Camelot (requires file path)
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                tmp_file.write(pdf_bytes.read())
                tmp_path = tmp_file.name
            
            # Get config
            config = self.camelot_configs[config_name]
            
            # Extract tables from first 15 pages
            tables = camelot.read_pdf(tmp_path, pages='1-15', **config)
            
            extracted_fees = []
            for table in tables:
                if self._is_fee_table(table.df):
                    fees = self._parse_swedish_fee_table(table.df, source_url)
                    extracted_fees.extend(fees)
            
            # Cleanup
            os.unlink(tmp_path)
            
            return extracted_fees
            
        except Exception as e:
            self.logger.error(f"Camelot extraction failed: {str(e)}")
            return []
    
    def _extract_with_pdfplumber(self, pdf_bytes, source_url):
        """Extract from PDF text using pdfplumber with enhanced parsing"""
        try:
            pdf_bytes.seek(0)
            
            with pdfplumber.open(pdf_bytes) as pdf:
                all_text = ""
                all_fees = []
                
                # Process first 15 pages
                for page_num, page in enumerate(pdf.pages[:15], 1):
                    # Try to extract tables first
                    tables = page.extract_tables()
                    for table in tables:
                        if table and self._is_fee_table_list(table):
                            table_fees = self._parse_table_list(table, source_url)
                            all_fees.extend(table_fees)
                    
                    # Also extract text for pattern matching
                    page_text = page.extract_text()
                    if page_text:
                        all_text += f"\n--- Page {page_num} ---\n{page_text}\n"
            
            # Extract fees from text using Swedish patterns
            text_fees = self._extract_fees_from_text(all_text, source_url)
            all_fees.extend(text_fees)
            
            return self._deduplicate_fees(all_fees)
            
        except Exception as e:
            self.logger.error(f"PDFplumber extraction failed: {str(e)}")
            return []
    
    def _is_fee_table(self, dataframe):
        """Determine if DataFrame contains Swedish fee information"""
        if dataframe.empty or len(dataframe.columns) < 2:
            return False
        
        # Check headers and first rows for Swedish fee keywords
        header_text = ' '.join(str(col).lower() for col in dataframe.columns)
        first_rows_text = ' '.join(str(val).lower() for _, row in dataframe.head(3).iterrows() 
                                  for val in row)
        
        combined_text = header_text + ' ' + first_rows_text
        
        # Check for fee patterns
        for pattern in self.fee_table_headers:
            if re.search(pattern, combined_text, re.IGNORECASE):
                return True
        
        # Check for currency amounts
        currency_pattern = r'\d{1,3}(?:\s\d{3})*(?:,\d{1,2})?\s*kr'
        if re.search(currency_pattern, combined_text):
            return True
        
        return False
    
    def _is_fee_table_list(self, table_list):
        """Check if a table list contains fee information"""
        if not table_list or len(table_list) < 2:
            return False
        
        # Convert to string for analysis
        table_text = ' '.join(str(cell) for row in table_list for cell in row if cell)
        
        # Check for fee indicators
        return any(indicator in table_text.lower() 
                  for indicator in ['avgift', 'taxa', 'kronor', 'kr', 'pris'])
    
    def _parse_swedish_fee_table(self, df, source_url):
        """Parse Swedish fee table into structured data"""
        fees = []
        
        # Identify amount column
        amount_col_idx = self._find_amount_column(df)
        if amount_col_idx is None:
            return fees
        
        # Identify service column (usually first text column)
        service_col_idx = 0
        for idx, col in enumerate(df.columns):
            if idx != amount_col_idx and df[col].dtype == 'object':
                service_col_idx = idx
                break
        
        for index, row in df.iterrows():
            if index == 0:  # Skip header row
                continue
            
            try:
                service_text = str(row.iloc[service_col_idx])
                amount_text = str(row.iloc[amount_col_idx])
                
                amount = self._extract_amount_from_text(amount_text)
                if amount and 50 <= amount <= 100000:
                    fee = {
                        'fee_name': self._clean_swedish_text(service_text),
                        'amount': amount,
                        'currency': 'SEK',
                        'category': self._categorize_service(service_text),
                        'source_url': source_url,
                        'source_type': 'PDF',
                        'extraction_method': 'camelot_table',
                        'confidence': 0.9,
                        'description': f"{service_text} - {amount_text}"
                    }
                    fees.append(fee)
            except:
                continue
        
        return fees
    
    def _parse_table_list(self, table_list, source_url):
        """Parse table from list format (pdfplumber)"""
        fees = []
        
        for row in table_list[1:]:  # Skip header
            if not row or all(not cell for cell in row):
                continue
            
            # Find amount in row
            amount = None
            service = None
            
            for cell in row:
                if cell:
                    cell_amount = self._extract_amount_from_text(str(cell))
                    if cell_amount:
                        amount = cell_amount
                    elif not service and len(str(cell)) > 5:
                        service = str(cell)
            
            if amount and service:
                fee = {
                    'fee_name': self._clean_swedish_text(service),
                    'amount': amount,
                    'currency': 'SEK',
                    'category': self._categorize_service(service),
                    'source_url': source_url,
                    'source_type': 'PDF',
                    'extraction_method': 'pdfplumber_table',
                    'confidence': 0.8
                }
                fees.append(fee)
        
        return fees
    
    def _find_amount_column(self, df):
        """Find column containing amounts"""
        for idx, col in enumerate(df.columns):
            # Check if column contains Swedish currency
            col_text = ' '.join(str(val) for val in df[col].dropna())
            if re.search(r'\d{1,3}(?:\s\d{3})*(?:,\d{1,2})?\s*kr', col_text):
                return idx
        return None
    
    def _extract_fees_from_text(self, text, source_url):
        """Extract fees from plain text using Swedish patterns"""
        fees = []
        
        # Enhanced Swedish currency patterns
        currency_patterns = [
            # Standard format: "1 250 kr" or "1 250,50 kr/timme"
            r'(\d{1,3}(?:\s\d{3})*(?:,\d{1,2})?)\s*kr(?:/(\w+))?',
            # With kronor: "1 250 kronor"
            r'(\d{1,3}(?:\s\d{3})*)\s*kronor',
            # SEK format: "SEK 1 250,50"
            r'SEK\s*(\d{1,3}(?:\s\d{3})*(?:,\d{1,2})?)',
            # Alternative format: "1.250,50 kr"
            r'(\d{1,3}(?:\.\d{3})*(?:,\d{1,2})?)\s*kr',
            # Format with colon: "Avgift: 1 250 kr"
            r'[Aa]vgift:?\s*(\d{1,3}(?:\s\d{3})*(?:,\d{1,2})?)\s*kr',
            # Format with equals: "Taxa = 1 250 kr"
            r'[Tt]axa\s*=\s*(\d{1,3}(?:\s\d{3})*(?:,\d{1,2})?)\s*kr'
        ]
        
        for pattern in currency_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                amount = self._parse_swedish_currency(match.group(1))
                
                if amount and 50 <= amount <= 100000:  # Reasonable fee range
                    # Get context around the match
                    start = max(0, match.start() - 150)
                    end = min(len(text), match.end() + 150)
                    context = text[start:end].strip()
                    
                    # Clean context
                    context_lines = context.split('\n')
                    context_clean = ' '.join(line.strip() for line in context_lines if line.strip())
                    
                    fee = {
                        'fee_name': self._extract_service_from_context(context_clean, match.group(0)),
                        'amount': amount,
                        'currency': 'SEK',
                        'category': self._categorize_service(context_clean),
                        'source_url': source_url,
                        'source_type': 'PDF',
                        'extraction_method': 'text_pattern',
                        'confidence': 0.7,
                        'description': context_clean[:200]
                    }
                    fees.append(fee)
        
        return fees
    
    def _parse_swedish_currency(self, amount_str):
        """Parse Swedish currency format to float"""
        if not amount_str:
            return None
        
        # Handle different formats
        # Remove spaces (thousand separators)
        cleaned = amount_str.replace(' ', '')
        # Replace dot thousand separators
        cleaned = cleaned.replace('.', '')
        # Convert comma decimal separator to dot
        cleaned = cleaned.replace(',', '.')
        
        try:
            return float(cleaned)
        except:
            return None
    
    def _extract_amount_from_text(self, text):
        """Extract amount from text string"""
        if not text:
            return None
        
        # Look for Swedish currency patterns
        patterns = [
            r'(\d{1,3}(?:\s\d{3})*(?:,\d{1,2})?)\s*kr',
            r'(\d{1,3}(?:\.\d{3})*(?:,\d{1,2})?)\s*kr',
            r'(\d+(?:,\d+)?)\s*kr'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, str(text), re.IGNORECASE)
            if match:
                return self._parse_swedish_currency(match.group(1))
        
        return None
    
    def _categorize_service(self, text):
        """Categorize service based on Swedish keywords"""
        text_lower = text.lower()
        
        # Comprehensive category mapping
        categories = {
            'bygglov': [
                'bygglov', 'bygganmälan', 'startbesked', 'slutbesked',
                'kontrollansvarig', 'nybyggnad', 'tillbyggnad', 'ändring',
                'rivning', 'marklov', 'byggnadsnämnd', 'bta', 'bya'
            ],
            'livsmedel': [
                'livsmedel', 'restaurang', 'serveringstillstånd', 'alkohol',
                'livsmedelskontroll', 'sanitet', 'hygien', 'kök', 'servering'
            ],
            'miljö': [
                'miljö', 'miljötillsyn', 'kemikalie', 'avlopp', 'utsläpp',
                'miljöfarlig', 'föroreningar', 'avfall', 'återvinning'
            ],
            'näringsverksamhet': [
                'näringsverksamhet', 'handelstillstånd', 'företag', 'handel',
                'försäljning', 'näringstillstånd', 'verksamhet'
            ],
            'socialtjänst': [
                'hemtjänst', 'äldreomsorg', 'omsorg', 'färdtjänst',
                'trygghetslarm', 'dagverksamhet', 'korttidsboende'
            ],
            'skola': [
                'förskola', 'fritids', 'pedagogisk', 'barnomsorg',
                'skolskjuts', 'musikskola', 'kulturskola'
            ],
            'vatten': [
                'vatten', 'va-', 'anslutning', 'servis', 'mätare',
                'vattenavgift', 'spillvatten', 'dagvatten'
            ]
        }
        
        # Score each category
        category_scores = {}
        for category, keywords in categories.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                category_scores[category] = score
        
        # Return category with highest score
        if category_scores:
            return max(category_scores, key=category_scores.get)
        
        return 'övrigt'
    
    def _clean_swedish_text(self, text):
        """Clean and normalize Swedish text"""
        if not text or pd.isna(text):
            return ""
        
        # Convert to string
        text = str(text)
        
        # Remove extra whitespace and normalize
        cleaned = re.sub(r'\s+', ' ', text).strip()
        
        # Remove common PDF artifacts
        cleaned = re.sub(r'[●•▪▫◦‣⁃]', '', cleaned)  # Bullet points
        cleaned = re.sub(r'\.{3,}', '', cleaned)  # Multiple dots
        cleaned = re.sub(r'-{3,}', '', cleaned)  # Multiple dashes
        cleaned = re.sub(r'_{3,}', '', cleaned)  # Multiple underscores
        
        # Remove page numbers and headers
        cleaned = re.sub(r'^\d+\s*$', '', cleaned)  # Just page numbers
        cleaned = re.sub(r'^Sida \d+.*$', '', cleaned, flags=re.MULTILINE)
        
        # Preserve Swedish characters
        cleaned = re.sub(r'[^\w\såäöÅÄÖ\-\(\)\.,/:=]', ' ', cleaned)
        
        # Remove redundant spaces
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned[:200]  # Limit length
    
    def _extract_service_from_context(self, context, amount_match):
        """Extract service description from context"""
        # Remove the amount match from context
        context_without_amount = context.replace(amount_match, '')
        
        # Split into sentences or lines
        lines = re.split(r'[.\n]', context_without_amount)
        
        # Find the most relevant line
        for line in lines:
            line = line.strip()
            if len(line) > 10 and not re.search(r'^\d+$', line):
                # Check if line contains service keywords
                service_keywords = ['avgift', 'taxa', 'handläggning', 'prövning', 'ansökan']
                if any(keyword in line.lower() for keyword in service_keywords):
                    return self._clean_swedish_text(line)
        
        # Fallback: use first non-empty line
        for line in lines:
            line = line.strip()
            if len(line) > 10:
                return self._clean_swedish_text(line)
        
        return self._clean_swedish_text(context_without_amount[:100])
    
    def _deduplicate_fees(self, fees):
        """Remove duplicate fees based on service and amount"""
        seen = set()
        unique_fees = []
        
        for fee in fees:
            # Create unique key
            key = f"{fee.get('fee_name', '')[:50]}_{fee.get('amount', 0)}"
            
            if key not in seen:
                seen.add(key)
                unique_fees.append(fee)
            else:
                # If duplicate, keep the one with higher confidence
                for idx, existing_fee in enumerate(unique_fees):
                    existing_key = f"{existing_fee.get('fee_name', '')[:50]}_{existing_fee.get('amount', 0)}"
                    if existing_key == key and fee.get('confidence', 0) > existing_fee.get('confidence', 0):
                        unique_fees[idx] = fee
                        break
        
        return unique_fees 