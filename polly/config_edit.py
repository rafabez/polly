"""
Config-file assistant for Polly.

Reads a config file, sends it + an instruction to the model asking for the
FULL new file content, shows a unified diff, asks for confirmation via the
safety layer, writes a timestamped backup, then overwrites the file.

Entry points:
  edit_file(api, file_path, instruction, dry_run) -> bool
  revert_file(file_path) -> bool
"""

import re
import difflib
from datetime import datetime
from pathlib import Path
from typing import Optional

from .safety import confirm, Risk
from .i18n import get_text
from .utils import print_info, print_error, print_success


def _backup_path(p: Path) -> Path:
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    return p.parent / f"{p.name}.{ts}.bak"


def _latest_backup(p: Path) -> Optional[Path]:
    """Return the most recent .bak for this file, or None."""
    backups = sorted(p.parent.glob(f"{p.name}.*.bak"), reverse=True)
    return backups[0] if backups else None


def _strip_fences(text: str) -> str:
    """Remove leading/trailing markdown code fences if the model wrapped the output."""
    text = text.strip()
    # Remove ```lang ... ``` or ``` ... ```
    m = re.match(r"^```[^\n]*\n(.*?)```\s*$", text, re.DOTALL)
    if m:
        return m.group(1)
    return text


def _colorize_diff(diff_lines: list) -> str:
    """Return diff with +/- lines highlighted (plain ANSI for terminal)."""
    out = []
    for line in diff_lines:
        if line.startswith("+") and not line.startswith("+++"):
            out.append(f"\033[32m{line}\033[0m")   # green
        elif line.startswith("-") and not line.startswith("---"):
            out.append(f"\033[31m{line}\033[0m")   # red
        elif line.startswith("@@"):
            out.append(f"\033[36m{line}\033[0m")   # cyan
        else:
            out.append(line)
    return "\n".join(out)


def edit_file(api, file_path: str, instruction: str, dry_run: bool = False) -> bool:
    """
    Read a file, ask the model to apply `instruction`, show the diff,
    confirm, backup, and write.

    Args:
        api:         PollinationsAPI instance.
        file_path:   Path to the file to edit.
        instruction: Plain-language edit instruction.
        dry_run:     If True, show diff but never write.

    Returns:
        True if the file was written (or would be in dry-run), False on error/abort.
    """
    from .config import get_config
    config = get_config()
    max_kb = int(config.get("edit_max_kb", 256))

    p = Path(file_path).expanduser()

    if not p.exists():
        print_error(get_text("edit.not_found", path=str(p)))
        return False

    size_kb = p.stat().st_size / 1024
    if size_kb > max_kb:
        print_error(get_text("edit.too_big", path=str(p), size=f"{size_kb:.0f}KB", limit=f"{max_kb}KB"))
        return False

    try:
        original = p.read_text(encoding="utf-8")
    except Exception as e:
        print_error(get_text("edit.read_error", error=str(e)))
        return False

    # Ask the model for the full new file
    print_info(get_text("edit.thinking"))
    system_msg = (
        "You are a precise config-file editor. "
        "The user will give you a file and an instruction. "
        "Reply with ONLY the complete new file content, no explanation, "
        "no markdown fences, no comments about your changes."
    )
    user_msg = (
        f"File: {p.name}\n\n"
        f"---BEGIN FILE---\n{original}\n---END FILE---\n\n"
        f"Instruction: {instruction}"
    )

    try:
        new_content = api.chat_completion(
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.1,
        )
    except Exception as e:
        print_error(get_text("edit.api_error", error=str(e)))
        return False

    new_content = _strip_fences(new_content)

    if new_content == original:
        print_info(get_text("edit.no_changes"))
        return True

    # Show diff
    diff = list(difflib.unified_diff(
        original.splitlines(),
        new_content.splitlines(),
        fromfile=f"a/{p.name}",
        tofile=f"b/{p.name}",
        lineterm="",
    ))

    if not diff:
        print_info(get_text("edit.no_changes"))
        return True

    print()
    print(_colorize_diff(diff))
    print()

    if dry_run:
        print_info(get_text("edit.dry_run", path=str(p)))
        return True

    # Confirm via safety layer (CAUTION — writes a file)
    if not confirm(f"edit {p.name}", Risk.CAUTION):
        print_info(get_text("safety.aborted"))
        return False

    # Backup then write
    bak = _backup_path(p)
    try:
        bak.write_text(original, encoding="utf-8")
        p.write_text(new_content, encoding="utf-8")
    except Exception as e:
        print_error(get_text("edit.write_error", error=str(e)))
        return False

    print_success(get_text("edit.backup_saved", path=str(bak)))
    print_success(get_text("edit.written", path=str(p)))
    return True


def revert_file(file_path: str) -> bool:
    """
    Restore the most recent .bak for the given file.

    Returns:
        True if reverted, False if no backup found or write failed.
    """
    p = Path(file_path).expanduser()
    bak = _latest_backup(p)

    if bak is None:
        print_error(get_text("edit.no_backup", path=str(p)))
        return False

    try:
        content = bak.read_text(encoding="utf-8")
        p.write_text(content, encoding="utf-8")
        print_success(get_text("edit.reverted", path=str(p), backup=str(bak)))
        return True
    except Exception as e:
        print_error(get_text("edit.write_error", error=str(e)))
        return False
