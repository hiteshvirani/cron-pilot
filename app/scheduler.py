from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from sqlalchemy.orm import Session
from app.models.models import Task, TaskRun, TaskStatus, ScheduleType
from app.task_executor import task_executor
from app.database import SessionLocal
from app.config import config
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class TaskScheduler:
    def __init__(self):
        # Configure job store
        jobstores = {
            'default': SQLAlchemyJobStore(url=config.database_url)
        }
        
        # Create scheduler
        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            timezone=config.scheduler_timezone,
            max_workers=config.scheduler_max_workers
        )
        
        self.scheduler.start()
        logger.info("Task scheduler started")
    
    def add_task_to_scheduler(self, task: Task) -> bool:
        """Add a task to the scheduler"""
        try:
            # Remove existing job if any
            self.remove_task_from_scheduler(task)
            
            if task.schedule_type == ScheduleType.MANUAL.value:
                # Manual tasks don't need scheduling
                return True
            
            elif task.schedule_type == ScheduleType.HOURLY.value:
                # Run every hour
                self.scheduler.add_job(
                    func=self._execute_task_job,
                    trigger=IntervalTrigger(hours=1),
                    args=[task.id],
                    id=f"task_{task.id}",
                    name=f"Task: {task.name}",
                    replace_existing=True
                )
            
            elif task.schedule_type == ScheduleType.DAILY.value:
                # Parse schedule config for daily time
                schedule_config = json.loads(task.schedule_config) if task.schedule_config else {}
                hour = schedule_config.get('hour', 0)
                minute = schedule_config.get('minute', 0)
                
                self.scheduler.add_job(
                    func=self._execute_task_job,
                    trigger=CronTrigger(hour=hour, minute=minute),
                    args=[task.id],
                    id=f"task_{task.id}",
                    name=f"Task: {task.name}",
                    replace_existing=True
                )
            
            elif task.schedule_type == ScheduleType.WEEKLY.value:
                # Parse schedule config for weekly schedule
                schedule_config = json.loads(task.schedule_config) if task.schedule_config else {}
                day_of_week = schedule_config.get('day_of_week', 'mon')
                hour = schedule_config.get('hour', 0)
                minute = schedule_config.get('minute', 0)
                
                self.scheduler.add_job(
                    func=self._execute_task_job,
                    trigger=CronTrigger(day_of_week=day_of_week, hour=hour, minute=minute),
                    args=[task.id],
                    id=f"task_{task.id}",
                    name=f"Task: {task.name}",
                    replace_existing=True
                )
            
            elif task.schedule_type == ScheduleType.CUSTOM.value:
                # Parse custom cron expression
                schedule_config = json.loads(task.schedule_config) if task.schedule_config else {}
                cron_expression = schedule_config.get('cron_expression', '0 0 * * *')
                
                # Parse cron expression (minute hour day month day_of_week)
                parts = cron_expression.split()
                if len(parts) != 5:
                    raise ValueError("Invalid cron expression format")
                
                minute, hour, day, month, day_of_week = parts
                
                self.scheduler.add_job(
                    func=self._execute_task_job,
                    trigger=CronTrigger(
                        minute=minute,
                        hour=hour,
                        day=day,
                        month=month,
                        day_of_week=day_of_week
                    ),
                    args=[task.id],
                    id=f"task_{task.id}",
                    name=f"Task: {task.name}",
                    replace_existing=True
                )
            
            logger.info(f"Task {task.name} (ID: {task.id}) scheduled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error scheduling task {task.name}: {e}")
            return False
    
    def remove_task_from_scheduler(self, task: Task) -> bool:
        """Remove a task from the scheduler"""
        try:
            job_id = f"task_{task.id}"
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
                logger.info(f"Task {task.name} (ID: {task.id}) removed from scheduler")
            return True
        except Exception as e:
            logger.error(f"Error removing task {task.name} from scheduler: {e}")
            return False
    
    def _execute_task_job(self, task_id: int):
        """Job function that executes a task"""
        db = SessionLocal()
        try:
            # Get task
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                logger.error(f"Task with ID {task_id} not found")
                return
            
            if not task.is_active:
                logger.info(f"Task {task.name} is not active, skipping execution")
                return
            
            # Check if task is already running
            running_task = db.query(TaskRun).filter(
                TaskRun.task_id == task_id,
                TaskRun.status == TaskStatus.RUNNING.value
            ).first()
            
            if running_task:
                logger.warning(f"Task {task.name} is already running, skipping")
                return
            
            # Execute task
            logger.info(f"Executing scheduled task: {task.name}")
            task_executor.execute_task(task, db)
            
        except Exception as e:
            logger.error(f"Error in scheduled task execution for task ID {task_id}: {e}")
        finally:
            db.close()
    
    def get_next_run_time(self, task: Task) -> Optional[datetime]:
        """Get the next scheduled run time for a task"""
        try:
            job_id = f"task_{task.id}"
            job = self.scheduler.get_job(job_id)
            if job and job.next_run_time:
                return job.next_run_time
            return None
        except Exception as e:
            logger.error(f"Error getting next run time for task {task.name}: {e}")
            return None
    
    def get_job_status(self, task: Task) -> Dict[str, Any]:
        """Get the current status of a scheduled job"""
        try:
            job_id = f"task_{task.id}"
            job = self.scheduler.get_job(job_id)
            
            if not job:
                return {
                    "scheduled": False,
                    "next_run": None,
                    "status": "not_scheduled"
                }
            
            return {
                "scheduled": True,
                "next_run": job.next_run_time,
                "status": "scheduled"
            }
            
        except Exception as e:
            logger.error(f"Error getting job status for task {task.name}: {e}")
            return {
                "scheduled": False,
                "next_run": None,
                "status": "error"
            }
    
    def pause_job(self, task: Task) -> bool:
        """Pause a scheduled job"""
        try:
            job_id = f"task_{task.id}"
            job = self.scheduler.get_job(job_id)
            if job:
                job.pause()
                logger.info(f"Task {task.name} paused")
                return True
            return False
        except Exception as e:
            logger.error(f"Error pausing task {task.name}: {e}")
            return False
    
    def resume_job(self, task: Task) -> bool:
        """Resume a paused job"""
        try:
            job_id = f"task_{task.id}"
            job = self.scheduler.get_job(job_id)
            if job:
                job.resume()
                logger.info(f"Task {task.name} resumed")
                return True
            return False
        except Exception as e:
            logger.error(f"Error resuming task {task.name}: {e}")
            return False
    
    def get_all_jobs(self) -> list[Dict[str, Any]]:
        """Get all scheduled jobs"""
        jobs = []
        try:
            for job in self.scheduler.get_jobs():
                jobs.append({
                    "id": job.id,
                    "name": job.name,
                    "next_run": job.next_run_time,
                    "trigger": str(job.trigger)
                })
        except Exception as e:
            logger.error(f"Error getting all jobs: {e}")
        
        return jobs
    
    def shutdown(self):
        """Shutdown the scheduler"""
        try:
            self.scheduler.shutdown()
            logger.info("Task scheduler shutdown")
        except Exception as e:
            logger.error(f"Error shutting down scheduler: {e}")

# Global scheduler instance
task_scheduler = TaskScheduler() 