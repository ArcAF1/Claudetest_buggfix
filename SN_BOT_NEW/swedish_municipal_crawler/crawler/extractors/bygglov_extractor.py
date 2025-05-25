import logging
import re
import requests
from io import BytesIO
import pdfplumber
from .pdf_extractor import SwedishPDFExtractor

class BygglovExtractor(SwedishPDFExtractor):
    """Specialized extractor for building permit fees (most standardized)"""
    
    def __init__(self):
        super().__init__()
        
        # Comprehensive bygglov keywords based on PBL (Plan- och bygglagen)
        self.bygglov_types = {
            'nybyggnad': {
                'keywords': ['nybyggnad', 'ny byggnad', 'uppföra', 'bygga ny'],
                'subtypes': ['enbostadshus', 'flerbostadshus', 'industribyggnad', 'komplementbyggnad']
            },
            'tillbyggnad': {
                'keywords': ['tillbyggnad', 'utbyggnad', 'påbyggnad', 'bygga till'],
                'subtypes': ['bostadshus', 'garage', 'uterum', 'altan']
            },
            'ändring': {
                'keywords': ['ändring', 'ombyggnad', 'renovering', 'ändra'],
                'subtypes': ['fasadändring', 'invändig ändring', 'ändrad användning']
            },
            'rivning': {
                'keywords': ['rivning', 'riva', 'rivningslov'],
                'subtypes': ['byggnad', 'del av byggnad']
            },
            'marklov': {
                'keywords': ['marklov', 'schaktning', 'fyllning', 'trädfällning'],
                'subtypes': []
            },
            'bygganmälan': {
                'keywords': ['bygganmälan', 'anmälan', 'anmälningspliktig'],
                'subtypes': ['attefall', 'eldstad', 'ventilation']
            }
        }
        
        # Area-based fee patterns
        self.area_patterns = [
            r'(\d+)\s*-\s*(\d+)\s*(?:kvm|m²|m2)',
            r'(?:upp till|max|högst)\s*(\d+)\s*(?:kvm|m²|m2)',
            r'(?:över|mer än|minst)\s*(\d+)\s*(?:kvm|m²|m2)',
            r'per\s*(?:kvm|m²|m2)',
            r'(\d+)\s*(?:kvm|m²|m2)'
        ]
        
        # PBB (Prisbasbelopp) patterns
        self.pbb_patterns = [
            r'(\d+(?:,\d+)?)\s*(?:x\s*)?PBB',
            r'(\d+(?:,\d+)?)\s*gånger\s*prisbasbelopp',
            r'prisbasbelopp\s*x\s*(\d+(?:,\d+)?)'
        ]
        
        # Current PBB value (updated yearly)
        self.current_pbb = 52500  # 2025 value - should be updated annually
    
    def extract_bygglov_fees_from_url(self, pdf_url):
        """Extract building permit specific fees from PDF"""
        try:
            # Use parent class method to get all fees
            all_fees = self.extract_fees_from_pdf_url(pdf_url)
            
            # Enhance with bygglov-specific parsing
            bygglov_fees = []
            
            for fee in all_fees:
                if self._is_bygglov_fee(fee):
                    enhanced_fee = self._enhance_bygglov_fee(fee)
                    bygglov_fees.append(enhanced_fee)
            
            # Also do specialized bygglov extraction
            try:
                response = requests.get(pdf_url, timeout=30, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                if response.status_code == 200:
                    pdf_bytes = BytesIO(response.content)
                    specialized_fees = self._extract_bygglov_specific(pdf_bytes, pdf_url)
                    bygglov_fees.extend(specialized_fees)
            except Exception as e:
                self.logger.error(f"Failed to download PDF for specialized extraction: {e}")
            
            return self._deduplicate_fees(bygglov_fees)
            
        except Exception as e:
            self.logger.error(f"Bygglov extraction failed: {e}")
            return []
    
    def _is_bygglov_fee(self, fee):
        """Check if fee is bygglov-related"""
        service_lower = fee.get('fee_name', '').lower()
        
        for bygglov_type, config in self.bygglov_types.items():
            if any(keyword in service_lower for keyword in config['keywords']):
                return True
        
        return fee.get('category') == 'bygglov'
    
    def _enhance_bygglov_fee(self, fee):
        """Enhance bygglov fee with specific metadata"""
        fee['bygglov_type'] = self._identify_bygglov_type(fee['fee_name'])
        fee['area_based'] = self._is_area_based(fee['fee_name'])
        fee['pbb_based'] = self._is_pbb_based(fee['fee_name'])
        
        # Extract area ranges if present
        area_info = self._extract_area_info(fee['fee_name'])
        if area_info:
            fee['area_range'] = area_info
        
        # Extract PBB information if present
        pbb_info = self._extract_pbb_info(fee.get('description', ''))
        if pbb_info:
            fee['pbb_multiplier'] = pbb_info
            fee['pbb_amount'] = pbb_info * self.current_pbb
        
        return fee
    
    def _identify_bygglov_type(self, service_text):
        """Identify specific type of building permit"""
        text_lower = service_text.lower()
        
        for bygglov_type, config in self.bygglov_types.items():
            if any(keyword in text_lower for keyword in config['keywords']):
                # Check for subtype
                for subtype in config['subtypes']:
                    if subtype in text_lower:
                        return f"{bygglov_type}_{subtype}"
                return bygglov_type
        
        return 'bygglov_allmän'
    
    def _is_area_based(self, service_text):
        """Check if fee is based on area"""
        text_lower = service_text.lower()
        area_indicators = ['kvm', 'm²', 'm2', 'bta', 'bya', 'bruttoarea', 'byggnadsarea']
        return any(indicator in text_lower for indicator in area_indicators)
    
    def _is_pbb_based(self, service_text):
        """Check if fee is based on PBB (prisbasbelopp)"""
        text_lower = service_text.lower()
        return 'pbb' in text_lower or 'prisbasbelopp' in text_lower
    
    def _extract_area_info(self, service_text):
        """Extract area range information"""
        for pattern in self.area_patterns:
            match = re.search(pattern, service_text, re.IGNORECASE)
            if match:
                if match.lastindex == 2:  # Range pattern
                    return {
                        'type': 'range',
                        'min': int(match.group(1)),
                        'max': int(match.group(2))
                    }
                elif match.lastindex == 1:  # Single value
                    return {
                        'type': 'threshold',
                        'value': int(match.group(1))
                    }
        return None
    
    def _extract_pbb_info(self, text):
        """Extract PBB multiplier from text"""
        for pattern in self.pbb_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    multiplier_str = match.group(1).replace(',', '.')
                    return float(multiplier_str)
                except ValueError:
                    continue
        return None
    
    def _extract_bygglov_specific(self, pdf_bytes, source_url):
        """Do specialized bygglov extraction"""
        fees = []
        
        try:
            pdf_bytes.seek(0)
            with pdfplumber.open(pdf_bytes) as pdf:
                for page in pdf.pages[:10]:
                    text = page.extract_text()
                    if not text:
                        continue
                    
                    # Look for bygglov fee tables
                    if self._is_bygglov_page(text):
                        # Extract structured bygglov fees
                        page_fees = self._extract_bygglov_from_page(text, source_url)
                        fees.extend(page_fees)
            
        except Exception as e:
            self.logger.error(f"Bygglov-specific extraction failed: {e}")
        
        return fees
    
    def _is_bygglov_page(self, text):
        """Check if page contains bygglov information"""
        text_lower = text.lower()
        bygglov_indicators = [
            'bygglovstaxa', 'byggnadsnämnden', 'plan- och bygglagen',
            'pbl', 'bygglovsavgift', 'bygganmälan', 'handläggningsavgift bygglov'
        ]
        return any(indicator in text_lower for indicator in bygglov_indicators)
    
    def _extract_bygglov_from_page(self, text, source_url):
        """Extract bygglov fees from page text"""
        fees = []
        
        # Enhanced patterns for bygglov fees
        bygglov_patterns = [
            # Pattern: "Nybyggnad villa: 25 000 kr"
            r'(nybyggnad\s+\w+):\s*(\d{1,3}(?:\s\d{3})*)\s*kr',
            # Pattern: "Bygglov för enbostadshus 15 000 kr"
            r'(bygglov\s+för\s+\w+)\s*(\d{1,3}(?:\s\d{3})*)\s*kr',
            # Pattern: "Tillbyggnad 0-50 kvm 8 000 kr"
            r'(tillbyggnad\s+\d+\s*-\s*\d+\s*kvm)\s*(\d{1,3}(?:\s\d{3})*)\s*kr',
            # Pattern with PBB
            r'(bygglov\s+\w+)\s*(\d+(?:,\d+)?)\s*x\s*PBB',
            # Pattern: "Handläggningsavgift nybyggnad: 12 500 kr"
            r'(handläggningsavgift\s+\w+):\s*(\d{1,3}(?:\s\d{3})*)\s*kr',
            # Pattern: "Enbostadshus upp till 120 kvm: 18 000 kr"
            r'(enbostadshus\s+upp\s+till\s+\d+\s+kvm):\s*(\d{1,3}(?:\s\d{3})*)\s*kr',
            # Pattern: "Attefallshus: 5 000 kr"
            r'(attefallshus|komplementbyggnad):\s*(\d{1,3}(?:\s\d{3})*)\s*kr',
            # Pattern: "Rivningslov: 8 500 kr"
            r'(rivningslov|rivning):\s*(\d{1,3}(?:\s\d{3})*)\s*kr'
        ]
        
        for pattern in bygglov_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                service = match.group(1)
                
                # Check if PBB-based
                if 'PBB' in pattern:
                    pbb_multiplier = float(match.group(2).replace(',', '.'))
                    amount = pbb_multiplier * self.current_pbb
                    pbb_based = True
                else:
                    amount = self._parse_swedish_currency(match.group(2))
                    pbb_based = False
                
                if amount and amount >= 100:  # Minimum reasonable bygglov fee
                    fee = {
                        'fee_name': self._clean_swedish_text(service),
                        'amount': amount,
                        'currency': 'SEK',
                        'category': 'bygglov',
                        'bygglov_type': self._identify_bygglov_type(service),
                        'area_based': self._is_area_based(service),
                        'pbb_based': pbb_based,
                        'source_url': source_url,
                        'source_type': 'PDF',
                        'extraction_method': 'bygglov_pattern',
                        'confidence': 0.95
                    }
                    
                    # Add area information if present
                    area_info = self._extract_area_info(service)
                    if area_info:
                        fee['area_range'] = area_info
                    
                    # Add PBB information if applicable
                    if pbb_based:
                        fee['pbb_multiplier'] = pbb_multiplier
                        fee['pbb_amount'] = amount
                    
                    fees.append(fee)
        
        # Also look for table-based bygglov fees
        table_fees = self._extract_bygglov_tables(text, source_url)
        fees.extend(table_fees)
        
        return fees
    
    def _extract_bygglov_tables(self, text, source_url):
        """Extract bygglov fees from table-like structures in text"""
        fees = []
        
        # Look for table patterns with multiple fees
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Check if line looks like a table row with bygglov info
            if self._is_bygglov_table_row(line):
                # Try to extract fee from this line
                fee_data = self._parse_bygglov_table_row(line, source_url)
                if fee_data:
                    fees.append(fee_data)
        
        return fees
    
    def _is_bygglov_table_row(self, line):
        """Check if line looks like a bygglov table row"""
        line_lower = line.lower()
        
        # Must contain bygglov-related keyword and amount
        has_bygglov_keyword = any(keyword in line_lower for keyword_group in self.bygglov_types.values() 
                                 for keyword in keyword_group['keywords'])
        has_amount = re.search(r'\d{1,3}(?:\s\d{3})*\s*kr', line)
        
        return has_bygglov_keyword and has_amount
    
    def _parse_bygglov_table_row(self, line, source_url):
        """Parse a single table row for bygglov fee"""
        try:
            # Extract amount
            amount_match = re.search(r'(\d{1,3}(?:\s\d{3})*)\s*kr', line)
            if not amount_match:
                return None
            
            amount = self._parse_swedish_currency(amount_match.group(1))
            if not amount or amount < 100:
                return None
            
            # Extract service description (everything before the amount)
            service_text = line[:amount_match.start()].strip()
            
            # Clean up common table separators
            service_text = re.sub(r'[\.]{3,}', ' ', service_text)  # Remove dot leaders
            service_text = re.sub(r'[-]{3,}', ' ', service_text)   # Remove dash separators
            service_text = re.sub(r'\s+', ' ', service_text).strip()
            
            if len(service_text) < 5:  # Too short to be meaningful
                return None
            
            fee = {
                'fee_name': self._clean_swedish_text(service_text),
                'amount': amount,
                'currency': 'SEK',
                'category': 'bygglov',
                'bygglov_type': self._identify_bygglov_type(service_text),
                'area_based': self._is_area_based(service_text),
                'pbb_based': self._is_pbb_based(line),
                'source_url': source_url,
                'source_type': 'PDF',
                'extraction_method': 'bygglov_table_row',
                'confidence': 0.85
            }
            
            # Add area information if present
            area_info = self._extract_area_info(service_text)
            if area_info:
                fee['area_range'] = area_info
            
            return fee
            
        except Exception as e:
            self.logger.error(f"Failed to parse bygglov table row: {e}")
            return None
    
    def get_bygglov_statistics(self, fees):
        """Get statistics about extracted bygglov fees"""
        if not fees:
            return {}
        
        bygglov_fees = [fee for fee in fees if fee.get('category') == 'bygglov']
        
        if not bygglov_fees:
            return {}
        
        stats = {
            'total_bygglov_fees': len(bygglov_fees),
            'types': {},
            'area_based_count': 0,
            'pbb_based_count': 0,
            'amount_range': {
                'min': min(fee['amount'] for fee in bygglov_fees),
                'max': max(fee['amount'] for fee in bygglov_fees),
                'avg': sum(fee['amount'] for fee in bygglov_fees) / len(bygglov_fees)
            }
        }
        
        # Count by type
        for fee in bygglov_fees:
            bygglov_type = fee.get('bygglov_type', 'unknown')
            stats['types'][bygglov_type] = stats['types'].get(bygglov_type, 0) + 1
            
            if fee.get('area_based'):
                stats['area_based_count'] += 1
            
            if fee.get('pbb_based'):
                stats['pbb_based_count'] += 1
        
        return stats 