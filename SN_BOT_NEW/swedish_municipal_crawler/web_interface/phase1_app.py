#!/usr/bin/env python3
"""
Phase 1 Web Interface for Swedish Municipal Fee Crawler
Focuses on the three specific Phase 1 data points:
1. Timtaxan för livsmedelskontroll (Hourly rate for food control)
2. Debiteringsmodell för livsmedelskontroll (Billing model: prepaid vs post-paid)
3. Timtaxan för bygglov (Hourly rate for building permits)
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO, emit
import sqlite3
import json
import pandas as pd
import io
from pathlib import Path
from datetime import datetime
import logging
import os
import subprocess
import threading
import time
import queue
import re
import socket
import sys
import psutil

app = Flask(__name__)
app.config['SECRET_KEY'] = 'phase1-municipal-data-viewer'

# Initialize SocketIO for real-time communication
socketio = SocketIO(app, cors_allowed_origins="*")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_latest_db():
    """Get the most recent Phase 1 database"""
    # Try multiple possible paths
    possible_paths = [
        Path('../data/output'),
        Path('data/output'),
        Path('../swedish_municipal_crawler/data/output'),
        Path('swedish_municipal_crawler/data/output')
    ]
    
    for output_dir in possible_paths:
        if output_dir.exists():
            db_files = list(output_dir.glob('phase1_municipal_data_*.db'))
            if db_files:
                latest_db = max(db_files, key=lambda x: x.stat().st_mtime)
                logger.info(f"Using database: {latest_db}")
                return latest_db
    
    logger.warning("No Phase 1 database files found in any expected location")
    return None

def get_latest_stats():
    """Get the most recent Phase 1 statistics file"""
    # Try multiple possible paths
    possible_paths = [
        Path('../data/output'),
        Path('data/output'),
        Path('../swedish_municipal_crawler/data/output'),
        Path('swedish_municipal_crawler/data/output')
    ]
    
    for output_dir in possible_paths:
        if output_dir.exists():
            stats_files = list(output_dir.glob('phase1_statistics_*.json'))
            if stats_files:
                return max(stats_files, key=lambda x: x.stat().st_mtime)
    
    return None

@app.route('/')
def index():
    """Phase 1 dashboard"""
    return render_template('phase1_dashboard.html')

@app.route('/api/phase1/overview')
def get_overview():
    """Get Phase 1 overview statistics"""
    db_path = get_latest_db()
    if not db_path:
        return jsonify({'error': 'No Phase 1 data found'}), 404
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if the table exists and has data
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='phase1_data'")
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': 'No phase1_data table found in database'}), 404

        # Get totals
        cursor.execute('SELECT COUNT(*) FROM phase1_data')
        total_municipalities = cursor.fetchone()[0]
        
        if total_municipalities == 0:
            conn.close()
            return jsonify({
                'total_municipalities': 0,
                'complete_data': 0,
                'partial_data': 0,
                'completion_rate': 0,
                'partial_rate': 0,
                'coverage': {
                    'timtaxa_livsmedel': {'count': 0, 'percentage': 0},
                    'debitering_livsmedel': {'count': 0, 'percentage': 0},
                    'timtaxa_bygglov': {'count': 0, 'percentage': 0}
                },
                'statistics': {
                    'timtaxa_livsmedel': {'average': None, 'min': None, 'max': None},
                    'timtaxa_bygglov': {'average': None, 'min': None, 'max': None}
                },
                'debitering_distribution': {},
                'quality_distribution': {},
                'latest_extraction': None
            })

        # Get complete data count
        cursor.execute('SELECT COUNT(*) FROM phase1_data WHERE status = "complete"')
        complete_data = cursor.fetchone()[0]

        # Get partial data count
        cursor.execute('SELECT COUNT(*) FROM phase1_data WHERE status = "partial"')
        partial_data = cursor.fetchone()[0]

        # Get field coverage
        coverage = {}
        for field in ['timtaxa_livsmedel', 'debitering_livsmedel', 'timtaxa_bygglov']:
            cursor.execute(f'SELECT COUNT(*) FROM phase1_data WHERE {field} IS NOT NULL AND {field} != ""')
            coverage[field] = cursor.fetchone()[0]

        # Get averages for timtaxa fields
        cursor.execute('''
            SELECT 
                AVG(CAST(timtaxa_livsmedel AS REAL)) as avg_livsmedel,
                AVG(CAST(timtaxa_bygglov AS REAL)) as avg_bygglov,
                MIN(CAST(timtaxa_livsmedel AS REAL)) as min_livsmedel,
                MAX(CAST(timtaxa_livsmedel AS REAL)) as max_livsmedel,
                MIN(CAST(timtaxa_bygglov AS REAL)) as min_bygglov,
                MAX(CAST(timtaxa_bygglov AS REAL)) as max_bygglov
            FROM phase1_data
            WHERE timtaxa_livsmedel IS NOT NULL OR timtaxa_bygglov IS NOT NULL
        ''')
        stats_row = cursor.fetchone()

        # Get debitering distribution
        cursor.execute('''
            SELECT debitering_livsmedel, COUNT(*) 
            FROM phase1_data 
            WHERE debitering_livsmedel IS NOT NULL AND debitering_livsmedel != ""
            GROUP BY debitering_livsmedel
        ''')
        debitering_dist = dict(cursor.fetchall())

        # Get quality distribution
        cursor.execute('''
            SELECT 
                CASE 
                    WHEN data_quality >= 90 THEN 'excellent'
                    WHEN data_quality >= 70 THEN 'good'
                    WHEN data_quality >= 50 THEN 'fair'
                    ELSE 'poor'
                END as quality_tier,
                COUNT(*) as count
            FROM phase1_data
            WHERE data_quality IS NOT NULL
            GROUP BY quality_tier
        ''')
        quality_dist = dict(cursor.fetchall())

        # Get latest extraction date
        cursor.execute('SELECT MAX(extraction_date) FROM phase1_data')
        latest_extraction = cursor.fetchone()[0]

        conn.close()

        return jsonify({
            'total_municipalities': total_municipalities,
            'complete_data': complete_data,
            'partial_data': partial_data,
            'completion_rate': round(complete_data / total_municipalities * 100, 1) if total_municipalities > 0 else 0,
            'partial_rate': round(partial_data / total_municipalities * 100, 1) if total_municipalities > 0 else 0,
            'coverage': {
                'timtaxa_livsmedel': {
                    'count': coverage['timtaxa_livsmedel'],
                    'percentage': round(coverage['timtaxa_livsmedel'] / total_municipalities * 100, 1) if total_municipalities > 0 else 0
                },
                'debitering_livsmedel': {
                    'count': coverage['debitering_livsmedel'],
                    'percentage': round(coverage['debitering_livsmedel'] / total_municipalities * 100, 1) if total_municipalities > 0 else 0
                },
                'timtaxa_bygglov': {
                    'count': coverage['timtaxa_bygglov'],
                    'percentage': round(coverage['timtaxa_bygglov'] / total_municipalities * 100, 1) if total_municipalities > 0 else 0
                }
            },
            'statistics': {
                'timtaxa_livsmedel': {
                    'average': round(stats_row[0]) if stats_row[0] else None,
                    'min': round(stats_row[2]) if stats_row[2] else None,
                    'max': round(stats_row[3]) if stats_row[3] else None
                },
                'timtaxa_bygglov': {
                    'average': round(stats_row[1]) if stats_row[1] else None,
                    'min': round(stats_row[4]) if stats_row[4] else None,
                    'max': round(stats_row[5]) if stats_row[5] else None
                }
            },
            'debitering_distribution': debitering_dist,
            'quality_distribution': quality_dist,
            'latest_extraction': latest_extraction
        })
        
    except Exception as e:
        logger.error(f"Error getting overview: {e}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route('/api/phase1/municipalities')
def get_municipalities():
    """Get all Phase 1 municipality data with filtering and sorting"""
    db_path = get_latest_db()
    if not db_path:
        return jsonify({'error': 'No Phase 1 data found'}), 404
    
    try:
        conn = sqlite3.connect(db_path)
        
        # Get query parameters
        search = request.args.get('search', '').strip()
        status_filter = request.args.get('status', '')
        sort_by = request.args.get('sort', 'municipality')
        sort_order = request.args.get('order', 'asc')
        
        # Build query
        query = '''
            SELECT 
                municipality,
                timtaxa_livsmedel,
                debitering_livsmedel,
                timtaxa_bygglov,
                data_completeness,
                data_quality,
                status,
                source_url,
                source_type,
                confidence,
                extraction_date
            FROM phase1_data
        '''
        
        conditions = []
        params = []
        
        if search:
            conditions.append('municipality LIKE ?')
            params.append(f'%{search}%')
        
        if status_filter:
            conditions.append('status = ?')
            params.append(status_filter)
        
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
        
        # Add sorting
        valid_sort_fields = ['municipality', 'timtaxa_livsmedel', 'timtaxa_bygglov', 'data_quality', 'data_completeness']
        if sort_by in valid_sort_fields:
            order = 'DESC' if sort_order.lower() == 'desc' else 'ASC'
            query += f' ORDER BY {sort_by} {order}'
        else:
            query += ' ORDER BY municipality ASC'
        
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        municipalities = []
        for row in cursor.fetchall():
            municipalities.append({
                'municipality': row[0],
                'timtaxa_livsmedel': row[1],
                'debitering_livsmedel': row[2],
                'timtaxa_bygglov': row[3],
                'data_completeness': round(row[4] * 100) if row[4] else 0,
                'data_quality': round(row[5], 1) if row[5] else 0,
                'status': row[6],
                'source_url': row[7],
                'source_type': row[8],
                'confidence': round(row[9], 2) if row[9] else 0,
                'extraction_date': row[10]
            })

        conn.close()
        return jsonify(municipalities)
        
    except Exception as e:
        logger.error(f"Error getting municipalities: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/phase1/comparison')
def get_comparison():
    """Get comparison data for visualization"""
    db_path = get_latest_db()
    if not db_path:
        return jsonify({'error': 'No Phase 1 data found'}), 404
    
    try:
        conn = sqlite3.connect(db_path)

        # Get data for charts
        df = pd.read_sql_query('''
            SELECT 
                municipality, 
                CAST(timtaxa_livsmedel AS REAL) as timtaxa_livsmedel,
                CAST(timtaxa_bygglov AS REAL) as timtaxa_bygglov,
                debitering_livsmedel
            FROM phase1_data
            WHERE timtaxa_livsmedel IS NOT NULL OR timtaxa_bygglov IS NOT NULL
            ORDER BY timtaxa_livsmedel DESC NULLS LAST
        ''', conn)

        conn.close()

        # Prepare data for charts
        comparison_data = {
            'municipalities': df['municipality'].tolist(),
            'timtaxa_livsmedel': df['timtaxa_livsmedel'].fillna(0).tolist(),
            'timtaxa_bygglov': df['timtaxa_bygglov'].fillna(0).tolist(),
            'debitering_livsmedel': df['debitering_livsmedel'].fillna('').tolist()
        }
        
        # Get top 10 highest and lowest for each field
        livsmedel_data = df[df['timtaxa_livsmedel'].notna()].sort_values('timtaxa_livsmedel', ascending=False)
        bygglov_data = df[df['timtaxa_bygglov'].notna()].sort_values('timtaxa_bygglov', ascending=False)
        
        comparison_data['top_livsmedel'] = {
            'municipalities': livsmedel_data.head(10)['municipality'].tolist(),
            'values': livsmedel_data.head(10)['timtaxa_livsmedel'].tolist()
        }
        
        comparison_data['bottom_livsmedel'] = {
            'municipalities': livsmedel_data.tail(10)['municipality'].tolist(),
            'values': livsmedel_data.tail(10)['timtaxa_livsmedel'].tolist()
        }
        
        comparison_data['top_bygglov'] = {
            'municipalities': bygglov_data.head(10)['municipality'].tolist(),
            'values': bygglov_data.head(10)['timtaxa_bygglov'].tolist()
        }
        
        comparison_data['bottom_bygglov'] = {
            'municipalities': bygglov_data.tail(10)['municipality'].tolist(),
            'values': bygglov_data.tail(10)['timtaxa_bygglov'].tolist()
        }

        return jsonify(comparison_data)
        
    except Exception as e:
        logger.error(f"Error getting comparison data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/phase1/missing-data')
def get_missing_data():
    """Get municipalities with missing data"""
    db_path = get_latest_db()
    if not db_path:
        return jsonify({'error': 'No Phase 1 data found'}), 404
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        missing = {
            'timtaxa_livsmedel': [],
            'debitering_livsmedel': [],
            'timtaxa_bygglov': [],
            'all_fields': []
        }

        # Get municipalities missing each field
        for field in ['timtaxa_livsmedel', 'debitering_livsmedel', 'timtaxa_bygglov']:
            cursor.execute(f'''
                SELECT municipality, source_url, source_type
                FROM phase1_data 
                WHERE {field} IS NULL OR {field} = ""
                ORDER BY municipality
            ''')
            missing[field] = [{'municipality': row[0], 'source_url': row[1], 'source_type': row[2]} 
                             for row in cursor.fetchall()]

        # Get municipalities missing all fields
        cursor.execute('''
            SELECT municipality, source_url, source_type
            FROM phase1_data 
            WHERE (timtaxa_livsmedel IS NULL OR timtaxa_livsmedel = "")
              AND (debitering_livsmedel IS NULL OR debitering_livsmedel = "")
              AND (timtaxa_bygglov IS NULL OR timtaxa_bygglov = "")
            ORDER BY municipality
        ''')
        missing['all_fields'] = [{'municipality': row[0], 'source_url': row[1], 'source_type': row[2]} 
                                for row in cursor.fetchall()]

        conn.close()
        return jsonify(missing)
        
    except Exception as e:
        logger.error(f"Error getting missing data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/phase1/statistics')
def get_statistics():
    """Get detailed statistics"""
    try:
        db_path = get_latest_db()
        if not db_path:
            return jsonify({'error': 'No database found'})
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get basic statistics
        cursor.execute('SELECT * FROM statistics ORDER BY created_at DESC LIMIT 1')
        stats_row = cursor.fetchone()
        
        if not stats_row:
            return jsonify({'error': 'No statistics available'})
        
        statistics = {
            'total_municipalities': stats_row[1],
            'complete_municipalities': stats_row[2],
            'partial_municipalities': stats_row[3],
            'empty_municipalities': stats_row[4],
            'avg_confidence': round(stats_row[5], 2),
            'avg_completeness': round(stats_row[6], 2),
            'field_coverage': {
                'livsmedel': round(stats_row[7] * 100, 1),
                'debitering': round(stats_row[8] * 100, 1),
                'bygglov': round(stats_row[9] * 100, 1)
            }
        }
        
        conn.close()
        return jsonify(statistics)
        
    except Exception as e:
        app.logger.error(f"Error getting statistics: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/phase1/export/<format>')
def export_data(format):
    """Export Phase 1 data in various formats"""
    db_path = get_latest_db()
    if not db_path:
        return jsonify({'error': 'No Phase 1 data found'}), 404
    
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query('SELECT * FROM phase1_data ORDER BY municipality', conn)
        conn.close()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M")

        if format == 'excel':
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Main data sheet
                df.to_excel(writer, sheet_name='Phase 1 Data', index=False)
                
                # Summary sheet
                summary_data = []
                total = len(df)
                complete = len(df[df['status'] == 'complete'])
                partial = len(df[df['status'] == 'partial'])
                
                summary_data.append(['Total Municipalities', total])
                summary_data.append(['Complete Data', complete])
                summary_data.append(['Partial Data', partial])
                summary_data.append(['Completion Rate (%)', round(complete/total*100, 1) if total > 0 else 0])
                
                # Field coverage
                for field in ['timtaxa_livsmedel', 'debitering_livsmedel', 'timtaxa_bygglov']:
                    count = len(df[df[field].notna() & (df[field] != '')])
                    summary_data.append([f'{field} Coverage', count])
                    summary_data.append([f'{field} Coverage (%)', round(count/total*100, 1) if total > 0 else 0])
                
                # Statistics for numeric fields
                for field in ['timtaxa_livsmedel', 'timtaxa_bygglov']:
                    numeric_data = pd.to_numeric(df[field], errors='coerce').dropna()
                    if len(numeric_data) > 0:
                        summary_data.append([f'{field} Average', round(numeric_data.mean())])
                        summary_data.append([f'{field} Min', round(numeric_data.min())])
                        summary_data.append([f'{field} Max', round(numeric_data.max())])
                
                summary_df = pd.DataFrame(summary_data, columns=['Metric', 'Value'])
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Missing data analysis
                missing_data = []
                for field in ['timtaxa_livsmedel', 'debitering_livsmedel', 'timtaxa_bygglov']:
                    missing_municipalities = df[df[field].isna() | (df[field] == '')]['municipality'].tolist()
                    for municipality in missing_municipalities:
                        missing_data.append([field, municipality])
                
                if missing_data:
                    missing_df = pd.DataFrame(missing_data, columns=['Missing Field', 'Municipality'])
                    missing_df.to_excel(writer, sheet_name='Missing Data', index=False)
            
            output.seek(0)
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'phase1_data_{timestamp}.xlsx'
            )

        elif format == 'csv':
            output = io.StringIO()
            df.to_csv(output, index=False, encoding='utf-8')
            output.seek(0)
            
            response = app.response_class(
                output.getvalue(),
                mimetype='text/csv',
                headers={'Content-Disposition': f'attachment; filename=phase1_data_{timestamp}.csv'}
            )
            return response

        elif format == 'json':
            return jsonify(df.to_dict(orient='records'))

        else:
            return jsonify({'error': 'Invalid format. Supported: excel, csv, json'}), 400
            
    except Exception as e:
        logger.error(f"Error exporting data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/phase1/municipality/<municipality_name>')
def get_municipality_detail(municipality_name):
    """Get detailed information for a specific municipality"""
    db_path = get_latest_db()
    if not db_path:
        return jsonify({'error': 'No Phase 1 data found'}), 404
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM phase1_data WHERE municipality = ?
        ''', (municipality_name,))
        
        row = cursor.fetchone()
        if not row:
            return jsonify({'error': 'Municipality not found'}), 404
        
        # Get column names
        cursor.execute("PRAGMA table_info(phase1_data)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Create municipality data dict
        municipality_data = dict(zip(columns, row))
        
        conn.close()
        return jsonify(municipality_data)
        
    except Exception as e:
        logger.error(f"Error getting municipality detail: {e}")
        return jsonify({'error': str(e)}), 500

# Global variables for crawler management
crawler_process = None
crawler_status = {
    'running': False,
    'progress': 0,
    'status': 'Not started',
    'municipalities_processed': 0,
    'logs': [],
    'success': False,
    'error': None
}

# Real-time log queue for streaming
log_queue = queue.Queue()
log_thread = None

def log_streamer():
    """Background thread to stream logs via WebSocket"""
    while True:
        try:
            # Get log message from queue (blocks until available)
            log_message = log_queue.get(timeout=1)
            if log_message is None:  # Shutdown signal
                break
            
            # Emit to all connected clients
            socketio.emit('crawler_log', log_message)
            
        except queue.Empty:
            continue
        except Exception as e:
            logger.error(f"Error in log streamer: {e}")

def add_log_message(message, level='info', source='crawler'):
    """Add a log message to both the status and real-time stream"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    
    log_entry = {
        'timestamp': timestamp,
        'message': message,
        'level': level,
        'source': source
    }
    
    # Add to crawler status logs (limited to last 50)
    crawler_status['logs'].append(log_entry)
    if len(crawler_status['logs']) > 50:
        crawler_status['logs'] = crawler_status['logs'][-50:]
    
    # Add to real-time stream queue
    try:
        log_queue.put_nowait(log_entry)
    except queue.Full:
        pass  # Skip if queue is full

