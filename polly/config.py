"""
Configuration management for Polly
"""

import time
import json as _json
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
    # Conversational memory (context carried between separate CLI invocations)
    "memory_enabled": True,
    "memory_ttl_minutes": 30,       # session expires after this much inactivity
    "memory_max_turns": 6,          # keep at most N user+assistant exchanges
    "memory_max_chars": 6000,       # global ceiling on context size
    "memory_max_response_chars": 1000,  # clip long replies (e.g. pasted code)
    "memory_max_tokens": 1500,  # rough token budget for memory (≈4 chars/token)
    # Retry config for transient upstream errors (429/502/503/timeout)
    "retry_max_attempts": 3,
    "retry_base_delay": 1.0,
    # Response cache (opt-in; only applied when temperature <= cache_max_temperature)
    "response_cache_enabled": False,
    "cache_ttl_minutes": 60,
    "cache_max_temperature": 0.0,
}

# Backend URL (hardcoded - not user-configurable)
BACKEND_URL = "https://api.interzonesec.com"

# Gen API — authoritative source for model metadata (with aliases, pricing, flags)
GEN_API_BASE_URL = "https://gen.pollinations.ai"
MODELS_CACHE_TTL = 86400  # 24 hours

# Tinybird — real-time model health monitor (same source as model-monitor.pollinations.ai)
TINYBIRD_URL = "https://api.europe-west2.gcp.tinybird.co/v0/pipes/model_health.json"
TINYBIRD_TOKEN = "p.eyJ1IjogImFjYTYzZjc5LThjNTYtNDhlNC05NWJjLWEyYmFjMTY0NmJkMyIsICJpZCI6ICI5ZWZmMGM3Ni1kOTZkLTQwYjgtYWQwOC1mNDFlMmRiYjBmYTIiLCAiaG9zdCI6ICJnY3AtZXVyb3BlLXdlc3QyIn0.6VnVkAQ5h_fkcDZVDUoU38dzTxaw0xo3DnmKkhECbA8"
HEALTH_WINDOW_MINUTES = 60  # look back 1h for "active" models (wider = more models listed)
HEALTH_CACHE_TTL = 900  # 15 minutes — list is stable over a 1h window, refresh less often

# Fallback models — used only when gen.pollinations.ai is unreachable
AVAILABLE_MODELS = {
    "openai-large": "GPT-5.4 - Most Powerful & Intelligent",
    "openai": "GPT-5.4 Nano - Fast & Balanced",
    "openai-fast": "GPT-5 Nano - Ultra Fast & Affordable",
    "mistral": "Mistral Small 3.2 - Balanced performance",
    "deepseek": "DeepSeek V4 Flash - Fast Reasoning & Coding",
    "qwen-coder": "Qwen3 Coder 30B - Specialized for Code Generation",
    "gemini-search": "Gemini 2.5 Flash Lite Search - Web-grounded responses",
}


def _fetch_tinybird_rows() -> list:
    """Fetch raw Tinybird rows for text models. Returns [] on any failure."""
    import requests as _req
    try:
        r = _req.get(
            TINYBIRD_URL,
            params={"token": TINYBIRD_TOKEN, "minutes": HEALTH_WINDOW_MINUTES},
            timeout=6,
        )
        r.raise_for_status()
        return [row for row in r.json().get("data", []) if row.get("event_type") == "generate.text"]
    except Exception:
        return []


def _fetch_healthy_model_names() -> set:
    """Return names of text models with >=50% success rate. Empty set on failure."""
    healthy = set()
    for row in _fetch_tinybird_rows():
        total = row.get("total_requests") or 0
        ok = row.get("status_2xx") or 0
        if total > 0 and ok / total >= 0.5:
            healthy.add(row["model"])
    return healthy


def fetch_health_stats(config_dir: Path = None) -> dict:
    """
    Return per-model health stats from the cache (or live Tinybird fetch).
    Result: { model_name: {"success_pct": int, "p50_ms": int} }
    Returns {} when data is unavailable.
    """
    if config_dir is None:
        config_dir = Path.home() / ".config" / "polly"
    health_cache = config_dir / "health_cache.json"

    stats = {}
    # Try reading from cache first
    if health_cache.exists():
        try:
            with open(health_cache, "r") as f:
                hc = _json.load(f)
            if time.time() - hc.get("timestamp", 0) < HEALTH_CACHE_TTL:
                return hc.get("stats", {})
        except Exception:
            pass

    # Fetch live
    for row in _fetch_tinybird_rows():
        total = row.get("total_requests") or 0
        ok = row.get("status_2xx") or 0
        name = row.get("model", "")
        if not name or total == 0:
            continue
        stats[name] = {
            "success_pct": int(ok / total * 100),
            "p50_ms": int(row.get("latency_p50_ms") or 0),
        }
    return stats


