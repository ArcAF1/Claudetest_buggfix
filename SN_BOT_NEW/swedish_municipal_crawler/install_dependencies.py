#!/usr/bin/env python3
"""
Phase 1 System - Dependency Installer
Installs all required dependencies for the Phase 1 Swedish Municipal Fee Crawler

Usage:
    python install_dependencies.py
"""

import subprocess
import sys
import os
from pathlib import Path

def print_banner():
    """Print installer banner"""
    print("=" * 70)
    print("🔧 PHASE 1 SYSTEM - DEPENDENCY INSTALLER")
    print("=" * 70)
    print("Installing all required packages for the Phase 1 system...")
    print()

def check_pip():
    """Check if pip is available"""
    try:
        subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                      capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError:
        print("❌ ERROR: pip is not available")
        print("   Please install pip first")
        return False

def install_requirements():
    """Install from requirements.txt"""
    requirements_file = Path(__file__).parent / 'requirements.txt'
    
    if not requirements_file.exists():
        print("❌ ERROR: requirements.txt not found!")
        return False
    
    print("📦 Installing packages from requirements.txt...")
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', 
            '-r', str(requirements_file),
            '--upgrade'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Requirements installed successfully")
            return True
        else:
            print("⚠️  Some packages may have failed:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ ERROR installing requirements: {e}")
        return False

def install_critical_packages():
    """Install critical packages individually"""
    critical_packages = [
        'aiohttp>=3.8.0',
        'asyncio-throttle>=1.0.0', 
        'nest-asyncio>=1.5.0',
        'camelot-py[cv]>=0.10.1',
        'scrapy>=2.8.0',
        'flask>=3.0.0',
        'pandas>=1.5.0',
        'openpyxl>=3.1.0',
        'pdfplumber>=0.9.0'
    ]
    
    print("🔧 Installing critical packages...")
    
    for package in critical_packages:
        print(f"   Installing {package.split('>=')[0]}...")
        try:
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', 
                package, '--quiet'
            ], capture_output=True)
            
            if result.returncode == 0:
                print(f"   ✅ {package.split('>=')[0]} installed")
            else:
                print(f"   ⚠️  {package.split('>=')[0]} may have issues")
                
        except Exception as e:
            print(f"   ❌ Failed to install {package}: {e}")

def verify_installation():
    """Verify that key packages can be imported"""
    print("🧪 Verifying installation...")
    
    test_imports = {
        'scrapy': 'scrapy',
        'flask': 'flask',
        'pandas': 'pandas', 
        'openpyxl': 'openpyxl',
        'camelot': 'camelot-py',
        'pdfplumber': 'pdfplumber',
        'aiohttp': 'aiohttp'
    }
    
    success_count = 0
    total_count = len(test_imports)
    
    for import_name, package_name in test_imports.items():
        try:
            __import__(import_name)
            print(f"   ✅ {package_name}")
            success_count += 1
        except ImportError:
            print(f"   ❌ {package_name} - import failed")
    
    print()
    print(f"📊 Verification Results: {success_count}/{total_count} packages working")
    
    if success_count == total_count:
        print("🎉 All packages installed successfully!")
        return True
    elif success_count >= total_count * 0.8:  # 80% success rate
        print("⚠️  Most packages working - system should function")
        return True
    else:
        print("❌ Too many packages failed - system may not work properly")
        return False

def main():
    """Main installer function"""
    print_banner()
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ ERROR: Python 3.8+ required")
        print(f"   Current version: {sys.version}")
        print("   Please upgrade Python first")
        return 1
    
    print(f"✅ Python version OK: {sys.version.split()[0]}")
    print()
    
    # Check pip
    if not check_pip():
        return 1
    
    print("✅ pip is available")
    print()
    
    # Install requirements
    requirements_success = install_requirements()
    print()
    
    # Install critical packages individually
    install_critical_packages()
    print()
    
    # Verify installation
    verification_success = verify_installation()
    print()
    
    if verification_success:
        print("🎉 Installation completed successfully!")
        print()
        print("🚀 You can now run the Phase 1 system:")
        print("   python start_phase1_system.py --quick-start")
        print()
        print("   Or double-click: START_PHASE1.command")
        return 0
    else:
        print("⚠️  Installation completed with some issues")
        print()
        print("🔧 Try running manually:")
        print("   pip install -r requirements.txt")
        print("   pip install aiohttp camelot-py[cv] scrapy flask pandas")
        return 1

if __name__ == '__main__':
    exit_code = main()
    
    # Keep window open on Windows
    if os.name == 'nt':
        input("\nPress Enter to close...")
    
    sys.exit(exit_code) 