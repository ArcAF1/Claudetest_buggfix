#!/usr/bin/env python3
"""
Phase 1 Specific Extractors
Extracts ONLY the three required data points:
1. Timtaxan för livsmedelskontroll (Hourly rate for food control)
2. Debiteringsmodell för livsmedelskontroll (Billing model: prepaid vs post-paid)
3. Timtaxan för bygglov (Hourly rate for building permits)
"""

import re
import logging
import signal
from typing import Dict, Optional, List
from datetime import datetime

class TimeoutError(Exception):
    """Custom timeout exception"""
    pass

def timeout_handler(signum, frame):
    """Handle timeout signal"""
    raise TimeoutError("Extraction timeout")

class LivsmedelTimtaxaExtractor:
    """Extract ONLY hourly rate for food control"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Simplified patterns to prevent hanging - FIXED to handle Swedish number formatting
        self.patterns = [
            # Direct patterns (simplified, no DOTALL) - Updated to handle spaced numbers
            r'livsmedelskontroll.*?(\d{1,2}\s?\d{3}|\d{3,4})\s*kr.*?timme',
            r'timtaxa.*?livsmedel.*?(\d{1,2}\s?\d{3}|\d{3,4})\s*kr',
            r'livsmedel.*?timtaxa.*?(\d{1,2}\s?\d{3}|\d{3,4})\s*kr',
            r'kontroll.*?livsmedel.*?(\d{1,2}\s?\d{3}|\d{3,4})\s*kr.*?timme',
            r'offentlig.*?kontroll.*?livsmedel.*?(\d{1,2}\s?\d{3}|\d{3,4})\s*kr',
            
            # Simple patterns - Updated to handle spaced numbers
            r'avgift.*?per.*?timme.*?(\d{1,2}\s?\d{3}|\d{3,4})\s*kr',
            r'(\d{1,2}\s?\d{3}|\d{3,4})\s*kr.*?per.*?timme',
            r'handläggning.*?(\d{1,2}\s?\d{3}|\d{3,4})\s*kr.*?timme',
            r'timavgift.*?(\d{1,2}\s?\d{3}|\d{3,4})\s*kr',
            
            # Table patterns (simplified) - Updated to handle spaced numbers
            r'livsmedelskontroll.*?(\d{1,2}\s?\d{3}|\d{3,4})',
            r'livsmedelsinspektion.*?(\d{1,2}\s?\d{3}|\d{3,4})\s*kr',
            r'kontrollavgift.*?livsmedel.*?(\d{1,2}\s?\d{3}|\d{3,4})',
        ]
        
        # Context validation patterns (simplified)
        self.context_patterns = [
            r'livsmedelskontroll',
            r'livsmedelstillsyn',
            r'offentlig.*?kontroll.*?livsmedel',
            r'kontrollavgift.*?livsmedel',
            r'livsmedelsinspektion'
        ]
    
    def extract(self, text: str, source_url: str = "") -> Optional[Dict]:
        """Extract food control hourly rate from text with timeout protection"""
        if not text:
            return None
        
        # Set timeout to prevent hanging
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(15)  # Increased from 10 to 15 seconds for more thorough extraction
        
        try:
            text_clean = self._clean_text(text)
            
            # Limit text size to prevent excessive processing
            if len(text_clean) > 100000:  # Increased from 50KB to 100KB for more thorough processing
                text_clean = text_clean[:100000]
            
            # Try each pattern
            for pattern in self.patterns:
                try:
                    matches = re.finditer(pattern, text_clean, re.IGNORECASE)
                    
                    for match in matches:
                        amount_str = match.group(1)
                        amount = int(amount_str.replace(' ', ''))
                        
                        # Validate amount range
                        if 800 <= amount <= 2000:
                            # Quick context validation
                            context = self._extract_context(text_clean, match.start(), match.end())
                            if self._validate_context(context):
                                confidence = self._calculate_confidence(pattern, context, amount)
                                
                                self.logger.info(f"Found food control hourly rate: {amount} kr/timme (confidence: {confidence:.2f})")
                                
                                return {
                                    'timtaxa_livsmedel': amount,
                                    'confidence': confidence,
                                    'extraction_method': 'livsmedel_timtaxa_pattern',
                                    'context': context[:200],  # Limit context size
                                    'source_url': source_url
                                }
                except re.error:
                    # Skip problematic patterns
                    continue
            
            return None
            
        except TimeoutError:
            self.logger.warning(f"Timeout during livsmedel timtaxa extraction for {source_url}")
            return None
        finally:
            signal.alarm(0)  # Cancel timeout
    
    def _clean_text(self, text: str) -> str:
        """Clean text for better pattern matching"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Normalize common variations
        text = re.sub(r'kr/tim|kr/h\b', 'kr/timme', text)
        text = re.sub(r'\bSEK\b', 'kr', text)
        return text
    
    def _extract_context(self, text: str, start: int, end: int, window: int = 200) -> str:
        """Extract context around the match"""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        return text[context_start:context_end]
    
    def _validate_context(self, context: str) -> bool:
        """Validate that context is about food control"""
        context_lower = context.lower()
        
        for pattern in self.context_patterns:
            if re.search(pattern, context_lower):
                return True
        
        return False
    
    def _calculate_confidence(self, pattern: str, context: str, amount: int) -> float:
        """Calculate extraction confidence"""
        confidence = 0.5  # Base confidence
        
        # Pattern specificity bonus
        if 'livsmedelskontroll' in pattern:
            confidence += 0.3
        elif 'livsmedel' in pattern:
            confidence += 0.2
        
        # Context validation bonus
        context_lower = context.lower()
        if 'timme' in context_lower:
            confidence += 0.1
        if 'avgift' in context_lower:
            confidence += 0.1
        
        # Amount reasonableness
        if 1000 <= amount <= 1600:  # Typical range
            confidence += 0.1
        
        return min(confidence, 1.0)

