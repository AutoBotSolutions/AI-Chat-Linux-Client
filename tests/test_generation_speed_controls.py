"""Tests for generation speed controls and worker parameter pass-through."""

from unittest.mock import patch


def _seed_valid_selection(window, provider="ollama", model="qwen2.5:3b"):
    window.provider_combo.clear()
    window.model_combo.clear()
    window.provider_combo.addItem(f"{provider} (online)", provider)
    window.provider_combo.setCurrentIndex(0)
    window.model_combo.addItem(model, model)
    window.model_combo.setCurrentIndex(0)


def test_start_generation_ollama_defaults_max_tokens_when_unlimited(chat_window):
    chat_window.settings.chat.max_tokens = None
    chat_window.settings.chat.temperature = 0.8
    chat_window.current_messages = [{"role": "user", "content": "hello"}]

    with patch("ui.main_window.ChatWorker") as MockWorker:
        instance = MockWorker.return_value
        instance.start.return_value = None
        chat_window.start_generation("ollama/qwen2.5:3b")

        assert MockWorker.called
        _, kwargs = MockWorker.call_args
        assert kwargs["max_tokens"] == 64
        assert kwargs["temperature"] == 0.8


def test_start_generation_respects_user_max_tokens(chat_window):
    chat_window.settings.chat.max_tokens = 64
    chat_window.settings.chat.temperature = 0.3
    chat_window.current_messages = [{"role": "user", "content": "hello"}]

    with patch("ui.main_window.ChatWorker") as MockWorker:
        instance = MockWorker.return_value
        instance.start.return_value = None
        chat_window.start_generation("ollama/mistral:7b")

        _, kwargs = MockWorker.call_args
        assert kwargs["max_tokens"] == 64
        assert kwargs["temperature"] == 0.3


def test_start_generation_clamps_user_max_tokens_to_speed_profile(chat_window):
    chat_window.settings.chat.max_tokens = 300
    chat_window.settings.chat.temperature = 0.7
    chat_window.current_messages = [{"role": "user", "content": "hello"}]

    with patch("ui.main_window.ChatWorker") as MockWorker:
        instance = MockWorker.return_value
        instance.start.return_value = None
        chat_window.start_generation("ollama/qwen2.5:3b")

        _, kwargs = MockWorker.call_args
        assert kwargs["max_tokens"] == 64


def test_fast_mode_substitutes_heavy_qwen_to_llama_when_needed(chat_window):
    chat_window.prefer_fast_local_models = True
    chat_window._models_by_provider = {"ollama": ["llama3.2:1b", "qwen2.5:3b"]}

    selected = "qwen2.5:3b"
    effective = chat_window._select_speed_optimized_model("ollama", selected)

    assert effective == "llama3.2:1b"


def test_fast_mode_does_not_change_non_ollama_models(chat_window):
    chat_window.prefer_fast_local_models = True
    chat_window._models_by_provider = {"groq": ["llama-3.1-8b-instant"]}

    selected = "llama-3.1-8b-instant"
    effective = chat_window._select_speed_optimized_model("groq", selected)

    assert effective == selected
