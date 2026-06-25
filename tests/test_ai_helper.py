import os
import sys

# Ensure project root is in the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ai_helper


def test_providers_exist():
    assert "🦙 Ollama (Local)" in ai_helper.PROVIDERS
    assert "🤖 OpenAI" in ai_helper.PROVIDERS
    assert "⚡ Groq" in ai_helper.PROVIDERS
    assert "💎 Gemini" in ai_helper.PROVIDERS


def test_ollama_has_llava():
    assert "llava" in ai_helper.MODEL_OPTIONS["ollama"]
    assert "llava:7b" in ai_helper.MODEL_OPTIONS["ollama"]


def test_model_options_structure():
    assert isinstance(ai_helper.MODEL_OPTIONS, dict)
    for provider in ["ollama", "openai", "groq", "gemini"]:
        assert provider in ai_helper.MODEL_OPTIONS
        assert isinstance(ai_helper.MODEL_OPTIONS[provider], list)
