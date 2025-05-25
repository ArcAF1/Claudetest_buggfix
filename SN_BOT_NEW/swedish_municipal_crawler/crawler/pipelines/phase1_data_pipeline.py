#!/usr/bin/env python3
"""
Phase 1 Data Pipeline
Handles data export, storage, and reporting for Phase 1 specific data points:
1. Timtaxan för livsmedelskontroll (Hourly rate for food control)
2. Debiteringsmodell för livsmedelskontroll (Billing model: prepaid vs post-paid)
3. Timtaxan för bygglov (Hourly rate for building permits)
"""

import csv
import json
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import statistics
import os

try:
    import pandas as pd
    import openpyxl
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

# Try to import SocketIO for real-time notifications
try:
    from flask_socketio import SocketIO
    SOCKETIO_AVAILABLE = True
except ImportError:
    SOCKETIO_AVAILABLE = False

class Phase1DataPipeline:
    """Comprehensive data pipeline for Phase 1 municipal fee data"""
    
    def __init__(self, output_dir: str = 'data/output'):
        self.logger = logging.getLogger(__name__)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Data storage
        self.municipalities_data = {}
        self.processing_stats = {
            'start_time': datetime.now(),
            'items_processed': 0,
            'items_exported': 0,
            'errors': []
        }
        
        # File paths with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        self.csv_file_path = self.output_dir / f'phase1_municipal_data_{timestamp}.csv'
        self.excel_file_path = self.output_dir / f'phase1_municipal_data_{timestamp}.xlsx'
        self.db_path = self.output_dir / f'phase1_municipal_data_{timestamp}.db'
        self.stats_file_path = self.output_dir / f'phase1_statistics_{timestamp}.json'
        self.comparison_file_path = self.output_dir / f'phase1_comparison_{timestamp}.csv'
        
        # File handles
        self.csv_file = None
        self.csv_writer = None
        self.db_conn = None
        
        # Real-time notification setup
        self.socketio = None
        self._setup_realtime_notifications()
        
        # Phase 1 specific field definitions
        self.phase1_fields = {
            'municipality': 'Municipality name',
            'timtaxa_livsmedel': 'Hourly rate for food control (kr)',
            'debitering_livsmedel': 'Billing model for food control',
            'timtaxa_bygglov': 'Hourly rate for building permits (kr)',
            'completeness_score': 'Data completeness (0-1)',
            'data_quality': 'Data quality score (0-100)',
            'source_url': 'Source URL',
            'source_type': 'Source type (PDF/HTML)',
            'extraction_date': 'Extraction date',
            'confidence': 'Extraction confidence (0-1)',
            'status': 'Data status (complete/partial)',
            'validation_warnings': 'Validation warnings'
        }
    
    def _setup_realtime_notifications(self):
        """Setup real-time notifications if SocketIO is available"""
        try:
            # Try to connect to the web interface's SocketIO instance
            # This is a bit tricky since we're in a separate process
            # We'll use a file-based notification system instead
            self.notification_file = self.output_dir / 'realtime_notifications.json'
            self.logger.debug("Real-time notifications setup completed")
        except Exception as e:
            self.logger.debug(f"Real-time notifications not available: {e}")
    
    def _emit_realtime_update(self, event_type: str, data: Dict):
        """Emit real-time update via file-based notification system"""
        try:
            notification = {
                'timestamp': datetime.now().isoformat(),
                'event_type': event_type,
                'data': data
            }
            
            # Write notification to file for web interface to pick up
            with open(self.notification_file, 'w', encoding='utf-8') as f:
                json.dump(notification, f, ensure_ascii=False)
            
            self.logger.debug(f"Real-time notification sent: {event_type}")
            
        except Exception as e:
            self.logger.debug(f"Error sending real-time notification: {e}")
    
    def open_spider(self, spider):
        """Initialize outputs for Phase 1 data"""
        try:
            spider.logger.info(f"Initializing Phase 1 data pipeline: {self.output_dir}")
            
            # Initialize CSV output
            self._initialize_csv_output()
            
            # Initialize SQLite database
            self._initialize_database()
            
            spider.logger.info(f"Phase 1 outputs initialized:")
            spider.logger.info(f"  CSV: {self.csv_file_path}")
            spider.logger.info(f"  Database: {self.db_path}")
            if PANDAS_AVAILABLE:
                spider.logger.info(f"  Excel: {self.excel_file_path}")
            
        except Exception as e:
            spider.logger.error(f"Error initializing Phase 1 data pipeline: {e}")
            self.processing_stats['errors'].append(f"Initialization error: {str(e)}")
    
    def _initialize_csv_output(self):
        """Initialize CSV output with Phase 1 specific columns"""
        self.csv_file = open(self.csv_file_path, 'w', newline='', encoding='utf-8')
        
        fieldnames = list(self.phase1_fields.keys())
        self.csv_writer = csv.DictWriter(self.csv_file, fieldnames=fieldnames)
        self.csv_writer.writeheader()
        
        self.logger.info(f"CSV output initialized: {self.csv_file_path}")
    
    def _initialize_database(self):
        """Initialize SQLite database with Phase 1 schema"""
        self.db_conn = sqlite3.connect(self.db_path)
        self._create_phase1_schema()
        self.logger.info(f"Database initialized: {self.db_path}")
    
    def _create_phase1_schema(self):
        """Create Phase 1 specific database schema"""
        cursor = self.db_conn.cursor()
        
        # Main Phase 1 data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS phase1_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                municipality TEXT UNIQUE NOT NULL,
                timtaxa_livsmedel INTEGER,
                debitering_livsmedel TEXT,
                timtaxa_bygglov INTEGER,
                completeness_score REAL,
                data_quality INTEGER,
                source_url TEXT,
                source_type TEXT,
                extraction_date TEXT,
                confidence REAL,
                status TEXT,
                validation_warnings TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Extraction statistics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS extraction_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric TEXT NOT NULL,
                value REAL,
                description TEXT,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Field coverage table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS field_coverage (
                field_name TEXT PRIMARY KEY,
                municipalities_with_field INTEGER,
                total_municipalities INTEGER,
                coverage_percentage REAL,
                average_value REAL,
                min_value REAL,
                max_value REAL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Quality distribution table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quality_distribution (
                quality_tier TEXT PRIMARY KEY,
                municipality_count INTEGER,
                percentage REAL,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.db_conn.commit()
        self.logger.debug("Phase 1 database schema created")
    
    def process_item(self, item, spider):
        """Process and store Phase 1 item"""
        try:
            self.processing_stats['items_processed'] += 1
            municipality = item.get('municipality', '')
            
            if not municipality:
                spider.logger.warning("Item without municipality name - skipping")
                return item
            
            # Store in memory for analysis
            self.municipalities_data[municipality] = dict(item)
            
            # Prepare item for export (clean up complex fields)
            export_item = self._prepare_item_for_export(item)
            
            # Write to CSV
            self.csv_writer.writerow(export_item)
            self.csv_file.flush()
            
            # Write to database
            self._insert_to_database(export_item)
            
            self.processing_stats['items_exported'] += 1
            
            # Emit real-time update for new data found
            self._emit_realtime_update('new_data', {
                'municipality': municipality,
                'timtaxa_livsmedel': export_item.get('timtaxa_livsmedel'),
                'debitering_livsmedel': export_item.get('debitering_livsmedel'),
                'timtaxa_bygglov': export_item.get('timtaxa_bygglov'),
                'status': export_item.get('status'),
                'confidence': export_item.get('confidence'),
                'source_url': export_item.get('source_url'),
                'total_processed': self.processing_stats['items_processed'],
                'total_exported': self.processing_stats['items_exported']
            })
            
            # Log progress periodically
            if self.processing_stats['items_processed'] % 10 == 0:
                self._log_progress(spider)
            
            return item
            
        except Exception as e:
            error_msg = f"Error processing item for {item.get('municipality', 'unknown')}: {e}"
            self.logger.error(error_msg)
            self.processing_stats['errors'].append(error_msg)
            return item
    
    def _prepare_item_for_export(self, item: Dict) -> Dict:
        """Prepare item for export by cleaning and formatting fields"""
        export_item = {}
        
        for field in self.phase1_fields.keys():
            value = item.get(field)
            
            # Handle special field formatting
            if field == 'validation_warnings' and isinstance(value, list):
                export_item[field] = '; '.join(value) if value else ''
            elif field == 'extraction_date' and value:
                # Ensure consistent date format
                try:
                    if isinstance(value, str):
                        export_item[field] = value
                    else:
                        export_item[field] = str(value)
                except:
                    export_item[field] = datetime.now().isoformat()
            elif field in ['completeness_score', 'confidence'] and value is not None:
                # Round to 3 decimal places
                export_item[field] = round(float(value), 3)
            elif field == 'data_quality' and value is not None:
                # Round to 1 decimal place
                export_item[field] = round(float(value), 1)
            else:
                export_item[field] = value if value is not None else ''
        
        return export_item
    
    def _insert_to_database(self, item: Dict):
        """Insert Phase 1 data into database"""
        cursor = self.db_conn.cursor()
        
        # Convert validation_warnings to string if it's a list
        validation_warnings = item.get('validation_warnings', '')
        if isinstance(validation_warnings, list):
            validation_warnings = '; '.join(validation_warnings)
        
        cursor.execute('''
            INSERT OR REPLACE INTO phase1_data (
                municipality, timtaxa_livsmedel, debitering_livsmedel,
                timtaxa_bygglov, completeness_score, data_quality,
                source_url, source_type, extraction_date, confidence,
                status, validation_warnings, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            item.get('municipality'),
            item.get('timtaxa_livsmedel'),
            item.get('debitering_livsmedel'),
            item.get('timtaxa_bygglov'),
            item.get('completeness_score'),
            item.get('data_quality'),
            item.get('source_url'),
            item.get('source_type'),
            item.get('extraction_date'),
            item.get('confidence'),
            item.get('status'),
            validation_warnings,
            datetime.now().isoformat()
        ))
        
        self.db_conn.commit()
    
    def _log_progress(self, spider):
        """Log processing progress with real-time updates"""
        total = self.processing_stats['items_processed']
        complete = sum(1 for m in self.municipalities_data.values() 
                      if m.get('status') == 'complete')
        partial = sum(1 for m in self.municipalities_data.values() 
                     if m.get('status') == 'partial')
        
        spider.logger.info(f"Phase 1 Progress: {total} municipalities processed, "
                          f"{complete} complete, {partial} partial")
        
        # Emit real-time progress update
        self._emit_realtime_update('progress_update', {
            'total_municipalities': total,
            'complete_municipalities': complete,
            'partial_municipalities': partial,
            'completion_rate': (complete / total * 100) if total > 0 else 0,
            'municipalities_with_data': complete + partial
        })
    
    def close_spider(self, spider):
        """Finalize Phase 1 data processing and generate reports"""
        try:
            spider.logger.info("Finalizing Phase 1 data pipeline...")
            
            # Close file handles
            if self.csv_file:
                self.csv_file.close()
            
            # Generate comprehensive statistics
            self._generate_phase1_statistics(spider)
            
            # Generate comparison report
            self._generate_comparison_report(spider)
            
            # Generate Excel report if pandas is available
            if PANDAS_AVAILABLE:
                self._generate_excel_report(spider)
            
            # Update database with final statistics
            self._update_database_statistics()
            
            # Close database connection
            if self.db_conn:
                self.db_conn.close()
            
            # Log final summary
            self._log_final_summary(spider)
            
        except Exception as e:
            spider.logger.error(f"Error finalizing Phase 1 data pipeline: {e}")
            self.processing_stats['errors'].append(f"Finalization error: {str(e)}")
    
    def _generate_phase1_statistics(self, spider):
        """Generate comprehensive Phase 1 statistics"""
        total = len(self.municipalities_data)
        if total == 0:
            spider.logger.warning("No municipalities data to analyze")
            return
        
        # Calculate field coverage
        field_coverage = {}
        for field in ['timtaxa_livsmedel', 'debitering_livsmedel', 'timtaxa_bygglov']:
            values = [m.get(field) for m in self.municipalities_data.values() if m.get(field)]
            field_coverage[field] = {
                'count': len(values),
                'percentage': (len(values) / total) * 100,
                'values': values
            }
        
        # Calculate quality distribution
        quality_distribution = {'excellent': 0, 'good': 0, 'fair': 0, 'poor': 0}
        for municipality_data in self.municipalities_data.values():
            quality = municipality_data.get('data_quality', 0)
            if quality >= 90:
                quality_distribution['excellent'] += 1
            elif quality >= 70:
                quality_distribution['good'] += 1
            elif quality >= 50:
                quality_distribution['fair'] += 1
            else:
                quality_distribution['poor'] += 1
        
        # Calculate timtaxa statistics
        timtaxa_stats = {}
        for field in ['timtaxa_livsmedel', 'timtaxa_bygglov']:
            values = field_coverage[field]['values']
            if values:
                timtaxa_stats[field] = {
                    'count': len(values),
                    'min': min(values),
                    'max': max(values),
                    'average': statistics.mean(values),
                    'median': statistics.median(values),
                    'std_dev': statistics.stdev(values) if len(values) > 1 else 0
                }
        
        # Calculate debitering distribution
        debitering_values = field_coverage['debitering_livsmedel']['values']
        debitering_distribution = {
            'förskott': debitering_values.count('förskott'),
            'efterhand': debitering_values.count('efterhand')
        }
        
        # Calculate completeness analysis values
        complete_data = sum(1 for m in self.municipalities_data.values() if m.get('status') == 'complete')
        partial_data = sum(1 for m in self.municipalities_data.values() if m.get('status') == 'partial')
        
        # Compile comprehensive statistics
        stats = {
            'extraction_metadata': {
                'extraction_date': datetime.now().isoformat(),
                'total_municipalities': total,
                'processing_time_minutes': (datetime.now() - self.processing_stats['start_time']).total_seconds() / 60,
                'items_processed': self.processing_stats['items_processed'],
                'items_exported': self.processing_stats['items_exported'],
                'errors_count': len(self.processing_stats['errors'])
            },
            'completeness_analysis': {
                'complete_data': complete_data,
                'partial_data': partial_data,
                'no_data': total - (complete_data + partial_data)
            },
            'field_coverage': {
                field: {
                    'municipalities_with_data': data['count'],
                    'coverage_percentage': data['percentage'],
                    'total_municipalities': total
                }
                for field, data in field_coverage.items()
            },
            'quality_distribution': {
                tier: {
                    'count': count,
                    'percentage': (count / total) * 100
                }
                for tier, count in quality_distribution.items()
            },
            'timtaxa_analysis': timtaxa_stats,
            'debitering_analysis': {
                'distribution': debitering_distribution,
                'total_with_billing_info': sum(debitering_distribution.values())
            },
            'success_metrics': {
                'overall_success_rate': ((complete_data + partial_data) / total) * 100 if total > 0 else 0,
                'complete_data_rate': (complete_data / total) * 100 if total > 0 else 0,
                'average_fields_per_municipality': sum(field_coverage[field]['count'] for field in field_coverage) / total if total > 0 else 0
            }
        }
        
        # Save statistics to JSON
        with open(self.stats_file_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        spider.logger.info(f"Phase 1 statistics saved: {self.stats_file_path}")
        return stats
    
    def _generate_comparison_report(self, spider):
        """Generate municipality comparison report for Phase 1 data"""
        try:
            with open(self.comparison_file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Header
                writer.writerow([
                    'Municipality',
                    'Timtaxa Livsmedel (kr)',
                    'Debitering Model',
                    'Timtaxa Bygglov (kr)',
                    'Data Quality (%)',
                    'Completeness (%)',
                    'Status',
                    'Source Type',
                    'Confidence'
                ])
                
                # Sort municipalities by name
                for municipality in sorted(self.municipalities_data.keys()):
                    data = self.municipalities_data[municipality]
                    
                    writer.writerow([
                        municipality,
                        data.get('timtaxa_livsmedel', 'Missing'),
                        data.get('debitering_livsmedel', 'Missing'),
                        data.get('timtaxa_bygglov', 'Missing'),
                        f"{data.get('data_quality', 0):.1f}",
                        f"{data.get('completeness_score', 0)*100:.1f}",
                        data.get('status', 'Unknown'),
                        data.get('source_type', 'Unknown'),
                        f"{data.get('confidence', 0):.2f}"
                    ])
            
            spider.logger.info(f"Comparison report saved: {self.comparison_file_path}")
            
        except Exception as e:
            spider.logger.error(f"Error generating comparison report: {e}")
    
    def _generate_excel_report(self, spider):
        """Generate Excel report with multiple sheets"""
        if not PANDAS_AVAILABLE:
            spider.logger.warning("Pandas not available - skipping Excel report")
            return
        
        try:
            # Create Excel writer
            with pd.ExcelWriter(self.excel_file_path, engine='openpyxl') as writer:
                
                # Main data sheet
                df_main = pd.DataFrame.from_dict(self.municipalities_data, orient='index')
                df_main.index.name = 'Municipality'
                df_main.to_excel(writer, sheet_name='Phase1_Data')
                
                # Summary statistics sheet
                summary_data = []
                total = len(self.municipalities_data)
                
                # Field coverage summary
                for field in ['timtaxa_livsmedel', 'debitering_livsmedel', 'timtaxa_bygglov']:
                    count = sum(1 for m in self.municipalities_data.values() if m.get(field))
                    summary_data.append({
                        'Metric': f'{field} Coverage',
                        'Value': count,
                        'Percentage': f"{(count/total)*100:.1f}%" if total > 0 else "0%"
                    })
                
                # Quality distribution
                quality_dist = {'excellent': 0, 'good': 0, 'fair': 0, 'poor': 0}
                for m in self.municipalities_data.values():
                    quality = m.get('data_quality', 0)
                    if quality >= 90:
                        quality_dist['excellent'] += 1
                    elif quality >= 70:
                        quality_dist['good'] += 1
                    elif quality >= 50:
                        quality_dist['fair'] += 1
                    else:
                        quality_dist['poor'] += 1
                
                for tier, count in quality_dist.items():
                    summary_data.append({
                        'Metric': f'Quality - {tier.capitalize()}',
                        'Value': count,
                        'Percentage': f"{(count/total)*100:.1f}%" if total > 0 else "0%"
                    })
                
                df_summary = pd.DataFrame(summary_data)
                df_summary.to_excel(writer, sheet_name='Summary', index=False)
                
                # Timtaxa analysis sheet
                timtaxa_data = []
                for municipality, data in self.municipalities_data.items():
                    timtaxa_data.append({
                        'Municipality': municipality,
                        'Timtaxa_Livsmedel': data.get('timtaxa_livsmedel'),
                        'Timtaxa_Bygglov': data.get('timtaxa_bygglov'),
                        'Difference': (data.get('timtaxa_livsmedel', 0) or 0) - (data.get('timtaxa_bygglov', 0) or 0) if data.get('timtaxa_livsmedel') and data.get('timtaxa_bygglov') else None
                    })
                
                df_timtaxa = pd.DataFrame(timtaxa_data)
                df_timtaxa.to_excel(writer, sheet_name='Timtaxa_Analysis', index=False)
            
            spider.logger.info(f"Excel report saved: {self.excel_file_path}")
            
        except Exception as e:
            spider.logger.error(f"Error generating Excel report: {e}")
    
    def _update_database_statistics(self):
        """Update database with final statistics"""
        if not self.db_conn:
            return
        
        try:
            cursor = self.db_conn.cursor()
            total = len(self.municipalities_data)
            
            # Clear existing statistics
            cursor.execute("DELETE FROM extraction_summary")
            cursor.execute("DELETE FROM field_coverage")
            cursor.execute("DELETE FROM quality_distribution")
            
            # Insert extraction summary
            summary_metrics = [
                ('total_municipalities', total, 'Total municipalities processed', 'general'),
                ('complete_items', sum(1 for m in self.municipalities_data.values() if m.get('status') == 'complete'), 'Municipalities with complete data', 'completeness'),
                ('partial_items', sum(1 for m in self.municipalities_data.values() if m.get('status') == 'partial'), 'Municipalities with partial data', 'completeness'),
                ('processing_time', (datetime.now() - self.processing_stats['start_time']).total_seconds() / 60, 'Processing time in minutes', 'performance')
            ]
            
            for metric, value, description, category in summary_metrics:
                cursor.execute(
                    "INSERT INTO extraction_summary (metric, value, description, category) VALUES (?, ?, ?, ?)",
                    (metric, value, description, category)
                )
            
            # Insert field coverage
            for field in ['timtaxa_livsmedel', 'debitering_livsmedel', 'timtaxa_bygglov']:
                values = [m.get(field) for m in self.municipalities_data.values() if m.get(field)]
                count = len(values)
                
                # Calculate statistics for numeric fields
                avg_value = None
                min_value = None
                max_value = None
                
                if field in ['timtaxa_livsmedel', 'timtaxa_bygglov'] and values:
                    avg_value = statistics.mean(values)
                    min_value = min(values)
                    max_value = max(values)
                
                cursor.execute('''
                    INSERT INTO field_coverage 
                    (field_name, municipalities_with_field, total_municipalities, coverage_percentage, average_value, min_value, max_value)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (field, count, total, (count/total)*100 if total > 0 else 0, avg_value, min_value, max_value))
            
            # Insert quality distribution
            quality_dist = {'excellent': 0, 'good': 0, 'fair': 0, 'poor': 0}
            for m in self.municipalities_data.values():
                quality = m.get('data_quality', 0)
                if quality >= 90:
                    quality_dist['excellent'] += 1
                elif quality >= 70:
                    quality_dist['good'] += 1
                elif quality >= 50:
                    quality_dist['fair'] += 1
                else:
                    quality_dist['poor'] += 1
            
            quality_descriptions = {
                'excellent': 'Data quality 90-100%',
                'good': 'Data quality 70-89%',
                'fair': 'Data quality 50-69%',
                'poor': 'Data quality <50%'
            }
            
            for tier, count in quality_dist.items():
                cursor.execute(
                    "INSERT INTO quality_distribution (quality_tier, municipality_count, percentage, description) VALUES (?, ?, ?, ?)",
                    (tier, count, (count/total)*100 if total > 0 else 0, quality_descriptions[tier])
                )
            
            self.db_conn.commit()
            self.logger.debug("Database statistics updated")
            
        except Exception as e:
            self.logger.error(f"Error updating database statistics: {e}")
    
    def _log_final_summary(self, spider):
        """Log final processing summary"""
        total = len(self.municipalities_data)
        complete = sum(1 for m in self.municipalities_data.values() if m.get('status') == 'complete')
        partial = sum(1 for m in self.municipalities_data.values() if m.get('status') == 'partial')
        processing_time = (datetime.now() - self.processing_stats['start_time']).total_seconds() / 60
        
        spider.logger.info("=== Phase 1 Data Pipeline Final Summary ===")
        spider.logger.info(f"Processing completed in {processing_time:.1f} minutes")
        spider.logger.info(f"Total municipalities: {total}")
        spider.logger.info(f"Complete data: {complete} ({complete/total*100:.1f}%)" if total > 0 else "Complete data: 0")
        spider.logger.info(f"Partial data: {partial} ({partial/total*100:.1f}%)" if total > 0 else "Partial data: 0")
        spider.logger.info(f"Items processed: {self.processing_stats['items_processed']}")
        spider.logger.info(f"Items exported: {self.processing_stats['items_exported']}")
        spider.logger.info(f"Errors encountered: {len(self.processing_stats['errors'])}")
        
        spider.logger.info(f"\nGenerated files:")
        spider.logger.info(f"  CSV: {self.csv_file_path}")
        spider.logger.info(f"  Database: {self.db_path}")
        spider.logger.info(f"  Statistics: {self.stats_file_path}")
        spider.logger.info(f"  Comparison: {self.comparison_file_path}")
        if PANDAS_AVAILABLE:
            spider.logger.info(f"  Excel: {self.excel_file_path}")
        
        if self.processing_stats['errors']:
            spider.logger.warning(f"Errors encountered during processing:")
            for error in self.processing_stats['errors'][:5]:  # Show first 5 errors
                spider.logger.warning(f"  - {error}")
            if len(self.processing_stats['errors']) > 5:
                spider.logger.warning(f"  ... and {len(self.processing_stats['errors']) - 5} more errors")
        
        spider.logger.info("=== End Phase 1 Data Pipeline Summary ===")

def export_phase1_data_to_csv(municipalities_data: Dict, output_path: str) -> bool:
    """Standalone function to export Phase 1 data to CSV"""
    try:
        fieldnames = [
            'municipality', 'timtaxa_livsmedel', 'debitering_livsmedel', 
            'timtaxa_bygglov', 'completeness_score', 'data_quality',
            'source_url', 'confidence', 'status'
        ]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for municipality, data in municipalities_data.items():
                row = {field: data.get(field, '') for field in fieldnames}
                writer.writerow(row)
        
        return True
    except Exception as e:
        logging.error(f"Error exporting to CSV: {e}")
        return False 