"""
Tests for ChatWindow timestamp-toggle behaviour.

The canonical _display_messages list must be the single source of truth:
adding messages, then toggling show_timestamps on or off, must produce a
consistent display that matches the current preference.
"""

import pytest
from unittest.mock import patch


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _chat_lines(window):
    """Return a list of non-empty lines from the chat display."""
    return [l for l in window.chat_display.toPlainText().splitlines() if l.strip()]


def _add_two_messages(window):
    """Seed the window with one user and one AI message."""
    window.add_message("You", "Hello")
    window.add_message("AI", "World")


# ---------------------------------------------------------------------------
# Initial rendering respects settings
# ---------------------------------------------------------------------------

class TestInitialRender:
    def test_timestamps_on_by_default(self, chat_window):
        """UIConfig defaults show_timestamps=True, so messages include brackets."""
        chat_window.settings.ui.show_timestamps = True
        _add_two_messages(chat_window)
        lines = _chat_lines(chat_window)
        assert all("[" in l for l in lines), f"Expected all lines to contain '[', got: {lines}"

    def test_timestamps_off_no_brackets(self, chat_window):
        """With show_timestamps=False messages must NOT contain '[HH:MM:SS]' brackets."""
        chat_window.settings.ui.show_timestamps = False
        _add_two_messages(chat_window)
        # Re-render with current (False) preference
        chat_window._render_display_messages()
        lines = _chat_lines(chat_window)
        assert all("[" not in l for l in lines), f"Expected NO brackets, got: {lines}"


# ---------------------------------------------------------------------------
# _render_display_messages is idempotent
# ---------------------------------------------------------------------------

class TestRenderIdempotent:
    def test_double_render_same_output(self, chat_window):
        chat_window.settings.ui.show_timestamps = True
        _add_two_messages(chat_window)
        first = chat_window.chat_display.toPlainText()
        chat_window._render_display_messages()
        second = chat_window.chat_display.toPlainText()
        assert first == second


# ---------------------------------------------------------------------------
# toggle_timestamps flips display consistently
# ---------------------------------------------------------------------------

class TestToggleTimestamps:
    def _set_timestamp_action(self, window, checked: bool):
        """Sync the menu action's checked state before calling toggle."""
        window.timestamp_action.setChecked(checked)
        window.settings.ui.show_timestamps = checked

    def test_toggle_on_adds_brackets(self, chat_window):
        """Turning timestamps ON must add '[…]' brackets to existing messages."""
        chat_window.settings.ui.show_timestamps = False
        _add_two_messages(chat_window)
        chat_window._render_display_messages()

        self._set_timestamp_action(chat_window, True)
        chat_window.toggle_timestamps()

        lines = _chat_lines(chat_window)
        assert all("[" in l for l in lines), f"Expected brackets after toggle ON: {lines}"

    def test_toggle_off_removes_brackets(self, chat_window):
        """Turning timestamps OFF must remove '[…]' brackets from existing messages."""
        chat_window.settings.ui.show_timestamps = True
        _add_two_messages(chat_window)

        self._set_timestamp_action(chat_window, False)
        chat_window.toggle_timestamps()

        lines = _chat_lines(chat_window)
        assert all("[" not in l for l in lines), f"Expected no brackets after toggle OFF: {lines}"

    def test_toggle_preserves_message_count(self, chat_window):
        """Toggling must not add or remove lines — only reformat them."""
        chat_window.settings.ui.show_timestamps = True
        _add_two_messages(chat_window)
        before_count = len(_chat_lines(chat_window))

        self._set_timestamp_action(chat_window, False)
        chat_window.toggle_timestamps()
        after_count = len(_chat_lines(chat_window))

        assert before_count == after_count

    def test_toggle_preserves_message_content(self, chat_window):
        """Message text must survive a toggle — only the timestamp wrapper changes."""
        chat_window.settings.ui.show_timestamps = True
        _add_two_messages(chat_window)

        self._set_timestamp_action(chat_window, False)
        chat_window.toggle_timestamps()

        text = chat_window.chat_display.toPlainText()
        assert "Hello" in text
        assert "World" in text


# ---------------------------------------------------------------------------
# Toggle blocked during active streaming
# ---------------------------------------------------------------------------

class TestToggleBlockedDuringStream:
    def test_toggle_refused_while_streaming(self, chat_window):
        """toggle_timestamps must refuse to change the display during active streaming."""
        chat_window.settings.ui.show_timestamps = True
        _add_two_messages(chat_window)
        snapshot_before = chat_window.chat_display.toPlainText()

        # Simulate active streaming state
        chat_window._streaming_in_progress = True
        # Try to turn off timestamps
        chat_window.timestamp_action.setChecked(False)

        with patch("ui.main_window.QMessageBox.information") as mock_info:
            chat_window.toggle_timestamps()

        # The info dialog must have been shown
        mock_info.assert_called_once()
        # The display must be unchanged
        assert chat_window.chat_display.toPlainText() == snapshot_before
        # The setting must not have been permanently changed — action reverted
        assert chat_window.timestamp_action.isChecked() is True


# ---------------------------------------------------------------------------
# _display_messages canonical store integrity
# ---------------------------------------------------------------------------

class TestCanonicalStore:
    def test_add_message_records_in_display_messages(self, chat_window):
        chat_window.add_message("You", "test text")
        assert len(chat_window._display_messages) == 1
        entry = chat_window._display_messages[0]
        assert entry["sender"] == "You"
        assert entry["message"] == "test text"
        assert "timestamp" in entry

    def test_clear_chat_resets_display_messages(self, chat_window):
        _add_two_messages(chat_window)
        assert len(chat_window._display_messages) == 2
        chat_window.clear_chat()
        assert chat_window._display_messages == []

    def test_render_matches_display_messages_length(self, chat_window):
        _add_two_messages(chat_window)
        chat_window._render_display_messages()
        rendered_lines = _chat_lines(chat_window)
        assert len(rendered_lines) == len(chat_window._display_messages)
