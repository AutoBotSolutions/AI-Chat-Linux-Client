"""
Settings dialog for configuring API keys and provider settings.
"""

import logging
from typing import Dict, Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QTabWidget, QWidget,
    QGroupBox, QCheckBox, QSpinBox, QComboBox,
    QLabel, QTextEdit, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

from core.settings import SettingsManager
from utils.key_handler import KeyHandler


class NoopKeyHandler:
    """Fallback key handler for settings dialog when secure storage is unavailable."""

    def get_key(self, provider_name: str):
        return None

    def set_key(self, provider_name: str, key: str):
        return None

    def delete_key(self, provider_name: str):
        return None

    def get_key_store_status(self):
        return "unavailable"


class ProviderSettingsWidget(QWidget):
    """Widget for configuring individual provider settings."""
    
    def __init__(self, provider_name: str, settings_manager: SettingsManager, key_handler: KeyHandler):
        super().__init__()
        self.provider_name = provider_name
        self.settings_manager = settings_manager
        self.key_handler = key_handler
        self.logger = logging.getLogger(__name__)
        
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """Initialize the UI for this provider."""
        layout = QVBoxLayout(self)
        
        # Provider info
        info_label = QLabel(f"Configure {self.provider_name.title()} Provider")
        info_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(info_label)
        
        # API Key section
        key_group = QGroupBox("API Key")
        key_layout = QVBoxLayout(key_group)
        
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText(f"Enter {self.provider_name} API key...")
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        key_layout.addWidget(self.key_input)
        
        # Key management buttons
        key_buttons = QHBoxLayout()
        
        self.show_key_btn = QPushButton("Show Key")
        self.show_key_btn.setCheckable(True)
        self.show_key_btn.toggled.connect(self.toggle_key_visibility)
        key_buttons.addWidget(self.show_key_btn)
        
        self.save_key_btn = QPushButton("Save Key")
        self.save_key_btn.clicked.connect(self.save_key)
        key_buttons.addWidget(self.save_key_btn)
        
        self.delete_key_btn = QPushButton("Delete Key")
        self.delete_key_btn.clicked.connect(self.delete_key)
        key_buttons.addWidget(self.delete_key_btn)
        
        key_layout.addLayout(key_buttons)
        layout.addWidget(key_group)
        
        # Provider-specific settings
        settings_group = QGroupBox("Provider Settings")
        settings_layout = QFormLayout(settings_group)
        
        # Enable/disable provider
        self.enabled_checkbox = QCheckBox("Enable Provider")
        settings_layout.addRow("Status:", self.enabled_checkbox)
        
        # Base URL (for providers that support it)
        if self.provider_name in ['ollama', 'huggingface', 'openrouter']:
            self.base_url_input = QLineEdit()
            self.base_url_input.setPlaceholderText("Enter base URL...")
            settings_layout.addRow("Base URL:", self.base_url_input)
        
        # Timeout setting
        self.timeout_spinbox = QSpinBox()
        self.timeout_spinbox.setRange(5, 300)
        self.timeout_spinbox.setValue(30)
        self.timeout_spinbox.setSuffix(" seconds")
        settings_layout.addRow("Timeout:", self.timeout_spinbox)
        
        # Max retries
        self.retries_spinbox = QSpinBox()
        self.retries_spinbox.setRange(0, 10)
        self.retries_spinbox.setValue(3)
        settings_layout.addRow("Max Retries:", self.retries_spinbox)
        
        layout.addWidget(settings_group)
        
        # Provider-specific info
        info_text = self.get_provider_info()
        if info_text:
            info_group = QGroupBox("Provider Information")
            info_layout = QVBoxLayout(info_group)
            info_label = QLabel(info_text)
            info_label.setWordWrap(True)
            info_label.setStyleSheet("color: #888888; font-size: 11px;")
            info_layout.addWidget(info_label)
            layout.addWidget(info_group)
        
        layout.addStretch()
    
    def get_provider_info(self) -> str:
        """Get provider-specific information."""
        info_map = {
            'ollama': "Ollama provides local AI model inference. Default URL: http://localhost:11434",
            'groq': "Groq offers ultra-low latency inference with Llama models. Get API key from https://console.groq.com/",
            'huggingface': "HuggingFace provides access to open-source models. Get API key from https://huggingface.co/settings/tokens",
            'openrouter': "OpenRouter provides access to multiple models through one API. Get API key from https://openrouter.ai/keys",
            'openai': "OpenAI provides access to GPT models including GPT-3.5, GPT-4, and GPT-4 Turbo. Get API key from https://platform.openai.com/api-keys"
        }
        return info_map.get(self.provider_name, "")
    
    def load_settings(self):
        """Load current settings for this provider."""
        try:
            # Load provider settings
            provider_config = self.settings_manager.providers.get(self.provider_name)
            if provider_config:
                self.enabled_checkbox.setChecked(provider_config.enabled)
                self.timeout_spinbox.setValue(provider_config.timeout)
                self.retries_spinbox.setValue(provider_config.max_retries)
                
                if hasattr(self, 'base_url_input') and provider_config.base_url:
                    self.base_url_input.setText(provider_config.base_url)
            
            # Load API key from config if available (not from encrypted storage)
            if provider_config and provider_config.api_key:
                self.key_input.setText(provider_config.api_key)
            
        except Exception as e:
            self.logger.error(f"Failed to load {self.provider_name} settings: {e}")
    
    def save_settings(self):
        """Save settings for this provider."""
        try:
            # Save provider settings
            provider_config = self.settings_manager.providers[self.provider_name]
            provider_config.enabled = self.enabled_checkbox.isChecked()
            provider_config.timeout = self.timeout_spinbox.value()
            provider_config.max_retries = self.retries_spinbox.value()
            
            if hasattr(self, 'base_url_input'):
                provider_config.base_url = self.base_url_input.text() or None
            
            # Save API key if provided
            key_text = self.key_input.text().strip()
            if key_text:
                self.key_handler.set_key(self.provider_name, key_text)
            
            self.settings_manager.save()
            self.logger.info(f"Saved {self.provider_name} settings")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save {self.provider_name} settings: {e}")
            return False
    
    def toggle_key_visibility(self, checked: bool):
        """Toggle API key visibility."""
        if checked:
            self.key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_key_btn.setText("Hide Key")
        else:
            self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_key_btn.setText("Show Key")
    
    def save_key(self):
        """Save the API key."""
        key_text = self.key_input.text().strip()
        if key_text:
            try:
                self.key_handler.set_key(self.provider_name, key_text)
                QMessageBox.information(self, "Success", f"{self.provider_name.title()} API key saved successfully!")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save API key: {e}")
        else:
            QMessageBox.warning(self, "Warning", "Please enter an API key first.")
    
    def delete_key(self):
        """Delete the stored API key."""
        reply = QMessageBox.question(
            self, "Confirm Delete", 
            f"Are you sure you want to delete the {self.provider_name.title()} API key?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.key_handler.delete_key(self.provider_name)
                self.key_input.clear()
                QMessageBox.information(self, "Success", f"{self.provider_name.title()} API key deleted successfully!")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to delete API key: {e}")


class SettingsDialog(QDialog):
    """Main settings dialog for the Chat Linux Client."""
    
    settings_changed = pyqtSignal()
    
    def __init__(self, settings_manager: SettingsManager, parent=None, default_tab: str = "Providers"):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.logger = logging.getLogger(__name__)
        try:
            self.key_handler = KeyHandler()
        except Exception as e:
            self.logger.error(f"Failed to initialize secure key storage in settings dialog: {e}")
            self.key_handler = NoopKeyHandler()
        self.default_tab = default_tab
        
        self.setWindowTitle("Chat Linux Client - Settings")
        self.setModal(True)
        self.resize(800, 600)
        
        self.init_ui()
        self.load_all_settings()
        
        # Set default tab
        self.set_default_tab()
    
    def init_ui(self):
        """Initialize the settings dialog UI."""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Provider settings tab
        self.create_provider_tab()
        
        # UI settings tab
        self.create_ui_tab()
        
        # Chat settings tab
        self.create_chat_tab()
        
        # Privacy settings tab
        self.create_privacy_tab()
        
        # Dialog buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save All Settings")
        self.save_button.clicked.connect(self.save_all_settings)
        button_layout.addWidget(self.save_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_settings)
        button_layout.addWidget(self.apply_button)
        
        layout.addLayout(button_layout)
    
    def create_provider_tab(self):
        """Create the provider configuration tab."""
        provider_widget = QWidget()
        provider_layout = QVBoxLayout(provider_widget)
        
        # Provider tabs
        self.provider_tabs = QTabWidget()
        provider_layout.addWidget(self.provider_tabs)
        
        # Add individual provider settings
        providers = ['ollama', 'groq', 'huggingface', 'openrouter', 'openai']
        self.provider_widgets = {}
        
        for provider in providers:
            widget = ProviderSettingsWidget(provider, self.settings_manager, self.key_handler)
            self.provider_tabs.addTab(widget, provider.title())
            self.provider_widgets[provider] = widget
        
        provider_layout.addStretch()
        self.tab_widget.addTab(provider_widget, "Providers")
    
    def create_ui_tab(self):
        """Create the UI settings tab."""
        ui_widget = QWidget()
        ui_layout = QFormLayout(ui_widget)
        
        # Theme
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light"])
        ui_layout.addRow("Theme:", self.theme_combo)
        
        # Font settings
        self.font_family_combo = QComboBox()
        self.font_family_combo.addItems(["Ubuntu Mono", "Courier New", "Monospace", "Arial"])
        ui_layout.addRow("Font Family:", self.font_family_combo)
        
        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setRange(8, 24)
        ui_layout.addRow("Font Size:", self.font_size_spinbox)
        
        # Window settings
        self.show_timestamps_checkbox = QCheckBox()
        ui_layout.addRow("Show Timestamps:", self.show_timestamps_checkbox)
        
        self.show_model_info_checkbox = QCheckBox()
        ui_layout.addRow("Show Model Info:", self.show_model_info_checkbox)
        
        self.auto_scroll_checkbox = QCheckBox()
        ui_layout.addRow("Auto-scroll:", self.auto_scroll_checkbox)
        
        ui_layout.addRow("", QWidget())  # Spacer
        self.tab_widget.addTab(ui_widget, "UI")
    
    def create_chat_tab(self):
        """Create the chat settings tab."""
        chat_widget = QWidget()
        chat_layout = QFormLayout(chat_widget)
        
        # Default model
        self.default_model_combo = QComboBox()
        chat_layout.addRow("Default Model:", self.default_model_combo)
        
        # Temperature
        self.temperature_spinbox = QSpinBox()
        self.temperature_spinbox.setRange(0, 200)
        self.temperature_spinbox.setValue(70)
        self.temperature_spinbox.setSuffix(" / 100")
        chat_layout.addRow("Temperature:", self.temperature_spinbox)
        
        # Max tokens
        self.max_tokens_spinbox = QSpinBox()
        self.max_tokens_spinbox.setRange(0, 4096)
        self.max_tokens_spinbox.setValue(0)
        self.max_tokens_spinbox.setSpecialValueText("Unlimited")
        chat_layout.addRow("Max Tokens:", self.max_tokens_spinbox)
        
        # Streaming
        self.stream_responses_checkbox = QCheckBox()
        chat_layout.addRow("Stream Responses:", self.stream_responses_checkbox)
        
        # Save history
        self.save_history_checkbox = QCheckBox()
        chat_layout.addRow("Save Chat History:", self.save_history_checkbox)
        
        # Context window
        self.context_window_spinbox = QSpinBox()
        self.context_window_spinbox.setRange(1, 50)
        chat_layout.addRow("Context Window:", self.context_window_spinbox)
        
        chat_layout.addRow("", QWidget())  # Spacer
        self.tab_widget.addTab(chat_widget, "Chat")
    
    def create_privacy_tab(self):
        """Create the privacy settings tab."""
        privacy_widget = QWidget()
        privacy_layout = QFormLayout(privacy_widget)

        self.key_store_status_label = QLabel("Unknown")
        self.key_store_status_label.setWordWrap(True)
        privacy_layout.addRow("Key Storage Status:", self.key_store_status_label)

        self.refresh_key_status_button = QPushButton("Refresh Key Status")
        self.refresh_key_status_button.clicked.connect(self.update_key_store_status)
        privacy_layout.addRow("", self.refresh_key_status_button)
        
        # Encryption
        self.encrypt_chats_checkbox = QCheckBox()
        privacy_layout.addRow("Encrypt Chat History:", self.encrypt_chats_checkbox)
        
        # API key handling
        self.delete_keys_on_exit_checkbox = QCheckBox()
        privacy_layout.addRow("Delete API Keys on Exit:", self.delete_keys_on_exit_checkbox)
        
        # Telemetry
        self.disable_telemetry_checkbox = QCheckBox()
        privacy_layout.addRow("Disable Telemetry:", self.disable_telemetry_checkbox)
        
        # Local storage
        self.local_storage_only_checkbox = QCheckBox()
        privacy_layout.addRow("Local Storage Only:", self.local_storage_only_checkbox)
        
        privacy_layout.addRow("", QWidget())  # Spacer
        self.tab_widget.addTab(privacy_widget, "Privacy")

    def update_key_store_status(self):
        """Refresh key storage health indicator text in privacy tab."""
        status = getattr(self.key_handler, "get_key_store_status", lambda: "unknown")()
        status_map = {
            "ok": ("OK: encrypted key store is readable.", "#51cf66"),
            "missing-file": ("No encrypted key file found yet.", "#aaaaaa"),
            "invalid-token": ("Needs re-entry: current encryption key cannot decrypt stored API keys.", "#ffb347"),
            "corrupt-json": ("Corrupt key store detected. Re-enter API keys in Providers tab.", "#ff6b6b"),
            "load-error": ("Key storage load error. Check logs for details.", "#ff6b6b"),
            "unavailable": ("Secure key storage unavailable in this session.", "#ff6b6b"),
            "uninitialized": ("Key storage not initialized yet.", "#aaaaaa"),
            "unknown": ("Key storage status unknown.", "#aaaaaa"),
        }
        text, color = status_map.get(status, status_map["unknown"])
        self.key_store_status_label.setText(text)
        self.key_store_status_label.setStyleSheet(f"color: {color};")
    
    def set_default_tab(self):
        """Set the default tab based on the default_tab parameter."""
        tab_names = ["Providers", "UI", "Chat", "Privacy"]
        if self.default_tab in tab_names:
            index = tab_names.index(self.default_tab)
            self.tab_widget.setCurrentIndex(index)
    
    def populate_default_model_combo(self):
        """Populate the default model combo box with available models."""
        try:
            # Import here to avoid circular imports
            import asyncio
            from core.provider_router import ProviderRouter
            
            # Create a temporary router to get available models
            router = ProviderRouter(self.settings_manager)
            
            # Run async method in sync context
            loop = asyncio.new_event_loop()
            try:
                # Get provider configuration
                provider_config = self.settings_manager.get_provider_dict(self.key_handler)
                loop.run_until_complete(router.initialize_providers(provider_config))
                models = loop.run_until_complete(router.get_all_models())
                
                # Clear and populate combo box
                self.default_model_combo.clear()
                self.default_model_combo.addItem("Select Model...", None)
                
                # Add models grouped by provider
                for provider_name, model_list in models.items():
                    if model_list:  # Only add providers that have models
                        # Add provider as separator
                        self.default_model_combo.addItem(f"--- {provider_name.upper()} ---", None)
                        # Add models for this provider
                        for model in sorted(model_list):
                            display_name = f"{model} ({provider_name})"
                            self.default_model_combo.addItem(display_name, model)
                
                # Set current selection if default model is configured
                current_default = self.settings_manager.chat.default_model
                if current_default:
                    index = self.default_model_combo.findData(current_default)
                    if index >= 0:
                        self.default_model_combo.setCurrentIndex(index)
                else:
                    self.default_model_combo.setCurrentIndex(0)  # "Select Model..."
                    
            except Exception as e:
                self.logger.warning(f"Could not populate models: {e}")
                # Fallback: add basic model options
                self.default_model_combo.clear()
                self.default_model_combo.addItem("Select Model...", None)
                self.default_model_combo.addItem("llama3.2:1b (ollama)", "llama3.2:1b")
                self.default_model_combo.addItem("qwen2.5:3b (ollama)", "qwen2.5:3b")
                self.default_model_combo.addItem("mistral:7b (ollama)", "mistral:7b")
                self.default_model_combo.addItem("gpt-3.5-turbo (openai)", "gpt-3.5-turbo")
                self.default_model_combo.addItem("gpt-4 (openai)", "gpt-4")
                
            finally:
                try:
                    loop.run_until_complete(loop.shutdown_asyncgens())
                except Exception:
                    pass
                loop.close()
                
        except Exception as e:
            self.logger.error(f"Failed to populate default model combo: {e}")
    
    def load_all_settings(self):
        """Load all current settings into the dialog."""
        try:
            # UI settings
            self.theme_combo.setCurrentText(self.settings_manager.ui.theme)
            self.font_family_combo.setCurrentText(self.settings_manager.ui.font_family)
            self.font_size_spinbox.setValue(self.settings_manager.ui.font_size)
            self.show_timestamps_checkbox.setChecked(self.settings_manager.ui.show_timestamps)
            self.show_model_info_checkbox.setChecked(self.settings_manager.ui.show_model_info)
            self.auto_scroll_checkbox.setChecked(self.settings_manager.ui.auto_scroll)
            
            # Chat settings
            raw_temperature = self.settings_manager.chat.temperature
            try:
                temperature = float(raw_temperature)
            except (TypeError, ValueError):
                temperature = 0.7
            temperature = max(0.0, min(2.0, temperature))
            self.temperature_spinbox.setValue(int(round(temperature * 100)))
            self.max_tokens_spinbox.setValue(self.settings_manager.chat.max_tokens or 0)
            self.stream_responses_checkbox.setChecked(self.settings_manager.chat.stream_responses)
            self.save_history_checkbox.setChecked(self.settings_manager.chat.save_history)
            self.context_window_spinbox.setValue(self.settings_manager.chat.context_window)
            
            # Privacy settings
            self.encrypt_chats_checkbox.setChecked(self.settings_manager.privacy.encrypt_chats)
            self.delete_keys_on_exit_checkbox.setChecked(self.settings_manager.privacy.delete_api_keys_on_exit)
            self.disable_telemetry_checkbox.setChecked(self.settings_manager.privacy.disable_telemetry)
            self.local_storage_only_checkbox.setChecked(self.settings_manager.privacy.local_storage_only)
            # Populate default model combo with available models
            self.populate_default_model_combo()
            self.update_key_store_status()
            
            self.logger.info("Settings loaded into dialog")
            
        except Exception as e:
            self.logger.error(f"Failed to load settings: {e}")
    
    def save_all_settings(self):
        """Save all settings and close the dialog."""
        if self.apply_settings():
            self.accept()
    
    def apply_settings(self) -> bool:
        """Apply all settings without closing the dialog."""
        try:
            # Save all provider settings
            for provider, widget in self.provider_widgets.items():
                if not widget.save_settings():
                    return False
            
            # Save UI settings
            self.settings_manager.ui.theme = self.theme_combo.currentText()
            self.settings_manager.ui.font_family = self.font_family_combo.currentText()
            self.settings_manager.ui.font_size = self.font_size_spinbox.value()
            self.settings_manager.ui.show_timestamps = self.show_timestamps_checkbox.isChecked()
            self.settings_manager.ui.show_model_info = self.show_model_info_checkbox.isChecked()
            self.settings_manager.ui.auto_scroll = self.auto_scroll_checkbox.isChecked()
            
            # Save chat settings
            validated_temp = max(0, min(200, self.temperature_spinbox.value()))
            self.settings_manager.chat.temperature = round(validated_temp / 100.0, 2)
            self.settings_manager.chat.max_tokens = self.max_tokens_spinbox.value() if self.max_tokens_spinbox.value() > 0 else None
            self.settings_manager.chat.stream_responses = self.stream_responses_checkbox.isChecked()
            self.settings_manager.chat.save_history = self.save_history_checkbox.isChecked()
            self.settings_manager.chat.context_window = self.context_window_spinbox.value()
            
            # Save default model selection
            selected_model = self.default_model_combo.currentData()
            self.settings_manager.chat.default_model = selected_model
            
            # Save privacy settings
            self.settings_manager.privacy.encrypt_chats = self.encrypt_chats_checkbox.isChecked()
            self.settings_manager.privacy.delete_api_keys_on_exit = self.delete_keys_on_exit_checkbox.isChecked()
            self.settings_manager.privacy.disable_telemetry = self.disable_telemetry_checkbox.isChecked()
            self.settings_manager.privacy.local_storage_only = self.local_storage_only_checkbox.isChecked()
            
            # Save all settings
            self.settings_manager.save()
            
            # Emit signal that settings changed
            self.settings_changed.emit()
            
            self.logger.info("All settings saved successfully")
            QMessageBox.information(self, "Success", "Settings saved successfully!")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save settings: {e}")
            QMessageBox.warning(self, "Error", f"Failed to save settings: {e}")
            return False
