from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.database import get_db
from app.api.auth import get_current_admin
from app.models.models import Task, TaskRun, ScheduleType, TaskStatus
from app.task_executor import task_executor
from app.scheduler import task_scheduler
from app.log_manager import log_manager
from app.environment_manager import environment_manager
import json
from datetime import datetime

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

@router.get("/")
def get_tasks(
    current_admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all tasks"""
    try:
        tasks = db.query(Task).all()
        result = []
        
        for task in tasks:
            # Get latest run
            latest_run = db.query(TaskRun).filter(
                TaskRun.task_id == task.id
            ).order_by(TaskRun.created_at.desc()).first()
            
            # Get next run time
            next_run = task_scheduler.get_next_run_time(task)
            
            # Get job status
            job_status = task_scheduler.get_job_status(task)
            
            task_data = {
                "id": task.id,
                "name": task.name,
                "module_name": task.module_name,
                "description": task.description,
                "file_path": task.file_path,
                "schedule_type": task.schedule_type,
                "schedule_config": task.schedule_config,
                "is_active": task.is_active,
                "created_at": task.created_at,
                "updated_at": task.updated_at,
                "latest_run": {
                    "status": latest_run.status if latest_run else None,
                    "started_at": latest_run.started_at if latest_run else None,
                    "completed_at": latest_run.completed_at if latest_run else None,
                    "duration_seconds": latest_run.duration_seconds if latest_run else None,
                    "error_message": latest_run.error_message if latest_run else None
                } if latest_run else None,
                "next_run": next_run,
                "job_status": job_status
            }
            result.append(task_data)
        
        return {"tasks": result}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching tasks: {str(e)}"
        )

@router.get("/discover")
def discover_tasks(
    current_admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Discover new task files"""
    try:
        from app.config import config
        discovered = task_executor.discover_tasks(config.tasks_directory)
        
        # Check which ones are already registered
        existing_tasks = db.query(Task).all()
        existing_names = {task.name for task in existing_tasks}
        
        new_tasks = []
        for task_info in discovered:
            if task_info['name'] not in existing_names:
                new_tasks.append(task_info)
        
        return {
            "discovered_tasks": discovered,
            "new_tasks": new_tasks,
            "existing_tasks": list(existing_names)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error discovering tasks: {str(e)}"
        )

@router.get("/environments")
def get_environments(
    current_admin: str = Depends(get_current_admin)
):
    """Get all discovered environments"""
    try:
        environments = environment_manager.discover_environments()
        return {"environments": environments}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error discovering environments: {str(e)}"
        )

@router.get("/requirements")
def get_requirements_files(
    current_admin: str = Depends(get_current_admin)
):
    """Get all discovered requirements files"""
    try:
        requirements_files = environment_manager.discover_requirements_files()
        return {"requirements_files": requirements_files}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error discovering requirements files: {str(e)}"
        )

@router.get("/projects")
def get_task_projects(
    current_admin: str = Depends(get_current_admin)
):
    """Get all discovered task projects"""
    try:
        task_projects = environment_manager.discover_task_projects()
        return {"task_projects": task_projects}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error discovering task projects: {str(e)}"
        )

@router.post("/validate-environment")
def validate_environment(
    env_data: Dict[str, Any],
    current_admin: str = Depends(get_current_admin)
):
    """Validate an environment and requirements"""
    try:
        env_path = env_data.get("environment_path")
        requirements_path = env_data.get("requirements_path")
        
        if not env_path:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Environment path is required"
            )
        
        validation_result = environment_manager.validate_environment(env_path, requirements_path)
        return validation_result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating environment: {str(e)}"
        )

