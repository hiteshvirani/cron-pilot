"""
Environment Demo Task - Demonstrates environment isolation

This task shows how different tasks can use different environments
and dependencies without conflicts. This task requires pandas and requests.
"""

from typing import Dict, Any
import logging
import time
from datetime import datetime

def run_task(config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Demo task that uses pandas and requests to demonstrate environment isolation.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Dict with execution results
    """
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting environment demo task")
        logger.info("This task demonstrates environment isolation")
        
        # Test pandas import (this will only work if pandas is installed in the environment)
        try:
            import pandas as pd
            logger.info(f"✅ Pandas imported successfully: {pd.__version__}")
            
            # Create a simple DataFrame
            data = {
                'name': ['Alice', 'Bob', 'Charlie'],
                'age': [25, 30, 35],
                'city': ['New York', 'London', 'Paris']
            }
            df = pd.DataFrame(data)
            logger.info(f"✅ Created DataFrame with {len(df)} rows")
            
        except ImportError as e:
            logger.error(f"❌ Pandas not available in this environment: {e}")
            return {
                "status": "error",
                "message": "Pandas not available - environment not properly configured",
                "timestamp": datetime.now().isoformat()
            }
        
        # Test requests import
        try:
            import requests
            logger.info(f"✅ Requests imported successfully: {requests.__version__}")
            
            # Make a simple HTTP request
            response = requests.get('https://httpbin.org/json', timeout=5)
            if response.status_code == 200:
                logger.info("✅ HTTP request successful")
            else:
                logger.warning(f"HTTP request returned status {response.status_code}")
                
        except ImportError as e:
            logger.error(f"❌ Requests not available in this environment: {e}")
            return {
                "status": "error",
                "message": "Requests not available - environment not properly configured",
                "timestamp": datetime.now().isoformat()
            }
        
        # Simulate some work
        logger.info("Processing data...")
        time.sleep(2)
        
        # Calculate some statistics
        avg_age = df['age'].mean()
        logger.info(f"Average age: {avg_age:.1f}")
        
        # Prepare result
        result = {
            "status": "success",
            "message": "Environment demo task completed successfully",
            "pandas_version": pd.__version__,
            "requests_version": requests.__version__,
            "data_processed": len(df),
            "average_age": avg_age,
            "environment_info": {
                "task_name": "environment_demo_task",
                "execution_time": datetime.now().isoformat(),
                "dependencies_verified": ["pandas", "requests"]
            }
        }
        
        logger.info(f"Task completed successfully: {result}")
        return result
        
    except Exception as e:
        error_msg = f"Environment demo task failed: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": error_msg,
            "timestamp": datetime.now().isoformat()
        }
