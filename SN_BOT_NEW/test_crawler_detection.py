#!/usr/bin/env python3
"""
Test script to debug crawler detection
"""

import psutil
import sys
from pathlib import Path

# Add web interface to path
sys.path.insert(0, str(Path(__file__).parent / 'swedish_municipal_crawler' / 'web_interface'))

try:
    from phase1_app import is_crawler_running
    print('Crawler running:', is_crawler_running())
except ImportError as e:
    print(f'Import error: {e}')
    
    # Manual implementation for testing
    def test_is_crawler_running():
        """Test implementation of crawler detection"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if any(pattern in cmdline for pattern in [
                        'start_phase1_system.py',
                        'phase1_spider',
                        'run_phase1_crawler.py'
                    ]):
                        print(f'Found matching process: PID {proc.info["pid"]}: {cmdline}')
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return False
        except Exception as e:
            print(f'Error in detection: {e}')
            return False
    
    print('Manual test - Crawler running:', test_is_crawler_running())

# Let's also check what processes psutil sees
print('\nAll Python processes:')
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        if 'python' in proc.info['name'].lower():
            cmdline = ' '.join(proc.info['cmdline'] or [])
            print(f'PID {proc.info["pid"]}: {cmdline}')
            
            # Check if this would match our patterns
            if any(pattern in cmdline for pattern in [
                'start_phase1_system.py',
                'phase1_spider', 
                'run_phase1_crawler.py'
            ]):
                print(f'  ^^^ THIS WOULD MATCH!')
                
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        continue 