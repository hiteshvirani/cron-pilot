"""
Quick Test Task - 30 Seconds

A quick task that runs for 30 seconds with frequent progress updates.
Useful for testing the system without waiting too long.
"""

from typing import Dict, Any
import logging
import time
from datetime import datetime

def run_task(config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Quick test task that runs for 30 seconds.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Dict with execution results
    """
    logger = logging.getLogger(__name__)
    
    # Default configuration
    default_config = {
        "duration_seconds": 30,
        "progress_interval_seconds": 5,
        "message": "Quick test task is running!"
    }
    
    # Merge with provided config
    if config:
        default_config.update(config)
    
    try:
        duration_seconds = default_config["duration_seconds"]
        progress_interval = default_config["progress_interval_seconds"]
        
        logger.info(f"Starting quick test task")
        logger.info(f"Configuration: {default_config}")
        logger.info(f"Task will run for {duration_seconds} seconds")
        
        start_time = datetime.now()
        end_time = start_time.timestamp() + duration_seconds
        
        logger.info(f"Task started at: {start_time.strftime('%H:%M:%S')}")
        logger.info(f"Expected end time: {datetime.fromtimestamp(end_time).strftime('%H:%M:%S')}")
        
        # Print the main message
        print(f"🚀 {default_config['message']}")
        logger.info(f"Main message: {default_config['message']}")
        
        # Run for the specified duration with progress updates
        current_time = time.time()
        progress_count = 0
        
        while current_time < end_time:
            # Sleep for progress interval or remaining time
            sleep_time = min(progress_interval, end_time - current_time)
            time.sleep(sleep_time)
            
            current_time = time.time()
            progress_count += 1
            
            # Calculate progress percentage
            elapsed = current_time - start_time.timestamp()
            progress_percent = min(100, (elapsed / duration_seconds) * 100)
            
            # Progress message
            progress_msg = f"⏱️  Progress: {progress_percent:.1f}% ({elapsed:.0f}s / {duration_seconds}s)"
            print(progress_msg)
            logger.info(progress_msg)
            
            # Additional status messages
            if progress_count % 2 == 0:
                status_msg = f"📊 Update #{progress_count} - Still running..."
                print(status_msg)
                logger.info(status_msg)
            
            if progress_count % 3 == 0:
                time_msg = f"🕐 Time: {datetime.now().strftime('%H:%M:%S')}"
                print(time_msg)
                logger.info(time_msg)
        
        # Task completed
        actual_duration = time.time() - start_time.timestamp()
        completion_msg = f"✅ Quick test completed! Duration: {actual_duration:.2f} seconds"
        print(completion_msg)
        logger.info(completion_msg)
        
        # Prepare result
        result = {
            "status": "success",
            "message": "Quick test task completed successfully",
            "expected_duration_seconds": duration_seconds,
            "actual_duration_seconds": actual_duration,
            "progress_updates": progress_count,
            "start_time": start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "main_message": default_config["message"]
        }
        
        logger.info(f"Task result: {result}")
        return result
        
    except Exception as e:
        error_msg = f"Quick test task failed: {str(e)}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        return {
            "status": "error",
            "message": error_msg,
            "timestamp": datetime.now().isoformat()
        } 