class LivsmedelDebiteringsExtractor:
    """Extract billing model for food control"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Patterns for prepaid billing (förskott)
        self.forskott_patterns = [
            r'livsmedel.*?förskott',
            r'förskott.*?livsmedel',
            r'livsmedelskontroll.*?förskottsbetalning',
            r'förskottsbetalning.*?livsmedelskontroll',
            r'livsmedel.*?betalas.*?i.*?förväg',
            r'livsmedel.*?faktureras.*?i.*?förskott',
            r'avgift.*?livsmedel.*?erläggas.*?i.*?förskott',
            r'livsmedelskontroll.*?debiteras.*?i.*?förskott'
        ]
        
        # Patterns for post-paid billing (efterhand)
        self.efterhand_patterns = [
            r'livsmedel.*?efterhand',
            r'efterhand.*?livsmedel',
            r'livsmedelskontroll.*?efterhandsdebitering',
            r'efterhandsdebitering.*?livsmedelskontroll',
            r'livsmedel.*?faktureras.*?i.*?efterhand',
            r'livsmedel.*?debiteras.*?efter.*?utförd',
            r'avgift.*?livsmedel.*?erläggas.*?efter',
            r'livsmedelskontroll.*?betalas.*?efter.*?kontroll'
        ]
    
    def extract(self, text: str, source_url: str = "") -> Optional[Dict]:
        """Extract billing model for food control with timeout protection"""
        if not text:
            return None
        
        # Set timeout to prevent hanging
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(15)  # Increased from 5 to 15 seconds for more thorough extraction
        
        try:
            text_clean = self._clean_text(text)
            
            # Limit text size to prevent excessive processing
            if len(text_clean) > 100000:  # Increased from 30KB to 100KB for more thorough processing
                text_clean = text_clean[:100000]
            
            # Check for förskott (prepaid)
            for pattern in self.forskott_patterns:
                try:
                    if re.search(pattern, text_clean, re.IGNORECASE):
                        context = self._extract_context_for_pattern(text_clean, pattern)
                        confidence = self._calculate_confidence(pattern, context, 'förskott')
                        
                        self.logger.info(f"Found food control billing model: förskott (confidence: {confidence:.2f})")
                        
                        return {
                            'debitering_livsmedel': 'förskott',
                            'confidence': confidence,
                            'extraction_method': 'livsmedel_debitering_pattern',
                            'context': context[:200],  # Limit context size
                            'source_url': source_url
                        }
                except re.error:
                    continue
            
            # Check for efterhand (post-paid)
            for pattern in self.efterhand_patterns:
                try:
                    if re.search(pattern, text_clean, re.IGNORECASE):
                        context = self._extract_context_for_pattern(text_clean, pattern)
                        confidence = self._calculate_confidence(pattern, context, 'efterhand')
                        
                        self.logger.info(f"Found food control billing model: efterhand (confidence: {confidence:.2f})")
                        
                        return {
                            'debitering_livsmedel': 'efterhand',
                            'confidence': confidence,
                            'extraction_method': 'livsmedel_debitering_pattern',
                            'context': context[:200],  # Limit context size
                            'source_url': source_url
                        }
                except re.error:
                    continue
            
            return None
            
        except TimeoutError:
            self.logger.warning(f"Timeout during livsmedel debitering extraction for {source_url}")
            return None
        finally:
            signal.alarm(0)  # Cancel timeout
    
    def _clean_text(self, text: str) -> str:
        """Clean text for better pattern matching"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Normalize common variations
        text = re.sub(r'i\s+förskott', 'i förskott', text)
        text = re.sub(r'i\s+efterhand', 'i efterhand', text)
        return text
    
    def _extract_context_for_pattern(self, text: str, pattern: str) -> str:
        """Extract context around pattern match"""
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            start = max(0, match.start() - 150)
            end = min(len(text), match.end() + 150)
            return text[start:end]
        return ""
    
    def _calculate_confidence(self, pattern: str, context: str, billing_type: str) -> float:
        """Calculate extraction confidence"""
        confidence = 0.6  # Base confidence
        
        # Pattern specificity bonus
        if 'livsmedelskontroll' in pattern:
            confidence += 0.2
        elif 'livsmedel' in pattern:
            confidence += 0.1
        
        # Context validation
        context_lower = context.lower()
        if billing_type in context_lower:
            confidence += 0.1
        if 'avgift' in context_lower or 'debitering' in context_lower:
            confidence += 0.1
        
        return min(confidence, 1.0)

