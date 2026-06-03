"""
Optional response cache for Polly.

Caches identical (model, mode, temperature, prompts) responses to disk so
repeated queries skip the API call entirely. Off by default; enabled with
--cache or response_cache_enabled=true in config.yaml.
"""

import json
import time
import hashlib
from pathlib import Path

from .config import get_config


def _cache_dir() -> Path:
    from .config import get_config as _gc
    base = Path.home() / ".config" / "polly"
    try:
        cfg = _gc()
        base = cfg.config_dir
    except Exception:
        pass
    return base / "cache"


def _cache_key(model: str, mode: str, temperature: float, system_prompt: str, user_prompt: str) -> str:
    """Stable sha256 key from the inputs that determine the response."""
    raw = f"{model}|{mode}|{temperature:.4f}|{system_prompt}|{user_prompt}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def get(key: str, ttl_minutes: int = 60) -> str | None:
    """Return cached response string if it exists and is still fresh, else None."""
    path = _cache_dir() / f"{key}.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        age_seconds = time.time() - data.get("ts", 0)
        if age_seconds > ttl_minutes * 60:
            return None
        return data.get("response")
    except Exception:
        return None


def put(key: str, response: str) -> None:
    """Write a response to the cache. Best-effort; never raises."""
    try:
        d = _cache_dir()
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{key}.json").write_text(
            json.dumps({"ts": time.time(), "response": response}),
            encoding="utf-8",
        )
    except Exception:
        pass


def clear() -> int:
    """Delete all cache files. Returns count removed."""
    d = _cache_dir()
    count = 0
    if d.exists():
        for f in d.glob("*.json"):
            try:
                f.unlink()
                count += 1
            except Exception:
                pass
    return count


def is_enabled(args) -> bool:
    """Return True if caching is active for this invocation."""
    if getattr(args, "no_cache", False):
        return False
    if getattr(args, "cache", False):
        return True
    config = get_config()
    return bool(config.get("response_cache_enabled", False))