def fetch_text_models(config_dir: Path = None) -> list:
    """
    Return text models that are both documented (gen.pollinations.ai) and
    currently healthy (>=50% success in last 5 min per Tinybird/model-monitor).

    Uses two caches:
    - models_cache.json     — gen API metadata, 24h TTL
    - health_cache.json     — Tinybird health data, 5min TTL

    Falls back to full gen API list (without health filter) if Tinybird is
    unreachable, and to AVAILABLE_MODELS if both fail.
    """
    import requests as _req

    if config_dir is None:
        config_dir = Path.home() / ".config" / "polly"

    # --- Load metadata (24h cache) ---
    meta_cache = config_dir / "models_cache.json"
    all_models = None

    if meta_cache.exists():
        try:
            with open(meta_cache, "r") as f:
                cache = _json.load(f)
            if time.time() - cache.get("timestamp", 0) < MODELS_CACHE_TTL:
                all_models = cache["models"]
        except Exception:
            pass

    if all_models is None:
        try:
            r = _req.get(f"{GEN_API_BASE_URL}/text/models", timeout=8)
            r.raise_for_status()
            all_models = r.json()
            try:
                config_dir.mkdir(parents=True, exist_ok=True)
                with open(meta_cache, "w") as f:
                    _json.dump({"timestamp": time.time(), "models": all_models}, f)
            except Exception:
                pass
        except Exception:
            all_models = [
                {"name": k, "description": v, "aliases": [], "paid_only": False}
                for k, v in AVAILABLE_MODELS.items()
            ]

    # --- Load health data (5min cache) ---
    health_cache = config_dir / "health_cache.json"
    healthy_names = None

    if health_cache.exists():
        try:
            with open(health_cache, "r") as f:
                hc = _json.load(f)
            if time.time() - hc.get("timestamp", 0) < HEALTH_CACHE_TTL:
                healthy_names = set(hc["healthy"])
        except Exception:
            pass

    if healthy_names is None:
        rows = _fetch_tinybird_rows()
        healthy_names = set()
        stats_to_cache = {}
        for row in rows:
            total = row.get("total_requests") or 0
            ok = row.get("status_2xx") or 0
            name = row.get("model", "")
            if not name or total == 0:
                continue
            if ok / total >= 0.5:
                healthy_names.add(name)
            stats_to_cache[name] = {
                "success_pct": int(ok / total * 100),
                "p50_ms": int(row.get("latency_p50_ms") or 0),
            }
        if healthy_names:
            try:
                config_dir.mkdir(parents=True, exist_ok=True)
                with open(health_cache, "w") as f:
                    _json.dump({
                        "timestamp": time.time(),
                        "healthy": list(healthy_names),
                        "stats": stats_to_cache,
                    }, f)
            except Exception:
                pass

    # --- Keep only usable text chat models (drop audio output, specialized tools) ---
    def _is_text_chat_model(m):
        out = m.get("output_modalities", ["text"])
        return "text" in out and "audio" not in out and not m.get("is_specialized")

    all_models = [m for m in all_models if _is_text_chat_model(m)]

    # --- Filter: keep only models active on Tinybird (fall back to all if health unavailable) ---
    if healthy_names:
        filtered = [m for m in all_models if m.get("name") in healthy_names]
        return filtered if filtered else all_models

    return all_models

# Temperature Presets
TEMPERATURE_PRESETS = {
    "precise": {"value": 0.3, "description": "For commands and code", "description_pt": "Para comandos e código"},
    "balanced": {"value": 0.7, "description": "General purpose (default)", "description_pt": "Uso geral (padrão)"},
    "creative": {"value": 1.5, "description": "Writing and brainstorming", "description_pt": "Escrita e brainstorming"},
    "wild": {"value": 2.5, "description": "Experimental responses", "description_pt": "Respostas experimentais"},
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
        self.is_first_run = not self.config_file.exists()
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

    def save_profile(self, profile_name: str) -> bool:
        """
        Save current configuration as a named profile.

        Args:
            profile_name: Name of the profile to save

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            profiles_dir = self.config_dir / "profiles"
            profiles_dir.mkdir(parents=True, exist_ok=True)

            profile_file = profiles_dir / f"{profile_name}.yaml"
            with open(profile_file, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
            return True
        except Exception as e:
            print(get_text("config.save_error", e=str(e)))
            return False

    def load_profile(self, profile_name: str) -> bool:
        """
        Load a named profile.

        Args:
            profile_name: Name of the profile to load

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            profiles_dir = self.config_dir / "profiles"
            profile_file = profiles_dir / f"{profile_name}.yaml"

            if not profile_file.exists():
                return False

            with open(profile_file, 'r') as f:
                profile_config = yaml.safe_load(f) or {}

            # Update current config with profile settings
            self.config.update(profile_config)
            # Save to main config
            return self.save_config()
        except Exception as e:
            print(get_text("config.load_error", e=str(e)))
            return False

    def list_profiles(self) -> list:
        """
        List all available profiles.

        Returns:
            list: List of profile names
        """
        try:
            profiles_dir = self.config_dir / "profiles"
            if not profiles_dir.exists():
                return []

            profiles = [f.stem for f in profiles_dir.glob("*.yaml")]
            return sorted(profiles)
        except Exception:
            return []

    def delete_profile(self, profile_name: str) -> bool:
        """
        Delete a named profile.

        Args:
            profile_name: Name of the profile to delete

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            profiles_dir = self.config_dir / "profiles"
            profile_file = profiles_dir / f"{profile_name}.yaml"

            if profile_file.exists():
                profile_file.unlink()
                return True
            return False
        except Exception:
            return False


# Global config instance
_config = None


def get_config() -> Config:
    """Get global configuration instance"""
    global _config
    if _config is None:
        _config = Config()
    return _config
