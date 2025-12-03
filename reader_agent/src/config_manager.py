"""
Configuration management for the reader agent.
"""

import os
import yaml
from typing import Dict, Any
from pathlib import Path


class ConfigManager:
    """Manages configuration from YAML file and environment variables."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to YAML configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self._validate_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file.
        
        Returns:
            Configuration dictionary
        """
        config_file = Path(self.config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}\n"
                "Please copy config.yaml.example to config.yaml and configure it."
            )
        
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # Load device API key from environment
        api_key = os.getenv('DEVICE_API_KEY')
        if not api_key:
            raise ValueError(
                "DEVICE_API_KEY environment variable not set.\n"
                "Please set it with: export DEVICE_API_KEY=your-api-key-here"
            )
        
        config['device']['api_key'] = api_key
        
        return config
    
    def _validate_config(self) -> None:
        """Validate required configuration fields."""
        required_fields = [
            ('api', 'base_url'),
            ('device', 'device_id'),
            ('device', 'api_key'),
            ('reader', 'poll_interval_ms'),
            ('offline', 'database_path'),
        ]
        
        for section, field in required_fields:
            if section not in self.config or field not in self.config[section]:
                raise ValueError(f"Missing required configuration: {section}.{field}")
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            section: Configuration section (e.g., 'api', 'device')
            key: Configuration key
            default: Default value if not found
            
        Returns:
            Configuration value
        """
        return self.config.get(section, {}).get(key, default)
    
    @property
    def api_base_url(self) -> str:
        """Get API base URL."""
        return self.get('api', 'base_url')
    
    @property
    def api_timeout(self) -> int:
        """Get API timeout in seconds."""
        return self.get('api', 'timeout_seconds', 10)
    
    @property
    def device_id(self) -> str:
        """Get device ID."""
        return self.get('device', 'device_id')
    
    @property
    def device_api_key(self) -> str:
        """Get device API key."""
        return self.get('device', 'api_key')
    
    @property
    def poll_interval(self) -> float:
        """Get poll interval in seconds."""
        return self.get('reader', 'poll_interval_ms', 500) / 1000.0
    
    @property
    def reconnect_delay(self) -> int:
        """Get reconnect delay in seconds."""
        return self.get('reader', 'reconnect_delay_seconds', 5)
    
    @property
    def offline_db_path(self) -> str:
        """Get offline database path."""
        return self.get('offline', 'database_path', './offline_events.db')
    
    @property
    def sync_interval(self) -> int:
        """Get sync interval in seconds."""
        return self.get('offline', 'sync_interval_seconds', 30)
    
    @property
    def log_level(self) -> str:
        """Get logging level."""
        return self.get('logging', 'level', 'INFO')
    
    @property
    def log_file(self) -> str:
        """Get log file path."""
        return self.get('logging', 'file', './reader_agent.log')



