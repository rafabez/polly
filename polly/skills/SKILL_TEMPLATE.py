"""
Polly skill template — copy this file, rename it, and drop it in
~/.config/polly/skills/ to create a custom skill.

The file name becomes the module name; the SKILL["name"] is what users type
in `polly --skill <name> "task"`.

Polly automatically discovers skills in:
  1. polly/skills/      (built-in)
  2. ~/.config/polly/skills/   (user skills — this directory)
  3. Installed packages with entry_points group "polly.skills"

=== Skill interface ===
SKILL dict    — metadata displayed in --list-skills
run(task, ctx) — called by Polly; must return a list of command strings

ctx keys (from system_context.collect()):
  os          "linux" | "darwin" | "win32"
  os_name     human-readable name ("Ubuntu 24.04", "Windows 11", ...)
  shell       "bash" | "zsh" | "PowerShell" | ...
  pkg_manager "apt" | "brew" | "winget" | ... (first found, may be empty)
  tools       dict of tool → version string (python, git, node, ...)
"""

SKILL = {
    "name": "myskill",                      # unique lowercase slug
    "description_en": "Short English description of what this skill does",
    "description_pt": "Breve descrição em português do que esse skill faz",
    "platforms": ["linux", "darwin", "windows"],   # supported platforms
}


def run(task: str, ctx: dict) -> list:
    """
    Translate the user's task into one or more candidate shell commands.

    Args:
        task: the raw natural-language request (e.g. "install nginx")
        ctx:  system context dict (see top of file for keys)

    Returns:
        List of command strings (usually 1-2). Polly will show them to the
        user, let them pick if multiple, then run through safety+confirm.
        Return [] if no command can be generated for this task.
    """
    platform = ctx.get("os", "linux")

    # Example: return a different command per platform
    if platform == "win32":
        return [f"winget install {task}"]
    elif platform == "darwin":
        return [f"brew install {task}"]
    else:
        return [f"apt install {task}"]