class BygglovTimtaxaExtractor:
    """Extract ONLY hourly rate for building permits"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Patterns for building permit hourly rates - FIXED to handle Swedish number formatting
        self.patterns = [
            # Direct patterns - Updated to handle spaced numbers
            r'bygglov.*?timtaxa.*?(\d{1,2}\s?\d{3}|\d{3,4})\s*kr',
            r'timtaxa.*?bygglov.*?(\d{1,2}\s?\d{3}|\d{3,4})\s*kr',
            r'handläggning.*?bygglov.*?(\d{1,2}\s?\d{3}|\d{3,4})\s*kr.*?timme',
            r'plan.*?och.*?bygg.*?timtaxa.*?(\d{1,2}\s?\d{3}|\d{3,4})\s*kr',
            r'byggnadsnämnd.*?timtaxa.*?(\d{1,2}\s?\d{3}|\d{3,4})\s*kr',
            
            # Table patterns - Updated to handle spaced numbers
            r'bygglov.*?(\d{1,2}\s?\d{3}|\d{3,4})\s*kr.*?timme',
            r'handläggningsavgift.*?bygglov.*?(\d{1,2}\s?\d{3}|\d{3,4})',
            r'avgift.*?per.*?timme.*?bygglov.*?(\d{1,2}\s?\d{3}|\d{3,4})',
            
            # PBL (Plan- och bygglagen) patterns - Updated to handle spaced numbers
            r'PBL.*?timtaxa.*?(\d{1,2}\s?\d{3}|\d{3,4})\s*kr',
            r'plan.*?och.*?bygglagen.*?(\d{1,2}\s?\d{3}|\d{3,4})\s*kr.*?timme',
            
            # Specific municipal patterns - Updated to handle spaced numbers
            r'bygglovshandläggning.*?(\d{1,2}\s?\d{3}|\d{3,4})\s*kr',
            r'timavgift.*?bygglov.*?(\d{1,2}\s?\d{3}|\d{3,4})',
            r'handläggningstid.*?bygglov.*?(\d{1,2}\s?\d{3}|\d{3,4})\s*kr',
            
            # Reverse patterns (amount first) - Updated to handle spaced numbers
            r'(\d{1,2}\s?\d{3}|\d{3,4})\s*kr.*?timme.*?bygglov',
            r'(\d{1,2}\s?\d{3}|\d{3,4})\s*kr.*?per.*?timme.*?plan.*?bygg',
            r'(\d{1,2}\s?\d{3}|\d{3,4})\s*kr.*?handläggning.*?bygglov'
        ]
        
        # Context validation patterns
        self.context_patterns = [
            r'bygglov',
            r'plan.*?och.*?bygg',
            r'byggnadsnämnd',
            r'PBL',
            r'plan.*?och.*?bygglagen',
            r'bygglovshandläggning'
        ]
    
    def extract(self, text: str, source_url: str = "") -> Optional[Dict]:
        """Extract building permit hourly rate from text with timeout protection"""
        if not text:
            return None
        
        # Set timeout to prevent hanging
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(15)  # Increased from 10 to 15 seconds for more thorough extraction
        
        try:
            text_clean = self._clean_text(text)
            
            # Limit text size to prevent excessive processing
            if len(text_clean) > 100000:  # Increased from 50KB to 100KB for more thorough processing
                text_clean = text_clean[:100000]
            
            # Try each pattern
            for pattern in self.patterns:
                try:
                    matches = re.finditer(pattern, text_clean, re.IGNORECASE)
                    
                    for match in matches:
                        amount_str = match.group(1)
                        amount = int(amount_str.replace(' ', ''))
                        
                        # Validate amount range
                        if 800 <= amount <= 2000:
                            # Quick context validation
                            context = self._extract_context(text_clean, match.start(), match.end())
                            if self._validate_context(context):
                                confidence = self._calculate_confidence(pattern, context, amount)
                                
                                self.logger.info(f"Found building permit hourly rate: {amount} kr/timme (confidence: {confidence:.2f})")
                                
                                return {
                                    'timtaxa_bygglov': amount,
                                    'confidence': confidence,
                                    'extraction_method': 'bygglov_timtaxa_pattern',
                                    'context': context[:200],  # Limit context size
                                    'source_url': source_url
                                }
                except re.error:
                    # Skip problematic patterns
                    continue
            
            return None
            
        except TimeoutError:
            self.logger.warning(f"Timeout during bygglov timtaxa extraction for {source_url}")
            return None
        finally:
            signal.alarm(0)  # Cancel timeout
    
    def _clean_text(self, text: str) -> str:
        """Clean text for better pattern matching"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Normalize common variations
        text = re.sub(r'kr/tim|kr/h\b', 'kr/timme', text)
        text = re.sub(r'\bSEK\b', 'kr', text)
        text = re.sub(r'plan-\s*och\s*bygg', 'plan och bygg', text)
        return text
    
    def _extract_context(self, text: str, start: int, end: int, window: int = 200) -> str:
        """Extract context around the match"""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        return text[context_start:context_end]
    
    def _validate_context(self, context: str) -> bool:
        """Validate that context is about building permits"""
        context_lower = context.lower()
        
        for pattern in self.context_patterns:
            if re.search(pattern, context_lower):
                return True
        
        return False
    
    def _calculate_confidence(self, pattern: str, context: str, amount: int) -> float:
        """Calculate extraction confidence"""
        confidence = 0.5  # Base confidence
        
        # Pattern specificity bonus
        if 'bygglov' in pattern:
            confidence += 0.3
        elif 'bygg' in pattern:
            confidence += 0.2
        
        # Context validation bonus
        context_lower = context.lower()
        if 'timme' in context_lower:
            confidence += 0.1
        if 'handläggning' in context_lower:
            confidence += 0.1
        if 'pbl' in context_lower:
            confidence += 0.1
        
        # Amount reasonableness
        if 1000 <= amount <= 1600:  # Typical range
            confidence += 0.1
        
        return min(confidence, 1.0)

