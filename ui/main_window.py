"""
Main window UI for the chat-linux-client application.
"""

import asyncio
import json
import logging
import os
import shlex
import shutil
from typing import Optional, Dict, Any, List
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel, QComboBox,
    QSplitter, QFrame, QScrollArea, QMenuBar, QStatusBar,
    QMessageBox, QProgressBar, QTabWidget, QFileDialog,
    QPlainTextEdit, QListWidget, QListWidgetItem, QApplication,
    QToolBar, QCheckBox, QSpinBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QProcess
from PyQt6.QtGui import QFont, QIcon, QAction, QActionGroup, QColor, QKeySequence, QTextDocument

from core.provider_router import ProviderRouter, RoutingStrategy
from core.model_manager import ModelManager
from core.settings import SettingsManager
from storage.history_manager import HistoryManager
from utils.system_checks import SystemChecker
from utils.key_handler import KeyHandler
from .settings_dialog import SettingsDialog


class NoopKeyHandler:
    """Fallback key handler used when encrypted key storage fails to initialize."""

    def get_key(self, provider_name: str):
        return None

    def set_key(self, provider_name: str, key: str):
        return None

    def delete_key(self, provider_name: str):
        return None

    def get_key_store_status(self):
        return "unavailable"


class ChatWorker(QThread):
    """Worker thread for handling chat requests asynchronously."""
    
    response_received = pyqtSignal(str)
    stream_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    status_changed = pyqtSignal(str)
    
    def __init__(self, router: ProviderRouter, messages: List[Dict[str, str]],
                 model: Optional[str] = None, stream: bool = True,
                 temperature: float = 0.7, max_tokens: Optional[int] = None):
        super().__init__()
        self.router = router
        self.messages = messages
        self.model = model
        self.stream = stream
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._is_running = True
    
    def run(self):
        """Run the chat request in a separate thread."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            async def collect_response_non_stream():
                chunks = []
                async for chunk in self.router.route_request(
                    messages=self.messages,
                    model=self.model,
                    stream=False,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                ):
                    chunks.append(chunk)
                return ''.join(chunks)
            
            if self.stream:
                response_text = ""
                async def collect_chunks():
                    chunks = []
                    async for chunk in self.router.route_request(
                        messages=self.messages,
                        model=self.model,
                        stream=True,
                        temperature=self.temperature,
                        max_tokens=self.max_tokens,
                    ):
                        if not self._is_running:
                            break
                        chunks.append(chunk)
                        self.stream_received.emit(chunk)
                    return ''.join(chunks)
                
                response_text = loop.run_until_complete(collect_chunks())

                # Some models/providers can return empty streams even when
                # non-streaming returns valid content. Retry once non-stream.
                if self._is_running and not response_text.strip():
                    self.status_changed.emit("Streaming returned no output; retrying once...")
                    response_text = loop.run_until_complete(collect_response_non_stream())
                
                if self._is_running:
                    self.response_received.emit(response_text)
            else:
                response = loop.run_until_complete(collect_response_non_stream())
                if self._is_running:
                    self.response_received.emit(response)
        
        except Exception as e:
            if self._is_running:
                self.error_occurred.emit(str(e))
        finally:
            try:
                loop.run_until_complete(loop.shutdown_asyncgens())
            except Exception as e:
                self.logger.debug(f"Failed to shutdown async generators in chat worker: {e}")
            loop.close()
    
    def stop(self):
        """Stop the worker thread."""
        self._is_running = False


class SystemCheckWorker(QThread):
    """Worker thread for running async system checks without blocking the UI."""

    report_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def run(self):
        """Run system checks in an isolated event loop."""
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            checker = SystemChecker()
            results = loop.run_until_complete(checker.check_all_systems())
            report = self._format_report(results, checker)
            self.report_ready.emit(report)
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            try:
                loop.run_until_complete(loop.shutdown_asyncgens())
            except Exception as e:
                # System check worker doesn't have logger, so we use print for debug
                print(f"Debug: Failed to shutdown async generators in system check worker: {e}")
            loop.close()

    @staticmethod
    def _format_report(results: Dict[str, Any], checker: SystemChecker) -> str:
        """Format check results into a readable report string."""
        report = "SYSTEM CHECK REPORT\n" + "=" * 50 + "\n\n"

        # System info
        sys_info = results['system_info']
        report += f"System: {sys_info['platform']} {sys_info['platform_release']}\n"
        report += f"Python: {sys_info['python_version']}\n\n"

        # Python checks
        python_checks = results['python_checks']
        report += "Python Environment:\n"
        report += f"  Version OK: {python_checks['python_version_ok']}\n"
        missing = ', '.join(python_checks['missing_packages']) if python_checks['missing_packages'] else 'None'
        report += f"  Missing packages: {missing}\n\n"

        # Network checks
        network_checks = results['network_checks']
        report += "Network Connectivity:\n"
        report += f"  Internet: {'Available' if network_checks['internet_available'] else 'Not Available'}\n\n"

        # Provider checks
        provider_checks = results['provider_checks']
        report += "AI Provider Connectivity:\n"
        for provider, check in provider_checks.items():
            status = "Available" if check['available'] else f"Not Available ({check.get('error', 'Unknown error')})"
            report += f"  {provider.title()}: {status}\n"
        report += "\n"

        # File system checks
        fs_checks = results['file_system_checks']
        report += "File System:\n"
        report += f"  Config dir accessible: {fs_checks['config_dir_accessible']}\n"
        report += f"  Data dir accessible: {fs_checks['data_dir_accessible']}\n"

        # Recommendations
        recommendations = checker.get_recommendations(results)
        if recommendations:
            report += "\nRecommendations:\n"
            for i, rec in enumerate(recommendations, 1):
                report += f"  {i}. {rec}\n"

        return report


class WarmupWorker(QThread):
    """Background thread that pre-loads an Ollama model into VRAM.

    Sending a zero-inference request eliminates the cold-start latency
    on the first real message, making the initial response as fast as
    subsequent ones.
    """

    warmup_done = pyqtSignal(str)   # model name on success
    warmup_failed = pyqtSignal(str) # error message on failure

    def __init__(self, base_url: str, model: str):
        super().__init__()
        self._base_url = base_url
        self._model = model

    def run(self):
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            from core.ollama_client import OllamaClient
            client = OllamaClient(base_url=self._base_url)
            loop.run_until_complete(client.warm_model(self._model))
            self.warmup_done.emit(self._model)
        except Exception as e:
            self.warmup_failed.emit(str(e))
        finally:
            try:
                loop.run_until_complete(loop.shutdown_asyncgens())
            except Exception as e:
                # Warmup worker doesn't have logger, so we use print for debug
                print(f"Debug: Failed to shutdown async generators in warmup worker: {e}")
            loop.close()


class EmbeddedTerminal(QWidget):
    """Lightweight in-app shell terminal powered by QProcess."""

    output_received = pyqtSignal(str)

    def __init__(self, parent=None, working_directory: Optional[str] = None):
        super().__init__(parent)
        self.process = QProcess(self)
        if working_directory and os.path.isdir(working_directory):
            self.process.setWorkingDirectory(working_directory)
        self.process.readyReadStandardOutput.connect(self._read_stdout)
        self.process.readyReadStandardError.connect(self._read_stderr)
        self.process.finished.connect(self._on_finished)

        layout = QVBoxLayout(self)
        toolbar = QHBoxLayout()

        self.start_button = QPushButton("Start Shell")
        self.start_button.clicked.connect(self.start_shell)
        toolbar.addWidget(self.start_button)

        self.interrupt_button = QPushButton("Ctrl+C")
        self.interrupt_button.clicked.connect(self.send_interrupt)
        self.interrupt_button.setEnabled(False)
        toolbar.addWidget(self.interrupt_button)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_output)
        toolbar.addWidget(self.clear_button)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.output.setPlaceholderText("Terminal output appears here...")
        layout.addWidget(self.output)

        self.command_editor = QPlainTextEdit()
        self.command_editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.command_editor.setPlaceholderText("Write one or multiple commands here...")
        self.command_editor.setMaximumHeight(110)
        layout.addWidget(self.command_editor)

        editor_button_row = QHBoxLayout()
        self.run_editor_button = QPushButton("Run Editor Commands")
        self.run_editor_button.clicked.connect(self.run_editor_commands)
        editor_button_row.addWidget(self.run_editor_button)

        self.clear_editor_button = QPushButton("Clear Editor")
        self.clear_editor_button.clicked.connect(lambda: self.command_editor.clear())
        editor_button_row.addWidget(self.clear_editor_button)
        editor_button_row.addStretch()
        layout.addLayout(editor_button_row)

        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Enter shell command and press Enter")
        self.command_input.returnPressed.connect(self.run_command)
        layout.addWidget(self.command_input)

    def start_shell(self):
        """Start an interactive shell session if not already running."""
        if self.process.state() != QProcess.ProcessState.NotRunning:
            return

        shell = self._resolve_shell()
        self.process.start(shell)
        if not self.process.waitForStarted(1500):
            self._append_output("Failed to start shell process.")
            return

        self.start_button.setEnabled(False)
        self.interrupt_button.setEnabled(True)
        self._append_output("Shell started. Commands run inside this tab session.")

    def run_command(self):
        """Send command text to the shell process."""
        command = self.command_input.text().strip()
        if not command:
            return

        if self.process.state() == QProcess.ProcessState.NotRunning:
            self.start_shell()
            if self.process.state() == QProcess.ProcessState.NotRunning:
                return

        self._append_output(f"$ {command}")
        self.process.write((command + "\n").encode("utf-8"))
        self.command_input.clear()

    def run_text(self, text: str):
        """Run a multi-line text block as-is in terminal."""
        payload = "" if text is None else str(text).strip()
        if not payload:
            return
        if self.process.state() == QProcess.ProcessState.NotRunning:
            self.start_shell()
            if self.process.state() == QProcess.ProcessState.NotRunning:
                return
        self._append_output("$ [running snippet]")
        self.process.write((payload + "\n").encode("utf-8"))

    def run_editor_commands(self):
        """Run commands from the multiline terminal editor."""
        text = self.command_editor.toPlainText()
        payload = "" if text is None else str(text).strip()
        if not payload:
            return
        self.run_text(payload)

    def send_interrupt(self):
        """Send a Ctrl+C style interrupt signal."""
        if self.process.state() != QProcess.ProcessState.NotRunning:
            self.process.write(b"\x03")

    def clear_output(self):
        self.output.clear()

    def stop(self):
        """Stop shell process for cleanup."""
        if self.process.state() == QProcess.ProcessState.NotRunning:
            return

        self.process.terminate()
        if not self.process.waitForFinished(800):
            self.process.kill()
            self.process.waitForFinished(800)

    def _read_stdout(self):
        text = bytes(self.process.readAllStandardOutput()).decode("utf-8", errors="replace")
        self._append_output(text.rstrip("\n"))

    def _read_stderr(self):
        text = bytes(self.process.readAllStandardError()).decode("utf-8", errors="replace")
        self._append_output(text.rstrip("\n"))

    def _on_finished(self, _exit_code: int, _exit_status):
        self.start_button.setEnabled(True)
        self.interrupt_button.setEnabled(False)
        self._append_output("Shell session closed.")

    @staticmethod
    def _resolve_shell() -> str:
        """Pick the best available interactive shell executable."""
        env_shell_raw = os.environ.get("SHELL", "").strip()
        env_shell = ""
        if env_shell_raw:
            try:
                parts = shlex.split(env_shell_raw)
                env_shell = parts[0] if parts else ""
            except ValueError:
                env_shell = env_shell_raw.split()[0] if env_shell_raw.split() else ""

        candidates = [
            env_shell,
            "bash",
            "/bin/bash",
            "sh",
            "/bin/sh",
        ]

        for candidate in candidates:
            if not candidate:
                continue
            if os.path.isabs(candidate) and os.path.exists(candidate):
                return candidate
            resolved = shutil.which(candidate)
            if resolved:
                return resolved

        # Final fallback, expected to exist on POSIX systems.
        return "/bin/sh"

    def _append_output(self, text: str):
        if text is None:
            return
        self.output_received.emit(str(text))
        if not text:
            self.output.appendPlainText("")
        else:
            self.output.appendPlainText(str(text))
        cursor = self.output.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.output.setTextCursor(cursor)


class ChatWindow(QMainWindow):
    """Main chat window for the application."""
    
    def __init__(self):
        super().__init__()

        # Initialize logger early so startup failures are captured.
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.settings = SettingsManager()
        self.router = ProviderRouter()
        self.model_manager = ModelManager()
        self.history_manager = HistoryManager()
        try:
            self.key_handler = KeyHandler()
            # Trigger an initial key-store read so decryption issues are detectable.
            self.key_handler.list_providers()
        except Exception as e:
            self.logger.error(f"Failed to initialize secure key storage: {e}")
            self.key_handler = NoopKeyHandler()
        
        # UI state
        self.current_worker = None
        self.system_check_worker = None
        self.current_messages = []
        self._display_messages = []
        self._models_by_provider = {}
        self._model_health = {}
        self._model_performance = {}
        self.provider_filter_mode = "all"
        self.prefer_fast_local_models = True
        self._streaming_in_progress = False
        self._current_stream_timestamp = None
        self._current_generation_model = None
        self._current_selected_model = None
        self._key_recovery_prompt_shown = False
        self._code_snippets: List[Dict[str, str]] = []
        self._terminal_counter = 0
        self._terminal_working_directory = os.getcwd()
        
        # Initialize performance tracking
        self._generation_start_time = None
        self._generation_tokens = 0

        # Persist model reliability ordering across app restarts.
        self._model_health_file = self.settings.config_dir / "model_health.json"
        self._load_model_health_cache()
        
        # Setup UI
        self.init_ui()
        self.setup_menu()
        self.setup_status_bar()
        
        # Load settings
        self.load_settings()
        
        # Initialize providers
        self.init_providers_sync()
        
        # Setup timer for status updates
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(5000)  # Update every 5 seconds

        # Warmup worker reference (kept alive so GC doesn't collect the QThread).
        self._warmup_worker: Optional[WarmupWorker] = None

        # Prompt users to recover API keys if encrypted storage cannot be decrypted.
        QTimer.singleShot(0, self._prompt_key_store_recovery_if_needed)
        # Pre-load the fast local model into VRAM after providers are ready.
        QTimer.singleShot(1500, self._prewarm_local_model)

    def _prewarm_local_model(self):
        """Silently load the fast local model into VRAM on startup.

        This eliminates the cold-start penalty for the first real request
        by firing a zero-inference load call in a background thread.
        """
        ollama_provider = self.router.providers.get("ollama")
        if not getattr(ollama_provider, "is_available", False):
            self.logger.debug("Skipping warmup: Ollama not available")
            return

        # Determine which model will actually run when fast mode is on.
        available_ollama = set(self._models_by_provider.get("ollama", []))
        if not available_ollama:
            self.logger.debug("Skipping warmup: no Ollama models listed yet")
            return

        # Pick the primary fast model (last resort alias used by all chains).
        target = None
        for candidate in ["llama3.2:1b", "qwen2.5:1.5b", "phi3:mini"]:
            if candidate in available_ollama:
                target = candidate
                break
        if target is None:
            target = next(iter(available_ollama))  # fall back to whatever is first

        base_url = getattr(ollama_provider, "base_url", "http://localhost:11434")
        self.logger.info("Starting model warmup: %s @ %s", target, base_url)

        self._warmup_worker = WarmupWorker(base_url=base_url, model=target)
        self._warmup_worker.warmup_done.connect(
            lambda m: self.logger.info("Warmup done: %s — first response will be fast", m)
        )
        self._warmup_worker.warmup_failed.connect(
            lambda e: self.logger.warning("Warmup failed (non-critical): %s", e)
        )
        self._warmup_worker.start()

    def _prompt_key_store_recovery_if_needed(self):
        """Show one-time guidance when encrypted key store cannot be decrypted."""
        if self._key_recovery_prompt_shown:
            return

        status = getattr(self.key_handler, "get_key_store_status", lambda: "unknown")()
        if status != "invalid-token":
            return

        self._key_recovery_prompt_shown = True
        reply = QMessageBox.question(
            self,
            "API Keys Need Attention",
            "Stored API keys could not be decrypted with the current encryption key.\n\n"
            "Would you like to open Settings now to re-enter your API keys?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.show_provider_settings("Providers")
    
    def init_ui(self):
        """Initialize the main UI components."""
        self.setWindowTitle("Private Chat Linux Client")
        self.setGeometry(
            self.settings.ui.window_x,
            self.settings.ui.window_y,
            self.settings.ui.window_width,
            self.settings.ui.window_height
        )
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create splitter for chat and controls
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Workspace tabs: conversation + coding tools
        self.workspace_tabs = QTabWidget()

        # Chat display area
        chat_tab = QWidget()
        chat_tab_layout = QVBoxLayout(chat_tab)

        # Create search toolbar
        self.search_toolbar = QToolBar()
        self.search_toolbar.setMovable(False)
        self.search_toolbar.setVisible(False)  # Hidden by default
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search chat...")
        self.search_input.setMaximumWidth(300)
        self.search_input.returnPressed.connect(self.search_next)
        self.search_toolbar.addWidget(self.search_input)
        
        # Search controls
        self.search_case_sensitive = QCheckBox("Case")
        self.search_case_sensitive.setToolTip("Case sensitive search")
        self.search_toolbar.addWidget(self.search_case_sensitive)
        
        self.search_whole_words = QCheckBox("Whole")
        self.search_whole_words.setToolTip("Whole words only")
        self.search_toolbar.addWidget(self.search_whole_words)
        
        # Navigation buttons
        self.search_prev_btn = QPushButton("▲")
        self.search_prev_btn.setToolTip("Previous result (Shift+F3)")
        self.search_prev_btn.clicked.connect(self.search_previous)
        self.search_prev_btn.setMaximumWidth(30)
        self.search_toolbar.addWidget(self.search_prev_btn)
        
        self.search_next_btn = QPushButton("▼")
        self.search_next_btn.setToolTip("Next result (F3)")
        self.search_next_btn.clicked.connect(self.search_next)
        self.search_next_btn.setMaximumWidth(30)
        self.search_toolbar.addWidget(self.search_next_btn)
        
        # Results label
        self.search_results_label = QLabel("")
        self.search_results_label.setStyleSheet("color: #666; font-size: 11px;")
        self.search_toolbar.addWidget(self.search_results_label)
        
        # Close button
        close_search_btn = QPushButton("✕")
        close_search_btn.setToolTip("Close search (Escape)")
        close_search_btn.clicked.connect(self.close_search)
        close_search_btn.setMaximumWidth(25)
        self.search_toolbar.addWidget(close_search_btn)
        
        chat_tab_layout.addWidget(self.search_toolbar)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont(self.settings.ui.font_family, self.settings.ui.font_size))
        self.chat_display.setPlaceholderText("Conversation stream will appear here...")
        chat_tab_layout.addWidget(self.chat_display)

        self.workspace_tabs.addTab(chat_tab, "Conversation")

        # Code snippets tab (auto-populated from AI fenced blocks)
        code_tab = QWidget()
        code_layout = QVBoxLayout(code_tab)

        self.code_blocks_list = QListWidget()
        self.code_blocks_list.currentRowChanged.connect(self._on_code_snippet_selected)
        self.code_blocks_list.itemSelectionChanged.connect(self._on_code_list_selection_changed)
        code_layout.addWidget(self.code_blocks_list)

        self.code_preview = QPlainTextEdit()
        self.code_preview.setReadOnly(False)
        self.code_preview.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.code_preview.setPlaceholderText("Select a snippet, then edit code here before copy/save/run.")
        self.code_preview.textChanged.connect(self._on_code_preview_changed)
        code_layout.addWidget(self.code_preview)

        code_button_layout = QHBoxLayout()
        self.copy_code_button = QPushButton("Copy Snippet")
        self.copy_code_button.clicked.connect(self.copy_selected_code_snippet)
        code_button_layout.addWidget(self.copy_code_button)

        self.save_code_button = QPushButton("Save Snippet")
        self.save_code_button.clicked.connect(self.save_selected_code_snippet)
        code_button_layout.addWidget(self.save_code_button)

        self.run_code_button = QPushButton("Run In Terminal")
        self.run_code_button.clicked.connect(self.run_selected_code_snippet)
        code_button_layout.addWidget(self.run_code_button)
        code_button_layout.addStretch()
        code_layout.addLayout(code_button_layout)

        self._update_snippet_action_state()

        self.workspace_tabs.addTab(code_tab, "Code Snippets")

        # Embedded terminal manager
        terminal_tab = QWidget()
        self.terminal_workspace_tab = terminal_tab
        terminal_layout = QVBoxLayout(terminal_tab)
        terminal_controls = QHBoxLayout()

        self.new_terminal_button = QPushButton("New Terminal")
        self.new_terminal_button.clicked.connect(self.create_terminal_session)
        terminal_controls.addWidget(self.new_terminal_button)

        self.close_terminal_button = QPushButton("Close Terminal")
        self.close_terminal_button.clicked.connect(self.close_current_terminal)
        terminal_controls.addWidget(self.close_terminal_button)

        terminal_controls.addStretch()
        terminal_layout.addLayout(terminal_controls)

        self.terminal_tabs = QTabWidget()
        terminal_layout.addWidget(self.terminal_tabs)
        self.workspace_tabs.addTab(terminal_tab, "Terminals")

        # Create one default terminal session for quick use.
        self.create_terminal_session(start_shell=False)
        
        # Input area
        input_widget = QWidget()
        input_layout = QVBoxLayout(input_widget)
        
        # Model selection
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Provider:"))

        self.provider_combo = QComboBox()
        self.provider_combo.setMinimumWidth(180)
        self.provider_combo.currentIndexChanged.connect(self.on_provider_changed)
        model_layout.addWidget(self.provider_combo)

        model_layout.addWidget(QLabel("Model:"))
        
        self.model_combo = QComboBox()
        self.model_combo.setMinimumWidth(200)
        self.model_combo.setVisible(True)
        model_layout.addWidget(self.model_combo)
        
        model_layout.addStretch()
        
        # Provider status
        self.status_label = QLabel("Initializing...")
        model_layout.addWidget(self.status_label)
        
        input_layout.addLayout(model_layout)
        
        # Message input
        input_layout.addWidget(QLabel("Message:"))
        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Type your message here...")
        self.input_box.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_box)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        button_layout.addWidget(self.send_button)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_generation)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_chat)
        button_layout.addWidget(self.clear_button)
        
        button_layout.addStretch()
        
        input_layout.addLayout(button_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        input_layout.addWidget(self.progress_bar)
        
        # Add widgets to splitter
        splitter.addWidget(self.workspace_tabs)
        splitter.addWidget(input_widget)
        splitter.setSizes([400, 200])
        
        main_layout.addWidget(splitter)
        
        # Apply dark theme
        self.apply_theme()
    
    def setup_menu(self):
        """Setup the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        export_action = QAction("Export Chat", self)
        export_action.setShortcut(QKeySequence.StandardKey.SaveAs)  # Ctrl+Shift+S
        export_action.triggered.connect(self.export_chat)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)  # Ctrl+Q
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        clear_action = QAction("Clear Chat", self)
        clear_action.setShortcut(QKeySequence("Ctrl+L"))  # Ctrl+L for Clear
        clear_action.triggered.connect(self.clear_chat)
        edit_menu.addAction(clear_action)
        
        # Add copy functionality
        copy_action = QAction("Copy Chat", self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)  # Ctrl+C
        copy_action.triggered.connect(self.copy_chat)
        edit_menu.addAction(copy_action)
        
        # Add search functionality
        search_action = QAction("Search Chat", self)
        search_action.setShortcut(QKeySequence.StandardKey.Find)  # Ctrl+F
        search_action.triggered.connect(self.toggle_search)
        edit_menu.addAction(search_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        self.timestamp_action = QAction("Show Timestamps", self)
        self.timestamp_action.setCheckable(True)
        self.timestamp_action.setChecked(self.settings.ui.show_timestamps)
        self.timestamp_action.setShortcut(QKeySequence("Ctrl+T"))  # Ctrl+T for Timestamps
        self.timestamp_action.triggered.connect(self.toggle_timestamps)
        view_menu.addAction(self.timestamp_action)
        
        self.model_info_action = QAction("Show Model Info", self)
        self.model_info_action.setCheckable(True)
        self.model_info_action.setChecked(self.settings.ui.show_model_info)
        self.model_info_action.setShortcut(QKeySequence("Ctrl+M"))  # Ctrl+M for Model Info
        self.model_info_action.triggered.connect(self.toggle_model_info)
        view_menu.addAction(self.model_info_action)

        view_menu.addSeparator()

        filter_group = QActionGroup(self)
        filter_group.setExclusive(True)

        self.filter_all_providers_action = QAction("Show All Providers", self)
        self.filter_all_providers_action.setCheckable(True)
        self.filter_all_providers_action.setChecked(True)
        self.filter_all_providers_action.triggered.connect(lambda: self.set_provider_filter("all"))
        filter_group.addAction(self.filter_all_providers_action)
        view_menu.addAction(self.filter_all_providers_action)

        self.filter_enabled_providers_action = QAction("Show Enabled Providers", self)
        self.filter_enabled_providers_action.setCheckable(True)
        self.filter_enabled_providers_action.triggered.connect(lambda: self.set_provider_filter("enabled"))
        filter_group.addAction(self.filter_enabled_providers_action)
        view_menu.addAction(self.filter_enabled_providers_action)

        self.filter_available_providers_action = QAction("Show Available Providers", self)
        self.filter_available_providers_action.setCheckable(True)
        self.filter_available_providers_action.triggered.connect(lambda: self.set_provider_filter("available"))
        filter_group.addAction(self.filter_available_providers_action)
        view_menu.addAction(self.filter_available_providers_action)

        view_menu.addSeparator()

        self.fast_local_models_action = QAction("Prefer Fast Local Models", self)
        self.fast_local_models_action.setCheckable(True)
        self.fast_local_models_action.setChecked(self.prefer_fast_local_models)
        self.fast_local_models_action.triggered.connect(self.toggle_prefer_fast_local_models)
        view_menu.addAction(self.fast_local_models_action)
        
        # Settings menu
        settings_menu = menubar.addMenu("Settings")
        
        providers_action = QAction("Configure Providers", self)
        providers_action.setShortcut(QKeySequence("Ctrl+P"))  # Ctrl+P for Providers
        providers_action.triggered.connect(lambda: self.show_provider_settings("Providers"))
        settings_menu.addAction(providers_action)
        
        api_keys_action = QAction("Manage API Keys", self)
        api_keys_action.setShortcut(QKeySequence("Ctrl+K"))  # Ctrl+K for Keys
        api_keys_action.triggered.connect(lambda: self.show_provider_settings("Providers"))
        settings_menu.addAction(api_keys_action)
        
        settings_menu.addSeparator()
        
        ui_settings_action = QAction("UI Settings", self)
        ui_settings_action.setShortcut(QKeySequence("Ctrl+U"))  # Ctrl+U for UI Settings
        ui_settings_action.triggered.connect(lambda: self.show_provider_settings("UI"))
        settings_menu.addAction(ui_settings_action)
        
        chat_settings_action = QAction("Chat Settings", self)
        chat_settings_action.setShortcut(QKeySequence("Ctrl+,"))  # Ctrl+, for Settings
        chat_settings_action.triggered.connect(lambda: self.show_provider_settings("Chat"))
        settings_menu.addAction(chat_settings_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        system_check_action = QAction("System Check", self)
        system_check_action.setShortcut(QKeySequence("F12"))  # F12 for System Check
        system_check_action.triggered.connect(self.run_system_check)
        help_menu.addAction(system_check_action)
        
        health_dashboard_action = QAction("Provider Health Dashboard", self)
        health_dashboard_action.triggered.connect(self.show_health_dashboard)
        help_menu.addAction(health_dashboard_action)
        
        help_menu.addSeparator()
        
        documentation_action = QAction("Documentation", self)
        documentation_action.triggered.connect(self.show_documentation)
        help_menu.addAction(documentation_action)
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_status_bar(self):
        """Setup the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Add provider health indicator to status bar
        self.health_label = QLabel("🔍 Checking...")
        self.health_label.setStyleSheet("color: #666; font-size: 11px; padding: 2px 8px;")
        self.health_label.setToolTip("Provider health status - hover for details")
        self.status_bar.addPermanentWidget(self.health_label)
        
        # Setup health monitoring timer
        self.health_timer = QTimer()
        self.health_timer.timeout.connect(self.update_provider_health_status)
        self.health_timer.start(30000)  # Update every 30 seconds
        
        # Initial health update
        self.update_provider_health_status()
    
    def load_settings(self):
        """Load application settings."""
        # Apply UI settings
        self.chat_display.setFont(QFont(self.settings.ui.font_family, self.settings.ui.font_size))
        self.input_box.setFont(QFont(self.settings.ui.font_family, self.settings.ui.font_size))
    
    async def init_providers(self):
        """Initialize AI providers."""
        try:
            provider_config = self.settings.get_provider_dict(self.key_handler)
            # Clear stale provider instances before re-initialization.
            self.router.providers.clear()
            await self.router.initialize_providers(provider_config)
            await self.update_model_list()
            self.status_label.setText("Providers loaded")
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
            self.logger.error(f"Failed to initialize providers: {e}")
    
    def init_providers_sync(self):
        """Synchronous wrapper for async provider initialization."""
        # Check if we're already in an event loop
        try:
            loop = asyncio.get_running_loop()
            # If we're in an async context, we can't use run_until_complete
            # Just skip initialization for now - it will be initialized later
            self.logger.debug("Skipping provider initialization in async context")
            return
        except RuntimeError:
            # No running loop, we can create our own
            pass
        
        # Use a fresh loop for each sync initialization to avoid reusing
        # closed/running loops across settings updates.
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(self.init_providers())
        except Exception as e:
            self.status_label.setText(f"Initialization Error: {str(e)}")
            self.logger.error(f"Failed to initialize providers synchronously: {e}")
        finally:
            try:
                loop.run_until_complete(loop.shutdown_asyncgens())
            except Exception as e:
                self.logger.debug(f"Failed to shutdown async generators during provider initialization: {e}")
            loop.close()
    
    async def update_model_list(self):
        """Update the model selection combo box."""
        try:
            models = await self.router.get_all_models()
            
            # Update UI directly
            self.update_model_list_ui(models)
            
            # Log update: "models" contains live-provider model maps.
            live_model_count = sum(len(model_list) for model_list in models.values())
            available_provider_count = sum(
                1 for provider in self.router.providers.values() if getattr(provider, "is_available", False)
            )
            configured_provider_count = len(getattr(self.settings, "providers", {}) or {})
            selectable_model_count = sum(len(model_list) for model_list in self._models_by_provider.values())

            self.logger.info(
                "Model catalog refreshed: selectable=%s across configured=%s providers; live=%s across available=%s providers",
                selectable_model_count,
                configured_provider_count,
                live_model_count,
                available_provider_count,
            )
            
        except Exception as e:
            self.logger.error(f"Failed to update model list: {e}")
    
    def update_model_list_ui(self, models: Dict[str, List[str]]):
        """Update provider/model combo boxes on the main thread."""
        try:
            self.logger.info(f"update_model_list_ui called with {len(models)} providers")

            active_providers = sum(
                1 for provider in self.router.providers.values() if getattr(provider, "is_available", False)
            )

            # Ensure all known providers are listed, including disabled/unavailable ones.
            known_provider_names = list(self.settings.providers.keys())
            if not known_provider_names:
                known_provider_names = sorted(set(models.keys()) | set(self.router.providers.keys()))

            provider_models = {}
            for provider_name in known_provider_names:
                provider_models[provider_name] = list(models.get(provider_name) or self.router._get_fallback_models(provider_name))

            total_models = sum(len(model_list) for model_list in provider_models.values())
            self.logger.info(f"Total models to add: {total_models}")

            self._models_by_provider = provider_models
            self.provider_combo.clear()
            self.model_combo.clear()

            if self._models_by_provider and total_models > 0:
                visible_provider_names = self._filter_provider_names(self._models_by_provider.keys())
                provider_names = sorted(
                    visible_provider_names,
                    key=lambda name: (
                        0 if self._is_provider_enabled(name) and getattr(self.router.providers.get(name), "is_available", False) else 1,
                        0 if self._is_provider_enabled(name) else 1,
                        name,
                    ),
                )

                if not provider_names:
                    self.provider_combo.addItem("No providers match current filter", None)
                    self.provider_combo.setCurrentIndex(0)
                    self.model_combo.addItem("No models for current filter", None)
                    self.model_combo.setCurrentIndex(0)
                    self.send_button.setEnabled(False)
                    self.status_label.setText("No providers match current filter")
                    return

                for provider_name in provider_names:
                    is_enabled = self._is_provider_enabled(provider_name)
                    is_online = getattr(self.router.providers.get(provider_name), "is_available", False)
                    if not is_enabled:
                        suffix = "disabled"
                    elif is_online:
                        suffix = "online"
                    else:
                        suffix = "offline"
                    self.provider_combo.addItem(f"{provider_name} ({suffix})", provider_name)

                default_provider = self.settings.chat.default_provider
                if isinstance(default_provider, str) and default_provider in self._models_by_provider:
                    provider_index = self.provider_combo.findData(default_provider)
                else:
                    provider_index = self.provider_combo.findData("ollama")
                    if provider_index < 0:
                        provider_index = 0

                self.provider_combo.setCurrentIndex(provider_index)
                selected_provider = self.provider_combo.currentData()
                self._populate_models_for_provider(selected_provider, preferred_model=self.settings.chat.default_model)

                self.provider_combo.repaint()
                self.model_combo.repaint()
                self.send_button.setEnabled(True)
                if active_providers > 0:
                    self.status_label.setText(f"Providers loaded ({active_providers} active)")
                else:
                    self.status_label.setText("Fallback models loaded. Start Ollama or configure another provider to generate responses.")
                self.logger.info("Provider/model combos updated and repainted")
            else:
                self.provider_combo.addItem("No available providers", None)
                self.provider_combo.setCurrentIndex(0)
                self.model_combo.addItem("No available models")
                self.model_combo.setCurrentIndex(0)
                self.send_button.setEnabled(False)
                self.status_label.setText("No available AI providers")
                self.logger.warning("No models available from any active providers")
                
        except Exception as e:
            self.logger.error(f"Failed to update model list UI: {e}")

    def _populate_models_for_provider(self, provider_name: Optional[str], preferred_model: Optional[str] = None):
        """Populate model combo based on the currently selected provider."""
        self.model_combo.clear()

        if not isinstance(provider_name, str) or not provider_name:
            self.model_combo.addItem("No models for provider", None)
            self.model_combo.setCurrentIndex(0)
            self.send_button.setEnabled(False)
            return

        if not self._is_provider_enabled(provider_name):
            self.model_combo.addItem("Provider disabled (enable in Settings)", None)
            self.model_combo.setCurrentIndex(0)
            self.send_button.setEnabled(False)
            return

        if not self._is_provider_available(provider_name):
            self.model_combo.addItem("Provider unavailable (check API key/network)", None)
            self.model_combo.setCurrentIndex(0)
            self.send_button.setEnabled(False)
            return

        models = self._models_by_provider.get(provider_name, [])
        if not models:
            self.model_combo.addItem("No models for provider", None)
            self.model_combo.setCurrentIndex(0)
            self.send_button.setEnabled(False)
            return

        full_model_keys = [f"{provider_name}/{m}" for m in models]
        health_rank = {
            True: 0,   # verified working
            None: 1,   # not yet verified
            False: 2,  # recently failed
        }
        sorted_pairs = sorted(
            zip(models, full_model_keys),
            key=lambda pair: (
                health_rank.get(self._model_health.get(pair[1]), 1),
                pair[0].lower(),
            )
        )

        for model, full_key in sorted_pairs:
            health = self._model_health.get(full_key)
            if health is True:
                label = f"{model}  [verified]"
            elif health is False:
                label = f"{model}  [retry]"
            else:
                label = model
            self.model_combo.addItem(label, model)

        preferred_index = -1
        if isinstance(preferred_model, str) and preferred_model:
            preferred_index = self.model_combo.findData(preferred_model)

        if preferred_index < 0 and provider_name == "ollama":
            preferred_index = self.model_combo.findData("llama3.2:1b")

        self.model_combo.setCurrentIndex(preferred_index if preferred_index >= 0 else 0)
        self.send_button.setEnabled(True)

    def _is_provider_enabled(self, provider_name: str) -> bool:
        """Return whether a provider is enabled in settings."""
        config = self.settings.providers.get(provider_name)
        return bool(config and getattr(config, "enabled", False))

    def _is_provider_available(self, provider_name: str) -> bool:
        """Return whether provider is currently reachable and initialized."""
        return bool(getattr(self.router.providers.get(provider_name), "is_available", False))

    def _filter_provider_names(self, provider_names):
        """Apply active provider filter mode to provider names."""
        names = list(provider_names)
        if self.provider_filter_mode == "enabled":
            return [name for name in names if self._is_provider_enabled(name)]
        if self.provider_filter_mode == "available":
            return [name for name in names if self._is_provider_enabled(name) and self._is_provider_available(name)]
        return names

    def set_provider_filter(self, mode: str):
        """Set provider visibility filter and refresh model/provider combos."""
        if mode not in {"all", "enabled", "available"}:
            mode = "all"
        self.provider_filter_mode = mode
        self.update_model_list_ui(self._models_by_provider)

    def toggle_prefer_fast_local_models(self):
        """Toggle automatic low-latency model substitution for local Ollama models."""
        self.prefer_fast_local_models = bool(self.fast_local_models_action.isChecked())
        if self.prefer_fast_local_models:
            self.status_bar.showMessage("Fast local model preference enabled")
        else:
            self.status_bar.showMessage("Fast local model preference disabled")

    def _select_speed_optimized_model(self, provider: str, model: str) -> str:
        """Return a speed-optimized model alias when fast mode is enabled."""
        if not self.prefer_fast_local_models or provider != "ollama":
            return model

        available = set(self._models_by_provider.get("ollama", []))
        if not available:
            return model

        # Prefer same-family smaller models; fallback to the known-fast 1B default.
        speed_aliases = {
            "qwen2.5:3b": ["qwen2.5:1.5b", "qwen2.5:0.5b", "llama3.2:1b"],
            "phi3.5:3.8b": ["phi3:mini", "llama3.2:1b"],
            "mistral:7b": ["qwen2.5:1.5b", "llama3.2:1b"],
        }

        for candidate in speed_aliases.get(model, []):
            if candidate in available and candidate != model:
                self.logger.info("Fast local alias selected: %s -> %s", model, candidate)
                self.status_bar.showMessage(f"Fast mode: using {candidate} instead of {model}")
                return candidate

        return model

    def on_provider_changed(self, _index: int):
        """Refresh model list when provider selection changes."""
        selected_provider = self.provider_combo.currentData()
        self._populate_models_for_provider(selected_provider, preferred_model=self.settings.chat.default_model)
        if isinstance(selected_provider, str):
            if not self._is_provider_enabled(selected_provider):
                self.status_label.setText(f"{selected_provider} is disabled. Enable it in Settings.")
            elif not getattr(self.router.providers.get(selected_provider), "is_available", False):
                self.status_label.setText(f"{selected_provider} is configured but currently unavailable.")
                self.send_button.setEnabled(False)
    
    def send_message(self):
        """Send a message to the AI."""
        message = self.input_box.text().strip()
        if not message:
            return

        current_data = self.model_combo.currentData()
        selected_provider = self.provider_combo.currentData() if hasattr(self, "provider_combo") else None

        if self.model_combo.count() == 0 or current_data is None:
            self.add_message("Error", "No AI providers are currently available. Configure a provider or start Ollama.")
            return

        # Backward-compatible path: old itemData format was (provider, model).
        if isinstance(current_data, tuple) and len(current_data) == 2:
            provider, model = current_data
        else:
            provider = selected_provider
            model = current_data

        if not isinstance(provider, str) or not provider or not isinstance(model, str) or not model:
            self.add_message("Error", "Invalid provider/model value. Please re-select a model and try again.")
            self.logger.warning(f"Invalid provider/model pair: provider={provider!r}, model={model!r}")
            return

        if not self._is_provider_enabled(provider):
            self.add_message("Error", f"Provider '{provider}' is disabled. Enable it in Settings first.")
            return

        if not getattr(self.router.providers.get(provider), "is_available", False):
            self.add_message("Error", f"Provider '{provider}' is not currently available. Check API key/network settings.")
            return
        
        # Add user message to chat
        self.add_message("You", message)
        
        # Add to message history
        self.current_messages.append({"role": "user", "content": message})
        
        # Clear input
        self.input_box.clear()
        
        # Get selected model
        selected_model = model
        effective_model = self._select_speed_optimized_model(provider, selected_model)
        full_model = f"{provider}/{effective_model}"
        self._current_selected_model = f"{provider}/{selected_model}"
        
        # Start generation
        self.start_generation(full_model)
    
    def start_generation(self, model: Optional[str] = None):
        """Start AI response generation."""
        # Update UI state
        self.send_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        model_health = self._model_health.get(model)
        if model_health is False:
            self.status_bar.showMessage("Generating response... (retrying model that failed previously)")
        elif model_health is None:
            self.status_bar.showMessage("Generating response... (first run for this model may be slower)")
        else:
            self.status_bar.showMessage("Generating response...")
        
        self._streaming_in_progress = bool(self.settings.chat.stream_responses)
        self._current_generation_model = model
        from datetime import datetime
        self._current_stream_timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Start performance tracking
        self._generation_start_time = datetime.now()
        self._generation_tokens = 0

        # For streaming mode, insert a stable prefix once and append chunks after it.
        if self._streaming_in_progress:
            cursor = self.chat_display.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            if self.settings.ui.show_timestamps:
                cursor.insertText(f"[{self._current_stream_timestamp}] AI: ")
            else:
                cursor.insertText("AI: ")
            if self.settings.ui.auto_scroll:
                self.chat_display.ensureCursorVisible()

        # Limit context size to improve latency on long chats.
        raw_context_window = self.settings.chat.context_window
        try:
            parsed_context_window = int(raw_context_window)
        except (TypeError, ValueError):
            parsed_context_window = 10

        context_window = max(1, min(50, parsed_context_window))
        if parsed_context_window != context_window:
            self.logger.warning(
                f"Invalid context_window={raw_context_window!r}; clamped to {context_window}"
            )

        contextual_messages = self.current_messages[-(context_window * 2):].copy()

        provider_name = model.split("/", 1)[0] if isinstance(model, str) and "/" in model else ""
        model_name = model.split("/", 1)[1] if isinstance(model, str) and "/" in model else ""
        profile = self._get_model_speed_profile(provider_name, model_name)

        # Reduce prompt size for local models to improve first-token latency.
        char_budget = profile.get("char_budget", 3500)
        if provider_name == "ollama":
            contextual_messages = self._trim_context_for_speed(contextual_messages, char_budget=char_budget)

        effective_max_tokens = self.settings.chat.max_tokens
        profile_max_tokens = profile.get("max_tokens")
        if effective_max_tokens is None and provider_name == "ollama":
            effective_max_tokens = profile_max_tokens
        elif isinstance(effective_max_tokens, int) and isinstance(profile_max_tokens, int):
            # Keep user limit but clamp to speed profile for heavy local models.
            effective_max_tokens = min(effective_max_tokens, profile_max_tokens)

        try:
            effective_temperature = float(self.settings.chat.temperature)
        except (TypeError, ValueError):
            effective_temperature = 0.7
        effective_temperature = max(0.0, min(2.0, effective_temperature))

        if provider_name == "ollama" and profile.get("name"):
            self.status_bar.showMessage(
                f"Generating response... ({profile['name']}: max_tokens={effective_max_tokens}, context~{char_budget} chars)"
            )
        
        # Start worker thread
        self.current_worker = ChatWorker(
            self.router,
            contextual_messages,
            model,
            self.settings.chat.stream_responses,
            temperature=effective_temperature,
            max_tokens=effective_max_tokens,
        )
        self.current_worker.response_received.connect(self.on_response_complete)
        self.current_worker.stream_received.connect(self.on_stream_received)
        self.current_worker.error_occurred.connect(self.on_error)
        self.current_worker.status_changed.connect(self.on_status_changed)
        self.current_worker.start()
    
    def stop_generation(self):
        """Stop AI response generation."""
        if self.current_worker:
            self.current_worker.stop()
            self.current_worker.wait()
            self.current_worker = None
        
        self.on_generation_complete()
    
    def on_stream_received(self, chunk: str):
        """Handle streaming response chunk."""
        if not self._streaming_in_progress:
            return

        if chunk is None:
            return

        # Append chunk to AI response
        cursor = self.chat_display.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(str(chunk))
        self.chat_display.ensureCursorVisible()
    
    def on_response_complete(self, response: str):
        """Handle complete response."""
        response_text = "" if response is None else str(response)

        if not response_text.strip():
            selected_model = self._current_generation_model or "the selected model"
            self.logger.warning(f"Model returned empty response: model={selected_model!r}")
            model_key = self._current_selected_model or selected_model
            if isinstance(model_key, str):
                self._model_health[model_key] = False
                self._save_model_health_cache()

            # Preserve stream formatting by finishing the current line before reporting.
            if self._streaming_in_progress:
                cursor = self.chat_display.textCursor()
                cursor.movePosition(cursor.MoveOperation.End)
                cursor.insertText("\n")

            self.add_message(
                "Error",
                f"No response was returned by {selected_model}. "
                "This model may not support chat responses or may still be loading. "
                "Try a different model."
            )
            self.on_generation_complete()
            return

        # Non-streaming mode receives the full response at once.
        if not self._streaming_in_progress:
            self.add_message("AI", response_text)
        else:
            cursor = self.chat_display.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            cursor.insertText("\n")
            self._append_display_message("AI", response_text, self._current_stream_timestamp)

        self.register_code_blocks_from_ai_response(response_text)

        health_key = self._current_selected_model or self._current_generation_model
        if isinstance(health_key, str) and response_text.strip():
            self._model_health[health_key] = True
            self._save_model_health_cache()
        
        # Add to message history
        self.current_messages.append({"role": "assistant", "content": response_text})
        
        # Save to history
        if self.settings.chat.save_history:
            user_message = None
            if len(self.current_messages) >= 2 and self.current_messages[-2].get("role") == "user":
                user_message = self.current_messages[-2].get("content")
            else:
                for msg in reversed(self.current_messages[:-1]):
                    if msg.get("role") == "user":
                        user_message = msg.get("content")
                        break

            if user_message:
                self.history_manager.save_message("user", user_message)
            self.history_manager.save_message("assistant", response_text)
        
        self.on_generation_complete()
    
    def on_error(self, error_message: str):
        """Handle generation error."""
        health_key = self._current_selected_model or self._current_generation_model
        if isinstance(health_key, str):
            self._model_health[health_key] = False
            self._save_model_health_cache()
        self.add_message("Error", f"Failed to generate response: {error_message}")
        self.logger.error(f"Generation error: {error_message}")
        self.on_generation_complete()

    @staticmethod
    def _trim_context_for_speed(messages: List[Dict[str, str]], char_budget: int = 3500) -> List[Dict[str, str]]:
        """Trim oldest context so local generation starts faster on large chats."""
        if char_budget <= 0:
            return messages[-2:]
        total = 0
        selected: List[Dict[str, Any]] = []
        for msg in reversed(messages):
            content = str(msg.get("content", ""))
            size = len(content)
            if selected and total + size > char_budget:
                break
            selected.append(msg)
            total += size
        return list(reversed(selected))

    @staticmethod
    def _get_model_speed_profile(provider_name: str, model_name: str) -> Dict[str, Any]:
        """Return per-model generation profile tuned for lower latency."""
        if provider_name != "ollama":
            return {"name": "default", "max_tokens": 256, "char_budget": 3000}

        lowered = (model_name or "").lower()
        if "qwen2.5:3b" in lowered or "qwen" in lowered:
            return {"name": "speed profile: qwen", "max_tokens": 64, "char_budget": 900}
        if "phi3.5:3.8b" in lowered or "phi" in lowered:
            return {"name": "speed profile: phi", "max_tokens": 80, "char_budget": 1200}
        if "mistral:7b" in lowered or "mistral" in lowered:
            return {"name": "speed profile: mistral", "max_tokens": 64, "char_budget": 900}
        if "llama3.2:1b" in lowered:
            return {"name": "speed profile: llama1b", "max_tokens": 128, "char_budget": 1500}
        return {"name": "speed profile: ollama-default", "max_tokens": 96, "char_budget": 1200}

    def _load_model_health_cache(self):
        """Load persisted model health map from disk."""
        try:
            if not self._model_health_file.exists():
                return
            with open(self._model_health_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                self._model_health = {
                    str(k): bool(v) if isinstance(v, bool) else None
                    for k, v in data.items()
                }
        except Exception as e:
            self.logger.warning(f"Failed to load model health cache: {e}")

    def _save_model_health_cache(self):
        """Persist model health map to disk."""
        try:
            with open(self._model_health_file, "w", encoding="utf-8") as f:
                json.dump(self._model_health, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.warning(f"Failed to save model health cache: {e}")
    
    def on_status_changed(self, status: str):
        """Handle status change."""
        self.status_bar.showMessage("" if status is None else str(status))
    
    def on_generation_complete(self):
        """Called when generation is complete."""
        # Calculate and store performance metrics
        if hasattr(self, '_generation_start_time') and self._current_generation_model:
            from datetime import datetime
            end_time = datetime.now()
            response_time = (end_time - self._generation_start_time).total_seconds()
            
            # Estimate tokens (rough approximation: 4 characters = 1 token)
            if hasattr(self, '_generation_tokens'):
                tokens = self._generation_tokens
            else:
                # Get the last AI message to estimate tokens
                tokens = 0
                for msg in reversed(self._display_messages):
                    if msg.get("sender") == "AI":
                        tokens = len(msg.get("message", "")) // 4
                        break
            
            # Calculate tokens per second
            tokens_per_second = tokens / response_time if response_time > 0 else 0
            
            # Store performance metrics
            self._model_performance[self._current_generation_model] = {
                'response_time': round(response_time, 2),
                'tokens': tokens,
                'tokens_per_second': round(tokens_per_second, 1),
                'timestamp': end_time.isoformat()
            }
        
        self._streaming_in_progress = False
        self._current_stream_timestamp = None
        self._current_generation_model = None
        self._current_selected_model = None
        self.send_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage("Ready")
        self.current_worker = None

    def create_terminal_session(self, start_shell: bool = True):
        """Create a new embedded terminal tab."""
        self._terminal_counter += 1
        terminal = EmbeddedTerminal(self, working_directory=self._terminal_working_directory)
        tab_name = f"Terminal {self._terminal_counter}"
        index = self.terminal_tabs.addTab(terminal, tab_name)
        self.terminal_tabs.setCurrentIndex(index)
        if start_shell:
            terminal.start_shell()

    def close_current_terminal(self):
        """Close active terminal tab and stop its process."""
        index = self.terminal_tabs.currentIndex()
        if index < 0:
            return
        widget = self.terminal_tabs.widget(index)
        if isinstance(widget, EmbeddedTerminal):
            widget.stop()
        self.terminal_tabs.removeTab(index)
        if self.terminal_tabs.count() == 0:
            self.create_terminal_session(start_shell=False)

    def get_active_terminal(self) -> Optional[EmbeddedTerminal]:
        """Return active embedded terminal widget, if any."""
        widget = self.terminal_tabs.currentWidget()
        if isinstance(widget, EmbeddedTerminal):
            return widget
        return None

    def _on_code_snippet_selected(self, row: int):
        """Update preview when user selects a snippet entry."""
        if row < 0 or row >= len(self._code_snippets):
            self.code_preview.clear()
            self._update_snippet_action_state()
            return
        snippet = self._code_snippets[row]
        self.code_preview.setPlainText(snippet.get("code", ""))
        self._update_snippet_action_state()

    def _on_code_preview_changed(self):
        """Keep selected snippet in sync with user edits in preview/editor box."""
        row = self.code_blocks_list.currentRow()
        if 0 <= row < len(self._code_snippets):
            self._code_snippets[row]["code"] = self.code_preview.toPlainText()
        self._update_snippet_action_state()

    def _on_code_list_selection_changed(self):
        """Refresh action state for selection changes not covered by row-change signals."""
        self._update_snippet_action_state()

    def _get_selected_snippet_text(self) -> str:
        """Return current editable snippet text for the selected row."""
        row = self.code_blocks_list.currentRow()
        if row < 0 or row >= len(self._code_snippets):
            return ""
        edited = self.code_preview.toPlainText()
        if edited is not None:
            return str(edited)
        return str(self._code_snippets[row].get("code", ""))

    def copy_selected_code_snippet(self):
        """Copy selected code snippet to system clipboard."""
        row = self.code_blocks_list.currentRow()
        if row < 0 or row >= len(self._code_snippets):
            self.status_bar.showMessage("Select a snippet to copy")
            return
        QApplication.clipboard().setText(self._get_selected_snippet_text())
        self.status_bar.showMessage("Snippet copied to clipboard")

    def save_selected_code_snippet(self):
        """Save selected code snippet to a file with language-based extension."""
        row = self.code_blocks_list.currentRow()
        if row < 0 or row >= len(self._code_snippets):
            self.status_bar.showMessage("Select a snippet to save")
            return

        snippet = self._code_snippets[row]
        language = snippet.get("language", "text")
        extension = self._language_to_extension(language)

        file_path, _selected = QFileDialog.getSaveFileName(
            self,
            "Save Code Snippet",
            f"snippet_{row + 1}.{extension}",
            "All Files (*.*)"
        )

        if not file_path:
            return

        if "." not in file_path.split("/")[-1]:
            file_path = f"{file_path}.{extension}"

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self._get_selected_snippet_text() + "\n")
            self.status_bar.showMessage(f"Snippet saved to {file_path}")
        except Exception as e:
            self.logger.error(f"Failed to save snippet: {e}")
            QMessageBox.warning(self, "Save Snippet", f"Failed to save snippet: {e}")

    def run_selected_code_snippet(self):
        """Send selected snippet text to currently active terminal tab."""
        row = self.code_blocks_list.currentRow()
        if row < 0 or row >= len(self._code_snippets):
            self.status_bar.showMessage("Select a snippet to run")
            return

        terminal = self.get_active_terminal()
        if terminal is None:
            self.status_bar.showMessage("No terminal available")
            return

        terminal.run_text(self._get_selected_snippet_text())
        self.workspace_tabs.setCurrentWidget(self.terminal_workspace_tab)
        self.status_bar.showMessage("Snippet sent to terminal")

    @staticmethod
    def _extract_fenced_code_blocks(text: str) -> List[Dict[str, str]]:
        """Extract fenced code blocks from markdown text."""
        import re

        if text is None:
            return []

        blocks = []
        pattern = re.compile(r"```([a-zA-Z0-9_+.-]*)\r?\n(.*?)```", re.DOTALL)
        for match in pattern.finditer(str(text)):
            language = (match.group(1) or "text").strip() or "text"
            code = (match.group(2) or "").rstrip()
            if code:
                blocks.append({"language": language, "code": code})
        return blocks

    @staticmethod
    def _extract_fallback_code_block(text: str) -> List[Dict[str, str]]:
        """Best-effort code capture when model output is not fenced markdown."""
        import re

        if text is None:
            return []

        raw_lines = [line.rstrip() for line in str(text).splitlines()]
        lines = [line for line in raw_lines if line.strip()]
        if len(lines) < 2:
            return []

        code_pattern = re.compile(
            r"^\s*(def |class |import |from |if |for |while |return |echo |SELECT |INSERT |UPDATE |DELETE |function |const |let |var |#include )"
        )
        code_like = 0
        for line in lines:
            stripped = line.strip()
            if code_pattern.match(stripped):
                code_like += 1
                continue
            if (
                "(" in stripped and ")" in stripped
                or stripped.endswith(";")
                or "{" in stripped
                or "}" in stripped
                or " = " in stripped
                or stripped.startswith("$")
            ):
                code_like += 1

        if code_like < 2:
            return []

        ratio = code_like / max(len(lines), 1)
        if ratio < 0.4:
            return []

        code = "\n".join(lines).strip()
        language = ChatWindow._guess_code_language(code)
        return [{"language": language, "code": code}]

    @staticmethod
    def _guess_code_language(code: str) -> str:
        """Heuristic language guess for fallback non-fenced code capture."""
        lowered = (code or "").lower()
        if "def " in lowered or "import " in lowered or "print(" in lowered:
            return "python"
        if "echo " in lowered or lowered.startswith("$"):
            return "bash"
        if "select " in lowered or "insert " in lowered or "update " in lowered:
            return "sql"
        if "function " in lowered or "const " in lowered or "let " in lowered:
            return "javascript"
        return "text"

    @staticmethod
    def _language_to_extension(language: str) -> str:
        """Map markdown fence language to a practical filename extension."""
        mapping = {
            "python": "py",
            "py": "py",
            "javascript": "js",
            "js": "js",
            "typescript": "ts",
            "ts": "ts",
            "c": "c",
            "cpp": "cpp",
            "c++": "cpp",
            "java": "java",
            "go": "go",
            "rust": "rs",
            "rs": "rs",
            "php": "php",
            "ruby": "rb",
            "rb": "rb",
            "kotlin": "kt",
            "swift": "swift",
            "bash": "sh",
            "sh": "sh",
            "shell": "sh",
            "zsh": "zsh",
            "json": "json",
            "yaml": "yaml",
            "yml": "yml",
            "html": "html",
            "css": "css",
            "xml": "xml",
            "sql": "sql",
            "markdown": "md",
            "md": "md",
            "text": "txt",
        }
        lowered = (language or "text").strip().lower()
        return mapping.get(lowered, "txt")

    def register_code_blocks_from_ai_response(self, response_text: str):
        """Persist code blocks from AI responses for copy/run workflows."""
        from datetime import datetime

        blocks = self._extract_fenced_code_blocks(response_text)
        if not blocks:
            blocks = self._extract_fallback_code_block(response_text)
        if not blocks:
            return

        timestamp = datetime.now().strftime("%H:%M:%S")
        for block in blocks:
            self._code_snippets.append(
                {
                    "language": block.get("language", "text"),
                    "code": block.get("code", ""),
                    "timestamp": timestamp,
                }
            )

        self._refresh_code_snippets_list()
        self.status_bar.showMessage(f"Captured {len(blocks)} code snippet(s)")

    def _refresh_code_snippets_list(self):
        """Refresh list widget with current captured snippets."""
        self.code_blocks_list.clear()
        for index, snippet in enumerate(self._code_snippets, start=1):
            language = snippet.get("language", "text")
            stamp = snippet.get("timestamp", "")
            label = f"{index}. [{language}] {stamp}".strip()
            self.code_blocks_list.addItem(QListWidgetItem(label))

        if self._code_snippets:
            self.code_blocks_list.setCurrentRow(len(self._code_snippets) - 1)
            self._update_snippet_action_state()
        else:
            self._update_snippet_action_state()

    def _update_snippet_action_state(self):
        """Enable snippet action buttons only when a valid snippet is selected."""
        selected_row = self.code_blocks_list.currentRow()
        has_selection = 0 <= selected_row < len(self._code_snippets)
        
        # Ensure buttons exist before setting state
        if hasattr(self, 'copy_code_button'):
            self.copy_code_button.setEnabled(has_selection)
        if hasattr(self, 'save_code_button'):
            self.save_code_button.setEnabled(has_selection)
        if hasattr(self, 'run_code_button'):
            self.run_code_button.setEnabled(has_selection)

    def _append_display_message(self, sender: str, message: str, timestamp: Optional[str] = None):
        """Store a canonical message record used to re-render the chat display."""
        from datetime import datetime

        entry = {
            "sender": "" if sender is None else str(sender),
            "message": "" if message is None else str(message),
            "timestamp": timestamp or datetime.now().strftime("%H:%M:%S"),
            "model_info": self._get_model_info() if sender == "AI" else ""
        }
        self._display_messages.append(entry)
        return entry

    def _render_display_messages(self):
        """Re-render all stored display messages using current timestamp preference."""
        lines = []
        show_timestamps = bool(self.settings.ui.show_timestamps)
        show_model_info = bool(self.settings.ui.show_model_info)
        
        for entry in self._display_messages:
            sender = entry.get("sender", "")
            message = entry.get("message", "")
            timestamp = entry.get("timestamp", "")
            model_info = entry.get("model_info", "")
            
            # Build the message line
            if show_timestamps and timestamp:
                base_line = f"[{timestamp}] {sender}: {message}"
            else:
                base_line = f"{sender}: {message}"
            
            # Add model info if enabled and available
            if show_model_info and model_info and sender == "AI":
                base_line += f"\n📊 {model_info}"
            
            lines.append(base_line)

        self.chat_display.setPlainText("\n".join(lines))
        if self.settings.ui.auto_scroll:
            cursor = self.chat_display.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.chat_display.setTextCursor(cursor)
            self.chat_display.ensureCursorVisible()
    
    def _get_model_info(self) -> str:
        """Get detailed information about the current model."""
        try:
            if not self._current_selected_model:
                return "No model selected"
            
            # Parse model string (provider/model)
            if "/" in self._current_selected_model:
                provider, model_name = self._current_selected_model.split("/", 1)
            else:
                provider = "unknown"
                model_name = self._current_selected_model
            
            # Get basic model info
            info_parts = [f"Model: {model_name}", f"Provider: {provider}"]
            
            # Add provider-specific info
            if provider.lower() == "openai":
                info_parts.extend(self._get_openai_model_info(model_name))
            elif provider.lower() == "ollama":
                info_parts.extend(self._get_ollama_model_info(model_name))
            elif provider.lower() == "groq":
                info_parts.extend(self._get_groq_model_info(model_name))
            elif provider.lower() == "huggingface":
                info_parts.extend(self._get_huggingface_model_info(model_name))
            elif provider.lower() == "openrouter":
                info_parts.extend(self._get_openrouter_model_info(model_name))
            else:
                info_parts.append("Provider: Unknown")
            
            # Add real-time health status
            health_key = self._current_selected_model
            if health_key in self._model_health:
                status = "✅ Healthy" if self._model_health[health_key] else "⚠️ Unhealthy"
                info_parts.append(f"Status: {status}")
            
            # Add performance metrics if available
            if hasattr(self, '_model_performance') and health_key in self._model_performance:
                perf = self._model_performance[health_key]
                if 'response_time' in perf:
                    info_parts.append(f"Response: {perf['response_time']}s")
                if 'tokens_per_second' in perf:
                    info_parts.append(f"Speed: {perf['tokens_per_second']} t/s")
            
            # Add context window info
            context_info = self._get_context_window_info(provider, model_name)
            if context_info:
                info_parts.append(f"Context: {context_info}")
            
            # Add cost information for cloud models
            if provider.lower() in ["openai", "groq", "openrouter"]:
                cost_info = self._get_cost_info(provider, model_name)
                if cost_info:
                    info_parts.append(f"Cost: {cost_info}")
            
            return " | ".join(info_parts)
            
        except Exception as e:
            self.logger.debug(f"Failed to get model info: {e}")
            return f"Model: {self._current_selected_model or 'Unknown'}"
    
    def _get_openai_model_info(self, model_name: str) -> List[str]:
        """Get OpenAI model information."""
        info = []
        
        # Model size/capability based on name
        if "gpt-4" in model_name:
            if "turbo" in model_name:
                info.append("Size: Large (GPT-4 Turbo)")
                info.append("Speed: Fast")
            elif "32k" in model_name:
                info.append("Context: 32K tokens")
            elif "vision" in model_name:
                info.append("Capability: Vision")
            else:
                info.append("Size: Large (GPT-4)")
        elif "gpt-3.5" in model_name:
            info.append("Size: Medium (GPT-3.5)")
            info.append("Speed: Fast")
        elif "davinci" in model_name:
            info.append("Size: Large (Davinci)")
            info.append("Legacy: Yes")
        elif "babbage" in model_name:
            info.append("Size: Small (Babbage)")
            info.append("Legacy: Yes")
        elif "curie" in model_name:
            info.append("Size: Medium (Curie)")
            info.append("Legacy: Yes")
        else:
            info.append("Size: Unknown")
        
        return info
    
    def _get_ollama_model_info(self, model_name: str) -> List[str]:
        """Get Ollama model information."""
        info = []
        
        # Extract size from model name
        if "1b" in model_name.lower():
            info.append("Size: Tiny (1B parameters)")
        elif "3b" in model_name.lower():
            info.append("Size: Small (3B parameters)")
        elif "7b" in model_name.lower():
            info.append("Size: Medium (7B parameters)")
        elif "13b" in model_name.lower():
            info.append("Size: Large (13B parameters)")
        elif "34b" in model_name.lower():
            info.append("Size: Very Large (34B parameters)")
        elif "70b" in model_name.lower():
            info.append("Size: Huge (70B parameters)")
        else:
            info.append("Size: Unknown")
        
        # Model family
        if "llama" in model_name.lower():
            info.append("Family: Llama")
        elif "mistral" in model_name.lower():
            info.append("Family: Mistral")
        elif "qwen" in model_name.lower():
            info.append("Family: Qwen")
        elif "codellama" in model_name.lower():
            info.append("Family: CodeLlama")
            info.append("Specialty: Code")
        else:
            info.append("Family: Unknown")
        
        # Special capabilities
        if "instruct" in model_name.lower():
            info.append("Type: Instruction-tuned")
        if "chat" in model_name.lower():
            info.append("Type: Chat")
        
        info.append("Hosting: Local")
        return info
    
    def _get_groq_model_info(self, model_name: str) -> List[str]:
        """Get Groq model information."""
        info = []
        
        if "llama" in model_name.lower():
            info.append("Family: Llama")
            if "70b" in model_name.lower():
                info.append("Size: Large (70B)")
            elif "8b" in model_name.lower():
                info.append("Size: Small (8B)")
        elif "mixtral" in model_name.lower():
            info.append("Family: Mixtral")
            info.append("Size: Large")
        elif "gemma" in model_name.lower():
            info.append("Family: Gemma")
            if "7b" in model_name.lower():
                info.append("Size: Medium (7B)")
        
        info.append("Speed: Ultra-fast")
        info.append("Hosting: Groq Cloud")
        return info
    
    def _get_huggingface_model_info(self, model_name: str) -> List[str]:
        """Get HuggingFace model information."""
        info = []
        
        # Common model patterns
        if "bert" in model_name.lower():
            info.append("Family: BERT")
            info.append("Type: Encoder-only")
        elif "gpt" in model_name.lower():
            info.append("Family: GPT")
            info.append("Type: Decoder-only")
        elif "t5" in model_name.lower():
            info.append("Family: T5")
            info.append("Type: Encoder-decoder")
        elif "distil" in model_name.lower():
            info.append("Optimization: Distilled")
        else:
            info.append("Family: Unknown")
        
        info.append("Hosting: HuggingFace")
        return info
    
    def _get_openrouter_model_info(self, model_name: str) -> List[str]:
        """Get OpenRouter model information."""
        info = []
        
        # OpenRouter provides access to many models
        if "anthropic" in model_name.lower() or "claude" in model_name.lower():
            info.append("Provider: Anthropic")
        elif "google" in model_name.lower() or "gemini" in model_name.lower():
            info.append("Provider: Google")
        elif "meta" in model_name.lower() or "llama" in model_name.lower():
            info.append("Provider: Meta")
        elif "mistral" in model_name.lower():
            info.append("Provider: Mistral AI")
        else:
            info.append("Provider: Various")
        
        info.append("Hosting: OpenRouter")
        return info
    
    def _get_context_window_info(self, provider: str, model_name: str) -> str:
        """Get context window information for a model."""
        try:
            # Known context windows for popular models
            context_windows = {
                # OpenAI
                "openai/gpt-4": "8K",
                "openai/gpt-4-32k": "32K", 
                "openai/gpt-4-turbo": "128K",
                "openai/gpt-4-turbo-128k": "128K",
                "openai/gpt-3.5-turbo": "4K",
                "openai/gpt-3.5-turbo-16k": "16K",
                
                # Ollama models (approximate)
                "ollama/llama3.2:1b": "128K",
                "ollama/llama3.2:3b": "128K", 
                "ollama/llama3:1b": "4K",
                "ollama/llama3:8b": "8K",
                "ollama/llama3:70b": "4K",
                "ollama/mistral:7b": "8K",
                "ollama/qwen2.5:3b": "32K",
                "ollama/qwen2.5:7b": "32K",
                "ollama/phi3.5:3.8b": "4K",
                
                # Groq
                "groq/llama2-70b-4096": "4K",
                "groq/mixtral-8x7b-32768": "32K",
                "groq/gemma-7b-it": "8K",
            }
            
            key = f"{provider.lower()}/{model_name.lower()}"
            for model_key, context in context_windows.items():
                if model_key in key or key in model_key:
                    return context
            
            # Try to extract from model name
            if "32k" in model_name.lower():
                return "32K"
            elif "16k" in model_name.lower():
                return "16K"
            elif "8k" in model_name.lower():
                return "8K"
            elif "4k" in model_name.lower():
                return "4K"
            elif "128k" in model_name.lower():
                return "128K"
            
            return "Unknown"
            
        except Exception as e:
            self.logger.debug(f"Failed to get context info: {e}")
            return "Unknown"
    
    def _get_cost_info(self, provider: str, model_name: str) -> str:
        """Get cost information for cloud models."""
        try:
            # Approximate costs per 1M tokens (input/output)
            costs = {
                # OpenAI
                "openai/gpt-4": "$10/$30",
                "openai/gpt-4-turbo": "$10/$30", 
                "openai/gpt-3.5-turbo": "$0.50/$1.50",
                
                # Groq (usually free tier with limits)
                "groq/llama2-70b-4096": "Free tier",
                "groq/mixtral-8x7b-32768": "Free tier",
                "groq/gemma-7b-it": "Free tier",
                
                # OpenRouter (varies by model)
                "openrouter/": "Various",
            }
            
            key = f"{provider.lower()}/{model_name.lower()}"
            for model_key, cost in costs.items():
                if model_key in key:
                    return cost
            
            return "Check provider"
            
        except Exception as e:
            self.logger.debug(f"Failed to get cost info: {e}")
            return "Unknown"
    
    def toggle_search(self):
        """Toggle search visibility."""
        if self.search_toolbar.isVisible():
            self.close_search()
        else:
            self.open_search()
    
    def open_search(self):
        """Open search toolbar."""
        self.search_toolbar.setVisible(True)
        self.search_input.setFocus()
        self.search_input.selectAll()
    
    def close_search(self):
        """Close search toolbar."""
        self.search_toolbar.setVisible(False)
        self.chat_display.setFocus()
        self._clear_search_highlight()
    
    def search_next(self):
        """Search for next occurrence."""
        self._perform_search(forward=True)
    
    def search_previous(self):
        """Search for previous occurrence."""
        self._perform_search(forward=False)
    
    def _perform_search(self, forward: bool = True):
        """Perform search with highlighting."""
        search_text = self.search_input.text().strip()
        if not search_text:
            self._update_search_results(0, 0)
            return
        
        # Get search options
        case_sensitive = self.search_case_sensitive.isChecked()
        whole_words = self.search_whole_words.isChecked()
        
        # Configure QTextDocument search flags
        flags = QTextDocument.FindFlag(0)
        if case_sensitive:
            flags |= QTextDocument.FindFlag.FindCaseSensitively
        if whole_words:
            flags |= QTextDocument.FindFlag.FindWholeWords
        
        # Get cursor
        cursor = self.chat_display.textCursor()
        
        # Perform search
        if forward:
            found_cursor = self.chat_display.document().find(search_text, cursor, flags)
        else:
            # Search backward
            cursor.movePosition(cursor.MoveOperation.Start)
            found_cursor = self.chat_display.document().find(search_text, cursor, flags)
        
        if found_cursor.isNull():
            # Wrap around
            if forward:
                cursor.movePosition(cursor.MoveOperation.Start)
            else:
                cursor.movePosition(cursor.MoveOperation.End)
            found_cursor = self.chat_display.document().find(search_text, cursor, flags)
        
        if not found_cursor.isNull():
            self.chat_display.setTextCursor(found_cursor)
            self._update_search_results(1, 1)  # For simplicity, show current match
        else:
            self._update_search_results(0, 0)
    
    def _clear_search_highlight(self):
        """Clear search highlighting."""
        cursor = self.chat_display.textCursor()
        cursor.movePosition(cursor.MoveOperation.Start)
        cursor.select(cursor.SelectionType.Document)
        format = cursor.charFormat()
        format.setBackground(QColor("transparent"))
        cursor.mergeCharFormat(format)
        self.chat_display.setTextCursor(cursor)
    
    def _update_search_results(self, current: int, total: int):
        """Update search results label."""
        if total == 0:
            self.search_results_label.setText("No results")
        elif total == 1:
            self.search_results_label.setText("1 result")
        else:
            self.search_results_label.setText(f"{current}/{total} results")
    
    def add_message(self, sender: str, message: str):
        """Add a message to the chat display."""
        entry = self._append_display_message(sender, message)
        if self.settings.ui.show_timestamps:
            self.chat_display.append(f"[{entry['timestamp']}] {entry['sender']}: {entry['message']}")
        else:
            self.chat_display.append(f"{entry['sender']}: {entry['message']}")
        
        if self.settings.ui.auto_scroll:
            self.chat_display.ensureCursorVisible()
    
    def clear_chat(self):
        """Clear the chat display."""
        self.chat_display.clear()
        self.current_messages = []
        self._display_messages = []
        self._code_snippets = []
        if hasattr(self, "code_blocks_list"):
            self.code_blocks_list.clear()
    
    def copy_chat(self):
        """Copy the entire chat content to clipboard."""
        chat_text = self.chat_display.toPlainText()
        if chat_text.strip():
            QApplication.clipboard().setText(chat_text)
            self.status_bar.showMessage("Chat copied to clipboard", 3000)
        else:
            self.status_bar.showMessage("No chat content to copy", 3000)
    
    def export_chat(self):
        """Export chat history."""
        if not self._display_messages:
            QMessageBox.information(self, "Export Chat", "There are no messages to export yet.")
            return

        from datetime import datetime

        default_name = f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export Chat",
            default_name,
            "Text Files (*.txt);;Markdown Files (*.md);;JSON Files (*.json)"
        )

        if not file_path:
            return

        # Ensure extension matches selected filter when user omits it.
        if "." not in file_path.split("/")[-1]:
            if "*.md" in selected_filter:
                file_path += ".md"
            elif "*.json" in selected_filter:
                file_path += ".json"
            else:
                file_path += ".txt"

        try:
            is_json = file_path.lower().endswith(".json")
            is_markdown = file_path.lower().endswith(".md")

            if is_json:
                payload = {
                    "exported_at": datetime.now().isoformat(),
                    "message_count": len(self._display_messages),
                    "messages": self._display_messages,
                }
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(payload, f, indent=2, ensure_ascii=False)
            else:
                lines = []
                if is_markdown:
                    lines.append("# Chat Export")
                    lines.append("")
                    lines.append(f"Exported at: {datetime.now().isoformat()}")
                    lines.append("")

                for entry in self._display_messages:
                    timestamp = entry.get("timestamp", "")
                    sender = entry.get("sender", "")
                    message = entry.get("message", "")

                    if is_markdown:
                        header = f"[{timestamp}] **{sender}**" if timestamp else f"**{sender}**"
                        lines.append(header)
                        lines.append("")
                        lines.append(str(message))
                        lines.append("")
                    else:
                        if timestamp:
                            lines.append(f"[{timestamp}] {sender}: {message}")
                        else:
                            lines.append(f"{sender}: {message}")

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(lines).rstrip() + "\n")

            QMessageBox.information(self, "Export Chat", f"Chat exported successfully to:\n{file_path}")
        except Exception as e:
            self.logger.error(f"Failed to export chat: {e}")
            QMessageBox.warning(self, "Export Chat", f"Failed to export chat: {e}")
    
    def toggle_timestamps(self):
        """Toggle timestamp display."""
        if self._streaming_in_progress:
            # Keep active stream output stable; apply changes after generation completes.
            self.timestamp_action.setChecked(self.settings.ui.show_timestamps)
            QMessageBox.information(self, "Timestamps", "Finish the current generation before toggling timestamps.")
            return

        self.settings.update_ui_config(show_timestamps=self.timestamp_action.isChecked())
        self._render_display_messages()
    
    def toggle_model_info(self):
        """Toggle model info display."""
        self.settings.update_ui_config(show_model_info=self.model_info_action.isChecked())
    
    def open_settings(self, default_tab: str = "Providers"):
        """Open settings dialog - alias for show_provider_settings."""
        self.show_provider_settings(default_tab)
    
    def show_provider_settings(self, default_tab: str = "Providers"):
        """Show provider configuration dialog."""
        try:
            dialog = SettingsDialog(self.settings, self, default_tab=default_tab)
            dialog.settings_changed.connect(self.on_settings_changed)
            dialog.exec()
        except Exception as e:
            self.logger.error(f"Failed to open settings dialog: {e}")
            QMessageBox.warning(self, "Error", f"Failed to open settings dialog: {e}")
    
    def on_settings_changed(self):
        """Handle settings changes."""
        try:
            # Reapply runtime UI settings from persisted config.
            self.load_settings()

            # Reapply theme if it changed
            self.apply_theme()
            
            # Update UI components based on new settings
            self.timestamp_action.setChecked(self.settings.ui.show_timestamps)
            self.model_info_action.setChecked(self.settings.ui.show_model_info)
            self.filter_all_providers_action.setChecked(self.provider_filter_mode == "all")
            self.filter_enabled_providers_action.setChecked(self.provider_filter_mode == "enabled")
            self.filter_available_providers_action.setChecked(self.provider_filter_mode == "available")
            self._render_display_messages()
            self.fast_local_models_action.setChecked(self.prefer_fast_local_models)
            
            # Reinitialize providers and refresh model list immediately.
            self.init_providers_sync()
            # The model combo and status label are already updated by init_providers_sync via update_model_list_ui
            
            self.logger.info("Settings applied successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to apply settings: {e}")
    
    def run_system_check(self):
        """Run system check and show results."""
        if self.system_check_worker and self.system_check_worker.isRunning():
            self.status_bar.showMessage("System check is already running...")
            return

        self.status_bar.showMessage("Running system check...")
        self.system_check_worker = SystemCheckWorker()
        self.system_check_worker.report_ready.connect(self.on_system_check_complete)
        self.system_check_worker.error_occurred.connect(self.on_system_check_error)
        self.system_check_worker.finished.connect(self.on_system_check_finished)
        self.system_check_worker.start()

    def on_system_check_complete(self, report: str):
        """Handle successful completion of system checks."""
        self.status_bar.showMessage("System check completed")
        self._show_system_check_dialog(report)
    
    def _show_system_check_dialog(self, report: str):
        """Show enhanced system check dialog with remediation options."""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QLabel, QScrollArea
        
        dialog = QDialog(self)
        dialog.setWindowTitle("System Check Results")
        dialog.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(dialog)
        
        # Title
        title_label = QLabel("System Check Results")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Create scrollable area for report
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(400)
        
        report_widget = QWidget()
        report_layout = QVBoxLayout(report_widget)
        
        # Report text
        report_text = QTextEdit()
        report_text.setPlainText(report)
        report_text.setReadOnly(True)
        report_text.setMaximumHeight(300)
        report_layout.addWidget(report_text)
        
        # Remediation section
        remediation_label = QLabel("Remediation Actions:")
        remediation_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 10px;")
        report_layout.addWidget(remediation_label)
        
        remediation_text = QTextEdit()
        remediation_text.setPlainText(self._generate_remediation_advice())
        remediation_text.setReadOnly(True)
        remediation_text.setMaximumHeight(200)
        report_layout.addWidget(remediation_text)
        
        scroll_area.setWidget(report_widget)
        layout.addWidget(scroll_area)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        # Common remediation actions
        install_deps_btn = QPushButton("Install Missing Dependencies")
        install_deps_btn.clicked.connect(lambda: self._install_dependencies(dialog))
        button_layout.addWidget(install_deps_btn)
        
        start_ollama_btn = QPushButton("Start Ollama Service")
        start_ollama_btn.clicked.connect(lambda: self._start_ollama_service(dialog))
        button_layout.addWidget(start_ollama_btn)
        
        fix_permissions_btn = QPushButton("Fix Permissions")
        fix_permissions_btn.clicked.connect(lambda: self._fix_permissions(dialog))
        button_layout.addWidget(fix_permissions_btn)
        
        check_config_btn = QPushButton("Check Configuration")
        check_config_btn.clicked.connect(lambda: self._check_configuration(dialog))
        button_layout.addWidget(check_config_btn)
        
        refresh_btn = QPushButton("Refresh Check")
        refresh_btn.clicked.connect(lambda: self._refresh_system_check(dialog))
        button_layout.addWidget(refresh_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    def _generate_remediation_advice(self) -> str:
        """Generate remediation advice based on common issues."""
        advice = """
COMMON REMEDIATION STEPS:

1. Missing Dependencies:
   • Run: pip install -r requirements.txt
   • Or: pip install PyQt6 aiohttp cryptography psutil markdown jsonschema rich
   • Ensure virtual environment is activated

2. Network Issues:
   • Check internet connection
   • Verify firewall settings
   • Test API key validity in Settings > Configure Providers

3. Provider Configuration:
   • Open Settings > Configure Providers
   • Enter valid API keys for each provider
   • Test provider connectivity

4. Performance Issues:
   • Close unnecessary applications
   • Check available disk space
   • Restart application if needed

5. File Permissions:
   • Ensure write permissions for config directory
   • Check ~/.local/share/chat-linux-client/ directory
   • Run with appropriate user permissions

AUTOMATED FIXES:
• Click "Install Missing Dependencies" to auto-install packages
• Click "Check Configuration" to verify settings
• Click "Refresh Check" to re-run system checks

For more help, check the documentation or report issues on GitHub.
"""
        return advice
    
    def _install_dependencies(self, parent_dialog):
        """Install missing dependencies."""
        try:
            self.status_bar.showMessage("Installing dependencies...")
            
            # Run pip install in background
            import subprocess
            import sys
            
            requirements_file = os.path.join(os.path.dirname(__file__), "..", "requirements.txt")
            
            if os.path.exists(requirements_file):
                cmd = [sys.executable, "-m", "pip", "install", "-r", requirements_file]
            else:
                cmd = [sys.executable, "-m", "pip", "install", 
                      "PyQt6", "aiohttp", "cryptography", "psutil", "markdown", "jsonschema", "rich"]
            
            # Run in background thread to avoid blocking UI
            from PyQt6.QtCore import QThread
            
            class InstallThread(QThread):
                def __init__(self, command):
                    super().__init__()
                    self.command = command
                
                def run(self):
                    try:
                        result = subprocess.run(self.command, capture_output=True, text=True, timeout=300)
                        self.result = result.returncode == 0
                        self.output = result.stdout + result.stderr
                    except Exception as e:
                        self.result = False
                        self.output = str(e)
            
            install_thread = InstallThread(cmd)
            install_thread.finished.connect(
                lambda: self._on_install_complete(install_thread, parent_dialog)
            )
            install_thread.start()
            
            QMessageBox.information(parent_dialog, "Installation Started", 
                                 "Dependency installation started in background. Check status bar for progress.")
            
        except Exception as e:
            QMessageBox.critical(parent_dialog, "Error", f"Failed to start installation: {e}")
    
    def _on_install_complete(self, thread: QThread, parent_dialog):
        """Handle completion of dependency installation."""
        try:
            if hasattr(thread, 'result') and thread.result:
                QMessageBox.information(parent_dialog, "Installation Complete", 
                                     "Dependencies installed successfully! Please restart the application.")
            else:
                error_msg = getattr(thread, 'output', 'Unknown error')
                QMessageBox.warning(parent_dialog, "Installation Failed", 
                                f"Installation failed: {error_msg}")
        except Exception as e:
            self.logger.error(f"Error handling install completion: {e}")
    
    def _check_configuration(self, parent_dialog):
        """Check application configuration."""
        try:
            issues = []
            
            # Check settings file
            config_file = os.path.expanduser("~/.config/chat-linux-client/config.json")
            if not os.path.exists(config_file):
                issues.append("Configuration file not found - will be created on first run")
            
            # Check API keys
            has_keys = False
            for provider_name in ["openai", "groq", "huggingface", "openrouter"]:
                key = self.key_handler.get_key(provider_name)
                if key:
                    has_keys = True
                    break
            
            if not has_keys:
                issues.append("No API keys configured - configure in Settings > Configure Providers")
            
            # Check directories
            data_dir = os.path.expanduser("~/.local/share/chat-linux-client")
            if not os.path.exists(data_dir):
                issues.append("Data directory not found - will be created automatically")
            
            if issues:
                QMessageBox.information(parent_dialog, "Configuration Issues", 
                                     "\n".join(f"• {issue}" for issue in issues))
            else:
                QMessageBox.information(parent_dialog, "Configuration OK", 
                                     "Configuration appears to be correct!")
                
        except Exception as e:
            QMessageBox.critical(parent_dialog, "Error", f"Failed to check configuration: {e}")
    
    def _start_ollama_service(self, parent_dialog):
        """Start Ollama service with one-click fix."""
        try:
            self.status_bar.showMessage("Starting Ollama service...")
            
            # Check if ollama is installed
            import subprocess
            import shutil
            
            if not shutil.which("ollama"):
                # Try to add to PATH and check again
                ollama_path = os.path.expanduser("~/.local/bin/ollama")
                if os.path.exists(ollama_path):
                    ollama_cmd = ollama_path
                else:
                    QMessageBox.warning(parent_dialog, "Ollama Not Found", 
                                      "Ollama is not installed. Please install it first:\n"
                                      "curl -fsSL https://ollama.com/install.sh | sh")
                    return
            else:
                ollama_cmd = "ollama"
            
            # Start ollama in background
            cmd = [ollama_cmd, "serve"]
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Wait a moment and check if it's running
            import time
            time.sleep(2)
            
            # Test if ollama is responding
            try:
                import requests
                response = requests.get("http://localhost:11434/api/version", timeout=5)
                if response.status_code == 200:
                    self.status_bar.showMessage("Ollama service started successfully")
                    QMessageBox.information(parent_dialog, "Success", 
                                          "Ollama service has been started successfully!\n"
                                          "You can now use local AI models.")
                else:
                    QMessageBox.warning(parent_dialog, "Warning", 
                                      "Ollama started but not responding properly.")
            except:
                QMessageBox.warning(parent_dialog, "Warning", 
                                  "Ollama started but may not be responding yet.\n"
                                  "Please wait a moment and try again.")
                
        except Exception as e:
            self.logger.error(f"Failed to start Ollama service: {e}")
            QMessageBox.critical(parent_dialog, "Error", f"Failed to start Ollama service: {e}")
    
    def _fix_permissions(self, parent_dialog):
        """Fix common permission issues with one-click fix."""
        try:
            self.status_bar.showMessage("Fixing permissions...")
            
            import subprocess
            import os
            
            # Fix virtual environment permissions
            venv_path = os.path.join(os.path.dirname(__file__), "..", "venv")
            if os.path.exists(venv_path):
                subprocess.run(["chmod", "-R", "u+rw", venv_path], capture_output=True)
                subprocess.run(["chmod", "+x", os.path.join(venv_path, "bin", "activate")], 
                             capture_output=True)
            
            # Fix config directory permissions
            config_dir = os.path.expanduser("~/.config/chat-linux-client")
            os.makedirs(config_dir, exist_ok=True)
            subprocess.run(["chmod", "u+rw", config_dir], capture_output=True)
            
            # Fix data directory permissions
            data_dir = os.path.expanduser("~/.local/share/chat-linux-client")
            os.makedirs(data_dir, exist_ok=True)
            subprocess.run(["chmod", "-R", "u+rw", data_dir], capture_output=True)
            
            self.status_bar.showMessage("Permissions fixed successfully")
            QMessageBox.information(parent_dialog, "Success", 
                                  "Permissions have been fixed for:\n"
                                  "• Virtual environment\n"
                                  "• Configuration directory\n"
                                  "• Data storage directory\n\n"
                                  "Please restart the application if you encounter issues.")
            
        except Exception as e:
            self.logger.error(f"Failed to fix permissions: {e}")
            QMessageBox.critical(parent_dialog, "Error", f"Failed to fix permissions: {e}")
    
    def _refresh_system_check(self, parent_dialog):
        """Refresh system check."""
        parent_dialog.accept()
        self.run_system_check()
    
    def update_provider_health_status(self):
        """Update provider health status in status bar."""
        try:
            if not hasattr(self, 'router') or not self.router:
                self.health_label.setText("🔍 Not initialized")
                self.health_label.setToolTip("Router not initialized")
                return
            
            # Count providers by status
            total_providers = len(self.router.providers)
            available_providers = sum(
                1 for provider in self.router.providers.values() 
                if getattr(provider, 'is_available', False)
            )
            healthy_providers = 0
            unhealthy_providers = 0
            
            # Build detailed tooltip information
            tooltip_details = []
            tooltip_details.append(f"Total Providers: {total_providers}")
            tooltip_details.append(f"Available: {available_providers}")
            
            # Check model health for each provider
            for provider_name, provider in self.router.providers.items():
                provider_status = "✅ Available" if getattr(provider, 'is_available', False) else "❌ Unavailable"
                tooltip_details.append(f"\n{provider_name}: {provider_status}")
                
                if getattr(provider, 'is_available', False):
                    # Count models for this provider
                    provider_models = [
                        key for key in self._model_health.keys() 
                        if key.startswith(f"{provider_name}/")
                    ]
                    healthy_models = sum(
                        1 for model in provider_models 
                        if self._model_health.get(model, True)
                    )
                    
                    tooltip_details.append(f"  Models: {len(provider_models)} ({healthy_models} healthy)")
                    
                    # Check if any models for this provider are healthy
                    provider_models_healthy = any(
                        key.startswith(f"{provider_name}/") and self._model_health.get(key, True)
                        for key in self._model_health.keys()
                    )
                    if provider_models_healthy:
                        healthy_providers += 1
                    else:
                        unhealthy_providers += 1
                else:
                    tooltip_details.append(f"  Models: Not accessible")
            
            # Update tooltip
            self.health_label.setToolTip("\n".join(tooltip_details))
            
            # Update status display
            if available_providers == 0:
                self.health_label.setText("❌ No providers")
                self.health_label.setStyleSheet("color: #d32f2f; font-size: 11px; padding: 2px 8px;")
            elif unhealthy_providers > 0:
                self.health_label.setText(f"⚠️ {healthy_providers}/{available_providers} healthy")
                self.health_label.setStyleSheet("color: #f57c00; font-size: 11px; padding: 2px 8px;")
            else:
                self.health_label.setText(f"✅ {available_providers} providers")
                self.health_label.setStyleSheet("color: #388e3c; font-size: 11px; padding: 2px 8px;")
                
        except Exception as e:
            self.logger.debug(f"Failed to update provider health status: {e}")
            self.health_label.setText("❓ Unknown")
            self.health_label.setStyleSheet("color: #666; font-size: 11px; padding: 2px 8px;")
            self.health_label.setToolTip(f"Error checking health: {str(e)}")

    def on_system_check_error(self, error_message: str):
        """Handle system check errors."""
        self.status_bar.showMessage("System check failed")
        self.logger.error(f"System check failed: {error_message}")
        QMessageBox.warning(self, "Error", f"System check failed: {error_message}")

    def on_system_check_finished(self):
        """Cleanup after system check worker finishes."""
        self.system_check_worker = None
    
    def show_health_dashboard(self):
        """Show provider health monitoring dashboard."""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, QScrollArea, QFrame, QGridLayout, QGroupBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Provider Health Dashboard")
        dialog.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(dialog)
        
        # Title
        title_label = QLabel("Provider Health Monitoring Dashboard")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # Main content area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(500)
        
        dashboard_widget = QWidget()
        dashboard_layout = QVBoxLayout(dashboard_widget)
        
        # Overall status section
        status_group = QGroupBox("Overall Status")
        status_layout = QGridLayout(status_group)
        
        if hasattr(self, 'router') and self.router:
            total_providers = len(self.router.providers)
            available_providers = sum(
                1 for provider in self.router.providers.values() 
                if getattr(provider, 'is_available', False)
            )
            healthy_providers = sum(
                1 for provider_name, provider in self.router.providers.items()
                if getattr(provider, 'is_available', False) and any(
                    key.startswith(f"{provider_name}/") and self._model_health.get(key, True)
                    for key in self._model_health.keys()
                )
            )
            
            status_layout.addWidget(QLabel("Total Providers:"), 0, 0)
            status_layout.addWidget(QLabel(str(total_providers)), 0, 1)
            status_layout.addWidget(QLabel("Available:"), 1, 0)
            status_layout.addWidget(QLabel(str(available_providers)), 1, 1)
            status_layout.addWidget(QLabel("Healthy:"), 2, 0)
            status_layout.addWidget(QLabel(str(healthy_providers)), 2, 1)
        else:
            status_layout.addWidget(QLabel("Status:"), 0, 0)
            status_layout.addWidget(QLabel("Router not initialized"), 0, 1)
        
        dashboard_layout.addWidget(status_group)
        
        # Provider details section
        providers_group = QGroupBox("Provider Details")
        providers_layout = QVBoxLayout(providers_group)
        
        if hasattr(self, 'router') and self.router:
            for provider_name, provider in self.router.providers.items():
                provider_frame = QFrame()
                provider_frame.setFrameStyle(QFrame.Shape.Box)
                provider_layout = QGridLayout(provider_frame)
                
                # Provider name and status
                status = "✅ Available" if getattr(provider, 'is_available', False) else "❌ Unavailable"
                provider_layout.addWidget(QLabel(f"<b>{provider_name}</b>"), 0, 0)
                provider_layout.addWidget(QLabel(status), 0, 1)
                
                if getattr(provider, 'is_available', False):
                    # Model count
                    provider_models = [
                        key for key in self._model_health.keys() 
                        if key.startswith(f"{provider_name}/")
                    ]
                    healthy_models = sum(
                        1 for model in provider_models 
                        if self._model_health.get(model, True)
                    )
                    
                    provider_layout.addWidget(QLabel("Models:"), 1, 0)
                    provider_layout.addWidget(QLabel(f"{len(provider_models)} ({healthy_models} healthy)"), 1, 1)
                    
                    # Model list
                    if provider_models:
                        model_list_text = "\n".join(
                            f"  {'✅' if self._model_health.get(model, True) else '❌'} {model.split('/', 1)[1]}"
                            for model in provider_models[:10]
                        )
                        if len(provider_models) > 10:
                            model_list_text += f"\n  ... and {len(provider_models) - 10} more"
                        
                        model_text = QTextEdit()
                        model_text.setPlainText(model_list_text)
                        model_text.setReadOnly(True)
                        model_text.setMaximumHeight(150)
                        provider_layout.addWidget(QLabel("Models:"), 2, 0)
                        provider_layout.addWidget(model_text, 2, 1)
                    
                    # Performance metrics if available
                    provider_performance = [
                        (model, metrics) for model, metrics in self._model_performance.items()
                        if model.startswith(f"{provider_name}/")
                    ]
                    if provider_performance:
                        perf_text = "Performance:\n"
                        for model, metrics in provider_performance[:5]:
                            perf_text += f"  {model.split('/', 1)[1]}: {metrics.get('response_time', 'N/A')}s, {metrics.get('tokens_per_second', 'N/A')} t/s\n"
                        
                        perf_label = QLabel(perf_text)
                        perf_label.setStyleSheet("font-family: monospace; font-size: 10px;")
                        provider_layout.addWidget(perf_label, 3, 0, 1, 2)
                else:
                    provider_layout.addWidget(QLabel("Status: Not accessible"), 1, 0, 1, 2)
                
                providers_layout.addWidget(provider_frame)
        else:
            providers_layout.addWidget(QLabel("No provider data available"))
        
        dashboard_layout.addWidget(providers_group)
        
        # Performance summary section
        if self._model_performance:
            perf_group = QGroupBox("Performance Summary")
            perf_layout = QVBoxLayout(perf_group)
            
            perf_summary = "Recent Performance:\n"
            for model, metrics in list(self._model_performance.items())[:10]:
                perf_summary += f"{model}: {metrics.get('response_time', 'N/A')}s, {metrics.get('tokens_per_second', 'N/A')} t/s\n"
            
            perf_text = QTextEdit()
            perf_text.setPlainText(perf_summary)
            perf_text.setReadOnly(True)
            perf_text.setMaximumHeight(150)
            perf_layout.addWidget(perf_text)
            
            dashboard_layout.addWidget(perf_group)
        
        scroll_area.setWidget(dashboard_widget)
        layout.addWidget(scroll_area)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(lambda: self._refresh_health_dashboard(dialog))
        button_layout.addWidget(refresh_btn)
        
        export_btn = QPushButton("Export Report")
        export_btn.clicked.connect(lambda: self._export_health_report())
        button_layout.addWidget(export_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    def _refresh_health_dashboard(self, dialog):
        """Refresh the health dashboard."""
        dialog.accept()
        self.update_provider_health_status()
        self.show_health_dashboard()
    
    def _export_health_report(self):
        """Export health report to file."""
        try:
            from datetime import datetime
            import os
            
            report = f"Provider Health Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            report += "=" * 60 + "\n\n"
            
            if hasattr(self, 'router') and self.router:
                total_providers = len(self.router.providers)
                available_providers = sum(
                    1 for provider in self.router.providers.values() 
                    if getattr(provider, 'is_available', False)
                )
                
                report += f"Total Providers: {total_providers}\n"
                report += f"Available Providers: {available_providers}\n\n"
                
                for provider_name, provider in self.router.providers.items():
                    report += f"\n{provider_name}:\n"
                    report += f"  Status: {'Available' if getattr(provider, 'is_available', False) else 'Unavailable'}\n"
                    
                    if getattr(provider, 'is_available', False):
                        provider_models = [
                            key for key in self._model_health.keys() 
                            if key.startswith(f"{provider_name}/")
                        ]
                        healthy_models = sum(
                            1 for model in provider_models 
                            if self._model_health.get(model, True)
                        )
                        
                        report += f"  Models: {len(provider_models)} ({healthy_models} healthy)\n"
                        
                        for model in provider_models:
                            health = "Healthy" if self._model_health.get(model, True) else "Unhealthy"
                            report += f"    {model.split('/', 1)[1]}: {health}\n"
                            
                            if model in self._model_performance:
                                metrics = self._model_performance[model]
                                report += f"      Performance: {metrics.get('response_time', 'N/A')}s, {metrics.get('tokens_per_second', 'N/A')} t/s\n"
            
            # Save to file
            reports_dir = os.path.expanduser("~/.local/share/chat-linux-client/reports")
            os.makedirs(reports_dir, exist_ok=True)
            
            report_file = os.path.join(reports_dir, f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            QMessageBox.information(self, "Export Success", f"Health report exported to:\n{report_file}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export health report: {e}")
    
    def show_documentation(self):
        """Show documentation dialog."""
        doc_text = """
Chat Linux Client - Documentation

GETTING STARTED:
1. Configure API keys in Settings > Configure Providers
2. Select your preferred AI provider and model
3. Start chatting!

PROVIDERS:
- Ollama: Local AI models (requires Ollama installation)
- Groq: Ultra-fast inference (API key required)
- HuggingFace: Open-source models (API key required)
- OpenRouter: Multi-model access (API key required)

FEATURES:
- Multiple AI provider support
- Real-time streaming responses
- Chat history persistence
- Auto-captured fenced code snippets with one-click copy
- Embedded terminal tabs for running generated commands/snippets
- Privacy-focused design
- Customizable themes and settings

SHORTCUTS:
- Enter: Send message
- Ctrl+L: Clear chat
- Ctrl+S: Export chat
- Ctrl+,: Open settings

TROUBLESHOOTING:
- If models don't appear: Check API keys and network connection
- For local models: Install and start Ollama
- For performance: Adjust context window and max tokens

For more information, see the README.md file.
        """.strip()
        
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Documentation")
        dialog.setText("Chat Linux Client Documentation")
        dialog.setDetailedText(doc_text)
        dialog.setIcon(QMessageBox.Icon.Information)
        dialog.exec()
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Private Chat Linux Client",
            "Private Chat Linux Client\n\n"
            "A privacy-first, multi-provider AI desktop client\n"
            "for Linux systems.\n\n"
            "Features:\n"
            "· Multiple AI provider support\n"
            "· Offline capability with Ollama\n"
            "· Streaming responses\n"
            "· Embedded coding terminals\n"
            "· Copyable code snippet capture\n"
            "· Privacy-focused design\n"
            "· Extensible architecture"
        )
    
    def apply_theme(self):
        """Apply the selected theme."""
        if self.settings.ui.theme == "dark":
            # Load external QSS file
            try:
                import os
                project_root = os.path.dirname(os.path.dirname(__file__))
                qss_file = os.path.join(project_root, "styles", "dark.qss")
                
                if os.path.exists(qss_file):
                    with open(qss_file, 'r') as f:
                        stylesheet = f.read()
                    self.setStyleSheet(stylesheet)
                    self.logger.info("Applied dark theme from QSS file")
                else:
                    self.logger.warning(f"QSS file not found: {qss_file}")
                    self._apply_fallback_theme()
            except Exception as e:
                self.logger.error(f"Failed to load QSS file: {e}")
                self._apply_fallback_theme()
        else:
            self.setStyleSheet("")  # Use system default
    
    def _apply_fallback_theme(self):
        """Apply fallback dark theme if QSS file fails to load."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QTextEdit {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
            }
            QLineEdit {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 5px;
            }
            QPushButton {
                background-color: #4a4a4a;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton:pressed {
                background-color: #3a3a3a;
            }
            QComboBox {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 3px;
                selection-background-color: #4a90e2;
                selection-color: #ffffff;
                combobox-popup: 0;
            }
            QComboBox QAbstractItemView {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                selection-background-color: #4a90e2;
                selection-color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
        """)
    
    def update_status(self):
        """Update provider status in status bar."""
        try:
            available_providers = sum(
                1 for provider in self.router.providers.values() if getattr(provider, "is_available", False)
            )
            if available_providers > 0:
                self.status_bar.showMessage(f"Ready - {available_providers} provider(s) available")
            else:
                self.status_bar.showMessage("Ready - No providers available")
        except Exception as e:
            self.logger.error(f"Failed to update status: {e}")
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Save window geometry
        self.settings.update_ui_config(
            window_x=self.x(),
            window_y=self.y(),
            window_width=self.width(),
            window_height=self.height()
        )
        
        # Stop status timer
        if hasattr(self, 'status_timer'):
            self.status_timer.stop()
        
        # Stop any running generation
        if self.current_worker:
            self.stop_generation()

        # Stop system check worker if running
        if self.system_check_worker and self.system_check_worker.isRunning():
            self.system_check_worker.wait(1000)
            if self.system_check_worker.isRunning():
                self.system_check_worker.terminate()
                self.system_check_worker.wait()

        # Stop any terminal subprocesses
        if hasattr(self, "terminal_tabs"):
            for index in range(self.terminal_tabs.count()):
                tab = self.terminal_tabs.widget(index)
                if isinstance(tab, EmbeddedTerminal):
                    tab.stop()
        
        # Save settings
        self.settings.save()
        self._save_model_health_cache()
        
        event.accept()
