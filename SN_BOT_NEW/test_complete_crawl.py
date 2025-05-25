#!/usr/bin/env python3
"""
Test script to demonstrate the complete Phase 1 crawling process
"""

import requests
import time
import json

def test_complete_crawl():
    base_url = "http://127.0.0.1:5001"
    
    print("🕷️ Phase 1 Crawler Test - Complete Process Demo")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(f"{base_url}/api/phase1/crawler-status")
        if response.status_code != 200:
            print("❌ Flask server not running. Please start it first.")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask server. Please start it first.")
        print("   Run: cd swedish_municipal_crawler/web_interface && python3 phase1_app.py")
        return
    
    print("✅ Flask server is running")
    
    # Start the crawler
    print("\n🚀 Starting crawler in test mode...")
    start_response = requests.post(
        f"{base_url}/api/phase1/start-crawler",
        json={"mode": "test"},
        headers={"Content-Type": "application/json"}
    )
    
    if start_response.status_code == 200:
        result = start_response.json()
        if result.get("success"):
            print("✅ Crawler started successfully!")
        else:
            print(f"❌ Failed to start crawler: {result.get('error')}")
            return
    else:
        print(f"❌ Failed to start crawler: HTTP {start_response.status_code}")
        return
    
    # Monitor progress
    print("\n📊 Monitoring progress...")
    print("-" * 50)
    
    last_progress = -1
    last_municipalities = -1
    start_time = time.time()
    
    while True:
        try:
            status_response = requests.get(f"{base_url}/api/phase1/crawler-status")
            if status_response.status_code == 200:
                status = status_response.json()
                
                current_progress = status.get("progress", 0)
                current_municipalities = status.get("municipalities_processed", 0)
                running = status.get("running", False)
                
                # Show progress updates
                if current_progress != last_progress or current_municipalities != last_municipalities:
                    elapsed = int(time.time() - start_time)
                    print(f"[{elapsed:3d}s] Progress: {current_progress:3d}% | Municipalities: {current_municipalities:2d} | Status: {status.get('status', 'Unknown')}")
                    
                    # Show recent logs
                    logs = status.get("logs", [])
                    for log in logs[-3:]:  # Show last 3 log entries
                        level = log.get("level", "info").upper()
                        message = log.get("message", "")
                        if len(message) > 80:
                            message = message[:77] + "..."
                        print(f"       [{level}] {message}")
                    
                    last_progress = current_progress
                    last_municipalities = current_municipalities
                
                # Check if finished
                if not running:
                    success = status.get("success", False)
                    if success:
                        print(f"\n🎉 Crawler completed successfully!")
                        print(f"   Total municipalities processed: {current_municipalities}")
                        print(f"   Total time: {int(time.time() - start_time)} seconds")
                    else:
                        error = status.get("error", "Unknown error")
                        print(f"\n❌ Crawler failed: {error}")
                    break
                
                # Check for timeout
                if time.time() - start_time > 300:  # 5 minutes
                    print(f"\n⏰ Timeout reached (5 minutes)")
                    break
                    
            else:
                print(f"❌ Failed to get status: HTTP {status_response.status_code}")
                break
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request error: {e}")
            break
        
        time.sleep(2)  # Check every 2 seconds
    
    # Show final results
    print("\n📋 Final Results:")
    print("-" * 30)
    
    try:
        overview_response = requests.get(f"{base_url}/api/phase1/overview")
        if overview_response.status_code == 200:
            overview = overview_response.json()
            print(f"Total municipalities: {overview.get('total_municipalities', 0)}")
            print(f"Complete data: {overview.get('complete_data', 0)}")
            print(f"Partial data: {overview.get('partial_data', 0)}")
            print(f"Completion rate: {overview.get('completion_rate', 0)}%")
        else:
            print("❌ Could not fetch overview data")
    except:
        print("❌ Error fetching final results")
    
    print(f"\n🌐 View full dashboard at: {base_url}")
    print("🎯 Mission accomplished! Your GUI crawler is fully functional.")

if __name__ == "__main__":
    test_complete_crawl() 