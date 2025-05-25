#!/usr/bin/env python3
"""
Simplified test script for enhanced pipeline components
Tests core logic without requiring Scrapy installation
"""

import logging
import sys
import os
import tempfile
import json
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Mock DropItem exception
class DropItem(Exception):
    pass

class MockSpider:
    """Mock spider for pipeline testing"""
    
    def __init__(self):
        self.name = 'test_spider'
        self.logger = logger

def test_enhanced_validation_logic():
    """Test enhanced validation pipeline logic"""
    logger.info("--- Testing Enhanced Validation Logic ---")
    
    # Import here to avoid Scrapy dependency issues
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Mock the validators
    class MockValidators:
        def validate_fee_amount(self, amount):
            return 50 <= amount <= 100000
        
        def validate_organization_number(self, org_nr):
            return len(str(org_nr)) >= 10
    
    # Test validation rules
    validation_rules = {
        'required_fields': {
            'weight': 1.0,
            'fields': ['fee_name', 'amount', 'currency', 'source_url']
        },
        'amount_validation': {
            'weight': 0.9,
            'min_amount': 50,
            'max_amount': 100000
        },
        'fee_name_validation': {
            'weight': 0.8,
            'min_length': 3,
            'max_length': 500
        }
    }
    
    test_items = [
        # Valid item
        {
            'fee_name': 'Bygglov för enbostadshus',
            'amount': 15000,
            'currency': 'SEK',
            'source_url': 'https://stockholm.se/avgifter.pdf'
        },
        # Invalid item - missing fields
        {
            'fee_name': 'Test',
            'amount': 1000
            # Missing currency and source_url
        },
        # Invalid item - amount too high
        {
            'fee_name': 'Expensive fee',
            'amount': 1000000,
            'currency': 'SEK',
            'source_url': 'https://test.se'
        }
    ]
    
    validators = MockValidators()
    valid_count = 0
    invalid_count = 0
    
    for item in test_items:
        # Test required fields
        required_fields = validation_rules['required_fields']['fields']
        has_required = all(item.get(field) for field in required_fields)
        
        # Test amount validation
        amount_valid = validators.validate_fee_amount(item.get('amount', 0))
        
        # Test fee name length
        fee_name = item.get('fee_name', '')
        name_valid = (validation_rules['fee_name_validation']['min_length'] <= 
                     len(fee_name) <= validation_rules['fee_name_validation']['max_length'])
        
        is_valid = has_required and amount_valid and name_valid
        
        if is_valid:
            valid_count += 1
            logger.info(f"✓ Valid: {fee_name}")
        else:
            invalid_count += 1
            reasons = []
            if not has_required:
                reasons.append("missing required fields")
            if not amount_valid:
                reasons.append("invalid amount")
            if not name_valid:
                reasons.append("invalid name length")
            logger.info(f"✗ Invalid: {fee_name} - {', '.join(reasons)}")
    
    logger.info(f"Validation results: {valid_count} valid, {invalid_count} invalid")
    return valid_count > 0 and invalid_count > 0  # Should have both valid and invalid