def parse_crawler_output(line):
    """Parse crawler output and extract meaningful information"""
    line = line.strip()
    if not line:
        return None
    
    # Remove ANSI color codes
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    clean_line = ansi_escape.sub('', line)
    
    # Skip DEBUG messages from PDF libraries and other verbose libraries
    if any(debug_pattern in clean_line for debug_pattern in [
        '[DEBUG] pdfminer',
        '[DEBUG] camelot',
        '[DEBUG] urllib3',
        '[DEBUG] requests',
        '[DEBUG] scrapy',
        'nexttoken:',
        'do_keyword:',
        'start_type:',
        'end_type:'
    ]):
        return None
    
    # Parse different types of log messages
    log_level = 'info'
    message = clean_line
    
    # Detect log levels
    if any(keyword in clean_line.upper() for keyword in ['ERROR', 'FAILED', 'EXCEPTION']):
        log_level = 'error'
    elif any(keyword in clean_line.upper() for keyword in ['WARNING', 'WARN']):
        log_level = 'warning'
    elif any(keyword in clean_line.upper() for keyword in ['SUCCESS', 'COMPLETED', 'FINISHED']):
        log_level = 'success'
    elif any(keyword in clean_line.upper() for keyword in ['DEBUG']):
        log_level = 'debug'
        # Skip most debug messages unless they're important
        if not any(important in clean_line for important in [
            'Starting', 'Processing', 'Crawling', 'Saving', 'Export'
        ]):
            return None
    
    # Extract specific information
    progress_info = {}
    
    # Municipality processing - be more specific about what we count
    if any(phrase in clean_line for phrase in [
        'Processing municipality',
        'Crawling municipality',
        'Extracting data from municipality',
        'Municipality processed:'
    ]):
        # Look for municipality names or specific patterns, not just any number
        municipality_match = re.search(r'municipality\s+(\d+)|municipality:\s*(\w+)', clean_line, re.IGNORECASE)
        if municipality_match:
            if municipality_match.group(1):  # Number after "municipality"
                count = int(municipality_match.group(1))
                if count < 1000:  # Sanity check - should be reasonable number
                    progress_info['municipality_count'] = count
            elif municipality_match.group(2):  # Municipality name
                # Count based on municipality name being processed
                progress_info['municipality_name'] = municipality_match.group(2)
    
    # Progress indicators
    if 'Starting' in clean_line and 'crawler' in clean_line:
        progress_info['stage'] = 'starting'
    elif 'Loading municipalities' in clean_line:
        progress_info['stage'] = 'loading'
    elif 'Starting spider' in clean_line or 'Beginning crawl' in clean_line:
        progress_info['stage'] = 'crawling'
    elif 'Saving' in clean_line or 'Database' in clean_line:
        progress_info['stage'] = 'saving'
    elif 'Export' in clean_line:
        progress_info['stage'] = 'exporting'
    
    return {
        'message': message,
        'level': log_level,
        'progress_info': progress_info
    }

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('status', {'message': 'Connected to crawler monitoring'})
    
    # Send current crawler status
    emit('crawler_status', crawler_status)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    pass

