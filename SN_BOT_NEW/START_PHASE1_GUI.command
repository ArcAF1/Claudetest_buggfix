#!/bin/bash

# Phase 1 Swedish Municipal Crawler - GUI Version
# This script starts the web interface with crawler controls

echo "🕷️  Phase 1 Swedish Municipal Crawler - GUI Version"
echo "=================================================="

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run install_dependencies.py first."
    echo "   python3 install_dependencies.py"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Check if required packages are installed
echo "📦 Checking dependencies..."
python3 -c "
import sys
required_packages = ['flask', 'scrapy', 'pandas', 'openpyxl']
missing = []
for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        missing.append(package)
if missing:
    print(f'❌ Missing packages: {missing}')
    print('Please run: pip install -r requirements.txt')
    sys.exit(1)
print('✅ All dependencies found')
"

if [ $? -ne 0 ]; then
    echo "Installing missing dependencies..."
    pip install -r requirements.txt
fi

# Navigate to web interface directory
cd swedish_municipal_crawler/web_interface

echo ""
echo "🚀 Starting Phase 1 GUI Dashboard..."
echo "📊 Dashboard will be available at: http://127.0.0.1:5001"
echo "🎯 Features:"
echo "   • Start/Stop crawler with one click"
echo "   • Real-time progress monitoring"
echo "   • Live log viewer"
echo "   • Data visualization and export"
echo ""
echo "💡 Usage:"
echo "   1. Open http://127.0.0.1:5001 in your browser"
echo "   2. Click 'Start Crawling' button"
echo "   3. Monitor progress in real-time"
echo "   4. View and export results"
echo ""
echo "⏹️  Press Ctrl+C to stop the server"
echo ""

# Start the Flask application
python3 phase1_app.py 