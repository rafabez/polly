"""Skill: package management (install, remove, search, update)."""

SKILL = {
    "name": "packages",
    "description_en": "Install, remove, search, or update packages",
    "description_pt": "Instalar, remover, pesquisar ou atualizar pacotes",
    "platforms": ["linux", "darwin", "windows"],
}

# Maps (pkg_manager, action) -> command template with {pkg} placeholder
_TEMPLATES = {
    # apt
    ("apt", "install"):  "apt install {pkg}",
    ("apt", "remove"):   "apt remove {pkg}",
    ("apt", "search"):   "apt search {pkg}",
    ("apt", "update"):   "apt update && apt upgrade",
    ("apt", "list"):     "apt list --installed",
    # apt-get (alias)
    ("apt-get", "install"):  "apt-get install {pkg}",
    ("apt-get", "remove"):   "apt-get remove {pkg}",
    ("apt-get", "search"):   "apt-cache search {pkg}",
    ("apt-get", "update"):   "apt-get update && apt-get upgrade",
    ("apt-get", "list"):     "dpkg --list",
    # dnf / yum
    ("dnf", "install"):  "dnf install {pkg}",
    ("dnf", "remove"):   "dnf remove {pkg}",
    ("dnf", "search"):   "dnf search {pkg}",
    ("dnf", "update"):   "dnf upgrade",
    ("dnf", "list"):     "dnf list installed",
    ("yum", "install"):  "yum install {pkg}",
    ("yum", "remove"):   "yum remove {pkg}",
    ("yum", "search"):   "yum search {pkg}",
    ("yum", "update"):   "yum update",
    ("yum", "list"):     "yum list installed",
    # pacman
    ("pacman", "install"):  "pacman -S {pkg}",
    ("pacman", "remove"):   "pacman -R {pkg}",
    ("pacman", "search"):   "pacman -Ss {pkg}",
    ("pacman", "update"):   "pacman -Syu",
    ("pacman", "list"):     "pacman -Q",
    # brew
    ("brew", "install"):  "brew install {pkg}",
    ("brew", "remove"):   "brew uninstall {pkg}",
    ("brew", "search"):   "brew search {pkg}",
    ("brew", "update"):   "brew update && brew upgrade",
    ("brew", "list"):     "brew list",
    # winget
    ("winget", "install"):  "winget install {pkg}",
    ("winget", "remove"):   "winget uninstall {pkg}",
    ("winget", "search"):   "winget search {pkg}",
    ("winget", "update"):   "winget upgrade --all",
    ("winget", "list"):     "winget list",
    # choco
    ("choco", "install"):  "choco install {pkg}",
    ("choco", "remove"):   "choco uninstall {pkg}",
    ("choco", "search"):   "choco search {pkg}",
    ("choco", "update"):   "choco upgrade all",
    ("choco", "list"):     "choco list --local-only",
    # scoop
    ("scoop", "install"):  "scoop install {pkg}",
    ("scoop", "remove"):   "scoop uninstall {pkg}",
    ("scoop", "search"):   "scoop search {pkg}",
    ("scoop", "update"):   "scoop update *",
    ("scoop", "list"):     "scoop list",
}

_ACTION_KEYWORDS = {
    "install": ["install", "add", "get", "setup"],
    "remove": ["remove", "uninstall", "delete", "purge"],
    "search": ["search", "find", "look", "query"],
    "update": ["update", "upgrade", "refresh"],
    "list": ["list", "show", "installed"],
}


def _detect_action(task: str) -> str:
    task_l = task.lower()
    for action, keywords in _ACTION_KEYWORDS.items():
        if any(kw in task_l for kw in keywords):
            return action
    return "install"


def _extract_pkg(task: str, action: str) -> str:
    """Best-effort: remove action words and return the remaining token(s)."""
    words = task.split()
    stopwords = set(_ACTION_KEYWORDS.get(action, []) + ["package", "packages", "the", "a", "an"])
    remaining = [w for w in words if w.lower() not in stopwords]
    return " ".join(remaining) if remaining else task


def run(task: str, ctx: dict) -> list:
    """Return 1-2 candidate install/remove/etc. commands for the task."""
    pm = ctx.get("pkg_manager", "")
    action = _detect_action(task)
    pkg = _extract_pkg(task, action)

    cmds = []
    key = (pm, action)
    if key in _TEMPLATES:
        cmds.append(_TEMPLATES[key].format(pkg=pkg))

    # Offer sudo prefix on Linux if not already present
    if pm in ("apt", "apt-get", "dnf", "yum", "pacman") and cmds:
        cmds.append(f"sudo {cmds[0]}")

    return cmds[:2]
