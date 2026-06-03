"""
OS Skills registry for Polly.

A skill is a small module that knows the idiomatic, platform-specific commands
for a category of system task (packages, services, disk...).  Skills return
candidate command strings — they never execute directly; all execution goes
through the safety+confirm path in executor.py.

Registration is automatic: every module in this package that defines a SKILL
dict is discovered at import time.
"""

import importlib
import pkgutil
from pathlib import Path
from typing import Optional

# Registry: { skill_name: skill_module }
_REGISTRY: dict = {}


def _load_all() -> None:
    """Auto-discover and register all skill modules in this package."""
    pkg_dir = Path(__file__).parent
    for info in pkgutil.iter_modules([str(pkg_dir)]):
        if info.name.startswith("_"):
            continue
        try:
            mod = importlib.import_module(f".{info.name}", package=__package__)
            if hasattr(mod, "SKILL"):
                name = mod.SKILL["name"]
                _REGISTRY[name] = mod
        except Exception:
            pass


def list_skills() -> list:
    """Return list of skill info dicts for display."""
    if not _REGISTRY:
        _load_all()
    return [mod.SKILL for mod in _REGISTRY.values()]


def get_skill(name: str) -> Optional[object]:
    """Return skill module by name (case-insensitive prefix match), or None."""
    if not _REGISTRY:
        _load_all()
    name_l = name.lower()
    if name_l in _REGISTRY:
        return _REGISTRY[name_l]
    matches = [k for k in _REGISTRY if k.startswith(name_l)]
    if len(matches) == 1:
        return _REGISTRY[matches[0]]
    return None


def run_skill(name: str, task: str, ctx: dict) -> list:
    """
    Run a skill and return a list of candidate command strings.
    ctx is the system_context dict (platform, pkg_manager, etc.).
    Returns [] if skill not found.
    """
    mod = get_skill(name)
    if mod is None:
        return []
    return mod.run(task, ctx)
