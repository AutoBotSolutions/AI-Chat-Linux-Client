"""Tests for explicit empty-response handling in ChatWindow."""

from unittest.mock import patch


def test_empty_response_shows_error_message(chat_window):
    chat_window._current_generation_model = "ollama/mistral:7b"
    chat_window._streaming_in_progress = False

    chat_window.on_response_complete("")

    text = chat_window.chat_display.toPlainText()
    assert "Error" in text
    assert "No response was returned" in text
    assert "ollama/mistral:7b" in text


def test_empty_stream_response_shows_error_message(chat_window):
    chat_window._current_generation_model = "ollama/mistral:7b"
    chat_window._streaming_in_progress = True

    chat_window.on_response_complete("   ")

    text = chat_window.chat_display.toPlainText()
    assert "Error" in text
    assert "No response was returned" in text
