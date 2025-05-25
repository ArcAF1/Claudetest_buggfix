#!/usr/bin/env python3
"""
Phase 1 Web Interface Demo Script
Demonstrates the web interface functionality with sample data
"""

import sys
import time
import webbrowser
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    """Demo the Phase 1 web interface"""
    print("🎯 Phase 1 Web Interface Demo")
    print("=" * 50)
    
    print("\n📋 This demo will:")
    print("1. Create sample Phase 1 data")
    print("2. Start the web interface")
    print("3. Open your browser to the dashboard")
    print("4. Show you the key features")
    
    input("\nPress Enter to continue...")
    
    # Step 1: Create test data
    print("\n📊 Creating sample Phase 1 data...")
    try:
        from test_web_interface import create_test_database, create_test_statistics
        db_path = create_test_database()
        stats_path = create_test_statistics()
        print(f"✓ Sample data created successfully")
    except Exception as e:
        print(f"✗ Error creating sample data: {e}")
        return 1
    
    # Step 2: Start web interface
    print("\n🚀 Starting Phase 1 web interface...")
    print("   URL: http://127.0.0.1:5001")
    print("   The interface will open in your browser automatically")
    
    # Step 3: Show features
    print("\n🎨 Dashboard Features:")
    print("   📊 Overview Cards - Total municipalities and completion rates")
    print("   📈 Field Coverage - Visual progress bars for each data point")
    print("   📉 Interactive Charts - Timtaxa comparison and billing distribution")
    print("   📋 Data Table - Searchable, sortable municipality data")
    print("   📤 Export Options - Excel, CSV, and JSON downloads")
    print("   🔍 Missing Data Analysis - Identify gaps for follow-up")
    
    print("\n💡 Try these features:")
    print("   • Search for municipalities in the data table")
    print("   • Filter by status (Complete/Partial)")
    print("   • Click on charts for interactive exploration")
    print("   • Export data using the buttons in the header")
    print("   • Check missing data section for follow-up actions")
    
    print("\n⚠️  Note: This is demo data with 5 sample municipalities")
    print("   Run the full Phase 1 crawler for real data:")
    print("   python run_phase1_crawler.py --test-mode")
    
    # Give user time to read
    time.sleep(2)
    
    # Open browser
    try:
        webbrowser.open('http://127.0.0.1:5001')
        print("\n🌐 Opening browser...")
    except:
        print("\n🌐 Please open http://127.0.0.1:5001 in your browser")
    
    # Start the web interface
    try:
        from phase1_app import app
        print("\n🎯 Phase 1 Web Interface is now running!")
        print("   Press Ctrl+C to stop the server")
        print("=" * 50)
        
        app.run(host='127.0.0.1', port=5001, debug=False)
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo completed!")
        print("   Thank you for trying the Phase 1 Web Interface")
        return 0
    except Exception as e:
        print(f"\n❌ Error starting web interface: {e}")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code) 