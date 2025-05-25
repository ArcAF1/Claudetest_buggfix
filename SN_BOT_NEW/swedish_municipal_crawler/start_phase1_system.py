#!/usr/bin/env python3
"""
Phase 1 System Starter
Complete deployment script for the Phase 1 Swedish Municipal Fee Crawler and Web Interface

This script provides a one-command solution to:
1. Set up the environment
2. Run the Phase 1 crawler
3. Launch the web interface
4. Provide comprehensive status monitoring

Usage:
    python start_phase1_system.py --help
    python start_phase1_system.py --quick-start
    python start_phase1_system.py --full-crawl
    python start_phase1_system.py --web-only
"""

import argparse
import sys
import os
import subprocess
import time
import webbrowser
import signal
from pathlib import Path
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

class Phase1SystemManager:
    """Manages the complete Phase 1 system deployment"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.web_interface_dir = self.project_root / 'web_interface'
        self.data_output_dir = self.project_root / 'data' / 'output'
        self.processes = []
        
    def print_banner(self):
        """Print system banner"""
        print("=" * 80)
        print("🎯 PHASE 1 SWEDISH MUNICIPAL FEE CRAWLER SYSTEM")
        print("=" * 80)
        print("Comprehensive solution for extracting and analyzing:")
        print("  • Timtaxan för livsmedelskontroll (Food control hourly rate)")
        print("  • Debiteringsmodell för livsmedelskontroll (Billing model)")
        print("  • Timtaxan för bygglov (Building permit hourly rate)")
        print("=" * 80)
        print()
    
    def check_system_requirements(self):
        """Check if system requirements are met"""
        logger.info("🔍 Checking system requirements...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            logger.error("❌ Python 3.8+ required")
            return False
        logger.info("✓ Python version OK")
        
        # Check required packages (package_name: import_name)
        required_packages = {
            'scrapy': 'scrapy',
            'flask': 'flask', 
            'pandas': 'pandas',
            'openpyxl': 'openpyxl',
            'camelot-py': 'camelot',
            'pdfplumber': 'pdfplumber',
            'aiohttp': 'aiohttp'
        }
        
        missing_packages = []
        for package_name, import_name in required_packages.items():
            try:
                __import__(import_name)
                logger.info(f"✓ {package_name} available")
            except ImportError:
                missing_packages.append(package_name)
                logger.warning(f"⚠️  {package_name} missing")
        
        if missing_packages:
            logger.error("❌ Missing required packages:")
            for package in missing_packages:
                logger.error(f"   - {package}")
            logger.info("Install with: pip install -r requirements.txt")
            return False
        
        logger.info("✅ All system requirements met")
        return True
    
    def setup_directories(self):
        """Setup required directories"""
        logger.info("📁 Setting up directories...")
        
        directories = [
            self.data_output_dir,
            self.project_root / 'data' / 'input',
            self.project_root / 'logs',
            self.project_root / 'data' / 'cache'
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"✓ {directory}")
        
        logger.info("✅ Directory structure ready")
    
    def check_existing_data(self):
        """Check for existing Phase 1 data"""
        logger.info("📊 Checking for existing Phase 1 data...")
        
        db_files = list(self.data_output_dir.glob('phase1_municipal_data_*.db'))
        stats_files = list(self.data_output_dir.glob('phase1_statistics_*.json'))
        
        if db_files:
            latest_db = max(db_files, key=lambda x: x.stat().st_mtime)
            mod_time = datetime.fromtimestamp(latest_db.stat().st_mtime)
            logger.info(f"✓ Found Phase 1 database: {latest_db.name}")
            logger.info(f"  Last modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
            return True
        else:
            logger.info("ℹ️  No existing Phase 1 data found")
            return False
    
    def run_crawler(self, test_mode=True, max_municipalities=None):
        """Run the Phase 1 crawler"""
        logger.info("🕷️  Starting Phase 1 crawler...")
        
        cmd = [sys.executable, 'run_phase1_crawler.py']
        
        if test_mode:
            cmd.append('--test-mode')
            logger.info("   Running in test mode with sample municipalities")
        else:
            # Use the comprehensive municipalities file for full crawl
            cmd.extend(['--municipalities-file', 'data/input/municipalities_full.csv'])
            logger.info("   Using comprehensive municipalities file (290 municipalities)")
        
        if max_municipalities:
            cmd.extend(['--max-municipalities', str(max_municipalities)])
            logger.info(f"   Limited to {max_municipalities} municipalities")
        
        cmd.extend(['--log-level', 'INFO'])
        
        try:
            logger.info(f"   Command: {' '.join(cmd)}")
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=False)
            
            if result.returncode == 0:
                logger.info("✅ Phase 1 crawler completed successfully")
                return True
            else:
                logger.error(f"❌ Phase 1 crawler failed with exit code {result.returncode}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error running crawler: {e}")
            return False
    
    def test_pipelines(self):
        """Test Phase 1 pipeline components"""
        logger.info("🧪 Testing Phase 1 pipeline components...")
        
        try:
            cmd = [sys.executable, 'run_phase1_crawler.py', '--test-pipelines']
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ Pipeline tests passed")
                return True
            else:
                logger.error("❌ Pipeline tests failed")
                logger.error(result.stderr)
                return False
                
        except Exception as e:
            logger.error(f"❌ Error testing pipelines: {e}")
            return False
    
    def start_web_interface(self, host='127.0.0.1', port=5001, debug=False, open_browser=True):
        """Start the Phase 1 web interface"""
        logger.info("🌐 Starting web interface with dynamic port detection...")
        web_env = os.environ.copy()
        web_env['PYTHONPATH'] = str(self.project_root)
        
        # Start the web process and capture output to get the actual port
        web_process = subprocess.Popen([
            sys.executable, 
            str(self.web_interface_dir / 'app.py')
        ], 
        cwd=str(self.web_interface_dir),
        env=web_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
        )
        
        # Read the first few lines to get the port information
        actual_port = None
        dashboard_url = None
        
        try:
            # Give the process a moment to start and output port info
            import time
            time.sleep(2)
            
            # Try to read port information from the output
            for _ in range(10):  # Try up to 10 lines
                line = web_process.stdout.readline()
                if line:
                    logger.info(f"Web server: {line.strip()}")
                    if "Found available port:" in line:
                        actual_port = int(line.split(":")[-1].strip())
                    elif "Dashboard will be available at:" in line:
                        dashboard_url = line.split("at:")[-1].strip()
                        break
                else:
                    break
            
            # If we couldn't parse the port, use default
            if not actual_port:
                actual_port = 5000  # fallback
            
            if not dashboard_url:
                dashboard_url = f"http://localhost:{actual_port}/phase1"
            
        except Exception as e:
            logger.warning(f"Could not parse port information: {e}")
            actual_port = 5000
            dashboard_url = f"http://localhost:{actual_port}/phase1"
        
        logger.info("✅ Web interface started!")
        logger.info(f"🌐 Dashboard available at: {dashboard_url}")
        logger.info("📊 Real-time monitoring enabled with Socket.IO")
        logger.info("🔄 Live updates for crawler progress and data discoveries")
        logger.info("\n" + "="*60)
        logger.info("PHASE 1 SYSTEM READY")
        logger.info("="*60)
        logger.info(f"• Web Dashboard: {dashboard_url}")
        logger.info("• Real-time Logs: Enabled")
        logger.info("• Live Data Updates: Enabled") 
        logger.info("• Export Functions: Available")
        logger.info("="*60)
        
        # Open browser if requested
        if open_browser:
            try:
                import webbrowser
                time.sleep(1)  # Give server a moment to fully start
                webbrowser.open(dashboard_url)
                logger.info("🌐 Browser opened automatically")
            except Exception as e:
                logger.info(f"🌐 Could not open browser automatically: {e}")
                logger.info(f"🌐 Please open manually: {dashboard_url}")
        
        self.processes.append(web_process)
        
        # Store the URL for later use
        self.dashboard_url = dashboard_url
        
        return True
    
    def show_system_status(self):
        """Show current system status"""
        logger.info("📊 System Status:")
        
        # Check data files
        db_files = list(self.data_output_dir.glob('phase1_municipal_data_*.db'))
        if db_files:
            latest_db = max(db_files, key=lambda x: x.stat().st_mtime)
            
            # Get basic stats from database
            try:
                import sqlite3
                conn = sqlite3.connect(latest_db)
                cursor = conn.cursor()
                
                cursor.execute('SELECT COUNT(*) FROM phase1_data')
                total = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM phase1_data WHERE status = "complete"')
                complete = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM phase1_data WHERE status = "partial"')
                partial = cursor.fetchone()[0]
                
                conn.close()
                
                logger.info(f"   📈 Total municipalities: {total}")
                
                # Fix division by zero error
                if total > 0:
                    logger.info(f"   ✅ Complete data: {complete} ({complete/total*100:.1f}%)")
                    logger.info(f"   ⚠️  Partial data: {partial} ({partial/total*100:.1f}%)")
                else:
                    logger.info(f"   ✅ Complete data: {complete} (0.0%)")
                    logger.info(f"   ⚠️  Partial data: {partial} (0.0%)")
                    logger.info("   ℹ️  No data found - database is empty")
                
            except Exception as e:
                logger.warning(f"   ⚠️  Could not read database: {e}")
        else:
            logger.info("   📊 No Phase 1 data available")
        
        # Check running processes
        active_processes = [p for p in self.processes if p.poll() is None]
        if active_processes:
            logger.info(f"   🔄 Active processes: {len(active_processes)}")
        else:
            logger.info("   💤 No active processes")
    
    def cleanup(self):
        """Cleanup running processes"""
        logger.info("🧹 Cleaning up...")
        
        for process in self.processes:
            if process.poll() is None:
                logger.info(f"   Terminating process {process.pid}")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.warning(f"   Force killing process {process.pid}")
                    process.kill()
        
        logger.info("✅ Cleanup completed")
    
    def quick_start(self):
        """Quick start with test data"""
        logger.info("🚀 Quick Start Mode")
        
        if not self.check_system_requirements():
            return False
        
        self.setup_directories()
        
        # Test pipelines first
        if not self.test_pipelines():
            logger.error("❌ Pipeline tests failed - aborting")
            return False
        
        # Run crawler with test data
        if not self.run_crawler(test_mode=True):
            logger.error("❌ Crawler failed - aborting")
            return False
        
        # Show status after crawling
        self.show_system_status()
        
        logger.info("🎉 Quick start completed successfully!")
        logger.info("   📊 Test data has been generated")
        logger.info("   🌐 To view results, run: python start_phase1_system.py --web-only")
        logger.info("   📁 Or check the generated files in data/output/")
        
        return True
    
    def full_crawl(self, max_municipalities=None):
        """Full crawl with real municipalities"""
        logger.info("🏭 Full Crawl Mode")
        
        if not self.check_system_requirements():
            return False
        
        self.setup_directories()
        
        # Check if user wants to proceed with full crawl
        if not max_municipalities:
            response = input("⚠️  Full crawl will process all municipalities. Continue? (y/N): ")
            if response.lower() != 'y':
                logger.info("❌ Full crawl cancelled by user")
                return False
        
        # Run crawler with real data
        if not self.run_crawler(test_mode=False, max_municipalities=max_municipalities):
            logger.error("❌ Crawler failed - aborting")
            return False
        
        # Show status after crawling
        self.show_system_status()
        
        logger.info("🎉 Full crawl completed successfully!")
        logger.info("   📊 Data has been saved to the output directory")
        logger.info("   🌐 To view results, run: python start_phase1_system.py --web-only")
        logger.info("   📁 Or check the generated files in data/output/")
        
        return True
    
    def web_only(self, host='127.0.0.1', port=5001, debug=False, open_browser=True):
        """Start only the web interface"""
        logger.info("🌐 Web Interface Only Mode")
        
        if not self.check_system_requirements():
            return False
        
        # Setup directories
        self.setup_directories()
        
        # Check for existing data (but don't require it)
        if not self.check_existing_data():
            logger.info("ℹ️  No existing Phase 1 data found - starting with empty interface")
            logger.info("   You can start crawling from the web interface")
        
        # Start web interface
        if not self.start_web_interface(host=host, port=port, debug=debug, open_browser=open_browser):
            logger.error("❌ Web interface failed to start")
            return False
        
        self.show_system_status()
        
        logger.info("🎉 Web interface started successfully!")
        logger.info(f"   URL: http://{host}:{port}")
        logger.info("   Press Ctrl+C to stop")
        
        return True

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\n🛑 Shutdown signal received...")
    if hasattr(signal_handler, 'manager'):
        signal_handler.manager.cleanup()
    print("👋 Phase 1 system stopped")
    sys.exit(0)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Phase 1 System Starter - Complete deployment solution',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start_phase1_system.py --quick-start
      Quick start with test data and web interface
      
  python start_phase1_system.py --full-crawl --max-municipalities 50
      Full crawl limited to 50 municipalities
      
  python start_phase1_system.py --web-only
      Start only the web interface (requires existing data)
      
  python start_phase1_system.py --web-only --host 0.0.0.0 --port 8080 --debug
      Start web interface on all interfaces with debug mode
        """
    )
    
    # Mode selection
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        '--quick-start',
        action='store_true',
        help='Quick start with test data (recommended for first use)'
    )
    mode_group.add_argument(
        '--full-crawl',
        action='store_true',
        help='Full crawl with real municipalities'
    )
    mode_group.add_argument(
        '--web-only',
        action='store_true',
        help='Start only the web interface (requires existing data)'
    )
    
    # Crawler options
    parser.add_argument(
        '--max-municipalities',
        type=int,
        help='Maximum number of municipalities to process (for testing)'
    )
    
    # Web interface options
    parser.add_argument(
        '--host',
        type=str,
        default='127.0.0.1',
        help='Web interface host (default: 127.0.0.1)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=5001,
        help='Web interface port (default: 5001)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode for web interface'
    )
    parser.add_argument(
        '--no-browser',
        action='store_true',
        help='Do not open browser automatically'
    )
    
    args = parser.parse_args()
    
    # Create system manager
    manager = Phase1SystemManager()
    signal_handler.manager = manager  # For cleanup on Ctrl+C
    
    # Setup signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Print banner
    manager.print_banner()
    
    try:
        success = False
        
        if args.quick_start:
            success = manager.quick_start()
            
        elif args.full_crawl:
            success = manager.full_crawl(max_municipalities=args.max_municipalities)
            
        elif args.web_only:
            success = manager.web_only(
                host=args.host, 
                port=args.port, 
                debug=args.debug,
                open_browser=not args.no_browser
            )
        
        if success:
            # Keep running until interrupted
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
        else:
            logger.error("❌ System startup failed")
            return 1
            
    except KeyboardInterrupt:
        pass
    finally:
        manager.cleanup()
    
    return 0

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code) 