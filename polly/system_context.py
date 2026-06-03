"""
System context provider for Polly.

Detects machine facts (OS, shell, package manager, key tool versions) and
produces a compact summary that is prepended to the system prompt so the model
gives platform-specific advice ("use apt" vs "use brew" vs "use winget").

Results are cached in ~/.config/polly/system.json for system_context_ttl_hours.
Refresh with `polly --rescan`. Show with `polly --show-system`.
"""

import os
import sys
import json
import time
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Optional


# Tools to probe for versions — (command, version-flag)
_VERSION_PROBES = [
    ("python", "--version"),
    ("python3", "--version"),
    ("git", "--version"),
    ("node", "--version"),
    ("docker", "--version"),
    ("curl", "--version"),
]

# Ordered list of package managers to detect (first found wins for primary)
_PKG_MANAGERS = [
    "apt", "apt-get", "dnf", "yum", "pacman", "zypper",  # Linux
    "brew",                                                 # macOS
    "winget", "choco", "scoop",                            # Windows
]


def _run(cmd: list, timeout: float = 2.0) -> Optional[str]:
    """Run a command and return the first line of output, or None on failure."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            errors="replace",
        )
        out = (result.stdout or result.stderr or "").strip()
        return out.splitlines()[0] if out else None
    except Exception:
        return None


def _detect_shell() -> str:
    """Best-effort shell detection."""
    shell = os.environ.get("SHELL") or os.environ.get("ComSpec") or ""
    if shell:
        return Path(shell).name
    if sys.platform == "win32":
        return "PowerShell" if os.environ.get("PSModulePath") else "cmd"
    return "sh"


def _detect_distro() -> str:
    """Read /etc/os-release on Linux for a human-readable distro string."""
    try:
        p = Path("/etc/os-release")
        if p.exists():
            info = {}
            for line in p.read_text(errors="replace").splitlines():
                if "=" in line:
                    k, _, v = line.partition("=")
                    info[k.strip()] = v.strip().strip('"')
            return info.get("PRETTY_NAME") or info.get("NAME") or ""
    except Exception:
        pass
    return ""


def _detect_pkg_manager() -> str:
    """Return the primary package manager name, or '' if none found."""
    for pm in _PKG_MANAGERS:
        if shutil.which(pm):
            return pm
    return ""


def _probe_versions() -> dict:
    """Return {tool: version_string} for available tools."""
    versions = {}
    seen_cmds = set()
    for cmd, flag in _VERSION_PROBES:
        if cmd in seen_cmds or not shutil.which(cmd):
            continue
        seen_cmds.add(cmd)
        out = _run([cmd, flag])
        if out:
            # Grab just the version number — first token that looks like x.y.z
            import re
            m = re.search(r"\d+\.\d+[\.\d]*", out)
            if m:
                versions[cmd] = m.group(0)
    return versions


def collect() -> dict:
    """
    Collect machine facts. All fields are best-effort; missing ones are omitted.
    Returns a dict suitable for serialisation and for summary().
    """
    ctx: dict = {}

    ctx["os"] = sys.platform  # win32 / darwin / linux
    ctx["os_version"] = platform.version()[:60]
    ctx["arch"] = platform.machine()

    system = platform.system()
    if system == "Darwin":
        ctx["os_name"] = f"macOS {platform.mac_ver()[0]}"
    elif system == "Windows":
        ctx["os_name"] = f"Windows {platform.release()}"
    elif system == "Linux":
        distro = _detect_distro()
        ctx["os_name"] = distro or "Linux"
    else:
        ctx["os_name"] = system

    ctx["shell"] = _detect_shell()

    pm = _detect_pkg_manager()
    if pm:
        ctx["pkg_manager"] = pm

    versions = _probe_versions()
    if versions:
        ctx["tools"] = versions

    ctx["collected_at"] = time.time()
    return ctx


def summary(ctx: dict) -> str:
    """
    Compact one-paragraph string (≤300 chars) injected into system prompts.
    Example: "OS: Ubuntu 24.04 (x86_64); shell: bash; pkg: apt; python 3.12, git 2.43"
    """
    parts = []

    os_name = ctx.get("os_name") or ctx.get("os", "")
    arch = ctx.get("arch", "")
    if os_name:
        parts.append(f"OS: {os_name}" + (f" ({arch})" if arch else ""))

    if ctx.get("shell"):
        parts.append(f"shell: {ctx['shell']}")

    if ctx.get("pkg_manager"):
        parts.append(f"pkg: {ctx['pkg_manager']}")

    tools = ctx.get("tools", {})
    if tools:
        tool_str = ", ".join(f"{k} {v}" for k, v in list(tools.items())[:5])
        parts.append(tool_str)

    result = "; ".join(parts)
    return result[:300]


def _cache_path() -> Path:
    return Path.home() / ".config" / "polly" / "system.json"


def load(ttl_hours: float = 24.0) -> Optional[dict]:
    """Load cached context if still fresh, else None."""
    p = _cache_path()
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        age = time.time() - data.get("collected_at", 0)
        if age < ttl_hours * 3600:
            return data
    except Exception:
        pass
    return None


def save(ctx: dict) -> None:
    """Write context to cache. Best-effort."""
    try:
        p = _cache_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(ctx, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


def get_or_collect(ttl_hours: float = 24.0) -> dict:
    """Return cached context or collect fresh if expired/missing."""
    ctx = load(ttl_hours)
    if ctx is None:
        ctx = collect()
        save(ctx)
    return ctx
