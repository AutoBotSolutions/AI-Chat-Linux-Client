"""
Settings and configuration management for the chat-linux-client.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class ProviderConfig:
    """Configuration for an AI provider."""
    enabled: bool = True
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3


@dataclass
class UIConfig:
    """UI configuration settings."""
    theme: str = "dark"
    font_size: int = 12
    font_family: str = "Ubuntu Mono"
    window_width: int = 900
    window_height: int = 600
    window_x: int = 100
    window_y: int = 100
    show_timestamps: bool = True
    show_model_info: bool = True
    auto_scroll: bool = True


@dataclass
class ChatConfig:
    """Chat configuration settings."""
    default_model: Optional[str] = None
    default_provider: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stream_responses: bool = True
    save_history: bool = True
    max_history_items: int = 1000
    context_window: int = 10


@dataclass
class PrivacyConfig:
    """Privacy and security settings."""
    encrypt_chats: bool = False
    encryption_key: Optional[str] = None
    delete_api_keys_on_exit: bool = False
    disable_telemetry: bool = True
    local_storage_only: bool = False


class SettingsManager:
    """Manages application settings and configuration."""
    
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir or self._get_default_config_dir())
        self.config_file = self.config_dir / "config.json"
        self.logger = logging.getLogger(__name__)
        
        # Default configuration
        self.providers = {
            "ollama": ProviderConfig(
                enabled=True,
                base_url="http://localhost:11434"
            ),
            "groq": ProviderConfig(
                enabled=False,
                base_url="https://api.groq.com/openai/v1"
            ),
            "huggingface": ProviderConfig(
                enabled=False,
                base_url="https://api-inference.huggingface.co"
            ),
            "openrouter": ProviderConfig(
                enabled=False,
                base_url="https://openrouter.ai/api/v1"
            ),
            "openai": ProviderConfig(
                enabled=False,
                base_url="https://api.openai.com/v1"
            )
        }
        
        self.ui = UIConfig()
        self.chat = ChatConfig()
        self.privacy = PrivacyConfig()
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing configuration
        self.load()
    
    def _get_default_config_dir(self) -> str:
        """Get default configuration directory."""
        home = Path.home()
        if os.name == 'nt':  # Windows
            return str(home / "AppData" / "Local" / "ChatLinuxClient")
        else:  # Linux/Mac
            return str(home / ".config" / "chat-linux-client")
    
    def load(self) -> None:
        """Load configuration from file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load provider configurations
                if "providers" in data:
                    for provider_name, provider_data in data["providers"].items():
                        if provider_name in self.providers:
                            for key, value in provider_data.items():
                                if hasattr(self.providers[provider_name], key):
                                    setattr(self.providers[provider_name], key, value)
                
                # Load UI configuration
                if "ui" in data:
                    for key, value in data["ui"].items():
                        if hasattr(self.ui, key):
                            setattr(self.ui, key, value)
                
                # Load chat configuration
                if "chat" in data:
                    for key, value in data["chat"].items():
                        if hasattr(self.chat, key):
                            setattr(self.chat, key, value)
                
                # Load privacy configuration
                if "privacy" in data:
                    for key, value in data["privacy"].items():
                        if hasattr(self.privacy, key):
                            setattr(self.privacy, key, value)
                
                self.logger.info(f"Configuration loaded from {self.config_file}")
            else:
                self.logger.info("No existing configuration found, using defaults")
                self.save()  # Save default configuration
        
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
    
    def save(self) -> None:
        """Save configuration to file."""
        try:
            data = {
                "providers": {
                    name: asdict(config) for name, config in self.providers.items()
                },
                "ui": asdict(self.ui),
                "chat": asdict(self.chat),
                "privacy": asdict(self.privacy)
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Configuration saved to {self.config_file}")
        
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
    
    def get_provider_config(self, provider_name: str) -> Optional[ProviderConfig]:
        """Get configuration for a specific provider."""
        return self.providers.get(provider_name)
    
    def set_provider_config(self, provider_name: str, config: ProviderConfig) -> None:
        """Set configuration for a specific provider."""
        self.providers[provider_name] = config
    
    def get_enabled_providers(self) -> Dict[str, ProviderConfig]:
        """Get all enabled providers."""
        return {name: config for name, config in self.providers.items() if config.enabled}
    
    def get_provider_dict(self, key_handler=None) -> Dict[str, Any]:
        """Get provider configuration as dictionary for API clients."""
        result = {}
        for name, config in self.providers.items():
            api_key = config.api_key
            # Try to get API key from key_handler if not in config
            if not api_key and key_handler:
                api_key = key_handler.get_key(name)
            
            # Set default base_url for Ollama if not configured
            base_url = config.base_url
            if name == "ollama" and not base_url:
                base_url = "http://localhost:11434"
            
            result[name] = {
                "api_key": api_key,
                "base_url": base_url,
                "timeout": config.timeout,
                "max_retries": config.max_retries
            }
        return result
    
    def update_ui_config(self, **kwargs) -> None:
        """Update UI configuration."""
        for key, value in kwargs.items():
            if hasattr(self.ui, key):
                setattr(self.ui, key, value)
        self.save()
    
    def update_chat_config(self, **kwargs) -> None:
        """Update chat configuration."""
        for key, value in kwargs.items():
            if hasattr(self.chat, key):
                setattr(self.chat, key, value)
        self.save()
    
    def update_privacy_config(self, **kwargs) -> None:
        """Update privacy configuration."""
        for key, value in kwargs.items():
            if hasattr(self.privacy, key):
                setattr(self.privacy, key, value)
        self.save()
    
    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults."""
        # Create a new instance and copy its state
        temp_settings = SettingsManager(str(self.config_dir))
        self.config = temp_settings.config
        self.config_dir = temp_settings.config_dir
        self.save()
    
    def export_config(self, file_path: str) -> bool:
        """Export configuration to a file."""
        try:
            data = {
                "providers": {
                    name: asdict(config) for name, config in self.providers.items()
                },
                "ui": asdict(self.ui),
                "chat": asdict(self.chat),
                "privacy": asdict(self.privacy)
            }
            
            # Remove sensitive data for export
            for provider in data["providers"].values():
                provider["api_key"] = None
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to export configuration: {e}")
            return False
    
    def import_config(self, file_path: str) -> bool:
        """Import configuration from a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Load configuration (preserving existing API keys)
            if "providers" in data:
                for provider_name, provider_data in data["providers"].items():
                    if provider_name in self.providers:
                        # Don't overwrite API keys during import
                        existing_key = self.providers[provider_name].api_key
                        for key, value in provider_data.items():
                            if key != "api_key" and hasattr(self.providers[provider_name], key):
                                setattr(self.providers[provider_name], key, value)
            
            if "ui" in data:
                for key, value in data["ui"].items():
                    if hasattr(self.ui, key):
                        setattr(self.ui, key, value)
            
            if "chat" in data:
                for key, value in data["chat"].items():
                    if hasattr(self.chat, key):
                        setattr(self.chat, key, value)
            
            if "privacy" in data:
                for key, value in data["privacy"].items():
                    if hasattr(self.privacy, key):
                        setattr(self.privacy, key, value)
            
            self.save()
            return True
        except Exception as e:
            self.logger.error(f"Failed to import configuration: {e}")
            return False
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of current configuration."""
        return {
            "config_dir": str(self.config_dir),
            "enabled_providers": list(self.get_enabled_providers().keys()),
            "ui_theme": self.ui.theme,
            "default_model": self.chat.default_model,
            "stream_responses": self.chat.stream_responses,
            "save_history": self.chat.save_history,
            "encrypt_chats": self.privacy.encrypt_chats,
            "disable_telemetry": self.privacy.disable_telemetry
        }
