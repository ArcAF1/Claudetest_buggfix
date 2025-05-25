#!/usr/bin/env python3
"""
Simple web interface for monitoring the Swedish Municipal Crawler
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import json
import os
import glob
from datetime import datetime
from pathlib import Path
import subprocess
import threading
import time
import sqlite3
import socket

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables for crawler management
crawler_process = None
monitoring_thread = None
stop_monitoring = False

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('dashboard.html')

@app.route('/phase1')
def phase1_dashboard():
    """Phase 1 dashboard"""
    return render_template('phase1_dashboard.html')

@app.route('/api/crawl-stats')
def crawl_stats():
    """Get latest crawl statistics"""
    try:
        # Find latest statistics file
        stats_files = glob.glob('data/output/crawl_statistics_*.json')
        if not stats_files:
            return jsonify({'error': 'No crawl statistics found'})
        
        latest_file = max(stats_files, key=os.path.getctime)
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            stats = json.load(f)
        
        return jsonify(stats)
    
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/recent-crawls')
def recent_crawls():
    """Get list of recent crawl files"""
    try:
        output_files = []
        
        # Get JSON files
        json_files = glob.glob('data/output/swedish_municipal_fees_*.json')
        for file_path in json_files:
            file_info = {
                'type': 'json',
                'filename': os.path.basename(file_path),
                'size': os.path.getsize(file_path),
                'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
            }
            output_files.append(file_info)
        
        # Get CSV files
        csv_files = glob.glob('data/output/swedish_municipal_fees_*.csv')
        for file_path in csv_files:
            file_info = {
                'type': 'csv',
                'filename': os.path.basename(file_path),
                'size': os.path.getsize(file_path),
                'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
            }
            output_files.append(file_info)
        
        # Sort by modification time
        output_files.sort(key=lambda x: x['modified'], reverse=True)
        
        return jsonify(output_files[:10])  # Return latest 10 files
    
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/failed-municipalities')
def failed_municipalities():
    """Get failed municipalities"""
    try:
        failed_file = 'data/output/failed_municipalities.json'
        if not os.path.exists(failed_file):
            return jsonify([])
        
        with open(failed_file, 'r', encoding='utf-8') as f:
            failed = json.load(f)
        
        return jsonify(failed)
    
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/logs')
def get_logs():
    """Get recent log entries"""
    try:
        log_file = 'data/output/crawler.log'
        if not os.path.exists(log_file):
            return jsonify([])
        
        # Read last 100 lines
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        recent_lines = lines[-100:] if len(lines) > 100 else lines
        
        return jsonify([line.strip() for line in recent_lines])
    
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/pause_crawler', methods=['POST'])
def pause_crawler():
    """Pause the currently running crawler"""
    global crawler_process, stop_monitoring
    
    try:
        if crawler_process and crawler_process.poll() is None:
            # Send SIGTERM to gracefully stop the crawler
            import signal
            crawler_process.send_signal(signal.SIGTERM)
            
            # Stop monitoring
            stop_monitoring = True
            
            # Wait a bit for graceful shutdown
            import time
            time.sleep(2)
            
            # If still running, force kill
            if crawler_process.poll() is None:
                crawler_process.kill()
            
            crawler_process = None
            
            socketio.emit('crawler_paused', {
                'message': 'Crawler paused successfully',
                'timestamp': datetime.now().isoformat()
            })
            
            return jsonify({
                'success': True,
                'message': 'Crawler paused successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No crawler is currently running'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error pausing crawler: {str(e)}'
        })

@app.route('/api/export_current_results', methods=['GET'])
def export_current_results():
    """Export current results from the latest database"""
    try:
        # Find the most recent database file - use correct project structure
        project_root = Path(__file__).parent.parent
        output_dir = project_root / 'data' / 'output'
        db_files = list(output_dir.glob('phase1_municipal_data_*.db'))
        
        if not db_files:
            return jsonify({
                'success': False,
                'message': 'No database files found'
            })
        
        # Get the most recent database
        latest_db = max(db_files, key=lambda x: x.stat().st_mtime)
        
        # Export to CSV
        import sqlite3
        import csv
        from datetime import datetime
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        export_filename = f'phase1_export_{timestamp}.csv'
        export_path = output_dir / export_filename
        
        conn = sqlite3.connect(latest_db)
        cursor = conn.cursor()
        
        # Get all data
        cursor.execute("SELECT * FROM phase1_data ORDER BY municipality")
        rows = cursor.fetchall()
        
        # Get column names
        cursor.execute("PRAGMA table_info(phase1_data)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Write to CSV
        with open(export_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(columns)
            writer.writerows(rows)
        
        conn.close()
        
        # Get statistics
        total_municipalities = len(rows)
        complete_municipalities = len([row for row in rows if row[columns.index('status')] == 'complete'])
        
        return jsonify({
            'success': True,
            'message': f'Results exported successfully',
            'filename': export_filename,
            'total_municipalities': total_municipalities,
            'complete_municipalities': complete_municipalities,
            'export_path': str(export_path)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error exporting results: {str(e)}'
        })

@app.route('/api/get_current_stats', methods=['GET'])
def get_current_stats():
    """Get current crawling statistics from the latest database"""
    try:
        # Find the most recent database file - use correct project structure
        project_root = Path(__file__).parent.parent
        output_dir = project_root / 'data' / 'output'
        db_files = list(output_dir.glob('phase1_municipal_data_*.db'))
        
        if not db_files:
            return jsonify({
                'success': True,
                'stats': {
                    'total_municipalities': 0,
                    'complete_municipalities': 0,
                    'partial_municipalities': 0,
                    'municipalities_with_data': 0,
                    'completion_rate': 0.0
                }
            })
        
        # Get the most recent database
        latest_db = max(db_files, key=lambda x: x.stat().st_mtime)
        
        import sqlite3
        conn = sqlite3.connect(latest_db)
        cursor = conn.cursor()
        
        # Get statistics
        cursor.execute("SELECT COUNT(*) FROM phase1_data")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM phase1_data WHERE status = 'complete'")
        complete = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM phase1_data WHERE status = 'partial'")
        partial = cursor.fetchone()[0]
        
        municipalities_with_data = complete + partial
        completion_rate = (complete / total * 100) if total > 0 else 0.0
        
        conn.close()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_municipalities': total,
                'complete_municipalities': complete,
                'partial_municipalities': partial,
                'municipalities_with_data': municipalities_with_data,
                'completion_rate': round(completion_rate, 1)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting stats: {str(e)}'
        })

@app.route('/api/phase1/overview')
def phase1_overview():
    """Get Phase 1 overview data"""
    try:
        # Find the most recent database file - use correct project structure
        project_root = Path(__file__).parent.parent
        output_dir = project_root / 'data' / 'output'
        db_files = list(output_dir.glob('phase1_municipal_data_*.db'))
        
        if not db_files:
            return jsonify({
                'total_municipalities': 0,
                'complete_data': 0,
                'partial_data': 0,
                'completion_rate': 0.0,
                'partial_rate': 0.0,
                'latest_extraction': None,
                'coverage': {
                    'timtaxa_livsmedel': {'count': 0, 'percentage': 0},
                    'debitering_livsmedel': {'count': 0, 'percentage': 0},
                    'timtaxa_bygglov': {'count': 0, 'percentage': 0}
                }
            })
        
        # Get the most recent database
        latest_db = max(db_files, key=lambda x: x.stat().st_mtime)
        
        conn = sqlite3.connect(latest_db)
        cursor = conn.cursor()
        
        # Get overview statistics
        cursor.execute("SELECT COUNT(*) FROM phase1_data")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM phase1_data WHERE status = 'complete'")
        complete = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM phase1_data WHERE status = 'partial'")
        partial = cursor.fetchone()[0]
        
        # Get field coverage
        cursor.execute("SELECT COUNT(*) FROM phase1_data WHERE timtaxa_livsmedel IS NOT NULL AND timtaxa_livsmedel != ''")
        livsmedel_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM phase1_data WHERE debitering_livsmedel IS NOT NULL AND debitering_livsmedel != ''")
        debitering_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM phase1_data WHERE timtaxa_bygglov IS NOT NULL AND timtaxa_bygglov != ''")
        bygglov_count = cursor.fetchone()[0]
        
        # Get latest extraction date
        cursor.execute("SELECT MAX(extraction_date) FROM phase1_data")
        latest_extraction = cursor.fetchone()[0]
        
        conn.close()
        
        completion_rate = (complete / total * 100) if total > 0 else 0.0
        partial_rate = (partial / total * 100) if total > 0 else 0.0
        
        return jsonify({
            'total_municipalities': total,
            'complete_data': complete,
            'partial_data': partial,
            'completion_rate': round(completion_rate, 1),
            'partial_rate': round(partial_rate, 1),
            'latest_extraction': latest_extraction,
            'coverage': {
                'timtaxa_livsmedel': {
                    'count': livsmedel_count,
                    'percentage': round((livsmedel_count / total * 100) if total > 0 else 0, 1)
                },
                'debitering_livsmedel': {
                    'count': debitering_count,
                    'percentage': round((debitering_count / total * 100) if total > 0 else 0, 1)
                },
                'timtaxa_bygglov': {
                    'count': bygglov_count,
                    'percentage': round((bygglov_count / total * 100) if total > 0 else 0, 1)
                }
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/phase1/municipalities')
def phase1_municipalities():
    """Get Phase 1 municipalities data"""
    try:
        # Find the most recent database file - use correct project structure
        project_root = Path(__file__).parent.parent
        output_dir = project_root / 'data' / 'output'
        db_files = list(output_dir.glob('phase1_municipal_data_*.db'))
        
        if not db_files:
            return jsonify([])
        
        # Get the most recent database
        latest_db = max(db_files, key=lambda x: x.stat().st_mtime)
        
        conn = sqlite3.connect(latest_db)
        cursor = conn.cursor()
        
        # Get status filter
        status_filter = request.args.get('status')
        
        if status_filter:
            cursor.execute("SELECT * FROM phase1_data WHERE status = ? ORDER BY municipality", (status_filter,))
        else:
            cursor.execute("SELECT * FROM phase1_data ORDER BY municipality")
        
        rows = cursor.fetchall()
        
        # Get column names
        cursor.execute("PRAGMA table_info(phase1_data)")
        columns = [row[1] for row in cursor.fetchall()]
        
        conn.close()
        
        # Convert to list of dictionaries
        municipalities = []
        for row in rows:
            municipality = dict(zip(columns, row))
            municipalities.append(municipality)
        
        return jsonify(municipalities)
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/phase1/start-crawler', methods=['POST'])
def start_phase1_crawler():
    """Start the Phase 1 crawler"""
    global crawler_process, monitoring_thread, stop_monitoring
    
    try:
        if crawler_process and crawler_process.poll() is None:
            return jsonify({
                'success': False,
                'error': 'Crawler is already running'
            })
        
        data = request.get_json()
        mode = data.get('mode', 'test')
        
        # Map mode to max municipalities
        mode_mapping = {
            'test': 10,
            'quick': 50,
            'full': None  # All municipalities
        }
        
        max_municipalities = mode_mapping.get(mode, 10)
        
        # Build command - run from parent directory where run_phase1_crawler.py is located
        cmd = ['python', 'run_phase1_crawler.py']
        if max_municipalities:
            cmd.extend(['--max-municipalities', str(max_municipalities)])
        cmd.extend(['--log-level', 'INFO'])
        
        # Get the parent directory (main project directory)
        project_root = Path(__file__).parent.parent
        
        # Start crawler process from the correct directory
        crawler_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
            cwd=str(project_root)  # Run from main project directory
        )
        
        # Start monitoring thread
        stop_monitoring = False
        monitoring_thread = threading.Thread(target=monitor_crawler_output)
        monitoring_thread.daemon = True
        monitoring_thread.start()
        
        # Start database monitoring thread
        db_monitoring_thread = threading.Thread(target=monitor_database_changes)
        db_monitoring_thread.daemon = True
        db_monitoring_thread.start()
        
        return jsonify({
            'success': True,
            'message': f'Crawler started in {mode} mode'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/phase1/comparison')
def phase1_comparison():
    """Get Phase 1 comparison data for charts"""
    try:
        # Find the most recent database file
        project_root = Path(__file__).parent.parent
        output_dir = project_root / 'data' / 'output'
        db_files = list(output_dir.glob('phase1_municipal_data_*.db'))
        
        if not db_files:
            return jsonify({
                'municipalities': [],
                'timtaxa_livsmedel': [],
                'timtaxa_bygglov': [],
                'debitering_livsmedel': [],
                'top_livsmedel': {'municipalities': [], 'values': []},
                'top_bygglov': {'municipalities': [], 'values': []}
            })
        
        # Get the most recent database
        latest_db = max(db_files, key=lambda x: x.stat().st_mtime)
        
        conn = sqlite3.connect(latest_db)
        cursor = conn.cursor()
        
        # Get municipalities with timtaxa data for comparison
        cursor.execute("""
            SELECT municipality, timtaxa_livsmedel, timtaxa_bygglov, debitering_livsmedel 
            FROM phase1_data 
            WHERE (timtaxa_livsmedel IS NOT NULL AND timtaxa_livsmedel != '') 
               OR (timtaxa_bygglov IS NOT NULL AND timtaxa_bygglov != '')
            ORDER BY municipality
        """)
        
        rows = cursor.fetchall()
        
        municipalities = []
        timtaxa_livsmedel = []
        timtaxa_bygglov = []
        debitering_livsmedel = []
        
        for row in rows:
            municipalities.append(row[0])
            timtaxa_livsmedel.append(row[1] if row[1] else 0)
            timtaxa_bygglov.append(row[2] if row[2] else 0)
            debitering_livsmedel.append(row[3] if row[3] else '')
        
        # Get top 10 highest timtaxa livsmedel
        cursor.execute("""
            SELECT municipality, timtaxa_livsmedel 
            FROM phase1_data 
            WHERE timtaxa_livsmedel IS NOT NULL AND timtaxa_livsmedel != ''
            ORDER BY CAST(timtaxa_livsmedel AS INTEGER) DESC 
            LIMIT 10
        """)
        top_livsmedel_rows = cursor.fetchall()
        
        # Get top 10 highest timtaxa bygglov
        cursor.execute("""
            SELECT municipality, timtaxa_bygglov 
            FROM phase1_data 
            WHERE timtaxa_bygglov IS NOT NULL AND timtaxa_bygglov != ''
            ORDER BY CAST(timtaxa_bygglov AS INTEGER) DESC 
            LIMIT 10
        """)
        top_bygglov_rows = cursor.fetchall()
        
        conn.close()
        
        return jsonify({
            'municipalities': municipalities,
            'timtaxa_livsmedel': timtaxa_livsmedel,
            'timtaxa_bygglov': timtaxa_bygglov,
            'debitering_livsmedel': debitering_livsmedel,
            'top_livsmedel': {
                'municipalities': [row[0] for row in top_livsmedel_rows],
                'values': [row[1] for row in top_livsmedel_rows]
            },
            'top_bygglov': {
                'municipalities': [row[0] for row in top_bygglov_rows],
                'values': [row[1] for row in top_bygglov_rows]
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/phase1/missing-data')
def phase1_missing_data():
    """Get Phase 1 missing data analysis"""
    try:
        # Find the most recent database file
        project_root = Path(__file__).parent.parent
        output_dir = project_root / 'data' / 'output'
        db_files = list(output_dir.glob('phase1_municipal_data_*.db'))
        
        if not db_files:
            return jsonify({
                'timtaxa_livsmedel': [],
                'debitering_livsmedel': [],
                'timtaxa_bygglov': [],
                'all_fields': []
            })
        
        # Get the most recent database
        latest_db = max(db_files, key=lambda x: x.stat().st_mtime)
        
        conn = sqlite3.connect(latest_db)
        cursor = conn.cursor()
        
        # Get municipalities missing timtaxa_livsmedel
        cursor.execute("""
            SELECT municipality, source_url, source_type 
            FROM phase1_data 
            WHERE timtaxa_livsmedel IS NULL OR timtaxa_livsmedel = ''
            ORDER BY municipality
        """)
        missing_livsmedel = [{'municipality': row[0], 'source_url': row[1], 'source_type': row[2]} for row in cursor.fetchall()]
        
        # Get municipalities missing debitering_livsmedel
        cursor.execute("""
            SELECT municipality, source_url, source_type 
            FROM phase1_data 
            WHERE debitering_livsmedel IS NULL OR debitering_livsmedel = ''
            ORDER BY municipality
        """)
        missing_debitering = [{'municipality': row[0], 'source_url': row[1], 'source_type': row[2]} for row in cursor.fetchall()]
        
        # Get municipalities missing timtaxa_bygglov
        cursor.execute("""
            SELECT municipality, source_url, source_type 
            FROM phase1_data 
            WHERE timtaxa_bygglov IS NULL OR timtaxa_bygglov = ''
            ORDER BY municipality
        """)
        missing_bygglov = [{'municipality': row[0], 'source_url': row[1], 'source_type': row[2]} for row in cursor.fetchall()]
        
        # Get municipalities missing all fields
        cursor.execute("""
            SELECT municipality, source_url, source_type 
            FROM phase1_data 
            WHERE (timtaxa_livsmedel IS NULL OR timtaxa_livsmedel = '')
              AND (debitering_livsmedel IS NULL OR debitering_livsmedel = '')
              AND (timtaxa_bygglov IS NULL OR timtaxa_bygglov = '')
            ORDER BY municipality
        """)
        missing_all = [{'municipality': row[0], 'source_url': row[1], 'source_type': row[2]} for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'timtaxa_livsmedel': missing_livsmedel,
            'debitering_livsmedel': missing_debitering,
            'timtaxa_bygglov': missing_bygglov,
            'all_fields': missing_all
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

def monitor_crawler_output():
    """Monitor crawler output and emit real-time logs"""
    global crawler_process, stop_monitoring
    
    if not crawler_process:
        return
    
    try:
        for line in iter(crawler_process.stdout.readline, ''):
            if stop_monitoring:
                break
            
            if line.strip():
                # Parse log line and emit to clients
                log_entry = parse_log_line(line.strip())
                socketio.emit('crawler_log', log_entry)
        
        # Wait for process to complete
        crawler_process.wait()
        
        # Emit completion status
        if crawler_process.returncode == 0:
            socketio.emit('crawler_finished', {
                'success': True,
                'message': 'Crawler completed successfully'
            })
        else:
            socketio.emit('crawler_finished', {
                'success': False,
                'error': f'Crawler failed with exit code {crawler_process.returncode}'
            })
            
    except Exception as e:
        socketio.emit('crawler_finished', {
            'success': False,
            'error': str(e)
        })

def monitor_database_changes():
    """Monitor database for new data and emit real-time updates"""
    global stop_monitoring
    
    last_count = 0
    last_complete_count = 0
    
    # Get the correct path to the output directory
    project_root = Path(__file__).parent.parent
    output_dir = project_root / 'data' / 'output'
    
    while not stop_monitoring:
        try:
            # Find the most recent database file
            db_files = list(output_dir.glob('phase1_municipal_data_*.db'))
            
            if db_files:
                latest_db = max(db_files, key=lambda x: x.stat().st_mtime)
                
                conn = sqlite3.connect(latest_db)
                cursor = conn.cursor()
                
                # Get current counts
                cursor.execute("SELECT COUNT(*) FROM phase1_data")
                current_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM phase1_data WHERE status = 'complete'")
                current_complete_count = cursor.fetchone()[0]
                
                conn.close()
                
                # Emit updates if counts changed
                if current_count != last_count or current_complete_count != last_complete_count:
                    socketio.emit('data_update', {
                        'total_municipalities': current_count,
                        'complete_municipalities': current_complete_count,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    last_count = current_count
                    last_complete_count = current_complete_count
            
            time.sleep(5)  # Check every 5 seconds
            
        except Exception as e:
            print(f"Error monitoring database: {e}")
            time.sleep(10)

def parse_log_line(line):
    """Parse a log line and extract relevant information"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    
    # Determine log level and source
    level = 'info'
    source = 'crawler'
    message = line
    
    if '[SUCCESS]' in line:
        level = 'success'
    elif '[ERROR]' in line:
        level = 'error'
    elif '[WARNING]' in line:
        level = 'warning'
    elif '[INFO]' in line:
        level = 'info'
    elif '[DEBUG]' in line:
        level = 'debug'
    
    if '[system]' in line:
        source = 'system'
    elif '[web]' in line:
        source = 'web'
    
    # Clean up the message
    message = line.replace('[SUCCESS]', '').replace('[ERROR]', '').replace('[WARNING]', '').replace('[INFO]', '').replace('[DEBUG]', '')
    message = message.replace('[crawler]', '').replace('[system]', '').replace('[web]', '').strip()
    
    return {
        'timestamp': timestamp,
        'level': level,
        'source': source,
        'message': message
    }

def find_available_port(start_port=5000, max_attempts=10):
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    
    # If no port found in range, let the system choose
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('localhost', 0))
        return s.getsockname()[1]

if __name__ == '__main__':
    import os
    
    # Try to get port from environment, otherwise find available port
    if 'PORT' in os.environ:
        port = int(os.environ['PORT'])
        print(f"🌐 Using port from environment: {port}")
    else:
        port = find_available_port()
        print(f"🌐 Found available port: {port}")
    
    print(f"🚀 Starting web interface on http://localhost:{port}")
    print(f"📊 Dashboard will be available at: http://localhost:{port}/phase1")
    
    socketio.run(app, debug=True, host='0.0.0.0', port=port) 