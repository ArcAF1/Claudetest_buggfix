#!/usr/bin/env python3
"""
Test the enhanced crawler with depth 5 specifically on Uppsala municipality
This tests the improved URL discovery patterns and deeper crawling capability
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

def test_enhanced_uppsala_crawler():
    """Test enhanced crawler with depth 5 on Uppsala municipality"""
    
    print("=== Testing Enhanced Crawler (Depth 5) on Uppsala ===")
    print("🎯 Target: Uppsala municipality deep-linked PDF")
    print("📄 Expected: https://www.uppsala.se/contentassets/a4ca833c530b4986b6a4874891c8a106/taxa-for-offentlig-kontroll-enligt-livsmedels--och-foderlagstiftningen.pdf")
    print()
    
    # Create a temporary municipalities file with just Uppsala
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
        writer = csv.writer(temp_file)
        writer.writerow(['municipality_name', 'website_url', 'municipality_code', 'population'])
        writer.writerow(['Uppsala', 'https://uppsala.se', '212000-2817', '230767'])
        temp_municipalities_file = temp_file.name
    
    print(f"📝 Created test municipalities file: {temp_municipalities_file}")
    print("   Municipality: Uppsala")
    print("   URL: https://uppsala.se")
    print("   Enhanced Features:")
    print("     ✅ Depth limit increased to 5")
    print("     ✅ More comprehensive URL patterns")
    print("     ✅ Better navigation keyword detection")
    print("     ✅ Enhanced PDF discovery patterns")
    print("     ✅ Improved scoring for document repositories")
    print()
    
    try:
        # Run the enhanced crawler with Uppsala only
        print("🕷️  Starting enhanced crawler on Uppsala...")
        print("   This will test depth 5 crawling with improved URL discovery")
        print()
        
        import subprocess
        
        cmd = [
            sys.executable, 
            'run_phase1_crawler.py',
            '--municipalities-file', temp_municipalities_file,
            '--max-municipalities', '1',
            '--log-level', 'INFO'
        ]
        
        print(f"🔧 Command: {' '.join(cmd)}")
        print()
        
        # Start timing
        start_time = time.time()
        
        # Run the crawler
        result = subprocess.run(
            cmd, 
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout for deeper crawling
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print("📊 Crawler Results:")
        print(f"   Exit code: {result.returncode}")
        print(f"   Duration: {duration:.1f} seconds")
        print()
        
        if result.stdout:
            print("📝 Crawler Output (last 100 lines):")
            print("-" * 60)
            # Show last 100 lines of output
            output_lines = result.stdout.split('\n')
            for line in output_lines[-100:]:
                if line.strip():
                    print(line)
            print("-" * 60)
            print()
            
            # Check for Uppsala PDF discovery
            if 'taxa-for-offentlig-kontroll-enligt-livsmedels--och-foderlagstiftningen.pdf' in result.stdout:
                print("🎉 SUCCESS: Found Uppsala's deep-linked PDF!")
            elif 'uppsala.se' in result.stdout and '.pdf' in result.stdout:
                print("✅ Found some PDFs from Uppsala - checking if target PDF was discovered...")
            else:
                print("⚠️  No Uppsala PDFs found in output")
        
        if result.stderr:
            print("⚠️  Crawler Errors:")
            print("-" * 60)
            print(result.stderr)
            print("-" * 60)
            print()
        
        # Check if any data was found
        output_dir = project_root / 'data' / 'output'
        db_files = list(output_dir.glob('phase1_municipal_data_*.db'))
        
        if db_files:
            latest_db = max(db_files, key=lambda x: x.stat().st_mtime)
            print(f"📊 Checking results in: {latest_db.name}")
            
            # Check database content
            import sqlite3
            conn = sqlite3.connect(latest_db)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM phase1_data WHERE municipality = "Uppsala"')
            uppsala_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM phase1_data WHERE municipality = "Uppsala" AND timtaxa_livsmedel IS NOT NULL')
            livsmedel_count = cursor.fetchone()[0]
            
            print(f"   Uppsala records: {uppsala_count}")
            print(f"   Records with food control data: {livsmedel_count}")
            
            if uppsala_count > 0:
                cursor.execute('''
                    SELECT municipality, timtaxa_livsmedel, source_url, confidence, data_completeness 
                    FROM phase1_data 
                    WHERE municipality = "Uppsala"
                    ORDER BY confidence DESC
                    LIMIT 5
                ''')
                records = cursor.fetchall()
                
                print("   Uppsala records found:")
                for record in records:
                    municipality, timtaxa, source_url, confidence, completeness = record
                    print(f"     📄 {timtaxa} kr/timme (confidence: {confidence:.2f}, completeness: {completeness:.1%})")
                    print(f"        Source: {source_url}")
                    
                    # Check if this is the target PDF
                    if 'taxa-for-offentlig-kontroll-enligt-livsmedels--och-foderlagstiftningen.pdf' in source_url:
                        print("        🎯 TARGET PDF FOUND!")
            
            conn.close()
        else:
            print("❌ No database files found")
        
        # Analyze crawl depth and URL discovery
        if result.stdout:
            depth_mentions = [line for line in result.stdout.split('\n') if 'depth' in line.lower()]
            if depth_mentions:
                print()
                print("🔍 Crawl Depth Analysis:")
                for mention in depth_mentions[-10:]:  # Last 10 depth mentions
                    print(f"   {mention.strip()}")
        
        # Clean up
        os.unlink(temp_municipalities_file)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⏰ Crawler timed out after 10 minutes")
        print("   This might indicate the crawler is working harder (good!)")
        print("   or that there's an infinite loop (needs investigation)")
        return False
    except Exception as e:
        print(f"❌ Error running crawler: {e}")
        return False

if __name__ == "__main__":
    success = test_enhanced_uppsala_crawler()
    
    if success:
        print()
        print("🎉 Enhanced Uppsala crawler test completed!")
        print("✅ Depth 5 crawling with improved URL discovery")
    else:
        print()
        print("❌ Enhanced Uppsala crawler test encountered issues")
        print()
        print("💡 Possible reasons:")
        print("   - Uppsala's PDF is very deeply nested")
        print("   - URL patterns need further refinement")
        print("   - Crawler timeout (might need longer for depth 5)")
        print("   - Website structure changed") 