import yaml
import os
from typing import Dict, Any
from pathlib import Path

class Config:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as file:
            config = yaml.safe_load(file)
        
        # Set defaults for missing values
        config.setdefault('admin', {})
        config['admin'].setdefault('username', 'admin')
        config['admin'].setdefault('password', 'admin123')
        
        config.setdefault('database', {})
        config['database'].setdefault('url', 'sqlite:///./cronpilot.db')
        
        config.setdefault('scheduler', {})
        config['scheduler'].setdefault('timezone', 'UTC')
        config['scheduler'].setdefault('max_workers', 10)
        
        config.setdefault('email', {})
        config['email'].setdefault('smtp_host', 'smtp.gmail.com')
        config['email'].setdefault('smtp_port', 587)
        config['email'].setdefault('use_tls', True)
        
        config.setdefault('logging', {})
        config['logging'].setdefault('retention_days', 7)
        config['logging'].setdefault('log_dir', './logs')
        config['logging'].setdefault('max_log_size_mb', 10)
        
        config.setdefault('tasks', {})
        config['tasks'].setdefault('directory', './tasks')
        config['tasks'].setdefault('auto_discover', True)
        
        return config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def reload(self):
        """Reload configuration from file"""
        self._config = self._load_config()
    
    @property
    def admin_username(self) -> str:
        return self.get('admin.username')
    
    @property
    def admin_password(self) -> str:
        return self.get('admin.password')
    
    @property
    def database_url(self) -> str:
        return self.get('database.url')
    
    @property
    def scheduler_timezone(self) -> str:
        return self.get('scheduler.timezone')
    
    @property
    def scheduler_max_workers(self) -> int:
        return self.get('scheduler.max_workers')
    
    @property
    def email_config(self) -> Dict[str, Any]:
        return self.get('email', {})
    
    @property
    def logging_config(self) -> Dict[str, Any]:
        return self.get('logging', {})
    
    @property
    def tasks_directory(self) -> str:
        return self.get('tasks.directory')
    
    @property
    def auto_discover_tasks(self) -> bool:
        return self.get('tasks.auto_discover', True)
    
    @property
    def server_host(self) -> str:
        return self.get('server.host', '0.0.0.0')
    
    @property
    def server_port(self) -> int:
        return self.get('server.port', 7000)

# Global configuration instance
config = Config() 