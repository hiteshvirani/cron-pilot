from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class TaskStatus(enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ScheduleType(enum.Enum):
    MANUAL = "manual"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    CUSTOM = "custom"

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    file_path = Column(String(500), nullable=False)
    module_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    schedule_type = Column(String(50), nullable=False, default=ScheduleType.MANUAL.value)
    schedule_config = Column(Text, nullable=True)  # JSON string for cron expression or schedule details
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    runs = relationship("TaskRun", back_populates="task", cascade="all, delete-orphan")
    emails = relationship("TaskEmail", back_populates="task", cascade="all, delete-orphan")

class TaskRun(Base):
    __tablename__ = "task_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    status = Column(String(50), nullable=False, default=TaskStatus.PENDING.value)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)
    logs_file_path = Column(String(500), nullable=True)
    scheduler_job_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    task = relationship("Task", back_populates="runs")

class EmailConfig(Base):
    __tablename__ = "email_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    smtp_host = Column(String(255), nullable=False)
    smtp_port = Column(Integer, nullable=False)
    username = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    from_email = Column(String(255), nullable=False)
    use_tls = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TaskEmail(Base):
    __tablename__ = "task_emails"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    email_address = Column(String(255), nullable=False)
    notify_on_success = Column(Boolean, default=True)
    notify_on_failure = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    task = relationship("Task", back_populates="emails") 