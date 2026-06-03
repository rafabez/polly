"""
Command executor for Polly.

Runs the command that Polly generated, gated by the safety layer.
Nothing executes here without passing safety.classify() + safety.confirm().
Every execution is audit-logged regardless of --no-memory.

Entry point: execute(cmd, dry_run=False)
"""

import os
import sys
import subprocess
from typing import Optional

from .safety import classify, confirm, audit
from .i18n import get_text
from .utils import print_info, print_error, print_success


def _user_shell() -> list:
    """
    Return the command prefix for running a shell command on this platform.
    Uses PowerShell on Windows, $SHELL (or bash) on Unix.
    """
    if sys.platform == "win32":
        # PowerShell gives us proper quoting and access to all Windows commands
        return ["powershell", "-NoProfile", "-Command"]
    shell = os.environ.get("SHELL", "bash")
    return [shell, "-c"]


def execute(cmd: str, dry_run: bool = False) -> Optional[int]:
    """
    Classify, confirm, and run a shell command.

    Args:
        cmd:     The shell command string to execute.
        dry_run: If True, show classification + command but never execute.

    Returns:
        Exit code (int) if executed, None if aborted/dry-run.
    """
    risk = classify(cmd)

    # Dry-run: just show what would happen
    if dry_run:
        print_info(get_text("exec.dry_run", cmd=cmd, risk=risk.value))
        return None

    # Gate on safety
    if not confirm(cmd, risk):
        print_info(get_text("safety.aborted"))
        return None

    # Run
    print_info(get_text("exec.running", cmd=cmd))
    prefix = _user_shell()

    try:
        proc = subprocess.run(
            prefix + [cmd],
            # Don't capture output — stream it live to the user's terminal
            stdin=sys.stdin if sys.stdin.isatty() else None,
        )
        exit_code = proc.returncode
    except KeyboardInterrupt:
        print()
        print_info(get_text("exec.interrupted"))
        audit(cmd, risk, -1, "interrupted by user")
        return -1
    except Exception as e:
        print_error(f"{get_text('exec.failed')}: {e}")
        audit(cmd, risk, -1, str(e))
        return -1

    if exit_code == 0:
        print_success(get_text("exec.exit_code", code=exit_code))
    else:
        print_error(get_text("exec.exit_code", code=exit_code))

    audit(cmd, risk, exit_code, f"exit={exit_code}")
    return exit_code


def pick_command(commands: list) -> Optional[str]:
    """
    When -c produced multiple commands, let the user pick one to execute.
    Returns the chosen command string or None if the user cancels.
    """
    if not commands:
        return None
    if len(commands) == 1:
        return commands[0]

    print_info(get_text("exec.pick_prompt"))
    for i, cmd in enumerate(commands, 1):
        print(f"  {i}. {cmd}")
    print()
    try:
        raw = input(get_text("exec.pick_choice", n=len(commands))).strip()
        if not raw or raw.lower() in ("q", "quit", "cancel"):
            return None
        idx = int(raw)
        if 1 <= idx <= len(commands):
            return commands[idx - 1]
        print_error(get_text("msg.invalid_selection") + f" 1-{len(commands)}")
        return None
    except (ValueError, KeyboardInterrupt, EOFError):
        return None
