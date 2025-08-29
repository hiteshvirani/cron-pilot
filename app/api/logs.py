from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.database import get_db
from app.api.auth import get_current_admin
from app.log_manager import log_manager
import os

router = APIRouter(prefix="/api/logs", tags=["logs"])

@router.get("/")
def get_all_logs(
    current_admin: str = Depends(get_current_admin)
):
    """Get all log files"""
    try:
        logs = log_manager.get_all_logs()
        return {"logs": logs}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching logs: {str(e)}"
        )

@router.get("/{log_id}/content")
def get_log_content(
    log_id: str,
    lines: Optional[int] = None,
    current_admin: str = Depends(get_current_admin)
):
    """Get log file content"""
    try:
        # Find log file by ID (filename without extension)
        log_files = log_manager.get_all_logs()
        log_file = None
        
        for log in log_files:
            if log['filename'].replace('.log', '') == log_id:
                log_file = log
                break
        
        if not log_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Log file not found"
            )
        
        content = log_manager.get_log_content(log_file['path'], lines)
        
        return {
            "log_file": log_file,
            "content": content,
            "lines_requested": lines
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reading log file: {str(e)}"
        )

@router.get("/download/{log_id}")
def download_log(
    log_id: str,
    current_admin: str = Depends(get_current_admin)
):
    """Download a log file"""
    try:
        # Find log file by ID
        log_files = log_manager.get_all_logs()
        log_file = None
        
        for log in log_files:
            if log['filename'].replace('.log', '') == log_id:
                log_file = log
                break
        
        if not log_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Log file not found"
            )
        
        if not os.path.exists(log_file['path']):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Log file does not exist on disk"
            )
        
        return FileResponse(
            path=log_file['path'],
            filename=log_file['filename'],
            media_type='text/plain'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error downloading log file: {str(e)}"
        )

@router.delete("/{log_id}")
def delete_log(
    log_id: str,
    current_admin: str = Depends(get_current_admin)
):
    """Delete a log file"""
    try:
        # Find log file by ID
        log_files = log_manager.get_all_logs()
        log_file = None
        
        for log in log_files:
            if log['filename'].replace('.log', '') == log_id:
                log_file = log
                break
        
        if not log_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Log file not found"
            )
        
        success = log_manager.delete_log(log_file['path'])
        
        if success:
            return {"message": "Log file deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete log file"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting log file: {str(e)}"
        )

@router.post("/cleanup")
def cleanup_old_logs(
    current_admin: str = Depends(get_current_admin)
):
    """Manually trigger log cleanup"""
    try:
        log_manager.cleanup_old_logs()
        return {"message": "Log cleanup completed"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during log cleanup: {str(e)}"
        )

@router.get("/stats")
def get_log_stats(
    current_admin: str = Depends(get_current_admin)
):
    """Get log statistics"""
    try:
        logs = log_manager.get_all_logs()
        
        total_files = len(logs)
        total_size_mb = sum(log['size_mb'] for log in logs)
        
        # Group by date
        from datetime import datetime
        from collections import defaultdict
        
        daily_stats = defaultdict(lambda: {"count": 0, "size_mb": 0})
        
        for log in logs:
            date_str = log['created_at'].strftime('%Y-%m-%d')
            daily_stats[date_str]["count"] += 1
            daily_stats[date_str]["size_mb"] += log['size_mb']
        
        return {
            "total_files": total_files,
            "total_size_mb": round(total_size_mb, 2),
            "daily_stats": dict(daily_stats)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting log stats: {str(e)}"
        ) 