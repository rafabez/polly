# Polly — Roadmap

> A vision and improvement plan for Polly. This is a living document: priorities
> shift, items get reordered, and not everything here will ship. The goal is to
> capture direction and trade-offs, not to promise dates.

---

## 1. Vision

Polly started as a multi-mode AI CLI on top of Pollinations. The intended
direction is to grow it into a **terminal companion for operating your computer**
— a tool that helps you *configure the OS, run and understand system tasks, and
interact with your machine* in plain language. Code generation stays useful, but
it is not the headline (Pollinations isn't the strongest at codegen); **system
interaction and honest, safe automation are**.

Three guiding principles, drawn from how the project already behaves:

1. **Honest UX over magic.** No silent fallbacks that mislead (we removed the
   "everything secretly becomes GPT-4" behavior). Errors should be clear and
   instructive.
2. **Reflect reality.** The model list shows what's *actually live* right now, not
   a static catalog. The same honesty should extend to system state.
3. **Bilingual, cross-platform, low-friction.** Every user-facing string in EN +
   PT; works on Linux, macOS, Windows; no API keys or accounts required of the
   end user.

---

## 2. Current state (honest assessment)

**Strengths**
- Clean multi-mode CLI: explain, command, debug, refactor, translate, interactive,
  motivational, default.
- Dynamic, health-filtered model list (gen.pollinations.ai + Tinybird monitor).
- Conversational memory across invocations, per-terminal, with logs.
- Cross-platform with OS-aware prompts; profiles; temperature presets; PDF I/O.
- Backend proxy with telemetry + dashboard.
- EN/PT i18n throughout.

**Gaps / technical debt**
- Test coverage is thin (config, prompts, memory only) — no API-client, CLI, or
  end-to-end tests.
- Context budgeting counts characters, not tokens; no model-specific limits.
- i18n and help tables are hand-synchronized — easy to drift; no check that every
  key exists in both languages.
- Backend uses a single shared API key and one hardcoded upstream; no per-user
  quota, no key rotation, no graceful multi-key failover.
- No response caching; repeated identical prompts re-hit the API.
- No retry/backoff strategy for transient upstream errors (429/502).
- The CLI cannot *act* on the system yet — it only suggests (`-c` prints a command
  but never runs it).

---

## 3. Horizons

### 🟢 NOW — Polish & quick wins (the existing tool, made better)

- **i18n integrity check.** A tiny test that asserts every key exists in both `en`
  and `pt` (and that `.format` placeholders match). Prevents drift.
- **Token-aware context budgeting.** Replace the char-count heuristic in
  `truncate_context` with a rough token estimate and use each model's real
  `context_length` (already available from gen API metadata).
- **Retry with backoff.** Wrap upstream calls (CLI `api.py` and backend) with a
  short exponential backoff on 429/502/timeout before surfacing the clear error.
- **Response cache (opt-in).** Cache identical (model, prompt, temperature=0)
  results for N minutes under `~/.config/polly/cache/`. Add `--no-cache`.
- **`polly --history`** to print/tail the conversation log, and `--history-clear`.
- **Self-update helper.** `polly --update` runs the `pipx install ... --force`
  one-liner so users don't have to remember it.
- **Model picker UX.** Show latency/health badges from the Tinybird data in `-lm`
  and the interactive picker (data is already fetched).
- **Tests + CI.** GitHub Actions running pytest on push; expand coverage to the
  API client (mocked) and CLI arg parsing.

### 🟡 NEXT — System interaction core (the vision starts here)

This is the pivot from "answers about your system" to "help with your system."

- **System context provider.** Detect OS/distro, shell, package manager, key
  versions (python, node, docker…), and inject a compact system summary into
  prompts so advice is specific ("install docker" → `apt` on Ubuntu, `brew` on
  macOS). Cache it; refresh on demand with `--rescan`.
- **Execute-with-confirmation mode.** Evolve `-c` so Polly can *offer to run* the
  command it generated: show it, explain it, ask Y/n, then execute and stream
  output. Never auto-run. `--dry-run` shows what would happen.
- **Safety layer (mandatory before any execution ships).**
  - Classify commands; require explicit confirmation for destructive ones
    (`rm -rf`, `dd`, `mkfs`, `:>`, privilege escalation, package removal…).
  - Configurable allowlist/denylist; a global "never execute" guard by default.
  - Backup-before-edit for config files, with a shown diff and easy revert.
  - Full audit trail in the history log (command, exit code, output summary).
- **Config-file assistant.** Read a config file, propose an edit in plain language,
  show a unified diff, write with a timestamped backup. Targets: dotfiles, nginx,
  systemd units, ssh config, etc.
- **OS skills (curated recipes).** Small, reviewed modules for common admin tasks:
  packages, services (systemd), firewall, users, cron, networking. Each skill
  knows the safe, idiomatic commands per platform.

### 🔴 LATER — Agentic OS companion (the ambitious end-state)

- **Multi-step task planning.** For goals that need several steps ("set up an
  nginx reverse proxy with a Let's Encrypt cert"), Polly drafts a plan, shows it,
  and executes step-by-step with confirmation and rollback points.
- **Stateful operations with rollback.** Snapshot what changed (files touched,
  packages installed, services modified) so a task can be undone.
- **Local/offline model option.** Allow pointing Polly at a local model (Ollama,
  llama.cpp) for privacy-sensitive system tasks, keeping Pollinations as default.
- **Screenshot / screen context (where supported).** Let Polly "see" a terminal
  error or a window to reason about it — opt-in, local-first.
- **Plugin/skill SDK.** A documented interface so the community can ship OS skills
  and integrations without forking core.

---

## 4. Cross-cutting tracks

### Backend & infrastructure
- Move the upstream URL + key fully to env (done) and add **multi-key failover**
  and **per-IP quota** so one user can't exhaust the shared key.
- Health-aware routing: if a model is failing on the monitor, the backend can warn
  or suggest a healthy alternative.
- Structured logs + metrics; alerting on upstream 402/401 (credit/key issues) so
  outages like the Gemini/Claude 402s are caught early.
- Document deploy fully (systemd unit, config.env, dashboard) in the backend repo.

### Quality & DX
- pytest + coverage gate in CI; lint (ruff) + format check.
- Type hints + mypy on core modules.
- A `CONTRIBUTING.md` section on the EN/PT i18n contract and the "honest UX" rule.
- Versioned releases and a changelog.

### Privacy & trust
- Document exactly what leaves the machine (prompts go to Pollinations via the
  proxy) and what stays local (memory, logs, caches).
- `polly --forget` exists; add `polly --purge` to wipe all local state (sessions,
  logs, caches) in one command.
- Make the history log opt-out for users who don't want conversations persisted.

---

## 5. Guardrails for the "system interaction" direction

Because executing commands is inherently risky, these are non-negotiable:

1. **Nothing runs without explicit, per-action user consent** (until/unless a user
   deliberately opts into an "auto" mode for a scoped task).
2. **Destructive actions always require a second, typed confirmation.**
3. **Every executed action is logged** with command, exit code, and output.
4. **Backups before edits**, with a one-command revert.
5. **Dry-run is always available** and is the default for anything irreversible.

---

## 6. How to contribute to the roadmap

Open an issue tagged `roadmap` to propose, reprioritize, or challenge an item.
Small polish items from the NOW list are the best first contributions. Anything
under "system interaction" must come with a safety story.
