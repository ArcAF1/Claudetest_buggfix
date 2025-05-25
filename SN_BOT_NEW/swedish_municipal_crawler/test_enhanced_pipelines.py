#!/usr/bin/env python3
"""
Test script for enhanced pipeline components
Tests validation, duplicate detection, and data export pipelines
"""

import asyncio
import logging
import sys
import os
import tempfile
import sqlite3
import json
from datetime import datetime
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crawler.pipelines.enhanced_validation_pipeline import EnhancedValidationPipeline
from crawler.pipelines.enhanced_duplicate_pipeline import EnhancedDuplicatesPipeline
from crawler.pipelines.enhanced_data_pipeline import EnhancedSwedishFeeDataPipeline

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

class MockSpider:
    """Mock spider for pipeline testing"""
    
    def __init__(self):
        self.name = 'test_spider'
        self.logger = logger

class EnhancedPipelineTester:
    """Comprehensive tester for enhanced pipeline components"""
    
    def __init__(self):
        self.validation_pipeline = EnhancedValidationPipeline()
        self.duplicate_pipeline = EnhancedDuplicatesPipeline()
        
        # Create temporary directory for data pipeline testing
        self.temp_dir = tempfile.mkdtemp()
        
        # Monkey patch the data pipeline to use temp directory
        self.data_pipeline = EnhancedSwedishFeeDataPipeline()
        self.data_pipeline.output_dir = Path(self.temp_dir)
        
        self.spider = MockSpider()
        
        # Test data - comprehensive fee items with various quality levels
        self.test_items = [
            # High quality item
            {
                'municipality': 'Stockholm',
                'municipality_org_number': '212000-0142',
                'fee_name': 'Bygglov för enbostadshus',
                'amount': 15000,
                'currency': 'SEK',
                'unit': 'kr',
                'category': 'bygglov',
                'description': 'Handläggningsavgift för bygglov av enbostadshus upp till 120 kvm',
                'bygglov_type': 'nybyggnad_enbostadshus',
                'area_based': True,
                'pbb_based': False,
                'source_url': 'https://stockholm.se/avgifter.pdf',
                'source_type': 'PDF',
                'extraction_method': 'bygglov_enhanced',
                'extraction_date': datetime.now().isoformat(),
                'cms_type': 'sitevision',
                'municipality_type': 'storstad',
                'confidence': 0.9,
                'context': 'Bygglovsavgifter enligt taxa för 2024'
            },
            
            # Medium quality item
            {
                'municipality': 'Göteborg',
                'fee_name': 'Miljötillstånd restaurang',
                'amount': 8500,
                'currency': 'SEK',
                'category': 'miljö',
                'description': 'Tillstånd för restaurangverksamhet',
                'source_url': 'https://goteborg.se/avgifter',
                'source_type': 'HTML',
                'extraction_method': 'municipio_table',
                'extraction_date': datetime.now().isoformat(),
                'cms_type': 'municipio',
                'confidence': 0.7,
                'context': 'Miljötillstånd och avgifter'
            },
            
            # Duplicate of first item (slightly different)
            {
                'municipality': 'Stockholm',
                'fee_name': 'Bygglov enbostadshus',  # Slightly different name
                'amount': 15000,
                'currency': 'SEK',
                'category': 'bygglov',
                'source_url': 'https://stockholm.se/bygglov',
                'source_type': 'HTML',
                'extraction_method': 'sitevision_enhanced',
                'confidence': 0.8,
                'context': 'Bygglovsavgifter'
            },
            
            # Low quality item (should be rejected)
            {
                'municipality': 'Test',
                'fee_name': 'Te',  # Too short
                'amount': 1000000,  # Too high
                'currency': 'USD',  # Wrong currency
                'source_url': 'https://example.com',
                'extraction_method': 'test',
                'confidence': 0.2
            },
            
            # Another valid item
            {
                'municipality': 'Malmö',
                'fee_name': 'Serveringstillstånd',
                'amount': 6500,
                'currency': 'SEK',
                'category': 'livsmedel',
                'source_url': 'https://malmo.se/avgifter.pdf',
                'source_type': 'PDF',
                'extraction_method': 'pdf_enhanced',
                'confidence': 0.85,
                'validation': {
                    'confidence_score': 0.85,
                    'warnings': [],
                    'validation_version': '2.0'
                },
                'quality': {
                    'overall_score': 0.8,
                    'data_completeness': 0.9,
                    'content_quality': 0.75,
                    'source_reliability': 0.85
                }
            },
            
            # Duplicate with higher quality (should replace)
            {
                'municipality': 'Göteborg',
                'fee_name': 'Miljötillstånd för restaurang',
                'amount': 8500,
                'currency': 'SEK',
                'category': 'miljö',
                'description': 'Detaljerad beskrivning av miljötillstånd för restaurangverksamhet med fullständig information',
                'source_url': 'https://goteborg.se/miljotillstand.pdf',
                'source_type': 'PDF',
                'extraction_method': 'pdf_enhanced',
                'confidence': 0.95,
                'validation': {
                    'confidence_score': 0.95,
                    'warnings': [],
                    'validation_version': '2.0'
                },
                'quality': {
                    'overall_score': 0.9,
                    'data_completeness': 0.95,
                    'content_quality': 0.9,
                    'source_reliability': 0.9
                }
            }
        ]
    
    async def test_all_pipelines(self):
        """Test all enhanced pipelines in sequence"""
        logger.info("=== Testing Enhanced Pipeline Components ===")
        
        results = {
            'validation': await self.test_validation_pipeline(),
            'duplicate_detection': await self.test_duplicate_pipeline(),
            'data_export': await self.test_data_pipeline(),
            'integration': await self.test_pipeline_integration()
        }
        
        # Cleanup
        self._cleanup()
        
        # Summary
        logger.info("\n=== Pipeline Test Summary ===")
        for pipeline, result in results.items():
            logger.info(f"{pipeline.upper()}: {result['status']}")
            if result.get('items_processed'):
                logger.info(f"  Items processed: {result['items_processed']}")
            if result.get('items_valid'):
                logger.info(f"  Items valid: {result['items_valid']}")
            if result.get('duplicates_removed'):
                logger.info(f"  Duplicates removed: {result['duplicates_removed']}")
        
        return results
    
    async def test_validation_pipeline(self):
        """Test enhanced validation pipeline"""
        logger.info("\n--- Testing Enhanced Validation Pipeline ---")
        
        result = {
            'status': 'PASS',
            'items_processed': 0,
            'items_valid': 0,
            'items_rejected': 0,
            'errors': []
        }
        
        try:
            # Initialize pipeline
            self.validation_pipeline.open_spider(self.spider)
            
            for item in self.test_items:
                try:
                    validated_item = self.validation_pipeline.process_item(item.copy(), self.spider)
                    result['items_valid'] += 1
                    
                    # Check if validation metadata was added
                    if 'validation' in validated_item:
                        confidence = validated_item['validation'].get('confidence_score', 0)
                        logger.info(f"✓ Validated: {validated_item.get('fee_name', 'Unknown')} (confidence: {confidence:.2f})")
                    else:
                        logger.info(f"✓ Validated: {validated_item.get('fee_name', 'Unknown')}")
                    
                except Exception as e:
                    result['items_rejected'] += 1
                    logger.info(f"✗ Rejected: {item.get('fee_name', 'Unknown')} - {e}")
                
                result['items_processed'] += 1
            
            # Close pipeline and get stats
            self.validation_pipeline.close_spider(self.spider)
            
            logger.info(f"Validation results: {result['items_valid']} valid, {result['items_rejected']} rejected")
            
        except Exception as e:
            logger.error(f"Validation pipeline test failed: {e}")
            result['status'] = 'FAIL'
            result['errors'].append(str(e))
        
        return result
    
    async def test_duplicate_pipeline(self):
        """Test enhanced duplicate detection pipeline"""
        logger.info("\n--- Testing Enhanced Duplicate Detection Pipeline ---")
        
        result = {
            'status': 'PASS',
            'items_processed': 0,
            'duplicates_removed': 0,
            'duplicates_merged': 0,
            'quality_upgrades': 0,
            'errors': []
        }
        
        try:
            # Process items through duplicate detection
            processed_items = []
            
            for item in self.test_items:
                try:
                    processed_item = self.duplicate_pipeline.process_item(item.copy(), self.spider)
                    processed_items.append(processed_item)
                    logger.info(f"✓ Processed: {processed_item.get('fee_name', 'Unknown')}")
                    
                except Exception as e:
                    if "Duplicate fee" in str(e):
                        result['duplicates_removed'] += 1
                        logger.info(f"✗ Duplicate removed: {item.get('fee_name', 'Unknown')}")
                    else:
                        logger.error(f"Error processing {item.get('fee_name', 'Unknown')}: {e}")
                        result['errors'].append(str(e))
                
                result['items_processed'] += 1
            
            # Get final stats from pipeline
            result['duplicates_merged'] = self.duplicate_pipeline.duplicates_merged
            result['quality_upgrades'] = self.duplicate_pipeline.quality_upgrades
            
            # Close pipeline
            self.duplicate_pipeline.close_spider(self.spider)
            
            logger.info(f"Duplicate detection results: {len(processed_items)} unique items, "
                       f"{result['duplicates_removed']} duplicates removed, "
                       f"{result['duplicates_merged']} merged, "
                       f"{result['quality_upgrades']} quality upgrades")
            
        except Exception as e:
            logger.error(f"Duplicate detection test failed: {e}")
            result['status'] = 'FAIL'
            result['errors'].append(str(e))
        
        return result
    
    async def test_data_pipeline(self):
        """Test enhanced data export pipeline"""
        logger.info("\n--- Testing Enhanced Data Export Pipeline ---")
        
        result = {
            'status': 'PASS',
            'items_processed': 0,
            'files_created': [],
            'database_tables': 0,
            'errors': []
        }
        
        try:
            # Initialize data pipeline
            self.data_pipeline.open_spider(self.spider)
            
            # Process valid items
            valid_items = [item for item in self.test_items if item.get('fee_name', '') != 'Te']
            
            for item in valid_items:
                try:
                    processed_item = self.data_pipeline.process_item(item.copy(), self.spider)
                    result['items_processed'] += 1
                    logger.info(f"✓ Exported: {item.get('fee_name', 'Unknown')}")
                    
                except Exception as e:
                    logger.error(f"Error exporting {item.get('fee_name', 'Unknown')}: {e}")
                    result['errors'].append(str(e))
            
            # Close pipeline (generates final outputs)
            self.data_pipeline.close_spider(self.spider)
            
            # Check created files
            output_files = list(Path(self.temp_dir).glob('*'))
            result['files_created'] = [f.name for f in output_files]
            
            logger.info(f"Created files: {result['files_created']}")
            
            # Check database
            db_files = [f for f in output_files if f.suffix == '.db']
            if db_files:
                db_path = db_files[0]
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Check tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                result['database_tables'] = len(tables)
                
                # Check data
                cursor.execute("SELECT COUNT(*) FROM fees")
                fee_count = cursor.fetchone()[0]
                
                logger.info(f"Database: {len(tables)} tables, {fee_count} fees")
                conn.close()
            
            # Check Excel file
            excel_files = [f for f in output_files if f.suffix == '.xlsx']
            if excel_files:
                logger.info(f"Excel file created: {excel_files[0].name}")
            
            # Check statistics file
            stats_files = [f for f in output_files if 'statistics' in f.name]
            if stats_files:
                with open(stats_files[0], 'r') as f:
                    stats = json.load(f)
                logger.info(f"Statistics: {stats.get('total_fees', 0)} fees, "
                           f"{stats.get('municipalities_count', 0)} municipalities")
            
        except Exception as e:
            logger.error(f"Data pipeline test failed: {e}")
            result['status'] = 'FAIL'
            result['errors'].append(str(e))
        
        return result
    
    async def test_pipeline_integration(self):
        """Test full pipeline integration"""
        logger.info("\n--- Testing Pipeline Integration ---")
        
        result = {
            'status': 'PASS',
            'items_input': len(self.test_items),
            'items_output': 0,
            'pipeline_chain': ['validation', 'duplicate_detection', 'data_export'],
            'errors': []
        }
        
        try:
            # Create fresh pipeline instances
            validation = EnhancedValidationPipeline()
            duplicates = EnhancedDuplicatesPipeline()
            data_export = EnhancedSwedishFeeDataPipeline()
            data_export.output_dir = Path(self.temp_dir) / 'integration'
            data_export.output_dir.mkdir(exist_ok=True)
            
            # Initialize all pipelines
            validation.open_spider(self.spider)
            data_export.open_spider(self.spider)
            
            # Process items through full pipeline chain
            final_items = []
            
            for item in self.test_items:
                try:
                    # Step 1: Validation
                    validated_item = validation.process_item(item.copy(), self.spider)
                    
                    # Step 2: Duplicate detection
                    deduped_item = duplicates.process_item(validated_item, self.spider)
                    
                    # Step 3: Data export
                    exported_item = data_export.process_item(deduped_item, self.spider)
                    
                    final_items.append(exported_item)
                    
                except Exception as e:
                    # Expected for invalid/duplicate items
                    logger.debug(f"Item filtered out: {item.get('fee_name', 'Unknown')} - {e}")
            
            result['items_output'] = len(final_items)
            
            # Close all pipelines
            validation.close_spider(self.spider)
            duplicates.close_spider(self.spider)
            data_export.close_spider(self.spider)
            
            logger.info(f"Integration test: {result['items_input']} input → {result['items_output']} output")
            
            # Verify final output quality
            for item in final_items:
                if 'validation' not in item:
                    result['errors'].append(f"Missing validation metadata: {item.get('fee_name')}")
                
                if not item.get('municipality'):
                    result['errors'].append(f"Missing municipality: {item.get('fee_name')}")
            
            if result['errors']:
                result['status'] = 'FAIL'
            
        except Exception as e:
            logger.error(f"Pipeline integration test failed: {e}")
            result['status'] = 'FAIL'
            result['errors'].append(str(e))
        
        return result
    
    def _cleanup(self):
        """Clean up temporary files"""
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
            logger.info(f"Cleaned up temporary directory: {self.temp_dir}")
        except Exception as e:
            logger.warning(f"Failed to cleanup temp directory: {e}")

async def main():
    """Main test function"""
    logger.info("Starting Enhanced Pipeline Component Tests")
    logger.info(f"Test started at: {datetime.now().isoformat()}")
    
    tester = EnhancedPipelineTester()
    
    try:
        # Run all tests
        results = await tester.test_all_pipelines()
        
        # Final summary
        logger.info("\n" + "="*60)
        logger.info("FINAL PIPELINE TEST SUMMARY")
        logger.info("="*60)
        
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result['status'] == 'PASS')
        
        logger.info(f"Tests passed: {passed_tests}/{total_tests}")
        
        if passed_tests == total_tests:
            logger.info("🎉 All pipeline tests PASSED!")
            return 0
        else:
            logger.error("❌ Some pipeline tests FAILED!")
            
            # Show failed tests
            for test_name, result in results.items():
                if result['status'] == 'FAIL':
                    logger.error(f"FAILED: {test_name}")
                    for error in result.get('errors', []):
                        logger.error(f"  - {error}")
            
            return 1
    
    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        return 1

if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 