"""Skill: system service management (start, stop, status, enable, disable)."""

SKILL = {
    "name": "services",
    "description_en": "Start, stop, restart, enable, or check status of system services",
    "description_pt": "Iniciar, parar, reiniciar, habilitar ou verificar serviços do sistema",
    "platforms": ["linux", "darwin", "windows"],
}

_ACTION_KEYWORDS = {
    "start":   ["start", "run", "launch", "begin"],
    "stop":    ["stop", "halt", "kill"],
    "restart": ["restart", "reload", "bounce"],
    "status":  ["status", "check", "info", "is", "running"],
    "enable":  ["enable", "autostart", "boot"],
    "disable": ["disable", "remove autostart"],
    "list":    ["list", "show", "all"],
}

# systemd commands (Linux)
_SYSTEMD = {
    "start":   "systemctl start {svc}",
    "stop":    "systemctl stop {svc}",
    "restart": "systemctl restart {svc}",
    "status":  "systemctl status {svc}",
    "enable":  "systemctl enable {svc}",
    "disable": "systemctl disable {svc}",
    "list":    "systemctl list-units --type=service",
}

# Windows sc / PowerShell
_WINDOWS = {
    "start":   "Start-Service {svc}",
    "stop":    "Stop-Service {svc}",
    "restart": "Restart-Service {svc}",
    "status":  "Get-Service {svc}",
    "enable":  "Set-Service -Name {svc} -StartupType Automatic",
    "disable": "Set-Service -Name {svc} -StartupType Disabled",
    "list":    "Get-Service",
}

# macOS launchctl
_MACOS = {
    "start":   "launchctl start {svc}",
    "stop":    "launchctl stop {svc}",
    "restart": "launchctl kickstart -k system/{svc}",
    "status":  "launchctl print system/{svc}",
    "list":    "launchctl list",
}


def _detect_action(task: str) -> str:
    task_l = task.lower()
    for action, kws in _ACTION_KEYWORDS.items():
        if any(kw in task_l for kw in kws):
            return action
    return "status"


def _extract_service(task: str, action: str) -> str:
    words = task.split()
    stopwords = set(sum(_ACTION_KEYWORDS.values(), []) + ["service", "the", "my", "a"])
    remaining = [w for w in words if w.lower() not in stopwords]
    return remaining[0] if remaining else "nginx"


def run(task: str, ctx: dict) -> list:
    platform = ctx.get("os", "linux")
    action = _detect_action(task)
    svc = _extract_service(task, action)

    if platform == "win32":
        table = _WINDOWS
        prefix = ""
    elif platform == "darwin":
        table = _MACOS
        prefix = ""
    else:
        table = _SYSTEMD
        prefix = "sudo "

    cmd = table.get(action, "").format(svc=svc)
    if not cmd:
        return []

    # Status is read-only; others may need sudo on Linux
    if platform not in ("win32", "darwin") and action != "status":
        return [f"{prefix}{cmd}"]
    return [cmd]
