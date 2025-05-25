#!/bin/bash
# Phase 1 System - Unix/Linux/Mac Startup Script
# Double-click this file to start the Phase 1 Swedish Municipal Fee Crawler

echo "================================================================================"
echo "                   PHASE 1 SWEDISH MUNICIPAL FEE CRAWLER"
echo "================================================================================"
echo "Starting Phase 1 system with test data..."
echo "This will open your web browser automatically when ready."
echo ""
echo "Press Ctrl+C to stop the system at any time."
echo "================================================================================"
echo ""

# Change to the script directory
cd "$(dirname "$0")"

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ ERROR: Python not found!"
    echo ""
    echo "Please install Python 3.8+ from:"
    echo "  - macOS: brew install python3 or https://python.org"
    echo "  - Ubuntu/Debian: sudo apt install python3"
    echo "  - CentOS/RHEL: sudo yum install python3"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# Use python3 if available, otherwise python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

# Run the Phase 1 system with quick start
$PYTHON_CMD start_phase1_system.py --quick-start

# Check exit code
if [ $? -ne 0 ]; then
    echo ""
    echo "================================================================================"
    echo "ERROR: Phase 1 system failed to start"
    echo "================================================================================"
    echo ""
    echo "Possible solutions:"
    echo "1. Install Python 3.8+ from https://python.org"
    echo "2. Install dependencies: pip install -r requirements.txt"
    echo "3. Check that you're in the correct directory"
    echo ""
    read -p "Press Enter to exit..."
fi 