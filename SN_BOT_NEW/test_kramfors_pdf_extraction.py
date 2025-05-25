#!/usr/bin/env python3
"""
Test PDF extraction with Kramfors municipality document
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

def test_kramfors_pdf_extraction():
    """Test extraction from Kramfors municipality PDF"""
    
    # Kramfors municipality PDF URL
    pdf_url = "https://www.kramfors.se/download/18.5d3eebb5193deb3662031eef/1735302616646/Livsmedelstaxa%202025.pdf"
    
    print("=== Testing Kramfors Municipality PDF Extraction ===")
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
        
        # Initialize extractors
        pdf_extractor = Phase1PDFExtractor()
        phase1_manager = Phase1ExtractorManager()
        
        # Extract from PDF
        print("🔍 Extracting Phase 1 data from PDF...")
        pdf_results = pdf_extractor.extract_phase1_from_pdf(temp_pdf_path, pdf_url)
        
        print("📊 PDF Extraction Results:")
        print(f"  Timtaxa livsmedel: {pdf_results.get('timtaxa_livsmedel', 'Not found')}")
        print(f"  Debitering livsmedel: {pdf_results.get('debitering_livsmedel', 'Not found')}")
        print(f"  Timtaxa bygglov: {pdf_results.get('timtaxa_bygglov', 'Not found')}")
        print(f"  Confidence: {pdf_results.get('confidence', 0):.2f}")
        print(f"  Extraction method: {pdf_results.get('extraction_method', 'N/A')}")
        print()
        
        # Also try text extraction for comparison
        print("📝 Extracting text from PDF for manual inspection...")
        try:
            import pdfplumber
            with pdfplumber.open(temp_pdf_path) as pdf:
                text_content = ""
                for page in pdf.pages:
                    text_content += page.extract_text() or ""
                
                print(f"📄 Extracted text length: {len(text_content)} characters")
                
                # Show first 1000 characters for better analysis
                if text_content:
                    print("📖 First 1000 characters of extracted text:")
                    print("-" * 50)
                    print(text_content[:1000])
                    print("-" * 50)
                    print()
                    
                    # Test Phase 1 extraction on the text
                    print("🔍 Testing Phase 1 extraction on extracted text...")
                    text_results = phase1_manager.extract_all_phase1_data(text_content, pdf_url)
                    
                    print("📊 Text Extraction Results:")
                    print(f"  Timtaxa livsmedel: {text_results.get('timtaxa_livsmedel', 'Not found')}")
                    print(f"  Debitering livsmedel: {text_results.get('debitering_livsmedel', 'Not found')}")
                    print(f"  Timtaxa bygglov: {text_results.get('timtaxa_bygglov', 'Not found')}")
                    print(f"  Confidence: {text_results.get('confidence', 0):.2f}")
                    print(f"  Data completeness: {text_results.get('data_completeness', 0):.1%}")
                    print()
                    
                    # Look for specific Swedish keywords
                    print("🔍 Searching for Swedish keywords in text...")
                    keywords = [
                        'timtaxa', 'avgift', 'kronor', 'kr', 'timme',
                        'livsmedelskontroll', 'livsmedel', 'offentlig kontroll',
                        'bygglov', 'plan- och bygg', 'handläggning',
                        'förskott', 'efterhand', 'debitering', 'livsmedelstaxa'
                    ]
                    
                    found_keywords = []
                    text_lower = text_content.lower()
                    for keyword in keywords:
                        if keyword in text_lower:
                            found_keywords.append(keyword)
                    
                    print(f"✅ Found keywords: {', '.join(found_keywords)}")
                    
                    # Look for potential amounts
                    import re
                    amounts = re.findall(r'\d{3,4}\s*kr', text_content, re.IGNORECASE)
                    if amounts:
                        print(f"💰 Found potential amounts: {', '.join(set(amounts))}")
                    
                    # Look for specific patterns that might indicate our data
                    print("\n🔍 Looking for specific Phase 1 patterns...")
                    
                    # Check for food control patterns
                    food_patterns = [
                        r'livsmedelskontroll.*?(\d{3,4})\s*kr',
                        r'timtaxa.*?livsmedel.*?(\d{3,4})',
                        r'(\d{3,4})\s*kr.*?timme.*?livsmedel',
                        r'avgift.*?per.*?timme.*?(\d{3,4})',
                        r'handläggning.*?(\d{3,4})\s*kr'
                    ]
                    
                    for pattern in food_patterns:
                        matches = re.findall(pattern, text_content, re.IGNORECASE | re.DOTALL)
                        if matches:
                            print(f"  🎯 Food control pattern found: {pattern} -> {matches}")
                    
                    # Check for billing model patterns
                    billing_patterns = [
                        r'förskott',
                        r'efterhand',
                        r'debitering',
                        r'fakturering'
                    ]
                    
                    for pattern in billing_patterns:
                        if re.search(pattern, text_content, re.IGNORECASE):
                            print(f"  💳 Billing pattern found: {pattern}")
                    
                else:
                    print("❌ No text could be extracted from PDF")
                    
        except Exception as e:
            print(f"❌ Text extraction failed: {e}")
        
        # Clean up
        os.unlink(temp_pdf_path)
        
        # Summary
        print("\n=== Summary ===")
        has_pdf_data = any(pdf_results.get(field) for field in ['timtaxa_livsmedel', 'debitering_livsmedel', 'timtaxa_bygglov'])
        has_text_data = any(text_results.get(field) for field in ['timtaxa_livsmedel', 'debitering_livsmedel', 'timtaxa_bygglov']) if 'text_results' in locals() else False
        
        if has_pdf_data or has_text_data:
            print("✅ SUCCESS: Found Phase 1 data in Kramfors municipality PDF!")
            return True
        else:
            print("❌ FAILED: No Phase 1 data found - may need pattern enhancement")
            print("   This could indicate the document uses different terminology")
            print("   or the data is structured differently than our current patterns expect")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Kramfors PDF extraction: {e}")
        return False

if __name__ == "__main__":
    success = test_kramfors_pdf_extraction()
    sys.exit(0 if success else 1) 