@socketio.on('request_status')
def handle_status_request():
    """Handle status request from client"""
    emit('crawler_status', crawler_status)

def is_crawler_running():
    """Check if any crawler process is actually running"""
    try:
        logger.info("Checking for running crawler processes...")
        found_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                
                # Check for actual crawler processes, but exclude web-only mode
                if 'start_phase1_system.py' in cmdline:
                    # Only consider it a crawler if it's NOT in web-only mode
                    if '--web-only' not in cmdline:
                        found_processes.append(f"PID {proc.info['pid']}: {cmdline}")
                        logger.info(f"Found crawler process: PID {proc.info['pid']}: {cmdline}")
                
                # Check for spider processes
                elif 'phase1_spider' in cmdline:
                    found_processes.append(f"PID {proc.info['pid']}: {cmdline}")
                    logger.info(f"Found spider process: PID {proc.info['pid']}: {cmdline}")
                
                # Check for direct crawler processes
                elif 'run_phase1_crawler.py' in cmdline:
                    found_processes.append(f"PID {proc.info['pid']}: {cmdline}")
                    logger.info(f"Found crawler script: PID {proc.info['pid']}: {cmdline}")
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if found_processes:
            logger.warning(f"Found {len(found_processes)} crawler processes running")
            for proc_info in found_processes:
                logger.warning(f"  - {proc_info}")
            return True
        else:
            logger.info("No crawler processes found")
            return False
            
    except Exception as e:
        logger.error(f"Error in crawler detection: {e}")
        # Fallback to global variable if psutil fails
        global crawler_process
        result = crawler_process and crawler_process.poll() is None
        logger.info(f"Fallback detection result: {result}")
        return result

