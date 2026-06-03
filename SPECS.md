# Polly — Technical Implementation Specs

> Implementation-ready specification for the [ROADMAP](ROADMAP.md). Each item is a
> self-contained **Work Unit (WU)** that can be coded independently, in order.
> Written to be executed by an implementer (human or model) without further
> architectural decisions. If a choice arises that isn't covered here, prefer the
> simplest option consistent with the Global Conventions below.

---

## How to use this document

- Do **one Work Unit at a time**, in the order listed (they're dependency-sorted).
- Each WU has: **Goal · Files · Spec · Config · i18n · CLI · Edge cases · Tests ·
  Acceptance · Verify**. Implement all sections; don't skip tests.
- After each WU: run `python -m pytest tests/test_basic.py -q` (must stay green),
  then the WU's **Verify** commands.
- Commit per WU with message `feat(WU-NN): <title>` or `fix/chore` as fitting.

## Global Conventions (apply to every WU)

1. **Bilingual contract.** Every user-facing string goes through `get_text(key)`
   in `polly/i18n.py` and MUST exist in BOTH `"en"` and `"pt"` dictionaries. The
   test `test_i18n_key_parity` / `test_i18n_placeholder_parity` enforce this.
2. **Honest UX.** Never fake success or silently substitute. On failure, return a
   clear, specific, actionable error. No silent fallbacks that mislead.
3. **Best-effort side state never breaks the main flow.** Memory, cache, logs,
   telemetry: wrap in try/except and degrade silently if they fail.
4. **Config lives in** `~/.config/polly/` (`Config.config_dir`). New on-disk state
   goes in a subfolder there. Windows path: `C:\Users\<u>\.config\polly\`.
5. **Cross-platform.** Code must run on Windows (PowerShell), macOS, Linux. Use
   `pathlib`, `sys.platform` guards, never hardcode `/`.
6. **New config keys** go in `DEFAULT_CONFIG` (`polly/config.py`) with a safe
   default and a one-line comment. Read via `config.get("key", default)`.
7. **New CLI flags** are added in `polly/cli.py` `create_parser()`, listed in
   `polly/help_formatter.py`, and (if they don't need a prompt) added to BOTH the
   `needs_prompt` set in `cli.py:validate_args` and the `is_config_command` set in
   `__main__.py:main`.
8. **Tests** go in `tests/test_basic.py` (or a new `tests/test_<area>.py`). Use
   `tmp_path` + `monkeypatch`; never touch the real `~/.config/polly`.

## Codebase map (current)

| File | Responsibility |
|------|----------------|
| `polly/__main__.py` | Entry flow: `main`, `handle_config_commands`, `handle_standard_query`, `handle_interactive_mode` |
| `polly/api.py` | `PollinationsAPI`: `chat_completion`, `simple_query`, `get_available_models`, error mapping |
| `polly/config.py` | `DEFAULT_CONFIG`, `Config`, `fetch_text_models`, Tinybird health, `AVAILABLE_MODELS` |
| `polly/cli.py` | argparse: `create_parser`, `_get_model_names`, `validate_args` |
| `polly/memory.py` | per-terminal session memory + `history.log` |
| `polly/prompts.py` | `PROMPTS_EN/PT`, `get_prompt`, modes |
| `polly/i18n.py` | `TRANSLATIONS` (en/pt), `get_text` |
| `polly/utils.py` | print helpers, `truncate_context`, interactive selectors, `show_spinner` |
| `polly/help_formatter.py` | Rich `print_help` |
| `polly/pdf_handler.py` | PDF read/write |

---

# PHASE 0 — Engineering foundation (do first)

## WU-01 — CI + lint + test gate
- **Goal:** every push runs tests; broken bilingual contract or failing test fails CI.
- **Files:** `.github/workflows/ci.yml` (new); `pyproject.toml` (add `[tool.ruff]`,
  dev deps `pytest`, `ruff`).
- **Spec:** GitHub Actions on push/PR: matrix Python 3.11–3.13; steps: install,
  `ruff check polly`, `pytest -q`. Ruff config: line length 100, ignore E501 in
  `i18n.py` (long strings). Don't fail on existing style nits — set a minimal rule
  set (`E`, `F`, `W`) and `--exit-zero` is NOT used (must actually gate).
- **Edge cases:** Windows-only code paths shouldn't break Linux CI (guard
  `_windows_console_id`, already guarded).
- **Tests:** n/a (this is the harness).
- **Acceptance:** ☐ CI green on a clean push ☐ a deliberately broken test fails CI
  ☐ adding an EN-only i18n key fails CI.
- **Verify:** push a branch; observe the Actions run.

## WU-02 — Token-aware context budgeting
- **Goal:** stop counting raw characters; budget by estimated tokens and respect
  each model's real `context_length`.
- **Files:** `polly/utils.py` (new `estimate_tokens`, update `truncate_context`);
  `polly/memory.py` (use it); `polly/config.py` (read model `context_length`).
- **Spec:**
  - `estimate_tokens(text: str) -> int`: return `max(1, len(text) // 4)` (≈4
    chars/token heuristic; no external deps).
  - Extend `truncate_context(messages, max_chars=None, max_tokens=None)`: if
    `max_tokens` given, budget by `estimate_tokens` summed over messages; keep
    leading system message + most recent messages that fit. Keep `max_chars`
    behavior for backward compat (one of the two must be provided).
  - In `memory.save_turn`, keep current char caps but ALSO cap by
    `memory_max_tokens` (new config).
- **Config:** `"memory_max_tokens": 1500` (comment: rough token budget for memory).
- **i18n:** none.
- **Edge cases:** empty messages; a single message larger than budget → keep it
  (never drop the only/most-recent user content — see WU rule that current prompt
  is sacred, already implemented in `handle_standard_query`).
- **Tests:** `estimate_tokens` monotonic; `truncate_context(max_tokens=...)` keeps
  system + drops oldest first.
- **Acceptance:** ☐ memory respects token budget ☐ existing memory tests pass.
- **Verify:** `python -c "from polly.utils import estimate_tokens; print(estimate_tokens('a'*400))"` → ~100.

---

# PHASE 1 — NOW: polish & quick wins

## WU-03 — Retry with backoff on transient upstream errors
- **Goal:** transient 429/502/503/timeout/conn errors retry briefly before
  surfacing the clear error.
- **Files:** `polly/api.py` (wrap the POST in `chat_completion`; add helper).
- **Spec:**
  - Add `_post_with_retry(self, url, json, headers, stream)` used by
    `chat_completion`. Retry on: `requests.exceptions.Timeout`,
    `ConnectionError`, and HTTP status in `{429, 502, 503}`.
  - Max attempts `retry_max_attempts` (default 3). Delay =
    `retry_base_delay * (2 ** (attempt-1))` seconds with ±25% jitter. If a
    `Retry-After` header is present on 429, honor it (cap at 30s).
  - Do NOT retry on 400/401/402/404/500 (these are deterministic — surface
    immediately via existing error mapping).
  - Streaming requests: retry only the initial connection, not mid-stream.
  - On final failure, raise the SAME clear errors the code raises today.
- **Config:** `"retry_max_attempts": 3`, `"retry_base_delay": 1.0`.
- **i18n:** optional `msg.retrying` ("Retrying… ({n})" / "Tentando novamente… ({n})")
  printed via `print_info` between attempts (only when not streaming/quiet).
- **Edge cases:** attempts=1 → no retry; respect `--no-markdown`/quiet (don't spam).
- **Tests:** monkeypatch `requests.post` to fail twice then succeed → returns
  result; to always 400 → raises immediately (no retry). Use a fake response obj.
- **Acceptance:** ☐ transient errors recover ☐ deterministic errors don't retry.
- **Verify:** point at an unreachable host → see bounded retries then the connection error.

## WU-04 — `--history`, `--history-clear`, `--purge`
- **Goal:** let users read/clear the conversation log and wipe all local state.
- **Files:** `polly/memory.py` (add helpers); `polly/cli.py` (flags);
  `polly/__main__.py` (`handle_config_commands` handlers); `help_formatter.py`.
- **Spec:**
  - `memory.read_history(limit_lines=200) -> str`: tail the `history.log`.
  - `memory.clear_history() -> bool`: truncate `history.log`.
  - `memory.purge_all() -> dict`: delete `sessions/`, `history.log`, `cache/`,
    `models_cache.json`, `health_cache.json`; return counts. Do NOT delete
    `config.yaml`.
  - Flags: `--history` (print tail), `--history-clear`, `--purge` (with a typed
    confirmation: prompt "Type 'yes' to wipe all local Polly state:").
- **Config:** none.
- **i18n (EN/PT):**
  - `msg.history_empty` = "No conversation history yet." / "Nenhum histórico de conversa ainda."
  - `msg.history_cleared` = "Conversation history cleared." / "Histórico de conversa limpo."
  - `msg.purge_confirm` = "Type 'yes' to wipe ALL local Polly state (memory, history, caches): " / "Digite 'yes' para apagar TODO o estado local do Polly (memória, histórico, caches): "
  - `msg.purge_done` = "Wiped local state: {summary}" / "Estado local apagado: {summary}"
  - `msg.purge_aborted` = "Purge aborted." / "Limpeza cancelada."
  - `info.history`, `info.history_clear`, `info.purge` (help descriptions, both langs).
- **CLI:** add the three flags to the "information" group; add to `needs_prompt` and
  `is_config_command` sets.
- **Tests:** `purge_all` on a temp config dir removes the right files, keeps config.
- **Acceptance:** ☐ `--history` shows recent log ☐ `--purge` confirms then wipes.
- **Verify:** `polly --history`, then `polly --purge`.

## WU-05 — `polly --update`
- **Goal:** one command to self-update from GitHub.
- **Files:** `polly/__main__.py` (handler); `cli.py`; `help_formatter.py`;
  `polly/utils.py` (optional `detect_install_method`).
- **Spec:**
  - `--update` runs `pipx install git+https://github.com/rafabez/polly.git --force`
    via `subprocess.run`, streaming output. If `pipx` not found on PATH, print the
    manual `pip install ...` command instead (don't fail hard).
  - Print success/fail clearly. Never auto-run on startup.
- **i18n (EN/PT):** `msg.updating` ("Updating Polly from GitHub…" / "Atualizando o
  Polly pelo GitHub…"), `msg.update_done`, `msg.update_failed`,
  `msg.update_no_pipx` ("pipx not found. Run: {cmd}" / "pipx não encontrado. Rode: {cmd}"),
  `info.update`.
- **CLI:** flag in "configuration" group; add to needs_prompt/is_config_command.
- **Edge cases:** offline → show the subprocess error verbatim; Windows pipx shim.
- **Tests:** monkeypatch subprocess to assert the command line is correct; pipx-missing path.
- **Acceptance:** ☐ updates when pipx present ☐ helpful message when absent.
- **Verify:** `polly --update`.

## WU-06 — Response cache (opt-in)
- **Goal:** avoid re-hitting the API for identical requests; save latency/cost.
- **Files:** new `polly/cache.py`; `polly/__main__.py` (`handle_standard_query`);
  `cli.py` (`--no-cache`, `--cache`).
- **Spec:**
  - Cache dir `~/.config/polly/cache/`. Key = sha256 of
    `model | mode | temperature | system_prompt | user_prompt`. Value = JSON
    `{ "ts": <epoch>, "response": <str> }`.
  - `cache.get(key, ttl) -> str|None`, `cache.put(key, response)`,
    `cache.clear()` (called by `purge_all` in WU-04).
  - Use cache ONLY when `response_cache_enabled` is true OR `--cache` passed, AND
    NOT when `--no-cache`. To preserve answer variety, by default only cache when
    effective `temperature <= cache_max_temperature` (default 0.0). Memory/history
    still record cache hits (mark `cached: true` in history line).
  - On hit: print response normally; skip the API call and the spinner.
- **Config:** `"response_cache_enabled": false`, `"cache_ttl_minutes": 60`,
  `"cache_max_temperature": 0.0`.
- **i18n:** none required (silent), optional dim note `msg.cache_hit`.
- **Edge cases:** never cache streaming responses unless fully buffered; never cache
  errors; corrupt cache file → ignore and refetch.
- **Tests:** put/get round-trip; TTL expiry; key stability for same inputs; different
  temperature → different key.
- **Acceptance:** ☐ identical temp-0 query served from cache ☐ `--no-cache` bypasses.
- **Verify:** `polly --cache -m mistral --temperature 0 "ping"` twice; second is instant.

## WU-07 — Health/latency badges in model lists
- **Goal:** show live health + latency next to models in `-lm` and the interactive picker.
- **Files:** `polly/config.py` (expose health stats); `polly/__main__.py`
  (`list_models` block); `polly/utils.py` (`interactive_model_selection`).
- **Spec:**
  - Add `fetch_health_stats() -> dict[str, dict]` in `config.py`: reuse the
    Tinybird call from `_fetch_healthy_model_names`, but return
    `{ name: {"success_pct": int, "p50_ms": int} }` (text models only). Cache in
    `health_cache.json` alongside the healthy set (extend the cached structure;
    keep backward-compatible read).
  - In `-lm` and the picker, append a dim badge per model:
    `  ✓ 98%  ~520ms` (green if ≥80%, yellow 50–79%). If no data for a model,
    no badge.
- **Config:** none new.
- **i18n:** none (badges are symbols/numbers).
- **Edge cases:** Tinybird unreachable → no badges, list still renders (current
  fallback). Windows console unicode → reuse existing `console` (Rich) which handles it.
- **Tests:** `fetch_health_stats` parses a sample Tinybird payload into the map.
- **Acceptance:** ☐ `-lm` shows badges when data present ☐ degrades cleanly offline.
- **Verify:** `polly -lm`.

## WU-08 — Fix streaming hang when output is redirected/piped
- **Goal:** `polly "..." | something` (non-TTY stdout) must not hang.
- **Files:** `polly/__main__.py` (`handle_standard_query`); `polly/utils.py`
  (spinner already TTY-aware? verify).
- **Spec:**
  - When `not sys.stdout.isatty()`: force non-streaming for standard queries
    (set effective `stream=False` regardless of config) so output flushes and the
    process exits cleanly. Streaming stays on for interactive TTY use.
  - Ensure `show_spinner` is a no-op when stdout isn't a TTY.
- **Config:** none.
- **Edge cases:** `-i` interactive always TTY; `--json`/`-o` already buffer.
- **Tests:** simulate non-tty (monkeypatch `sys.stdout.isatty` → False) and assert
  the code path picks non-stream.
- **Acceptance:** ☐ `polly "hi" | cat` returns promptly and exits.
- **Verify (PowerShell):** `polly "say hi" | Out-String`.

---

# PHASE 2 — NEXT: system-interaction core

> Order is mandatory: **WU-09 (system context) → WU-10 (safety) → WU-11 (execute)**.
> Execution MUST NOT ship before the safety layer.

## WU-09 — System context provider
- **Goal:** make advice specific to the user's actual machine.
- **Files:** new `polly/system_context.py`; `polly/prompts.py` (inject summary);
  `polly/cli.py` (`--rescan`, `--show-system`); `__main__.py`.
- **Spec:**
  - `collect() -> dict`: OS + version (`platform`), distro (parse
    `/etc/os-release` on Linux), shell (env `SHELL`/`ComSpec`/parent), package
    manager (detect `apt|dnf|pacman|brew|winget|choco|scoop` by which/availability),
    arch, and versions of `python, git, node, docker` (run `--version`, 2s timeout
    each, skip if absent). Best-effort; missing items omitted.
  - Cache to `~/.config/polly/system.json` with `system_context_ttl_hours`
    (default 24). `--rescan` forces refresh. `--show-system` prints it.
  - `summary(ctx) -> str`: compact one-paragraph string (≤300 chars), e.g.
    "OS: Ubuntu 24.04 (x86_64); shell: bash; pkg: apt; docker 27.1, python 3.12".
  - In `prompts.get_prompt`, when `system_context_enabled`, prepend the summary to
    the SYSTEM prompt for modes `default`, `command`, `command_explain`, `debug`,
    `refactor` (NOT translate/motivational). Keep it short to protect context.
- **Config:** `"system_context_enabled": true`, `"system_context_ttl_hours": 24`.
- **i18n (EN/PT):** `info.rescan`, `info.show_system`, `msg.system_rescanned`,
  header `msg.system_header`.
- **Edge cases:** locked-down machines where subprocess is blocked → catch, omit.
  Privacy: this data is LOCAL only and only summarized into prompts; document it.
- **Tests:** `summary` formats a fake ctx; `collect` doesn't crash with missing tools
  (monkeypatch `shutil.which` → None).
- **Acceptance:** ☐ `polly --show-system` prints real machine facts ☐ "install
  docker" advice uses the right package manager.
- **Verify:** `polly --show-system`; `polly -c "install docker"`.

## WU-10 — Safety layer (prereq for any execution)
- **Goal:** classify commands and gate dangerous ones; full audit.
- **Files:** new `polly/safety.py`; `polly/config.py` (allow/deny config);
  `polly/memory.py` (audit via `append_history` or a dedicated audit line).
- **Spec:**
  - `classify(cmd: str) -> Risk` where `Risk` ∈ {`SAFE`, `CAUTION`, `DESTRUCTIVE`,
    `BLOCKED`}. Rules (regex, case-insensitive, cross-platform):
    - BLOCKED (never run): fork bombs, `mkfs`, `dd if=.* of=/dev/`, writing to raw
      disks, `:(){ :|:& };:`, `chmod -R 777 /`, mass `rm -rf /` or `%SystemRoot%`,
      curl|wget piped to shell (`curl ... | sh`).
    - DESTRUCTIVE (typed confirm): `rm -rf`, `rmdir /s`, `Remove-Item -Recurse`,
      `format`, package removal (`apt remove`, `pacman -R`), `git reset --hard`,
      `git clean -fd`, `> file` truncation, `kill -9`, service stop/disable,
      `sudo`/`Administrator` elevation.
    - CAUTION (single y/n): network installs, writing files, moving/renaming,
      `chmod/chown`, editing system config.
    - SAFE: read-only (`ls`, `cat`, `pwd`, `git status`, `ps`, `df`…).
  - Config-driven overrides: `safety_allowlist` (regex → force SAFE),
    `safety_denylist` (regex → force BLOCKED). Denylist wins over everything.
  - `confirm(cmd, risk) -> bool`: SAFE → True without prompt only if
    `execute_autoconfirm_safe` (default false) else single confirm; CAUTION →
    y/N; DESTRUCTIVE → require typing the literal word shown
    (`type "RUN" to proceed`); BLOCKED → never, print why.
  - `audit(cmd, risk, exit_code, output_summary)`: append a structured line to
    `history.log` (prefix `[EXEC]`).
- **Config:** `"safety_allowlist": []`, `"safety_denylist": []`,
  `"execute_autoconfirm_safe": false`.
- **i18n (EN/PT):** `safety.blocked` ("Blocked for safety: {reason}" / "Bloqueado por
  segurança: {reason}"), `safety.confirm_caution`, `safety.confirm_destructive`
  ("This is destructive. Type {word} to proceed: " / "Isso é destrutivo. Digite
  {word} para continuar: "), `safety.aborted`.
- **Tests (critical, high coverage):** table of sample commands → expected Risk;
  denylist forces BLOCKED; allowlist forces SAFE; destructive requires exact word.
- **Acceptance:** ☐ `rm -rf /` → BLOCKED ☐ `apt remove x` → DESTRUCTIVE ☐ `ls` →
  SAFE ☐ denylist beats allowlist.
- **Verify:** unit tests; no execution yet.

## WU-11 — Execute-with-confirmation mode
- **Goal:** Polly can RUN the command it generated, gated by WU-10.
- **Files:** new `polly/executor.py`; `polly/__main__.py` (wire into command mode);
  `cli.py` (`-X/--execute`, `--dry-run`).
- **Spec:**
  - After `-c` generates a command (or with `polly -X "task"`), show it, run
    `safety.classify` + `safety.confirm`. On approval, execute via
    `subprocess.run` in the user's shell (PowerShell on Windows, `$SHELL` else),
    streaming stdout/stderr live; capture exit code; `safety.audit(...)`.
  - `--dry-run`: show the command + classification, never execute. Default for any
    DESTRUCTIVE unless explicitly confirmed.
  - Multi-command output (`-c3`): let the user pick which to run (numbered).
  - NEVER auto-run without consent. Respect `--no-memory` for not logging? No —
    always audit executions (security), independent of memory.
- **Config:** `"execute_enabled": true` (master switch; if false, `-X` errors with
  a clear message).
- **i18n (EN/PT):** `exec.running` ("Running: {cmd}" / "Executando: {cmd}"),
  `exec.exit_code`, `exec.dry_run`, `exec.disabled`, `info.execute`, `info.dry_run`.
- **Edge cases:** command needs a TTY (e.g. `top`) — run attached; long-running →
  stream; Ctrl-C → terminate child, audit as aborted; Windows quoting.
- **Tests:** monkeypatch subprocess; assert SAFE runs after confirm, BLOCKED never
  runs, `--dry-run` never runs. (Don't execute real destructive commands in tests.)
- **Acceptance:** ☐ `polly -X "list files in this folder"` runs `ls`/`dir` after
  confirm ☐ destructive requires typed word ☐ `--dry-run` shows only.
- **Verify:** `polly -X "show current directory"`.

## WU-12 — Config-file assistant
- **Goal:** edit a config file in plain language, safely, with diff + backup.
- **Files:** new `polly/config_edit.py`; `cli.py` (`--edit FILE`); `__main__.py`.
- **Spec:**
  - `polly --edit <file> "instruction"`: read file, send (file + instruction) to
    the model asking for the FULL new file content, compute a unified diff
    (`difflib.unified_diff`), show it colorized, ask confirm (CAUTION via WU-10),
    on yes write a timestamped backup `<file>.YYYYMMDD-HHMMSS.bak` then overwrite.
  - Refuse files above a size cap (`edit_max_kb`, default 256) — print why.
  - `--revert <file>`: restore the most recent `.bak`.
- **Config:** `"edit_max_kb": 256`.
- **i18n (EN/PT):** `edit.no_changes`, `edit.backup_saved` ("Backup: {path}" /
  "Backup: {path}"), `edit.written`, `edit.too_big`, `edit.reverted`, `info.edit`,
  `info.revert`.
- **Edge cases:** model returns markdown fences → strip; file unchanged → say so;
  permission denied → clear error.
- **Tests:** diff/backup/write round-trip in tmp_path; revert restores; size cap.
- **Acceptance:** ☐ edits a sample `.conf` with visible diff + backup ☐ revert works.
- **Verify:** `polly --edit ~/.bashrc "add alias ll='ls -la'"` (review diff, confirm).

## WU-13 — OS skills (curated recipes)
- **Goal:** reliable, idiomatic recipes for common admin tasks per platform.
- **Files:** new `polly/skills/__init__.py` (registry) + one module per skill
  (e.g. `packages.py`, `services.py`, `firewall.py`); `cli.py` (`--skill NAME` and
  `--list-skills`); `__main__.py`.
- **Spec:**
  - A skill = `{ name, description, platforms, run(args, ctx) -> list[str] }`
    returning candidate commands (NOT executed directly — they flow through WU-11's
    safety+confirm). Skills use `system_context` (WU-09) to pick the right tool.
  - Registry auto-discovers modules in `polly/skills/`. `--list-skills` prints them
    (bilingual descriptions). Natural-language routing optional later.
  - Ship 3 starter skills: `packages` (install/remove/search), `services`
    (start/stop/status/enable), `disk` (usage/largest dirs — read-only).
- **Config:** none.
- **i18n:** skill descriptions via `get_text("skill.<name>")` (EN/PT).
- **Tests:** registry discovers skills; `packages.run("install docker", ctx)` yields
  `apt install docker...` on an apt ctx, `brew install...` on brew ctx.
- **Acceptance:** ☐ `--list-skills` lists 3 ☐ a skill yields platform-correct commands.
- **Verify:** `polly --list-skills`; `polly --skill packages "install htop"`.

---

# PHASE 3 — LATER: agentic companion (design-level specs)

> These are larger; specs here define interfaces + acceptance, leaving room for
> iteration. Build only after Phase 2 is stable. Pollinations function-calling is
> confirmed working (OpenAI-format `tool_calls`, multi-turn), so the agent loop can
> use native tool calls.

## WU-14 — Generalized OpenAI-compatible client (enables local models)
- **Goal:** let Polly talk to ANY OpenAI-compatible endpoint (Pollinations default,
  Ollama, OpenAI, etc.) — foundation for local/offline.
- **Files:** `polly/api.py` (generalize), `polly/config.py` (provider block).
- **Spec:** config `provider: { type: "pollinations"|"openai", base_url, api_key,
  model_map }`. Default keeps current backend behavior. When `openai`, POST to
  `{base_url}/chat/completions` with `Authorization: Bearer`. Reuse error mapping
  + WU-03 retry.
- **Acceptance:** ☐ `provider.type=openai`, `base_url=http://localhost:11434/v1`
  (Ollama) answers a prompt.
- **Verify:** run against a local Ollama if available.

## WU-15 — Tool-using agent loop (multi-step tasks)
- **Goal:** for goals needing several steps, plan → call tools → observe → continue,
  with confirmation + audit at each action.
- **Files:** new `polly/agent.py`; reuse `executor`, `safety`, `system_context`.
- **Spec:** define a small tool set as OpenAI function schemas
  (`run_command`, `read_file`, `write_file`, `web_search` via a search-capable
  model). Loop: send messages+tools → if `tool_calls`, run each through
  safety+confirm, append `role:tool` results, repeat (cap `agent_max_steps`,
  default 8). Show the plan first; allow abort anytime.
- **Config:** `"agent_max_steps": 8`, `"agent_enabled": false` (opt-in).
- **Acceptance:** ☐ "create a folder `demo` and a `hello.txt` inside" completes via
  tool calls with per-action confirm.
- **Verify:** scripted demo task.

## WU-16 — Stateful rollback
- **Goal:** undo what a task changed.
- **Spec:** before each mutating action, record an inverse where possible (file
  backups, "installed X" → offer `remove X`). `polly --undo-last` reverses the last
  task's recorded changes. Store transaction log in `~/.config/polly/transactions/`.
- **Acceptance:** ☐ a task that created files can be fully undone.

## WU-17 — Vision/screen context (opt-in, local-first)
- **Goal:** let Polly reason about a screenshot or terminal error image.
- **Spec:** `polly --see` captures the screen (platform tool) or takes an image
  path, sends to a vision model (`qwen-vision`/`qwen-vision-pro`, confirmed
  text+image input). Opt-in; never auto-capture.
- **Acceptance:** ☐ `polly --see error.png "what's wrong?"` describes the image.

## WU-18 — Plugin/skill SDK
- **Goal:** third-party skills without forking core.
- **Spec:** document the skill interface (WU-13), load skills from
  `~/.config/polly/skills/` and from installed packages exposing a
  `polly.skills` entry point. Provide a template + docs.
- **Acceptance:** ☐ a skill dropped in the user skills dir is discovered and listed.

---

# CROSS-CUTTING TRACKS (parallelizable)

## CT-A — Backend hardening (`polly-backend` repo)
- Multi-key failover: `POLLINATIONS_API_KEYS` (comma list); rotate on 401/402/429.
- Per-IP quota beyond the existing slowapi limit; return clear 429 JSON.
- Health-aware routing: if Tinybird shows a model failing, return a warning field
  or suggest an alternative in the error envelope.
- Alerting: log + notify on sustained 401/402 (key/credit problems) — these caused
  real outages (Gemini/Claude 402, enter-vs-gen 401).
- Deploy docs: systemd unit, `/etc/polly-backend/config.env`, dashboard, in the
  backend README.

## CT-B — Quality & DX
- mypy on `polly/` core; type hints on public functions.
- `CONTRIBUTING.md`: the EN/PT i18n contract, the honest-UX rule, the safety rules.
- Versioned releases + `CHANGELOG.md`.

## CT-C — Privacy & trust
- `docs/PRIVACY.md`: what leaves the machine (prompts → Pollinations via proxy) vs
  what stays local (memory, history, caches, system.json).
- `history_enabled` config to opt out of persistent logging.
- `--purge` (WU-04) as the one-command wipe.

---

# Suggested execution order (single track)

WU-01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09 → 10 → 11 → 12 → 13 →
(CT-A/B/C anytime) → 14 → 15 → 16 → 17 → 18.

Each WU is independently shippable. Stop after any WU with a green test suite.
