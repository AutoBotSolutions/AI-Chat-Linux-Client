"""
Tests for provider-first model selection flow.

This file validates the new UI behavior where provider and model are selected
in separate dropdowns and model options are scoped to the selected provider.
"""

from types import SimpleNamespace
from unittest.mock import patch


class TestProviderDropdownPopulation:
    def test_update_model_list_populates_provider_combo(self, chat_window):
        chat_window.router.providers = {
            "ollama": SimpleNamespace(is_available=True),
            "groq": SimpleNamespace(is_available=False),
        }

        models = {
            "ollama": ["llama3.2:1b", "mistral:7b"],
            "groq": ["llama-3.1-8b-instant"],
        }
        chat_window.update_model_list_ui(models)

        # All system providers should be listed, not only initialized ones.
        assert chat_window.provider_combo.count() >= 5
        assert chat_window.provider_combo.findData("ollama") >= 0
        assert chat_window.provider_combo.findData("groq") >= 0
        assert chat_window.provider_combo.findData("huggingface") >= 0
        assert chat_window.provider_combo.findData("openrouter") >= 0
        assert chat_window.provider_combo.findData("openai") >= 0

    def test_provider_switch_reloads_model_combo(self, chat_window):
        chat_window.settings.providers["groq"].enabled = True
        chat_window.router.providers = {
            "ollama": SimpleNamespace(is_available=True),
            "groq": SimpleNamespace(is_available=True),
        }

        models = {
            "ollama": ["llama3.2:1b", "phi3.5:3.8b"],
            "groq": ["llama-3.1-8b-instant"],
        }
        chat_window.update_model_list_ui(models)

        groq_index = chat_window.provider_combo.findData("groq")
        chat_window.provider_combo.setCurrentIndex(groq_index)

        assert chat_window.model_combo.count() == 1
        assert chat_window.model_combo.currentData() == "llama-3.1-8b-instant"

    def test_filter_enabled_hides_disabled_providers(self, chat_window):
        chat_window.settings.providers["groq"].enabled = False
        chat_window.settings.providers["openai"].enabled = True
        chat_window.router.providers = {
            "ollama": SimpleNamespace(is_available=True),
            "openai": SimpleNamespace(is_available=False),
            "groq": SimpleNamespace(is_available=False),
        }
        models = {
            "ollama": ["llama3.2:1b"],
            "openai": ["gpt-4o"],
            "groq": ["llama-3.1-8b-instant"],
        }
        chat_window.update_model_list_ui(models)

        chat_window.set_provider_filter("enabled")
        assert chat_window.provider_combo.findData("ollama") >= 0
        assert chat_window.provider_combo.findData("openai") >= 0
        assert chat_window.provider_combo.findData("groq") == -1

    def test_filter_available_shows_online_only(self, chat_window):
        chat_window.settings.providers["groq"].enabled = True
        chat_window.settings.providers["openai"].enabled = True
        chat_window.router.providers = {
            "ollama": SimpleNamespace(is_available=True),
            "openai": SimpleNamespace(is_available=False),
            "groq": SimpleNamespace(is_available=True),
        }
        models = {
            "ollama": ["llama3.2:1b"],
            "openai": ["gpt-4o"],
            "groq": ["llama-3.1-8b-instant"],
        }
        chat_window.update_model_list_ui(models)

        chat_window.set_provider_filter("available")
        assert chat_window.provider_combo.findData("ollama") >= 0
        assert chat_window.provider_combo.findData("groq") >= 0
        assert chat_window.provider_combo.findData("openai") == -1


class TestProviderModelSendFlow:
    def test_send_uses_selected_provider_and_model(self, chat_window):
        # Mimic real UI state: provider map exists before provider selection changes.
        chat_window.settings.providers["groq"].enabled = True
        chat_window._models_by_provider = {"groq": ["llama-3.1-8b-instant"]}
        chat_window.provider_combo.clear()
        chat_window.provider_combo.addItem("groq (online)", "groq")
        chat_window.router.providers["groq"] = SimpleNamespace(is_available=True)
        chat_window.provider_combo.setCurrentIndex(0)
        chat_window._populate_models_for_provider("groq")

        chat_window.input_box.setText("ping")

        with patch.object(chat_window, "start_generation") as mock_generation:
            chat_window.send_message()

        mock_generation.assert_called_once_with("groq/llama-3.1-8b-instant")

    def test_provider_without_models_disables_send(self, chat_window):
        chat_window.settings.providers["openai"].enabled = True
        chat_window._models_by_provider = {"openai": []}
        chat_window._populate_models_for_provider("openai")

        assert chat_window.send_button.isEnabled() is False
        assert chat_window.model_combo.currentData() is None

    def test_disabled_provider_disables_send_and_shows_hint(self, chat_window):
        chat_window.settings.providers["openrouter"].enabled = False
        chat_window._models_by_provider = {"openrouter": ["openai/gpt-4o"]}
        chat_window._populate_models_for_provider("openrouter")

        assert chat_window.send_button.isEnabled() is False
        assert "disabled" in chat_window.model_combo.currentText().lower()

    def test_unavailable_provider_disables_send_and_shows_hint(self, chat_window):
        chat_window.settings.providers["openai"].enabled = True
        chat_window.router.providers["openai"] = SimpleNamespace(is_available=False)
        chat_window._models_by_provider = {"openai": ["gpt-4o", "gpt-4o-mini"]}

        chat_window._populate_models_for_provider("openai")

        assert chat_window.send_button.isEnabled() is False
        assert "unavailable" in chat_window.model_combo.currentText().lower()
