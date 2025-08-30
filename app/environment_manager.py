import os
import subprocess
import venv
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json

logger = logging.getLogger(__name__)

class EnvironmentManager:
    def __init__(self, tasks_directory: str = "./tasks"):
        self.tasks_directory = tasks_directory
    
    def discover_environments(self) -> List[Dict[str, str]]:
        """Discover all virtual environments in the tasks directory"""
        environments = []
        
        try:
            tasks_path = Path(self.tasks_directory)
            if not tasks_path.exists():
                return environments
            
            # Look for virtual environments in task directories
            for item in tasks_path.iterdir():
                if item.is_dir():
                    # Check for common virtual environment patterns
                    env_paths = [
                        item / "venv",
                        item / "env",
                        item / ".venv",
                        item / ".env",
                        item / "virtualenv"
                    ]
                    
                    for env_path in env_paths:
                        if env_path.exists() and self._is_valid_venv(env_path):
                            environments.append({
                                "name": f"{item.name}_{env_path.name}",
                                "path": str(env_path.absolute()),
                                "task_folder": item.name,
                                "python_executable": self._get_python_executable(env_path)
                            })
            
            # Also check for global environments in tasks directory
            global_envs = [
                tasks_path / "environments" / "venv",
                tasks_path / "environments" / "env",
                tasks_path / ".venv",
                tasks_path / ".env"
            ]
            
            for env_path in global_envs:
                if env_path.exists() and self._is_valid_venv(env_path):
                    environments.append({
                        "name": f"global_{env_path.name}",
                        "path": str(env_path.absolute()),
                        "task_folder": "global",
                        "python_executable": self._get_python_executable(env_path)
                    })
            
            # Check for environments directly in tasks directory
            direct_envs = [
                tasks_path / "venv",
                tasks_path / "env", 
                tasks_path / ".venv",
                tasks_path / ".env",
                tasks_path / "test_env"  # Include our test environment
            ]
            
            for env_path in direct_envs:
                if env_path.exists() and self._is_valid_venv(env_path):
                    environments.append({
                        "name": f"tasks_{env_path.name}",
                        "path": str(env_path.absolute()),
                        "task_folder": "tasks",
                        "python_executable": self._get_python_executable(env_path)
                    })
                    
        except Exception as e:
            logger.error(f"Error discovering environments: {e}")
        
        return environments
    
    def discover_requirements_files(self) -> List[Dict[str, str]]:
        """Discover all requirements.txt files in the tasks directory"""
        requirements_files = []
        
        try:
            tasks_path = Path(self.tasks_directory)
            if not tasks_path.exists():
                return requirements_files
            
            # Search recursively for requirements.txt files
            for requirements_file in tasks_path.rglob("requirements.txt"):
                relative_path = requirements_file.relative_to(tasks_path)
                requirements_files.append({
                    "name": f"{relative_path.parent}_{requirements_file.name}",
                    "path": str(requirements_file.absolute()),
                    "task_folder": str(relative_path.parent),
                    "size": requirements_file.stat().st_size
                })
            
            # Also check for other requirements files
            for pattern in ["requirements-*.txt", "req-*.txt", "deps.txt"]:
                for req_file in tasks_path.rglob(pattern):
                    relative_path = req_file.relative_to(tasks_path)
                    requirements_files.append({
                        "name": f"{relative_path.parent}_{req_file.name}",
                        "path": str(req_file.absolute()),
                        "task_folder": str(relative_path.parent),
                        "size": req_file.stat().st_size
                    })
                    
        except Exception as e:
            logger.error(f"Error discovering requirements files: {e}")
        
        return requirements_files
    
    def discover_task_projects(self) -> List[Dict[str, str]]:
        """Discover task projects with multiple files and main execution files"""
        task_projects = []
        
        try:
            tasks_path = Path(self.tasks_directory)
            if not tasks_path.exists():
                return task_projects
            
            for item in tasks_path.iterdir():
                if item.is_dir():
                    # Look for main execution files
                    main_files = [
                        item / "main.py",
                        item / "run.py",
                        item / "task.py",
                        item / "execute.py",
                        item / f"{item.name}.py"
                    ]
                    
                    for main_file in main_files:
                        if main_file.exists():
                            # Check if there are other Python files in the directory
                            python_files = list(item.glob("*.py"))
                            if len(python_files) > 1:  # Multiple files indicate a project
                                task_projects.append({
                                    "name": item.name,
                                    "path": str(item.absolute()),
                                    "main_file": str(main_file.relative_to(tasks_path)),
                                    "file_count": len(python_files),
                                    "files": [f.name for f in python_files]
                                })
                                break
                    
                    # Also check for __init__.py files (package structure)
                    if (item / "__init__.py").exists():
                        python_files = list(item.glob("*.py"))
                        if len(python_files) > 1:
                            # Find the main execution file
                            main_file = None
                            for py_file in python_files:
                                if py_file.name not in ["__init__.py"]:
                                    main_file = py_file
                                    break
                            
                            if main_file:
                                task_projects.append({
                                    "name": item.name,
                                    "path": str(item.absolute()),
                                    "main_file": str(main_file.relative_to(tasks_path)),
                                    "file_count": len(python_files),
                                    "files": [f.name for f in python_files],
                                    "is_package": True
                                })
                    
        except Exception as e:
            logger.error(f"Error discovering task projects: {e}")
        
        return task_projects
    
    def create_environment(self, env_path: str, requirements_path: Optional[str] = None) -> bool:
        """Create a new virtual environment and install requirements"""
        try:
            env_path = Path(env_path)
            
            # Create virtual environment
            if not env_path.exists():
                logger.info(f"Creating virtual environment at {env_path}")
                venv.create(env_path, with_pip=True)
            
            # Install requirements if provided
            if requirements_path and Path(requirements_path).exists():
                python_exec = self._get_python_executable(env_path)
                if python_exec:
                    logger.info(f"Installing requirements from {requirements_path}")
                    result = subprocess.run([
                        python_exec, "-m", "pip", "install", "-r", requirements_path
                    ], capture_output=True, text=True)
                    
                    if result.returncode != 0:
                        logger.error(f"Failed to install requirements: {result.stderr}")
                        return False
                    
                    logger.info("Requirements installed successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating environment: {e}")
            return False
    
    def activate_environment(self, env_path: str) -> Optional[str]:
        """Get the activation command for an environment"""
        try:
            env_path = Path(env_path)
            if not self._is_valid_venv(env_path):
                return None
            
            # Return the python executable path
            return self._get_python_executable(env_path)
            
        except Exception as e:
            logger.error(f"Error activating environment: {e}")
            return None
    
    def _is_valid_venv(self, env_path: Path) -> bool:
        """Check if a path is a valid virtual environment"""
        try:
            # Check for common virtual environment indicators
            indicators = [
                env_path / "bin" / "python",
                env_path / "bin" / "activate",
                env_path / "Scripts" / "python.exe",
                env_path / "Scripts" / "activate.bat"
            ]
            
            return any(indicator.exists() for indicator in indicators)
            
        except Exception:
            return False
    
    def _get_python_executable(self, env_path: Path) -> Optional[str]:
        """Get the Python executable path for a virtual environment"""
        try:
            # Check for Unix-style environment
            unix_python = env_path / "bin" / "python"
            if unix_python.exists():
                return str(unix_python.absolute())
            
            # Check for Windows-style environment
            windows_python = env_path / "Scripts" / "python.exe"
            if windows_python.exists():
                return str(windows_python.absolute())
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting Python executable: {e}")
            return None
    
    def validate_environment(self, env_path: str, requirements_path: Optional[str] = None) -> Dict[str, any]:
        """Validate an environment and its requirements"""
        try:
            env_path = Path(env_path)
            result = {
                "valid": False,
                "errors": [],
                "warnings": []
            }
            
            # Check if environment exists and is valid
            if not env_path.exists():
                result["errors"].append("Environment path does not exist")
                return result
            
            if not self._is_valid_venv(env_path):
                result["errors"].append("Path is not a valid virtual environment")
                return result
            
            # Check Python executable
            python_exec = self._get_python_executable(env_path)
            if not python_exec:
                result["errors"].append("Could not find Python executable in environment")
                return result
            
            # Test Python execution
            try:
                test_result = subprocess.run([
                    python_exec, "-c", "import sys; print(sys.version)"
                ], capture_output=True, text=True, timeout=10)
                
                if test_result.returncode != 0:
                    result["errors"].append(f"Python execution failed: {test_result.stderr}")
                    return result
                
            except subprocess.TimeoutExpired:
                result["errors"].append("Python execution timed out")
                return result
            
            # Check requirements if provided
            if requirements_path:
                req_path = Path(requirements_path)
                if not req_path.exists():
                    result["errors"].append("Requirements file does not exist")
                    return result
                
                # Try to install requirements
                try:
                    install_result = subprocess.run([
                        python_exec, "-m", "pip", "install", "-r", requirements_path
                    ], capture_output=True, text=True, timeout=60)
                    
                    if install_result.returncode != 0:
                        result["warnings"].append(f"Requirements installation had issues: {install_result.stderr}")
                    
                except subprocess.TimeoutExpired:
                    result["warnings"].append("Requirements installation timed out")
            
            result["valid"] = True
            result["python_executable"] = python_exec
            return result
            
        except Exception as e:
            result = {
                "valid": False,
                "errors": [str(e)],
                "warnings": []
            }
            return result

# Global environment manager instance
environment_manager = EnvironmentManager()
