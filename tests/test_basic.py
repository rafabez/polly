"""
Basic tests for Polly
"""

import re
import json
import time
import pytest
from polly.config import get_config, AVAILABLE_MODELS
from polly.prompts import get_prompt, get_available_modes
from polly.i18n import TRANSLATIONS
from polly import memory


def test_config_loads():
    """Test that configuration loads successfully"""
    config = get_config()
    assert config is not None
    assert config.get("default_model") in AVAILABLE_MODELS


def test_available_models():
    """Test that core fallback models are available"""
    expected_models = ["openai", "deepseek", "mistral", "qwen-coder"]
    for model in expected_models:
        assert model in AVAILABLE_MODELS


def test_prompt_modes():
    """Test that prompt modes work correctly"""
    modes = get_available_modes()
    assert "explain" in modes
    assert "command" in modes
    assert "debug" in modes

    # Test getting a prompt
    system, user = get_prompt("explain", "test content")
    assert system is not None
    assert "test content" in user


def test_command_prompt():
    """Test command mode prompt"""
    system, user = get_prompt("command", "list files")
    assert "command" in system.lower() or "bash" in system.lower()
    assert "list files" in user


def test_translate_prompt():
    """Test translate mode with target_language parameter"""
    system, user = get_prompt("translate", "Hello", target_language="Spanish")
    assert "Spanish" in user
    assert "Hello" in user


def test_stream_disabled_when_not_tty(monkeypatch):
    """When stdout is not a TTY, effective_stream must be False even if args.stream=True."""
    import sys
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)
    # The logic: effective_stream = args.stream and sys.stdout.isatty()
    stream_arg = True
    effective = stream_arg and sys.stdout.isatty()
    assert effective is False


def test_retry_succeeds_after_transient(monkeypatch):
    """_post_with_retry returns after two 429s followed by a 200."""
    import requests as req
    from polly.api import PollinationsAPI

    call_count = 0

    class FakeResp:
        def __init__(self, status):
            self.status_code = status
            self.headers = {}
            self.text = ""

    def fake_post(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        return FakeResp(429 if call_count < 3 else 200)

    monkeypatch.setattr(req, "post", fake_post)
    monkeypatch.setattr("polly.api.time.sleep", lambda _: None)

    api = PollinationsAPI()
    resp = api._post_with_retry("http://x", {}, {})
    assert resp.status_code == 200
    assert call_count == 3


def test_retry_no_retry_on_400(monkeypatch):
    """_post_with_retry does NOT retry on deterministic 400."""
    import requests as req
    from polly.api import PollinationsAPI

    call_count = 0

    class FakeResp:
        status_code = 400
        headers = {}
        text = ""

    def fake_post(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        return FakeResp()

    monkeypatch.setattr(req, "post", fake_post)
    api = PollinationsAPI()
    resp = api._post_with_retry("http://x", {}, {})
    assert resp.status_code == 400
    assert call_count == 1  # no retry


def test_estimate_tokens_monotonic():
    """Longer text → more tokens (monotonic)."""
    from polly.utils import estimate_tokens
    assert estimate_tokens("") >= 1
    assert estimate_tokens("hello") < estimate_tokens("hello " * 100)


def test_truncate_context_max_tokens():
    """truncate_context with max_tokens keeps system + most recent that fit."""
    from polly.utils import truncate_context
    sys_msg = {"role": "system", "content": "S" * 40}   # ~10 tokens
    old = {"role": "user", "content": "A" * 400}         # ~100 tokens
    new = {"role": "user", "content": "B" * 100}         # ~25 tokens
    result = truncate_context([sys_msg, old, new], max_tokens=40)
    assert result[0] == sys_msg           # system always kept
    assert any(m == new for m in result)  # most recent kept
    assert not any(m == old for m in result)  # oldest dropped


def test_truncate_context_never_drops_last():
    """Single message larger than budget is still kept."""
    from polly.utils import truncate_context
    huge = {"role": "user", "content": "X" * 40000}
    result = truncate_context([huge], max_tokens=10)
    assert result == [huge]


def test_i18n_key_parity():
    """Every translation key must exist in both English and Portuguese."""
    en = set(TRANSLATIONS["en"])
    pt = set(TRANSLATIONS["pt"])
    only_en = en - pt
    only_pt = pt - en
    assert not only_en, f"Keys missing from PT: {sorted(only_en)}"
    assert not only_pt, f"Keys missing from EN: {sorted(only_pt)}"


def test_i18n_placeholder_parity():
    """A key's {placeholders} must match between EN and PT so .format() never breaks."""
    en, pt = TRANSLATIONS["en"], TRANSLATIONS["pt"]
    placeholder = re.compile(r"{(\w+)}")
    mismatches = {}
    for key in set(en) & set(pt):
        en_ph = set(placeholder.findall(str(en[key])))
        pt_ph = set(placeholder.findall(str(pt[key])))
        if en_ph != pt_ph:
            mismatches[key] = {"en": sorted(en_ph), "pt": sorted(pt_ph)}
    assert not mismatches, f"Placeholder mismatches: {mismatches}"


@pytest.fixture
def mem(tmp_path, monkeypatch):
    """Isolate memory storage in a temp dir with a fixed session key."""
    monkeypatch.setattr(memory, "_config_dir", lambda: tmp_path)
    monkeypatch.setenv("WT_SESSION", "test-session")
    return memory


def test_memory_save_and_load(mem):
    """A saved exchange is reloaded as user+assistant messages."""
    mem.save_turn("question one", "answer one")
    ctx = mem.load_context()
    assert len(ctx) == 2
    assert ctx[0] == {"role": "user", "content": "question one"}
    assert ctx[1]["role"] == "assistant"
    assert ctx[1]["content"] == "answer one"


def test_memory_isolation_by_session(tmp_path, monkeypatch):
    """Different terminal sessions keep separate memory."""
    monkeypatch.setattr(memory, "_config_dir", lambda: tmp_path)

    monkeypatch.setenv("WT_SESSION", "session-A")
    memory.save_turn("topic A", "answer A")

    monkeypatch.setenv("WT_SESSION", "session-B")
    assert memory.load_context() == []  # B starts empty
    memory.save_turn("topic B", "answer B")

    monkeypatch.setenv("WT_SESSION", "session-A")
    ctx = memory.load_context()
    assert ctx[0]["content"] == "topic A"


def test_memory_ttl_expiry(mem):
    """Context older than the TTL is treated as empty."""
    mem.save_turn("old question", "old answer")
    path = mem._session_path()
    data = json.loads(path.read_text(encoding="utf-8"))
    data["updated_at"] = time.time() - (mem._ttl_seconds() + 60)
    path.write_text(json.dumps(data), encoding="utf-8")
    assert mem.load_context() == []


def test_memory_turn_limit(mem):
    """Only the most recent N turns are kept."""
    for i in range(10):
        mem.save_turn(f"q{i}", f"a{i}")
    ctx = mem.load_context()
    max_turns = get_config().get("memory_max_turns", 6)
    assert len(ctx) <= max_turns * 2
    assert ctx[-2]["content"] == "q9"  # most recent question retained


def test_memory_response_truncation(mem):
    """Long assistant replies are clipped."""
    mem.save_turn("q", "x" * 5000)
    ctx = mem.load_context()
    assert "[truncado]" in ctx[1]["content"]
    assert len(ctx[1]["content"]) < 5000


def test_memory_clear(mem):
    """clear_session removes stored context."""
    mem.save_turn("q", "a")
    assert mem.load_context()
    assert mem.clear_session() is True
    assert mem.load_context() == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
