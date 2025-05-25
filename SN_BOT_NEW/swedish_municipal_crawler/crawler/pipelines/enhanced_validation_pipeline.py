import logging
import re
from datetime import datetime
from ..utils.validators import SwedishValidators

class EnhancedValidationPipeline:
    """Enhanced validation pipeline with confidence scoring and detailed validation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validators = SwedishValidators()
        
        # Validation statistics
        self.stats = {
            'total_processed': 0,
            'total_valid': 0,
            'total_invalid': 0,
            'validation_errors': {},
            'confidence_distribution': {
                'high': 0,    # >= 0.8
                'medium': 0,  # 0.6 - 0.8
                'low': 0      # < 0.6
            },
            'extraction_methods': {},
            'categories': {}
        }
        
        # Validation rules with weights
        self.validation_rules = {
            'required_fields': {
                'weight': 1.0,
                'fields': ['fee_name', 'amount', 'currency', 'source_url']
            },
            'amount_validation': {
                'weight': 0.9,
                'min_amount': 10,
                'max_amount': 500000
            },
            'fee_name_validation': {
                'weight': 0.8,
                'min_length': 3,
                'max_length': 500,
                'forbidden_patterns': [
                    r'lorem ipsum',
                    r'test\s*fee',
                    r'example',
                    r'placeholder',
                    r'dummy',
                    r'sample'
                ]
            },
            'currency_validation': {
                'weight': 0.7,
                'allowed_currencies': ['SEK', 'kr', 'kronor']
            },
            'url_validation': {
                'weight': 0.6,
                'required_domains': ['.se']
            },
            'category_validation': {
                'weight': 0.5,
                'valid_categories': [
                    'bygglov', 'miljö', 'livsmedel', 'näringsverksamhet',
                    'socialtjänst', 'skola', 'vatten', 'övrigt'
                ]
            }
        }
        
        # Swedish-specific validation patterns
        self.swedish_patterns = {
            'valid_fee_keywords': [
                'avgift', 'taxa', 'kostnad', 'pris', 'handläggning',
                'prövning', 'ansökan', 'tillsyn', 'kontroll', 'besiktning'
            ],
            'invalid_content': [
                'cookie', 'gdpr', 'privacy', 'policy', 'terms',
                'navigation', 'menu', 'footer', 'header', 'sidebar'
            ]
        }
    
    def process_item(self, item, spider):
        """Process and validate an extracted fee item"""
        self.stats['total_processed'] += 1
        
        try:
            # Perform comprehensive validation
            validation_result = self._validate_item(item)
            
            if validation_result['is_valid']:
                # Enhance item with validation metadata
                item = self._enhance_item(item, validation_result)
                self.stats['total_valid'] += 1
                
                # Update statistics
                self._update_statistics(item, validation_result)
                
                return item
            else:
                # Log validation failure
                self._log_validation_failure(item, validation_result)
                self.stats['total_invalid'] += 1
                
                # Drop invalid item
                raise DropItem(f"Validation failed: {validation_result['errors']}")
        
        except Exception as e:
            self.logger.error(f"Validation pipeline error: {e}")
            self.stats['total_invalid'] += 1
            raise DropItem(f"Validation pipeline error: {e}")
    
    def _validate_item(self, item):
        """Perform comprehensive validation on an item"""
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'confidence_score': 0.0,
            'validation_scores': {}
        }
        
        total_weight = 0
        weighted_score = 0
        
        # Apply each validation rule
        for rule_name, rule_config in self.validation_rules.items():
            rule_result = self._apply_validation_rule(item, rule_name, rule_config)
            
            validation_result['validation_scores'][rule_name] = rule_result
            
            if rule_result['is_valid']:
                weighted_score += rule_result['score'] * rule_config['weight']
            else:
                validation_result['errors'].extend(rule_result['errors'])
                if rule_result['critical']:
                    validation_result['is_valid'] = False
            
            if rule_result['warnings']:
                validation_result['warnings'].extend(rule_result['warnings'])
            
            total_weight += rule_config['weight']
        
        # Calculate overall confidence score
        if total_weight > 0:
            validation_result['confidence_score'] = weighted_score / total_weight
        
        # Apply Swedish-specific validation
        swedish_result = self._validate_swedish_content(item)
        validation_result['validation_scores']['swedish_content'] = swedish_result
        
        if not swedish_result['is_valid']:
            validation_result['errors'].extend(swedish_result['errors'])
            validation_result['is_valid'] = False
        
        return validation_result
    
    def _apply_validation_rule(self, item, rule_name, rule_config):
        """Apply a specific validation rule"""
        result = {
            'is_valid': True,
            'score': 1.0,
            'errors': [],
            'warnings': [],
            'critical': False
        }
        
        try:
            if rule_name == 'required_fields':
                result = self._validate_required_fields(item, rule_config)
            elif rule_name == 'amount_validation':
                result = self._validate_amount(item, rule_config)
            elif rule_name == 'fee_name_validation':
                result = self._validate_fee_name(item, rule_config)
            elif rule_name == 'currency_validation':
                result = self._validate_currency(item, rule_config)
            elif rule_name == 'url_validation':
                result = self._validate_url(item, rule_config)
            elif rule_name == 'category_validation':
                result = self._validate_category(item, rule_config)
        
        except Exception as e:
            result = {
                'is_valid': False,
                'score': 0.0,
                'errors': [f"Validation rule {rule_name} failed: {e}"],
                'warnings': [],
                'critical': True
            }
        
        return result
    
    def _validate_required_fields(self, item, config):
        """Validate required fields are present"""
        result = {'is_valid': True, 'score': 1.0, 'errors': [], 'warnings': [], 'critical': True}
        
        missing_fields = []
        for field in config['fields']:
            if field not in item or not item[field]:
                missing_fields.append(field)
        
        if missing_fields:
            result['is_valid'] = False
            result['score'] = 0.0
            result['errors'].append(f"Missing required fields: {missing_fields}")
        
        return result
    
    def _validate_amount(self, item, config):
        """Validate fee amount"""
        result = {'is_valid': True, 'score': 1.0, 'errors': [], 'warnings': [], 'critical': True}
        
        try:
            amount = float(item.get('amount', 0))
            
            if amount < config['min_amount']:
                result['is_valid'] = False
                result['errors'].append(f"Amount {amount} below minimum {config['min_amount']}")
            elif amount > config['max_amount']:
                result['is_valid'] = False
                result['errors'].append(f"Amount {amount} above maximum {config['max_amount']}")
            elif amount < 50:
                result['warnings'].append(f"Amount {amount} is unusually low")
                result['score'] = 0.7
            elif amount > 100000:
                result['warnings'].append(f"Amount {amount} is unusually high")
                result['score'] = 0.8
            
            # Additional validation using validators
            if not self.validators.validate_fee_amount(amount):
                result['is_valid'] = False
                result['errors'].append(f"Amount {amount} failed validator check")
        
        except (ValueError, TypeError):
            result['is_valid'] = False
            result['score'] = 0.0
            result['errors'].append(f"Invalid amount format: {item.get('amount')}")
        
        return result
    
    def _validate_fee_name(self, item, config):
        """Validate fee name"""
        result = {'is_valid': True, 'score': 1.0, 'errors': [], 'warnings': [], 'critical': True}
        
        fee_name = str(item.get('fee_name', '')).strip()
        
        # Length validation
        if len(fee_name) < config['min_length']:
            result['is_valid'] = False
            result['errors'].append(f"Fee name too short: {len(fee_name)} < {config['min_length']}")
        elif len(fee_name) > config['max_length']:
            result['warnings'].append(f"Fee name very long: {len(fee_name)} > {config['max_length']}")
            result['score'] = 0.8
        
        # Forbidden patterns
        fee_name_lower = fee_name.lower()
        for pattern in config['forbidden_patterns']:
            if re.search(pattern, fee_name_lower):
                result['is_valid'] = False
                result['errors'].append(f"Fee name contains forbidden pattern: {pattern}")
        
        # Check for meaningful content
        if re.match(r'^[\d\s\-_.,]+$', fee_name):
            result['is_valid'] = False
            result['errors'].append("Fee name contains only numbers and punctuation")
        
        # Check for Swedish content
        if not any(keyword in fee_name_lower for keyword in self.swedish_patterns['valid_fee_keywords']):
            result['warnings'].append("Fee name doesn't contain common Swedish fee keywords")
            result['score'] = 0.7
        
        return result
    
    def _validate_currency(self, item, config):
        """Validate currency"""
        result = {'is_valid': True, 'score': 1.0, 'errors': [], 'warnings': [], 'critical': False}
        
        currency = str(item.get('currency', '')).strip()
        
        if currency not in config['allowed_currencies']:
            result['warnings'].append(f"Unexpected currency: {currency}")
            result['score'] = 0.8
        
        # Normalize currency
        if currency.lower() in ['kr', 'kronor']:
            item['currency'] = 'SEK'
        
        return result
    
    def _validate_url(self, item, config):
        """Validate source URL"""
        result = {'is_valid': True, 'score': 1.0, 'errors': [], 'warnings': [], 'critical': False}
        
        url = str(item.get('source_url', '')).strip()
        
        if not url:
            result['is_valid'] = False
            result['errors'].append("Missing source URL")
            return result
        
        # Check for Swedish domain
        if not any(domain in url.lower() for domain in config['required_domains']):
            result['warnings'].append(f"URL doesn't appear to be Swedish: {url}")
            result['score'] = 0.8
        
        # Basic URL format validation
        if not re.match(r'https?://', url):
            result['warnings'].append(f"URL missing protocol: {url}")
            result['score'] = 0.9
        
        return result
    
    def _validate_category(self, item, config):
        """Validate category"""
        result = {'is_valid': True, 'score': 1.0, 'errors': [], 'warnings': [], 'critical': False}
        
        category = str(item.get('category', '')).strip().lower()
        
        if category and category not in config['valid_categories']:
            result['warnings'].append(f"Unknown category: {category}")
            result['score'] = 0.9
        
        return result
    
    def _validate_swedish_content(self, item):
        """Validate Swedish-specific content"""
        result = {'is_valid': True, 'score': 1.0, 'errors': [], 'warnings': []}
        
        # Check fee name for Swedish characteristics
        fee_name = str(item.get('fee_name', '')).lower()
        description = str(item.get('description', '')).lower()
        
        # Check for invalid content
        for invalid_term in self.swedish_patterns['invalid_content']:
            if invalid_term in fee_name or invalid_term in description:
                result['is_valid'] = False
                result['errors'].append(f"Content contains invalid term: {invalid_term}")
        
        # Check for Swedish characters
        swedish_chars = ['å', 'ä', 'ö']
        has_swedish_chars = any(char in fee_name + description for char in swedish_chars)
        
        if not has_swedish_chars and len(fee_name) > 20:
            result['warnings'].append("Content lacks Swedish characters")
            result['score'] = 0.8
        
        return result
    
    def _enhance_item(self, item, validation_result):
        """Enhance item with validation metadata"""
        # Add validation metadata
        item['validation'] = {
            'confidence_score': validation_result['confidence_score'],
            'validation_date': datetime.now().isoformat(),
            'validation_version': '2.0',
            'warnings': validation_result['warnings'],
            'validation_scores': validation_result['validation_scores']
        }
        
        # Enhance confidence based on extraction method
        extraction_method = item.get('extraction_method', '')
        if 'playwright' in extraction_method:
            item['validation']['confidence_score'] += 0.05
        elif 'table' in extraction_method:
            item['validation']['confidence_score'] += 0.1
        elif 'pdf' in extraction_method:
            item['validation']['confidence_score'] += 0.15
        
        # Cap confidence at 1.0
        item['validation']['confidence_score'] = min(item['validation']['confidence_score'], 1.0)
        
        # Add quality indicators
        item['quality'] = self._calculate_quality_indicators(item, validation_result)
        
        return item
    
    def _calculate_quality_indicators(self, item, validation_result):
        """Calculate quality indicators for the item"""
        quality = {
            'overall_score': validation_result['confidence_score'],
            'data_completeness': 0.0,
            'content_quality': 0.0,
            'source_reliability': 0.0
        }
        
        # Data completeness
        optional_fields = ['category', 'description', 'unit', 'extraction_method']
        present_optional = sum(1 for field in optional_fields if item.get(field))
        quality['data_completeness'] = present_optional / len(optional_fields)
        
        # Content quality
        fee_name = str(item.get('fee_name', ''))
        description = str(item.get('description', ''))
        
        content_score = 0.5  # Base score
        
        # Boost for longer, more descriptive names
        if len(fee_name) > 20:
            content_score += 0.1
        if len(description) > 50:
            content_score += 0.1
        
        # Boost for Swedish keywords
        swedish_keyword_count = sum(1 for keyword in self.swedish_patterns['valid_fee_keywords']
                                  if keyword in fee_name.lower() or keyword in description.lower())
        content_score += min(swedish_keyword_count * 0.1, 0.3)
        
        quality['content_quality'] = min(content_score, 1.0)
        
        # Source reliability
        extraction_method = item.get('extraction_method', '')
        source_type = item.get('source_type', '')
        
        reliability_score = 0.5  # Base score
        
        if 'pdf' in extraction_method.lower():
            reliability_score += 0.2
        elif 'table' in extraction_method.lower():
            reliability_score += 0.15
        elif 'playwright' in extraction_method.lower():
            reliability_score += 0.1
        
        if source_type == 'PDF':
            reliability_score += 0.1
        
        quality['source_reliability'] = min(reliability_score, 1.0)
        
        return quality
    
    def _update_statistics(self, item, validation_result):
        """Update validation statistics"""
        confidence = validation_result['confidence_score']
        
        # Confidence distribution
        if confidence >= 0.8:
            self.stats['confidence_distribution']['high'] += 1
        elif confidence >= 0.6:
            self.stats['confidence_distribution']['medium'] += 1
        else:
            self.stats['confidence_distribution']['low'] += 1
        
        # Extraction methods
        method = item.get('extraction_method', 'unknown')
        self.stats['extraction_methods'][method] = self.stats['extraction_methods'].get(method, 0) + 1
        
        # Categories
        category = item.get('category', 'unknown')
        self.stats['categories'][category] = self.stats['categories'].get(category, 0) + 1
    
    def _log_validation_failure(self, item, validation_result):
        """Log validation failure details"""
        self.logger.warning(f"Validation failed for item: {item.get('fee_name', 'Unknown')}")
        
        for error in validation_result['errors']:
            self.logger.warning(f"  Error: {error}")
            
            # Track error types
            error_type = error.split(':')[0] if ':' in error else error
            self.stats['validation_errors'][error_type] = self.stats['validation_errors'].get(error_type, 0) + 1
    
    def close_spider(self, spider):
        """Log final validation statistics"""
        self.logger.info("=== Enhanced Validation Pipeline Statistics ===")
        self.logger.info(f"Total processed: {self.stats['total_processed']}")
        self.logger.info(f"Total valid: {self.stats['total_valid']}")
        self.logger.info(f"Total invalid: {self.stats['total_invalid']}")
        
        if self.stats['total_processed'] > 0:
            success_rate = (self.stats['total_valid'] / self.stats['total_processed']) * 100
            self.logger.info(f"Success rate: {success_rate:.1f}%")
        
        # Confidence distribution
        self.logger.info("Confidence distribution:")
        for level, count in self.stats['confidence_distribution'].items():
            self.logger.info(f"  {level}: {count}")
        
        # Top extraction methods
        self.logger.info("Extraction methods:")
        for method, count in sorted(self.stats['extraction_methods'].items(), 
                                  key=lambda x: x[1], reverse=True)[:5]:
            self.logger.info(f"  {method}: {count}")
        
        # Top categories
        self.logger.info("Categories:")
        for category, count in sorted(self.stats['categories'].items(), 
                                    key=lambda x: x[1], reverse=True)[:5]:
            self.logger.info(f"  {category}: {count}")
        
        # Top validation errors
        if self.stats['validation_errors']:
            self.logger.info("Top validation errors:")
            for error, count in sorted(self.stats['validation_errors'].items(), 
                                     key=lambda x: x[1], reverse=True)[:5]:
                self.logger.info(f"  {error}: {count}")

# Import DropItem for pipeline
try:
    from scrapy.exceptions import DropItem
except ImportError:
    class DropItem(Exception):
        pass 