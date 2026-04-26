"""
Shared pytest fixtures for the chat-linux-client test suite.

All fixtures run under QT_QPA_PLATFORM=offscreen so no display is required.
Heavy I/O dependencies (ProviderRouter, HistoryManager, KeyHandler) are
replaced with MagicMock instances so tests stay fast and hermetic.
"""

import os
import sys

# Force offscreen Qt platform before any Qt import happens.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QApplication

# Ensure the project root is on sys.path so "ui", "core", etc. are importable.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ---------------------------------------------------------------------------
# Minimal settings stubs
# ---------------------------------------------------------------------------

def _make_mock_settings():
    """Return a MagicMock that quacks like a SettingsManager instance."""
    from core.settings import UIConfig, ChatConfig, PrivacyConfig

    settings = MagicMock()
    settings.ui = UIConfig()          # Real dataclass — gives real attribute access
    settings.chat = ChatConfig()
    settings.privacy = PrivacyConfig()
    settings.providers = {
        "ollama": MagicMock(enabled=True),
        "groq": MagicMock(enabled=False),
        "huggingface": MagicMock(enabled=False),
        "openrouter": MagicMock(enabled=False),
        "openai": MagicMock(enabled=False),
    }

    # Stub mutators called during ChatWindow lifecycle
    settings.update_ui_config = MagicMock()
    settings.update_chat_config = MagicMock()
    settings.save = MagicMock()
    settings.load = MagicMock()
    return settings


def _make_mock_router():
    router = MagicMock()
    router.providers = {}
    router.get_all_models = MagicMock(return_value=[])
    return router


# ---------------------------------------------------------------------------
# chat_window fixture
# ---------------------------------------------------------------------------

@pytest.fixture()
def chat_window(qtbot):
    """
    A fully-constructed ChatWindow with all heavy I/O mocked out.

    Patches applied for the duration of each test:
    - SettingsManager  → returns a real-dataclass-backed MagicMock
    - ProviderRouter   → empty MagicMock (no real provider init)
    - ModelManager     → MagicMock
    - HistoryManager   → MagicMock (no SQLite)
    - KeyHandler       → raises RuntimeError → exercises NoopKeyHandler path
    - init_providers_sync → no-op (skips asyncio loop)
    - status_timer     → QTimer is created but we stop it immediately
    """
    mock_settings = _make_mock_settings()
    mock_router = _make_mock_router()

    with (
        patch("ui.main_window.SettingsManager", return_value=mock_settings),
        patch("ui.main_window.ProviderRouter", return_value=mock_router),
        patch("ui.main_window.ModelManager", return_value=MagicMock()),
        patch("ui.main_window.HistoryManager", return_value=MagicMock()),
        patch("ui.main_window.KeyHandler", side_effect=RuntimeError("test: no keychain")),
        patch.object(
            # Prevent the real async provider init from running
            __import__("ui.main_window", fromlist=["ChatWindow"]).ChatWindow,
            "init_providers_sync",
            lambda self: None,
        ),
    ):
        from ui.main_window import ChatWindow
        window = ChatWindow()
        qtbot.addWidget(window)
        # Stop the status poll timer so it doesn't fire during tests
        window.status_timer.stop()
        yield window
