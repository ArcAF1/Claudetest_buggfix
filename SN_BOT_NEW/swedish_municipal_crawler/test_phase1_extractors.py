#!/usr/bin/env python3
"""
Test script for Phase 1 extractors
Tests the three specific Phase 1 data point extractors
"""

import sys
import os
import logging
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crawler.extractors.phase1_extractors import (
    LivsmedelTimtaxaExtractor,
    LivsmedelDebiteringsExtractor,
    BygglovTimtaxaExtractor,
    Phase1ExtractorManager
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

class Phase1ExtractorTester:
    """Test Phase 1 extractors with sample Swedish municipal text"""
    
    def __init__(self):
        self.livsmedel_timtaxa_extractor = LivsmedelTimtaxaExtractor()
        self.livsmedel_debitering_extractor = LivsmedelDebiteringsExtractor()
        self.bygglov_timtaxa_extractor = BygglovTimtaxaExtractor()
        self.phase1_manager = Phase1ExtractorManager()
        
        # Test data with Swedish municipal text samples
        self.test_samples = [
            {
                'name': 'Stockholm Taxa Document',
                'text': """
                Taxa för livsmedelskontroll 2024
                
                Avgifter för offentlig kontroll enligt livsmedelslagen
                
                Timtaxa för livsmedelskontroll: 1350 kr per timme
                
                Debitering sker i förskott enligt kommunfullmäktiges beslut.
                
                Bygglovstaxa
                Plan- och bygglov handläggs enligt PBL.
                Timtaxa för handläggning av bygglov: 1200 kr per timme
                """,
                'expected': {
                    'timtaxa_livsmedel': 1350,
                    'debitering_livsmedel': 'förskott',
                    'timtaxa_bygglov': 1200
                }
            },
            {
                'name': 'Göteborg Avgifter',
                'text': """
                Avgifter för miljö- och hälsoskydd
                
                Livsmedelskontroll
                Avgift per nedlagd handläggningstimme för livsmedelskontroll: 1400 kr
                
                Debitering av avgifter sker i efterhand efter utförd kontroll.
                
                Byggnadsnämndens taxa
                Handläggning av bygglov debiteras med 1150 kr per timme.
                """,
                'expected': {
                    'timtaxa_livsmedel': 1400,
                    'debitering_livsmedel': 'efterhand',
                    'timtaxa_bygglov': 1150
                }
            },
            {
                'name': 'Malmö Styrdokument',
                'text': """
                Styrdokument - Taxor och avgifter
                
                Offentlig kontroll av livsmedelsverksamhet
                Timavgift för livsmedelstillsyn: 1275 kr/timme
                
                Avgiften för livsmedelskontroll faktureras i förskott.
                
                Plan- och bygglov enligt PBL
                Bygglovshandläggning: 1300 kr per timme
                """,
                'expected': {
                    'timtaxa_livsmedel': 1275,
                    'debitering_livsmedel': 'förskott',
                    'timtaxa_bygglov': 1300
                }
            },
            {
                'name': 'Uppsala Partial Data',
                'text': """
                Kommunala avgifter och taxor
                
                Miljö- och hälsoskydd
                Livsmedelskontroll utförs enligt livsmedelslagen.
                Kontrollavgift livsmedel: 1425 kr per timme
                
                Bygglov hanteras av byggnadsnämnden.
                """,
                'expected': {
                    'timtaxa_livsmedel': 1425,
                    'debitering_livsmedel': None,
                    'timtaxa_bygglov': None
                }
            },
            {
                'name': 'Västerås Billing Only',
                'text': """
                Information om avgifter
                
                Livsmedelskontroll
                Avgifter för livsmedelskontroll debiteras i efterhand 
                efter genomförd inspektion.
                
                Bygglov och andra tillstånd hanteras enligt gällande taxa.
                """,
                'expected': {
                    'timtaxa_livsmedel': None,
                    'debitering_livsmedel': 'efterhand',
                    'timtaxa_bygglov': None
                }
            }
        ]
    
    def test_individual_extractors(self):
        """Test each extractor individually"""
        logger.info("=== Testing Individual Phase 1 Extractors ===")
        
        results = {
            'livsmedel_timtaxa': {'passed': 0, 'failed': 0},
            'livsmedel_debitering': {'passed': 0, 'failed': 0},
            'bygglov_timtaxa': {'passed': 0, 'failed': 0}
        }
        
        for sample in self.test_samples:
            logger.info(f"\nTesting sample: {sample['name']}")
            
            # Test food control hourly rate extractor
            livsmedel_result = self.livsmedel_timtaxa_extractor.extract(sample['text'])
            expected_livsmedel = sample['expected']['timtaxa_livsmedel']
            
            if expected_livsmedel:
                if livsmedel_result and livsmedel_result.get('timtaxa_livsmedel') == expected_livsmedel:
                    logger.info(f"✓ Food control hourly rate: {livsmedel_result['timtaxa_livsmedel']} kr")
                    results['livsmedel_timtaxa']['passed'] += 1
                else:
                    logger.error(f"✗ Food control hourly rate: expected {expected_livsmedel}, got {livsmedel_result}")
                    results['livsmedel_timtaxa']['failed'] += 1
            else:
                if not livsmedel_result:
                    logger.info("✓ Food control hourly rate: correctly found none")
                    results['livsmedel_timtaxa']['passed'] += 1
                else:
                    logger.warning(f"? Food control hourly rate: unexpected result {livsmedel_result}")
            
            # Test billing model extractor
            debitering_result = self.livsmedel_debitering_extractor.extract(sample['text'])
            expected_debitering = sample['expected']['debitering_livsmedel']
            
            if expected_debitering:
                if debitering_result and debitering_result.get('debitering_livsmedel') == expected_debitering:
                    logger.info(f"✓ Billing model: {debitering_result['debitering_livsmedel']}")
                    results['livsmedel_debitering']['passed'] += 1
                else:
                    logger.error(f"✗ Billing model: expected {expected_debitering}, got {debitering_result}")
                    results['livsmedel_debitering']['failed'] += 1
            else:
                if not debitering_result:
                    logger.info("✓ Billing model: correctly found none")
                    results['livsmedel_debitering']['passed'] += 1
                else:
                    logger.warning(f"? Billing model: unexpected result {debitering_result}")
            
            # Test building permit hourly rate extractor
            bygglov_result = self.bygglov_timtaxa_extractor.extract(sample['text'])
            expected_bygglov = sample['expected']['timtaxa_bygglov']
            
            if expected_bygglov:
                if bygglov_result and bygglov_result.get('timtaxa_bygglov') == expected_bygglov:
                    logger.info(f"✓ Building permit hourly rate: {bygglov_result['timtaxa_bygglov']} kr")
                    results['bygglov_timtaxa']['passed'] += 1
                else:
                    logger.error(f"✗ Building permit hourly rate: expected {expected_bygglov}, got {bygglov_result}")
                    results['bygglov_timtaxa']['failed'] += 1
            else:
                if not bygglov_result:
                    logger.info("✓ Building permit hourly rate: correctly found none")
                    results['bygglov_timtaxa']['passed'] += 1
                else:
                    logger.warning(f"? Building permit hourly rate: unexpected result {bygglov_result}")
        
        return results
    
    def test_combined_extractor(self):
        """Test the combined Phase 1 extractor manager"""
        logger.info("\n=== Testing Combined Phase 1 Extractor ===")
        
        results = {'passed': 0, 'failed': 0}
        
        for sample in self.test_samples:
            logger.info(f"\nTesting combined extraction: {sample['name']}")
            
            # Extract all Phase 1 data
            combined_result = self.phase1_manager.extract_all_phase1_data(sample['text'])
            
            # Check results
            expected = sample['expected']
            success = True
            
            for field, expected_value in expected.items():
                actual_value = combined_result.get(field)
                
                if expected_value is not None:
                    if actual_value == expected_value:
                        logger.info(f"✓ {field}: {actual_value}")
                    else:
                        logger.error(f"✗ {field}: expected {expected_value}, got {actual_value}")
                        success = False
                else:
                    if actual_value is None:
                        logger.info(f"✓ {field}: correctly found none")
                    else:
                        logger.warning(f"? {field}: unexpected value {actual_value}")
            
            # Check metadata
            confidence = combined_result.get('confidence', 0)
            completeness = combined_result.get('data_completeness', 0)
            
            logger.info(f"Confidence: {confidence:.2f}, Completeness: {completeness:.1%}")
            
            if success:
                results['passed'] += 1
            else:
                results['failed'] += 1
        
        return results
    
    def test_edge_cases(self):
        """Test edge cases and error conditions"""
        logger.info("\n=== Testing Edge Cases ===")
        
        edge_cases = [
            {
                'name': 'Empty text',
                'text': '',
                'should_find': False
            },
            {
                'name': 'Invalid amounts',
                'text': 'Livsmedelskontroll kostar 50000 kr per timme och bygglov 10 kr per timme',
                'should_find': False  # Amounts outside valid range
            },
            {
                'name': 'Mixed languages',
                'text': 'Food control fee is 1350 SEK per hour. Livsmedelskontroll 1350 kr/timme.',
                'should_find': True  # Should find Swedish part
            },
            {
                'name': 'Multiple amounts',
                'text': 'Livsmedelskontroll: 1200 kr/timme för små företag, 1400 kr/timme för stora företag',
                'should_find': True  # Should find first valid amount
            }
        ]
        
        results = {'passed': 0, 'failed': 0}
        
        for case in edge_cases:
            logger.info(f"\nTesting edge case: {case['name']}")
            
            result = self.phase1_manager.extract_all_phase1_data(case['text'])
            has_data = any(result.get(field) for field in ['timtaxa_livsmedel', 'debitering_livsmedel', 'timtaxa_bygglov'])
            
            if case['should_find'] == has_data:
                logger.info(f"✓ Edge case handled correctly")
                results['passed'] += 1
            else:
                logger.error(f"✗ Edge case failed: expected to find data: {case['should_find']}, actually found: {has_data}")
                results['failed'] += 1
        
        return results
    
    def run_all_tests(self):
        """Run all Phase 1 extractor tests"""
        logger.info("Starting Phase 1 Extractor Tests")
        
        # Test individual extractors
        individual_results = self.test_individual_extractors()
        
        # Test combined extractor
        combined_results = self.test_combined_extractor()
        
        # Test edge cases
        edge_results = self.test_edge_cases()
        
        # Summary
        logger.info("\n" + "="*60)
        logger.info("PHASE 1 EXTRACTOR TEST SUMMARY")
        logger.info("="*60)
        
        logger.info("Individual Extractors:")
        for extractor, results in individual_results.items():
            total = results['passed'] + results['failed']
            if total > 0:
                success_rate = (results['passed'] / total) * 100
                logger.info(f"  {extractor}: {results['passed']}/{total} ({success_rate:.1f}%)")
        
        logger.info("Combined Extractor:")
        total_combined = combined_results['passed'] + combined_results['failed']
        if total_combined > 0:
            success_rate = (combined_results['passed'] / total_combined) * 100
            logger.info(f"  Combined: {combined_results['passed']}/{total_combined} ({success_rate:.1f}%)")
        
        logger.info("Edge Cases:")
        total_edge = edge_results['passed'] + edge_results['failed']
        if total_edge > 0:
            success_rate = (edge_results['passed'] / total_edge) * 100
            logger.info(f"  Edge cases: {edge_results['passed']}/{total_edge} ({success_rate:.1f}%)")
        
        # Overall success
        total_tests = sum(r['passed'] + r['failed'] for r in individual_results.values())
        total_tests += combined_results['passed'] + combined_results['failed']
        total_tests += edge_results['passed'] + edge_results['failed']
        
        total_passed = sum(r['passed'] for r in individual_results.values())
        total_passed += combined_results['passed'] + edge_results['passed']
        
        if total_tests > 0:
            overall_success = (total_passed / total_tests) * 100
            logger.info(f"\nOverall Success Rate: {total_passed}/{total_tests} ({overall_success:.1f}%)")
            
            if overall_success >= 80:
                logger.info("🎉 Phase 1 extractors are working well!")
                return 0
            else:
                logger.warning("⚠️ Phase 1 extractors need improvement")
                return 1
        else:
            logger.error("❌ No tests were run")
            return 1

def main():
    """Main test function"""
    tester = Phase1ExtractorTester()
    return tester.run_all_tests()

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code) 