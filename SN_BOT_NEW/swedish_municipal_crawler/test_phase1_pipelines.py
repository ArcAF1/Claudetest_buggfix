#!/usr/bin/env python3
"""
Test script for Phase 1 Enhanced Pipeline Components
Tests validation, duplicate detection, and data export pipelines
"""

import sys
import os
import logging
import tempfile
import sqlite3
from pathlib import Path
from datetime import datetime

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crawler.pipelines.phase1_enhanced_validation_pipeline import Phase1EnhancedValidationPipeline
from crawler.pipelines.phase1_duplicate_pipeline import Phase1DuplicatesPipeline
from crawler.pipelines.phase1_data_pipeline import Phase1DataPipeline
from crawler.items import Phase1DataItem

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

class MockSpider:
    """Mock spider for testing pipelines"""
    def __init__(self):
        self.logger = logging.getLogger('test_spider')

class Phase1PipelineTester:
    """Test Phase 1 pipeline components"""
    
    def __init__(self):
        self.spider = MockSpider()
        
        # Sample test data representing different quality levels
        self.test_items = [
            # Complete high-quality item
            {
                'municipality': 'Stockholm',
                'timtaxa_livsmedel': 1350,
                'debitering_livsmedel': 'förskott',
                'timtaxa_bygglov': 1200,
                'source_url': 'https://stockholm.se/taxor.pdf',
                'source_type': 'PDF',
                'extraction_date': datetime.now().isoformat(),
                'confidence': 0.95,
                'extraction_method': 'phase1_pdf_enhanced'
            },
            # Partial data item
            {
                'municipality': 'Göteborg',
                'timtaxa_livsmedel': 1400,
                'debitering_livsmedel': 'efterhand',
                'source_url': 'https://goteborg.se/avgifter.html',
                'source_type': 'HTML',
                'extraction_date': datetime.now().isoformat(),
                'confidence': 0.80,
                'extraction_method': 'phase1_html'
            },
            # Another partial item
            {
                'municipality': 'Malmö',
                'timtaxa_bygglov': 1300,
                'source_url': 'https://malmo.se/bygglov.pdf',
                'source_type': 'PDF',
                'extraction_date': datetime.now().isoformat(),
                'confidence': 0.75,
                'extraction_method': 'phase1_pdf'
            },
            # Duplicate with lower quality (should be rejected)
            {
                'municipality': 'Stockholm',
                'timtaxa_livsmedel': 1300,  # Different value
                'source_url': 'https://stockholm.se/old-taxor.html',
                'source_type': 'HTML',
                'extraction_date': datetime.now().isoformat(),
                'confidence': 0.60,  # Lower confidence
                'extraction_method': 'phase1_html'
            },
            # Duplicate with higher quality (should replace)
            {
                'municipality': 'Göteborg',
                'timtaxa_livsmedel': 1400,
                'debitering_livsmedel': 'efterhand',
                'timtaxa_bygglov': 1250,  # Additional field
                'source_url': 'https://goteborg.se/nya-taxor.pdf',
                'source_type': 'PDF',
                'extraction_date': datetime.now().isoformat(),
                'confidence': 0.90,  # Higher confidence
                'extraction_method': 'phase1_pdf_enhanced'
            },
            # Invalid data (should be rejected)
            {
                'municipality': 'Uppsala',
                'timtaxa_livsmedel': 5000,  # Out of range
                'debitering_livsmedel': 'invalid_model',  # Invalid value
                'source_url': 'https://uppsala.se/test.html',
                'source_type': 'HTML',
                'extraction_date': datetime.now().isoformat(),
                'confidence': 0.30,
                'extraction_method': 'phase1_html'
            },
            # Edge case - municipality name variations
            {
                'municipality': 'Västerås kommun',  # Should be normalized
                'timtaxa_livsmedel': 1250,
                'debitering_livsmedel': 'förskott',
                'source_url': 'https://vasteras.se/taxor.pdf',
                'source_type': 'PDF',
                'extraction_date': datetime.now().isoformat(),
                'confidence': 0.85,
                'extraction_method': 'phase1_pdf'
            }
        ]
    
    def test_validation_pipeline(self):
        """Test the enhanced validation pipeline"""
        logger.info("=== Testing Phase 1 Enhanced Validation Pipeline ===")
        
        pipeline = Phase1EnhancedValidationPipeline()
        results = {'passed': 0, 'failed': 0, 'enhanced': 0}
        
        for i, test_data in enumerate(self.test_items):
            logger.info(f"\nTesting item {i+1}: {test_data.get('municipality')}")
            
            # Create Phase1DataItem
            item = Phase1DataItem()
            for key, value in test_data.items():
                item[key] = value
            
            try:
                processed_item = pipeline.process_item(item, self.spider)
                
                # Check if item was enhanced
                if processed_item.get('municipality') != test_data.get('municipality'):
                    results['enhanced'] += 1
                    logger.info(f"✓ Municipality name enhanced: {test_data.get('municipality')} -> {processed_item.get('municipality')}")
                
                # Check validation results
                completeness = processed_item.get('completeness_score', 0)
                quality = processed_item.get('data_quality', 0)
                status = processed_item.get('status', 'unknown')
                
                logger.info(f"✓ Validation passed: completeness={completeness:.2f}, quality={quality:.1f}, status={status}")
                results['passed'] += 1
                
            except Exception as e:
                logger.info(f"✗ Validation failed: {e}")
                results['failed'] += 1
        
        # Test pipeline statistics
        pipeline.close_spider(self.spider)
        
        logger.info(f"\nValidation Pipeline Results:")
        logger.info(f"  Passed: {results['passed']}")
        logger.info(f"  Failed: {results['failed']}")
        logger.info(f"  Enhanced: {results['enhanced']}")
        
        return results
    
    def test_duplicate_pipeline(self):
        """Test the duplicate detection pipeline"""
        logger.info("\n=== Testing Phase 1 Duplicate Detection Pipeline ===")
        
        pipeline = Phase1DuplicatesPipeline()
        results = {'processed': 0, 'duplicates_removed': 0, 'replacements': 0}
        
        # First pass validation to get valid items
        validation_pipeline = Phase1EnhancedValidationPipeline()
        valid_items = []
        
        for test_data in self.test_items:
            item = Phase1DataItem()
            for key, value in test_data.items():
                item[key] = value
            
            try:
                validated_item = validation_pipeline.process_item(item, self.spider)
                valid_items.append(validated_item)
            except:
                continue  # Skip invalid items
        
        # Test duplicate detection
        processed_items = []
        for item in valid_items:
            try:
                processed_item = pipeline.process_item(item, self.spider)
                processed_items.append(processed_item)
                results['processed'] += 1
                logger.info(f"✓ Processed: {processed_item.get('municipality')}")
            except Exception as e:
                if "Duplicate municipality" in str(e):
                    results['duplicates_removed'] += 1
                    logger.info(f"✓ Duplicate removed: {str(e)}")
                else:
                    logger.error(f"✗ Unexpected error: {e}")
        
        # Check statistics
        stats = pipeline.get_duplicate_statistics()
        results['replacements'] = stats['replacements_made']
        
        pipeline.close_spider(self.spider)
        
        logger.info(f"\nDuplicate Pipeline Results:")
        logger.info(f"  Unique items processed: {results['processed']}")
        logger.info(f"  Duplicates removed: {results['duplicates_removed']}")
        logger.info(f"  Quality replacements: {results['replacements']}")
        
        return results, processed_items
    
    def test_data_pipeline(self, test_items):
        """Test the data export pipeline"""
        logger.info("\n=== Testing Phase 1 Data Pipeline ===")
        
        # Create temporary output directory
        with tempfile.TemporaryDirectory() as temp_dir:
            pipeline = Phase1DataPipeline(output_dir=temp_dir)
            pipeline.open_spider(self.spider)
            
            results = {'exported': 0, 'errors': 0}
            
            # Process items
            for item in test_items:
                try:
                    pipeline.process_item(item, self.spider)
                    results['exported'] += 1
                    logger.info(f"✓ Exported: {item.get('municipality')}")
                except Exception as e:
                    results['errors'] += 1
                    logger.error(f"✗ Export error for {item.get('municipality')}: {e}")
            
            # Close pipeline and generate reports
            pipeline.close_spider(self.spider)
            
            # Check generated files
            output_path = Path(temp_dir)
            generated_files = list(output_path.glob('*'))
            
            logger.info(f"\nData Pipeline Results:")
            logger.info(f"  Items exported: {results['exported']}")
            logger.info(f"  Export errors: {results['errors']}")
            logger.info(f"  Files generated: {len(generated_files)}")
            
            for file_path in generated_files:
                logger.info(f"    - {file_path.name} ({file_path.stat().st_size} bytes)")
                
                # Verify file contents for key files
                if file_path.suffix == '.csv' and 'municipal_data' in file_path.name:
                    self._verify_csv_content(file_path)
                elif file_path.suffix == '.db':
                    self._verify_database_content(file_path)
                elif file_path.suffix == '.json' and 'statistics' in file_path.name:
                    self._verify_statistics_content(file_path)
            
            return results
    
    def _verify_csv_content(self, csv_path):
        """Verify CSV file content"""
        try:
            import csv
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                
            logger.info(f"    CSV verification: {len(rows)} data rows")
            
            # Check required columns
            required_columns = ['municipality', 'timtaxa_livsmedel', 'debitering_livsmedel', 'timtaxa_bygglov']
            if all(col in reader.fieldnames for col in required_columns):
                logger.info("    ✓ All required columns present")
            else:
                logger.warning("    ⚠ Missing required columns")
                
        except Exception as e:
            logger.error(f"    ✗ CSV verification failed: {e}")
    
    def _verify_database_content(self, db_path):
        """Verify SQLite database content"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check main data table
            cursor.execute("SELECT COUNT(*) FROM phase1_data")
            data_count = cursor.fetchone()[0]
            
            # Check statistics tables
            cursor.execute("SELECT COUNT(*) FROM extraction_summary")
            summary_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM field_coverage")
            coverage_count = cursor.fetchone()[0]
            
            conn.close()
            
            logger.info(f"    Database verification:")
            logger.info(f"      Data records: {data_count}")
            logger.info(f"      Summary metrics: {summary_count}")
            logger.info(f"      Coverage records: {coverage_count}")
            
        except Exception as e:
            logger.error(f"    ✗ Database verification failed: {e}")
    
    def _verify_statistics_content(self, stats_path):
        """Verify statistics JSON content"""
        try:
            import json
            with open(stats_path, 'r', encoding='utf-8') as f:
                stats = json.load(f)
            
            required_sections = ['extraction_metadata', 'completeness_analysis', 'field_coverage', 'success_metrics']
            present_sections = [section for section in required_sections if section in stats]
            
            logger.info(f"    Statistics verification:")
            logger.info(f"      Sections present: {len(present_sections)}/{len(required_sections)}")
            
            if 'success_metrics' in stats:
                success_rate = stats['success_metrics'].get('overall_success_rate', 0)
                logger.info(f"      Overall success rate: {success_rate:.1f}%")
                
        except Exception as e:
            logger.error(f"    ✗ Statistics verification failed: {e}")
    
    def run_all_tests(self):
        """Run all pipeline tests"""
        logger.info("Starting Phase 1 Pipeline Component Tests")
        
        # Test validation pipeline
        validation_results = self.test_validation_pipeline()
        
        # Test duplicate detection pipeline
        duplicate_results, processed_items = self.test_duplicate_pipeline()
        
        # Test data export pipeline
        data_results = self.test_data_pipeline(processed_items)
        
        # Overall summary
        logger.info("\n" + "="*60)
        logger.info("PHASE 1 PIPELINE TESTS SUMMARY")
        logger.info("="*60)
        
        logger.info("Validation Pipeline:")
        logger.info(f"  Items passed validation: {validation_results['passed']}")
        logger.info(f"  Items failed validation: {validation_results['failed']}")
        logger.info(f"  Items enhanced: {validation_results['enhanced']}")
        
        logger.info("Duplicate Detection Pipeline:")
        logger.info(f"  Unique items processed: {duplicate_results['processed']}")
        logger.info(f"  Duplicates removed: {duplicate_results['duplicates_removed']}")
        logger.info(f"  Quality replacements: {duplicate_results['replacements']}")
        
        logger.info("Data Export Pipeline:")
        logger.info(f"  Items exported: {data_results['exported']}")
        logger.info(f"  Export errors: {data_results['errors']}")
        
        # Calculate overall success
        total_tests = (validation_results['passed'] + validation_results['failed'] + 
                      duplicate_results['processed'] + duplicate_results['duplicates_removed'] +
                      data_results['exported'] + data_results['errors'])
        
        successful_tests = (validation_results['passed'] + duplicate_results['processed'] + 
                           data_results['exported'])
        
        if total_tests > 0:
            success_rate = (successful_tests / total_tests) * 100
            logger.info(f"\nOverall Pipeline Success Rate: {success_rate:.1f}%")
            
            if success_rate >= 80:
                logger.info("🎉 Phase 1 pipelines are working well!")
                return 0
            else:
                logger.warning("⚠️ Phase 1 pipelines need improvement")
                return 1
        else:
            logger.error("❌ No tests were run")
            return 1

def main():
    """Main test function"""
    tester = Phase1PipelineTester()
    return tester.run_all_tests()

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code) 