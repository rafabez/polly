"""
Basic tests for Polly
"""

import json
import time
import pytest
from polly.config import get_config, AVAILABLE_MODELS
from polly.prompts import get_prompt, get_available_modes
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
