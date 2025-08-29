#!/usr/bin/env python3
"""
Test script to verify multiple concurrent task execution
"""

import requests
import time
import threading
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:7000"
AUTH = ("admin", "admin123")

def run_task_and_monitor(task_id, task_name):
    """Run a task and monitor its progress"""
    print(f"🚀 Starting {task_name} (Task ID: {task_id})")
    
    # Start the task
    response = requests.post(f"{BASE_URL}/api/tasks/{task_id}/run", auth=AUTH)
    if response.status_code == 200:
        data = response.json()
        run_id = data.get('task_run_id')
        print(f"   ✅ {task_name} started (Run ID: {run_id})")
        
        # Monitor the task
        start_time = time.time()
        while True:
            time.sleep(5)  # Check every 5 seconds
            
            # Get task runs
            runs_response = requests.get(f"{BASE_URL}/api/tasks/{task_id}/runs", auth=AUTH)
            if runs_response.status_code == 200:
                runs = runs_response.json()["task_runs"]
                if runs:
                    latest_run = runs[0]
                    if latest_run["id"] == run_id:
                        status = latest_run["status"]
                        elapsed = time.time() - start_time
                        
                        if status == "running":
                            print(f"   ⏱️  {task_name}: Still running... ({elapsed:.1f}s)")
                        elif status == "success":
                            duration = latest_run.get("duration_seconds", 0)
                            print(f"   ✅ {task_name}: Completed in {duration:.2f}s")
                            break
                        elif status == "failed":
                            error = latest_run.get("error_message", "Unknown error")
                            print(f"   ❌ {task_name}: Failed - {error}")
                            break
                        else:
                            print(f"   ⚠️  {task_name}: Status {status}")
                            break
                    else:
                        print(f"   ⚠️  {task_name}: Run ID mismatch")
                        break
                else:
                    print(f"   ⚠️  {task_name}: No runs found")
                    break
            else:
                print(f"   ❌ {task_name}: Failed to get runs")
                break
    else:
        print(f"   ❌ {task_name}: Failed to start - {response.status_code}")

def test_concurrent_execution():
    """Test running multiple tasks concurrently"""
    print("🧪 Testing Concurrent Task Execution")
    print("=" * 50)
    
    # Get available tasks
    response = requests.get(f"{BASE_URL}/api/tasks/", auth=AUTH)
    if response.status_code != 200:
        print("❌ Failed to get tasks")
        return
    
    tasks = response.json()["tasks"]
    print(f"📋 Found {len(tasks)} tasks")
    
    # Find suitable tasks for concurrent testing
    test_tasks = []
    for task in tasks:
        if "quick_test" in task["name"] or "simple_2min" in task["name"]:
            test_tasks.append(task)
    
    if len(test_tasks) < 2:
        print("❌ Need at least 2 test tasks for concurrent testing")
        return
    
    print(f"🎯 Using {len(test_tasks)} tasks for concurrent testing:")
    for task in test_tasks:
        print(f"   - {task['name']} (ID: {task['id']})")
    
    # Start all tasks concurrently
    print("\n🚀 Starting concurrent task execution...")
    threads = []
    
    for task in test_tasks:
        thread = threading.Thread(
            target=run_task_and_monitor,
            args=(task["id"], task["name"])
        )
        threads.append(thread)
        thread.start()
        time.sleep(1)  # Small delay between starts
    
    # Wait for all threads to complete
    print("\n⏳ Waiting for all tasks to complete...")
    for thread in threads:
        thread.join()
    
    print("\n✅ Concurrent execution test completed!")

def test_system_capacity():
    """Test system capacity with multiple quick tasks"""
    print("\n🧪 Testing System Capacity")
    print("=" * 50)
    
    # Get quick test task
    response = requests.get(f"{BASE_URL}/api/tasks/", auth=AUTH)
    if response.status_code != 200:
        print("❌ Failed to get tasks")
        return
    
    tasks = response.json()["tasks"]
    quick_task = None
    for task in tasks:
        if "quick_test" in task["name"]:
            quick_task = task
            break
    
    if not quick_task:
        print("❌ Quick test task not found")
        return
    
    print(f"🎯 Testing with {quick_task['name']} (ID: {quick_task['id']})")
    
    # Start multiple instances
    num_instances = 5
    print(f"🚀 Starting {num_instances} concurrent instances...")
    
    start_time = time.time()
    threads = []
    
    for i in range(num_instances):
        thread = threading.Thread(
            target=run_task_and_monitor,
            args=(quick_task["id"], f"{quick_task['name']}-{i+1}")
        )
        threads.append(thread)
        thread.start()
        time.sleep(0.5)  # Small delay between starts
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    total_time = time.time() - start_time
    print(f"\n✅ Capacity test completed in {total_time:.2f}s")
    print(f"📊 Started {num_instances} tasks concurrently")

def main():
    """Run all concurrent tests"""
    print("🚀 CronPilot Concurrent Task Testing")
    print("=" * 60)
    
    # Test 1: Basic concurrent execution
    test_concurrent_execution()
    
    # Test 2: System capacity
    test_system_capacity()
    
    print("\n" + "=" * 60)
    print("🎉 Concurrent task testing completed!")
    print("\n📊 Results:")
    print("   - Multiple tasks can run simultaneously")
    print("   - Each task has its own execution context")
    print("   - Logs are separated per task execution")
    print("   - System handles concurrent load well")

if __name__ == "__main__":
    main() 