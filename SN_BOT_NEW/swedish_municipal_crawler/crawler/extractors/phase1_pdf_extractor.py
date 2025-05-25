#!/usr/bin/env python3
"""
Phase 1 PDF Extractor
Specialized PDF extraction for the three Phase 1 data points:
1. Timtaxan för livsmedelskontroll (Hourly rate for food control)
2. Debiteringsmodell för livsmedelskontroll (Billing model: prepaid vs post-paid)
3. Timtaxan för bygglov (Hourly rate for building permits)
"""

import re
import logging
import tempfile
import os
from pathlib import Path
from typing import Dict, Optional, List, Tuple
from datetime import datetime

try:
    import camelot
    import pdfplumber
    import pandas as pd
    CAMELOT_AVAILABLE = True
except ImportError:
    CAMELOT_AVAILABLE = False
    logging.warning("Camelot or pdfplumber not available. PDF extraction will be limited.")

from .phase1_extractors import Phase1ExtractorManager

class Phase1PDFExtractor:
    """Phase 1 focused PDF extractor for Swedish municipal fee documents"""
    
    def __init__(self, cache_dir: str = "data/cache/pdfs"):
        self.logger = logging.getLogger(__name__)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Phase 1 text extractors
        self.phase1_manager = Phase1ExtractorManager()
        
        # Phase 1 specific table headers to look for
        self.phase1_table_headers = [
            # Food control headers
            'livsmedelskontroll', 'livsmedelstillsyn', 'offentlig kontroll',
            'timtaxa', 'timavgift', 'kr/timme', 'avgift per timme',
            'kontrollavgift', 'livsmedelsinspektion',
            
            # Building permit headers
            'bygglov', 'plan- och bygglov', 'byggnadsnämnd',
            'handläggningsavgift', 'PBL', 'plan- och bygglagen',
            'bygglovshandläggning', 'bygglovstaxa',
            
            # Billing model headers
            'debitering', 'förskott', 'efterhand', 'betalning',
            'fakturering', 'förskottsbetalning', 'efterhandsdebitering'
        ]
        
        # Phase 1 specific section titles
        self.phase1_sections = [
            r'livsmedelskontroll',
            r'livsmedelstillsyn',
            r'offentlig.*?kontroll.*?livsmedel',
            r'bygglov',
            r'plan.*?och.*?bygglov',
            r'byggnadsnämnd',
            r'taxa.*?livsmedel',
            r'taxa.*?bygglov',
            r'avgifter.*?livsmedel',
            r'avgifter.*?bygglov'
        ]
    
    def extract_phase1_from_pdf(self, pdf_path: str, source_url: str = "") -> Dict:
        """Extract Phase 1 data from PDF using multiple methods"""
        self.logger.info(f"Extracting Phase 1 data from PDF: {pdf_path}")
        
        results = {
            'source_url': source_url,
            'source_type': 'PDF',
            'extraction_date': datetime.now().isoformat(),
            'extraction_method': 'phase1_pdf_combined',
            'data_completeness': 0,
            'validation_warnings': []
        }
        
        if not CAMELOT_AVAILABLE:
            self.logger.warning("PDF extraction libraries not available")
            return results
        
        try:
            # Method 1: Table extraction with Camelot
            table_results = self._extract_from_tables(pdf_path, source_url)
            if table_results:
                results.update(table_results)
            
            # Method 2: Text extraction with pdfplumber
            text_results = self._extract_from_text(pdf_path, source_url)
            if text_results:
                # Merge results, preferring table extraction for conflicts
                for key, value in text_results.items():
                    if key not in results or not results[key]:
                        results[key] = value
            
            # Calculate data completeness
            phase1_fields = ['timtaxa_livsmedel', 'debitering_livsmedel', 'timtaxa_bygglov']
            found_fields = sum(1 for field in phase1_fields if results.get(field))
            results['data_completeness'] = found_fields / len(phase1_fields)
            
            # Calculate overall confidence
            confidences = []
            for field in phase1_fields:
                if results.get(field):
                    # Look for confidence in nested data
                    if isinstance(results.get(field), dict) and 'confidence' in results[field]:
                        confidences.append(results[field]['confidence'])
                    elif results.get('confidence'):
                        confidences.append(results['confidence'])
            
            if confidences:
                results['confidence'] = sum(confidences) / len(confidences)
            else:
                results['confidence'] = 0
            
            self.logger.info(f"Phase 1 PDF extraction completed: {results['data_completeness']:.1%} complete")
            
        except Exception as e:
            self.logger.error(f"Error extracting from PDF {pdf_path}: {e}")
            results['validation_warnings'].append(f"PDF extraction error: {str(e)}")
        
        return results
    
    def _extract_from_tables(self, pdf_path: str, source_url: str) -> Dict:
        """Extract Phase 1 data from PDF tables using Camelot"""
        results = {}
        
        try:
            # Try lattice method first (for tables with borders)
            tables = camelot.read_pdf(pdf_path, pages='all', flavor='lattice')
            
            if len(tables) == 0:
                # Fallback to stream method (for tables without borders)
                tables = camelot.read_pdf(pdf_path, pages='all', flavor='stream')
            
            self.logger.info(f"Found {len(tables)} tables in PDF")
            
            for i, table in enumerate(tables):
                df = table.df
                
                # Check if table contains Phase 1 relevant data
                if self._is_phase1_relevant_table(df):
                    self.logger.info(f"Processing Phase 1 relevant table {i+1}")
                    
                    # Extract Phase 1 data from this table
                    table_results = self._extract_phase1_from_table(df, source_url)
                    if table_results:
                        results.update(table_results)
        
        except Exception as e:
            self.logger.debug(f"Table extraction failed: {e}")
        
        return results
    
    def _extract_from_text(self, pdf_path: str, source_url: str) -> Dict:
        """Extract Phase 1 data from PDF text using pdfplumber"""
        results = {}
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                full_text = ""
                
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        full_text += page_text + "\n"
                
                # Use Phase 1 text extractors on the full text
                if full_text.strip():
                    text_results = self.phase1_manager.extract_all_phase1_data(full_text, source_url)
                    if text_results:
                        results.update(text_results)
        
        except Exception as e:
            self.logger.debug(f"Text extraction failed: {e}")
        
        return results
    
    def _is_phase1_relevant_table(self, df: pd.DataFrame) -> bool:
        """Check if table contains Phase 1 relevant data"""
        # Convert all table content to lowercase string
        table_text = df.to_string().lower()
        
        # Check for Phase 1 keywords
        for header in self.phase1_table_headers:
            if header.lower() in table_text:
                return True
        
        # Check for specific patterns
        if re.search(r'\d{3,4}.*?kr.*?timme', table_text):
            return True
        
        if re.search(r'förskott|efterhand', table_text):
            return True
        
        return False
    
    def _extract_phase1_from_table(self, df: pd.DataFrame, source_url: str) -> Dict:
        """Extract Phase 1 data from a specific table"""
        results = {}
        
        # Convert table to text for pattern matching
        table_text = df.to_string()
        
        # Try to extract using text patterns
        text_results = self.phase1_manager.extract_all_phase1_data(table_text, source_url)
        if text_results:
            results.update(text_results)
        
        # Also try structured table extraction
        structured_results = self._extract_structured_table_data(df, source_url)
        if structured_results:
            # Merge with preference for structured data
            for key, value in structured_results.items():
                if key not in results or not results[key]:
                    results[key] = value
        
        return results
    
    def _extract_structured_table_data(self, df: pd.DataFrame, source_url: str) -> Dict:
        """Extract Phase 1 data from structured table format"""
        results = {}
        
        try:
            # Look for rows containing Phase 1 keywords
            for index, row in df.iterrows():
                row_text = ' '.join(str(cell).lower() for cell in row if pd.notna(cell))
                
                # Check for food control hourly rate
                if any(keyword in row_text for keyword in ['livsmedelskontroll', 'livsmedel', 'offentlig kontroll']):
                    amount = self._extract_amount_from_row(row)
                    if amount and 800 <= amount <= 2000:
                        results['timtaxa_livsmedel'] = amount
                        results['extraction_method'] = 'table_structured'
                
                # Check for building permit hourly rate
                if any(keyword in row_text for keyword in ['bygglov', 'plan- och bygg', 'pbl']):
                    amount = self._extract_amount_from_row(row)
                    if amount and 800 <= amount <= 2000:
                        results['timtaxa_bygglov'] = amount
                        results['extraction_method'] = 'table_structured'
                
                # Check for billing model
                if 'förskott' in row_text:
                    results['debitering_livsmedel'] = 'förskott'
                    results['extraction_method'] = 'table_structured'
                elif 'efterhand' in row_text:
                    results['debitering_livsmedel'] = 'efterhand'
                    results['extraction_method'] = 'table_structured'
        
        except Exception as e:
            self.logger.debug(f"Structured table extraction failed: {e}")
        
        return results
    
    def _extract_amount_from_row(self, row: pd.Series) -> Optional[int]:
        """Extract amount from table row"""
        for cell in row:
            if pd.isna(cell):
                continue
            
            cell_str = str(cell)
            
            # Look for amount patterns
            amount_match = re.search(r'(\d{3,4})', cell_str)
            if amount_match:
                try:
                    amount = int(amount_match.group(1))
                    if 800 <= amount <= 2000:  # Reasonable range for hourly rates
                        return amount
                except ValueError:
                    continue
        
        return None
    
    def is_phase1_relevant_pdf(self, pdf_path: str) -> bool:
        """Quick check if PDF is likely to contain Phase 1 data"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Check first few pages for Phase 1 indicators
                pages_to_check = min(3, len(pdf.pages))
                
                for i in range(pages_to_check):
                    page_text = pdf.pages[i].extract_text()
                    if page_text:
                        page_text_lower = page_text.lower()
                        
                        # Check for Phase 1 section titles
                        for section in self.phase1_sections:
                            if re.search(section, page_text_lower):
                                return True
                        
                        # Check for specific Phase 1 patterns
                        if re.search(r'\d{3,4}\s*kr.*?timme', page_text_lower):
                            return True
                        
                        if re.search(r'förskott|efterhand', page_text_lower):
                            return True
            
            return False
            
        except Exception as e:
            self.logger.debug(f"Error checking PDF relevance: {e}")
            return True  # Assume relevant if we can't check
    
    def extract_phase1_from_url(self, pdf_url: str) -> Dict:
        """Download and extract Phase 1 data from PDF URL"""
        import requests
        import hashlib
        
        # Create cache filename
        url_hash = hashlib.md5(pdf_url.encode()).hexdigest()
        cache_file = self.cache_dir / f"phase1_{url_hash}.pdf"
        
        try:
            # Download PDF if not cached
            if not cache_file.exists():
                self.logger.info(f"Downloading PDF: {pdf_url}")
                response = requests.get(pdf_url, timeout=30)
                response.raise_for_status()
                
                with open(cache_file, 'wb') as f:
                    f.write(response.content)
            
            # Extract Phase 1 data
            return self.extract_phase1_from_pdf(str(cache_file), pdf_url)
            
        except Exception as e:
            self.logger.error(f"Error processing PDF from URL {pdf_url}: {e}")
            return {
                'source_url': pdf_url,
                'source_type': 'PDF',
                'extraction_date': datetime.now().isoformat(),
                'validation_warnings': [f"PDF processing error: {str(e)}"],
                'data_completeness': 0,
                'confidence': 0
            } 