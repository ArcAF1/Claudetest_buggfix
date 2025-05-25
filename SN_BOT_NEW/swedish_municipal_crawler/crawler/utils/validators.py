import re
from datetime import datetime

class SwedishValidators:
    """Validators for Swedish data formats"""
    
    @staticmethod
    def validate_organization_number(org_nr):
        """Validate Swedish organization number"""
        # Remove common separators
        cleaned = re.sub(r'[-\s]', '', str(org_nr))
        
        # Check format (10 or 12 digits)
        if not re.match(r'^\d{10}$|^\d{12}$', cleaned):
            return False
        
        # If 12 digits, extract 10-digit number
        if len(cleaned) == 12:
            cleaned = cleaned[2:]
        
        # Luhn algorithm validation
        digits = [int(d) for d in cleaned]
        checksum = 0
        
        for i in range(9):
            num = digits[i]
            if i % 2 == 0:
                num *= 2
                if num > 9:
                    num = num // 10 + num % 10
            checksum += num
        
        return (10 - (checksum % 10)) % 10 == digits[9]
    
    @staticmethod
    def validate_swedish_phone(phone):
        """Validate Swedish phone number"""
        # Remove common separators
        cleaned = re.sub(r'[\s\-\(\)]', '', str(phone))
        
        # Check Swedish phone patterns
        patterns = [
            r'^0\d{1,3}\d{5,8}$',  # Landline
            r'^07\d{8}$',          # Mobile
            r'^\+467\d{8}$',       # International mobile
            r'^\+460\d{1,3}\d{5,8}$'  # International landline
        ]
        
        return any(re.match(pattern, cleaned) for pattern in patterns)
    
    @staticmethod
    def validate_postal_code(postal_code):
        """Validate Swedish postal code"""
        # Remove spaces
        cleaned = re.sub(r'\s', '', str(postal_code))
        
        # Swedish postal codes are 5 digits
        return bool(re.match(r'^\d{5}$', cleaned))
    
    @staticmethod
    def validate_fee_amount(amount):
        """Validate fee amount is reasonable"""
        try:
            amount_float = float(amount)
            # Reasonable range for municipal fees
            return 0 < amount_float <= 100000
        except:
            return False
    
    @staticmethod
    def validate_date_format(date_str):
        """Validate Swedish date formats"""
        date_formats = [
            '%Y-%m-%d',      # ISO format
            '%d/%m/%Y',      # Swedish format
            '%d.%m.%Y',      # Alternative format
            '%Y%m%d'         # Compact format
        ]
        
        for fmt in date_formats:
            try:
                datetime.strptime(date_str, fmt)
                return True
            except:
                continue
        
        return False
    
    @staticmethod
    def clean_municipality_name(name):
        """Clean and standardize municipality name"""
        if not name:
            return ""
        
        # Remove common suffixes
        name = re.sub(r'\s*(kommun|stad|municipality)$', '', name, flags=re.IGNORECASE)
        
        # Standardize capitalization
        return name.strip().title() 