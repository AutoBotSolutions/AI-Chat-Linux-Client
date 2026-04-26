"""
Tests for ChatWindow.export_chat() — covers all three output formats plus
the empty-state guard and the auto-extension logic.
"""

import json
import os
import tempfile
import pytest
from unittest.mock import patch


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _seed_messages(window):
    """Populate _display_messages with two canonical entries."""
    window._display_messages = [
        {"sender": "You", "message": "Hello world", "timestamp": "10:00:00"},
        {"sender": "AI",  "message": "Hi there!",   "timestamp": "10:00:01"},
    ]


# ---------------------------------------------------------------------------
# Empty-state guard
# ---------------------------------------------------------------------------

class TestExportGuard:
    def test_empty_messages_shows_info_not_crash(self, chat_window, qtbot):
        """export_chat() with no messages must show an informational dialog and return."""
        chat_window._display_messages = []

        # Intercept QMessageBox.information so no real dialog blocks the test.
        with patch("ui.main_window.QMessageBox.information") as mock_info:
            chat_window.export_chat()

        mock_info.assert_called_once()
        args = mock_info.call_args[0]
        assert "no messages" in args[2].lower()


# ---------------------------------------------------------------------------
# Plain-text export
# ---------------------------------------------------------------------------

class TestExportTxt:
    def _run_export(self, chat_window, suffix=".txt", selected_filter="Text Files (*.txt)"):
        _seed_messages(chat_window)
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
            tmp_path = f.name

        try:
            with (
                patch("ui.main_window.QFileDialog.getSaveFileName",
                      return_value=(tmp_path, selected_filter)),
                patch("ui.main_window.QMessageBox.information"),
            ):
                chat_window.export_chat()
            return open(tmp_path, encoding="utf-8").read()
        finally:
            os.unlink(tmp_path)

    def test_txt_contains_sender_and_message(self, chat_window):
        content = self._run_export(chat_window)
        assert "You: Hello world" in content
        assert "AI: Hi there!" in content

    def test_txt_contains_timestamps_when_present(self, chat_window):
        content = self._run_export(chat_window)
        assert "[10:00:00]" in content
        assert "[10:00:01]" in content

    def test_txt_ends_with_newline(self, chat_window):
        content = self._run_export(chat_window)
        assert content.endswith("\n")


# ---------------------------------------------------------------------------
# Markdown export
# ---------------------------------------------------------------------------

class TestExportMarkdown:
    def _run_export(self, chat_window):
        _seed_messages(chat_window)
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
            tmp_path = f.name

        try:
            with (
                patch("ui.main_window.QFileDialog.getSaveFileName",
                      return_value=(tmp_path, "Markdown Files (*.md)")),
                patch("ui.main_window.QMessageBox.information"),
            ):
                chat_window.export_chat()
            return open(tmp_path, encoding="utf-8").read()
        finally:
            os.unlink(tmp_path)

    def test_md_has_h1_header(self, chat_window):
        content = self._run_export(chat_window)
        assert content.startswith("# Chat Export")

    def test_md_has_bold_sender_names(self, chat_window):
        content = self._run_export(chat_window)
        assert "**You**" in content
        assert "**AI**" in content

    def test_md_has_message_bodies(self, chat_window):
        content = self._run_export(chat_window)
        assert "Hello world" in content
        assert "Hi there!" in content


# ---------------------------------------------------------------------------
# JSON export
# ---------------------------------------------------------------------------

class TestExportJson:
    def _run_export(self, chat_window):
        _seed_messages(chat_window)
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            tmp_path = f.name

        try:
            with (
                patch("ui.main_window.QFileDialog.getSaveFileName",
                      return_value=(tmp_path, "JSON Files (*.json)")),
                patch("ui.main_window.QMessageBox.information"),
            ):
                chat_window.export_chat()
            with open(tmp_path, encoding="utf-8") as f:
                return json.load(f)
        finally:
            os.unlink(tmp_path)

    def test_json_top_level_keys(self, chat_window):
        data = self._run_export(chat_window)
        assert "exported_at" in data
        assert "message_count" in data
        assert "messages" in data

    def test_json_message_count_matches(self, chat_window):
        data = self._run_export(chat_window)
        assert data["message_count"] == 2
        assert len(data["messages"]) == 2

    def test_json_message_fields(self, chat_window):
        data = self._run_export(chat_window)
        first = data["messages"][0]
        assert first["sender"] == "You"
        assert first["message"] == "Hello world"
        assert first["timestamp"] == "10:00:00"


# ---------------------------------------------------------------------------
# Auto-extension logic
# ---------------------------------------------------------------------------

class TestAutoExtension:
    """When user provides a bare filename (no dot), the correct extension is appended."""

    def _run_export(self, chat_window, bare_path, selected_filter):
        _seed_messages(chat_window)
        # tmp dir for output files
        with tempfile.TemporaryDirectory() as tmp_dir:
            target = os.path.join(tmp_dir, bare_path)
            with (
                patch("ui.main_window.QFileDialog.getSaveFileName",
                      return_value=(target, selected_filter)),
                patch("ui.main_window.QMessageBox.information"),
            ):
                chat_window.export_chat()

            # After auto-extension the file should exist with a suffix.
            files = os.listdir(tmp_dir)
            assert len(files) == 1, f"Expected 1 file, got: {files}"
            return files[0]

    def test_bare_name_gets_txt_extension(self, chat_window):
        name = self._run_export(chat_window, "myexport", "Text Files (*.txt)")
        assert name.endswith(".txt")

    def test_bare_name_gets_md_extension(self, chat_window):
        name = self._run_export(chat_window, "myexport", "Markdown Files (*.md)")
        assert name.endswith(".md")

    def test_bare_name_gets_json_extension(self, chat_window):
        name = self._run_export(chat_window, "myexport", "JSON Files (*.json)")
        assert name.endswith(".json")


# ---------------------------------------------------------------------------
# Cancelled dialog
# ---------------------------------------------------------------------------

class TestExportCancelled:
    def test_cancelled_dialog_no_file_written(self, chat_window, tmp_path):
        _seed_messages(chat_window)
        with patch("ui.main_window.QFileDialog.getSaveFileName", return_value=("", "")):
            # Should return silently without writing anything or raising.
            chat_window.export_chat()
        assert list(tmp_path.iterdir()) == []
