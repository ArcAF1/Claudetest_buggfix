#!/usr/bin/env python3
"""
Test the fixed crawler detection logic
"""

import psutil

def test_is_crawler_running():
    """Test the fixed crawler detection"""
    print("Testing fixed crawler detection...")
    found_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline'] or [])
            
            print(f"Checking process: {cmdline}")
            
            # Check for actual crawler processes, but exclude web-only mode
            if 'start_phase1_system.py' in cmdline:
                print(f"  Found start_phase1_system.py process")
                # Only consider it a crawler if it's NOT in web-only mode
                if '--web-only' not in cmdline:
                    print(f"  -> This is a CRAWLER (no --web-only)")
                    found_processes.append(f"PID {proc.info['pid']}: {cmdline}")
                else:
                    print(f"  -> This is WEB INTERFACE (has --web-only) - EXCLUDED")
            
            # Check for spider processes
            elif 'phase1_spider' in cmdline:
                print(f"  -> This is a SPIDER process")
                found_processes.append(f"PID {proc.info['pid']}: {cmdline}")
            
            # Check for direct crawler processes
            elif 'run_phase1_crawler.py' in cmdline:
                print(f"  -> This is a CRAWLER SCRIPT")
                found_processes.append(f"PID {proc.info['pid']}: {cmdline}")
                
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    print(f"\nResult: Found {len(found_processes)} crawler processes")
    for proc_info in found_processes:
        print(f"  - {proc_info}")
    
    return len(found_processes) > 0

if __name__ == "__main__":
    result = test_is_crawler_running()
    print(f"\nCrawler running: {result}") 