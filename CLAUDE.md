# Polly — project notes

CLI AI assistant for Linux/macOS/Windows terminals, powered by Pollinations.ai. No
API keys required (historically). Python 3.8+. Entry point: `polly = polly.__main__:main`.

## Layout

- `polly/__main__.py`, `polly/cli.py` — argparse CLI, modes (chat, command, debug, translate, refactor, etc.)
- `polly/api.py` — `PollinationsAPI` client: `simple_query` (GET) and `chat_completion` (OpenAI-compatible POST)
- `polly/config.py` — YAML config at `~/.config/polly/config.yaml`, plus profiles, OS/locale detection, model catalog
- `polly/prompts.py` — system prompts per mode
- `polly/i18n.py` — EN/PT-BR strings
- `polly/pdf_handler.py` — read/write PDFs
- `polly/help_formatter.py`, `polly/utils.py` — UX helpers
- `web/` — landing page; `DOCS/` — quickstart/install docs; `examples/`, `tests/`

## Network topology (as the code is written today)

Three URLs are involved (`polly/config.py`):

- `BACKEND_URL = "https://api.interzonesec.com"` — author-operated proxy, **used by default** (`use_backend: True`)
- `API_BASE_URL = "https://text.pollinations.ai"` — legacy Pollinations direct API (fallback when `use_backend=False` or `--direct`)
- `NEW_API_BASE_URL = "https://enter.pollinations.ai/api/generate/v1"` — only consulted in `get_available_models`

Request flow in `chat_completion` (`polly/api.py:129-134`):

- `use_backend` → `POST {BACKEND_URL}/api/chat/completions`
- else → `POST {API_BASE_URL}/openai`

## Why it stopped working (June 2026)

Pollinations migrated their API. Three independent breakages stack up:

1. **Proxy backend is down.** `https://api.interzonesec.com/api/chat/completions` returns
   HTTP 308 with body `{"detail":"Pollinations API error: "}` and no `Location` header.
   `requests` doesn't follow, `raise_for_status()` doesn't trigger on 3xx,
   `response.json()` parses fine, then `data["choices"]` raises `KeyError` →
   the `except (KeyError, json.JSONDecodeError)` branch at `polly/api.py:194` prints
   "⚠️  Invalid API response." — exactly the error the user reports.

2. **Legacy direct API is mostly empty.** `https://text.pollinations.ai/models` now
   lists a **single** model (`openai-fast`, GPT-OSS 20B on OVH, aliased as
   `openai`/`gpt-oss`). POSTing the default model (`openai-large`) to
   `text.pollinations.ai/openai` returns:

   ```json
   {"error":"Model not found: openai-large",
    "deprecation_notice":"NOTE: The Pollinations legacy text API is being deprecated
     for authenticated users. ... Anonymous requests to text.pollinations.ai are NOT affected."}
   ```

   So even `--direct` is broken for any model other than `openai-fast`/`openai`/`gpt-oss`.

3. **The new gateway requires an API key.** The current real API is at
   `https://gen.pollinations.ai/v1` (OpenAI-compatible, `/v1/models` and
   `/v1/chat/completions`). `/v1/models` is public (returns ~100 models including
   `openai-large`, `gpt-5.5`, `claude-opus-4.8`, etc.), but `/v1/chat/completions`
   returns 401 without a Bearer token. Keys come from
   [enter.pollinations.ai](https://enter.pollinations.ai) and look like `sk_...`.

   `NEW_API_BASE_URL` in `config.py` is wrong too — the actual base is
   `https://gen.pollinations.ai/v1`, not `enter.pollinations.ai/api/generate/v1`.

## Defaults today

- `default_model: openai-large` — no longer reachable on any endpoint the client uses
- `use_backend: True` → broken backend → "Invalid API response" on every call
- `referrer: interzonesec.com`
- Hardcoded model catalog in `AVAILABLE_MODELS` lists `mistral`, `deepseek`, `qwen-coder`,
  `openai`, `gemini`, `gemini-search` — slugs that mostly only resolve on the
  authenticated `gen.pollinations.ai` gateway now.

## To get a user un-stuck quickly

Either of these works as a one-off (no code changes):

- Edit `~/.config/polly/config.yaml`: set `default_model: openai-fast` and
  `use_backend: false`. This routes to the still-public legacy endpoint, which
  only serves that one model.
- Or run `polly --direct --model openai-fast "..."` to verify connectivity.

A real fix requires repointing the client at `https://gen.pollinations.ai/v1` and
either adding API-key support (Authorization: Bearer sk_…) or restoring the proxy
backend.
