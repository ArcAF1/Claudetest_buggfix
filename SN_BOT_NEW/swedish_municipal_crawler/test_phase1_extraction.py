#!/usr/bin/env python3
"""
Test Phase 1 Extraction
Quick test to verify Phase 1 extractors work with sample Swedish municipal text
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from crawler.extractors.phase1_extractors import Phase1ExtractorManager

def test_phase1_extraction():
    """Test Phase 1 extraction with sample Swedish text"""
    
    # Sample Swedish municipal text with Phase 1 data
    sample_texts = [
        # Text with food control hourly rate
        """
        Livsmedelskontroll och tillsyn
        
        Kommunen utför livsmedelskontroll enligt livsmedelslagen. 
        Timtaxan för livsmedelskontroll är 1 250 kr per timme.
        Debiteringsmodell: Förskottsbetalning krävs för alla kontroller.
        
        Kontakt: Miljö- och hälsoskyddskontoret
        """,
        
        # Text with building permit rates
        """
        Bygglov och planärenden
        
        Handläggning av bygglovsärenden:
        - Timtaxa för handläggning: 1 150 kr/timme
        - Startavgift: 5 000 kr
        - Slutbesked: 2 500 kr
        
        Plan- och byggkontoret
        """,
        
        # Text with billing model
        """
        Avgifter och betalning
        
        Livsmedelskontroll:
        - Timkostnad: 1 300 kr
        - Betalning: Efterhand enligt faktura
        - Moms tillkommer ej (kommunal verksamhet)
        """,
        
        # Complete text with all three data points
        """
        Taxa för miljö- och hälsoskydd 2024
        
        Livsmedelskontroll:
        - Timtaxa: 1 200 kr per timme
        - Debiteringsmodell: Förskottsbetalning
        - Minimiavgift: 2 400 kr
        
        Bygglov:
        - Handläggningstimme: 1 100 kr
        - Expeditionsavgift: 1 500 kr
        
        Gäller från 2024-01-01
        """
    ]
    
    extractor = Phase1ExtractorManager()
    
    print("=== Phase 1 Extraction Test ===")
    print()
    
    total_tests = len(sample_texts)
    successful_extractions = 0
    
    for i, text in enumerate(sample_texts, 1):
        print(f"Test {i}/{total_tests}:")
        print("-" * 40)
        
        # Extract Phase 1 data
        result = extractor.extract_all_phase1_data(text, f"test_url_{i}")
        
        # Show results
        print(f"Timtaxa livsmedel: {result.get('timtaxa_livsmedel', 'Not found')}")
        print(f"Debitering livsmedel: {result.get('debitering_livsmedel', 'Not found')}")
        print(f"Timtaxa bygglov: {result.get('timtaxa_bygglov', 'Not found')}")
        print(f"Confidence: {result.get('confidence', 0):.2f}")
        print(f"Data completeness: {result.get('data_completeness', 0):.1%}")
        
        # Check if any data was found
        has_data = any(result.get(field) for field in ['timtaxa_livsmedel', 'debitering_livsmedel', 'timtaxa_bygglov'])
        if has_data:
            successful_extractions += 1
            print("✅ SUCCESS: Found Phase 1 data")
        else:
            print("❌ FAILED: No Phase 1 data found")
        
        print()
    
    print("=== Test Summary ===")
    print(f"Total tests: {total_tests}")
    print(f"Successful extractions: {successful_extractions}")
    print(f"Success rate: {successful_extractions/total_tests*100:.1f}%")
    
    if successful_extractions > 0:
        print("✅ Phase 1 extractors are working!")
        return True
    else:
        print("❌ Phase 1 extractors are not working properly!")
        return False

if __name__ == '__main__':
    success = test_phase1_extraction()
    sys.exit(0 if success else 1) 