@app.route('/api/phase1/reset-crawler-state', methods=['POST'])
def reset_crawler_state():
    """Reset the global crawler state to clear any stale references"""
    global crawler_process, crawler_status
    
    try:
        # Reset global variables
        crawler_process = None
        crawler_status = {
            'running': False,
            'progress': 0,
            'status': 'Not started',
            'municipalities_processed': 0,
            'logs': [],
            'success': False,
            'error': None
        }
        
        logger.info("Crawler state reset successfully")
        return jsonify({'success': True, 'message': 'Crawler state reset'})
        
    except Exception as e:
        logger.error(f"Error resetting crawler state: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/phase1/start-crawler', methods=['POST'])
def start_crawler():
    """Start the Phase 1 crawler"""
    global crawler_process, crawler_status, log_thread
    
    try:
        # Reset global crawler_process to None to clear any stale references
        crawler_process = None
        
        # Check if crawler is already running (improved detection)
        is_running = is_crawler_running()
        logger.info(f"Crawler detection result: {is_running}")
        
        if is_running:
            logger.warning("Crawler detection says crawler is already running")
            return jsonify({'error': 'Crawler is already running'}), 400
        else:
            logger.info("No crawler detected - proceeding to start new crawler")
        
        # Get mode from request
        data = request.get_json() or {}
        mode = data.get('mode', 'test')
        
        # Reset crawler status
        crawler_status = {
            'running': True,
            'progress': 0,
            'status': 'Starting...',
            'municipalities_processed': 0,
            'logs': [],
            'success': False,
            'error': None
        }
        
        # Start log streaming thread if not already running
        if log_thread is None or not log_thread.is_alive():
            log_thread = threading.Thread(target=log_streamer, daemon=True)
            log_thread.start()
        
        # Build command based on mode
        cmd = ['python', '../start_phase1_system.py']
        
        if mode == 'test':
            cmd.extend(['--quick-start'])
            add_log_message('Starting crawler in test mode (10 municipalities)', 'info', 'system')
        elif mode == 'quick':
            cmd.extend(['--full-crawl', '--max-municipalities', '50'])
            add_log_message('Starting crawler in quick mode (50 municipalities)', 'info', 'system')
        elif mode == 'full':
            cmd.extend(['--full-crawl'])
            add_log_message('Starting crawler in full mode (all municipalities)', 'info', 'system')
        else:
            return jsonify({'error': f'Invalid mode: {mode}'}), 400
        
        def run_crawler():
            global crawler_process, crawler_status
            
            try:
                # Reset status
                crawler_status['running'] = True
                crawler_status['progress'] = 0
                crawler_status['status'] = 'Starting crawler...'
                crawler_status['municipalities_processed'] = 0
                crawler_status['success'] = False
                crawler_status['error'] = None
                
                add_log_message(f'Starting Phase 1 crawler in {mode} mode...', 'info', 'system')
                
                # Start pipeline notification monitoring
                global stop_monitoring
                stop_monitoring = False
                notification_thread = threading.Thread(target=monitor_pipeline_notifications, daemon=True)
                notification_thread.start()
                add_log_message('Real-time monitoring started', 'info', 'system')
                
                # Build command
                cmd = [
                    sys.executable, 'run_phase1_crawler.py',
                    '--mode', mode,
                    '--max-municipalities', str(max_municipalities)
                ]
                
                # Start crawler process
                crawler_process = subprocess.Popen(
                    cmd,
                    cwd=project_root,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    bufsize=1
                )
                
                add_log_message(f'Crawler process started (PID: {crawler_process.pid})', 'info', 'system')
                crawler_status['progress'] = 10
                crawler_status['status'] = 'Crawler process started'
                
                # Monitor output
                municipalities_count = 0
                last_output_time = time.time()
                
                while crawler_process.poll() is None:
                    try:
                        # Read output with timeout
                        output = crawler_process.stdout.readline()
                        current_time = time.time()
                        
                        if output:
                            last_output_time = current_time
                            add_log_message(output.strip(), 'info', 'crawler')
                            
                            # Parse for municipality count
                            if 'municipalities processed' in output.lower():
                                import re
                                match = re.search(r'(\d+)\s+municipalities?\s+processed', output.lower())
                                if match:
                                    municipalities_count = int(match.group(1))
                                    crawler_status['municipalities_processed'] = municipalities_count
                                
                                # Update progress based on municipalities processed
                                if municipalities_count > 0:
                                    base_progress = 30  # After crawling starts
                                    max_progress = 80   # Before saving
                                    expected_municipalities = {'test': 10, 'quick': 50, 'full': 290}.get(mode, 50)
                                    
                                    municipality_progress = min(50, (municipalities_count / expected_municipalities) * 50)
                                    crawler_status['progress'] = max(crawler_status['progress'], base_progress + municipality_progress)
                                    crawler_status['status'] = f'Processing municipalities... ({municipalities_count} processed)'
                                
                                # Emit real-time status update
                                socketio.emit('crawler_status_update', {
                                    'progress': crawler_status['progress'],
                                    'status': crawler_status['status'],
                                    'municipalities_processed': crawler_status['municipalities_processed']
                                })
                        else:
                            # No output, check if process is still alive
                            if current_time - last_output_time > 300:  # 5 minutes without output
                                add_log_message('No output for 5 minutes - checking process health', 'warning', 'system')
                                if crawler_process.poll() is not None:
                                    break
                            time.sleep(0.1)
                    
                    except Exception as e:
                        add_log_message(f'Error reading crawler output: {str(e)}', 'error', 'system')
                        break
                
                # Process finished - determine final status
                return_code = crawler_process.returncode
                
                # Stop monitoring
                stop_monitoring = True
                add_log_message('Real-time monitoring stopped', 'info', 'system')
                
                if return_code == 0:
                    crawler_status['running'] = False
                    crawler_status['progress'] = 100
                    crawler_status['status'] = 'Completed successfully'
                    crawler_status['success'] = True
                    add_log_message(f'Crawler completed successfully! Processed {municipalities_count} municipalities', 'success', 'system')
                else:
                    crawler_status['running'] = False
                    crawler_status['status'] = 'Failed'
                    crawler_status['success'] = False
                    crawler_status['error'] = f'Crawler failed with exit code {return_code}'
                    add_log_message(f'Crawler failed with exit code {return_code}', 'error', 'system')
                
                # Emit final status
                socketio.emit('crawler_finished', {
                    'success': crawler_status['success'],
                    'status': crawler_status['status'],
                    'municipalities_processed': municipalities_count,
                    'error': crawler_status.get('error')
                })
                
            except Exception as e:
                # Stop monitoring on error
                stop_monitoring = True
                
                crawler_status['running'] = False
                crawler_status['status'] = 'Error'
                crawler_status['success'] = False
                crawler_status['error'] = str(e)
                add_log_message(f'Error running crawler: {str(e)}', 'error', 'system')
                
                socketio.emit('crawler_finished', {
                    'success': False,
                    'status': 'Error',
                    'error': str(e)
                })
        
        # Start crawler in background thread
        crawler_thread = threading.Thread(target=run_crawler, daemon=True)
        crawler_thread.start()
        
        return jsonify({'success': True, 'message': 'Crawler started successfully'})
        
    except Exception as e:
        app.logger.error(f"Error starting crawler: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/phase1/stop-crawler', methods=['POST'])
def stop_crawler():
    """Stop the Phase 1 crawler"""
    global crawler_process, crawler_status
    
    try:
        if crawler_process and crawler_process.poll() is None:
            crawler_process.terminate()
            crawler_status['running'] = False
            crawler_status['status'] = 'Stopped by user'
            crawler_status['logs'].append({
                'message': 'Crawler stopped by user',
                'level': 'warning'
            })
            return jsonify({'success': True, 'message': 'Crawler stopped'})
        else:
            return jsonify({'error': 'No crawler running'})
            
    except Exception as e:
        app.logger.error(f"Error stopping crawler: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/phase1/crawler-status')
def get_crawler_status():
    """Get current crawler status"""
    global crawler_status
    
    # Clear logs after sending to prevent memory buildup
    current_status = crawler_status.copy()
    crawler_status['logs'] = []
    
    return jsonify(current_status)

def find_available_port(start_port=5001, max_attempts=10):
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    return None

@app.route('/api/phase1/debug-crawler-detection')
def debug_crawler_detection():
    """Debug endpoint to test crawler detection"""
    try:
        result = is_crawler_running()
        
        # Also check global variable
        global crawler_process
        global_result = crawler_process and crawler_process.poll() is None
        
        return jsonify({
            'is_crawler_running': result,
            'global_crawler_process': global_result,
            'crawler_process_exists': crawler_process is not None,
            'crawler_process_poll': crawler_process.poll() if crawler_process else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def monitor_pipeline_notifications():
    """Monitor pipeline notification file for real-time updates"""
    global stop_monitoring
    
    # Get the correct path to the output directory
    project_root = Path(__file__).parent.parent
    output_dir = project_root / 'data' / 'output'
    notification_file = output_dir / 'realtime_notifications.json'
    
    last_notification_time = None
    
    while not stop_monitoring:
        try:
            if notification_file.exists():
                # Check if file has been modified
                current_mtime = notification_file.stat().st_mtime
                
                if last_notification_time is None or current_mtime > last_notification_time:
                    last_notification_time = current_mtime
                    
                    # Read the notification
                    with open(notification_file, 'r', encoding='utf-8') as f:
                        notification = json.load(f)
                    
                    event_type = notification.get('event_type')
                    data = notification.get('data', {})
                    
                    if event_type == 'new_data':
                        # Emit new data found notification
                        socketio.emit('new_data_found', {
                            'municipality': data.get('municipality'),
                            'timtaxa_livsmedel': data.get('timtaxa_livsmedel'),
                            'debitering_livsmedel': data.get('debitering_livsmedel'),
                            'timtaxa_bygglov': data.get('timtaxa_bygglov'),
                            'status': data.get('status'),
                            'confidence': data.get('confidence'),
                            'source_url': data.get('source_url'),
                            'timestamp': notification.get('timestamp')
                        })
                        
                        logger.info(f"Real-time update: New data found for {data.get('municipality')}")
                    
                    elif event_type == 'progress_update':
                        # Emit progress update
                        socketio.emit('data_update', {
                            'total_municipalities': data.get('total_municipalities'),
                            'complete_municipalities': data.get('complete_municipalities'),
                            'partial_municipalities': data.get('partial_municipalities'),
                            'completion_rate': data.get('completion_rate'),
                            'municipalities_with_data': data.get('municipalities_with_data'),
                            'timestamp': notification.get('timestamp')
                        })
                        
                        logger.debug(f"Real-time progress update: {data.get('total_municipalities')} processed")
            
            time.sleep(1)  # Check every second for real-time updates
            
        except Exception as e:
            logger.debug(f"Error monitoring pipeline notifications: {e}")
            time.sleep(5)  # Wait longer on error

if __name__ == '__main__':
    port = find_available_port()
    if port is None:
        print("❌ Could not find an available port")
        sys.exit(1)
    
    print(f"🚀 Starting Phase 1 Web Interface on port {port}...")
    socketio.run(app, debug=True, host='0.0.0.0', port=port) 