import re
import logging
from typing import List, Dict, Optional

class SwedishParser:
    """Parser for Swedish municipal text and fee information"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Swedish fee-related keywords with weights
        self.fee_keywords = {
            'avgift': 20,
            'taxa': 18,
            'timtaxa': 15,
            'kostnad': 12,
            'pris': 10,
            'handläggningsavgift': 15,
            'tillsynsavgift': 14,
            'ansökningsavgift': 13,
            'expeditionsavgift': 12,
            'årsavgift': 11,
            'grundavgift': 10
        }
        
        # Swedish amount patterns
        self.amount_patterns = [
            r'(\d+(?:[,\.]\d+)?)\s*kr(?:onor)?',
            r'(\d+(?:[,\.]\d+)?)\s*sek',
            r'(\d+(?:[,\.]\d+)?)\s*kronor',
            r'kr\s*(\d+(?:[,\.]\d+)?)',
            r'(\d+(?:\s?\d{3})*(?:[,\.]\d+)?)\s*kr'
        ]
        
        # Swedish number words
        self.number_words = {
            'noll': 0, 'en': 1, 'ett': 1, 'två': 2, 'tre': 3, 'fyra': 4,
            'fem': 5, 'sex': 6, 'sju': 7, 'åtta': 8, 'nio': 9, 'tio': 10,
            'elva': 11, 'tolv': 12, 'tretton': 13, 'fjorton': 14, 'femton': 15,
            'sexton': 16, 'sjutton': 17, 'arton': 18, 'nitton': 19, 'tjugo': 20,
            'trettio': 30, 'fyrtio': 40, 'femtio': 50, 'sextio': 60,
            'sjuttio': 70, 'åttio': 80, 'nittio': 90, 'hundra': 100, 'tusen': 1000
        }
    
    def extract_amounts_from_text(self, text: str) -> List[Dict]:
        """Extract monetary amounts from Swedish text"""
        amounts = []
        
        for pattern in self.amount_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                amount_str = match.group(1)
                try:
                    # Clean and convert amount
                    cleaned_amount = self._clean_swedish_number(amount_str)
                    amount_value = float(cleaned_amount)
                    
                    amounts.append({
                        'raw_text': match.group(0),
                        'amount': amount_value,
                        'currency': 'SEK',
                        'position': match.span()
                    })
                except ValueError:
                    continue
        
        return amounts
    
    def extract_fee_context(self, text: str, amount_position: tuple) -> str:
        """Extract context around a fee amount"""
        start, end = amount_position
        
        # Get surrounding text (100 chars before and after)
        context_start = max(0, start - 100)
        context_end = min(len(text), end + 100)
        
        context = text[context_start:context_end].strip()
        
        # Try to find sentence boundaries
        sentences = re.split(r'[.!?]', context)
        if len(sentences) > 1:
            # Find the sentence containing the amount
            for sentence in sentences:
                if text[start:end] in sentence:
                    return sentence.strip()
        
        return context
    
    def classify_fee_type(self, text: str) -> str:
        """Classify the type of fee based on Swedish text"""
        text_lower = text.lower()
        
        # Building permits
        if any(word in text_lower for word in ['bygglov', 'byggnadsnämnd', 'pbl']):
            return 'Bygglov'
        
        # Environmental
        if any(word in text_lower for word in ['miljö', 'miljönämnd', 'miljöprövning']):
            return 'Miljö'
        
        # Food/Restaurant
        if any(word in text_lower for word in ['livsmedel', 'serveringstillstånd', 'restaurang']):
            return 'Livsmedel'
        
        # Business
        if any(word in text_lower for word in ['näringsverksamhet', 'företag', 'handel']):
            return 'Näringsverksamhet'
        
        # General administrative
        if any(word in text_lower for word in ['handläggning', 'administration', 'expedition']):
            return 'Administration'
        
        return 'Allmän avgift'
    
    def parse_fee_schedule(self, text: str) -> List[Dict]:
        """Parse a Swedish fee schedule from text"""
        fees = []
        
        # Split text into potential fee entries
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for fee patterns in each line
            amounts = self.extract_amounts_from_text(line)
            
            for amount_info in amounts:
                # Check if line contains fee keywords
                if any(keyword in line.lower() for keyword in self.fee_keywords.keys()):
                    fee_name = self._extract_fee_name(line, amount_info['position'])
                    fee_type = self.classify_fee_type(line)
                    
                    fee = {
                        'fee_name': fee_name,
                        'amount': amount_info['amount'],
                        'currency': amount_info['currency'],
                        'category': fee_type,
                        'raw_text': line,
                        'confidence': self._calculate_confidence(line)
                    }
                    fees.append(fee)
        
        return fees
    
    def _clean_swedish_number(self, number_str: str) -> str:
        """Clean Swedish number format for parsing"""
        # Replace Swedish decimal comma with dot
        cleaned = number_str.replace(',', '.')
        
        # Remove spaces in large numbers (e.g., "1 000" -> "1000")
        cleaned = re.sub(r'(\d)\s+(\d)', r'\1\2', cleaned)
        
        return cleaned
    
    def _extract_fee_name(self, text: str, amount_position: tuple) -> str:
        """Extract fee name from text around amount"""
        start, end = amount_position
        
        # Get text before the amount
        before_amount = text[:start].strip()
        
        # Look for fee name patterns
        fee_patterns = [
            r'([^.!?]*(?:avgift|taxa|kostnad|pris)[^.!?]*)',
            r'([A-ZÅÄÖ][^.!?]*)',  # Capitalized text
            r'([^,;]*)'  # Text until punctuation
        ]
        
        for pattern in fee_patterns:
            match = re.search(pattern, before_amount, re.IGNORECASE)
            if match:
                fee_name = match.group(1).strip()
                if len(fee_name) > 5:  # Minimum length check
                    return fee_name
        
        # Fallback: use text before amount
        return before_amount[-50:].strip() if before_amount else 'Avgift'
    
    def _calculate_confidence(self, text: str) -> float:
        """Calculate confidence score for fee extraction"""
        score = 0.0
        text_lower = text.lower()
        
        # Keyword presence
        for keyword, weight in self.fee_keywords.items():
            if keyword in text_lower:
                score += weight
        
        # Amount format quality
        if re.search(r'\d+[,\.]\d{2}\s*kr', text):
            score += 10  # Precise amount format
        elif re.search(r'\d+\s*kr', text):
            score += 5   # Basic amount format
        
        # Text structure
        if ':' in text or '-' in text:
            score += 5  # Structured format
        
        # Normalize to 0-1 range
        return min(1.0, score / 50.0)
    
    def normalize_municipality_name(self, name: str) -> str:
        """Normalize Swedish municipality name"""
        if not name:
            return ""
        
        # Remove common suffixes
        name = re.sub(r'\s*(kommun|stad|municipality)$', '', name, flags=re.IGNORECASE)
        
        # Handle special Swedish characters
        name = name.strip()
        
        # Capitalize properly
        return name.title()
    
    def parse_contact_info(self, text: str) -> Dict:
        """Extract contact information from Swedish text"""
        contact_info = {}
        
        # Phone numbers
        phone_pattern = r'(?:tel|telefon|tfn)[:\s]*(\+?46\s?-?\s?\d{1,3}\s?-?\s?\d{5,8}|\d{2,4}\s?-?\s?\d{5,8})'
        phone_match = re.search(phone_pattern, text, re.IGNORECASE)
        if phone_match:
            contact_info['phone'] = phone_match.group(1).strip()
        
        # Email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact_info['email'] = email_match.group(0)
        
        # Postal codes
        postal_pattern = r'\b\d{3}\s?\d{2}\b'
        postal_match = re.search(postal_pattern, text)
        if postal_match:
            contact_info['postal_code'] = postal_match.group(0)
        
        return contact_info 