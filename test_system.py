#!/usr/bin/env python3
"""
Comprehensive test script for CronPilot system
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:7000"
AUTH = ("admin", "admin123")

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        print("✅ Health check passed")
        return True
    else:
        print(f"❌ Health check failed: {response.status_code}")
        return False

def test_authentication():
    """Test authentication"""
    print("🔍 Testing authentication...")
    response = requests.get(f"{BASE_URL}/api/tasks/", auth=AUTH)
    if response.status_code == 200:
        print("✅ Authentication working")
        return True
    else:
        print(f"❌ Authentication failed: {response.status_code}")
        return False

def test_tasks_api():
    """Test tasks API"""
    print("🔍 Testing tasks API...")
    
    # Get tasks
    response = requests.get(f"{BASE_URL}/api/tasks/", auth=AUTH)
    if response.status_code == 200:
        tasks = response.json()["tasks"]
        print(f"✅ Found {len(tasks)} tasks")
        
        if tasks:
            task_id = tasks[0]["id"]
            print(f"   Using task ID: {task_id}")
            
            # Test running a task
            print("   Running task...")
            run_response = requests.post(f"{BASE_URL}/api/tasks/{task_id}/run", auth=AUTH)
            if run_response.status_code == 200:
                print("   ✅ Task execution started")
                
                # Wait a bit and check task runs
                time.sleep(3)
                runs_response = requests.get(f"{BASE_URL}/api/tasks/{task_id}/runs", auth=AUTH)
                if runs_response.status_code == 200:
                    runs = runs_response.json()["task_runs"]
                    if runs:
                        latest_run = runs[0]
                        print(f"   ✅ Task run completed: {latest_run['status']}")
                        return True
                    else:
                        print("   ❌ No task runs found")
                        return False
                else:
                    print(f"   ❌ Failed to get task runs: {runs_response.status_code}")
                    return False
            else:
                print(f"   ❌ Failed to run task: {run_response.status_code}")
                return False
        else:
            print("   ⚠️  No tasks found")
            return True
    else:
        print(f"❌ Failed to get tasks: {response.status_code}")
        return False

def test_logs_api():
    """Test logs API"""
    print("🔍 Testing logs API...")
    
    response = requests.get(f"{BASE_URL}/api/logs/", auth=AUTH)
    if response.status_code == 200:
        logs = response.json()["logs"]
        print(f"✅ Found {len(logs)} log files")
        
        if logs:
            log_id = logs[0]["filename"].replace(".log", "")
            print(f"   Using log ID: {log_id}")
            
            # Test getting log content
            content_response = requests.get(f"{BASE_URL}/api/logs/{log_id}/content", auth=AUTH)
            if content_response.status_code == 200:
                content = content_response.json()
                print(f"   ✅ Log content retrieved ({len(content['content'])} characters)")
                return True
            else:
                print(f"   ❌ Failed to get log content: {content_response.status_code}")
                return False
        else:
            print("   ⚠️  No log files found")
            return True
    else:
        print(f"❌ Failed to get logs: {response.status_code}")
        return False

def test_admin_stats():
    """Test admin stats API"""
    print("🔍 Testing admin stats API...")
    
    response = requests.get(f"{BASE_URL}/api/admin/stats", auth=AUTH)
    if response.status_code == 200:
        stats = response.json()
        print("✅ Admin stats retrieved:")
        print(f"   Tasks: {stats['tasks']['total']} total, {stats['tasks']['active']} active")
        print(f"   Runs: {stats['runs']['total']} total, {stats['runs']['successful']} successful")
        print(f"   Logs: {stats['logs']['total_files']} files, {stats['logs']['total_size_mb']} MB")
        return True
    else:
        print(f"❌ Failed to get admin stats: {response.status_code}")
        return False

def test_admin_panel():
    """Test admin panel pages"""
    print("🔍 Testing admin panel...")
    
    pages = ["/admin", "/admin/tasks", "/admin/logs"]
    
    for page in pages:
        response = requests.get(f"{BASE_URL}{page}", auth=AUTH)
        if response.status_code == 200:
            print(f"   ✅ {page} accessible")
        else:
            print(f"   ❌ {page} failed: {response.status_code}")
            return False
    
    print("✅ Admin panel working")
    return True

def test_scheduling():
    """Test task scheduling"""
    print("🔍 Testing task scheduling...")
    
    # Get a task
    response = requests.get(f"{BASE_URL}/api/tasks/", auth=AUTH)
    if response.status_code == 200:
        tasks = response.json()["tasks"]
        if tasks:
            task_id = tasks[0]["id"]
            
            # Test setting hourly schedule
            schedule_data = {
                "schedule_type": "hourly",
                "is_active": True
            }
            
            schedule_response = requests.put(
                f"{BASE_URL}/api/tasks/{task_id}/schedule",
                auth=AUTH,
                json=schedule_data
            )
            
            if schedule_response.status_code == 200:
                print("✅ Task scheduling working")
                return True
            else:
                print(f"❌ Task scheduling failed: {schedule_response.status_code}")
                return False
        else:
            print("⚠️  No tasks to test scheduling")
            return True
    else:
        print(f"❌ Failed to get tasks for scheduling test: {response.status_code}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting CronPilot System Test")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health),
        ("Authentication", test_authentication),
        ("Tasks API", test_tasks_api),
        ("Logs API", test_logs_api),
        ("Admin Stats", test_admin_stats),
        ("Admin Panel", test_admin_panel),
        ("Task Scheduling", test_scheduling),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! CronPilot is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the system.")
    
    print(f"\n🌐 Admin Panel: {BASE_URL}/admin")
    print(f"📚 API Docs: {BASE_URL}/docs")

if __name__ == "__main__":
    main() 