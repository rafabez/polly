"""
OS Skills registry for Polly (WU-18: Plugin/Skill SDK).

A skill is a small module that knows the idiomatic, platform-specific commands
for a category of system task (packages, services, disk...).  Skills return
candidate command strings — they never execute directly; all execution goes
through the safety+confirm path in executor.py.

== Skill interface ==
A skill module must define:

  SKILL = {
      "name": "myskill",               # unique lowercase identifier
      "description_en": "...",         # shown in --list-skills (English)
      "description_pt": "...",         # shown in --list-skills (Portuguese)
      "platforms": ["linux", "darwin", "windows"],
  }

  def run(task: str, ctx: dict) -> list[str]:
      # task: the user's natural-language request
      # ctx:  system_context dict (os, pkg_manager, shell, tools, ...)
      # returns: list of candidate command strings (1-3 max)

== Installing third-party skills ==
Three discovery paths, checked in order:

  1. Built-in: polly/skills/*.py  (packages, services, disk)
  2. User skills: ~/.config/polly/skills/*.py  (drop a .py file here)
  3. Package entry points: packages that expose the entry point group
     "polly.skills" are loaded automatically.  In your package's
     setup.cfg / pyproject.toml:

       [options.entry_points]
       polly.skills =
           myskill = mypackage.myskill

     The referenced module must define SKILL + run() as above.
"""

import importlib
import importlib.metadata
import importlib.util
import pkgutil
from pathlib import Path
from typing import Optional

# Registry: { skill_name: skill_module }
_REGISTRY: dict = {}

_USER_SKILLS_DIR = Path.home() / ".config" / "polly" / "skills"


def _load_builtin() -> None:
    """Load built-in skills from polly/skills/."""
    pkg_dir = Path(__file__).parent
    for info in pkgutil.iter_modules([str(pkg_dir)]):
        if info.name.startswith("_"):
            continue
        try:
            mod = importlib.import_module(f".{info.name}", package=__package__)
            if hasattr(mod, "SKILL"):
                _REGISTRY[mod.SKILL["name"]] = mod
        except Exception:
            pass


def _load_user_skills() -> None:
    """Load user skills from ~/.config/polly/skills/*.py."""
    if not _USER_SKILLS_DIR.exists():
        return
    import sys
    if str(_USER_SKILLS_DIR) not in sys.path:
        sys.path.insert(0, str(_USER_SKILLS_DIR))
    for py in _USER_SKILLS_DIR.glob("*.py"):
        if py.name.startswith("_"):
            continue
        try:
            spec = importlib.util.spec_from_file_location(py.stem, py)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if hasattr(mod, "SKILL"):
                _REGISTRY[mod.SKILL["name"]] = mod
        except Exception:
            pass


def _load_entry_points() -> None:
    """Load skills from installed packages exposing the 'polly.skills' group."""
    try:
        eps = importlib.metadata.entry_points(group="polly.skills")
        for ep in eps:
            try:
                mod = ep.load()
                if hasattr(mod, "SKILL"):
                    _REGISTRY[mod.SKILL["name"]] = mod
            except Exception:
                pass
    except Exception:
        pass


def _load_all() -> None:
    """Discover and register all skills from all sources."""
    _load_builtin()
    _load_user_skills()
    _load_entry_points()


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
