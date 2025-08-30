# CronPilot Environment Management

## Overview

CronPilot now supports **advanced environment management** that allows different tasks to run in isolated environments with their own dependencies. This solves the problem of conflicting requirements between tasks.

## Key Features

### 🔧 Environment Isolation
- **Virtual Environment Support**: Each task can run in its own virtual environment
- **Dependency Management**: Automatic installation of requirements.txt files
- **Conflict Prevention**: No more dependency conflicts between tasks
- **Version Control**: Different tasks can use different versions of the same library

### 📁 Automatic Discovery
- **Environment Detection**: Automatically finds virtual environments in task folders
- **Requirements Discovery**: Scans for requirements.txt files throughout the task directory
- **Project Detection**: Identifies multi-file task projects with main execution files
- **Smart Organization**: Groups environments and requirements by task folders

### 🎛️ Admin Panel Integration
- **Environment Manager**: Visual interface to manage environments and requirements
- **Task Configuration**: Easy environment selection for each task
- **Validation Tools**: Built-in environment validation and testing
- **Real-time Monitoring**: Track environment status and requirements installation

## How It Works

### 1. Environment Discovery

The system automatically scans the `tasks/` directory for:

```
tasks/
├── task1/
│   ├── venv/                    # Virtual environment
│   ├── requirements.txt         # Dependencies
│   └── main.py                  # Task file
├── task2/
│   ├── .env/                    # Alternative env name
│   ├── requirements-dev.txt     # Alternative req name
│   └── task.py                  # Task file
└── global_envs/
    └── shared_venv/             # Shared environments
```

### 2. Task Execution Flow

When a task runs with environment configuration:

1. **Environment Activation**: System activates the specified virtual environment
2. **Requirements Installation**: Installs dependencies from requirements.txt
3. **Isolated Execution**: Task runs in the isolated environment
4. **Result Capture**: Results are captured and logged
5. **Cleanup**: Temporary files are cleaned up

### 3. Environment Types

