#!/usr/bin/env python3
"""
Phase 1 Web Interface Startup Script
Launches the Flask web application for Phase 1 data visualization
"""

import argparse
import sys
import os
import socket
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_dependencies():
    """Check if required dependencies are available"""
    missing_deps = []
    
    try:
        import flask
    except ImportError:
        missing_deps.append('Flask')
    
    try:
        import pandas
    except ImportError:
        missing_deps.append('pandas')
    
    try:
        import openpyxl
    except ImportError:
        missing_deps.append('openpyxl')
    
    if missing_deps:
        print("Missing dependencies:")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("\nInstall with: pip install -r web_interface/requirements.txt")
        return False
    
    return True

def check_data_availability():
    """Check if Phase 1 data is available"""
    output_dir = Path('../data/output')
    if not output_dir.exists():
        output_dir = Path('data/output')
    
    db_files = list(output_dir.glob('phase1_municipal_data_*.db'))
    
    if not db_files:
        print("⚠️  No Phase 1 database files found!")
        print("   Run the Phase 1 crawler first to generate data:")
        print("   python run_phase1_crawler.py --test-mode")
        return False
    
    latest_db = max(db_files, key=lambda x: x.stat().st_mtime)
    print(f"✓ Found Phase 1 database: {latest_db}")
    return True

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

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Phase 1 Web Interface - View and analyze Phase 1 municipal data'
    )
    
    parser.add_argument(
        '--host',
        type=str,
        default='127.0.0.1',
        help='Host to bind to (default: 127.0.0.1)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=5001,
        help='Port to bind to (default: 5001)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Run in debug mode'
    )
    
    parser.add_argument(
        '--skip-checks',
        action='store_true',
        help='Skip dependency and data checks'
    )
    
    args = parser.parse_args()
    
    print("=== Phase 1 Web Interface ===")
    print("Starting Phase 1 Municipal Data Dashboard")
    print("=" * 40)
    
    # Check dependencies
    if not args.skip_checks:
        if not check_dependencies():
            return 1
        
        if not check_data_availability():
            print("\nYou can still start the web interface, but it will show 'No data found' until you run the crawler.")
            response = input("Continue anyway? (y/N): ")
            if response.lower() != 'y':
                return 1
    
    # Import and start the Flask app
    try:
        from phase1_app import app, socketio
        
        # Check if the requested port is available
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((args.host, args.port))
        except OSError:
            print(f"⚠️  Port {args.port} is already in use")
            available_port = find_available_port(args.port)
            if available_port:
                print(f"   Using port {available_port} instead")
                args.port = available_port
            else:
                print("❌ Could not find an available port")
                return 1
        
        print(f"\n🚀 Starting Phase 1 Web Interface...")
        print(f"   URL: http://{args.host}:{args.port}")
        print(f"   Debug mode: {'ON' if args.debug else 'OFF'}")
        print(f"   Real-time logging: ENABLED")
        print("\nPress Ctrl+C to stop the server")
        print("=" * 40)
        
        socketio.run(
            app,
            host=args.host,
            port=args.port,
            debug=args.debug
        )
        
    except KeyboardInterrupt:
        print("\n\n👋 Phase 1 Web Interface stopped")
        return 0
    except Exception as e:
        print(f"\n❌ Error starting web interface: {e}")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code) 