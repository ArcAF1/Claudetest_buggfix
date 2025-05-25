#!/usr/bin/env python3
"""
Test the enhanced crawler specifically on Uppsala municipality
"""

import sys
import os
import tempfile
import csv
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent / "swedish_municipal_crawler"
sys.path.insert(0, str(project_root))

def test_uppsala_crawler():
    """Test crawler specifically on Uppsala municipality"""
    
    print("=== Testing Enhanced Crawler on Uppsala ===")
    print()
    
    # Create a temporary municipalities file with just Uppsala
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
        writer = csv.writer(temp_file)
        writer.writerow(['municipality', 'url', 'org_number', 'population'])
        writer.writerow(['Uppsala', 'https://uppsala.se', '212000-2817', '230767'])
        temp_municipalities_file = temp_file.name
    
    print(f"📝 Created test municipalities file: {temp_municipalities_file}")
    print("   Municipality: Uppsala")
    print("   URL: https://uppsala.se")
    print()
    
    try:
        # Run the crawler with Uppsala only
        print("🕷️  Starting enhanced crawler on Uppsala...")
        print("   This will test the improved PDF discovery patterns")
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
        
        # Run the crawler
        result = subprocess.run(
            cmd, 
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        print("📊 Crawler Results:")
        print(f"   Exit code: {result.returncode}")
        print()
        
        if result.stdout:
            print("📝 Crawler Output:")
            print("-" * 50)
            # Show last 50 lines of output
            output_lines = result.stdout.split('\n')
            for line in output_lines[-50:]:
                if line.strip():
                    print(line)
            print("-" * 50)
            print()
        
        if result.stderr:
            print("⚠️  Crawler Errors:")
            print("-" * 50)
            print(result.stderr)
            print("-" * 50)
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
            
            cursor.execute('SELECT COUNT(*) FROM phase1_data')
            total_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM phase1_data WHERE timtaxa_livsmedel IS NOT NULL')
            livsmedel_count = cursor.fetchone()[0]
            
            print(f"   Total records: {total_count}")
            print(f"   Records with food control data: {livsmedel_count}")
            
            if total_count > 0:
                cursor.execute('SELECT municipality, timtaxa_livsmedel, source_url FROM phase1_data LIMIT 5')
                records = cursor.fetchall()
                
                print("   Sample records:")
                for record in records:
                    print(f"     {record[0]}: {record[1]} kr/timme from {record[2]}")
            
            conn.close()
        else:
            print("❌ No database files found")
        
        # Clean up
        os.unlink(temp_municipalities_file)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⏰ Crawler timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"❌ Error running crawler: {e}")
        return False

if __name__ == "__main__":
    success = test_uppsala_crawler()
    
    if success:
        print("🎉 Uppsala crawler test completed!")
    else:
        print("❌ Uppsala crawler test failed")
        print()
        print("💡 This might be expected if Uppsala doesn't have the data")
        print("   or if the crawler needs further improvements") 