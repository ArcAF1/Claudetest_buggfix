from crawler.utils.validators import SwedishValidators
import logging

class ValidationPipeline:
    """Pipeline to validate extracted Swedish municipal fee data"""
    
    def __init__(self):
        self.validators = SwedishValidators()
        self.logger = logging.getLogger(__name__)
        self.stats = {
            'valid_items': 0,
            'invalid_items': 0,
            'validation_errors': {}
        }
    
    def process_item(self, item, spider):
        """Validate item data"""
        errors = []
        
        # Validate required fields
        required_fields = ['fee_name', 'municipality', 'source_url']
        for field in required_fields:
            if not item.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Validate municipality name
        if item.get('municipality'):
            cleaned_name = self.validators.clean_municipality_name(item['municipality'])
            item['municipality'] = cleaned_name
        
        # Validate organization number if present
        if item.get('municipality_org_number'):
            if not self.validators.validate_organization_number(item['municipality_org_number']):
                errors.append("Invalid organization number format")
        
        # Validate fee amount if present
        if item.get('amount') and item['amount'] != 'See PDF':
            # Extract numeric value
            import re
            amount_str = str(item['amount']).replace(',', '.')
            amount_match = re.search(r'(\d+(?:\.\d+)?)', amount_str)
            
            if amount_match:
                amount_value = float(amount_match.group(1))
                if not self.validators.validate_fee_amount(amount_value):
                    errors.append("Fee amount outside reasonable range")
                item['amount_numeric'] = amount_value
            else:
                errors.append("Could not parse fee amount")
        
        # Validate extraction date
        if item.get('extraction_date'):
            if not self.validators.validate_date_format(item['extraction_date'][:10]):  # ISO date part
                errors.append("Invalid extraction date format")
        
        # Log validation results
        if errors:
            self.stats['invalid_items'] += 1
            error_key = item.get('municipality', 'unknown')
            if error_key not in self.stats['validation_errors']:
                self.stats['validation_errors'][error_key] = []
            self.stats['validation_errors'][error_key].extend(errors)
            
            self.logger.warning(f"Validation errors for {item.get('municipality', 'unknown')}: {errors}")
            # Still pass the item but mark it as having validation issues
            item['validation_errors'] = errors
        else:
            self.stats['valid_items'] += 1
        
        return item
    
    def close_spider(self, spider):
        """Log validation statistics"""
        total_items = self.stats['valid_items'] + self.stats['invalid_items']
        if total_items > 0:
            valid_percentage = (self.stats['valid_items'] / total_items) * 100
            self.logger.info(f"Validation complete: {valid_percentage:.1f}% valid items")
            self.logger.info(f"Valid items: {self.stats['valid_items']}")
            self.logger.info(f"Items with errors: {self.stats['invalid_items']}")
            
            if self.stats['validation_errors']:
                self.logger.info("Validation errors by municipality:")
                for municipality, errors in self.stats['validation_errors'].items():
                    self.logger.info(f"  {municipality}: {len(errors)} errors") 