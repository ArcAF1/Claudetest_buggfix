#!/usr/bin/env python3
"""
Test the enhanced crawler with verified URL patterns on Ale and Alingsås municipalities
This tests the municipality-specific strategic URL patterns and enhanced discovery
"""

import sys
import os
import tempfile
import csv
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent / "swedish_municipal_crawler"
sys.path.insert(0, str(project_root))

def test_ale_alingsas_crawler():
    """Test enhanced crawler with verified patterns on Ale and Alingsås"""
    
    print("=== Testing Enhanced Crawler on Ale and Alingsås ===")
    print("🎯 Target: Verified URL patterns for specific municipalities")
    print("📄 Expected: Better discovery using municipality-specific paths")
    print()
    
    # Create test municipalities file with just Ale and Alingsås
    test_municipalities = [
        {
            'name': 'Ale',
            'url': 'https://ale.se',
            'org_number': '212000-1421'
        },
        {
            'name': 'Alingsås',
            'url': 'https://alingsas.se',
            'org_number': '212000-1439'
        }
    ]
    
    # Create temporary municipalities file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.DictWriter(f, fieldnames=['municipality_name', 'website_url', 'org_number'])
        writer.writeheader()
        for muni in test_municipalities:
            writer.writerow({
                'municipality_name': muni['name'],
                'website_url': muni['url'],
                'org_number': muni['org_number']
            })
        temp_file = f.name
    
    try:
        print(f"📁 Created test file: {temp_file}")
        print("🚀 Starting enhanced crawler test...")
        print()
        
        # Run the crawler with enhanced settings
        import subprocess
        cmd = [
            sys.executable, "run_phase1_crawler.py",
            "--municipalities-file", temp_file,
            "--max-municipalities", "2",
            "--log-level", "INFO"
        ]
        
        print(f"🔧 Running command: {' '.join(cmd)}")
        print("=" * 80)
        
        # Run with real-time output
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Track important events
        strategic_urls_found = []
        pdfs_found = []
        errors_found = []
        
        for line in iter(process.stdout.readline, ''):
            line = line.strip()
            if line:
                print(line)
                
                # Track strategic URL generation
                if "Generated strategic URL" in line or "Creating strategic requests" in line:
                    strategic_urls_found.append(line)
                
                # Track PDF discoveries
                if "Found relevant PDF" in line:
                    pdfs_found.append(line)
                
                # Track errors
                if "ERROR" in line or "404" in line:
                    errors_found.append(line)
        
        process.wait()
        
        print("=" * 80)
        print("🏁 Crawler test completed!")
        print()
        
        # Summary
        print("📊 Test Results Summary:")
        print(f"   Strategic URLs generated: {len(strategic_urls_found)}")
        print(f"   PDFs discovered: {len(pdfs_found)}")
        print(f"   Errors encountered: {len(errors_found)}")
        print()
        
        if strategic_urls_found:
            print("🎯 Strategic URLs Generated:")
            for url in strategic_urls_found[:5]:  # Show first 5
                print(f"   {url}")
            if len(strategic_urls_found) > 5:
                print(f"   ... and {len(strategic_urls_found) - 5} more")
            print()
        
        if pdfs_found:
            print("📄 PDFs Discovered:")
            for pdf in pdfs_found:
                print(f"   {pdf}")
            print()
        
        if errors_found:
            print("⚠️  Errors (sample):")
            for error in errors_found[:3]:  # Show first 3
                print(f"   {error}")
            if len(errors_found) > 3:
                print(f"   ... and {len(errors_found) - 3} more errors")
            print()
        
        # Check output files
        output_dir = project_root / "data" / "output"
        if output_dir.exists():
            csv_files = list(output_dir.glob("phase1_municipal_data_*.csv"))
            db_files = list(output_dir.glob("phase1_municipal_data_*.db"))
            
            if csv_files:
                latest_csv = max(csv_files, key=lambda x: x.stat().st_mtime)
                print(f"📁 Latest output file: {latest_csv.name}")
                
                # Check if we found any data
                try:
                    with open(latest_csv, 'r') as f:
                        lines = f.readlines()
                        if len(lines) > 1:  # More than just header
                            print(f"✅ Found {len(lines) - 1} data entries!")
                        else:
                            print("❌ No data entries found (empty results)")
                except Exception as e:
                    print(f"⚠️  Could not read output file: {e}")
        
        print()
        print("🔍 Analysis:")
        print("   - Check if municipality-specific URL patterns are being used")
        print("   - Verify that verified paths (like /om-kommunen/forfattningssamling.html) are accessed")
        print("   - Look for reduced 404 errors compared to generic patterns")
        print("   - Monitor PDF discovery from verified document repositories")
        
        return process.returncode == 0
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    finally:
        # Clean up
        try:
            os.unlink(temp_file)
        except:
            pass

if __name__ == "__main__":
    print("🧪 Enhanced Crawler Test for Ale and Alingsås")
    print("=" * 60)
    
    success = test_ale_alingsas_crawler()
    
    if success:
        print("✅ Test completed successfully!")
    else:
        print("❌ Test failed!")
    
    print("\n🎯 Next Steps:")
    print("   1. Review the strategic URL patterns being generated")
    print("   2. Check if verified paths are reducing 404 errors")
    print("   3. Monitor document discovery improvements")
    print("   4. Analyze any remaining issues with URL patterns") 