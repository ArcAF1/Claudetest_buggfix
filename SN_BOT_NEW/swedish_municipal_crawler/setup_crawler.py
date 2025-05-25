#!/usr/bin/env python3
"""
Setup script for Swedish Municipal Crawler with enhanced PDF extraction
Installs system dependencies and configures the environment
"""

import os
import sys
import subprocess
import platform
import logging

def setup_logging():
    """Setup logging for the setup process"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [SETUP] %(levelname)s: %(message)s'
    )
    return logging.getLogger(__name__)

def run_command(command, description):
    """Run a system command with error handling"""
    logger = logging.getLogger(__name__)
    logger.info(f"Running: {description}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        logger.info(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"✗ {description} failed: {e.stderr}")
        return False

def install_system_dependencies():
    """Install system dependencies based on the operating system"""
    logger = logging.getLogger(__name__)
    system = platform.system().lower()
    
    logger.info(f"Detected operating system: {system}")
    
    if system == "darwin":  # macOS
        logger.info("Installing macOS dependencies...")
        
        # Check if Homebrew is installed
        if not run_command("which brew", "Checking for Homebrew"):
            logger.error("Homebrew not found. Please install Homebrew first:")
            logger.error("Visit: https://brew.sh/")
            return False
        
        # Install system dependencies
        dependencies = [
            ("brew install ghostscript", "Installing Ghostscript"),
            ("brew install poppler", "Installing Poppler (for PDF processing)"),
            ("brew install tesseract", "Installing Tesseract OCR"),
            ("brew install redis", "Installing Redis"),
        ]
        
        for command, description in dependencies:
            if not run_command(command, description):
                logger.warning(f"Failed to install: {description}")
    
    elif system == "linux":
        logger.info("Installing Linux dependencies...")
        
        # Detect Linux distribution
        try:
            with open('/etc/os-release', 'r') as f:
                os_info = f.read().lower()
        except FileNotFoundError:
            os_info = ""
        
        if "ubuntu" in os_info or "debian" in os_info:
            # Ubuntu/Debian
            dependencies = [
                ("sudo apt-get update", "Updating package list"),
                ("sudo apt-get install -y ghostscript", "Installing Ghostscript"),
                ("sudo apt-get install -y poppler-utils", "Installing Poppler utilities"),
                ("sudo apt-get install -y tesseract-ocr", "Installing Tesseract OCR"),
                ("sudo apt-get install -y redis-server", "Installing Redis"),
                ("sudo apt-get install -y python3-tk", "Installing Tkinter"),
                ("sudo apt-get install -y libgl1-mesa-glx", "Installing OpenGL libraries"),
            ]
        elif "centos" in os_info or "rhel" in os_info or "fedora" in os_info:
            # CentOS/RHEL/Fedora
            dependencies = [
                ("sudo yum update -y", "Updating package list"),
                ("sudo yum install -y ghostscript", "Installing Ghostscript"),
                ("sudo yum install -y poppler-utils", "Installing Poppler utilities"),
                ("sudo yum install -y tesseract", "Installing Tesseract OCR"),
                ("sudo yum install -y redis", "Installing Redis"),
                ("sudo yum install -y tkinter", "Installing Tkinter"),
            ]
        else:
            logger.warning("Unknown Linux distribution. Please install dependencies manually:")
            logger.warning("- ghostscript")
            logger.warning("- poppler-utils")
            logger.warning("- tesseract-ocr")
            logger.warning("- redis-server")
            return True
        
        for command, description in dependencies:
            if not run_command(command, description):
                logger.warning(f"Failed to install: {description}")
    
    elif system == "windows":
        logger.warning("Windows detected. Please install dependencies manually:")
        logger.warning("1. Install Ghostscript: https://www.ghostscript.com/download/gsdnld.html")
        logger.warning("2. Install Poppler: https://poppler.freedesktop.org/")
        logger.warning("3. Install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki")
        logger.warning("4. Install Redis: https://redis.io/download")
        logger.warning("5. Add all tools to your PATH environment variable")
    
    return True

def install_python_dependencies():
    """Install Python dependencies"""
    logger = logging.getLogger(__name__)
    
    # Upgrade pip first
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install requirements
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt", 
                      "Installing Python dependencies"):
        return False
    
    # Install Playwright browsers
    if not run_command("playwright install chromium", "Installing Playwright browsers"):
        logger.warning("Failed to install Playwright browsers. You may need to run this manually.")
    
    return True

def setup_directories():
    """Create necessary directories"""
    logger = logging.getLogger(__name__)
    
    directories = [
        'data/input',
        'data/output',
        'data/cache',
        'data/cache/pdfs',
        'crawls/swedish_municipalities',
        'logs'
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"✓ Created directory: {directory}")
        except Exception as e:
            logger.error(f"✗ Failed to create directory {directory}: {e}")
            return False
    
    return True

def test_pdf_extraction():
    """Test PDF extraction capabilities"""
    logger = logging.getLogger(__name__)
    
    try:
        # Test Camelot
        import camelot
        logger.info("✓ Camelot import successful")
        
        # Test pdfplumber
        import pdfplumber
        logger.info("✓ pdfplumber import successful")
        
        # Test OpenCV (required by Camelot)
        import cv2
        logger.info("✓ OpenCV import successful")
        
        # Test pandas
        import pandas as pd
        logger.info("✓ Pandas import successful")
        
        logger.info("✓ All PDF extraction dependencies are working")
        return True
        
    except ImportError as e:
        logger.error(f"✗ PDF extraction test failed: {e}")
        logger.error("Please check that all dependencies are installed correctly")
        return False

def test_redis_connection():
    """Test Redis connection"""
    logger = logging.getLogger(__name__)
    
    try:
        import redis
        client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        client.ping()
        logger.info("✓ Redis connection successful")
        return True
    except Exception as e:
        logger.warning(f"⚠ Redis connection failed: {e}")
        logger.warning("Redis is optional but recommended for caching")
        return False

def create_sample_config():
    """Create sample configuration files"""
    logger = logging.getLogger(__name__)
    
    # Create sample municipalities file if it doesn't exist
    municipalities_file = 'data/input/municipalities.csv'
    if not os.path.exists(municipalities_file):
        sample_data = """municipality,url,org_number,population
