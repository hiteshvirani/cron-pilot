import importlib.util
import sys
import os
import traceback
import subprocess
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from sqlalchemy.orm import Session
from app.models.models import Task, TaskRun, TaskStatus
from app.log_manager import log_manager
from app.email_service import email_service
from app.environment_manager import environment_manager
import logging

logger = logging.getLogger(__name__)

class TaskExecutor:
    def __init__(self):
        self.loaded_modules = {}
    
    def load_task_module(self, task: Task) -> Optional[Callable]:
        """Dynamically load a task module"""
        try:
            # Check if module is already loaded
            if task.module_name in self.loaded_modules:
                return self.loaded_modules[task.module_name]
            
            # Load module from file
            spec = importlib.util.spec_from_file_location(task.module_name, task.file_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Could not load module from {task.file_path}")
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[task.module_name] = module
            spec.loader.exec_module(module)
            
            # Look for run_task function
            if hasattr(module, 'run_task'):
                self.loaded_modules[task.module_name] = module.run_task
                return module.run_task
            else:
                raise AttributeError(f"Module {task.module_name} does not have a 'run_task' function")
                
        except Exception as e:
            logger.error(f"Error loading task module {task.module_name}: {e}")
            return None
    
    def execute_task(self, task: Task, db: Session, config: Optional[Dict[str, Any]] = None) -> TaskRun:
        """Execute a task and return the task run record"""
        # Create task run record
        task_run = TaskRun(
            task_id=task.id,
            status=TaskStatus.RUNNING.value,
            started_at=datetime.utcnow()
        )
        db.add(task_run)
        db.commit()
        db.refresh(task_run)
        
        # Create logger for this execution
        task_logger, log_file_path = log_manager.create_task_logger(task.id, task.name)
        task_run.logs_file_path = log_file_path
        db.commit()
        
        try:
            task_logger.info(f"Starting task execution: {task.name}")
            
            # Handle environment setup if specified
            python_executable = None
            if task.environment_path:
                task_logger.info(f"Setting up environment: {task.environment_path}")
                
                # Validate environment
                env_validation = environment_manager.validate_environment(
                    task.environment_path, 
                    task.requirements_path
                )
                
                if not env_validation["valid"]:
                    raise Exception(f"Environment validation failed: {env_validation['errors']}")
                
                python_executable = env_validation["python_executable"]
                task_logger.info(f"Using Python executable: {python_executable}")
                
                # Install requirements if specified
                if task.requirements_path:
                    task_logger.info(f"Installing requirements from: {task.requirements_path}")
                    install_result = subprocess.run([
                        python_executable, "-m", "pip", "install", "-r", task.requirements_path
                    ], capture_output=True, text=True, timeout=300)
                    
                    if install_result.returncode != 0:
                        task_logger.warning(f"Requirements installation had issues: {install_result.stderr}")
                    else:
                        task_logger.info("Requirements installed successfully")
            
            # Execute task based on environment setup
            if python_executable:
                # Execute in isolated environment
                result = self._execute_task_in_environment(task, python_executable, config, task_logger)
            else:
                # Execute in current environment (legacy mode)
                run_function = self.load_task_module(task)
                if not run_function:
                    raise Exception(f"Could not load task module: {task.module_name}")
                
                task_logger.info(f"Task module loaded successfully: {task.module_name}")
                result = run_function(config or {})
            
            # Calculate duration
            end_time = datetime.utcnow()
            duration = (end_time - task_run.started_at).total_seconds()
            
            # Update task run record
            task_run.status = TaskStatus.SUCCESS.value
            task_run.completed_at = end_time
            task_run.duration_seconds = duration
            
            task_logger.info(f"Task completed successfully in {duration:.2f} seconds")
            task_logger.info(f"Task result: {result}")
            
            db.commit()
            
            # Send email notification
            try:
                email_service.send_task_notification(task_run, db)
            except Exception as e:
                task_logger.error(f"Failed to send email notification: {e}")
            
            return task_run
            
        except Exception as e:
            # Handle task execution error
            error_message = str(e)
            stack_trace = traceback.format_exc()
            
            task_logger.error(f"Task execution failed: {error_message}")
            task_logger.error(f"Stack trace: {stack_trace}")
            
            # Update task run record
            task_run.status = TaskStatus.FAILED.value
            task_run.completed_at = datetime.utcnow()
            task_run.error_message = error_message
            
            if task_run.started_at:
                duration = (task_run.completed_at - task_run.started_at).total_seconds()
                task_run.duration_seconds = duration
            
            db.commit()
            
            # Send email notification for failure
            try:
                email_service.send_task_notification(task_run, db)
            except Exception as email_error:
                task_logger.error(f"Failed to send failure email notification: {email_error}")
            
            return task_run
    
    def discover_tasks(self, tasks_directory: str) -> list[Dict[str, Any]]:
        """Discover Python files in tasks directory that could be tasks"""
        discovered_tasks = []
        
        try:
            if not os.path.exists(tasks_directory):
                return discovered_tasks
            
            for filename in os.listdir(tasks_directory):
                if filename.endswith('.py') and not filename.startswith('__'):
                    file_path = os.path.join(tasks_directory, filename)
                    module_name = filename[:-3]  # Remove .py extension
                    
                    # Try to load the module to check if it has run_task function
                    try:
                        spec = importlib.util.spec_from_file_location(module_name, file_path)
                        if spec and spec.loader:
                            module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(module)
                            
                            if hasattr(module, 'run_task'):
                                discovered_tasks.append({
                                    'name': module_name,
                                    'file_path': file_path,
                                    'module_name': module_name,
                                    'description': getattr(module, '__doc__', 'No description available')
                                })
                    except Exception as e:
                        logger.warning(f"Could not load potential task {filename}: {e}")
            
        except Exception as e:
            logger.error(f"Error discovering tasks: {e}")
        
        return discovered_tasks
    
    def _execute_task_in_environment(self, task: Task, python_executable: str, config: Optional[Dict[str, Any]], task_logger) -> Dict[str, Any]:
        """Execute a task in an isolated environment"""
        try:
            # Create a temporary script to execute the task
            import tempfile
            import json
            
            # Prepare the execution script
            script_content = f'''
import sys
import os
import json
import traceback
from pathlib import Path

# Add the task directory to Python path
task_dir = Path("{os.path.dirname(task.file_path)}")
sys.path.insert(0, str(task_dir))

# Import and execute the task
try:
    import {task.module_name}
    
    # Prepare config
    config = {json.dumps(config or {})}
    
    # Execute task
    result = {task.module_name}.run_task(config)
    
    # Print result as JSON
    print("TASK_RESULT_START")
    print(json.dumps(result))
    print("TASK_RESULT_END")
    
except Exception as e:
    print("TASK_ERROR_START")
    print(json.dumps({{
        "status": "error",
        "message": str(e),
        "traceback": traceback.format_exc()
    }}))
    print("TASK_ERROR_END")
'''
            
            # Create temporary script file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as script_file:
                script_file.write(script_content)
                script_path = script_file.name
            
            try:
                # Execute the script in the isolated environment
                task_logger.info(f"Executing task in isolated environment: {python_executable}")
                
                result = subprocess.run([
                    python_executable, script_path
                ], capture_output=True, text=True, timeout=3600)  # 1 hour timeout
                
                # Parse the output
                output = result.stdout
                error_output = result.stderr
                
                if error_output:
                    task_logger.warning(f"Task stderr output: {error_output}")
                
                # Look for task result in output
                if "TASK_RESULT_START" in output and "TASK_RESULT_END" in output:
                    start_idx = output.find("TASK_RESULT_START") + len("TASK_RESULT_START")
                    end_idx = output.find("TASK_RESULT_END")
                    result_json = output[start_idx:end_idx].strip()
                    
                    try:
                        return json.loads(result_json)
                    except json.JSONDecodeError as e:
                        task_logger.error(f"Failed to parse task result JSON: {e}")
                        return {"status": "error", "message": f"Failed to parse result: {e}"}
                
                elif "TASK_ERROR_START" in output and "TASK_ERROR_END" in output:
                    start_idx = output.find("TASK_ERROR_START") + len("TASK_ERROR_START")
                    end_idx = output.find("TASK_ERROR_END")
                    error_json = output[start_idx:end_idx].strip()
                    
                    try:
                        error_result = json.loads(error_json)
                        task_logger.error(f"Task execution error: {error_result}")
                        return error_result
                    except json.JSONDecodeError as e:
                        task_logger.error(f"Failed to parse error JSON: {e}")
                        return {"status": "error", "message": f"Failed to parse error: {e}"}
                
                else:
                    # Fallback: return output as result
                    task_logger.warning("Could not find task result markers, returning raw output")
                    return {
                        "status": "success",
                        "message": "Task executed (raw output)",
                        "output": output,
                        "return_code": result.returncode
                    }
                
            finally:
                # Clean up temporary script
                try:
                    os.unlink(script_path)
                except:
                    pass
                    
        except Exception as e:
            task_logger.error(f"Error executing task in environment: {e}")
            return {"status": "error", "message": str(e)}

    def validate_task_file(self, file_path: str) -> Dict[str, Any]:
        """Validate if a file is a valid task file"""
        try:
            if not os.path.exists(file_path):
                return {"valid": False, "error": "File does not exist"}
            
            if not file_path.endswith('.py'):
                return {"valid": False, "error": "File must be a Python file"}
            
            filename = os.path.basename(file_path)
            module_name = filename[:-3]
            
            # Try to load the module
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if not spec or not spec.loader:
                return {"valid": False, "error": "Could not load module"}
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Check for run_task function
            if not hasattr(module, 'run_task'):
                return {"valid": False, "error": "Module must have a 'run_task' function"}
            
            # Check if run_task is callable
            if not callable(module.run_task):
                return {"valid": False, "error": "'run_task' must be a callable function"}
            
            return {
                "valid": True,
                "module_name": module_name,
                "description": getattr(module, '__doc__', 'No description available')
            }
            
        except Exception as e:
            return {"valid": False, "error": str(e)}

# Global task executor instance
task_executor = TaskExecutor() 