#!/usr/bin/env python3
"""
Test script for CronPilot Environment Management Features

This script tests the new environment management capabilities including:
- Environment discovery
- Requirements file discovery
- Task project discovery
- Environment validation
- Task execution with isolated environments
"""

import requests
import json
import time
import os
import sys
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:7000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def get_auth_headers():
    """Get authentication headers"""
    import base64
    credentials = f"{ADMIN_USERNAME}:{ADMIN_PASSWORD}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return {"Authorization": f"Basic {encoded}"}

def test_health_check():
    """Test basic health check"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_environment_discovery():
    """Test environment discovery API"""
    print("\n🔍 Testing environment discovery...")
    try:
        response = requests.get(f"{BASE_URL}/api/tasks/environments", headers=get_auth_headers())
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Environment discovery successful")
            print(f"   Found {len(data.get('environments', []))} environments")
            for env in data.get('environments', []):
                print(f"   - {env['name']}: {env['path']}")
            return True
        else:
            print(f"❌ Environment discovery failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Environment discovery error: {e}")
        return False

def test_requirements_discovery():
    """Test requirements file discovery API"""
    print("\n🔍 Testing requirements file discovery...")
    try:
        response = requests.get(f"{BASE_URL}/api/tasks/requirements", headers=get_auth_headers())
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Requirements discovery successful")
            print(f"   Found {len(data.get('requirements_files', []))} requirements files")
            for req in data.get('requirements_files', []):
                print(f"   - {req['name']}: {req['path']}")
            return True
        else:
            print(f"❌ Requirements discovery failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Requirements discovery error: {e}")
        return False

def test_project_discovery():
    """Test task project discovery API"""
    print("\n🔍 Testing task project discovery...")
    try:
        response = requests.get(f"{BASE_URL}/api/tasks/projects", headers=get_auth_headers())
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Project discovery successful")
            print(f"   Found {len(data.get('task_projects', []))} task projects")
            for proj in data.get('task_projects', []):
                print(f"   - {proj['name']}: {proj['main_file']} ({proj['file_count']} files)")
            return True
        else:
            print(f"❌ Project discovery failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Project discovery error: {e}")
        return False

def test_environment_validation():
    """Test environment validation API"""
    print("\n🔍 Testing environment validation...")
    try:
        # Test with system Python (should work)
        validation_data = {
            "environment_path": "/usr/bin/python3"  # This might not be a venv, but should be valid Python
        }
        
        response = requests.post(
            f"{BASE_URL}/api/tasks/validate-environment", 
            headers=get_auth_headers(),
            json=validation_data
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Environment validation API working")
            print(f"   Validation result: {data}")
            return True
        else:
            print(f"❌ Environment validation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Environment validation error: {e}")
        return False

def test_task_execution_with_environment():
    """Test task execution with environment configuration"""
    print("\n🔍 Testing task execution with environment...")
    try:
        # First, get existing tasks
        response = requests.get(f"{BASE_URL}/api/tasks", headers=get_auth_headers())
        if response.status_code != 200:
            print(f"❌ Failed to get tasks: {response.status_code}")
            return False
        
        tasks = response.json().get('tasks', [])
        if not tasks:
            print("❌ No tasks available for testing")
            return False
        
        # Use the first task for testing
        task = tasks[0]
        print(f"   Testing with task: {task['name']}")
        
        # Run the task
        response = requests.post(
            f"{BASE_URL}/api/tasks/{task['id']}/run",
            headers=get_auth_headers(),
            json={}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Task execution started successfully")
            print(f"   Task run ID: {data.get('task_run_id')}")
            print(f"   Status: {data.get('status')}")
            return True
        else:
            print(f"❌ Task execution failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Task execution error: {e}")
        return False

def create_test_environment():
    """Create a test virtual environment for testing"""
    print("\n🔧 Creating test environment...")
    try:
        import venv
        import subprocess
        
        # Create test environment
        test_env_path = "./tasks/test_env"
        if not os.path.exists(test_env_path):
            print(f"   Creating virtual environment at {test_env_path}")
            venv.create(test_env_path, with_pip=True)
        
        # Create test requirements file
        requirements_path = "./tasks/test_requirements.txt"
        with open(requirements_path, 'w') as f:
            f.write("requests==2.31.0\n")
            f.write("pandas==2.0.3\n")
        
        print(f"✅ Test environment created")
        print(f"   Environment: {test_env_path}")
        print(f"   Requirements: {requirements_path}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create test environment: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting CronPilot Environment Management Test")
    print("=" * 60)
    
    # Test results
    results = []
    
    # Basic health check
    results.append(("Health Check", test_health_check()))
    
    # Create test environment
    results.append(("Test Environment Creation", create_test_environment()))
    
    # Environment management tests
    results.append(("Environment Discovery", test_environment_discovery()))
    results.append(("Requirements Discovery", test_requirements_discovery()))
    results.append(("Project Discovery", test_project_discovery()))
    results.append(("Environment Validation", test_environment_validation()))
    results.append(("Task Execution with Environment", test_task_execution_with_environment()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Environment management is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
