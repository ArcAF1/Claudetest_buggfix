#!/usr/bin/env python3
"""
Phase 1 Duplicate Detection Pipeline
Ensures one entry per municipality for Phase 1 data and keeps the highest quality version.
"""

import logging
import hashlib
from datetime import datetime
from scrapy.exceptions import DropItem
from typing import Dict, Optional

class Phase1DuplicatesPipeline:
    """Detect and handle duplicates for Phase 1 data - one entry per municipality"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.seen_municipalities = {}
        self.duplicates_removed = 0
        self.replacements_made = 0
        self.total_processed = 0
        
        # Quality comparison weights
        self.quality_weights = {
            'completeness_score': 0.4,    # 40% weight for completeness
            'data_quality': 0.3,          # 30% weight for data quality
            'confidence': 0.2,            # 20% weight for extraction confidence
            'source_quality': 0.1         # 10% weight for source quality
        }
    
    def process_item(self, item, spider):
        """Process item and handle duplicates"""
        try:
            self.total_processed += 1
            municipality = item.get('municipality', '').strip()
            
            if not municipality:
                spider.logger.warning("Item without municipality name - rejecting")
                raise DropItem("Missing municipality name")
            
            # Normalize municipality name for comparison
            normalized_municipality = self._normalize_municipality_name(municipality)
            
            if normalized_municipality in self.seen_municipalities:
                existing_item = self.seen_municipalities[normalized_municipality]
                
                # Compare quality and decide which to keep
                if self._should_replace_existing(existing_item, item, spider):
                    self.seen_municipalities[normalized_municipality] = item
                    self.replacements_made += 1
                    spider.logger.info(f"Replaced {municipality} data with higher quality version "
                                     f"(quality: {existing_item.get('data_quality', 0):.1f} -> "
                                     f"{item.get('data_quality', 0):.1f})")
                    return item
                else:
                    self.duplicates_removed += 1
                    spider.logger.debug(f"Duplicate municipality {municipality} - keeping existing higher quality data")
                    raise DropItem(f"Duplicate municipality: {municipality} (lower quality)")
            else:
                # First time seeing this municipality
                self.seen_municipalities[normalized_municipality] = item
                spider.logger.debug(f"First entry for municipality: {municipality}")
                return item
                
        except DropItem:
            raise
        except Exception as e:
            self.logger.error(f"Error processing duplicate detection: {e}")
            # Don't drop the item for processing errors, just log and continue
            return item
    
    def _normalize_municipality_name(self, municipality: str) -> str:
        """Normalize municipality name for consistent comparison"""
        if not municipality:
            return ""
        
        # Convert to lowercase and strip whitespace
        normalized = municipality.lower().strip()
        
        # Remove common variations
        normalized = normalized.replace(' kommun', '')
        normalized = normalized.replace(' stad', '')
        normalized = normalized.replace('kommun ', '')
        normalized = normalized.replace('stad ', '')
        
        # Handle special characters
        char_replacements = {
            'å': 'a', 'ä': 'a', 'ö': 'o',
            'é': 'e', 'è': 'e', 'ü': 'u'
        }
        
        for old_char, new_char in char_replacements.items():
            normalized = normalized.replace(old_char, new_char)
        
        # Remove extra spaces
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def _should_replace_existing(self, existing: Dict, new: Dict, spider) -> bool:
        """Determine if new item should replace existing based on quality metrics"""
        try:
            existing_score = self._calculate_overall_quality_score(existing)
            new_score = self._calculate_overall_quality_score(new)
            
            spider.logger.debug(f"Quality comparison for {new.get('municipality')}: "
                              f"existing={existing_score:.2f}, new={new_score:.2f}")
            
            # Replace if new item has significantly better quality (5% threshold)
            return new_score > existing_score + 0.05
            
        except Exception as e:
            self.logger.error(f"Error comparing item quality: {e}")
            # If we can't compare, keep existing
            return False
    
    def _calculate_overall_quality_score(self, item: Dict) -> float:
        """Calculate overall quality score for comparison"""
        score = 0.0
        
        # Completeness score (0-1)
        completeness = item.get('completeness_score', 0)
        score += completeness * self.quality_weights['completeness_score']
        
        # Data quality (0-100, normalize to 0-1)
        data_quality = item.get('data_quality', 0) / 100.0
        score += data_quality * self.quality_weights['data_quality']
        
        # Extraction confidence (0-1)
        confidence = item.get('confidence', 0)
        score += confidence * self.quality_weights['confidence']
        
        # Source quality (0-1)
        source_quality = self._assess_source_quality(item)
        score += source_quality * self.quality_weights['source_quality']
        
        return score
    
    def _assess_source_quality(self, item: Dict) -> float:
        """Assess source quality (0-1 scale)"""
        source_url = item.get('source_url', '')
        source_type = item.get('source_type', '')
        extraction_method = item.get('extraction_method', '')
        
        quality = 0.0
        
        # Source type quality
        if source_type == 'PDF':
            quality += 0.4  # PDFs often more reliable
        elif source_type == 'HTML':
            quality += 0.3
        
        # URL quality
        if '.se' in source_url:
            quality += 0.2  # Swedish domain
        if any(term in source_url.lower() for term in ['kommun', 'stad']):
            quality += 0.2  # Official municipal domain
        
        # Extraction method quality
        if 'pdf' in extraction_method.lower():
            quality += 0.1
        if 'enhanced' in extraction_method.lower():
            quality += 0.1
        
        return min(quality, 1.0)
    
    def _create_item_fingerprint(self, item: Dict) -> str:
        """Create a fingerprint for the item based on its content"""
        # Create fingerprint based on municipality and key data
        fingerprint_data = {
            'municipality': item.get('municipality', ''),
            'timtaxa_livsmedel': item.get('timtaxa_livsmedel'),
            'debitering_livsmedel': item.get('debitering_livsmedel'),
            'timtaxa_bygglov': item.get('timtaxa_bygglov'),
            'source_url': item.get('source_url', '')
        }
        
        # Convert to string and hash
        fingerprint_str = str(sorted(fingerprint_data.items()))
        return hashlib.md5(fingerprint_str.encode('utf-8')).hexdigest()
    
    def get_duplicate_statistics(self) -> Dict:
        """Get statistics about duplicate detection"""
        return {
            'total_processed': self.total_processed,
            'unique_municipalities': len(self.seen_municipalities),
            'duplicates_removed': self.duplicates_removed,
            'replacements_made': self.replacements_made,
            'duplicate_rate': (self.duplicates_removed / self.total_processed * 100) if self.total_processed > 0 else 0
        }
    
    def get_municipality_summary(self) -> Dict:
        """Get summary of municipalities and their data quality"""
        summary = {}
        
        for municipality, item in self.seen_municipalities.items():
            summary[municipality] = {
                'completeness_score': item.get('completeness_score', 0),
                'data_quality': item.get('data_quality', 0),
                'confidence': item.get('confidence', 0),
                'status': item.get('status', 'unknown'),
                'source_type': item.get('source_type', 'unknown'),
                'fields_found': item.get('phase1_fields_found', 0)
            }
        
        return summary
    
    def close_spider(self, spider):
        """Log duplicate detection statistics"""
        stats = self.get_duplicate_statistics()
        
        spider.logger.info("=== Phase 1 Duplicate Detection Statistics ===")
        spider.logger.info(f"Total items processed: {stats['total_processed']}")
        spider.logger.info(f"Unique municipalities: {stats['unique_municipalities']}")
        spider.logger.info(f"Duplicates removed: {stats['duplicates_removed']}")
        spider.logger.info(f"Quality replacements made: {stats['replacements_made']}")
        spider.logger.info(f"Duplicate rate: {stats['duplicate_rate']:.1f}%")
        
        if stats['total_processed'] > 0:
            retention_rate = (stats['unique_municipalities'] / stats['total_processed']) * 100
            spider.logger.info(f"Data retention rate: {retention_rate:.1f}%")
        
        # Log quality distribution of final dataset
        summary = self.get_municipality_summary()
        if summary:
            complete_count = sum(1 for item in summary.values() if item['status'] == 'complete')
            partial_count = sum(1 for item in summary.values() if item['status'] == 'partial')
            
            spider.logger.info(f"\nFinal Dataset Quality:")
            spider.logger.info(f"  Complete municipalities: {complete_count} "
                             f"({complete_count/len(summary)*100:.1f}%)")
            spider.logger.info(f"  Partial municipalities: {partial_count} "
                             f"({partial_count/len(summary)*100:.1f}%)")
            
            # Average quality metrics
            avg_completeness = sum(item['completeness_score'] for item in summary.values()) / len(summary)
            avg_quality = sum(item['data_quality'] for item in summary.values()) / len(summary)
            avg_confidence = sum(item['confidence'] for item in summary.values()) / len(summary)
            
            spider.logger.info(f"  Average completeness: {avg_completeness:.2f}")
            spider.logger.info(f"  Average data quality: {avg_quality:.1f}%")
            spider.logger.info(f"  Average confidence: {avg_confidence:.2f}")
        
        spider.logger.info("=== End Duplicate Detection Statistics ===")

class Phase1ItemMerger:
    """Helper class to merge multiple items for the same municipality"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def merge_items(self, primary_item: Dict, secondary_item: Dict) -> Dict:
        """Merge two items for the same municipality, keeping best data from each"""
        merged = primary_item.copy()
        
        # Merge Phase 1 fields - keep the one with higher confidence for each field
        phase1_fields = ['timtaxa_livsmedel', 'debitering_livsmedel', 'timtaxa_bygglov']
        
        for field in phase1_fields:
            primary_value = primary_item.get(field)
            secondary_value = secondary_item.get(field)
            
            # If primary doesn't have the field but secondary does, use secondary
            if not primary_value and secondary_value:
                merged[field] = secondary_value
                merged[f'{field}_source'] = secondary_item.get('source_url', '')
            
            # If both have the field, keep the one with higher confidence
            elif primary_value and secondary_value:
                primary_confidence = primary_item.get('confidence', 0)
                secondary_confidence = secondary_item.get('confidence', 0)
                
                if secondary_confidence > primary_confidence:
                    merged[field] = secondary_value
                    merged[f'{field}_source'] = secondary_item.get('source_url', '')
        
        # Recalculate completeness and quality
        fields_present = sum(1 for field in phase1_fields if merged.get(field))
        merged['completeness_score'] = fields_present / 3.0
        merged['phase1_fields_found'] = fields_present
        
        # Update status
        if fields_present == 3:
            merged['status'] = 'complete'
        elif fields_present > 0:
            merged['status'] = 'partial'
        else:
            merged['status'] = 'empty'
        
        # Add merge metadata
        merged['merged_from_sources'] = [
            primary_item.get('source_url', ''),
            secondary_item.get('source_url', '')
        ]
        merged['merge_date'] = datetime.now().isoformat()
        
        self.logger.debug(f"Merged items for {merged.get('municipality')}: "
                         f"{fields_present}/3 fields after merge")
        
        return merged 