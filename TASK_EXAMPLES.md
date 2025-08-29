# Task Examples Created

## 🎯 Simple 2-Minute Task

**File**: `tasks/simple_2min_task.py`

### Features:
- ✅ Runs for exactly 2 minutes (120 seconds)
- ✅ Prints progress updates every 10 seconds
- ✅ Shows percentage completion
- ✅ Displays current time every 6 updates
- ✅ Logs all activity to file
- ✅ Returns detailed execution results

### What it prints:
```
🚀 Hello from simple 2-minute task!
⏱️  Progress: 8.3% (10s / 120s)
⏱️  Progress: 16.7% (20s / 120s)
📊 Still running... Check #3
⏱️  Progress: 25.0% (30s / 120s)
⏱️  Progress: 33.3% (40s / 120s)
⏱️  Progress: 41.7% (50s / 120s)
🕐 Current time: 00:31:06
⏱️  Progress: 50.0% (60s / 120s)
... (continues for 2 minutes)
✅ Task completed! Actual duration: 120.01 seconds
```

### Test Results:
- ✅ **Duration**: Exactly 120.01 seconds
- ✅ **Progress Updates**: 12 updates during execution
- ✅ **Logging**: Complete log file created
- ✅ **Status**: Successfully completed

## 🚀 Quick Test Task (30 Seconds)

**File**: `tasks/quick_test_task.py`

### Features:
- ✅ Runs for 30 seconds
- ✅ Progress updates every 5 seconds
- ✅ More frequent status messages
- ✅ Perfect for quick testing

### What it prints:
```
🚀 Quick test task is running!
⏱️  Progress: 16.7% (5s / 30s)
⏱️  Progress: 33.3% (10s / 30s)
📊 Update #2 - Still running...
⏱️  Progress: 50.0% (15s / 30s)
🕐 Time: 00:35:15
⏱️  Progress: 66.7% (20s / 30s)
📊 Update #4 - Still running...
⏱️  Progress: 83.3% (25s / 30s)
⏱️  Progress: 100.0% (30s / 30s)
✅ Quick test completed! Duration: 30.02 seconds
```

## 📊 How to Use These Tasks

### 1. **Access via Admin Panel**
- Go to: http://localhost:7000/admin
- Login: admin/admin123
- Navigate to Tasks page
- Click "Run" button on any task

### 2. **Access via API**
```bash
# Run 2-minute task
curl -u admin:admin123 -X POST http://localhost:7000/api/tasks/3/run

# Run quick test task
curl -u admin:admin123 -X POST http://localhost:7000/api/tasks/4/run
```

### 3. **Monitor Progress**
```bash
# Check task status
curl -u admin:admin123 http://localhost:7000/api/tasks/3/runs

# View logs
curl -u admin:admin123 http://localhost:7000/api/logs/
```

## 🎯 Task Configuration

Both tasks accept configuration parameters:

```python
# Example configuration
config = {
    "duration_minutes": 1,  # For 2-min task
    "duration_seconds": 15,  # For quick task
    "progress_interval_seconds": 5,
    "message": "Custom message here!"
}
```

## 📈 Monitoring Features

### Real-time Monitoring:
- ✅ **Progress percentage** displayed
- ✅ **Time elapsed** vs **total time**
- ✅ **Status updates** during execution
- ✅ **Current time** stamps
- ✅ **Completion confirmation**

### Log Management:
- ✅ **Individual log files** for each execution
- ✅ **Download logs** via admin panel
- ✅ **View log content** in real-time
- ✅ **Automatic cleanup** after 7 days

### Task History:
- ✅ **Execution history** for each task
- ✅ **Success/failure status**
- ✅ **Duration tracking**
- ✅ **Error messages** (if any)

## 🚀 Ready to Use!

These tasks are perfect for:
- ✅ **Testing the system** functionality
- ✅ **Demonstrating** long-running tasks
- ✅ **Monitoring** task execution
- ✅ **Learning** how to create custom tasks
- ✅ **Verifying** logging and status tracking

Both tasks are **fully functional** and ready to run immediately! 