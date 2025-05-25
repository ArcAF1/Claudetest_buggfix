#!/usr/bin/env python3
"""
Port Conflict Resolver for Swedish Municipal Crawler
Helps resolve common port conflicts, especially on macOS with AirPlay Receiver
"""

import subprocess
import sys
import os

def check_port_usage(port):
    """Check what's using a specific port"""
    try:
        result = subprocess.run(['lsof', '-i', f':{port}'], 
                              capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            print(f"🔍 Port {port} is being used by:")
            print(result.stdout)
            return True
        else:
            print(f"✅ Port {port} is available")
            return False
    except FileNotFoundError:
        print("⚠️  lsof command not found - cannot check port usage")
        return False

def disable_airplay_instructions():
    """Show instructions to disable AirPlay Receiver on macOS"""
    print("\n" + "="*60)
    print("🍎 MACOS AIRPLAY RECEIVER CONFLICT DETECTED")
    print("="*60)
    print("To disable AirPlay Receiver and free up port 5000:")
    print("")
    print("1. Open System Preferences/Settings")
    print("2. Go to 'General' → 'AirDrop & Handoff'")
    print("3. Turn OFF 'AirPlay Receiver'")
    print("")
    print("Alternative: The crawler now uses port 5001 by default")
    print("="*60)

def main():
    print("🔧 Port Conflict Resolver for Swedish Municipal Crawler")
    print("="*60)
    print("ℹ️  NOTE: The crawler now uses DYNAMIC PORT DETECTION!")
    print("   It automatically finds an available port starting from 5000")
    print("="*60)
    
    # Check common ports
    ports_to_check = [5000, 5001, 5002, 5003, 5004]
    
    available_ports = []
    
    for port in ports_to_check:
        print(f"\n📡 Checking port {port}...")
        port_in_use = check_port_usage(port)
        
        if not port_in_use:
            available_ports.append(port)
        
        if port == 5000 and port_in_use:
            # Check if it's AirPlay Receiver
            try:
                result = subprocess.run(['lsof', '-i', ':5000'], 
                                      capture_output=True, text=True)
                if 'ControlCe' in result.stdout or 'AirPlay' in result.stdout:
                    disable_airplay_instructions()
            except:
                pass
    
    print(f"\n✅ Available ports found: {available_ports}")
    print(f"🔄 The crawler will automatically use the first available port")
    print(f"🌐 No manual configuration needed!")
    
    if available_ports:
        print(f"\n🎯 Expected dashboard URL: http://localhost:{available_ports[0]}/phase1")
    
    print("\n💡 Dynamic Port Detection Benefits:")
    print("  • No more port conflicts")
    print("  • Works on any system configuration") 
    print("  • Automatically avoids AirPlay Receiver")
    print("  • No manual port configuration needed")

if __name__ == '__main__':
    main() 