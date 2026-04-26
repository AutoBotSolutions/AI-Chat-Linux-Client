"""Comprehensive workflow tests for the Code Snippets tab.

This module validates the full snippets-tab lifecycle:
- fenced block extraction
- snippet registration/list rendering
- selection and editor synchronization
- action button state transitions
- copy/save/run actions with and without selection
- clear/reset behavior
"""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest


class TestExtraction:
    def test_extract_returns_empty_for_none(self, chat_window):
        assert chat_window._extract_fenced_code_blocks(None) == []

    def test_extract_ignores_non_fenced_text(self, chat_window):
        assert chat_window._extract_fenced_code_blocks("plain text only") == []

    def test_extract_ignores_empty_code_fence(self, chat_window):
        text = "```python\n\n```"
        assert chat_window._extract_fenced_code_blocks(text) == []

    def test_extract_defaults_language_to_text(self, chat_window):
        text = "```\nhello\n```"
        blocks = chat_window._extract_fenced_code_blocks(text)
        assert len(blocks) == 1
        assert blocks[0]["language"] == "text"
        assert blocks[0]["code"] == "hello"

    def test_extract_multiple_blocks_preserves_order(self, chat_window):
        text = """
```python
print(1)
```

```bash
echo hi
```
""".strip()
        blocks = chat_window._extract_fenced_code_blocks(text)
        assert [b["language"] for b in blocks] == ["python", "bash"]
        assert [b["code"] for b in blocks] == ["print(1)", "echo hi"]

    def test_fallback_extracts_unfenced_python_like_block(self, chat_window):
        text = "import os\nvalue = 2\nprint(value)"
        blocks = chat_window._extract_fallback_code_block(text)
        assert len(blocks) == 1
        assert blocks[0]["language"] == "python"

    def test_fallback_ignores_non_code_text(self, chat_window):
        text = "This is a plain paragraph.\nIt has no code structure."
        blocks = chat_window._extract_fallback_code_block(text)
        assert blocks == []


class TestRegistrationAndRendering:
    def test_register_adds_rows_to_store_and_list(self, chat_window):
        chat_window.register_code_blocks_from_ai_response("```python\nprint('x')\n```")
        assert len(chat_window._code_snippets) == 1
        assert chat_window.code_blocks_list.count() == 1
        assert "[python]" in chat_window.code_blocks_list.item(0).text()

    def test_register_with_multiple_blocks_appends_entries(self, chat_window):
        chat_window.register_code_blocks_from_ai_response("```python\nprint(1)\n```")
        chat_window.register_code_blocks_from_ai_response("```bash\necho 2\n```\n```json\n{\"k\": 3}\n```")
        assert len(chat_window._code_snippets) == 3
        assert chat_window.code_blocks_list.count() == 3

    def test_register_auto_selects_latest_and_updates_editor(self, chat_window):
        chat_window.register_code_blocks_from_ai_response("```python\nprint(1)\n```")
        chat_window.register_code_blocks_from_ai_response("```bash\necho hi\n```")
        assert chat_window.code_blocks_list.currentRow() == 1
        assert chat_window.code_preview.toPlainText() == "echo hi"

    def test_register_uses_fallback_for_unfenced_code(self, chat_window):
        chat_window.register_code_blocks_from_ai_response("import sys\nvalue = 3\nprint(value)")
        assert len(chat_window._code_snippets) == 1
        assert chat_window.code_blocks_list.count() == 1


class TestSelectionAndEditSync:
    def test_selecting_row_loads_editor_text(self, chat_window):
        chat_window.register_code_blocks_from_ai_response("```python\nprint('a')\n```")
        chat_window.register_code_blocks_from_ai_response("```python\nprint('b')\n```")

        chat_window.code_blocks_list.setCurrentRow(0)
        assert chat_window.code_preview.toPlainText() == "print('a')"

        chat_window.code_blocks_list.setCurrentRow(1)
        assert chat_window.code_preview.toPlainText() == "print('b')"

    def test_editor_changes_update_selected_snippet_store(self, chat_window):
        chat_window.register_code_blocks_from_ai_response("```python\nprint('old')\n```")
        chat_window.code_blocks_list.setCurrentRow(0)
        chat_window.code_preview.setPlainText("print('new')")
        assert chat_window._code_snippets[0]["code"] == "print('new')"

    def test_get_selected_snippet_text_returns_edited_text(self, chat_window):
        chat_window.register_code_blocks_from_ai_response("```python\nprint('orig')\n```")
        chat_window.code_blocks_list.setCurrentRow(0)
        chat_window.code_preview.setPlainText("print('edited')")
        assert chat_window._get_selected_snippet_text() == "print('edited')"


