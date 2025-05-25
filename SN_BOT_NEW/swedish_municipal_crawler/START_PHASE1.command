#!/bin/bash
# Phase 1 System - macOS .command file
# Double-click this file to start the Phase 1 Swedish Municipal Fee Crawler

# Clear the terminal for a clean start
clear

echo "================================================================================"
echo "                   PHASE 1 SWEDISH MUNICIPAL FEE CRAWLER"
echo "================================================================================"
echo "🚀 Starting Phase 1 system with REAL crawler..."
echo "🌐 This will crawl actual municipal websites and open your browser when ready."
echo ""
echo "💡 Press Ctrl+C to stop the system at any time."
echo "================================================================================"
echo ""

# Change to the script directory (where this .command file is located)
cd "$(dirname "$0")"

echo "📁 Working directory: $(pwd)"
echo ""

# Clean up any existing crawler processes
echo "🧹 Cleaning up any existing crawler processes..."
pkill -f "start_phase1_system.py" 2>/dev/null
pkill -f "phase1_spider" 2>/dev/null
pkill -f "run_phase1_web.py" 2>/dev/null
pkill -f "phase1_app.py" 2>/dev/null

# Wait a moment for processes to terminate
sleep 2

# Check if any processes are still running
RUNNING_PROCESSES=$(ps aux | grep -E "(start_phase1_system|phase1_spider|run_phase1_web|phase1_app)" | grep -v grep | wc -l)
if [[ $RUNNING_PROCESSES -gt 0 ]]; then
    echo "⚠️  Some processes still running, force killing..."
    pkill -9 -f "start_phase1_system.py" 2>/dev/null
    pkill -9 -f "phase1_spider" 2>/dev/null
    pkill -9 -f "run_phase1_web.py" 2>/dev/null
    pkill -9 -f "phase1_app.py" 2>/dev/null
    sleep 1
fi

echo "✅ Process cleanup completed"
echo ""

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "🐍 Using virtual environment: $VIRTUAL_ENV"
    PYTHON_CMD="python"
    PIP_CMD="pip"
else
    # Check for python3 and pip3
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        echo "🐍 Using: python3 ($(python3 --version))"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
        echo "🐍 Using: python ($(python --version))"
    else
        echo "❌ ERROR: Python not found!"
        echo ""
        echo "🔧 Please install Python 3.8+ first:"
        echo "   brew install python3"
        echo ""
        read -p "Press Enter to close this window..."
        exit 1
    fi

    if command -v pip3 &> /dev/null; then
        PIP_CMD="pip3"
    elif command -v pip &> /dev/null; then
        PIP_CMD="pip"
    else
        echo "❌ ERROR: pip not found!"
        echo ""
        echo "🔧 Please install pip first"
        echo ""
        read -p "Press Enter to close this window..."
        exit 1
    fi
fi

echo ""

# Check if requirements.txt exists
if [[ ! -f "requirements.txt" ]]; then
    echo "❌ ERROR: requirements.txt not found!"
    echo "   Make sure you're in the correct directory"
    echo ""
    read -p "Press Enter to close this window..."
    exit 1
fi

# Install/update dependencies automatically
echo "📦 Checking and installing dependencies..."
echo "   This may take a moment on first run..."
echo ""

# Install requirements
$PIP_CMD install -r requirements.txt --quiet --disable-pip-version-check

if [[ $? -ne 0 ]]; then
    echo "⚠️  Some packages may have failed to install, but continuing..."
    echo ""
fi

# Install specific packages that might be missing
echo "🔧 Ensuring critical packages are installed..."
$PIP_CMD install aiohttp asyncio-throttle nest-asyncio --quiet --disable-pip-version-check 2>/dev/null

echo "✅ Dependencies check completed"
echo ""

# Check if the Phase 1 system script exists
if [[ ! -f "start_phase1_system.py" ]]; then
    echo "❌ ERROR: start_phase1_system.py not found!"
    echo "   Make sure you're in the swedish_municipal_crawler directory"
    echo ""
    read -p "Press Enter to close this window..."
    exit 1
fi

echo "🎯 Found Phase 1 system script"
echo ""
echo "🌐 Starting Phase 1 interactive web interface..."
echo "   You can start/stop crawling and monitor progress from the web interface"
echo "   🔍 Automatically finding available port (starting from 5000)..."
echo "   📱 Browser will open automatically when ready"
echo "================================================================================"

# Start the interactive web interface
$PYTHON_CMD start_phase1_system.py --web-only

# Capture exit code
EXIT_CODE=$?

echo ""
echo "================================================================================"

if [[ $EXIT_CODE -eq 0 ]]; then
    echo "✅ SUCCESS: Phase 1 interactive web interface started successfully!"
    echo ""
    echo "🌐 The web interface is running with automatic port detection"
    echo "🌐 Your browser should have opened automatically"
    echo ""
    echo "🎮 From the web interface you can:"
    echo "   • Start/stop crawling with real-time monitoring"
    echo "   • Choose how many municipalities to crawl"
    echo "   • View live logs and progress"
    echo "   • Export results when complete"
    echo ""
    echo "💡 The interface allows full control over the crawling process!"
else
    echo "❌ ERROR: Phase 1 system failed to start (Exit code: $EXIT_CODE)"
    echo ""
    echo "🔧 Possible solutions:"
    echo "1. Install Python 3.8+: brew install python3"
    echo "2. Install dependencies: $PIP_CMD install -r requirements.txt"
    echo "3. Check internet connection"
    echo "4. Verify you're in the correct directory"
    echo ""
    echo "🐛 For detailed error information, run manually:"
    echo "   $PYTHON_CMD start_phase1_system.py --web-only"
fi

echo ""
read -p "Press Enter to close this window..." 