#!/usr/bin/env python3
"""
Create Demo Data for Phase 1 System
Generates realistic sample data to demonstrate the web interface
"""

import sqlite3
import json
import csv
import pandas as pd
from datetime import datetime
from pathlib import Path
import random

def create_demo_data():
    """Create demo Phase 1 data"""
    
    # Sample municipalities with realistic data
    demo_municipalities = [
        {
            'municipality': 'Stockholm',
            'timtaxa_livsmedel': 1250,
            'debitering_livsmedel': 'förskott',
            'timtaxa_bygglov': 1150,
            'source_url': 'https://stockholm.se/taxa',
            'confidence': 0.95,
            'data_completeness': 1.0,
            'status': 'complete'
        },
        {
            'municipality': 'Göteborg',
            'timtaxa_livsmedel': 1180,
            'debitering_livsmedel': 'efterhand',
            'timtaxa_bygglov': 1100,
            'source_url': 'https://goteborg.se/avgifter',
            'confidence': 0.90,
            'data_completeness': 1.0,
            'status': 'complete'
        },
        {
            'municipality': 'Malmö',
            'timtaxa_livsmedel': 1300,
            'debitering_livsmedel': 'förskott',
            'timtaxa_bygglov': None,  # Missing data
            'source_url': 'https://malmo.se/taxa',
            'confidence': 0.85,
            'data_completeness': 0.67,
            'status': 'partial'
        },
        {
            'municipality': 'Uppsala',
            'timtaxa_livsmedel': 1220,
            'debitering_livsmedel': 'efterhand',
            'timtaxa_bygglov': 1080,
            'source_url': 'https://uppsala.se/avgifter',
            'confidence': 0.88,
            'data_completeness': 1.0,
            'status': 'complete'
        },
        {
            'municipality': 'Västerås',
            'timtaxa_livsmedel': None,  # Missing data
            'debitering_livsmedel': 'förskott',
            'timtaxa_bygglov': 1200,
            'source_url': 'https://vasteras.se/taxa',
            'confidence': 0.75,
            'data_completeness': 0.67,
            'status': 'partial'
        },
        {
            'municipality': 'Örebro',
            'timtaxa_livsmedel': 1160,
            'debitering_livsmedel': 'efterhand',
            'timtaxa_bygglov': 1050,
            'source_url': 'https://orebro.se/avgifter',
            'confidence': 0.92,
            'data_completeness': 1.0,
            'status': 'complete'
        },
        {
            'municipality': 'Linköping',
            'timtaxa_livsmedel': 1280,
            'debitering_livsmedel': 'förskott',
            'timtaxa_bygglov': 1120,
            'source_url': 'https://linkoping.se/taxa',
            'confidence': 0.87,
            'data_completeness': 1.0,
            'status': 'complete'
        },
        {
            'municipality': 'Helsingborg',
            'timtaxa_livsmedel': 1190,
            'debitering_livsmedel': 'efterhand',
            'timtaxa_bygglov': None,  # Missing data
            'source_url': 'https://helsingborg.se/avgifter',
            'confidence': 0.80,
            'data_completeness': 0.67,
            'status': 'partial'
        },
        {
            'municipality': 'Jönköping',
            'timtaxa_livsmedel': 1240,
            'debitering_livsmedel': 'förskott',
            'timtaxa_bygglov': 1170,
            'source_url': 'https://jonkoping.se/taxa',
            'confidence': 0.89,
            'data_completeness': 1.0,
            'status': 'complete'
        },
        {
            'municipality': 'Norrköping',
            'timtaxa_livsmedel': 1210,
            'debitering_livsmedel': 'efterhand',
            'timtaxa_bygglov': 1090,
            'source_url': 'https://norrkoping.se/avgifter',
            'confidence': 0.91,
            'data_completeness': 1.0,
            'status': 'complete'
        }
    ]
    
    # Create output directory
    output_dir = Path('data/output')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    
    # Create CSV file
    csv_file = output_dir / f'phase1_municipal_data_{timestamp}.csv'
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'municipality', 'timtaxa_livsmedel', 'debitering_livsmedel', 
            'timtaxa_bygglov', 'source_url', 'confidence', 'data_completeness', 
            'status', 'extraction_date', 'source_type'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for item in demo_municipalities:
            row = item.copy()
            row['extraction_date'] = datetime.now().isoformat()
            row['source_type'] = 'HTML'
            writer.writerow(row)
    
    print(f"✅ Created CSV: {csv_file}")
    
    # Create SQLite database
    db_file = output_dir / f'phase1_municipal_data_{timestamp}.db'
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE phase1_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            municipality TEXT NOT NULL,
            timtaxa_livsmedel REAL,
            debitering_livsmedel TEXT,
            timtaxa_bygglov REAL,
            source_url TEXT,
            confidence REAL,
            data_completeness REAL,
            data_quality REAL,
            status TEXT,
            extraction_date TEXT,
            source_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total_municipalities INTEGER,
            complete_municipalities INTEGER,
            partial_municipalities INTEGER,
            empty_municipalities INTEGER,
            avg_confidence REAL,
            avg_completeness REAL,
            livsmedel_coverage REAL,
            debitering_coverage REAL,
            bygglov_coverage REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE coverage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            field_name TEXT,
            municipalities_with_data INTEGER,
            total_municipalities INTEGER,
            coverage_percentage REAL,
            avg_value REAL,
            min_value REAL,
            max_value REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE quality (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            municipality TEXT,
            quality_score REAL,
            completeness_score REAL,
            confidence_score REAL,
            data_freshness_score REAL,
            overall_grade TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert data
    for item in demo_municipalities:
        # Calculate data quality score (0-100)
        data_quality = (item['confidence'] + item['data_completeness']) / 2 * 100
        
        cursor.execute('''
            INSERT INTO phase1_data (
                municipality, timtaxa_livsmedel, debitering_livsmedel, 
                timtaxa_bygglov, source_url, confidence, data_completeness, 
                data_quality, status, extraction_date, source_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            item['municipality'], item['timtaxa_livsmedel'], item['debitering_livsmedel'],
            item['timtaxa_bygglov'], item['source_url'], item['confidence'],
            item['data_completeness'], data_quality, item['status'], datetime.now().isoformat(), 'HTML'
        ))
    
    # Calculate and insert statistics
    total = len(demo_municipalities)
    complete = len([m for m in demo_municipalities if m['status'] == 'complete'])
    partial = len([m for m in demo_municipalities if m['status'] == 'partial'])
    empty = total - complete - partial
    
    avg_confidence = sum(m['confidence'] for m in demo_municipalities) / total
    avg_completeness = sum(m['data_completeness'] for m in demo_municipalities) / total
    
    livsmedel_coverage = len([m for m in demo_municipalities if m['timtaxa_livsmedel']]) / total
    debitering_coverage = len([m for m in demo_municipalities if m['debitering_livsmedel']]) / total
    bygglov_coverage = len([m for m in demo_municipalities if m['timtaxa_bygglov']]) / total
    
    cursor.execute('''
        INSERT INTO statistics (
            total_municipalities, complete_municipalities, partial_municipalities,
            empty_municipalities, avg_confidence, avg_completeness,
            livsmedel_coverage, debitering_coverage, bygglov_coverage
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (total, complete, partial, empty, avg_confidence, avg_completeness,
          livsmedel_coverage, debitering_coverage, bygglov_coverage))
    
    # Insert coverage data
    coverage_data = [
        ('timtaxa_livsmedel', len([m for m in demo_municipalities if m['timtaxa_livsmedel']]), 
         total, livsmedel_coverage * 100,
         sum(m['timtaxa_livsmedel'] for m in demo_municipalities if m['timtaxa_livsmedel']) / len([m for m in demo_municipalities if m['timtaxa_livsmedel']]),
         min(m['timtaxa_livsmedel'] for m in demo_municipalities if m['timtaxa_livsmedel']),
         max(m['timtaxa_livsmedel'] for m in demo_municipalities if m['timtaxa_livsmedel'])),
        ('timtaxa_bygglov', len([m for m in demo_municipalities if m['timtaxa_bygglov']]), 
         total, bygglov_coverage * 100,
         sum(m['timtaxa_bygglov'] for m in demo_municipalities if m['timtaxa_bygglov']) / len([m for m in demo_municipalities if m['timtaxa_bygglov']]),
         min(m['timtaxa_bygglov'] for m in demo_municipalities if m['timtaxa_bygglov']),
         max(m['timtaxa_bygglov'] for m in demo_municipalities if m['timtaxa_bygglov'])),
    ]
    
    for coverage in coverage_data:
        cursor.execute('''
            INSERT INTO coverage (
                field_name, municipalities_with_data, total_municipalities,
                coverage_percentage, avg_value, min_value, max_value
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', coverage)
    
    # Insert quality data
    for item in demo_municipalities:
        quality_score = (item['confidence'] + item['data_completeness']) / 2
        grade = 'A' if quality_score >= 0.9 else 'B' if quality_score >= 0.8 else 'C' if quality_score >= 0.7 else 'D'
        
        cursor.execute('''
            INSERT INTO quality (
                municipality, quality_score, completeness_score, confidence_score,
                data_freshness_score, overall_grade
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (item['municipality'], quality_score, item['data_completeness'], 
              item['confidence'], 0.95, grade))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Created Database: {db_file}")
    
    # Create Excel file
    excel_file = output_dir / f'phase1_municipal_data_{timestamp}.xlsx'
    
    # Convert to DataFrame
    df = pd.DataFrame(demo_municipalities)
    df['extraction_date'] = datetime.now().isoformat()
    df['source_type'] = 'HTML'
    
    # Create Excel with multiple sheets
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        # Main data sheet
        df.to_excel(writer, sheet_name='Phase1_Data', index=False)
        
        # Summary sheet
        summary_data = {
            'Metric': ['Total Municipalities', 'Complete Data', 'Partial Data', 'Average Confidence', 'Average Completeness'],
            'Value': [total, complete, partial, f"{avg_confidence:.2f}", f"{avg_completeness:.1%}"]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
        
        # Coverage sheet
        coverage_df = pd.DataFrame([
            {'Field': 'Timtaxa Livsmedel', 'Coverage': f"{livsmedel_coverage:.1%}", 'Count': len([m for m in demo_municipalities if m['timtaxa_livsmedel']])},
            {'Field': 'Debitering Livsmedel', 'Coverage': f"{debitering_coverage:.1%}", 'Count': len([m for m in demo_municipalities if m['debitering_livsmedel']])},
            {'Field': 'Timtaxa Bygglov', 'Coverage': f"{bygglov_coverage:.1%}", 'Count': len([m for m in demo_municipalities if m['timtaxa_bygglov']])}
        ])
        coverage_df.to_excel(writer, sheet_name='Coverage', index=False)
    
    print(f"✅ Created Excel: {excel_file}")
    
    # Create statistics JSON
    stats_file = output_dir / f'phase1_statistics_{timestamp}.json'
    statistics = {
        'generation_date': datetime.now().isoformat(),
        'total_municipalities': total,
        'complete_municipalities': complete,
        'partial_municipalities': partial,
        'empty_municipalities': empty,
        'completion_rate': complete / total,
        'partial_rate': partial / total,
        'average_confidence': avg_confidence,
        'average_completeness': avg_completeness,
        'field_coverage': {
            'timtaxa_livsmedel': livsmedel_coverage,
            'debitering_livsmedel': debitering_coverage,
            'timtaxa_bygglov': bygglov_coverage
        },
        'data_quality': {
            'high_quality': len([m for m in demo_municipalities if m['confidence'] >= 0.9]),
            'medium_quality': len([m for m in demo_municipalities if 0.8 <= m['confidence'] < 0.9]),
            'low_quality': len([m for m in demo_municipalities if m['confidence'] < 0.8])
        }
    }
    
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(statistics, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Created Statistics: {stats_file}")
    
    print()
    print("🎉 Demo data created successfully!")
    print(f"📊 Generated data for {total} municipalities:")
    print(f"   ✅ Complete: {complete} ({complete/total:.1%})")
    print(f"   ⚠️  Partial: {partial} ({partial/total:.1%})")
    print(f"   📈 Average confidence: {avg_confidence:.2f}")
    print(f"   📈 Average completeness: {avg_completeness:.1%}")
    print()
    print("🌐 You can now start the web interface to view this data!")
    print("   python3 start_phase1_system.py --web-only")

if __name__ == '__main__':
    create_demo_data() 