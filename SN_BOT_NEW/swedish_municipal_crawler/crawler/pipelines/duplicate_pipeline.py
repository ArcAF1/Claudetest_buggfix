import hashlib
import logging
try:  # Scrapy may not be installed when running tests
    from scrapy.exceptions import DropItem
except Exception:  # pragma: no cover - fallback
    class DropItem(Exception):
        pass

class DuplicatesPipeline:
    """Pipeline to filter out duplicate fee items"""
    
    def __init__(self):
        self.seen_items = set()
        self.logger = logging.getLogger(__name__)
        self.stats = {
            'unique_items': 0,
            'duplicate_items': 0
        }
    
    def process_item(self, item, spider):
        """Check for duplicates and filter them out"""
        # Create a hash based on key fields
        key_fields = [
            item.get('municipality', ''),
            item.get('fee_name', ''),
            item.get('amount', ''),
            item.get('category', ''),
            item.get('source_url', '')
        ]
        
        # Create hash from key fields
        item_hash = hashlib.md5('|'.join(key_fields).encode('utf-8')).hexdigest()
        
        if item_hash in self.seen_items:
            self.stats['duplicate_items'] += 1
            self.logger.debug(f"Duplicate item found: {item.get('fee_name', 'Unknown')} "
                            f"from {item.get('municipality', 'Unknown')}")
            raise DropItem(f"Duplicate item: {item_hash}")
        else:
            self.seen_items.add(item_hash)
            self.stats['unique_items'] += 1
            return item
    
    def close_spider(self, spider):
        """Log duplicate statistics"""
        total_processed = self.stats['unique_items'] + self.stats['duplicate_items']
        if total_processed > 0:
            duplicate_percentage = (self.stats['duplicate_items'] / total_processed) * 100
            self.logger.info(f"Duplicate filtering complete:")
            self.logger.info(f"  Unique items: {self.stats['unique_items']}")
            self.logger.info(f"  Duplicates removed: {self.stats['duplicate_items']}")
            self.logger.info(f"  Duplicate rate: {duplicate_percentage:.1f}%") 