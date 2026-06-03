"""
Tool-using agent loop for Polly (WU-15).

Polly acts as an agent: it sends the goal to the model with a set of tool
definitions, the model decides which tools to call, Polly runs each through the
safety+confirm layer, feeds the results back, and loops until the model gives a
final text answer or the step cap is reached.

The user can abort at any step (Ctrl-C or by answering 'n' to a confirmation).
Nothing destructive ever runs without explicit user approval (safety.confirm).

Entry point: run(api, goal, dry_run, stream) -> None
"""

import json

from .i18n import get_text
from .utils import print_info, print_error, print_success, print_warning, print_response
from .executor import execute

# ── Tool definitions (OpenAI function-calling schema) ─────────────────────────

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": (
                "Execute a shell command on the user's machine. "
                "The command runs in the user's default shell. "
                "Always prefer read-only commands when possible."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The shell command to run",
                    },
                    "reason": {
                        "type": "string",
                        "description": "One-sentence explanation of why this command is needed",
                    },
                },
                "required": ["command", "reason"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file on the user's machine.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute or relative path to the file",
                    },
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": (
                "Write content to a file. Creates the file if it does not exist, "
                "overwrites if it does."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to write to",
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write",
                    },
                    "reason": {
                        "type": "string",
                        "description": "Why this file needs to be written",
                    },
                },
                "required": ["path", "content", "reason"],
            },
        },
    },
]

# ── Tool execution ─────────────────────────────────────────────────────────────

def _run_tool(name: str, args: dict, dry_run: bool) -> str:
    """
    Dispatch a tool call from the model.
    All mutating tools go through safety.confirm.
    Returns a string result to feed back to the model.
    """
    if name == "run_command":
        cmd = args.get("command", "")
        reason = args.get("reason", "")
        print_info(f"[tool] run_command: {cmd}")
        if reason:
            print_info(f"       reason: {reason}")
        exit_code = execute(cmd, dry_run=dry_run)
        if exit_code is None:
            return "Command was aborted by user."
        return f"Command exited with code {exit_code}."

    elif name == "read_file":
        from pathlib import Path
        path = args.get("path", "")
        print_info(f"[tool] read_file: {path}")
        try:
            from .utils import read_file as _rf
            content = _rf(path)
            # Cap to avoid flooding the context
            if len(content) > 4000:
                content = content[:4000] + "\n…[truncated]"
            return content
        except Exception as e:
            return f"Error reading file: {e}"

    elif name == "write_file":
        from pathlib import Path
        from .safety import confirm, Risk
        path = args.get("path", "")
        content = args.get("content", "")
        reason = args.get("reason", "")
        print_info(f"[tool] write_file: {path}")
        if reason:
            print_info(f"       reason: {reason}")
        if dry_run:
            print_info(get_text("exec.dry_run", cmd=f"write {path}", risk="caution"))
            return "File write skipped (dry-run)."
        if not confirm(f"write_file({path})", Risk.CAUTION):
            return "File write aborted by user."
        try:
            p = Path(path).expanduser()
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
            return f"Written {len(content)} characters to {path}."
        except Exception as e:
            return f"Error writing file: {e}"

    else:
        return f"Unknown tool: {name}"


# ── Agent loop ─────────────────────────────────────────────────────────────────

def run(
    api,
    goal: str,
    dry_run: bool = False,
    no_markdown: bool = False,
) -> None:
    """
    Run the agent loop for a given goal.

    1. Show the plan (model's first response).
    2. If the model calls tools, confirm + execute each, feed results back.
    3. Repeat until a final text answer or max_steps reached.
    4. Print the final answer.
    """
    from .config import get_config
    config = get_config()

    if not config.get("agent_enabled", False):
        print_error(get_text("agent.disabled"))
        return

    max_steps = int(config.get("agent_max_steps", 8))
    model = config.get("default_model")
    temperature = float(config.get("temperature", 0.7))

    system_msg = (
        "You are Polly, an AI assistant that helps users accomplish tasks on their "
        "computer. You have access to tools to run commands, read files, and write "
        "files. Always explain what you are doing before each tool call. "
        "When the task is complete, summarise what you did in plain language. "
        "If you need clarification, ask — do not guess. "
        "Be conservative: prefer read-only operations when they answer the question."
    )

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": goal},
    ]

    print_info(get_text("agent.starting", goal=goal))
    print()

    for step in range(1, max_steps + 1):
        # Build the request payload
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "tools": TOOLS,
            "tool_choice": "auto",
        }

        # Determine endpoint
        if api.use_custom_provider:
            url = api._custom_provider_url()
        elif api.use_backend:
            url = f"{api.backend_url}/api/chat/completions"
        else:
            url = f"{api.base_url}/openai"

        try:
            resp = api._post_with_retry(url, payload, api._get_headers())
            resp.raise_for_status()
            data = resp.json()
        except KeyboardInterrupt:
            print()
            print_info(get_text("agent.aborted"))
            return
        except Exception as e:
            print_error(f"{get_text('agent.api_error')}: {e}")
            return

        choice = data["choices"][0]
        msg = choice["message"]
        finish_reason = choice.get("finish_reason", "")

        # Append assistant message to history
        messages.append(msg)

        tool_calls = msg.get("tool_calls") or []

        if not tool_calls:
            # Final answer
            content = msg.get("content", "")
            print()
            print_success(get_text("agent.done"))
            print()
            print_response(content, format_markdown=not no_markdown)
            return

        # --- Process tool calls ---
        print_info(get_text("agent.step", step=step, total=max_steps))

        tool_results = []
        for tc in tool_calls:
            fn = tc.get("function", {})
            name = fn.get("name", "")
            try:
                args = json.loads(fn.get("arguments", "{}"))
            except json.JSONDecodeError:
                args = {}

            try:
                result = _run_tool(name, args, dry_run)
            except KeyboardInterrupt:
                print()
                print_info(get_text("agent.aborted"))
                return

            tool_results.append({
                "role": "tool",
                "tool_call_id": tc.get("id", ""),
                "content": result,
            })

        messages.extend(tool_results)

        if finish_reason == "stop":
            break

    # Reached max steps without a final answer
    print_warning(get_text("agent.max_steps", n=max_steps))
