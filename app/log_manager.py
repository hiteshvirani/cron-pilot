import os
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any
from app.config import config
import threading
import time

class LogManager:
    def __init__(self):
        self.log_dir = Path(config.logging_config.get('log_dir', './logs'))
        self.retention_days = config.logging_config.get('retention_days', 7)
        self.max_log_size_mb = config.logging_config.get('max_log_size_mb', 10)
        
        # Ensure log directory exists
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup cleanup thread
        self._setup_cleanup_thread()
    
    def _setup_cleanup_thread(self):
        """Setup background thread for log cleanup"""
        def cleanup_worker():
            while True:
                try:
                    self.cleanup_old_logs()
                    # Run cleanup every 24 hours
                    time.sleep(24 * 60 * 60)
                except Exception as e:
                    print(f"Error in log cleanup: {e}")
                    time.sleep(60)  # Wait 1 minute before retrying
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
    
    def create_task_logger(self, task_id: int, task_name: str) -> tuple[logging.Logger, str]:
        """Create a logger for a specific task execution"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"task_{task_id}_{task_name}_{timestamp}.log"
        log_file_path = self.log_dir / log_filename
        
        # Create logger
        logger = logging.getLogger(f"task_{task_id}_{timestamp}")
        logger.setLevel(logging.INFO)
        
        # Clear any existing handlers
        logger.handlers.clear()
        
        # Create file handler
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(file_handler)
        
        return logger, str(log_file_path)
    
    def get_log_content(self, log_file_path: str, lines: Optional[int] = None) -> str:
        """Get log content from file"""
        try:
            if not os.path.exists(log_file_path):
                return "Log file not found"
            
            with open(log_file_path, 'r') as f:
                if lines:
                    # Get last N lines
                    all_lines = f.readlines()
                    return ''.join(all_lines[-lines:])
                else:
                    return f.read()
        except Exception as e:
            return f"Error reading log file: {str(e)}"
    
    def get_log_stats(self, log_file_path: str) -> Dict[str, Any]:
        """Get log file statistics"""
        try:
            if not os.path.exists(log_file_path):
                return {"error": "Log file not found"}
            
            stat = os.stat(log_file_path)
            return {
                "size_bytes": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "created_at": datetime.fromtimestamp(stat.st_ctime),
                "modified_at": datetime.fromtimestamp(stat.st_mtime),
                "exists": True
            }
        except Exception as e:
            return {"error": str(e)}
    
    def delete_log(self, log_file_path: str) -> bool:
        """Delete a log file"""
        try:
            if os.path.exists(log_file_path):
                os.remove(log_file_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting log file {log_file_path}: {e}")
            return False
    
    def cleanup_old_logs(self):
        """Clean up logs older than retention_days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            deleted_count = 0
            
            for log_file in self.log_dir.glob("*.log"):
                try:
                    file_stat = log_file.stat()
                    file_date = datetime.fromtimestamp(file_stat.st_mtime)
                    
                    if file_date < cutoff_date:
                        log_file.unlink()
                        deleted_count += 1
                except Exception as e:
                    print(f"Error processing log file {log_file}: {e}")
            
            if deleted_count > 0:
                print(f"Cleaned up {deleted_count} old log files")
                
        except Exception as e:
            print(f"Error during log cleanup: {e}")
    
    def get_all_logs(self) -> list[Dict[str, Any]]:
        """Get list of all log files with metadata"""
        logs = []
        
        try:
            for log_file in self.log_dir.glob("*.log"):
                try:
                    stat = log_file.stat()
                    logs.append({
                        "filename": log_file.name,
                        "path": str(log_file),
                        "size_bytes": stat.st_size,
                        "size_mb": round(stat.st_size / (1024 * 1024), 2),
                        "created_at": datetime.fromtimestamp(stat.st_ctime),
                        "modified_at": datetime.fromtimestamp(stat.st_mtime)
                    })
                except Exception as e:
                    print(f"Error processing log file {log_file}: {e}")
            
            # Sort by modification time (newest first)
            logs.sort(key=lambda x: x["modified_at"], reverse=True)
            
        except Exception as e:
            print(f"Error getting log files: {e}")
        
        return logs
    
    def rotate_log_if_needed(self, log_file_path: str) -> bool:
        """Rotate log file if it exceeds max size"""
        try:
            if not os.path.exists(log_file_path):
                return False
            
            stat = os.stat(log_file_path)
            size_mb = stat.st_size / (1024 * 1024)
            
            if size_mb > self.max_log_size_mb:
                # Create backup filename
                backup_path = f"{log_file_path}.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                os.rename(log_file_path, backup_path)
                return True
            
            return False
        except Exception as e:
            print(f"Error rotating log file {log_file_path}: {e}")
            return False

# Global log manager instance
log_manager = LogManager() 