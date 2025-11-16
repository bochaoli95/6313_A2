"""
Configuration loader for YAML config files
"""
import yaml
import os
from typing import Dict, Any


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file"""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        # Return default config if file not found
        return {
            "api_gateway": {
                "host": "0.0.0.0",
                "port": 8000,
                "routing_percentage": 0.5
            },
            "microservices": {
                "user_service_v1": {"url": "http://user_service_v1:8001"},
                "user_service_v2": {"url": "http://user_service_v2:8002"},
                "order_service": {"url": "http://order_service:8003"}
            }

        }

