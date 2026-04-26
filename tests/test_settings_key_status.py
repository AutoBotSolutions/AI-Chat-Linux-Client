"""Tests for key storage status indicator in settings privacy tab."""

from core.settings import SettingsManager
from ui.settings_dialog import SettingsDialog


class FakeKeyHandler:
    def __init__(self, status: str):
        self._status = status

    def get_key(self, provider_name: str):
        return None

    def set_key(self, provider_name: str, key: str):
        return None

    def delete_key(self, provider_name: str):
        return None

    def get_key_store_status(self):
        return self._status


def test_key_status_invalid_token_message(qtbot, tmp_path, monkeypatch):
    monkeypatch.setattr("ui.settings_dialog.KeyHandler", lambda: FakeKeyHandler("invalid-token"))
    settings = SettingsManager(config_dir=str(tmp_path))
    dialog = SettingsDialog(settings)
    qtbot.addWidget(dialog)

    dialog.update_key_store_status()

    assert "Needs re-entry" in dialog.key_store_status_label.text()


def test_key_status_ok_message(qtbot, tmp_path, monkeypatch):
    monkeypatch.setattr("ui.settings_dialog.KeyHandler", lambda: FakeKeyHandler("ok"))
    settings = SettingsManager(config_dir=str(tmp_path))
    dialog = SettingsDialog(settings)
    qtbot.addWidget(dialog)

    dialog.update_key_store_status()

    assert "OK" in dialog.key_store_status_label.text()
