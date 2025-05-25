@echo off
REM Phase 1 System - Windows Startup Script
REM Double-click this file to start the Phase 1 Swedish Municipal Fee Crawler

echo ================================================================================
echo                    PHASE 1 SWEDISH MUNICIPAL FEE CRAWLER
echo ================================================================================
echo Starting Phase 1 system with test data...
echo This will open your web browser automatically when ready.
echo.
echo Press Ctrl+C to stop the system at any time.
echo ================================================================================
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Run the Phase 1 system with quick start
python start_phase1_system.py --quick-start

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo ================================================================================
    echo ERROR: Phase 1 system failed to start
    echo ================================================================================
    echo.
    echo Possible solutions:
    echo 1. Install Python 3.8+ from https://python.org
    echo 2. Install dependencies: pip install -r requirements.txt
    echo 3. Check that you're in the correct directory
    echo.
    pause
) 