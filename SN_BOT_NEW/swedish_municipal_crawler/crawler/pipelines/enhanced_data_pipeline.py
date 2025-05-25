import csv
import json
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
import pandas as pd
from collections import defaultdict, Counter

class EnhancedSwedishFeeDataPipeline:
    """Enhanced data pipeline with SQLite storage, Excel export, and comprehensive analytics"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.fees_by_municipality = defaultdict(list)
        self.total_fees = 0
        self.output_dir = Path('data/output')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize outputs with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.csv_file_path = self.output_dir / f'swedish_municipal_fees_{timestamp}.csv'
        self.excel_file_path = self.output_dir / f'swedish_municipal_fees_{timestamp}.xlsx'
        self.db_path = self.output_dir / f'swedish_municipal_fees_{timestamp}.db'
        self.stats_file_path = self.output_dir / f'extraction_statistics_{timestamp}.json'
        
        # File handles
        self.csv_file = None
        self.csv_writer = None
        self.db_conn = None
        
        # Statistics tracking
        self.stats = {
            'extraction_started': datetime.now().isoformat(),
            'total_fees': 0,
            'municipalities': set(),
            'categories': Counter(),
            'extraction_methods': Counter(),
            'cms_types': Counter(),
            'confidence_scores': [],
            'validation_scores': [],
            'source_types': Counter(),
            'bygglov_fees': 0,
            'pdf_fees': 0,
            'html_fees': 0,
            'errors': []
        }
        
        # Enhanced field mapping
        self.fieldnames = [
            # Core identification
            'municipality', 'municipality_org_number', 'fee_name', 'amount', 'currency',
            'unit', 'category', 'description',
            
            # Bygglov specific
            'bygglov_type', 'area_based', 'pbb_based', 'area_range', 'pbb_multiplier',
            
            # Source information
            'source_url', 'source_type', 'extraction_method', 'extraction_date',
            'cms_type', 'municipality_type',
            
            # Quality indicators
            'confidence', 'validation_confidence', 'overall_quality',
            'data_completeness', 'content_quality', 'source_reliability',
            
            # Validation metadata
            'validation_warnings', 'validation_version',
            
            # Context
            'context', 'element_info'
        ]
    
    def open_spider(self, spider):
        """Initialize all output formats"""
        try:
            # CSV initialization
            self.csv_file = open(self.csv_file_path, 'w', newline='', encoding='utf-8')
            self.csv_writer = csv.DictWriter(self.csv_file, fieldnames=self.fieldnames)
            self.csv_writer.writeheader()
            
            # SQLite initialization
            self.db_conn = sqlite3.connect(self.db_path)
            self._create_database_schema()
            
            spider.logger.info(f"Enhanced data pipeline initialized:")
            spider.logger.info(f"  CSV: {self.csv_file_path}")
            spider.logger.info(f"  Excel: {self.excel_file_path}")
            spider.logger.info(f"  Database: {self.db_path}")
            
        except Exception as e:
            spider.logger.error(f"Failed to initialize data pipeline: {e}")
            raise
    
    def _create_database_schema(self):
        """Create comprehensive SQLite database schema"""
        cursor = self.db_conn.cursor()
        
        # Main fees table with all enhanced fields
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                municipality TEXT NOT NULL,
                municipality_org_number TEXT,
                fee_name TEXT NOT NULL,
                amount REAL NOT NULL,
                currency TEXT DEFAULT 'SEK',
                unit TEXT DEFAULT 'kr',
                category TEXT,
                description TEXT,
                
                -- Bygglov specific
                bygglov_type TEXT,
                area_based BOOLEAN,
                pbb_based BOOLEAN,
                area_range TEXT,
                pbb_multiplier REAL,
                
                -- Source information
                source_url TEXT,
                source_type TEXT,
                extraction_method TEXT,
                extraction_date TEXT,
                cms_type TEXT,
                municipality_type TEXT,
                
                -- Quality indicators
                confidence REAL,
                validation_confidence REAL,
                overall_quality REAL,
                data_completeness REAL,
                content_quality REAL,
                source_reliability REAL,
                
                -- Validation metadata
                validation_warnings TEXT,
                validation_version TEXT,
                
                -- Context
                context TEXT,
                element_info TEXT,
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Municipality summary table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS municipality_summary (
                municipality TEXT PRIMARY KEY,
                total_fees INTEGER,
                avg_confidence REAL,
                avg_amount REAL,
                cms_type TEXT,
                municipality_type TEXT,
                categories TEXT,
                extraction_methods TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Category analysis table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS category_analysis (
                category TEXT PRIMARY KEY,
                total_fees INTEGER,
                avg_amount REAL,
                min_amount REAL,
                max_amount REAL,
                municipalities INTEGER,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Extraction statistics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS extraction_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                extraction_date TEXT,
                total_fees INTEGER,
                municipalities INTEGER,
                avg_confidence REAL,
                extraction_methods TEXT,
                cms_distribution TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_municipality ON fees(municipality)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON fees(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_amount ON fees(amount)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_confidence ON fees(confidence)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_extraction_method ON fees(extraction_method)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_cms_type ON fees(cms_type)')
        
        self.db_conn.commit()
        self.logger.info("Database schema created successfully")
    
    def process_item(self, item, spider):
        """Process and store each fee item with enhanced data handling"""
        try:
            # Convert item to enhanced dict format
            enhanced_item = self._enhance_item_data(item)
            
            # Write to CSV
            self.csv_writer.writerow(enhanced_item)
            self.csv_file.flush()
            
            # Write to SQLite
            self._insert_to_database(enhanced_item)
            
            # Update statistics
            self._update_statistics(enhanced_item)
            
            # Store for municipality grouping
            municipality = enhanced_item['municipality']
            self.fees_by_municipality[municipality].append(enhanced_item)
            
            self.total_fees += 1
            
            # Log progress
            if self.total_fees % 100 == 0:
                spider.logger.info(f"Processed {self.total_fees} total fees from {len(self.fees_by_municipality)} municipalities")
            
            return item
            
        except Exception as e:
            self.logger.error(f"Error processing item: {e}")
            self.stats['errors'].append(str(e))
            return item
    
    def _enhance_item_data(self, item):
        """Convert item to enhanced format with all fields"""
        enhanced = {}
        
        # Map all possible fields, handling nested structures
        for field in self.fieldnames:
            if field in item:
                enhanced[field] = item[field]
            elif field == 'validation_confidence':
                enhanced[field] = item.get('validation', {}).get('confidence_score', '')
            elif field == 'overall_quality':
                enhanced[field] = item.get('quality', {}).get('overall_score', '')
            elif field == 'data_completeness':
                enhanced[field] = item.get('quality', {}).get('data_completeness', '')
            elif field == 'content_quality':
                enhanced[field] = item.get('quality', {}).get('content_quality', '')
            elif field == 'source_reliability':
                enhanced[field] = item.get('quality', {}).get('source_reliability', '')
            elif field == 'validation_warnings':
                warnings = item.get('validation', {}).get('warnings', [])
                enhanced[field] = '; '.join(warnings) if warnings else ''
            elif field == 'validation_version':
                enhanced[field] = item.get('validation', {}).get('validation_version', '')
            elif field == 'element_info':
                element_info = item.get('element_info', {})
                enhanced[field] = json.dumps(element_info) if element_info else ''
            elif field == 'area_range':
                area_range = item.get('area_range', {})
                enhanced[field] = json.dumps(area_range) if area_range else ''
            else:
                enhanced[field] = ''
        
        # Ensure numeric fields are properly formatted
        for numeric_field in ['amount', 'confidence', 'validation_confidence', 'overall_quality',
                             'data_completeness', 'content_quality', 'source_reliability', 'pbb_multiplier']:
            if enhanced.get(numeric_field):
                try:
                    enhanced[numeric_field] = float(enhanced[numeric_field])
                except (ValueError, TypeError):
                    enhanced[numeric_field] = 0.0
        
        # Ensure boolean fields are properly formatted
        for bool_field in ['area_based', 'pbb_based']:
            if enhanced.get(bool_field):
                enhanced[bool_field] = bool(enhanced[bool_field])
        
        return enhanced
    
    def _insert_to_database(self, item):
        """Insert enhanced item into SQLite database"""
        cursor = self.db_conn.cursor()
        
        # Prepare values for insertion
        values = []
        placeholders = []
        
        for field in self.fieldnames:
            value = item.get(field, None)
            
            # Handle special cases
            if field in ['area_based', 'pbb_based'] and value is not None:
                value = 1 if value else 0
            elif field in ['element_info', 'area_range'] and isinstance(value, str) and value:
                # Keep as JSON string
                pass
            elif value == '':
                value = None
            
            values.append(value)
            placeholders.append('?')
        
        # Insert into fees table
        query = f'''
            INSERT INTO fees ({', '.join(self.fieldnames)})
            VALUES ({', '.join(placeholders)})
        '''
        
        cursor.execute(query, values)
        self.db_conn.commit()
    
    def _update_statistics(self, item):
        """Update running statistics"""
        municipality = item.get('municipality', 'Unknown')
        self.stats['municipalities'].add(municipality)
        
        category = item.get('category', 'övrigt')
        self.stats['categories'][category] += 1
        
        extraction_method = item.get('extraction_method', 'unknown')
        self.stats['extraction_methods'][extraction_method] += 1
        
        cms_type = item.get('cms_type', 'unknown')
        self.stats['cms_types'][cms_type] += 1
        
        source_type = item.get('source_type', 'unknown')
        self.stats['source_types'][source_type] += 1
        
        # Track confidence scores
        confidence = item.get('confidence')
        if confidence is not None:
            self.stats['confidence_scores'].append(float(confidence))
        
        validation_confidence = item.get('validation_confidence')
        if validation_confidence is not None:
            self.stats['validation_scores'].append(float(validation_confidence))
        
        # Count special types
        if item.get('bygglov_type'):
            self.stats['bygglov_fees'] += 1
        
        if item.get('source_type') == 'PDF':
            self.stats['pdf_fees'] += 1
        else:
            self.stats['html_fees'] += 1
    
    def close_spider(self, spider):
        """Generate comprehensive outputs and close resources"""
        try:
            # Close CSV file
            if self.csv_file:
                self.csv_file.close()
            
            # Update database summaries
            self._update_database_summaries()
            
            # Generate Excel file with multiple sheets
            self._generate_excel_output()
            
            # Generate comprehensive statistics
            self._generate_final_statistics()
            
            # Close database
            if self.db_conn:
                self.db_conn.close()
            
            # Log final summary
            self._log_final_summary(spider)
            
        except Exception as e:
            spider.logger.error(f"Error in pipeline cleanup: {e}")
    
    def _update_database_summaries(self):
        """Update summary tables in database"""
        cursor = self.db_conn.cursor()
        
        # Update municipality summary
        for municipality, fees in self.fees_by_municipality.items():
            total_fees = len(fees)
            avg_confidence = sum(f.get('confidence', 0) for f in fees) / total_fees
            avg_amount = sum(f.get('amount', 0) for f in fees) / total_fees
            
            cms_types = [f.get('cms_type', 'unknown') for f in fees]
            cms_type = max(set(cms_types), key=cms_types.count)
            
            municipality_types = [f.get('municipality_type', 'unknown') for f in fees]
            municipality_type = max(set(municipality_types), key=municipality_types.count)
            
            categories = list(set(f.get('category', 'övrigt') for f in fees))
            extraction_methods = list(set(f.get('extraction_method', 'unknown') for f in fees))
            
            cursor.execute('''
                INSERT OR REPLACE INTO municipality_summary 
                (municipality, total_fees, avg_confidence, avg_amount, cms_type, 
                 municipality_type, categories, extraction_methods)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (municipality, total_fees, avg_confidence, avg_amount, cms_type,
                  municipality_type, ', '.join(categories), ', '.join(extraction_methods)))
        
        # Update category analysis
        for category, count in self.stats['categories'].items():
            cursor.execute('''
                SELECT AVG(amount), MIN(amount), MAX(amount), COUNT(DISTINCT municipality)
                FROM fees WHERE category = ?
            ''', (category,))
            
            avg_amount, min_amount, max_amount, municipalities = cursor.fetchone()
            
            cursor.execute('''
                INSERT OR REPLACE INTO category_analysis 
                (category, total_fees, avg_amount, min_amount, max_amount, municipalities)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (category, count, avg_amount, min_amount, max_amount, municipalities))
        
        self.db_conn.commit()
    
    def _generate_excel_output(self):
        """Generate comprehensive Excel file with multiple sheets"""
        try:
            with pd.ExcelWriter(self.excel_file_path, engine='openpyxl') as writer:
                # Sheet 1: All fees data
                df_fees = pd.read_csv(self.csv_file_path)
                df_fees.to_excel(writer, sheet_name='Municipal_Fees', index=False)
                
                # Sheet 2: Municipality summary
                municipality_data = []
                for municipality, fees in self.fees_by_municipality.items():
                    summary = {
                        'Municipality': municipality,
                        'Total_Fees': len(fees),
                        'Avg_Amount': sum(f.get('amount', 0) for f in fees) / len(fees),
                        'Avg_Confidence': sum(f.get('confidence', 0) for f in fees) / len(fees),
                        'Categories': len(set(f.get('category', 'övrigt') for f in fees)),
                        'CMS_Type': max([f.get('cms_type', 'unknown') for f in fees], 
                                      key=[f.get('cms_type', 'unknown') for f in fees].count),
                        'Extraction_Methods': len(set(f.get('extraction_method', 'unknown') for f in fees))
                    }
                    municipality_data.append(summary)
                
                df_municipalities = pd.DataFrame(municipality_data)
                df_municipalities.to_excel(writer, sheet_name='Municipality_Summary', index=False)
                
                # Sheet 3: Category breakdown
                category_data = []
                for category, count in self.stats['categories'].items():
                    category_fees = [f for fees in self.fees_by_municipality.values() 
                                   for f in fees if f.get('category') == category]
                    
                    if category_fees:
                        amounts = [f.get('amount', 0) for f in category_fees]
                        category_summary = {
                            'Category': category,
                            'Total_Fees': count,
                            'Avg_Amount': sum(amounts) / len(amounts),
                            'Min_Amount': min(amounts),
                            'Max_Amount': max(amounts),
                            'Municipalities': len(set(f.get('municipality') for f in category_fees))
                        }
                        category_data.append(category_summary)
                
                df_categories = pd.DataFrame(category_data)
                df_categories.to_excel(writer, sheet_name='Category_Breakdown', index=False)
                
                # Sheet 4: Bygglov analysis (if applicable)
                bygglov_fees = [f for fees in self.fees_by_municipality.values() 
                               for f in fees if f.get('bygglov_type')]
                
                if bygglov_fees:
                    df_bygglov = pd.DataFrame(bygglov_fees)
                    df_bygglov.to_excel(writer, sheet_name='Bygglov_Analysis', index=False)
                
                # Sheet 5: Quality metrics
                quality_data = []
                for municipality, fees in self.fees_by_municipality.items():
                    confidences = [f.get('confidence', 0) for f in fees if f.get('confidence')]
                    validations = [f.get('validation_confidence', 0) for f in fees if f.get('validation_confidence')]
                    
                    quality_summary = {
                        'Municipality': municipality,
                        'Total_Fees': len(fees),
                        'Avg_Confidence': sum(confidences) / len(confidences) if confidences else 0,
                        'Avg_Validation': sum(validations) / len(validations) if validations else 0,
                        'High_Quality_Fees': len([f for f in fees if f.get('confidence', 0) > 0.8]),
                        'PDF_Fees': len([f for f in fees if f.get('source_type') == 'PDF']),
                        'HTML_Fees': len([f for f in fees if f.get('source_type') != 'PDF'])
                    }
                    quality_data.append(quality_summary)
                
                df_quality = pd.DataFrame(quality_data)
                df_quality.to_excel(writer, sheet_name='Quality_Metrics', index=False)
            
            self.logger.info(f"Excel file generated: {self.excel_file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to generate Excel file: {e}")
    
    def _generate_final_statistics(self):
        """Generate comprehensive final statistics"""
        self.stats['extraction_completed'] = datetime.now().isoformat()
        self.stats['total_fees'] = self.total_fees
        self.stats['municipalities_count'] = len(self.stats['municipalities'])
        self.stats['municipalities_list'] = sorted(list(self.stats['municipalities']))
        
        # Convert counters to dicts for JSON serialization
        self.stats['categories'] = dict(self.stats['categories'])
        self.stats['extraction_methods'] = dict(self.stats['extraction_methods'])
        self.stats['cms_types'] = dict(self.stats['cms_types'])
        self.stats['source_types'] = dict(self.stats['source_types'])
        
        # Calculate confidence statistics
        if self.stats['confidence_scores']:
            self.stats['confidence_stats'] = {
                'average': sum(self.stats['confidence_scores']) / len(self.stats['confidence_scores']),
                'min': min(self.stats['confidence_scores']),
                'max': max(self.stats['confidence_scores']),
                'count': len(self.stats['confidence_scores'])
            }
        
        if self.stats['validation_scores']:
            self.stats['validation_stats'] = {
                'average': sum(self.stats['validation_scores']) / len(self.stats['validation_scores']),
                'min': min(self.stats['validation_scores']),
                'max': max(self.stats['validation_scores']),
                'count': len(self.stats['validation_scores'])
            }
        
        # Calculate averages
        if self.total_fees > 0:
            self.stats['avg_fees_per_municipality'] = self.total_fees / len(self.stats['municipalities'])
        
        # Remove raw score lists (too large for JSON)
        del self.stats['confidence_scores']
        del self.stats['validation_scores']
        
        # Save statistics
        with open(self.stats_file_path, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False, default=str)
        
        self.logger.info(f"Final statistics saved: {self.stats_file_path}")
    
    def _log_final_summary(self, spider):
        """Log comprehensive final summary"""
        spider.logger.info("=== Enhanced Data Pipeline Summary ===")
        spider.logger.info(f"Total fees extracted: {self.total_fees}")
        spider.logger.info(f"Municipalities processed: {len(self.stats['municipalities'])}")
        spider.logger.info(f"Categories found: {len(self.stats['categories'])}")
        spider.logger.info(f"Extraction methods used: {len(self.stats['extraction_methods'])}")
        spider.logger.info(f"Bygglov fees: {self.stats['bygglov_fees']}")
        spider.logger.info(f"PDF fees: {self.stats['pdf_fees']}")
        spider.logger.info(f"HTML fees: {self.stats['html_fees']}")
        
        if self.stats.get('confidence_stats'):
            spider.logger.info(f"Average confidence: {self.stats['confidence_stats']['average']:.3f}")
        
        spider.logger.info("Output files generated:")
        spider.logger.info(f"  CSV: {self.csv_file_path}")
        spider.logger.info(f"  Excel: {self.excel_file_path}")
        spider.logger.info(f"  Database: {self.db_path}")
        spider.logger.info(f"  Statistics: {self.stats_file_path}")
        
        # Top categories
        top_categories = sorted(self.stats['categories'].items(), key=lambda x: x[1], reverse=True)[:5]
        spider.logger.info("Top categories:")
        for category, count in top_categories:
            spider.logger.info(f"  {category}: {count} fees")
        
        # Top extraction methods
        top_methods = sorted(self.stats['extraction_methods'].items(), key=lambda x: x[1], reverse=True)[:5]
        spider.logger.info("Top extraction methods:")
        for method, count in top_methods:
            spider.logger.info(f"  {method}: {count} fees") 