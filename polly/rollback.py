"""
Stateful rollback for Polly (WU-16).

Records what each task changed so it can be undone with `polly --undo-last`.

What is tracked:
  - Files created (can delete)
  - Files overwritten (backup stored, can restore)
  - Commands run (not undoable; recorded for the audit log)

Transactions are stored in ~/.config/polly/transactions/<ts>.json.
Each entry written by record_*() is appended to the active transaction.
commit_transaction() finalises it; undo_last() reverses the most recent one.
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Optional

_TRANSACTIONS_DIR = Path.home() / ".config" / "polly" / "transactions"
_BACKUPS_DIR = Path.home() / ".config" / "polly" / "rollback_backups"

# Active transaction accumulates changes during a task; None between tasks
_active: Optional[dict] = None


def _ts() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S-%f")


def _transactions_dir() -> Path:
    _TRANSACTIONS_DIR.mkdir(parents=True, exist_ok=True)
    return _TRANSACTIONS_DIR


def _backups_dir() -> Path:
    _BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    return _BACKUPS_DIR


# ── Transaction lifecycle ──────────────────────────────────────────────────────

def begin_transaction(description: str) -> None:
    """Start recording a new transaction (call at start of each agent task)."""
    global _active
    _active = {
        "id": _ts(),
        "description": description,
        "started_at": time.time(),
        "actions": [],
    }


def commit_transaction() -> Optional[str]:
    """
    Save the active transaction to disk.
    Returns the transaction ID, or None if there was nothing to record.
    """
    global _active
    if not _active or not _active["actions"]:
        _active = None
        return None
    _active["committed_at"] = time.time()
    tid = _active["id"]
    path = _transactions_dir() / f"{tid}.json"
    try:
        path.write_text(json.dumps(_active, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass
    _active = None
    return tid


def _append_action(action: dict) -> None:
    """Append an action to the active transaction (best-effort)."""
    if _active is not None:
        _active["actions"].append(action)


# ── Recording helpers ──────────────────────────────────────────────────────────

def record_file_created(path: str) -> None:
    """Record that a file was created (undo = delete it)."""
    _append_action({"type": "file_created", "path": path})


def record_file_overwritten(path: str, original_content: str) -> None:
    """
    Record that a file was overwritten.  Stores the original content in a
    backup file so undo can restore it.
    """
    backup_name = f"{_ts()}_{Path(path).name}.bak"
    backup_path = _backups_dir() / backup_name
    try:
        backup_path.write_text(original_content, encoding="utf-8")
    except Exception:
        backup_name = None
    _append_action({
        "type": "file_overwritten",
        "path": path,
        "backup": str(backup_path) if backup_name else None,
    })


def record_command_run(command: str, exit_code: int) -> None:
    """Record a command run (informational only — commands are not undoable)."""
    _append_action({
        "type": "command_run",
        "command": command,
        "exit_code": exit_code,
        "note": "Commands cannot be automatically undone.",
    })


# ── Undo ──────────────────────────────────────────────────────────────────────

def _latest_transaction() -> Optional[dict]:
    """Return the most recent committed transaction, or None."""
    d = _transactions_dir()
    files = sorted(d.glob("*.json"), reverse=True)
    for f in files:
        try:
            return json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
    return None


def _delete_latest_transaction_file() -> None:
    d = _transactions_dir()
    files = sorted(d.glob("*.json"), reverse=True)
    if files:
        try:
            files[0].unlink()
        except Exception:
            pass


def undo_last() -> tuple[bool, list[str]]:
    """
    Undo the most recent committed transaction.

    Returns (success, list_of_messages) where each message describes what
    was reversed (or why an action could not be undone).
    """
    tx = _latest_transaction()
    if tx is None:
        return False, ["No transaction to undo."]

    msgs = [f"Undoing: {tx['description']}"]
    success = True

    # Reverse actions in reverse order
    for action in reversed(tx["actions"]):
        atype = action["type"]

        if atype == "file_created":
            p = Path(action["path"])
            try:
                if p.exists():
                    p.unlink()
                    msgs.append(f"  deleted: {action['path']}")
                else:
                    msgs.append(f"  skip (already gone): {action['path']}")
            except Exception as e:
                msgs.append(f"  FAILED to delete {action['path']}: {e}")
                success = False

        elif atype == "file_overwritten":
            backup = action.get("backup")
            p = Path(action["path"])
            if not backup:
                msgs.append(f"  cannot restore {action['path']} (no backup)")
                success = False
                continue
            bp = Path(backup)
            if not bp.exists():
                msgs.append(f"  cannot restore {action['path']} (backup missing)")
                success = False
                continue
            try:
                content = bp.read_text(encoding="utf-8")
                p.write_text(content, encoding="utf-8")
                bp.unlink()
                msgs.append(f"  restored: {action['path']}")
            except Exception as e:
                msgs.append(f"  FAILED to restore {action['path']}: {e}")
                success = False

        elif atype == "command_run":
            msgs.append(f"  (not undoable) command: {action['command']}")

    _delete_latest_transaction_file()
    return success, msgs


def list_transactions(limit: int = 10) -> list[dict]:
    """Return a list of recent transactions (most recent first)."""
    d = _transactions_dir()
    txs = []
    for f in sorted(d.glob("*.json"), reverse=True)[:limit]:
        try:
            tx = json.loads(f.read_text(encoding="utf-8"))
            txs.append({
                "id": tx.get("id", "?"),
                "description": tx.get("description", "?"),
                "actions": len(tx.get("actions", [])),
                "started_at": tx.get("started_at", 0),
            })
        except Exception:
            pass
    return txs
