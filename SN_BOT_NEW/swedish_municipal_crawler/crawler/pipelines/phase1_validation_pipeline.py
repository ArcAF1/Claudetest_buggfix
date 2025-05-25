#!/usr/bin/env python3
"""
Phase 1 Validation Pipeline
Validates the three specific Phase 1 data points:
1. Timtaxan för livsmedelskontroll (800-2000 kr/hour)
2. Debiteringsmodell för livsmedelskontroll ('förskott' or 'efterhand')
3. Timtaxan för bygglov (800-2000 kr/hour)
"""

import logging
from datetime import datetime
try:
    from scrapy.exceptions import DropItem
except Exception:  # pragma: no cover - fallback if Scrapy is missing
    class DropItem(Exception):
        pass
from typing import Dict, List, Optional

class Phase1ValidationPipeline:
    """Phase 1 focused validation pipeline"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Phase 1 validation rules
        self.validation_rules = {
            'timtaxa_livsmedel': {
                'required': False,  # Not all municipalities may have this
                'type': int,
                'min_value': 800,
                'max_value': 2000,
                'description': 'Hourly rate for food control'
            },
            'debitering_livsmedel': {
                'required': False,
                'type': str,
                'allowed_values': ['förskott', 'efterhand'],
                'description': 'Billing model for food control'
            },
            'timtaxa_bygglov': {
                'required': False,
                'type': int,
                'min_value': 800,
                'max_value': 2000,
                'description': 'Hourly rate for building permits'
            }
        }
        
        # Statistics
        self.stats = {
            'total_items': 0,
            'valid_items': 0,
            'rejected_items': 0,
            'items_with_livsmedel_timtaxa': 0,
            'items_with_debitering_model': 0,
            'items_with_bygglov_timtaxa': 0,
            'complete_items': 0,  # Items with all 3 fields
            'validation_warnings': []
        }
    
    def process_item(self, item, spider):
        """Validate Phase 1 item"""
        self.stats['total_items'] += 1
        
        # Validate Phase 1 fields
        validation_result = self._validate_phase1_item(item)
        
        if not validation_result['is_valid']:
            self.stats['rejected_items'] += 1
            spider.logger.warning(f"Rejected Phase 1 item: {validation_result['errors']}")
            raise DropItem(f"Phase 1 validation failed: {'; '.join(validation_result['errors'])}")
        
        # Add validation metadata
        item['validation_warnings'] = validation_result['warnings']
        item['validation_date'] = datetime.now().isoformat()
        item['validation_version'] = 'phase1_v1.0'
        
        # Update statistics
        self._update_statistics(item)
        
        self.stats['valid_items'] += 1
        return item
    
    def _validate_phase1_item(self, item: Dict) -> Dict:
        """Validate Phase 1 specific fields"""
        errors = []
        warnings = []
        is_valid = True
        
        # Check municipality (required)
        if not item.get('municipality'):
            errors.append("Municipality is required")
            is_valid = False
        
        # Validate each Phase 1 field
        phase1_fields_found = 0
        
        # 1. Validate timtaxa_livsmedel
        if 'timtaxa_livsmedel' in item and item['timtaxa_livsmedel']:
            validation = self._validate_field(
                item['timtaxa_livsmedel'], 
                self.validation_rules['timtaxa_livsmedel']
            )
            if validation['is_valid']:
                phase1_fields_found += 1
                self.stats['items_with_livsmedel_timtaxa'] += 1
            else:
                errors.extend(validation['errors'])
                is_valid = False
        
        # 2. Validate debitering_livsmedel
        if 'debitering_livsmedel' in item and item['debitering_livsmedel']:
            validation = self._validate_field(
                item['debitering_livsmedel'], 
                self.validation_rules['debitering_livsmedel']
            )
            if validation['is_valid']:
                phase1_fields_found += 1
                self.stats['items_with_debitering_model'] += 1
            else:
                errors.extend(validation['errors'])
                is_valid = False
        
        # 3. Validate timtaxa_bygglov
        if 'timtaxa_bygglov' in item and item['timtaxa_bygglov']:
            validation = self._validate_field(
                item['timtaxa_bygglov'], 
                self.validation_rules['timtaxa_bygglov']
            )
            if validation['is_valid']:
                phase1_fields_found += 1
                self.stats['items_with_bygglov_timtaxa'] += 1
            else:
                errors.extend(validation['errors'])
                is_valid = False
        
        # Check if we have at least one Phase 1 field
        if phase1_fields_found == 0:
            errors.append("No Phase 1 data found (need at least one of: timtaxa_livsmedel, debitering_livsmedel, timtaxa_bygglov)")
            is_valid = False
        
        # Check for complete items (all 3 fields)
        if phase1_fields_found == 3:
            self.stats['complete_items'] += 1
        
        # Validate data completeness
        data_completeness = item.get('data_completeness', 0)
        if data_completeness < 0.33:  # Less than 1/3 fields found
            warnings.append(f"Low data completeness: {data_completeness:.1%}")
        
        # Validate confidence
        confidence = item.get('confidence', 0)
        if confidence < 0.5:
            warnings.append(f"Low extraction confidence: {confidence:.2f}")
        
        # Validate source URL
        source_url = item.get('source_url', '')
        if not source_url:
            warnings.append("Missing source URL")
        elif not self._is_valid_municipal_url(source_url):
            warnings.append(f"Source URL may not be from official municipality: {source_url}")
        
        return {
            'is_valid': is_valid,
            'errors': errors,
            'warnings': warnings,
            'phase1_fields_found': phase1_fields_found
        }
    
    def _validate_field(self, value, rule: Dict) -> Dict:
        """Validate individual field against rule"""
        errors = []
        is_valid = True
        
        # Type validation
        expected_type = rule.get('type')
        if expected_type and not isinstance(value, expected_type):
            try:
                # Try to convert
                if expected_type == int:
                    value = int(value)
                elif expected_type == str:
                    value = str(value)
            except (ValueError, TypeError):
                errors.append(f"Invalid type for {rule.get('description', 'field')}: expected {expected_type.__name__}")
                is_valid = False
                return {'is_valid': is_valid, 'errors': errors}
        
        # Range validation for numeric fields
        if expected_type == int:
            min_val = rule.get('min_value')
            max_val = rule.get('max_value')
            
            if min_val is not None and value < min_val:
                errors.append(f"{rule.get('description', 'Value')} too low: {value} < {min_val}")
                is_valid = False
            
            if max_val is not None and value > max_val:
                errors.append(f"{rule.get('description', 'Value')} too high: {value} > {max_val}")
                is_valid = False
        
        # Allowed values validation
        allowed_values = rule.get('allowed_values')
        if allowed_values and value not in allowed_values:
            errors.append(f"Invalid value for {rule.get('description', 'field')}: '{value}' not in {allowed_values}")
            is_valid = False
        
        return {'is_valid': is_valid, 'errors': errors}
    
    def _is_valid_municipal_url(self, url: str) -> bool:
        """Check if URL appears to be from a Swedish municipality"""
        if not url:
            return False
        
        url_lower = url.lower()
        
        # Swedish municipality indicators
        municipal_indicators = [
            '.se/',  # Swedish domain
            'kommun',  # Municipality
            'stad',    # City
        ]
        
        # Should have at least one municipal indicator
        return any(indicator in url_lower for indicator in municipal_indicators)
    
    def _update_statistics(self, item: Dict):
        """Update validation statistics"""
        # Track warnings
        warnings = item.get('validation_warnings', [])
        self.stats['validation_warnings'].extend(warnings)
    
    def close_spider(self, spider):
        """Log Phase 1 validation statistics"""
        spider.logger.info("=== Phase 1 Validation Statistics ===")
        spider.logger.info(f"Total items processed: {self.stats['total_items']}")
        spider.logger.info(f"Valid items: {self.stats['valid_items']}")
        spider.logger.info(f"Rejected items: {self.stats['rejected_items']}")
        spider.logger.info(f"Items with food control hourly rate: {self.stats['items_with_livsmedel_timtaxa']}")
        spider.logger.info(f"Items with billing model: {self.stats['items_with_debitering_model']}")
        spider.logger.info(f"Items with building permit hourly rate: {self.stats['items_with_bygglov_timtaxa']}")
        spider.logger.info(f"Complete items (all 3 fields): {self.stats['complete_items']}")
        
        if self.stats['valid_items'] > 0:
            completeness_rate = (self.stats['complete_items'] / self.stats['valid_items']) * 100
            spider.logger.info(f"Data completeness rate: {completeness_rate:.1f}%")
            
            # Field coverage
            livsmedel_coverage = (self.stats['items_with_livsmedel_timtaxa'] / self.stats['valid_items']) * 100
            debitering_coverage = (self.stats['items_with_debitering_model'] / self.stats['valid_items']) * 100
            bygglov_coverage = (self.stats['items_with_bygglov_timtaxa'] / self.stats['valid_items']) * 100
            
            spider.logger.info(f"Field coverage:")
            spider.logger.info(f"  Food control hourly rate: {livsmedel_coverage:.1f}%")
            spider.logger.info(f"  Billing model: {debitering_coverage:.1f}%")
            spider.logger.info(f"  Building permit hourly rate: {bygglov_coverage:.1f}%")
        
        # Most common warnings
        if self.stats['validation_warnings']:
            from collections import Counter
            warning_counts = Counter(self.stats['validation_warnings'])
            spider.logger.info("Most common validation warnings:")
            for warning, count in warning_counts.most_common(5):
                spider.logger.info(f"  {warning}: {count} times")

def validate_phase1_data(item: Dict) -> Dict:
    """Standalone function to validate Phase 1 data"""
    validator = Phase1ValidationPipeline()
    return validator._validate_phase1_item(item) 