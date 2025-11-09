"""
Basic tests for Polly
"""

import pytest
from polly.config import get_config, AVAILABLE_MODELS
from polly.prompts import get_prompt, get_available_modes


def test_config_loads():
    """Test that configuration loads successfully"""
    config = get_config()
    assert config is not None
    assert config.get("default_model") in AVAILABLE_MODELS


def test_available_models():
    """Test that all expected models are available"""
    expected_models = ["gemini", "openai", "deepseek", "mistral", "qwen-coder"]
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
    """Test translate mode with language parameter"""
    system, user = get_prompt("translate", "Hello", language="Spanish")
    assert "Spanish" in user
    assert "Hello" in user


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
