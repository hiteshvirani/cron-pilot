# CronPilot Environment Management Guide

## Quick Start

### 1. Create Environment for Task
```bash
cd tasks/my_task
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows
pip install pandas requests
pip freeze > requirements.txt
```

### 2. Configure Task in Admin Panel
1. Go to Tasks → Environment Manager
2. View discovered environments and requirements
3. Edit task schedule → Environment Configuration
4. Select environment and requirements file
5. Save configuration

### 3. Run Task
- Task will automatically activate environment
- Install requirements if needed
- Execute in isolated environment
- Log results and cleanup

## Features

✅ **Environment Isolation**: Each task runs in its own virtual environment
✅ **Auto-Discovery**: Finds environments and requirements automatically  
✅ **Multi-File Projects**: Supports complex task projects with multiple files
✅ **Admin Interface**: Visual environment management in web UI
✅ **API Support**: Full REST API for environment management
✅ **Validation**: Built-in environment and requirements validation

## API Endpoints

- `GET /api/tasks/environments` - List discovered environments
- `GET /api/tasks/requirements` - List requirements files
- `GET /api/tasks/projects` - List task projects
- `POST /api/tasks/validate-environment` - Validate environment

## Example Usage

```python
# Task with specific dependencies
def run_task(config):
    import pandas as pd  # Only works if pandas installed in environment
    import requests
    
    # Your task logic here
    return {"status": "success"}
```

## Benefits

- **No Dependency Conflicts**: Different tasks can use different library versions
- **Easy Management**: Visual interface for environment configuration
- **Automatic Setup**: Requirements installed automatically before execution
- **Isolation**: Tasks can't interfere with each other's dependencies
- **Scalability**: Support for complex multi-file task projects
