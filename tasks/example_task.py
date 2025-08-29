"""
Example Task - Demonstrates basic task functionality

This task shows how to:
1. Use the centralized email system
2. Handle configuration parameters
3. Log information
4. Return results
"""

from typing import Dict, Any
import logging
import time
from datetime import datetime

def run_task(config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Main task function that will be executed by the scheduler.
    
    Args:
        config: Optional configuration dictionary with parameters like:
            - send_email: Whether to send email notification
            - email_recipients: List of email addresses to notify
            - delay_seconds: How long to wait (for testing)
            - message: Custom message to include in logs
    
    Returns:
        Dict with execution results
    """
    logger = logging.getLogger(__name__)
    
    # Default configuration
    default_config = {
        "send_email": False,
        "email_recipients": [],
        "delay_seconds": 2,
        "message": "Hello from example task!"
    }
    
    # Merge with provided config
    if config:
        default_config.update(config)
    
    try:
        logger.info("Starting example task execution")
        logger.info(f"Configuration: {default_config}")
        
        # Simulate some work
        logger.info(f"Processing task with message: {default_config['message']}")
        
        if default_config['delay_seconds'] > 0:
            logger.info(f"Waiting for {default_config['delay_seconds']} seconds...")
            time.sleep(default_config['delay_seconds'])
        
        # Simulate some data processing
        processed_items = 42
        logger.info(f"Processed {processed_items} items")
        
        # Example of using the email system
        if default_config['send_email'] and default_config['email_recipients']:
            logger.info("Sending email notifications...")
            # The email service will be called automatically by the task executor
            # You can also access it directly if needed:
            # from app.email_service import email_service
            # email_service.send_custom_email(...)
        
        # Prepare result
        result = {
            "status": "success",
            "message": "Example task completed successfully",
            "processed_items": processed_items,
            "timestamp": datetime.now().isoformat(),
            "config_used": default_config
        }
        
        logger.info(f"Task completed successfully: {result}")
        return result
        
    except Exception as e:
        error_msg = f"Example task failed: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": error_msg,
            "timestamp": datetime.now().isoformat()
        } 