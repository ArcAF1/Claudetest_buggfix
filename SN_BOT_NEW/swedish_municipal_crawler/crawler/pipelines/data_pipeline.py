import json
import csv
import pandas as pd
from datetime import datetime
import logging
import os

class SwedishFeeDataPipeline:
    """Main data processing pipeline for Swedish municipal fees"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.items = []
        self.output_dir = 'data/output'
        self.stats = {
            'total_items': 0,
            'municipalities_processed': set(),
            'categories': {},
            'cms_types': {},
            'source_types': {}
        }
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
    
    def process_item(self, item, spider):
        """Process and collect items for batch output"""
        self.items.append(dict(item))
        self.stats['total_items'] += 1
        
        # Update statistics
        municipality = item.get('municipality', 'Unknown')
        self.stats['municipalities_processed'].add(municipality)
        
        category = item.get('category', 'Unknown')
        self.stats['categories'][category] = self.stats['categories'].get(category, 0) + 1
        
        cms_type = item.get('cms_type', 'Unknown')
        self.stats['cms_types'][cms_type] = self.stats['cms_types'].get(cms_type, 0) + 1
        
        source_type = item.get('source_type', 'Unknown')
        self.stats['source_types'][source_type] = self.stats['source_types'].get(source_type, 0) + 1
        
        return item
    
    def close_spider(self, spider):
        """Save all collected data when spider closes"""
        if not self.items:
            self.logger.warning("No items to save")
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save as JSON
        json_file = os.path.join(self.output_dir, f'swedish_municipal_fees_{timestamp}.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.items, f, indent=2, ensure_ascii=False)
        
        # Save as CSV
        csv_file = os.path.join(self.output_dir, f'swedish_municipal_fees_{timestamp}.csv')
        df = pd.DataFrame(self.items)
        df.to_csv(csv_file, index=False, encoding='utf-8')
        
        # Save summary statistics
        stats_file = os.path.join(self.output_dir, f'crawl_statistics_{timestamp}.json')
        summary_stats = {
            'crawl_timestamp': timestamp,
            'total_items': self.stats['total_items'],
            'municipalities_count': len(self.stats['municipalities_processed']),
            'municipalities_list': list(self.stats['municipalities_processed']),
            'categories': self.stats['categories'],
            'cms_types': self.stats['cms_types'],
            'source_types': self.stats['source_types']
        }
        
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(summary_stats, f, indent=2, ensure_ascii=False)
        
        # Create Excel file with multiple sheets
        excel_file = os.path.join(self.output_dir, f'swedish_municipal_fees_{timestamp}.xlsx')
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # Main data sheet
            df.to_excel(writer, sheet_name='Municipal_Fees', index=False)
            
            # Summary by municipality
            municipality_summary = df.groupby('municipality').agg({
                'fee_name': 'count',
                'amount_numeric': ['mean', 'min', 'max']
            }).round(2)
            municipality_summary.columns = ['Fee_Count', 'Avg_Amount', 'Min_Amount', 'Max_Amount']
            municipality_summary.to_excel(writer, sheet_name='Municipality_Summary')
            
            # Category breakdown
            if 'category' in df.columns:
                category_summary = df['category'].value_counts()
                category_summary.to_excel(writer, sheet_name='Category_Breakdown')
        
        # Log final statistics
        self.logger.info(f"Data export complete:")
        self.logger.info(f"  Total items saved: {self.stats['total_items']}")
        self.logger.info(f"  Municipalities processed: {len(self.stats['municipalities_processed'])}")
        self.logger.info(f"  Files created:")
        self.logger.info(f"    JSON: {json_file}")
        self.logger.info(f"    CSV: {csv_file}")
        self.logger.info(f"    Excel: {excel_file}")
        self.logger.info(f"    Statistics: {stats_file}")
        
        # Log category breakdown
        if self.stats['categories']:
            self.logger.info("Category breakdown:")
            for category, count in sorted(self.stats['categories'].items(), key=lambda x: x[1], reverse=True):
                self.logger.info(f"  {category}: {count} items")
        
        # Log CMS type breakdown
        if self.stats['cms_types']:
            self.logger.info("CMS type breakdown:")
            for cms_type, count in sorted(self.stats['cms_types'].items(), key=lambda x: x[1], reverse=True):
                self.logger.info(f"  {cms_type}: {count} items") 