"""Skill: disk usage (read-only — always SAFE)."""

SKILL = {
    "name": "disk",
    "description_en": "Show disk usage, free space, or largest directories",
    "description_pt": "Mostrar uso do disco, espaço livre ou maiores diretórios",
    "platforms": ["linux", "darwin", "windows"],
}

_LINUX_COMMANDS = {
    "free":    "df -h",
    "usage":   "du -sh * | sort -rh | head -20",
    "largest": "du -ah . | sort -rh | head -20",
    "inode":   "df -i",
}

_WINDOWS_COMMANDS = {
    "free":    "Get-PSDrive -PSProvider FileSystem",
    "usage":   "Get-ChildItem -File -Recurse | Sort-Object Length -Descending | Select-Object -First 20 FullName, Length",
    "largest": "Get-ChildItem -Directory | ForEach-Object { $s=(Get-ChildItem $_ -Recurse -File | Measure-Object -Property Length -Sum).Sum; [PSCustomObject]@{Dir=$_.Name;SizeMB=[math]::Round($s/1MB,1)}} | Sort-Object SizeMB -Descending | Select-Object -First 10",
    "inode":   "Get-PSDrive -PSProvider FileSystem",
}

_MACOS_COMMANDS = {
    "free":    "df -h",
    "usage":   "du -sh * | sort -rh | head -20",
    "largest": "du -ah . | sort -rh | head -20",
    "inode":   "df -i",
}

_ACTION_KEYWORDS = {
    "free":    ["free", "available", "space", "remaining"],
    "largest": ["largest", "biggest", "big", "heavy", "size"],
    "inode":   ["inode", "inodes"],
    "usage":   ["usage", "used", "disk", "storage", "how much"],
}


def _detect_subcommand(task: str) -> str:
    task_l = task.lower()
    for sub, kws in _ACTION_KEYWORDS.items():
        if any(kw in task_l for kw in kws):
            return sub
    return "free"


def run(task: str, ctx: dict) -> list:
    platform = ctx.get("os", "linux")
    sub = _detect_subcommand(task)

    if platform == "win32":
        cmd = _WINDOWS_COMMANDS.get(sub, _WINDOWS_COMMANDS["free"])
    elif platform == "darwin":
        cmd = _MACOS_COMMANDS.get(sub, _MACOS_COMMANDS["free"])
    else:
        cmd = _LINUX_COMMANDS.get(sub, _LINUX_COMMANDS["free"])

    return [cmd]
