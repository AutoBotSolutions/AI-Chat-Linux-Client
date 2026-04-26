"""
Tests for ChatWindow.send_message() input validation.

These tests verify that all the guards introduced in the critical-bug-fix
phase handle edge cases without crashing and produce the correct user-visible
error messages.
"""

import pytest
from unittest.mock import patch, MagicMock
from types import SimpleNamespace


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _set_combo_item(window, data, label="test-model"):
    """Set the model combo to a single item carrying the given data."""
    window.model_combo.clear()
    from PyQt6.QtCore import Qt
    window.model_combo.addItem(label, userData=data)
    window.model_combo.setCurrentIndex(0)


def _chat_text(window):
    return window.chat_display.toPlainText()


# ---------------------------------------------------------------------------
# Empty input
# ---------------------------------------------------------------------------

class TestEmptyInput:
    def test_empty_string_does_nothing(self, chat_window):
        """Blank message must return silently without adding any chat entry."""
        chat_window.input_box.setText("   ")
        before = _chat_text(chat_window)

        with patch.object(chat_window, "start_generation") as mock_gen:
            chat_window.send_message()

        mock_gen.assert_not_called()
        assert _chat_text(chat_window) == before  # display unchanged

    def test_empty_input_box_does_nothing(self, chat_window):
        chat_window.input_box.clear()
        with patch.object(chat_window, "start_generation") as mock_gen:
            chat_window.send_message()
        mock_gen.assert_not_called()


# ---------------------------------------------------------------------------
# No model available
# ---------------------------------------------------------------------------

class TestNoModelAvailable:
    def test_empty_combo_shows_error_message(self, chat_window):
        """Combo with zero items must add an Error message, not crash."""
        chat_window.model_combo.clear()
        chat_window.input_box.setText("hello")

        with patch.object(chat_window, "start_generation") as mock_gen:
            chat_window.send_message()

        mock_gen.assert_not_called()
        assert "Error" in _chat_text(chat_window)

    def test_none_item_data_shows_error_message(self, chat_window):
        """Item with None data (not a tuple) must show an error."""
        _set_combo_item(chat_window, None)
        chat_window.input_box.setText("hello")

        with patch.object(chat_window, "start_generation") as mock_gen:
            chat_window.send_message()

        mock_gen.assert_not_called()
        # Either "No AI providers" or "Invalid model selection" error expected
        assert "Error" in _chat_text(chat_window)


# ---------------------------------------------------------------------------
# Malformed item data
# ---------------------------------------------------------------------------

class TestMalformedItemData:
    def test_non_tuple_data_shows_error(self, chat_window):
        """A plain string in itemData must be caught and shown as an error."""
        _set_combo_item(chat_window, "not-a-tuple")
        chat_window.input_box.setText("test")

        with patch.object(chat_window, "start_generation") as mock_gen:
            chat_window.send_message()

        mock_gen.assert_not_called()
        assert "Error" in _chat_text(chat_window)

    def test_single_element_tuple_shows_error(self, chat_window):
        _set_combo_item(chat_window, ("ollama",))
        chat_window.input_box.setText("test")

        with patch.object(chat_window, "start_generation") as mock_gen:
            chat_window.send_message()

        mock_gen.assert_not_called()
        assert "Error" in _chat_text(chat_window)

    def test_empty_provider_string_shows_error(self, chat_window):
        _set_combo_item(chat_window, ("", "llama3"))
        chat_window.input_box.setText("test")

        with patch.object(chat_window, "start_generation") as mock_gen:
            chat_window.send_message()

        mock_gen.assert_not_called()
        assert "Error" in _chat_text(chat_window)

    def test_empty_model_string_shows_error(self, chat_window):
        _set_combo_item(chat_window, ("ollama", ""))
        chat_window.input_box.setText("test")

        with patch.object(chat_window, "start_generation") as mock_gen:
            chat_window.send_message()

        mock_gen.assert_not_called()
        assert "Error" in _chat_text(chat_window)


# ---------------------------------------------------------------------------
# Successful dispatch
# ---------------------------------------------------------------------------

class TestSuccessfulDispatch:
    def test_valid_data_adds_user_message(self, chat_window):
        """Valid tuple combo item must add 'You: …' to the chat display."""
        chat_window.router.providers["ollama"] = SimpleNamespace(is_available=True)
        _set_combo_item(chat_window, ("ollama", "llama3"))
        chat_window.input_box.setText("ping")

        with patch.object(chat_window, "start_generation"):
            chat_window.send_message()

        assert "You" in _chat_text(chat_window)
        assert "ping" in _chat_text(chat_window)

    def test_valid_data_clears_input_box(self, chat_window):
        """Input box must be empty after a successful send."""
        chat_window.router.providers["ollama"] = SimpleNamespace(is_available=True)
        _set_combo_item(chat_window, ("ollama", "llama3"))
        chat_window.input_box.setText("ping")

        with patch.object(chat_window, "start_generation"):
            chat_window.send_message()

        assert chat_window.input_box.text() == ""

    def test_valid_data_appends_to_current_messages(self, chat_window):
        """User message must be recorded in current_messages for context."""
        chat_window.router.providers["ollama"] = SimpleNamespace(is_available=True)
        _set_combo_item(chat_window, ("ollama", "llama3"))
        chat_window.input_box.setText("context test")

        with patch.object(chat_window, "start_generation"):
            chat_window.send_message()

        roles = [m["role"] for m in chat_window.current_messages]
        assert "user" in roles

    def test_valid_data_calls_start_generation_with_full_model(self, chat_window):
        """start_generation must receive 'provider/model' composite string."""
        chat_window.router.providers["ollama"] = SimpleNamespace(is_available=True)
        _set_combo_item(chat_window, ("ollama", "llama3.2"))
        chat_window.input_box.setText("test")

        with patch.object(chat_window, "start_generation") as mock_gen:
            chat_window.send_message()

        mock_gen.assert_called_once_with("ollama/llama3.2")
