import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.models import EmailConfig, TaskEmail, Task, TaskRun
from app.config import config
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.config = None
        self._load_config()
    
    def _load_config(self):
        """Load email configuration from database"""
        try:
            from app.database import SessionLocal
            db = SessionLocal()
            try:
                self.config = db.query(EmailConfig).filter(EmailConfig.is_active == True).first()
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error loading email config: {e}")
            self.config = None
    
    def is_configured(self) -> bool:
        """Check if email is properly configured"""
        return (
            self.config is not None and
            self.config.smtp_host and
            self.config.smtp_port and
            self.config.username and
            self.config.password and
            self.config.from_email
        )
    
    def send_email(self, to_email: str, subject: str, body: str, html_body: Optional[str] = None) -> bool:
        """Send an email"""
        if not self.is_configured():
            logger.error("Email not configured")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.config.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add text and HTML parts
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
                if self.config.use_tls:
                    server.starttls()
                
                server.login(self.config.username, self.config.password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {e}")
            return False
    
    def send_task_notification(self, task_run: TaskRun, db: Session) -> bool:
        """Send notification for task completion"""
        if not self.is_configured():
            return False
        
        try:
            # Get task and its email configurations
            task = db.query(Task).filter(Task.id == task_run.task_id).first()
            if not task:
                return False
            
            task_emails = db.query(TaskEmail).filter(TaskEmail.task_id == task.id).all()
            if not task_emails:
                return False
            
            # Determine if we should send notification
            should_send = False
            if task_run.status == "success":
                should_send = any(email.notify_on_success for email in task_emails)
            elif task_run.status == "failed":
                should_send = any(email.notify_on_failure for email in task_emails)
            
            if not should_send:
                return False
            
            # Prepare email content
            subject = f"Task Notification: {task.name} - {task_run.status.upper()}"
            
            # Calculate duration
            duration = "N/A"
            if task_run.duration_seconds:
                duration = f"{task_run.duration_seconds:.2f} seconds"
            
            # Create email body
            body = f"""
Task Execution Report

Task: {task.name}
Status: {task_run.status.upper()}
Started: {task_run.started_at}
Completed: {task_run.completed_at}
Duration: {duration}

"""
            
            if task_run.error_message:
                body += f"Error: {task_run.error_message}\n"
            
            if task_run.logs_file_path:
                body += f"Logs: Available in admin panel\n"
            
            # Create HTML version
            html_body = f"""
<html>
<body>
<h2>Task Execution Report</h2>
<table>
<tr><td><strong>Task:</strong></td><td>{task.name}</td></tr>
<tr><td><strong>Status:</strong></td><td>{task_run.status.upper()}</td></tr>
<tr><td><strong>Started:</strong></td><td>{task_run.started_at}</td></tr>
<tr><td><strong>Completed:</strong></td><td>{task_run.completed_at}</td></tr>
<tr><td><strong>Duration:</strong></td><td>{duration}</td></tr>
</table>
"""
            
            if task_run.error_message:
                html_body += f"<p><strong>Error:</strong> {task_run.error_message}</p>"
            
            if task_run.logs_file_path:
                html_body += "<p><strong>Logs:</strong> Available in admin panel</p>"
            
            html_body += "</body></html>"
            
            # Send to all configured emails
            success_count = 0
            for task_email in task_emails:
                if (
                    (task_run.status == "success" and task_email.notify_on_success) or
                    (task_run.status == "failed" and task_email.notify_on_failure)
                ):
                    if self.send_email(task_email.email_address, subject, body, html_body):
                        success_count += 1
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error sending task notification: {e}")
            return False
    
    def send_custom_email(self, to_emails: List[str], subject: str, body: str, html_body: Optional[str] = None) -> Dict[str, Any]:
        """Send custom email to multiple recipients"""
        if not self.is_configured():
            return {"success": False, "error": "Email not configured"}
        
        results = {
            "success": True,
            "sent": [],
            "failed": []
        }
        
        for email in to_emails:
            if self.send_email(email, subject, body, html_body):
                results["sent"].append(email)
            else:
                results["failed"].append(email)
                results["success"] = False
        
        return results
    
    def test_connection(self) -> Dict[str, Any]:
        """Test email configuration"""
        if not self.is_configured():
            return {"success": False, "error": "Email not configured"}
        
        try:
            with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
                if self.config.use_tls:
                    server.starttls()
                
                server.login(self.config.username, self.config.password)
                
                return {
                    "success": True,
                    "message": "Email configuration is working correctly"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# Global email service instance
email_service = EmailService() 