class Phase1ExtractorManager:
    """Manager for all Phase 1 extractors"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.livsmedel_timtaxa_extractor = LivsmedelTimtaxaExtractor()
        self.livsmedel_debitering_extractor = LivsmedelDebiteringsExtractor()
        self.bygglov_timtaxa_extractor = BygglovTimtaxaExtractor()
    
    def extract_all_phase1_data(self, text: str, source_url: str = "") -> Dict:
        """Extract all Phase 1 data points from text with timeout protection"""
        # Set overall timeout for the entire extraction process
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(30)  # 30 second total timeout
        
        try:
            results = {
                'municipality': '',  # To be filled by spider
                'source_url': source_url,
                'extraction_date': datetime.now().isoformat(),
                'extraction_method': 'phase1_combined',
                'data_completeness': 0,
                'validation_warnings': []
            }
            
            # Limit text size for all extractors
            if len(text) > 100000:  # Limit to 100KB total
                text = text[:100000]
                results['validation_warnings'].append('Text truncated due to size limit')
            
            # Extract food control hourly rate
            try:
                livsmedel_timtaxa = self.livsmedel_timtaxa_extractor.extract(text, source_url)
                if livsmedel_timtaxa:
                    results.update(livsmedel_timtaxa)
                    results['data_completeness'] += 1
            except Exception as e:
                self.logger.warning(f"Error extracting livsmedel timtaxa: {e}")
            
            # Extract food control billing model
            try:
                livsmedel_debitering = self.livsmedel_debitering_extractor.extract(text, source_url)
                if livsmedel_debitering:
                    results.update(livsmedel_debitering)
                    results['data_completeness'] += 1
            except Exception as e:
                self.logger.warning(f"Error extracting livsmedel debitering: {e}")
            
            # Extract building permit hourly rate
            try:
                bygglov_timtaxa = self.bygglov_timtaxa_extractor.extract(text, source_url)
                if bygglov_timtaxa:
                    results.update(bygglov_timtaxa)
                    results['data_completeness'] += 1
            except Exception as e:
                self.logger.warning(f"Error extracting bygglov timtaxa: {e}")
            
            # Calculate overall confidence
            confidences = []
            if 'timtaxa_livsmedel' in results:
                confidences.append(results.get('confidence', 0))
            if 'debitering_livsmedel' in results:
                confidences.append(results.get('confidence', 0))
            if 'timtaxa_bygglov' in results:
                confidences.append(results.get('confidence', 0))
            
            if confidences:
                results['confidence'] = sum(confidences) / len(confidences)
            else:
                results['confidence'] = 0
            
            # Data completeness as fraction
            results['data_completeness'] = results['data_completeness'] / 3.0
            
            self.logger.info(f"Phase 1 extraction completed: {results['data_completeness']:.1%} complete, "
                            f"confidence: {results.get('confidence', 0):.2f}")
            
            return results
            
        except TimeoutError:
            self.logger.warning(f"Overall timeout during Phase 1 extraction for {source_url}")
            return {
                'municipality': '',
                'source_url': source_url,
                'extraction_date': datetime.now().isoformat(),
                'extraction_method': 'phase1_combined_timeout',
                'data_completeness': 0,
                'confidence': 0,
                'validation_warnings': ['Extraction timed out']
            }
        except Exception as e:
            self.logger.error(f"Unexpected error during Phase 1 extraction: {e}")
            return {
                'municipality': '',
                'source_url': source_url,
                'extraction_date': datetime.now().isoformat(),
                'extraction_method': 'phase1_combined_error',
                'data_completeness': 0,
                'confidence': 0,
                'validation_warnings': [f'Extraction error: {str(e)}']
            }
        finally:
            signal.alarm(0)  # Cancel timeout 