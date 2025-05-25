#!/usr/bin/env python3
"""
Debug Kramfors PDF extraction to understand the text structure
"""

import sys
import os
import requests
import tempfile
from pathlib import Path
import re

# Add project root to path
project_root = Path(__file__).parent / "swedish_municipal_crawler"
sys.path.insert(0, str(project_root))

def debug_kramfors_text():
    """Debug the Kramfors PDF text to understand the structure"""
    
    pdf_url = "https://www.kramfors.se/download/18.5d3eebb5193deb3662031eef/1735302616646/Livsmedelstaxa%202025.pdf"
    
    try:
        # Download PDF
        response = requests.get(pdf_url, timeout=30)
        response.raise_for_status()
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(response.content)
            temp_pdf_path = temp_file.name
        
        # Extract text
        import pdfplumber
        with pdfplumber.open(temp_pdf_path) as pdf:
            text_content = ""
            for page in pdf.pages:
                text_content += page.extract_text() or ""
        
        print("=== FULL KRAMFORS PDF TEXT ===")
        print(text_content)
        print("\n=== END TEXT ===")
        
        # Look for the 222 kr pattern specifically
        print("\n=== SEARCHING FOR 222 KR CONTEXT ===")
        lines = text_content.split('\n')
        for i, line in enumerate(lines):
            if '222' in line:
                print(f"Line {i}: {line}")
                # Show context (previous and next lines)
                if i > 0:
                    print(f"  Previous: {lines[i-1]}")
                if i < len(lines) - 1:
                    print(f"  Next: {lines[i+1]}")
                print()
        
        # Test specific patterns
        print("=== TESTING SPECIFIC PATTERNS ===")
        patterns = [
            r'avgift.*?per.*?timme.*?(\d{3,4})\s*kr',
            r'(\d{3,4})\s*kr.*?per.*?timme',
            r'handläggning.*?(\d{3,4})\s*kr.*?timme',
            r'timavgift.*?(\d{3,4})\s*kr',
            r'avgift.*?(\d{3,4})\s*kr.*?timme',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE | re.DOTALL)
            if matches:
                print(f"Pattern: {pattern}")
                print(f"Matches: {matches}")
                
                # Show context for each match
                for match in re.finditer(pattern, text_content, re.IGNORECASE | re.DOTALL):
                    start = max(0, match.start() - 100)
                    end = min(len(text_content), match.end() + 100)
                    context = text_content[start:end]
                    print(f"Context: ...{context}...")
                print()
        
        # Clean up
        os.unlink(temp_pdf_path)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_kramfors_text() 