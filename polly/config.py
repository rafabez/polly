"""
Configuration management for Polly
"""

import os
import locale
import platform
import yaml
from pathlib import Path
from typing import Dict, Any
from .i18n import get_text


def detect_os() -> str:
    """
    Detect the current operating system.

    Returns:
        str: Operating system name in lowercase (e.g., 'linux', 'darwin', 'windows')
    """
    return platform.system().lower()


def detect_language() -> str:
    """
    Detect system language from locale.

    Returns:
        str: Language code ('pt' for Portuguese variants, 'en' for others)
    """
    try:
        # Use modern locale detection (getdefaultlocale is deprecated in Python 3.13+)
        locale.setlocale(locale.LC_ALL, '')
        lang_code, _ = locale.getlocale()
        if lang_code:
            # Check if Portuguese variant (pt, pt_BR, pt_PT, etc.)
            if lang_code.lower().startswith('pt'):
                return 'pt'
        return 'en'  # Default to English
    except Exception:
        return 'en'  # Fallback to English on any error


def normalize_os(os_value: str) -> str:
    """
    Normalize OS value to a standard internal format.

    Converts case-insensitive input to lowercase and maps 'macos' to 'darwin'
    (since that's what platform.system() returns on macOS).

    Args:
        os_value: OS value (case-insensitive). Accepted formats:
            - 'auto' - Auto-detect OS
            - 'linux' - Linux (case-insensitive)
            - 'macos'/'darwin' - macOS (case-insensitive, converts to 'darwin')
            - 'windows' - Windows (case-insensitive)

    Returns:
        str: Normalized OS value ('auto', 'linux', 'darwin', 'windows')

    Raises:
        ValueError: If OS value is not recognized

    Examples:
        >>> normalize_os('LINUX')
        'linux'
        >>> normalize_os('MacOS')
        'darwin'
        >>> normalize_os('windows')
        'windows'
        >>> normalize_os('AUTO')
        'auto'
        >>> normalize_os('DARWIN')  # Darwin is also accepted
        'darwin'
    """
    if not isinstance(os_value, str):
        raise ValueError(f"OS value must be a string, got {type(os_value).__name__}")

    # Normalize to lowercase
    normalized = os_value.lower().strip()

    # Map macos to darwin (internal representation)
    if normalized == "macos":
        return "darwin"

    # Validate against allowed values
    allowed_values = {"auto", "linux", "darwin", "windows"}
    if normalized not in allowed_values:
        raise ValueError(
            f"Invalid OS: '{os_value}'. "
            f"Allowed values (case-insensitive): auto, linux, macos, darwin, windows"
        )

    return normalized


# Default configuration
DEFAULT_CONFIG = {
    "default_model": "openai-large",  # Most capable and reliable model
    "temperature": 0.7,
    "stream": False,
    "referrer": "interzonesec.com",
    "language": "auto",  # auto (detect from locale), pt, en, pt-br, portuguese, english
    "use_backend": True,  # Use proxy backend by default
    "os": "auto",  # Operating system: auto, linux, darwin, windows
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
API_TIMEOUT = 90  # Request timeout (90s - API can be slow)

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
                # Use English for errors during config loading to avoid circular dependency
                print(get_text("config.load_error", lang="en", e=str(e)))
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
            # Config is loaded, safe to auto-detect language
            print(get_text("config.save_error", e=str(e)))
            return False
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        self.config[key] = value

    def get_effective_os(self) -> str:
        """
        Get the effective operating system.

        Resolves "auto" to the actual detected OS. Normalizes the OS value to
        handle case-insensitive input and map 'macos' to 'darwin'. Ensures
        backwards compatibility by defaulting to "auto" if the os field doesn't
        exist in the config.

        Returns:
            str: Operating system name in lowercase (e.g., 'linux', 'darwin', 'windows')
        """
        os_value = self.config.get("os", "auto")
        # Normalize the OS value to handle case-insensitive input
        try:
            normalized = normalize_os(os_value)
        except ValueError:
            # Fallback to "auto" if normalization fails
            # Use English to avoid potential circular dependency
            print(get_text("config.invalid_os", lang="en", os_value=os_value))
            normalized = "auto"

        if normalized == "auto":
            return detect_os()
        return normalized

    def get_effective_language(self) -> str:
        """
        Get the effective language.

        Resolves "auto" to the detected system language from locale.
        Also normalizes variant language codes to standard codes.
        Ensures backwards compatibility by defaulting to "auto" if the
        language field doesn't exist in the config.

        Returns:
            str: Language code ('pt' or 'en')
        """
        lang_value = self.config.get("language", "auto")

        # Handle "auto" detection
        if lang_value == "auto":
            return detect_language()

        # Normalize language variants
        if lang_value in ["pt-br", "pt_br", "portuguese"]:
            return "pt"
        elif lang_value in ["english"]:
            return "en"

        # Return as-is if it's already a valid code
        return lang_value

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
