"""Tests for EmbeddedTerminal behavior and shell resolution robustness."""

from unittest.mock import MagicMock, patch

from ui.main_window import EmbeddedTerminal


def test_resolve_shell_handles_env_with_args(monkeypatch):
    monkeypatch.setenv("SHELL", "/bin/bash -l")

    with (
        patch("ui.main_window.os.path.exists", return_value=True),
        patch("ui.main_window.shutil.which", return_value=None),
    ):
        resolved = EmbeddedTerminal._resolve_shell()

    assert resolved == "/bin/bash"


def test_append_output_emits_signal(qtbot):
    terminal = EmbeddedTerminal()
    qtbot.addWidget(terminal)

    with qtbot.waitSignal(terminal.output_received, timeout=1000) as captured:
        terminal._append_output("hello")

    assert captured.args == ["hello"]
    assert "hello" in terminal.output.toPlainText()


def test_chatwindow_close_terminal_keeps_one_tab(chat_window):
    # Ensure there is exactly one terminal tab then close it.
    assert chat_window.terminal_tabs.count() >= 1
    chat_window.terminal_tabs.setCurrentIndex(0)

    current = chat_window.terminal_tabs.currentWidget()
    current.stop = MagicMock()

    chat_window.close_current_terminal()

    # Closing the last tab should auto-create a replacement terminal tab.
    assert chat_window.terminal_tabs.count() == 1
    current.stop.assert_called_once()


def test_embedded_terminal_sets_working_directory_when_valid(tmp_path):
    terminal = EmbeddedTerminal(working_directory=str(tmp_path))
    assert terminal.process.workingDirectory() == str(tmp_path)


def test_terminal_has_editable_command_editor(qtbot):
    terminal = EmbeddedTerminal()
    qtbot.addWidget(terminal)
    assert terminal.command_editor.isReadOnly() is False


def test_run_editor_commands_delegates_to_run_text(qtbot):
    terminal = EmbeddedTerminal()
    qtbot.addWidget(terminal)
    terminal.command_editor.setPlainText("echo one\necho two")

    with patch.object(terminal, "run_text") as mock_run_text:
        terminal.run_editor_commands()

    mock_run_text.assert_called_once_with("echo one\necho two")
