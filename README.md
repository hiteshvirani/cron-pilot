# CronPilot - Task Scheduling & Management System

CronPilot is a comprehensive FastAPI-based task scheduling and management system that allows you to run, schedule, and monitor Python tasks with a beautiful web interface.

## 🚀 Features

- **Task Management**: Register, schedule, and manage Python tasks
- **Flexible Scheduling**: Support for manual, hourly, daily, weekly, and custom cron schedules
- **Real-time Logging**: Comprehensive logging with file-based storage and automatic cleanup
- **Email Notifications**: Centralized email system for task completion notifications
- **Web Admin Panel**: Modern, responsive web interface for task management
- **Dynamic Task Loading**: Automatically discover and load Python task files
- **Task Execution History**: Track task runs, status, and performance metrics
- **Log Management**: View, download, and manage log files with automatic rotation

## 📋 Requirements

- Python 3.8+
- FastAPI
- SQLAlchemy
- APScheduler
- Other dependencies (see requirements.txt)

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd CronPilot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the system**:
   Edit `config.yaml` to set your preferences:
   ```yaml
   admin:
     username: "admin"
     password: "your_secure_password"  # Change this!
   
   database:
     url: "sqlite:///./cronpilot.db"
   
   email:
     smtp_host: "smtp.gmail.com"
     smtp_port: 587
     username: "your_email@gmail.com"
     password: "your_app_password"
     from_email: "your_email@gmail.com"
   ```

4. **Run the application**:
   ```bash
   python -m app.main
   ```

5. **Access the admin panel**:
   Open your browser and go to `http://localhost:7000/admin`

## 📁 Project Structure

```
CronPilot/
├── app/                    # Main application code
│   ├── api/               # API endpoints
│   ├── models/            # Database models
│   ├── config.py          # Configuration management
│   ├── database.py        # Database setup
│   ├── email_service.py   # Email functionality
│   ├── log_manager.py     # Log management
│   ├── main.py            # FastAPI application
│   ├── scheduler.py       # Task scheduler
│   └── task_executor.py   # Task execution
├── tasks/                 # User task files
├── logs/                  # Task execution logs
├── templates/             # Admin panel templates
├── static/                # Static files
├── config.yaml           # Configuration file
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 📝 Creating Tasks

Tasks are Python files that follow a specific interface. Here's an example:

```python
# tasks/my_task.py
from typing import Dict, Any
import logging

def run_task(config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Main task function that will be executed by the scheduler.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Dict with execution results
    """
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting my task")
        
        # Your task logic here
        result = {"status": "success", "message": "Task completed"}
        
        logger.info("Task completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Task failed: {str(e)}")
        return {"status": "error", "message": str(e)}
```

### Task Requirements

1. **File Location**: Place task files in the `tasks/` directory
2. **Function Name**: Must have a `run_task` function
3. **Function Signature**: `def run_task(config: Dict[str, Any] = None) -> Dict[str, Any]`
4. **Return Value**: Must return a dictionary with at least a `status` key

## 🔧 Configuration

### Schedule Types

- **Manual**: Run tasks only when manually triggered
- **Hourly**: Run every hour
- **Daily**: Run daily at a specific time
- **Weekly**: Run weekly on a specific day and time
- **Custom**: Use custom cron expressions

### Email Configuration

Configure email settings in `config.yaml`:

```yaml
email:
  smtp_host: "smtp.gmail.com"
  smtp_port: 587
  username: "your_email@gmail.com"
  password: "your_app_password"  # Use app password for Gmail
  from_email: "your_email@gmail.com"
  use_tls: true
```

### Log Management

```yaml
logging:
  retention_days: 7          # Keep logs for 7 days
  log_dir: "./logs"          # Log directory
  max_log_size_mb: 10        # Max log file size
```

## 🌐 API Endpoints

### Authentication
All endpoints require HTTP Basic Authentication with admin credentials.

### Task Management
- `GET /api/tasks` - List all tasks
- `POST /api/tasks/register` - Register a new task
- `POST /api/tasks/{task_id}/run` - Manually run a task
- `PUT /api/tasks/{task_id}/schedule` - Update task schedule
- `GET /api/tasks/{task_id}/runs` - Get task execution history
- `DELETE /api/tasks/{task_id}` - Delete a task

### Log Management
- `GET /api/logs` - List all log files
- `GET /api/logs/{log_id}/content` - Get log content
- `GET /api/logs/download/{log_id}` - Download log file
- `DELETE /api/logs/{log_id}` - Delete log file
- `POST /api/logs/cleanup` - Manually trigger log cleanup

### Admin Panel
- `GET /admin` - Dashboard
- `GET /admin/tasks` - Task management page
- `GET /admin/logs` - Log management page
- `GET /admin/email` - Email configuration page
- `GET /admin/settings` - System settings page

## 📊 Admin Panel Features

### Dashboard
- System statistics
- Recent task activity
- Quick actions
- System status

### Task Management
- View all tasks with status
- Manual task execution
- Schedule configuration
- Task history and logs

### Log Management
- Browse log files
- View log content
- Download logs
- Delete old logs

### Email Configuration
- Configure SMTP settings
- Test email configuration
- Manage task email notifications

## 🔒 Security

- **Authentication**: HTTP Basic Authentication with configurable credentials
- **Task Isolation**: Tasks run in isolated environments
- **Input Validation**: All inputs are validated and sanitized
- **Error Handling**: Comprehensive error handling and logging

## 🚀 Deployment

### Development
```bash
python -m app.main
```

### Production
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker (Optional)
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🐛 Troubleshooting

### Common Issues

1. **Task not loading**: Ensure the task file has a `run_task` function
2. **Email not working**: Check SMTP settings and use app passwords for Gmail
3. **Database errors**: Ensure the database directory is writable
4. **Permission errors**: Check file permissions for logs and tasks directories

### Logs
- Application logs: Check console output
- Task logs: Available in the admin panel under Logs
- Database logs: Check SQLite database file

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the documentation
- Review the example tasks
- Check the logs for error messages
- Open an issue on GitHub

---

**CronPilot** - Making task scheduling simple and powerful! 🚀 