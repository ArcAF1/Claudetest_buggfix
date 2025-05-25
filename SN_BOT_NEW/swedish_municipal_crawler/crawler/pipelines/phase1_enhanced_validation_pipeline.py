#!/usr/bin/env python3
"""
Phase 1 Enhanced Validation Pipeline
Validates and enhances the three specific Phase 1 data points:
1. Timtaxan för livsmedelskontroll (Hourly rate for food control)
2. Debiteringsmodell för livsmedelskontroll (Billing model: prepaid vs post-paid)
3. Timtaxan för bygglov (Hourly rate for building permits)
"""

import logging
import re
from datetime import datetime
from scrapy.exceptions import DropItem
from typing import Dict, List, Optional
from ..utils.validators import SwedishValidators

class Phase1EnhancedValidationPipeline:
    """Enhanced validation pipeline specifically for Phase 1 data"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validators = SwedishValidators()
        
        # Phase 1 specific statistics
        self.stats = {
            'total_items': 0,
            'complete_items': 0,      # Has all 3 fields
            'partial_items': 0,       # Has 1-2 fields
            'rejected_items': 0,
            'enhanced_items': 0,      # Items that were enhanced/cleaned
            'field_coverage': {
                'timtaxa_livsmedel': 0,
                'debitering_livsmedel': 0,
                'timtaxa_bygglov': 0
            },
            'validation_warnings': [],
            'data_quality_distribution': {
                'excellent': 0,    # 90-100%
                'good': 0,         # 70-89%
                'fair': 0,         # 50-69%
                'poor': 0          # <50%
            },
            'timtaxa_ranges': {
                'livsmedel': {'min': float('inf'), 'max': 0, 'values': []},
                'bygglov': {'min': float('inf'), 'max': 0, 'values': []}
            },
            'debitering_distribution': {
                'förskott': 0,
                'efterhand': 0,
                'unknown': 0
            }
        }
        
        # Validation rules for Phase 1
        self.validation_rules = {
            'timtaxa_livsmedel': {
                'min_value': 800,
                'max_value': 2000,
                'typical_range': (1000, 1600),
                'description': 'Hourly rate for food control'
            },
            'timtaxa_bygglov': {
                'min_value': 800,
                'max_value': 2000,
                'typical_range': (900, 1500),
                'description': 'Hourly rate for building permits'
            },
            'debitering_livsmedel': {
                'allowed_values': ['förskott', 'efterhand'],
                'description': 'Billing model for food control'
            }
        }
    
    def process_item(self, item, spider):
        """Validate and enhance Phase 1 item"""
        try:
            self.stats['total_items'] += 1
            
            # Validate municipality (required)
            if not self._validate_municipality(item, spider):
                self.stats['rejected_items'] += 1
                raise DropItem("Missing or invalid municipality")
            
            # Clean and enhance municipality name
            original_municipality = item.get('municipality', '')
            item['municipality'] = self.validators.clean_municipality_name(original_municipality)
            if item['municipality'] != original_municipality:
                self.stats['enhanced_items'] += 1
                spider.logger.debug(f"Enhanced municipality name: {original_municipality} -> {item['municipality']}")
            
            # Validate and enhance Phase 1 fields
            fields_present = 0
            validation_warnings = []
            
            # 1. Validate timtaxa_livsmedel
            if self._validate_and_enhance_timtaxa(item, 'timtaxa_livsmedel', spider):
                fields_present += 1
                self.stats['field_coverage']['timtaxa_livsmedel'] += 1
                self._update_timtaxa_stats('livsmedel', item['timtaxa_livsmedel'])
            
            # 2. Validate debitering_livsmedel
            if self._validate_and_enhance_debitering(item, spider):
                fields_present += 1
                self.stats['field_coverage']['debitering_livsmedel'] += 1
                self._update_debitering_stats(item['debitering_livsmedel'])
            
            # 3. Validate timtaxa_bygglov
            if self._validate_and_enhance_timtaxa(item, 'timtaxa_bygglov', spider):
                fields_present += 1
                self.stats['field_coverage']['timtaxa_bygglov'] += 1
                self._update_timtaxa_stats('bygglov', item['timtaxa_bygglov'])
            
            # Check if we have any valid Phase 1 data
            if fields_present == 0:
                self.stats['rejected_items'] += 1
                raise DropItem("No valid Phase 1 data found")
            
            # Calculate completeness and quality scores
            item['completeness_score'] = fields_present / 3.0
            item['data_quality'] = self._assess_data_quality(item)
            item['validation_warnings'] = validation_warnings
            item['validation_date'] = datetime.now().isoformat()
            item['validation_version'] = 'phase1_enhanced_v1.0'
            
            # Categorize item
            if fields_present == 3:
                self.stats['complete_items'] += 1
                item['status'] = 'complete'
            else:
                self.stats['partial_items'] += 1
                item['status'] = 'partial'
            
            # Update quality distribution
            self._update_quality_distribution(item['data_quality'])
            
            # Add Phase 1 specific metadata
            item['phase1_fields_found'] = fields_present
            item['phase1_success_rate'] = fields_present / 3.0
            
            spider.logger.info(f"Validated {item['municipality']}: {fields_present}/3 fields, "
                             f"quality: {item['data_quality']:.1f}%")
            
            return item
            
        except DropItem:
            raise
        except Exception as e:
            self.logger.error(f"Error validating item: {e}")
            self.stats['rejected_items'] += 1
            raise DropItem(f"Validation error: {str(e)}")
    
    def _validate_municipality(self, item: Dict, spider) -> bool:
        """Validate municipality field"""
        municipality = item.get('municipality', '').strip()
        
        if not municipality:
            spider.logger.warning("Missing municipality name")
            return False
        
        # Check if it looks like a valid Swedish municipality
        if len(municipality) < 2:
            spider.logger.warning(f"Municipality name too short: {municipality}")
            return False
        
        # Check for obvious test/invalid data
        invalid_patterns = ['test', 'example', 'sample', 'xxx', '123']
        if any(pattern in municipality.lower() for pattern in invalid_patterns):
            spider.logger.warning(f"Invalid municipality name: {municipality}")
            return False
        
        return True
    
    def _validate_and_enhance_timtaxa(self, item: Dict, field: str, spider) -> bool:
        """Validate and enhance timtaxa fields"""
        value = item.get(field)
        if not value:
            return False
        
        try:
            # Convert to float and validate
            amount = float(value)
            rules = self.validation_rules[field]
            
            # Check range
            if amount < rules['min_value'] or amount > rules['max_value']:
                spider.logger.warning(f"Invalid {field} for {item['municipality']}: {amount} "
                                    f"(valid range: {rules['min_value']}-{rules['max_value']})")
                item[field] = None
                return False
            
            # Convert to integer (Swedish rates are typically whole numbers)
            item[field] = int(amount)
            
            # Add quality indicators
            if rules['typical_range'][0] <= amount <= rules['typical_range'][1]:
                item[f'{field}_quality'] = 'typical'
            elif amount < rules['typical_range'][0]:
                item[f'{field}_quality'] = 'low'
            else:
                item[f'{field}_quality'] = 'high'
            
            return True
            
        except (ValueError, TypeError) as e:
            spider.logger.warning(f"Invalid {field} value for {item['municipality']}: {value} - {e}")
            item[field] = None
            return False
    
    def _validate_and_enhance_debitering(self, item: Dict, spider) -> bool:
        """Validate and enhance debitering model"""
        value = item.get('debitering_livsmedel')
        if not value:
            return False
        
        # Normalize the value
        normalized = self._normalize_debitering_value(value)
        
        if normalized:
            item['debitering_livsmedel'] = normalized
            item['debitering_livsmedel_original'] = value  # Keep original for reference
            return True
        else:
            spider.logger.warning(f"Invalid debitering model for {item['municipality']}: {value}")
            item['debitering_livsmedel'] = None
            return False
    
    def _normalize_debitering_value(self, value: str) -> Optional[str]:
        """Normalize debitering model to standard values"""
        if not value:
            return None
        
        value_lower = str(value).lower().strip()
        
        # Patterns for förskott (prepaid)
        forskott_patterns = [
            'förskott', 'förväg', 'advance', 'prepaid', 'i förskott',
            'förskottsbetalning', 'förskottsfaktura', 'betalas i förväg'
        ]
        
        # Patterns for efterhand (post-paid)
        efterhand_patterns = [
            'efterhand', 'efterskott', 'faktura', 'i efterhand',
            'efterhandsdebitering', 'efterhandsfaktura', 'betalas efter',
            'debiteras efter', 'faktureras efter'
        ]
        
        # Check for förskott patterns
        for pattern in forskott_patterns:
            if pattern in value_lower:
                return 'förskott'
        
        # Check for efterhand patterns
        for pattern in efterhand_patterns:
            if pattern in value_lower:
                return 'efterhand'
        
        return None
    
    def _assess_data_quality(self, item: Dict) -> float:
        """Assess overall data quality for Phase 1 item"""
        score = 0
        
        # Base confidence from extraction
        confidence = item.get('confidence', 0)
        score += confidence * 40
        
        # Completeness score (30 points)
        completeness = item.get('completeness_score', 0)
        score += completeness * 30
        
        # Source quality (15 points)
        source_url = item.get('source_url', '')
        if source_url.endswith('.pdf'):
            score += 10  # PDFs often more reliable
        if '.se' in source_url and any(term in source_url for term in ['kommun', 'stad']):
            score += 5   # Official municipal domain
        
        # Value reasonableness (10 points)
        timtaxa_livsmedel = item.get('timtaxa_livsmedel')
        if timtaxa_livsmedel and item.get('timtaxa_livsmedel_quality') == 'typical':
            score += 3
        
        timtaxa_bygglov = item.get('timtaxa_bygglov')
        if timtaxa_bygglov and item.get('timtaxa_bygglov_quality') == 'typical':
            score += 3
        
        # Valid debitering model (4 points)
        if item.get('debitering_livsmedel') in ['förskott', 'efterhand']:
            score += 4
        
        # Extraction method quality (5 points)
        extraction_method = item.get('extraction_method', '')
        if 'pdf' in extraction_method.lower():
            score += 3
        elif 'enhanced' in extraction_method.lower():
            score += 2
        
        return min(score, 100)
    
    def _update_timtaxa_stats(self, category: str, value: int):
        """Update timtaxa statistics"""
        stats = self.stats['timtaxa_ranges'][category]
        stats['values'].append(value)
        stats['min'] = min(stats['min'], value)
        stats['max'] = max(stats['max'], value)
    
    def _update_debitering_stats(self, value: str):
        """Update debitering statistics"""
        if value in ['förskott', 'efterhand']:
            self.stats['debitering_distribution'][value] += 1
        else:
            self.stats['debitering_distribution']['unknown'] += 1
    
    def _update_quality_distribution(self, quality: float):
        """Update quality distribution statistics"""
        if quality >= 90:
            self.stats['data_quality_distribution']['excellent'] += 1
        elif quality >= 70:
            self.stats['data_quality_distribution']['good'] += 1
        elif quality >= 50:
            self.stats['data_quality_distribution']['fair'] += 1
        else:
            self.stats['data_quality_distribution']['poor'] += 1
    
    def close_spider(self, spider):
        """Log comprehensive Phase 1 validation statistics"""
        total = self.stats['total_items']
        if total == 0:
            spider.logger.warning("No items processed in Phase 1 validation")
            return
        
        spider.logger.info("=== Phase 1 Enhanced Validation Statistics ===")
        spider.logger.info(f"Total municipalities processed: {total}")
        spider.logger.info(f"Valid items: {total - self.stats['rejected_items']}")
        spider.logger.info(f"Rejected items: {self.stats['rejected_items']}")
        spider.logger.info(f"Enhanced items: {self.stats['enhanced_items']}")
        
        # Completeness statistics
        spider.logger.info(f"\nData Completeness:")
        spider.logger.info(f"  Complete data (all 3 fields): {self.stats['complete_items']} "
                          f"({self.stats['complete_items']/total*100:.1f}%)")
        spider.logger.info(f"  Partial data (1-2 fields): {self.stats['partial_items']} "
                          f"({self.stats['partial_items']/total*100:.1f}%)")
        
        # Field coverage
        spider.logger.info(f"\nField Coverage:")
        for field, count in self.stats['field_coverage'].items():
            percentage = (count / total) * 100
            spider.logger.info(f"  {field}: {count} ({percentage:.1f}%)")
        
        # Quality distribution
        spider.logger.info(f"\nData Quality Distribution:")
        for quality, count in self.stats['data_quality_distribution'].items():
            percentage = (count / total) * 100 if total > 0 else 0
            spider.logger.info(f"  {quality.capitalize()}: {count} ({percentage:.1f}%)")
        
        # Timtaxa statistics
        spider.logger.info(f"\nTimtaxa Statistics:")
        for category, stats in self.stats['timtaxa_ranges'].items():
            if stats['values']:
                avg = sum(stats['values']) / len(stats['values'])
                spider.logger.info(f"  {category}: {len(stats['values'])} values, "
                                  f"range: {stats['min']}-{stats['max']} kr, "
                                  f"average: {avg:.0f} kr")
        
        # Debitering distribution
        spider.logger.info(f"\nBilling Model Distribution:")
        total_debitering = sum(self.stats['debitering_distribution'].values())
        for model, count in self.stats['debitering_distribution'].items():
            percentage = (count / total_debitering) * 100 if total_debitering > 0 else 0
            spider.logger.info(f"  {model}: {count} ({percentage:.1f}%)")
        
        # Success metrics
        success_rate = ((self.stats['complete_items'] + self.stats['partial_items']) / total) * 100
        complete_rate = (self.stats['complete_items'] / total) * 100
        
        spider.logger.info(f"\nPhase 1 Success Metrics:")
        spider.logger.info(f"  Overall success rate: {success_rate:.1f}%")
        spider.logger.info(f"  Complete data rate: {complete_rate:.1f}%")
        spider.logger.info(f"  Average fields per municipality: {sum(self.stats['field_coverage'].values()) / total:.1f}")
        
        # Recommendations
        if complete_rate < 50:
            spider.logger.warning("⚠️  Low complete data rate. Consider improving extraction patterns.")
        if self.stats['data_quality_distribution']['poor'] > total * 0.2:
            spider.logger.warning("⚠️  High number of poor quality items. Review validation rules.")
        
        spider.logger.info("=== End Phase 1 Validation Statistics ===")

def validate_phase1_item(item: Dict) -> Dict:
    """Standalone function to validate a single Phase 1 item"""
    validator = Phase1EnhancedValidationPipeline()
    
    # Mock spider for logging
    class MockSpider:
        def __init__(self):
            self.logger = logging.getLogger(__name__)
    
    try:
        return validator.process_item(item, MockSpider())
    except DropItem as e:
        return {'error': str(e), 'valid': False}
    except Exception as e:
        return {'error': f"Validation error: {str(e)}", 'valid': False} 