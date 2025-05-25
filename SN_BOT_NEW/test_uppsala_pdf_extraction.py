#!/usr/bin/env python3
"""
Test PDF extraction with Uppsala municipality document
Tests extraction of Phase 1 data from Swedish municipal tax PDFs
"""

import sys
import os
import requests
import tempfile
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent / "swedish_municipal_crawler"
sys.path.insert(0, str(project_root))

from crawler.extractors.phase1_extractors import Phase1ExtractorManager
from crawler.extractors.phase1_pdf_extractor import Phase1PDFExtractor

def test_uppsala_pdf_extraction():
    """Test extraction from Uppsala municipality PDF"""
    
    # Uppsala municipality PDF URL
    pdf_url = "https://www.uppsala.se/contentassets/a4ca833c530b4986b6a4874891c8a106/taxa-for-offentlig-kontroll-enligt-livsmedels--och-foderlagstiftningen.pdf"
    
    print("=== Testing Uppsala Municipality PDF Extraction ===")
    print(f"PDF URL: {pdf_url}")
    print()
    
    try:
        # Download PDF
        print("📥 Downloading PDF...")
        response = requests.get(pdf_url, timeout=30)
        response.raise_for_status()
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(response.content)
            temp_pdf_path = temp_file.name
        
        print(f"✅ PDF downloaded: {len(response.content)} bytes")
        print()
        
        # Test PDF extractor
        print("🔍 Testing PDF extraction...")
        pdf_extractor = Phase1PDFExtractor()
        
        # Extract Phase 1 data directly from PDF
        results = pdf_extractor.extract_phase1_from_pdf(temp_pdf_path, pdf_url)
        
        print(f"📄 PDF processing completed")
        print()
        
        print("📊 Extraction Results:")
        print(f"  Municipality: Uppsala")
        print(f"  Source URL: {pdf_url}")
        print(f"  Data Completeness: {results.get('data_completeness', 0):.1%}")
        print(f"  Overall Confidence: {results.get('confidence', 0):.2f}")
        print(f"  Extraction Method: {results.get('extraction_method', 'unknown')}")
        print()
        
        # Show specific findings
        if results.get('timtaxa_livsmedel'):
            print(f"✅ Food Control Hourly Rate: {results['timtaxa_livsmedel']} kr/timme")
        else:
            print("❌ Food Control Hourly Rate: Not found")
            
        if results.get('debitering_livsmedel'):
            print(f"✅ Food Control Billing Model: {results['debitering_livsmedel']}")
        else:
            print("❌ Food Control Billing Model: Not found")
            
        if results.get('timtaxa_bygglov'):
            print(f"✅ Building Permit Hourly Rate: {results['timtaxa_bygglov']} kr/timme")
        else:
            print("❌ Building Permit Hourly Rate: Not found")
        
        # Show any warnings
        if results.get('validation_warnings'):
            print()
            print("⚠️  Warnings:")
            for warning in results['validation_warnings']:
                print(f"  - {warning}")
        
        print()
        
        # Clean up
        os.unlink(temp_pdf_path)
        
        return results
        
    except Exception as e:
        print(f"❌ Error during extraction: {e}")
        return None

if __name__ == "__main__":
    results = test_uppsala_pdf_extraction()
    
    if results and results.get('data_completeness', 0) > 0:
        print("🎉 SUCCESS: Found Phase 1 data in Uppsala PDF!")
    else:
        print("⚠️  No Phase 1 data found - may need pattern improvements") 