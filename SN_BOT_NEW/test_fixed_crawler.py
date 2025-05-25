#!/usr/bin/env python3
"""
Test script to verify the fixed crawler works properly
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent / 'swedish_municipal_crawler'))

from crawler.extractors.phase1_extractors import Phase1ExtractorManager

def test_text_extraction():
    """Test that the extractors work with realistic municipal website text"""
    
    # Sample HTML-like text that might come from a municipal website
    sample_municipal_text = """
    Välkommen till Testkommun
    
    Avgifter och taxor
    
    Livsmedelskontroll
    Kommunen utför livsmedelskontroll enligt livsmedelslagen.
    Timtaxa för livsmedelskontroll: 1 350 kr per timme
    Avgiften debiteras i förskott.
    
    Bygglov och planärenden
    Plan- och byggkontoret handlägger bygglovsärenden.
    Handläggningstimme för bygglov: 1 200 kr/timme
    
    Kontakt
    För frågor kontakta kommunen på telefon 0123-456789
    """
    
    # Test with noisy HTML-like text (what the spider might extract)
    noisy_html_text = """
    <html><head><title>Testkommun</title></head><body>
    <nav>Meny Navigation Hem Om oss Kontakt</nav>
    <main>
    <h1>Avgifter och taxor</h1>
    <div class="content">
    <h2>Livsmedelskontroll</h2>
    <p>Kommunen utför livsmedelskontroll enligt livsmedelslagen.</p>
    <p>Timtaxa för livsmedelskontroll: 1 350 kr per timme</p>
    <p>Avgiften debiteras i förskott.</p>
    
    <h2>Bygglov och planärenden</h2>
    <p>Plan- och byggkontoret handlägger bygglovsärenden.</p>
    <p>Handläggningstimme för bygglov: 1 200 kr/timme</p>
    </div>
    </main>
    <footer>Copyright Testkommun</footer>
    </body></html>
    """
    
    # Clean the HTML text (simulate what the fixed spider does)
    import re
    clean_text = re.sub(r'<[^>]+>', ' ', noisy_html_text)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    print("=== Testing Fixed Text Extraction ===")
    print(f"Original HTML length: {len(noisy_html_text)} characters")
    print(f"Cleaned text length: {len(clean_text)} characters")
    print()
    print("Cleaned text sample:")
    print(clean_text[:300] + "..." if len(clean_text) > 300 else clean_text)
    print()
    
    # Test extraction
    extractor = Phase1ExtractorManager()
    
    print("=== Testing with Clean Municipal Text ===")
    result1 = extractor.extract_all_phase1_data(sample_municipal_text, "test_url_1")
    print(f"Timtaxa livsmedel: {result1.get('timtaxa_livsmedel', 'Not found')}")
    print(f"Debitering livsmedel: {result1.get('debitering_livsmedel', 'Not found')}")
    print(f"Timtaxa bygglov: {result1.get('timtaxa_bygglov', 'Not found')}")
    print(f"Confidence: {result1.get('confidence', 0):.2f}")
    print(f"Data completeness: {result1.get('data_completeness', 0):.1%}")
    print()
    
    print("=== Testing with Cleaned HTML Text ===")
    result2 = extractor.extract_all_phase1_data(clean_text, "test_url_2")
    print(f"Timtaxa livsmedel: {result2.get('timtaxa_livsmedel', 'Not found')}")
    print(f"Debitering livsmedel: {result2.get('debitering_livsmedel', 'Not found')}")
    print(f"Timtaxa bygglov: {result2.get('timtaxa_bygglov', 'Not found')}")
    print(f"Confidence: {result2.get('confidence', 0):.2f}")
    print(f"Data completeness: {result2.get('data_completeness', 0):.1%}")
    print()
    
    # Test with very noisy text (what might happen with bad extraction)
    very_noisy_text = """
    javascript:void(0) Navigation Menu Home About Contact
    Cookie Policy Privacy Policy
    Avgifter och taxor Click here for more info
    Livsmedelskontroll enligt livsmedelslagen
    Timtaxa för livsmedelskontroll: 1 350 kr per timme
    Avgiften debiteras i förskott
    Social Media Links Facebook Twitter Instagram
    Bygglov handläggs av plan- och byggkontoret
    Handläggningstimme för bygglov: 1 200 kr/timme
    Footer Copyright 2024 All rights reserved
    """
    
    print("=== Testing with Very Noisy Text ===")
    result3 = extractor.extract_all_phase1_data(very_noisy_text, "test_url_3")
    print(f"Timtaxa livsmedel: {result3.get('timtaxa_livsmedel', 'Not found')}")
    print(f"Debitering livsmedel: {result3.get('debitering_livsmedel', 'Not found')}")
    print(f"Timtaxa bygglov: {result3.get('timtaxa_bygglov', 'Not found')}")
    print(f"Confidence: {result3.get('confidence', 0):.2f}")
    print(f"Data completeness: {result3.get('data_completeness', 0):.1%}")
    print()
    
    # Summary
    total_tests = 3
    successful_tests = sum(1 for result in [result1, result2, result3] 
                          if any(result.get(field) for field in ['timtaxa_livsmedel', 'debitering_livsmedel', 'timtaxa_bygglov']))
    
    print("=== Test Summary ===")
    print(f"Total tests: {total_tests}")
    print(f"Successful extractions: {successful_tests}")
    print(f"Success rate: {successful_tests/total_tests*100:.1f}%")
    
    if successful_tests >= 2:
        print("✅ Fixed text extraction is working!")
        return True
    else:
        print("❌ Text extraction still has issues!")
        return False

if __name__ == "__main__":
    test_text_extraction() 