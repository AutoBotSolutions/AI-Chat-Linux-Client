"""Tests for coding-focused ChatWindow UI features.

Covers:
- fenced code extraction
- snippet registration/display
- snippet copy action
- snippet run action (with terminal mock)
"""

from unittest.mock import patch, MagicMock
import os


class TestCodeBlockExtraction:
    def test_extracts_language_and_code(self, chat_window):
        text = (
            "Here is code:\n"
            "```python\n"
            "print('hello')\n"
            "```\n"
        )

        blocks = chat_window._extract_fenced_code_blocks(text)
        assert len(blocks) == 1
        assert blocks[0]["language"] == "python"
        assert blocks[0]["code"] == "print('hello')"

    def test_extracts_multiple_blocks(self, chat_window):
        text = (
            "```bash\n"
            "echo first\n"
            "```\n"
            "text\n"
            "```json\n"
            "{\"a\": 1}\n"
            "```\n"
        )

        blocks = chat_window._extract_fenced_code_blocks(text)
        assert len(blocks) == 2
        assert blocks[0]["language"] == "bash"
        assert blocks[1]["language"] == "json"

    def test_extracts_windows_newline_fence(self, chat_window):
        text = "```python\r\nprint('win')\r\n```"
        blocks = chat_window._extract_fenced_code_blocks(text)
        assert len(blocks) == 1
        assert blocks[0]["code"] == "print('win')"


class TestSnippetRegistration:
    def test_register_populates_internal_store_and_list(self, chat_window):
        response = "```python\nprint(123)\n```"
        chat_window.register_code_blocks_from_ai_response(response)

        assert len(chat_window._code_snippets) == 1
        assert chat_window.code_blocks_list.count() == 1
        assert chat_window.code_preview.toPlainText() == "print(123)"

    def test_register_ignores_non_code_response(self, chat_window):
        before = len(chat_window._code_snippets)
        chat_window.register_code_blocks_from_ai_response("No fenced code here")
        assert len(chat_window._code_snippets) == before

    def test_code_preview_is_editable(self, chat_window):
        assert chat_window.code_preview.isReadOnly() is False


class TestSnippetActions:
    def test_copy_selected_snippet_to_clipboard(self, chat_window):
        chat_window.register_code_blocks_from_ai_response("```python\nprint('x')\n```")
        chat_window.code_blocks_list.setCurrentRow(0)
        chat_window.code_preview.setPlainText("print('edited')")

        with patch("ui.main_window.QApplication.clipboard") as mock_clipboard:
            clipboard = mock_clipboard.return_value
            chat_window.copy_selected_code_snippet()
            clipboard.setText.assert_called_once_with("print('edited')")

    def test_run_selected_snippet_uses_active_terminal(self, chat_window):
        chat_window.register_code_blocks_from_ai_response("```bash\necho hi\n```")
        chat_window.code_blocks_list.setCurrentRow(0)
        chat_window.code_preview.setPlainText("echo edited")

        fake_terminal = MagicMock()

        with patch.object(chat_window, "get_active_terminal", return_value=fake_terminal):
            chat_window.run_selected_code_snippet()

        fake_terminal.run_text.assert_called_once_with("echo edited")
        assert chat_window.workspace_tabs.currentWidget() is chat_window.terminal_workspace_tab

    def test_run_selected_snippet_without_selection_is_safe(self, chat_window):
        # no snippet selected
        chat_window.run_selected_code_snippet()
        assert "Select a snippet" in chat_window.status_bar.currentMessage()

    def test_save_selected_snippet_writes_file(self, chat_window, tmp_path):
        chat_window.register_code_blocks_from_ai_response("```python\nprint('saved')\n```")
        chat_window.code_blocks_list.setCurrentRow(0)
        chat_window.code_preview.setPlainText("print('edited save')")

        target = tmp_path / "snippet_output"
        with patch("ui.main_window.QFileDialog.getSaveFileName", return_value=(str(target), "All Files (*.*)")):
            chat_window.save_selected_code_snippet()

        saved_path = str(target) + ".py"
        assert os.path.exists(saved_path)
        with open(saved_path, encoding="utf-8") as f:
            content = f.read()
        assert "print('edited save')" in content


class TestSnippetActionState:
    def test_buttons_disabled_without_selection(self, chat_window):
        assert chat_window.copy_code_button.isEnabled() is False
        assert chat_window.save_code_button.isEnabled() is False
        assert chat_window.run_code_button.isEnabled() is False

    def test_buttons_enabled_with_valid_selection(self, chat_window):
        chat_window.register_code_blocks_from_ai_response("```bash\necho ok\n```")
        chat_window.code_blocks_list.setCurrentRow(0)
        assert chat_window.copy_code_button.isEnabled() is True
        assert chat_window.save_code_button.isEnabled() is True
        assert chat_window.run_code_button.isEnabled() is True

    def test_buttons_remain_enabled_when_selected_snippet_text_cleared(self, chat_window):
        chat_window.register_code_blocks_from_ai_response("```bash\necho ok\n```")
        chat_window.code_blocks_list.setCurrentRow(0)
        chat_window.code_preview.setPlainText("   ")
        assert chat_window.copy_code_button.isEnabled() is True
        assert chat_window.save_code_button.isEnabled() is True
        assert chat_window.run_code_button.isEnabled() is True


class TestLanguageExtensionMapping:
    def test_cpp_maps_to_cpp_extension(self, chat_window):
        assert chat_window._language_to_extension("c++") == "cpp"

    def test_rust_maps_to_rs_extension(self, chat_window):
        assert chat_window._language_to_extension("rust") == "rs"

    def test_unknown_language_defaults_to_txt(self, chat_window):
        assert chat_window._language_to_extension("brainfuck") == "txt"
