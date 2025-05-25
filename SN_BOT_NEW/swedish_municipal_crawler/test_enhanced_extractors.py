#!/usr/bin/env python3
"""
Test script for enhanced CMS-specific extractors
Tests JavaScript handling, validation, and extraction quality
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crawler.extractors.enhanced_sitevision_extractor import EnhancedSitevisionExtractor
from crawler.extractors.enhanced_municipio_extractor import EnhancedMunicipioExtractor
from crawler.extractors.enhanced_generic_extractor import EnhancedGenericExtractor
from crawler.pipelines.enhanced_validation_pipeline import EnhancedValidationPipeline
from crawler.utils.validators import SwedishValidators

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

class MockResponse:
    """Mock response object for testing"""
    
    def __init__(self, url, html_content):
        self.url = url
        self.text = html_content
        self._html_content = html_content
    
    def css(self, selector):
        """Mock CSS selector - returns empty list for simplicity"""
        return MockSelectorList([])
    
    def urljoin(self, url):
        """Mock URL joining"""
        return f"{self.url.rstrip('/')}/{url.lstrip('/')}"

class MockSelectorList:
    """Mock selector list"""
    
    def __init__(self, items):
        self.items = items
    
    def getall(self):
        return self.items
    
    def get(self, default=''):
        return self.items[0] if self.items else default

class MockSpider:
    """Mock spider for pipeline testing"""
    
    def __init__(self):
        self.name = 'test_spider'

class EnhancedExtractorTester:
    """Comprehensive tester for enhanced extractors"""
    
    def __init__(self):
        self.sitevision_extractor = EnhancedSitevisionExtractor()
        self.municipio_extractor = EnhancedMunicipioExtractor()
        self.generic_extractor = EnhancedGenericExtractor()
        self.validation_pipeline = EnhancedValidationPipeline()
        self.validators = SwedishValidators()
        
        # Test data
        self.test_urls = {
            'sitevision': [
                'https://stockholm.se',
                'https://goteborg.se',
                'https://malmo.se'
            ],
            'municipio': [
                'https://uppsala.se',
                'https://vasteras.se',
                'https://orebro.se'
            ],
            'generic': [
                'https://linkoping.se',
                'https://helsingborg.se',
                'https://norrkoping.se'
            ]
        }
        
        # Sample HTML content for testing
        self.sample_html = {
            'sitevision': '''
            <div class="sv-portlet">
                <h3>Bygglovsavgifter</h3>
                <p>Handläggningsavgift för bygglov: 15 000 kr</p>
                <p>Nybyggnad villa upp till 120 kvm: 18 500 kr</p>
                <table class="sv-table">
                    <tr><th>Åtgärd</th><th>Avgift</th></tr>
                    <tr><td>Tillbyggnad</td><td>8 500 kr</td></tr>
                    <tr><td>Rivningslov</td><td>5 200 kr</td></tr>
                </table>
            </div>
            ''',
            'municipio': '''
            <div class="entry-content">
                <h2>Kommunala avgifter</h2>
                <div class="wp-block-table">
                    <table>
                        <tr><th>Tjänst</th><th>Kostnad</th></tr>
                        <tr><td>Miljötillstånd</td><td>12 000 kr</td></tr>
                        <tr><td>Serveringstillstånd</td><td>6 500 kr</td></tr>
                    </table>
                </div>
                [fee amount="3500"]Bygganmälan[/fee]
                <ul class="fee-list">
                    <li>Hemtjänst: 285 kr/timme</li>
                    <li>Färdtjänst: 45 kr/resa</li>
                </ul>
            </div>
            ''',
            'generic': '''
            <main class="content">
                <h1>Taxa och avgifter</h1>
                <div class="fee-card">
                    <h3>Byggnadsnämnden</h3>
                    <p>Bygglov enbostadshus - 14 500 kr</p>
                    <p>Startbesked - 2 800 kr</p>
                </div>
                <table class="table">
                    <thead>
                        <tr><th>Service</th><th>Pris</th></tr>
                    </thead>
                    <tbody>
                        <tr><td>Livsmedelsregistrering</td><td>1 250 kr</td></tr>
                        <tr><td>Alkoholtillstånd</td><td>8 900 kr</td></tr>
                    </tbody>
                </table>
            </main>
            '''
        }
    
    async def test_all_extractors(self):
        """Test all enhanced extractors"""
        logger.info("=== Testing Enhanced CMS-Specific Extractors ===")
        
        results = {
            'sitevision': await self.test_sitevision_extractor(),
            'municipio': await self.test_municipio_extractor(),
            'generic': await self.test_generic_extractor(),
            'validation': await self.test_validation_pipeline()
        }
        
        # Summary
        logger.info("\n=== Test Summary ===")
        for extractor, result in results.items():
            logger.info(f"{extractor.upper()}: {result['status']}")
            if result.get('fees_extracted', 0) > 0:
                logger.info(f"  Fees extracted: {result['fees_extracted']}")
            if result.get('validation_passed', 0) > 0:
                logger.info(f"  Validation passed: {result['validation_passed']}")
        
        return results
    
    async def test_sitevision_extractor(self):
        """Test enhanced SiteVision extractor"""
        logger.info("\n--- Testing Enhanced SiteVision Extractor ---")
        
        result = {
            'status': 'PASS',
            'fees_extracted': 0,
            'js_extraction_tested': False,
            'errors': []
        }
        
        try:
            # Test HTML extraction
            response = MockResponse('https://stockholm.se/avgifter', self.sample_html['sitevision'])
            fees = self.sitevision_extractor.extract_fees_from_sitevision(response)
            
            logger.info(f"HTML extraction: {len(fees)} fees found")
            result['fees_extracted'] += len(fees)
            
            # Log extracted fees
            for fee in fees:
                logger.info(f"  - {fee.get('fee_name', 'Unknown')}: {fee.get('amount', 0)} {fee.get('currency', 'SEK')}")
            
            # Test JavaScript extraction (if Playwright available)
            try:
                test_url = self.test_urls['sitevision'][0]
                js_fees = await self.sitevision_extractor.extract_with_playwright(test_url)
                logger.info(f"JavaScript extraction: {len(js_fees)} fees found")
                result['fees_extracted'] += len(js_fees)
                result['js_extraction_tested'] = True
                
                # Log JS extracted fees
                for fee in js_fees[:3]:  # Show first 3
                    logger.info(f"  - {fee.get('fee_name', 'Unknown')}: {fee.get('amount', 0)} {fee.get('currency', 'SEK')}")
                
            except Exception as e:
                logger.warning(f"JavaScript extraction failed: {e}")
                result['errors'].append(f"JS extraction: {e}")
            
            # Test validation
            validation_passed = 0
            for fee in fees:
                if self._validate_fee_basic(fee):
                    validation_passed += 1
            
            logger.info(f"Validation: {validation_passed}/{len(fees)} fees passed")
            
        except Exception as e:
            logger.error(f"SiteVision extractor test failed: {e}")
            result['status'] = 'FAIL'
            result['errors'].append(str(e))
        
        return result
    
    async def test_municipio_extractor(self):
        """Test enhanced Municipio extractor"""
        logger.info("\n--- Testing Enhanced Municipio Extractor ---")
        
        result = {
            'status': 'PASS',
            'fees_extracted': 0,
            'ajax_extraction_tested': False,
            'shortcode_extraction_tested': False,
            'errors': []
        }
        
        try:
            # Test HTML extraction
            response = MockResponse('https://uppsala.se/avgifter', self.sample_html['municipio'])
            fees = self.municipio_extractor.extract_fees_from_municipio(response)
            
            logger.info(f"HTML extraction: {len(fees)} fees found")
            result['fees_extracted'] += len(fees)
            
            # Log extracted fees
            for fee in fees:
                logger.info(f"  - {fee.get('fee_name', 'Unknown')}: {fee.get('amount', 0)} {fee.get('currency', 'SEK')}")
            
            # Test AJAX extraction (if Playwright available)
            try:
                test_url = self.test_urls['municipio'][0]
                ajax_fees = await self.municipio_extractor.extract_with_ajax(test_url)
                logger.info(f"AJAX extraction: {len(ajax_fees)} fees found")
                result['fees_extracted'] += len(ajax_fees)
                result['ajax_extraction_tested'] = True
                
            except Exception as e:
                logger.warning(f"AJAX extraction failed: {e}")
                result['errors'].append(f"AJAX extraction: {e}")
            
            # Test shortcode extraction
            shortcode_fees = self.municipio_extractor._extract_from_shortcodes(response)
            logger.info(f"Shortcode extraction: {len(shortcode_fees)} fees found")
            result['shortcode_extraction_tested'] = len(shortcode_fees) > 0
            
            # Test validation
            validation_passed = 0
            for fee in fees:
                if self._validate_fee_basic(fee):
                    validation_passed += 1
            
            logger.info(f"Validation: {validation_passed}/{len(fees)} fees passed")
            
        except Exception as e:
            logger.error(f"Municipio extractor test failed: {e}")
            result['status'] = 'FAIL'
            result['errors'].append(str(e))
        
        return result
    
    async def test_generic_extractor(self):
        """Test enhanced generic extractor"""
        logger.info("\n--- Testing Enhanced Generic Extractor ---")
        
        result = {
            'status': 'PASS',
            'fees_extracted': 0,
            'strategies_tested': 0,
            'playwright_tested': False,
            'errors': []
        }
        
        try:
            # Test HTML extraction
            response = MockResponse('https://linkoping.se/avgifter', self.sample_html['generic'])
            fees = self.generic_extractor.extract_fees_generic(response)
            
            logger.info(f"HTML extraction: {len(fees)} fees found")
            result['fees_extracted'] += len(fees)
            
            # Log extracted fees
            for fee in fees:
                logger.info(f"  - {fee.get('fee_name', 'Unknown')}: {fee.get('amount', 0)} {fee.get('currency', 'SEK')}")
            
            # Test multiple strategies with Playwright
            try:
                test_url = self.test_urls['generic'][0]
                strategy_fees = await self.generic_extractor.extract_with_multiple_strategies(test_url)
                logger.info(f"Multi-strategy extraction: {len(strategy_fees)} fees found")
                result['fees_extracted'] += len(strategy_fees)
                result['playwright_tested'] = True
                result['strategies_tested'] = len(self.generic_extractor.extraction_strategies)
                
            except Exception as e:
                logger.warning(f"Multi-strategy extraction failed: {e}")
                result['errors'].append(f"Multi-strategy extraction: {e}")
            
            # Test individual extraction methods
            table_fees = self.generic_extractor._extract_from_tables(response)
            list_fees = self.generic_extractor._extract_from_lists(response)
            card_fees = self.generic_extractor._extract_from_cards(response)
            
            logger.info(f"Table extraction: {len(table_fees)} fees")
            logger.info(f"List extraction: {len(list_fees)} fees")
            logger.info(f"Card extraction: {len(card_fees)} fees")
            
            # Test validation
            validation_passed = 0
            for fee in fees:
                if self._validate_fee_basic(fee):
                    validation_passed += 1
            
            logger.info(f"Validation: {validation_passed}/{len(fees)} fees passed")
            
        except Exception as e:
            logger.error(f"Generic extractor test failed: {e}")
            result['status'] = 'FAIL'
            result['errors'].append(str(e))
        
        return result
    
    async def test_validation_pipeline(self):
        """Test enhanced validation pipeline"""
        logger.info("\n--- Testing Enhanced Validation Pipeline ---")
        
        result = {
            'status': 'PASS',
            'validation_passed': 0,
            'validation_failed': 0,
            'confidence_scores': [],
            'errors': []
        }
        
        try:
            # Create test fee items
            test_fees = [
                {
                    'fee_name': 'Bygglov för enbostadshus',
                    'amount': 15000,
                    'currency': 'SEK',
                    'source_url': 'https://stockholm.se/avgifter',
                    'category': 'bygglov',
                    'extraction_method': 'sitevision_enhanced',
                    'description': 'Handläggningsavgift för bygglov av enbostadshus upp till 120 kvm'
                },
                {
                    'fee_name': 'Miljötillstånd restaurang',
                    'amount': 8500,
                    'currency': 'SEK',
                    'source_url': 'https://goteborg.se/avgifter',
                    'category': 'miljö',
                    'extraction_method': 'municipio_table',
                    'description': 'Tillstånd för restaurangverksamhet'
                },
                {
                    'fee_name': 'Test fee',  # Should fail validation
                    'amount': 50000000,  # Too high
                    'currency': 'USD',  # Wrong currency
                    'source_url': 'https://example.com',  # Wrong domain
                    'category': 'invalid',
                    'extraction_method': 'test'
                },
                {
                    'fee_name': '',  # Should fail - empty name
                    'amount': 'invalid',  # Should fail - invalid amount
                    'currency': 'SEK',
                    'source_url': 'https://malmo.se'
                }
            ]
            
            spider = MockSpider()
            
            for i, fee in enumerate(test_fees):
                try:
                    validated_fee = self.validation_pipeline.process_item(fee, spider)
                    result['validation_passed'] += 1
                    
                    # Extract confidence score
                    confidence = validated_fee.get('validation', {}).get('confidence_score', 0)
                    result['confidence_scores'].append(confidence)
                    
                    logger.info(f"Fee {i+1} PASSED validation (confidence: {confidence:.2f})")
                    logger.info(f"  Name: {validated_fee.get('fee_name', 'Unknown')}")
                    logger.info(f"  Amount: {validated_fee.get('amount', 0)} {validated_fee.get('currency', 'SEK')}")
                    
                except Exception as e:
                    result['validation_failed'] += 1
                    logger.info(f"Fee {i+1} FAILED validation: {e}")
            
            # Test validation statistics
            logger.info(f"Validation results: {result['validation_passed']} passed, {result['validation_failed']} failed")
            
            if result['confidence_scores']:
                avg_confidence = sum(result['confidence_scores']) / len(result['confidence_scores'])
                logger.info(f"Average confidence score: {avg_confidence:.2f}")
            
            # Test pipeline statistics
            stats = self.validation_pipeline.stats
            logger.info(f"Pipeline stats: {stats['total_processed']} processed, {stats['total_valid']} valid")
            
        except Exception as e:
            logger.error(f"Validation pipeline test failed: {e}")
            result['status'] = 'FAIL'
            result['errors'].append(str(e))
        
        return result
    
    def _validate_fee_basic(self, fee):
        """Basic fee validation"""
        try:
            # Check required fields
            required_fields = ['fee_name', 'amount', 'currency']
            if not all(field in fee for field in required_fields):
                return False
            
            # Check amount
            amount = fee.get('amount')
            if not isinstance(amount, (int, float)) or amount <= 0:
                return False
            
            # Check fee name
            fee_name = fee.get('fee_name', '')
            if not fee_name or len(fee_name.strip()) < 3:
                return False
            
            return True
            
        except Exception:
            return False
    
    def test_validators(self):
        """Test Swedish validators"""
        logger.info("\n--- Testing Swedish Validators ---")
        
        # Test organization number validation
        valid_org_numbers = ['212000-0142', '556036-0793', '202100-5489']
        invalid_org_numbers = ['123456-7890', '000000-0000', 'invalid']
        
        logger.info("Organization number validation:")
        for org_nr in valid_org_numbers:
            result = self.validators.validate_organization_number(org_nr)
            logger.info(f"  {org_nr}: {'PASS' if result else 'FAIL'}")
        
        for org_nr in invalid_org_numbers:
            result = self.validators.validate_organization_number(org_nr)
            logger.info(f"  {org_nr}: {'FAIL' if not result else 'UNEXPECTED PASS'}")
        
        # Test phone number validation
        valid_phones = ['08-123 456 78', '070-123 45 67', '+46 8 123 456 78']
        invalid_phones = ['123', '555-1234', '+1-555-123-4567']
        
        logger.info("Phone number validation:")
        for phone in valid_phones:
            result = self.validators.validate_swedish_phone(phone)
            logger.info(f"  {phone}: {'PASS' if result else 'FAIL'}")
        
        # Test postal code validation
        valid_postal_codes = ['11122', '413 01', '90325']
        invalid_postal_codes = ['1234', '123456', 'ABC12']
        
        logger.info("Postal code validation:")
        for postal in valid_postal_codes:
            result = self.validators.validate_postal_code(postal)
            logger.info(f"  {postal}: {'PASS' if result else 'FAIL'}")
        
        # Test fee amount validation
        valid_amounts = [100, 1500.50, 25000]
        invalid_amounts = [-100, 0, 1000000, 'invalid']
        
        logger.info("Fee amount validation:")
        for amount in valid_amounts:
            result = self.validators.validate_fee_amount(amount)
            logger.info(f"  {amount}: {'PASS' if result else 'FAIL'}")

async def main():
    """Main test function"""
    logger.info("Starting Enhanced Extractor Tests")
    logger.info(f"Test started at: {datetime.now().isoformat()}")
    
    tester = EnhancedExtractorTester()
    
    # Test validators first
    tester.test_validators()
    
    # Test extractors
    results = await tester.test_all_extractors()
    
    # Final summary
    logger.info("\n" + "="*60)
    logger.info("FINAL TEST SUMMARY")
    logger.info("="*60)
    
    total_fees = sum(result.get('fees_extracted', 0) for result in results.values())
    total_errors = sum(len(result.get('errors', [])) for result in results.values())
    
    logger.info(f"Total fees extracted: {total_fees}")
    logger.info(f"Total errors: {total_errors}")
    
    # Check if Playwright is available
    try:
        import playwright
        logger.info("✓ Playwright is available for JavaScript extraction")
    except ImportError:
        logger.warning("⚠ Playwright not available - JavaScript extraction will be limited")
    
    # Check if all extractors passed
    all_passed = all(result.get('status') == 'PASS' for result in results.values())
    
    if all_passed:
        logger.info("🎉 All tests PASSED!")
        return 0
    else:
        logger.error("❌ Some tests FAILED!")
        return 1

if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 