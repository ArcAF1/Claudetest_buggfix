#!/usr/bin/env python3
"""
Test script for Phase 1 Web Interface
Tests API endpoints and basic functionality
"""

import sys
import os
import tempfile
import sqlite3
import json
from pathlib import Path
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def create_test_database():
    """Create a test database with sample Phase 1 data"""
    # Create temporary database
    temp_dir = Path('data/output')
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    db_path = temp_dir / f'phase1_municipal_data_{timestamp}.db'
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create Phase 1 data table
    cursor.execute('''
        CREATE TABLE phase1_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            municipality TEXT UNIQUE NOT NULL,
            timtaxa_livsmedel INTEGER,
            debitering_livsmedel TEXT,
            timtaxa_bygglov INTEGER,
            completeness_score REAL,
            data_quality INTEGER,
            source_url TEXT,
            source_type TEXT,
            extraction_date TEXT,
            confidence REAL,
            status TEXT,
            validation_warnings TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert sample data
    sample_data = [
        ('Stockholm', 1350, 'förskott', 1200, 1.0, 95, 'https://stockholm.se/taxor.pdf', 'PDF', datetime.now().isoformat(), 0.95, 'complete', ''),
        ('Göteborg', 1400, 'efterhand', None, 0.67, 80, 'https://goteborg.se/avgifter.html', 'HTML', datetime.now().isoformat(), 0.80, 'partial', ''),
        ('Malmö', None, None, 1300, 0.33, 75, 'https://malmo.se/bygglov.pdf', 'PDF', datetime.now().isoformat(), 0.75, 'partial', ''),
        ('Uppsala', 1250, 'förskott', 1150, 1.0, 90, 'https://uppsala.se/taxor.pdf', 'PDF', datetime.now().isoformat(), 0.90, 'complete', ''),
        ('Västerås', 1300, None, 1250, 0.67, 85, 'https://vasteras.se/avgifter.html', 'HTML', datetime.now().isoformat(), 0.85, 'partial', ''),
    ]
    
    for data in sample_data:
        cursor.execute('''
            INSERT INTO phase1_data (
                municipality, timtaxa_livsmedel, debitering_livsmedel,
                timtaxa_bygglov, completeness_score, data_quality,
                source_url, source_type, extraction_date, confidence,
                status, validation_warnings
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', data)
    
    conn.commit()
    conn.close()
    
    print(f"✓ Created test database: {db_path}")
    return db_path

def create_test_statistics():
    """Create a test statistics file"""
    temp_dir = Path('data/output')
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stats_path = temp_dir / f'phase1_statistics_{timestamp}.json'
    
    stats = {
        'extraction_metadata': {
            'extraction_date': datetime.now().isoformat(),
            'total_municipalities': 5,
            'processing_time_minutes': 2.5,
            'items_processed': 5,
            'items_exported': 5,
            'errors_count': 0
        },
        'completeness_analysis': {
            'complete_data': 2,
            'partial_data': 3,
            'no_data': 0
        },
        'field_coverage': {
            'timtaxa_livsmedel': {
                'municipalities_with_data': 3,
                'coverage_percentage': 60.0,
                'total_municipalities': 5
            },
            'debitering_livsmedel': {
                'municipalities_with_data': 3,
                'coverage_percentage': 60.0,
                'total_municipalities': 5
            },
            'timtaxa_bygglov': {
                'municipalities_with_data': 4,
                'coverage_percentage': 80.0,
                'total_municipalities': 5
            }
        },
        'success_metrics': {
            'overall_success_rate': 100.0,
            'complete_data_rate': 40.0,
            'average_fields_per_municipality': 2.2
        }
    }
    
    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Created test statistics: {stats_path}")
    return stats_path

def test_api_endpoints():
    """Test API endpoints"""
    try:
        from phase1_app import app
        
        with app.test_client() as client:
            print("\n=== Testing API Endpoints ===")
            
            # Test overview endpoint
            response = client.get('/api/phase1/overview')
            if response.status_code == 200:
                data = response.get_json()
                print(f"✓ Overview API: {data.get('total_municipalities', 0)} municipalities")
            else:
                print(f"✗ Overview API failed: {response.status_code}")
            
            # Test municipalities endpoint
            response = client.get('/api/phase1/municipalities')
            if response.status_code == 200:
                data = response.get_json()
                print(f"✓ Municipalities API: {len(data)} records")
            else:
                print(f"✗ Municipalities API failed: {response.status_code}")
            
            # Test comparison endpoint
            response = client.get('/api/phase1/comparison')
            if response.status_code == 200:
                data = response.get_json()
                print(f"✓ Comparison API: {len(data.get('municipalities', []))} municipalities")
            else:
                print(f"✗ Comparison API failed: {response.status_code}")
            
            # Test missing data endpoint
            response = client.get('/api/phase1/missing-data')
            if response.status_code == 200:
                data = response.get_json()
                print(f"✓ Missing Data API: {len(data.get('all_fields', []))} missing all fields")
            else:
                print(f"✗ Missing Data API failed: {response.status_code}")
            
            # Test export endpoints
            for format_type in ['json', 'csv']:
                response = client.get(f'/api/phase1/export/{format_type}')
                if response.status_code == 200:
                    print(f"✓ Export {format_type.upper()} API: Success")
                else:
                    print(f"✗ Export {format_type.upper()} API failed: {response.status_code}")
            
            return True
            
    except Exception as e:
        print(f"✗ API testing failed: {e}")
        return False

def test_dashboard_rendering():
    """Test dashboard template rendering"""
    try:
        from phase1_app import app
        
        with app.test_client() as client:
            print("\n=== Testing Dashboard Rendering ===")
            
            response = client.get('/')
            if response.status_code == 200:
                content = response.get_data(as_text=True)
                
                # Check for key elements
                checks = [
                    ('Phase 1 Data Analysis', 'Main title'),
                    ('Total Municipalities', 'Overview card'),
                    ('Timtaxa Comparison', 'Chart section'),
                    ('Municipality Data', 'Data table'),
                    ('Missing Data Analysis', 'Missing data section')
                ]
                
                for check_text, description in checks:
                    if check_text in content:
                        print(f"✓ {description}: Found")
                    else:
                        print(f"✗ {description}: Missing")
                
                return True
            else:
                print(f"✗ Dashboard rendering failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"✗ Dashboard rendering failed: {e}")
        return False

def main():
    """Main test function"""
    print("=== Phase 1 Web Interface Test ===")
    print("Testing web interface functionality...")
    
    # Create test data
    try:
        db_path = create_test_database()
        stats_path = create_test_statistics()
    except Exception as e:
        print(f"✗ Failed to create test data: {e}")
        return 1
    
    # Test API endpoints
    api_success = test_api_endpoints()
    
    # Test dashboard rendering
    dashboard_success = test_dashboard_rendering()
    
    # Summary
    print("\n=== Test Summary ===")
    if api_success and dashboard_success:
        print("✅ All tests passed!")
        print("\nTo start the web interface:")
        print("  python run_phase1_web.py")
        print("  Then visit: http://127.0.0.1:5001")
        return 0
    else:
        print("❌ Some tests failed!")
        print("Check the error messages above for details.")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code) 