class TestButtonState:
    def test_buttons_disabled_without_snippets(self, chat_window):
        assert chat_window.copy_code_button.isEnabled() is False
        assert chat_window.save_code_button.isEnabled() is False
        assert chat_window.run_code_button.isEnabled() is False

    def test_buttons_enabled_when_snippet_selected(self, chat_window):
        chat_window.register_code_blocks_from_ai_response("```bash\necho ok\n```")
        chat_window.code_blocks_list.setCurrentRow(0)
        assert chat_window.copy_code_button.isEnabled() is True
        assert chat_window.save_code_button.isEnabled() is True
        assert chat_window.run_code_button.isEnabled() is True

    def test_buttons_disabled_after_clear_chat(self, chat_window):
        chat_window.register_code_blocks_from_ai_response("```bash\necho ok\n```")
        chat_window.clear_chat()
        assert chat_window.copy_code_button.isEnabled() is False
        assert chat_window.save_code_button.isEnabled() is False
        assert chat_window.run_code_button.isEnabled() is False


class TestActions:
    def test_copy_uses_editor_text(self, chat_window):
        chat_window.register_code_blocks_from_ai_response("```python\nprint('x')\n```")
        chat_window.code_blocks_list.setCurrentRow(0)
        chat_window.code_preview.setPlainText("print('clipboard')")

        with patch("ui.main_window.QApplication.clipboard") as mock_clipboard:
            clip = mock_clipboard.return_value
            chat_window.copy_selected_code_snippet()
            clip.setText.assert_called_once_with("print('clipboard')")

    def test_copy_without_selection_shows_status(self, chat_window):
        chat_window.copy_selected_code_snippet()
        assert "Select a snippet" in chat_window.status_bar.currentMessage()

    def test_run_uses_editor_text_and_switches_tab(self, chat_window):
        chat_window.register_code_blocks_from_ai_response("```bash\necho x\n```")
        chat_window.code_blocks_list.setCurrentRow(0)
        chat_window.code_preview.setPlainText("echo from editor")

        fake_terminal = MagicMock()
        with patch.object(chat_window, "get_active_terminal", return_value=fake_terminal):
            chat_window.run_selected_code_snippet()

        fake_terminal.run_text.assert_called_once_with("echo from editor")
        assert chat_window.workspace_tabs.currentWidget() is chat_window.terminal_workspace_tab

    def test_run_without_terminal_shows_status(self, chat_window):
        chat_window.register_code_blocks_from_ai_response("```bash\necho x\n```")
        chat_window.code_blocks_list.setCurrentRow(0)

        with patch.object(chat_window, "get_active_terminal", return_value=None):
            chat_window.run_selected_code_snippet()

        assert "No terminal available" in chat_window.status_bar.currentMessage()

    def test_save_uses_editor_text_and_adds_extension(self, chat_window, tmp_path):
        chat_window.register_code_blocks_from_ai_response("```python\nprint('orig')\n```")
        chat_window.code_blocks_list.setCurrentRow(0)
        chat_window.code_preview.setPlainText("print('saved from editor')")

        target = tmp_path / "snippet_file"
        with patch("ui.main_window.QFileDialog.getSaveFileName", return_value=(str(target), "All Files (*.*)")):
            chat_window.save_selected_code_snippet()

        saved = str(target) + ".py"
        assert os.path.exists(saved)
        with open(saved, encoding="utf-8") as f:
            content = f.read()
        assert "print('saved from editor')" in content

    def test_save_cancel_is_noop(self, chat_window):
        chat_window.register_code_blocks_from_ai_response("```python\nprint('x')\n```")
        chat_window.code_blocks_list.setCurrentRow(0)

        with patch("ui.main_window.QFileDialog.getSaveFileName", return_value=("", "")):
            chat_window.save_selected_code_snippet()

        # Should not crash and should keep snippets intact.
        assert len(chat_window._code_snippets) == 1


@pytest.mark.parametrize(
    "language,expected",
    [
        ("python", "py"),
        ("bash", "sh"),
        ("c++", "cpp"),
        ("rust", "rs"),
        ("unknown-language", "txt"),
    ],
)
def test_extension_mapping_samples(chat_window, language, expected):
    assert chat_window._language_to_extension(language) == expected