Stockholm,https://stockholm.se,212000-0142,975551
Göteborg,https://goteborg.se,212000-1355,579281
Malmö,https://malmo.se,212000-1124,347949
Uppsala,https://uppsala.se,212000-2817,230767
Västerås,https://vasteras.se,212000-0100,154049"""
        
        try:
            with open(municipalities_file, 'w', encoding='utf-8') as f:
                f.write(sample_data)
            logger.info(f"✓ Created sample municipalities file: {municipalities_file}")
        except Exception as e:
            logger.error(f"✗ Failed to create sample file: {e}")
            return False
    
    return True

def main():
    """Main setup function"""
    logger = setup_logging()
    
    logger.info("=" * 60)
    logger.info("Swedish Municipal Crawler - Enhanced Setup")
    logger.info("=" * 60)
    
    success = True
    
    # Step 1: Install system dependencies
    logger.info("\n1. Installing system dependencies...")
    if not install_system_dependencies():
        success = False
    
    # Step 2: Setup directories
    logger.info("\n2. Setting up directories...")
    if not setup_directories():
        success = False
    
    # Step 3: Install Python dependencies
    logger.info("\n3. Installing Python dependencies...")
    if not install_python_dependencies():
        success = False
    
    # Step 4: Test PDF extraction
    logger.info("\n4. Testing PDF extraction capabilities...")
    if not test_pdf_extraction():
        success = False
    
    # Step 5: Test Redis
    logger.info("\n5. Testing Redis connection...")
    test_redis_connection()  # Non-critical
    
    # Step 6: Create sample config
    logger.info("\n6. Creating sample configuration...")
    if not create_sample_config():
        success = False
    
    # Final status
    logger.info("\n" + "=" * 60)
    if success:
        logger.info("✓ Setup completed successfully!")
        logger.info("\nNext steps:")
        logger.info("1. Review and update data/input/municipalities.csv")
        logger.info("2. Run the crawler: python run_crawler.py")
        logger.info("3. Monitor progress: python web_interface/app.py")
    else:
        logger.error("✗ Setup completed with errors!")
        logger.error("Please review the error messages above and fix any issues.")
    
    logger.info("=" * 60)
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 