@router.post("/register")
def register_task(
    task_data: Dict[str, Any],
    current_admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Register a new task"""
    try:
        # Validate task file
        validation = task_executor.validate_task_file(task_data['file_path'])
        if not validation['valid']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid task file: {validation['error']}"
            )
        
        # Check if task already exists
        existing_task = db.query(Task).filter(Task.name == task_data['name']).first()
        if existing_task:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task with this name already exists"
            )
        
        # Create new task
        task = Task(
            name=task_data['name'],
            file_path=task_data['file_path'],
            module_name=validation['module_name'],
            description=task_data.get('description', validation.get('description', '')),
            schedule_type=task_data.get('schedule_type', ScheduleType.MANUAL.value),
            schedule_config=json.dumps(task_data.get('schedule_config', {})) if task_data.get('schedule_config') else None,
            is_active=task_data.get('is_active', True)
        )
        
        db.add(task)
        db.commit()
        db.refresh(task)
        
        # Add to scheduler if not manual
        if task.schedule_type != ScheduleType.MANUAL.value:
            task_scheduler.add_task_to_scheduler(task)
        
        return {"message": "Task registered successfully", "task_id": task.id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registering task: {str(e)}"
        )

@router.post("/{task_id}/run")
def run_task(
    task_id: int,
    config: Optional[Dict[str, Any]] = None,
    current_admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Manually run a task"""
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Check if task is already running
        running_task = db.query(TaskRun).filter(
            TaskRun.task_id == task_id,
            TaskRun.status == TaskStatus.RUNNING.value
        ).first()
        
        if running_task:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task is already running"
            )
        
        # Execute task
        task_run = task_executor.execute_task(task, db, config)
        
        return {
            "message": "Task execution started",
            "task_run_id": task_run.id,
            "status": task_run.status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error running task: {str(e)}"
        )

@router.put("/{task_id}/schedule")
def update_task_schedule(
    task_id: int,
    schedule_data: Dict[str, Any],
    current_admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update task schedule and environment configuration"""
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Update schedule
        task.schedule_type = schedule_data.get('schedule_type', task.schedule_type)
        task.schedule_config = json.dumps(schedule_data.get('schedule_config', {})) if schedule_data.get('schedule_config') else None
        task.is_active = schedule_data.get('is_active', task.is_active)
        
        # Update environment configuration
        task.environment_path = schedule_data.get('environment_path', task.environment_path)
        task.requirements_path = schedule_data.get('requirements_path', task.requirements_path)
        
        # Update python executable if environment is specified
        if task.environment_path:
            validation = environment_manager.validate_environment(task.environment_path, task.requirements_path)
            if validation["valid"]:
                task.python_executable = validation["python_executable"]
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Environment validation failed: {validation['errors']}"
                )
        else:
            task.python_executable = None
        
        task.updated_at = datetime.utcnow()
        
        db.commit()
        
        # Update scheduler
        if task.schedule_type == ScheduleType.MANUAL.value:
            task_scheduler.remove_task_from_scheduler(task)
        else:
            task_scheduler.add_task_to_scheduler(task)
        
        return {"message": "Task configuration updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating task configuration: {str(e)}"
        )

@router.get("/{task_id}/runs")
def get_task_runs(
    task_id: int,
    limit: int = 10,
    current_admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get task execution history"""
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        runs = db.query(TaskRun).filter(
            TaskRun.task_id == task_id
        ).order_by(TaskRun.created_at.desc()).limit(limit).all()
        
        result = []
        for run in runs:
            run_data = {
                "id": run.id,
                "status": run.status,
                "started_at": run.started_at,
                "completed_at": run.completed_at,
                "duration_seconds": run.duration_seconds,
                "error_message": run.error_message,
                "logs_file_path": run.logs_file_path,
                "created_at": run.created_at
            }
            result.append(run_data)
        
        return {"task_runs": result}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching task runs: {str(e)}"
        )

@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    current_admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete a task"""
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Remove from scheduler
        task_scheduler.remove_task_from_scheduler(task)
        
        # Delete task (cascade will delete runs and emails)
        db.delete(task)
        db.commit()
        
        return {"message": "Task deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting task: {str(e)}"
        ) 