"""
Conversational memory for Polly.

Persists a short rolling context between separate CLI invocations so the user can
continue a topic across commands (including pasting code) without entering the
interactive (-i) mode.

Two separate stores:
  - Session memory (working context): ephemeral, per-terminal, used to build the
    prompt. Lives at ~/.config/polly/sessions/<hash>.json
  - Conversation log (history): persistent, global, append-only, human-readable.
    Lives at ~/.config/polly/history.log
"""

import os
import sys
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict

from .config import get_config
from .utils import truncate_context


def _config_dir() -> Path:
    """Base config dir (matches Config.config_dir)."""
    return Path.home() / ".config" / "polly"


def _sessions_dir() -> Path:
    return _config_dir() / "sessions"


def _history_path() -> Path:
    return _config_dir() / "history.log"


def _windows_console_id() -> str:
    """
    Stable identifier for the current Windows console window. The console window
    handle (HWND) is shared by every process attached to that terminal and is the
    same across separate `polly` invocations in the same window — crucially, it
    survives the pipx launcher's intermediate process (unlike getppid, which
    returns a fresh PID each run). Returns "" if unavailable.
    """
    try:
        import ctypes
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        return f"console-{hwnd}" if hwnd else ""
    except Exception:
        return ""


def _session_key() -> str:
    """
    Identify the current terminal session. Cascade (first that exists wins):
      1. Windows console HWND - stable per terminal window, survives pipx launcher
      2. WT_SESSION           - Windows Terminal (unique GUID per tab)
      3. TERM_SESSION_ID      - macOS Terminal / iTerm
      4. tty name             - Linux/Mac
      5. parent PID           - the shell that launched polly
      6. "global"             - no terminal (e.g. pure pipe)
    The raw key is hashed to a short, filesystem-safe name.
    """
    raw = None
    if sys.platform == "win32":
        raw = _windows_console_id() or None

    if not raw:
        raw = (
            os.environ.get("WT_SESSION")
            or os.environ.get("TERM_SESSION_ID")
        )
    if not raw:
        try:
            raw = os.ttyname(0)
        except (OSError, AttributeError):
            raw = None
    if not raw:
        try:
            raw = f"ppid-{os.getppid()}"
        except OSError:
            raw = "global"

    return hashlib.md5(raw.encode("utf-8", errors="replace")).hexdigest()[:12]


def _session_path() -> Path:
    return _sessions_dir() / f"{_session_key()}.json"


def _ttl_seconds() -> int:
    return int(get_config().get("memory_ttl_minutes", 30)) * 60


def load_context() -> List[Dict[str, str]]:
    """
    Return the session's stored messages (user/assistant turns), or [] if the
    session is missing, unreadable, or expired (older than the TTL).
    """
    path = _session_path()
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return []

    if time.time() - data.get("updated_at", 0) > _ttl_seconds():
        return []  # expired -> start fresh

    messages = data.get("messages", [])
    return messages if isinstance(messages, list) else []


def _truncate_response(text: str) -> str:
    """Clip a long assistant reply (e.g. pasted code) so it cannot dominate
    the rolling context."""
    limit = int(get_config().get("memory_max_response_chars", 1000))
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + " …[truncado]"


def save_turn(user_msg: str, assistant_msg: str) -> None:
    """
    Append a (user, assistant) exchange to the current session, trimming to the
    configured turn count, per-response size, and global char ceiling.
    """
    config = get_config()
    max_turns = int(config.get("memory_max_turns", 6))
    max_chars = int(config.get("memory_max_chars", 6000))
    max_tokens = int(config.get("memory_max_tokens", 1500))

    messages = load_context()
    messages.append({"role": "user", "content": user_msg.strip()})
    messages.append({"role": "assistant", "content": _truncate_response(assistant_msg)})

    # Keep only the most recent N turns (each turn == user + assistant == 2 msgs)
    if len(messages) > max_turns * 2:
        messages = messages[-max_turns * 2:]

    # Cap by chars AND tokens — whichever is exhausted first
    messages = truncate_context(messages, max_chars=max_chars, max_tokens=max_tokens)

    path = _session_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"updated_at": time.time(), "messages": messages}, f, ensure_ascii=False)
    except Exception:
        pass  # memory is best-effort; never break the main flow

    cleanup_old_sessions()


def clear_session() -> bool:
    """Delete the current session's memory file. Returns True if a file was removed."""
    path = _session_path()
    try:
        if path.exists():
            path.unlink()
            return True
    except Exception:
        pass
    return False


def format_context() -> str:
    """Human-readable rendering of the active session context for `--context`."""
    messages = load_context()
    if not messages:
        return ""

    lines = []
    for msg in messages:
        role = msg.get("role", "?")
        label = "You" if role == "user" else "Polly"
        content = msg.get("content", "").strip()
        lines.append(f"[{label}]\n{content}\n")
    return "\n".join(lines)


def append_history(model: str, mode: str, user_msg: str, assistant_msg: str) -> None:
    """Append a readable record of the exchange to the global history log."""
    path = _history_path()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    block = (
        f"{'=' * 70}\n"
        f"[{ts}] model={model} mode={mode}\n"
        f"--- You ---\n{user_msg.strip()}\n"
        f"--- Polly ---\n{assistant_msg.strip()}\n"
    )
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(block)
    except Exception:
        pass


def history_path_str() -> str:
    """Public path to the history log, for user-facing messages."""
    return str(_history_path())


def read_history(limit_lines: int = 200) -> str:
    """Return the last `limit_lines` lines of history.log, or '' if empty."""
    path = _history_path()
    if not path.exists():
        return ""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
        return "\n".join(lines[-limit_lines:])
    except Exception:
        return ""


def clear_history() -> bool:
    """Truncate history.log. Returns True if file existed."""
    path = _history_path()
    try:
        if path.exists():
            path.write_text("", encoding="utf-8")
            return True
    except Exception:
        pass
    return False


def purge_all() -> dict:
    """
    Delete all local Polly state: sessions, history, caches.
    Does NOT touch config.yaml.
    Returns a summary dict with counts of items removed.
    """
    config_dir = _config_dir()
    summary = {"sessions": 0, "cache_files": 0, "other": 0}

    # Sessions
    sessions = _sessions_dir()
    if sessions.exists():
        for f in sessions.glob("*.json"):
            try:
                f.unlink()
                summary["sessions"] += 1
            except Exception:
                pass

    # History log
    hp = _history_path()
    if hp.exists():
        try:
            hp.unlink()
            summary["other"] += 1
        except Exception:
            pass

    # Cache files (models_cache, health_cache, response cache dir)
    for name in ("models_cache.json", "health_cache.json"):
        f = config_dir / name
        if f.exists():
            try:
                f.unlink()
                summary["cache_files"] += 1
            except Exception:
                pass

    cache_dir = config_dir / "cache"
    if cache_dir.exists():
        for f in cache_dir.glob("*.json"):
            try:
                f.unlink()
                summary["cache_files"] += 1
            except Exception:
                pass

    return summary


def cleanup_old_sessions() -> None:
    """Remove session files older than the TTL. Cheap housekeeping on save."""
    ttl = _ttl_seconds()
    now = time.time()
    sessions = _sessions_dir()
    if not sessions.exists():
        return
    for f in sessions.glob("*.json"):
        try:
            if now - f.stat().st_mtime > ttl:
                f.unlink()
        except Exception:
            pass
