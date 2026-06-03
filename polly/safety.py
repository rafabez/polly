"""
Safety layer for Polly command execution.

Classifies commands by risk level and gates dangerous ones behind explicit
user confirmation. This module MUST be used by any execution path — nothing
runs without going through classify() + confirm().

Risk levels (ascending danger):
  SAFE        — read-only; may run with a single y/n or auto if configured
  CAUTION     — writes, network installs, renames; requires y/n
  DESTRUCTIVE — irreversible (rm -rf, format, service stop…); requires typing a word
  BLOCKED     — never executed; hard stop with explanation
"""

import re
from enum import Enum
from typing import Optional

from .config import get_config
from .i18n import get_text


class Risk(Enum):
    SAFE = "safe"
    CAUTION = "caution"
    DESTRUCTIVE = "destructive"
    BLOCKED = "blocked"


# ── Pattern tables ────────────────────────────────────────────────────────────

_BLOCKED_PATTERNS = [
    # Fork bomb
    r":\(\)\s*\{.*\|.*&",
    # Disk nuking
    r"\bdd\b.*\bof=/dev/(s|h|v|xv|nv|nvme|mmcblk)",
    r"\bmkfs\b",
    r"\bshred\b.*(/dev/|/proc/)",
    # Piping remote code into a shell
    r"\b(curl|wget|fetch)\b.*(http|ftp).*\|\s*(bash|sh|zsh|fish|cmd|powershell)",
    # Mass permission changes on root
    r"\bchmod\s+-[rR]\s+777\s+/[^/]",
    r"\bchown\s+-[rR].*\s+/[^/]",
    # Wipe entire disk/root
    r"\brm\s+(-[rfRF]+\s+)+/\s*$",
    r"\bRemove-Item\s+.*-Recurse.*C:\\\\?$",
    r"\bformat\s+[cCdD]:\s*/",
    # Windows system dir nuking
    r"[%$]SystemRoot%?\\\\?$",
]

_DESTRUCTIVE_PATTERNS = [
    # rm -rf
    r"\brm\s+.*-[rRfF]*[rR][fF]",
    r"\brm\s+.*-[rRfF]*[fF][rR]",
    r"\brmdir\s+(/s|--no-preserve-root)",
    # Windows equivalents
    r"\bRemove-Item\b.*-Recurse",
    r"\brd\s+/s",
    # Format / wipe
    r"\bformat\b",
    r"\bdiskpart\b",
    # Package removal
    r"\b(apt|apt-get|yum|dnf|pacman|brew|pip|npm|cargo)\b.*(remove|uninstall|purge|erase)",
    r"\bwinget\b.*(uninstall|remove)",
    # Git destructive
    r"\bgit\b.*(reset\s+--hard|clean\s+-[fdFD])",
    r"\bgit\b.*push\s+--force",
    # Truncate a file
    r">\s*\S+",
    # kill -9
    r"\bkill\s+-9\b",
    r"\bkillall\b",
    r"\bStop-Process\b",
    # Privilege escalation
    r"\bsudo\b",
    r"\brunas\b",
    r"\bsu\s+-",
    # Service stop/disable
    r"\b(systemctl|service)\b.*(stop|disable|mask)",
    r"\bStop-Service\b",
    r"\bsc\b.*(stop|delete)",
    # crontab remove
    r"\bcrontab\s+-r",
]

_CAUTION_PATTERNS = [
    # Network installs
    r"\b(apt|apt-get|yum|dnf|pacman|brew|pip|npm|yarn|cargo|gem|winget|choco|scoop)\b.*(install|upgrade|update)",
    # File writes / moves
    r"\bmv\b",
    r"\bMove-Item\b",
    r"\bcp\b.*(-r|-R)",
    r"\bchmod\b",
    r"\bchown\b",
    r"\bsed\b.*-i",
    r"\bawk\b.*>",
    # System config edits
    r"\bnano\b|\bvim\b|\bvi\b|\bemacs\b|\bnotepad\b",
    r"/etc/",
    r"C:\\Windows\\System32",
    # Firewall / network
    r"\bufw\b|\biptables\b|\bfirewall-cmd\b",
    r"\bifconfig\b|\bip\s+addr\b",
    # Cron edits
    r"\bcrontab\s+-e",
]