def test_duplicate_detection_logic():
    """Test duplicate detection logic"""
    logger.info("--- Testing Duplicate Detection Logic ---")
    
    import hashlib
    import re
    
    def normalize_text(text):
        if not text:
            return ""
        # More aggressive normalization for duplicate detection
        text = str(text).lower().strip()
        # Remove common Swedish words and prepositions
        text = re.sub(r'\b(för|av|till|med|och|eller|i|på|vid|från)\b', '', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def create_fingerprint(item):
        municipality = normalize_text(item.get('municipality', ''))
        fee_name = normalize_text(item.get('fee_name', ''))
        amount = str(int(item.get('amount', 0)))
        
        fingerprint_str = f"{municipality}|{fee_name}|{amount}"
        return hashlib.md5(fingerprint_str.encode()).hexdigest()
    
    def calculate_similarity(text1, text2):
        """Simple similarity calculation"""
        if not text1 or not text2:
            return 0.0
        
        # Normalize both texts
        norm1 = normalize_text(text1)
        norm2 = normalize_text(text2)
        
        if norm1 == norm2:
            return 1.0
        
        # Check if one is contained in the other
        if norm1 in norm2 or norm2 in norm1:
            return 0.8
        
        # Simple word overlap
        words1 = set(norm1.split())
        words2 = set(norm2.split())
        
        if not words1 or not words2:
            return 0.0
        
        overlap = len(words1.intersection(words2))
        total = len(words1.union(words2))
        
        return overlap / total if total > 0 else 0.0
    
    def calculate_quality_score(item):
        score = 0.5  # Base score
        
        # Confidence boost
        confidence = item.get('confidence', 0.5)
        score += confidence * 0.3
        
        # Completeness boost
        important_fields = ['fee_name', 'amount', 'currency', 'category', 'description']
        present_fields = sum(1 for field in important_fields if item.get(field))
        completeness = present_fields / len(important_fields)
        score += completeness * 0.2
        
        return min(score, 1.0)
    
    test_items = [
        {
            'municipality': 'Stockholm',
            'fee_name': 'Bygglov för enbostadshus',
            'amount': 15000,
            'currency': 'SEK',
            'confidence': 0.9,
            'category': 'bygglov',
            'description': 'Detailed description'
        },
        {
            'municipality': 'Stockholm',
            'fee_name': 'Bygglov enbostadshus',  # Similar name (should be detected as duplicate)
            'amount': 15000,
            'currency': 'SEK',
            'confidence': 0.7,  # Lower confidence
            'category': 'bygglov'
        },
        {
            'municipality': 'Göteborg',
            'fee_name': 'Miljötillstånd',
            'amount': 8500,
            'currency': 'SEK',
            'confidence': 0.8
        }
    ]
    
    seen_items = []
    duplicates_found = 0
    unique_items = 0
    
    for item in test_items:
        is_duplicate = False
        best_match_idx = -1
        best_similarity = 0.0
        
        # Check against existing items
        for i, existing_item in enumerate(seen_items):
            # Must be same municipality and similar amount
            if (existing_item['municipality'] == item['municipality'] and
                abs(existing_item['amount'] - item['amount']) <= 100):
                
                # Check fee name similarity
                similarity = calculate_similarity(
                    existing_item['fee_name'], 
                    item['fee_name']
                )
                
                if similarity > 0.7:  # Threshold for duplicate detection
                    is_duplicate = True
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match_idx = i
        
        if is_duplicate:
            duplicates_found += 1
            existing_item = seen_items[best_match_idx]
            
            # Compare quality
            existing_quality = calculate_quality_score(existing_item)
            new_quality = calculate_quality_score(item)
            
            if new_quality > existing_quality:
                seen_items[best_match_idx] = item
                logger.info(f"✓ Replaced duplicate with higher quality: {item.get('fee_name')} "
                           f"(similarity: {best_similarity:.2f})")
            else:
                logger.info(f"✗ Dropped duplicate: {item.get('fee_name')} "
                           f"(similarity: {best_similarity:.2f})")
        else:
            seen_items.append(item)
            unique_items += 1
            logger.info(f"✓ Added unique item: {item.get('fee_name')}")
    
    logger.info(f"Duplicate detection: {unique_items} unique, {duplicates_found} duplicates")
    return duplicates_found > 0  # Should find at least one duplicate

def test_data_export_logic():
    """Test data export logic"""
    logger.info("--- Testing Data Export Logic ---")
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Test CSV writing
        import csv
        from collections import defaultdict, Counter
        
        test_items = [
            {
                'municipality': 'Stockholm',
                'fee_name': 'Bygglov för enbostadshus',
                'amount': 15000,
                'currency': 'SEK',
                'category': 'bygglov',
                'source_type': 'PDF',
                'confidence': 0.9
            },
            {
                'municipality': 'Göteborg',
                'fee_name': 'Miljötillstånd',
                'amount': 8500,
                'currency': 'SEK',
                'category': 'miljö',
                'source_type': 'HTML',
                'confidence': 0.8
            }
        ]
        
        # Test CSV export
        csv_path = Path(temp_dir) / 'test_fees.csv'
        fieldnames = ['municipality', 'fee_name', 'amount', 'currency', 'category', 'source_type', 'confidence']
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for item in test_items:
                # Ensure all fields are present
                row = {field: item.get(field, '') for field in fieldnames}
                writer.writerow(row)
        
        # Verify CSV was created and has content
        with open(csv_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.strip().split('\n')
            
        logger.info(f"✓ CSV created with {len(lines)} lines (including header)")
        
        # Test statistics generation
        stats = {
            'total_fees': len(test_items),
            'municipalities': set(item['municipality'] for item in test_items),
            'categories': Counter(item['category'] for item in test_items),
            'source_types': Counter(item['source_type'] for item in test_items)
        }
        
        # Convert sets to lists for JSON serialization
        stats['municipalities'] = list(stats['municipalities'])
        stats['categories'] = dict(stats['categories'])
        stats['source_types'] = dict(stats['source_types'])
        
        # Test JSON export
        stats_path = Path(temp_dir) / 'test_stats.json'
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        # Verify JSON was created
        with open(stats_path, 'r', encoding='utf-8') as f:
            loaded_stats = json.load(f)
        
        logger.info(f"✓ Statistics JSON created: {loaded_stats['total_fees']} fees, "
                   f"{len(loaded_stats['municipalities'])} municipalities")
        
        return True
        
    except Exception as e:
        logger.error(f"Data export test failed: {e}")
        return False
    
    finally:
        # Cleanup
        import shutil
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

def test_pipeline_integration():
    """Test pipeline integration logic"""
    logger.info("--- Testing Pipeline Integration ---")
    
    # Simulate pipeline chain
    test_items = [
        {
            'municipality': 'Stockholm',
            'fee_name': 'Bygglov för enbostadshus',
            'amount': 15000,
            'currency': 'SEK',
            'source_url': 'https://stockholm.se/avgifter.pdf',
            'confidence': 0.9
        },
        {
            'municipality': 'Stockholm',
            'fee_name': 'Bygglov enbostadshus',  # Duplicate
            'amount': 15000,
            'currency': 'SEK',
            'source_url': 'https://stockholm.se/bygglov',
            'confidence': 0.7
        },
        {
            'municipality': 'Test',
            'fee_name': 'Bad',  # Invalid
            'amount': 1000000,
            'currency': 'USD'
        }
    ]
    
    # Step 1: Validation
    validated_items = []
    for item in test_items:
        # Simple validation
        has_required = all(item.get(field) for field in ['fee_name', 'amount', 'currency'])
        amount_valid = 50 <= item.get('amount', 0) <= 100000
        currency_valid = item.get('currency') == 'SEK'
        
        if has_required and amount_valid and currency_valid:
            validated_items.append(item)
            logger.info(f"✓ Validated: {item.get('fee_name')}")
        else:
            logger.info(f"✗ Rejected: {item.get('fee_name')}")
    
    # Step 2: Duplicate detection
    import hashlib
    seen = {}
    unique_items = []
    
    for item in validated_items:
        key = f"{item['municipality']}|{item['fee_name']}|{item['amount']}"
        fingerprint = hashlib.md5(key.encode()).hexdigest()
        
        if fingerprint not in seen:
            seen[fingerprint] = item
            unique_items.append(item)
            logger.info(f"✓ Added unique: {item.get('fee_name')}")
        else:
            # Keep higher confidence
            if item.get('confidence', 0) > seen[fingerprint].get('confidence', 0):
                seen[fingerprint] = item
                # Replace in unique_items
                for i, existing in enumerate(unique_items):
                    if existing is seen[fingerprint]:
                        unique_items[i] = item
                        break
                logger.info(f"✓ Replaced with higher quality: {item.get('fee_name')}")
            else:
                logger.info(f"✗ Dropped duplicate: {item.get('fee_name')}")
    
    # Step 3: Data export (simulated)
    exported_count = len(unique_items)
    logger.info(f"✓ Exported {exported_count} items")
    
    logger.info(f"Pipeline integration: {len(test_items)} input → {exported_count} output")
    
    return exported_count > 0 and exported_count < len(test_items)

def main():
    """Main test function"""
    logger.info("Starting Enhanced Pipeline Component Tests (Simplified)")
    logger.info(f"Test started at: {datetime.now().isoformat()}")
    
    tests = [
        ("Validation Logic", test_enhanced_validation_logic),
        ("Duplicate Detection Logic", test_duplicate_detection_logic),
        ("Data Export Logic", test_data_export_logic),
        ("Pipeline Integration", test_pipeline_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            status = "PASS" if result else "FAIL"
            logger.info(f"{test_name}: {status}")
        except Exception as e:
            logger.error(f"{test_name}: FAIL - {e}")
            results.append((test_name, False))
    
    # Final summary
    logger.info("\n" + "="*60)
    logger.info("FINAL TEST SUMMARY")
    logger.info("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    logger.info(f"Tests passed: {passed}/{total}")
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"  {status}: {test_name}")
    
    if passed == total:
        logger.info("🎉 All pipeline logic tests PASSED!")
        return 0
    else:
        logger.error("❌ Some pipeline logic tests FAILED!")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code) 