#### Virtual Environments
- **venv/**: Standard Python virtual environment
- **env/**: Alternative environment name
- **.venv/**: Hidden environment (common in modern projects)
- **.env/**: Another common naming pattern

#### Requirements Files
- **requirements.txt**: Standard requirements file
- **requirements-*.txt**: Environment-specific requirements
- **req-*.txt**: Alternative naming pattern
- **deps.txt**: Dependencies file

## Usage Guide

### Setting Up Environments

#### Option 1: Automatic Discovery
1. Create a virtual environment in your task folder:
   ```bash
   cd tasks/my_task
   python -m venv venv
   ```

2. Create a requirements.txt file:
   ```txt
   pandas==2.0.3
   requests==2.31.0
   ```

3. The system will automatically discover and register them.

#### Option 2: Manual Configuration
1. Go to the admin panel → Tasks
2. Click "Environment Manager"
3. View discovered environments and requirements
4. Configure tasks to use specific environments

### Configuring Tasks

#### Via Admin Panel
1. Go to Tasks → Edit Schedule
2. In the Environment Configuration section:
   - Select environment from dropdown
   - Select requirements file from dropdown
3. Save configuration

#### Via API
```bash
curl -X PUT "http://localhost:7000/api/tasks/1/schedule" \
  -H "Authorization: Basic YWRtaW46YWRtaW4xMjM=" \
  -H "Content-Type: application/json" \
  -d '{
    "environment_path": "./tasks/my_task/venv",
    "requirements_path": "./tasks/my_task/requirements.txt",
    "schedule_type": "daily",
    "schedule_config": {"hour": 9, "minute": 0}
  }'
```

### Creating Multi-File Task Projects

For complex tasks with multiple files:

```
tasks/
├── data_processing_project/
│   ├── __init__.py
│   ├── main.py              # Main execution file
│   ├── data_loader.py       # Data loading utilities
│   ├── processors.py        # Data processing logic
│   ├── venv/                # Project environment
│   └── requirements.txt     # Project dependencies
```

The system will:
- Detect the project structure
- Identify `main.py` as the execution file
- Register the entire project as a task
- Use the project's environment and requirements

## API Endpoints

### Environment Management

#### Get Environments
```http
GET /api/tasks/environments
Authorization: Basic <credentials>
```

Response:
```json
{
  "environments": [
    {
      "name": "task1_venv",
      "path": "/path/to/tasks/task1/venv",
      "task_folder": "task1",
      "python_executable": "/path/to/tasks/task1/venv/bin/python"
    }
  ]
}
```

#### Get Requirements Files
```http
GET /api/tasks/requirements
Authorization: Basic <credentials>
```

Response:
```json
{
  "requirements_files": [
    {
      "name": "task1_requirements.txt",
      "path": "/path/to/tasks/task1/requirements.txt",
      "task_folder": "task1",
      "size": 1024
    }
  ]
}
```

#### Get Task Projects
```http
GET /api/tasks/projects
Authorization: Basic <credentials>
```

Response:
```json
{
  "task_projects": [
    {
      "name": "data_processing_project",
      "path": "/path/to/tasks/data_processing_project",
      "main_file": "data_processing_project/main.py",
      "file_count": 5,
      "files": ["main.py", "data_loader.py", "processors.py"],
      "is_package": true
    }
  ]
}
```

#### Validate Environment
```http
POST /api/tasks/validate-environment
Authorization: Basic <credentials>
Content-Type: application/json

{
  "environment_path": "/path/to/venv",
  "requirements_path": "/path/to/requirements.txt"
}
```

Response:
```json
{
  "valid": true,
  "python_executable": "/path/to/venv/bin/python",
  "errors": [],
  "warnings": []
}
```

## Best Practices

### 1. Environment Organization
- Keep environments close to their tasks
- Use descriptive environment names
- Group related tasks in the same environment

### 2. Requirements Management
- Pin specific versions for reproducibility
- Use separate requirements files for different environments
- Document dependencies clearly

### 3. Task Structure
- Use clear, descriptive task names
- Organize multi-file tasks as packages
- Keep main execution logic in `main.py` or `task.py`

### 4. Security Considerations
- Don't include sensitive data in requirements files
- Use environment variables for secrets
- Regularly update dependencies for security patches

## Troubleshooting

### Common Issues

#### Environment Not Found
- Check that the virtual environment exists
- Verify the path is correct
- Ensure the environment has the required structure

#### Requirements Installation Fails
- Check requirements.txt syntax
- Verify all packages are available
- Check for version conflicts

#### Task Execution Fails
- Verify the environment is valid
- Check that all dependencies are installed
- Review task logs for specific errors

### Debugging Commands

#### Validate Environment Manually
```bash
# Check if environment exists
ls -la /path/to/venv/

# Test Python executable
/path/to/venv/bin/python --version

# Test requirements installation
/path/to/venv/bin/pip install -r requirements.txt
```

#### Check System Logs
```bash
# View application logs
tail -f logs/app.log

# View task-specific logs
tail -f logs/task_<id>_<name>_<timestamp>.log
```

## Migration Guide

### From Single Environment
If you're upgrading from the single-environment version:

1. **Backup your current setup**
2. **Create virtual environments** for existing tasks
3. **Move requirements** to task-specific files
4. **Update task configurations** to use new environments
5. **Test thoroughly** before deploying

### Example Migration
```bash
# Before: Single requirements.txt
# After: Task-specific environments

# Create environment for existing task
cd tasks/existing_task
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r ../../requirements.txt

# Create task-specific requirements
pip freeze > requirements.txt
```

## Performance Considerations

### Environment Startup Time
- Virtual environments add ~1-2 seconds to task startup
- Requirements installation adds time based on package count
- Consider pre-installing common dependencies

### Resource Usage
- Each environment uses additional disk space
- Memory usage is similar to single environment
- CPU usage is minimal during environment activation

### Optimization Tips
- Use shared environments for similar tasks
- Pre-install common dependencies
- Use requirements caching when possible
- Monitor environment sizes and clean up unused ones

## Future Enhancements

### Planned Features
- **Docker Support**: Container-based task execution
- **Conda Environments**: Support for Conda environments
- **Dependency Caching**: Faster requirements installation
- **Environment Templates**: Pre-configured environment templates
- **Auto-scaling**: Dynamic environment creation and cleanup

### Contributing
To contribute to environment management features:

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests for new functionality
5. Submit a pull request

## Conclusion

The environment management system provides a robust solution for running tasks with different dependencies in isolation. This enables more complex workflows and prevents dependency conflicts while maintaining the simplicity of the CronPilot interface.

For support and questions, please refer to the main documentation or open an issue on GitHub.
