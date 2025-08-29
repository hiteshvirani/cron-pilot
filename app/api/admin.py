from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.database import get_db
from app.api.auth import get_current_admin
from app.models.models import Task, TaskRun, EmailConfig, TaskEmail
from app.scheduler import task_scheduler
from app.email_service import email_service
from app.log_manager import log_manager
import json
from datetime import datetime

router = APIRouter(tags=["admin"])

# Setup templates
templates = Jinja2Templates(directory="templates")

@router.get("/admin", response_class=HTMLResponse)
def admin_dashboard(
    request: Request,
    current_admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin dashboard page"""
    try:
        # Get basic stats
        total_tasks = db.query(Task).count()
        active_tasks = db.query(Task).filter(Task.is_active == True).count()
        total_runs = db.query(TaskRun).count()
        
        # Get recent runs
        recent_runs = db.query(TaskRun).order_by(TaskRun.created_at.desc()).limit(5).all()
        
        # Get log stats
        log_stats = log_manager.get_all_logs()
        total_logs = len(log_stats)
        total_log_size = sum(log['size_mb'] for log in log_stats)
        
        # Get email config status
        email_configured = email_service.is_configured()
        
        context = {
            "request": request,
            "admin_user": current_admin,
            "stats": {
                "total_tasks": total_tasks,
                "active_tasks": active_tasks,
                "total_runs": total_runs,
                "total_logs": total_logs,
                "total_log_size_mb": round(total_log_size, 2),
                "email_configured": email_configured
            },
            "recent_runs": recent_runs
        }
        
        return templates.TemplateResponse("dashboard.html", context)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading dashboard: {str(e)}"
        )

@router.get("/admin/tasks", response_class=HTMLResponse)
def admin_tasks(
    request: Request,
    current_admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Tasks management page"""
    try:
        tasks = db.query(Task).all()
        
        # Get additional info for each task
        for task in tasks:
            # Latest run
            latest_run = db.query(TaskRun).filter(
                TaskRun.task_id == task.id
            ).order_by(TaskRun.created_at.desc()).first()
            task.latest_run = latest_run
            
            # Next run time
            task.next_run = task_scheduler.get_next_run_time(task)
            
            # Job status
            task.job_status = task_scheduler.get_job_status(task)
        
        context = {
            "request": request,
            "admin_user": current_admin,
            "tasks": tasks
        }
        
        return templates.TemplateResponse("tasks.html", context)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading tasks page: {str(e)}"
        )

@router.get("/admin/logs", response_class=HTMLResponse)
def admin_logs(
    request: Request,
    current_admin: str = Depends(get_current_admin)
):
    """Logs management page"""
    try:
        logs = log_manager.get_all_logs()
        
        context = {
            "request": request,
            "admin_user": current_admin,
            "logs": logs
        }
        
        return templates.TemplateResponse("logs.html", context)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading logs page: {str(e)}"
        )

@router.get("/admin/email", response_class=HTMLResponse)
def admin_email(
    request: Request,
    current_admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Email configuration page"""
    try:
        email_config = db.query(EmailConfig).filter(EmailConfig.is_active == True).first()
        
        # Get task email configurations
        task_emails = db.query(TaskEmail).all()
        
        context = {
            "request": request,
            "admin_user": current_admin,
            "email_config": email_config,
            "task_emails": task_emails
        }
        
        return templates.TemplateResponse("email.html", context)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading email page: {str(e)}"
        )

@router.get("/admin/settings", response_class=HTMLResponse)
def admin_settings(
    request: Request,
    current_admin: str = Depends(get_current_admin)
):
    """Settings page"""
    try:
        from app.config import config
        
        context = {
            "request": request,
            "admin_user": current_admin,
            "config": {
                "admin_username": config.admin_username,
                "database_url": config.database_url,
                "scheduler_timezone": config.scheduler_timezone,
                "scheduler_max_workers": config.scheduler_max_workers,
                "logging_retention_days": config.logging_config.get('retention_days'),
                "tasks_directory": config.tasks_directory
            }
        }
        
        return templates.TemplateResponse("settings.html", context)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading settings page: {str(e)}"
        )

@router.get("/api/admin/stats")
def get_admin_stats(
    current_admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get admin dashboard statistics"""
    try:
        # Task stats
        total_tasks = db.query(Task).count()
        active_tasks = db.query(Task).filter(Task.is_active == True).count()
        manual_tasks = db.query(Task).filter(Task.schedule_type == 'manual').count()
        scheduled_tasks = total_tasks - manual_tasks
        
        # Run stats
        total_runs = db.query(TaskRun).count()
        successful_runs = db.query(TaskRun).filter(TaskRun.status == 'success').count()
        failed_runs = db.query(TaskRun).filter(TaskRun.status == 'failed').count()
        running_tasks = db.query(TaskRun).filter(TaskRun.status == 'running').count()
        
        # Log stats
        logs = log_manager.get_all_logs()
        total_logs = len(logs)
        total_log_size = sum(log['size_mb'] for log in logs)
        
        # Email stats
        email_configured = email_service.is_configured()
        total_task_emails = db.query(TaskEmail).count()
        
        # Recent activity
        recent_runs = db.query(TaskRun).order_by(TaskRun.created_at.desc()).limit(10).all()
        recent_activity = []
        
        for run in recent_runs:
            task = db.query(Task).filter(Task.id == run.task_id).first()
            recent_activity.append({
                "task_name": task.name if task else "Unknown",
                "status": run.status,
                "started_at": run.started_at,
                "duration": run.duration_seconds
            })
        
        return {
            "tasks": {
                "total": total_tasks,
                "active": active_tasks,
                "manual": manual_tasks,
                "scheduled": scheduled_tasks
            },
            "runs": {
                "total": total_runs,
                "successful": successful_runs,
                "failed": failed_runs,
                "running": running_tasks
            },
            "logs": {
                "total_files": total_logs,
                "total_size_mb": round(total_log_size, 2)
            },
            "email": {
                "configured": email_configured,
                "total_task_emails": total_task_emails
            },
            "recent_activity": recent_activity
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting admin stats: {str(e)}"
        )

@router.post("/api/admin/email/test")
def test_email_config(
    email_data: Dict[str, Any],
    current_admin: str = Depends(get_current_admin)
):
    """Test email configuration"""
    try:
        # Test the provided email configuration
        test_result = email_service.test_connection()
        
        if test_result["success"]:
            # Try to send a test email
            test_email_result = email_service.send_email(
                to_email=email_data.get("test_email"),
                subject="CronPilot - Email Test",
                body="This is a test email from CronPilot to verify email configuration.",
                html_body="<h2>CronPilot Email Test</h2><p>This is a test email to verify email configuration.</p>"
            )
            
            if test_email_result:
                return {"success": True, "message": "Email configuration test successful"}
            else:
                return {"success": False, "message": "Email configuration test failed"}
        else:
            return test_result
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error testing email configuration: {str(e)}"
        ) 