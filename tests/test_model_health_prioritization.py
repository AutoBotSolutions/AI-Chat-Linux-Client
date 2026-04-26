"""Tests for per-model health prioritization and labeling in model dropdown."""

from types import SimpleNamespace


def _model_labels(window):
    return [window.model_combo.itemText(i) for i in range(window.model_combo.count())]


def test_verified_models_are_listed_first(chat_window):
    chat_window.settings.providers["ollama"].enabled = True
    chat_window.router.providers["ollama"] = SimpleNamespace(is_available=True)
    chat_window._models_by_provider = {"ollama": ["mistral:7b", "llama3.2:1b", "qwen2.5:3b"]}

    chat_window._model_health["ollama/qwen2.5:3b"] = True
    chat_window._model_health["ollama/mistral:7b"] = False

    chat_window._populate_models_for_provider("ollama")
    labels = _model_labels(chat_window)

    assert labels[0].startswith("qwen2.5:3b")
    assert "[verified]" in labels[0]


def test_failed_models_get_retry_label(chat_window):
    chat_window.settings.providers["ollama"].enabled = True
    chat_window.router.providers["ollama"] = SimpleNamespace(is_available=True)
    chat_window._models_by_provider = {"ollama": ["mistral:7b"]}
    chat_window._model_health["ollama/mistral:7b"] = False

    chat_window._populate_models_for_provider("ollama")

    assert "[retry]" in chat_window.model_combo.itemText(0)


def test_successful_response_marks_model_verified(chat_window):
    chat_window._current_generation_model = "ollama/phi3.5:3.8b"
    chat_window._streaming_in_progress = False

    chat_window.on_response_complete("hello")

    assert chat_window._model_health["ollama/phi3.5:3.8b"] is True
