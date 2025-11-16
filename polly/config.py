"""
Configuration management for Polly
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any

# Default configuration
DEFAULT_CONFIG = {
    "default_model": "openai-large",  # Most capable and reliable model
    "temperature": 0.7,
    "stream": False,
    "referrer": "interzonesec.com",
    "language": "pt",  # pt, en, pt-br, portuguese, english
    "use_backend": True,  # Use proxy backend by default
}

# Backend URL (hardcoded - not user-configurable)
BACKEND_URL = "https://api.interzonesec.com"

# Available models with descriptions (ordered by reliability)
AVAILABLE_MODELS = {
    "openai-large": "OpenAI GPT-4.1 - Most capable (default)",
    "mistral": "Mistral Small 3.2 24B - Balanced performance",
    "deepseek": "DeepSeek V3.1 - Advanced reasoning model",
    "qwen-coder": "Qwen 2.5 Coder 32B - Specialized for coding",
    "openai": "OpenAI GPT-5 Nano - Fast (temperature=1.0 only)",
    "gemini": "Gemini 2.5 Flash Lite - Fast (currently unstable)",
    "gemini-search": "Gemini 2.5 Flash Lite with Google Search",
}

# API Configuration
API_BASE_URL = "https://text.pollinations.ai"  # Direct API (fallback)
API_TIMEOUT = 30

# New Pollinations API Configuration
NEW_API_BASE_URL = "https://enter.pollinations.ai/api/generate/v1"


class Config:
    """Manages Polly configuration"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "polly"
        self.config_file = self.config_dir / "config.yaml"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    user_config = yaml.safe_load(f) or {}
                # Merge with defaults
                config = DEFAULT_CONFIG.copy()
                config.update(user_config)
                return config
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
                return DEFAULT_CONFIG.copy()
        return DEFAULT_CONFIG.copy()
    
    def save_config(self) -> bool:
        """Save current configuration to file"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        self.config[key] = value
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.config = DEFAULT_CONFIG.copy()
        self.save_config()


# Global config instance
_config = None


def get_config() -> Config:
    """Get global configuration instance"""
    global _config
    if _config is None:
        _config = Config()
    return _config
