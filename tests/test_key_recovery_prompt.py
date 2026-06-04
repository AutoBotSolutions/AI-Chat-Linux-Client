"""Tests for startup API-key recovery prompt behavior."""

from unittest.mock import patch
from PyQt6.QtWidgets import QMessageBox


def test_prompt_opens_settings_when_user_accepts(chat_window):
    chat_window._key_recovery_prompt_shown = False
    chat_window.key_handler.get_key_store_status = lambda: "invalid-token"

    with patch("ui.main_window.QMessageBox.question", return_value=QMessageBox.StandardButton.Yes), \
         patch.object(chat_window, "show_provider_settings") as mock_show:
        chat_window._prompt_key_store_recovery_if_needed()

    mock_show.assert_called_once_with("Providers")
    assert chat_window._key_recovery_prompt_shown is True


def test_prompt_does_nothing_when_status_ok(chat_window):
    chat_window._key_recovery_prompt_shown = False
    chat_window.key_handler.get_key_store_status = lambda: "ok"

    with (
        patch("ui.main_window.QMessageBox.question") as mock_question,
        patch.object(chat_window, "show_provider_settings") as mock_show,
    ):
        chat_window._prompt_key_store_recovery_if_needed()

    mock_question.assert_not_called()
    mock_show.assert_not_called()
    assert chat_window._key_recovery_prompt_shown is False


def test_prompt_shows_once_only(chat_window):
    chat_window._key_recovery_prompt_shown = False
    chat_window.key_handler.get_key_store_status = lambda: "invalid-token"

    with patch("ui.main_window.QMessageBox.question", return_value=QMessageBox.StandardButton.No) as mock_question:
        chat_window._prompt_key_store_recovery_if_needed()
        chat_window._prompt_key_store_recovery_if_needed()

    assert mock_question.call_count == 1
