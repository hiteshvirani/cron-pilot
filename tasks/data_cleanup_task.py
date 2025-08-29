"""
Data Cleanup Task - Example of a maintenance task

This task demonstrates:
1. File system operations
2. Data cleanup logic
3. Error handling
4. Progress logging
"""

from typing import Dict, Any
import logging
import os
import glob
from datetime import datetime, timedelta
import shutil

def run_task(config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Data cleanup task that removes old temporary files.
    
    Args:
        config: Optional configuration dictionary with parameters like:
            - temp_directories: List of directories to clean
            - max_age_days: Maximum age of files to keep
            - file_patterns: File patterns to match (e.g., "*.tmp")
            - dry_run: If True, don't actually delete files
    
    Returns:
        Dict with cleanup results
    """
    logger = logging.getLogger(__name__)
    
    # Default configuration
    default_config = {
        "temp_directories": ["/tmp", "./temp"],
        "max_age_days": 7,
        "file_patterns": ["*.tmp", "*.log", "*.cache"],
        "dry_run": True  # Safety first!
    }
    
    # Merge with provided config
    if config:
        default_config.update(config)
    
    try:
        logger.info("Starting data cleanup task")
        logger.info(f"Configuration: {default_config}")
        
        total_files_found = 0
        total_files_deleted = 0
        total_size_freed = 0
        errors = []
        
        cutoff_date = datetime.now() - timedelta(days=default_config['max_age_days'])
        logger.info(f"Removing files older than: {cutoff_date}")
        
        for directory in default_config['temp_directories']:
            if not os.path.exists(directory):
                logger.warning(f"Directory does not exist: {directory}")
                continue
            
            logger.info(f"Processing directory: {directory}")
            
            for pattern in default_config['file_patterns']:
                pattern_path = os.path.join(directory, pattern)
                matching_files = glob.glob(pattern_path)
                
                for file_path in matching_files:
                    try:
                        # Get file stats
                        stat = os.stat(file_path)
                        file_age = datetime.fromtimestamp(stat.st_mtime)
                        file_size = stat.st_size
                        
                        total_files_found += 1
                        
                        if file_age < cutoff_date:
                            if default_config['dry_run']:
                                logger.info(f"[DRY RUN] Would delete: {file_path} (age: {file_age})")
                            else:
                                if os.path.isfile(file_path):
                                    os.remove(file_path)
                                elif os.path.isdir(file_path):
                                    shutil.rmtree(file_path)
                                
                                total_files_deleted += 1
                                total_size_freed += file_size
                                logger.info(f"Deleted: {file_path} (age: {file_age}, size: {file_size} bytes)")
                        else:
                            logger.debug(f"Keeping file (too new): {file_path}")
                            
                    except Exception as e:
                        error_msg = f"Error processing {file_path}: {str(e)}"
                        logger.error(error_msg)
                        errors.append(error_msg)
        
        # Prepare result
        result = {
            "status": "success",
            "message": "Data cleanup completed",
            "total_files_found": total_files_found,
            "total_files_deleted": total_files_deleted,
            "total_size_freed_bytes": total_size_freed,
            "total_size_freed_mb": round(total_size_freed / (1024 * 1024), 2),
            "errors": errors,
            "dry_run": default_config['dry_run'],
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Cleanup completed: {result}")
        return result
        
    except Exception as e:
        error_msg = f"Data cleanup task failed: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": error_msg,
            "timestamp": datetime.now().isoformat()
        } 