_SAFE_PATTERNS = [
    r"\bls\b|\bdir\b|\bGet-ChildItem\b",
    r"\bcat\b|\bGet-Content\b|\btype\b",
    r"\becho\b|\bWrite-Output\b|\bpwd\b|\bSet-Location\b",
    r"\bgit\s+(status|log|diff|branch|remote|show|fetch)\b",
    r"\bps\b|\bGet-Process\b|\btop\b|\bhtop\b",
    r"\bdf\b|\bdu\b|\bGet-PSDrive\b",
    r"\bwhich\b|\bwhere\b|\bwhereis\b|\bGet-Command\b",
    r"\benv\b|\bprintenv\b|\bGet-Env\b|\bSet-Location\b",
    r"\bman\b|\bhelp\b",
    r"\bping\b|\btraceroute\b|\bnslookup\b",
    r"\bsystemctl\s+(status|list-units|is-active)\b",
    r"\bdocker\s+(ps|images|inspect|logs)\b",
]


def _matches_any(patterns: list, cmd: str) -> bool:
    for pat in patterns:
        if re.search(pat, cmd, re.IGNORECASE):
            return True
    return False


def _check_config_overrides(cmd: str) -> Optional[Risk]:
    """Apply user-configured allowlist/denylist. Denylist wins."""
    config = get_config()
    denylist = config.get("safety_denylist", [])
    allowlist = config.get("safety_allowlist", [])

    for pat in denylist:
        if re.search(pat, cmd, re.IGNORECASE):
            return Risk.BLOCKED

    for pat in allowlist:
        if re.search(pat, cmd, re.IGNORECASE):
            return Risk.SAFE

    return None


def classify(cmd: str) -> Risk:
    """
    Classify a command string into a Risk level.
    Config overrides are applied first (denylist wins over everything).
    """
    override = _check_config_overrides(cmd)
    if override is not None:
        return override

    if _matches_any(_BLOCKED_PATTERNS, cmd):
        return Risk.BLOCKED
    if _matches_any(_DESTRUCTIVE_PATTERNS, cmd):
        return Risk.DESTRUCTIVE
    if _matches_any(_SAFE_PATTERNS, cmd):
        return Risk.SAFE
    if _matches_any(_CAUTION_PATTERNS, cmd):
        return Risk.CAUTION

    # Default to CAUTION for unknown commands — better safe than sorry
    return Risk.CAUTION


def _prompt(msg: str) -> str:
    """Read a line from stdin; return '' on EOF/interrupt."""
    try:
        return input(msg).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return ""


def confirm(cmd: str, risk: Risk) -> bool:
    """
    Ask the user for confirmation based on the risk level.
    Returns True if execution should proceed, False otherwise.
    """
    config = get_config()

    if risk == Risk.BLOCKED:
        from .utils import print_error
        print_error(get_text("safety.blocked", reason=_block_reason(cmd)))
        return False

    if risk == Risk.SAFE:
        if config.get("execute_autoconfirm_safe", False):
            return True
        answer = _prompt(get_text("safety.confirm_safe", cmd=cmd))
        return answer.lower() in ("y", "yes", "s", "sim")

    if risk == Risk.CAUTION:
        answer = _prompt(get_text("safety.confirm_caution", cmd=cmd))
        return answer.lower() in ("y", "yes", "s", "sim")

    # DESTRUCTIVE — require typing a specific word
    confirm_word = "RUN"
    answer = _prompt(get_text("safety.confirm_destructive", cmd=cmd, word=confirm_word))
    return answer == confirm_word


def _block_reason(cmd: str) -> str:
    """Return a short reason string for why this command is blocked."""
    cmd_l = cmd.lower()
    if "mkfs" in cmd_l or "dd" in cmd_l:
        return "disk format/wipe operations are not allowed"
    if "curl" in cmd_l or "wget" in cmd_l:
        return "piping remote code into a shell is not allowed"
    if "chmod 777" in cmd_l or "chown" in cmd_l:
        return "recursive permission changes on root are not allowed"
    if "fork bomb" in cmd_l or ":(){" in cmd:
        return "fork bombs are not allowed"
    return "this command is blocked by safety rules"


def audit(cmd: str, risk: Risk, exit_code: int, output_summary: str) -> None:
    """Write a structured audit line to history.log."""
    try:
        from . import memory
        from datetime import datetime
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = (
            f"{'=' * 70}\n"
            f"[EXEC] [{ts}] risk={risk.value} exit={exit_code}\n"
            f"cmd: {cmd}\n"
            f"out: {output_summary[:200]}\n"
        )
        p = memory._history_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass  # audit is best-effort
