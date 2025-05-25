import hashlib
import re
import logging
from datetime import datetime
from scrapy.exceptions import DropItem

class EnhancedDuplicatesPipeline:
    """Enhanced duplicate detection with intelligent merging and quality scoring"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.seen_fees = {}
        self.duplicates_removed = 0
        self.duplicates_merged = 0
        self.quality_upgrades = 0
        
        # Duplicate detection strategies
        self.detection_strategies = [
            'exact_match',
            'fuzzy_match',
            'semantic_match'
        ]
        
        # Quality indicators for comparison
        self.quality_weights = {
            'confidence': 0.3,
            'validation_score': 0.25,
            'extraction_method': 0.2,
            'data_completeness': 0.15,
            'source_reliability': 0.1
        }
    
    def process_item(self, item, spider):
        """Enhanced duplicate detection with intelligent merging"""
        try:
            # Create multiple fingerprints for different detection strategies
            fingerprints = self._create_fingerprints(item)
            
            # Check for duplicates using different strategies
            duplicate_found = False
            best_match = None
            best_strategy = None
            
            for strategy, fingerprint in fingerprints.items():
                if fingerprint in self.seen_fees:
                    existing_item = self.seen_fees[fingerprint]
                    duplicate_found = True
                    best_match = existing_item
                    best_strategy = strategy
                    break
            
            if duplicate_found:
                # Decide whether to merge, replace, or drop
                action = self._determine_action(best_match, item, best_strategy)
                
                if action == 'replace':
                    # Replace with higher quality item
                    self._replace_item(best_match, item, fingerprints)
                    self.quality_upgrades += 1
                    self.logger.debug(f"Replaced duplicate with higher quality version: {item.get('fee_name', 'Unknown')}")
                    return item
                
                elif action == 'merge':
                    # Merge items to create enhanced version
                    merged_item = self._merge_items(best_match, item)
                    self._replace_item(best_match, merged_item, fingerprints)
                    self.duplicates_merged += 1
                    self.logger.debug(f"Merged duplicate items: {item.get('fee_name', 'Unknown')}")
                    return merged_item
                
                else:  # action == 'drop'
                    self.duplicates_removed += 1
                    raise DropItem(f"Duplicate fee (lower quality): {item.get('fee_name', 'Unknown')}")
            
            else:
                # No duplicate found, store all fingerprints
                for strategy, fingerprint in fingerprints.items():
                    self.seen_fees[fingerprint] = item
                
                return item
        
        except Exception as e:
            self.logger.error(f"Error in duplicate detection: {e}")
            return item
    
    def _create_fingerprints(self, item):
        """Create multiple fingerprints for different detection strategies"""
        fingerprints = {}
        
        # Extract key fields
        municipality = self._normalize_text(item.get('municipality', ''))
        fee_name = self._normalize_text(item.get('fee_name', ''))
        amount = self._normalize_amount(item.get('amount', 0))
        unit = self._normalize_text(item.get('unit', 'kr'))
        
        # Strategy 1: Exact match
        exact_str = f"{municipality}|{fee_name}|{amount}|{unit}"
        fingerprints['exact_match'] = hashlib.md5(exact_str.encode()).hexdigest()
        
        # Strategy 2: Fuzzy match (ignore minor variations)
        fuzzy_fee_name = self._fuzzy_normalize(fee_name)
        fuzzy_str = f"{municipality}|{fuzzy_fee_name}|{amount}|{unit}"
        fingerprints['fuzzy_match'] = hashlib.md5(fuzzy_str.encode()).hexdigest()
        
        # Strategy 3: Semantic match (focus on core meaning)
        semantic_fee_name = self._semantic_normalize(fee_name)
        semantic_str = f"{municipality}|{semantic_fee_name}|{amount}"
        fingerprints['semantic_match'] = hashlib.md5(semantic_str.encode()).hexdigest()
        
        return fingerprints
    
    def _normalize_text(self, text):
        """Basic text normalization"""
        if not text:
            return ""
        return re.sub(r'\s+', ' ', str(text).lower().strip())
    
    def _normalize_amount(self, amount):
        """Normalize amount for comparison"""
        try:
            # Round to nearest 10 for fuzzy matching
            return str(int(round(float(amount), -1)))
        except (ValueError, TypeError):
            return "0"
    
    def _fuzzy_normalize(self, text):
        """Fuzzy normalization for minor variations"""
        if not text:
            return ""
        
        # Remove common variations
        text = re.sub(r'\b(för|av|till|från|med|utan|per)\b', '', text)
        text = re.sub(r'\b(avgift|taxa|kostnad|pris|belopp)\b', 'avgift', text)
        text = re.sub(r'\b(kr|kronor|sek)\b', '', text)
        text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _semantic_normalize(self, text):
        """Semantic normalization for core meaning"""
        if not text:
            return ""
        
        # Extract key semantic components
        semantic_keywords = [
            'bygglov', 'miljötillstånd', 'serveringstillstånd', 'näringstillstånd',
            'hemtjänst', 'äldreomsorg', 'barnomsorg', 'förskola',
            'vatten', 'avlopp', 'renhållning', 'parkering',
            'nybyggnad', 'tillbyggnad', 'ändring', 'rivning'
        ]
        
        text_lower = text.lower()
        found_keywords = [kw for kw in semantic_keywords if kw in text_lower]
        
        if found_keywords:
            return ' '.join(sorted(found_keywords))
        else:
            # Fallback to first few significant words
            words = re.findall(r'\b\w{3,}\b', text_lower)
            return ' '.join(words[:3])
    
    def _determine_action(self, existing_item, new_item, strategy):
        """Determine what action to take with duplicate"""
        existing_quality = self._calculate_quality_score(existing_item)
        new_quality = self._calculate_quality_score(new_item)
        
        quality_diff = new_quality - existing_quality
        
        # If new item is significantly better, replace
        if quality_diff > 0.15:
            return 'replace'
        
        # If items are similar quality, merge
        elif abs(quality_diff) <= 0.15:
            return 'merge'
        
        # If existing item is better, drop new one
        else:
            return 'drop'
    
    def _calculate_quality_score(self, item):
        """Calculate overall quality score for an item"""
        score = 0.0
        
        # Confidence score
        confidence = item.get('validation', {}).get('confidence_score', item.get('confidence', 0.5))
        score += confidence * self.quality_weights['confidence']
        
        # Validation score
        validation_score = item.get('quality', {}).get('overall_score', 0.5)
        score += validation_score * self.quality_weights['validation_score']
        
        # Extraction method quality
        method_score = self._score_extraction_method(item.get('extraction_method', ''))
        score += method_score * self.quality_weights['extraction_method']
        
        # Data completeness
        completeness_score = self._score_data_completeness(item)
        score += completeness_score * self.quality_weights['data_completeness']
        
        # Source reliability
        reliability_score = self._score_source_reliability(item)
        score += reliability_score * self.quality_weights['source_reliability']
        
        return min(score, 1.0)
    
    def _score_extraction_method(self, method):
        """Score extraction method reliability"""
        method_scores = {
            'pdf': 0.9,
            'bygglov': 0.95,
            'table': 0.8,
            'playwright': 0.7,
            'ajax': 0.6,
            'enhanced': 0.75,
            'generic': 0.5
        }
        
        method_lower = method.lower()
        for key, score in method_scores.items():
            if key in method_lower:
                return score
        
        return 0.4  # Default for unknown methods
    
    def _score_data_completeness(self, item):
        """Score based on data completeness"""
        important_fields = [
            'fee_name', 'amount', 'currency', 'category', 'description',
            'source_url', 'extraction_method', 'municipality'
        ]
        
        present_fields = sum(1 for field in important_fields if item.get(field))
        return present_fields / len(important_fields)
    
    def _score_source_reliability(self, item):
        """Score source reliability"""
        source_url = item.get('source_url', '')
        source_type = item.get('source_type', '')
        
        score = 0.5  # Base score
        
        # PDF sources are generally more reliable
        if source_type == 'PDF' or source_url.endswith('.pdf'):
            score += 0.3
        
        # Official municipal domains
        if '.se' in source_url and any(term in source_url for term in ['kommun', 'stad']):
            score += 0.2
        
        return min(score, 1.0)
    
    def _merge_items(self, existing_item, new_item):
        """Intelligently merge two similar items"""
        merged_item = existing_item.copy()
        
        # Merge strategy: take the best value for each field
        for key, new_value in new_item.items():
            if key not in merged_item or not merged_item[key]:
                # Take new value if existing is missing
                merged_item[key] = new_value
            elif new_value and len(str(new_value)) > len(str(merged_item[key])):
                # Take new value if it's more detailed
                merged_item[key] = new_value
        
        # Merge validation metadata
        if 'validation' in new_item and 'validation' in existing_item:
            merged_validation = existing_item['validation'].copy()
            
            # Take higher confidence score
            if new_item['validation'].get('confidence_score', 0) > merged_validation.get('confidence_score', 0):
                merged_validation['confidence_score'] = new_item['validation']['confidence_score']
            
            # Merge warnings
            existing_warnings = set(merged_validation.get('warnings', []))
            new_warnings = set(new_item['validation'].get('warnings', []))
            merged_validation['warnings'] = list(existing_warnings.union(new_warnings))
            
            merged_item['validation'] = merged_validation
        
        # Update extraction metadata
        merged_item['extraction_date'] = datetime.now().isoformat()
        merged_item['extraction_method'] = f"merged_{existing_item.get('extraction_method', 'unknown')}"
        
        return merged_item
    
    def _replace_item(self, old_item, new_item, fingerprints):
        """Replace old item with new item in all fingerprint mappings"""
        # Remove old fingerprints
        old_fingerprints = self._create_fingerprints(old_item)
        for fingerprint in old_fingerprints.values():
            if fingerprint in self.seen_fees:
                del self.seen_fees[fingerprint]
        
        # Add new fingerprints
        for fingerprint in fingerprints.values():
            self.seen_fees[fingerprint] = new_item
    
    def close_spider(self, spider):
        """Log duplicate detection statistics"""
        total_processed = len(self.seen_fees) + self.duplicates_removed
        
        self.logger.info("=== Enhanced Duplicate Detection Statistics ===")
        self.logger.info(f"Total items processed: {total_processed}")
        self.logger.info(f"Unique items kept: {len(self.seen_fees)}")
        self.logger.info(f"Duplicates removed: {self.duplicates_removed}")
        self.logger.info(f"Items merged: {self.duplicates_merged}")
        self.logger.info(f"Quality upgrades: {self.quality_upgrades}")
        
        if total_processed > 0:
            dedup_rate = (self.duplicates_removed / total_processed) * 100
            self.logger.info(f"Deduplication rate: {dedup_rate:.1f}%") 