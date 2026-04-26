"""
Configuration manager for handling application configuration.
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from datetime import datetime


class ConfigManager:
    """Manages application configuration with optional encryption."""
    
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir or self._get_default_config_dir())
        self.config_file = self.config_dir / "app_config.json"
        self.encrypted_config_file = self.config_dir / "app_config.enc"
        self.key_file = self.config_dir / ".key"
        
        self.logger = logging.getLogger(__name__)
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize configuration
        self.config = {}
        self._encryption_key = None
        self._fernet = None
        
        # Load configuration
        self.load()
    
    def _get_default_config_dir(self) -> str:
        """Get default configuration directory."""
        home = Path.home()
        if os.name == 'nt':  # Windows
            return str(home / "AppData" / "Local" / "ChatLinuxClient" / "config")
        else:  # Linux/Mac
            return str(home / ".config" / "chat-linux-client")
    
    def _generate_encryption_key(self, password: str) -> bytes:
        """Generate encryption key from password."""
        password_bytes = password.encode('utf-8')
        salt = b'chat_linux_client_salt'  # In production, use a random salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
        return key
    
    def _save_encryption_key(self, key: bytes) -> None:
        """Save encryption key to file."""
        try:
            with open(self.key_file, 'wb') as f:
                f.write(key)
            # Set file permissions to be readable only by owner
            os.chmod(self.key_file, 0o600)
        except Exception as e:
            self.logger.error(f"Failed to save encryption key: {e}")
    
    def _load_encryption_key(self) -> Optional[bytes]:
        """Load encryption key from file."""
        try:
            if self.key_file.exists():
                with open(self.key_file, 'rb') as f:
                    return f.read()
        except Exception as e:
            self.logger.error(f"Failed to load encryption key: {e}")
        return None
    
    def enable_encryption(self, password: str) -> bool:
        """Enable configuration encryption."""
        try:
            self._encryption_key = self._generate_encryption_key(password)
            self._fernet = Fernet(self._encryption_key)
            self._save_encryption_key(self._encryption_key)
            
            # Encrypt existing configuration
            if self.config:
                self._save_encrypted()
            
            # Remove unencrypted config file
            if self.config_file.exists():
                self.config_file.unlink()
            
            self.logger.info("Configuration encryption enabled")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to enable encryption: {e}")
            return False
    
    def disable_encryption(self) -> bool:
        """Disable configuration encryption."""
        try:
            if self._fernet and self.config:
                # Save unencrypted configuration
                self._save_unencrypted()
            
            # Remove encrypted files
            if self.encrypted_config_file.exists():
                self.encrypted_config_file.unlink()
            if self.key_file.exists():
                self.key_file.unlink()
            
            self._encryption_key = None
            self._fernet = None
            
            self.logger.info("Configuration encryption disabled")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to disable encryption: {e}")
            return False
    
    def is_encrypted(self) -> bool:
        """Check if configuration is encrypted."""
        return self._fernet is not None
    
    def _save_unencrypted(self) -> None:
        """Save configuration to unencrypted file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save unencrypted config: {e}")
            raise
    
    def _save_encrypted(self) -> None:
        """Save configuration to encrypted file."""
        if not self._fernet:
            raise Exception("Encryption not enabled")
        
        try:
            config_json = json.dumps(self.config, ensure_ascii=False)
            encrypted_data = self._fernet.encrypt(config_json.encode('utf-8'))
            
            with open(self.encrypted_config_file, 'wb') as f:
                f.write(encrypted_data)
        except Exception as e:
            self.logger.error(f"Failed to save encrypted config: {e}")
            raise
    
    def _load_unencrypted(self) -> None:
        """Load configuration from unencrypted file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                self.config = {}
        except Exception as e:
            self.logger.error(f"Failed to load unencrypted config: {e}")
            self.config = {}
    
    def _load_encrypted(self) -> None:
        """Load configuration from encrypted file."""
        try:
            if self.encrypted_config_file.exists():
                with open(self.encrypted_config_file, 'rb') as f:
                    encrypted_data = f.read()
                
                decrypted_data = self._fernet.decrypt(encrypted_data)
                self.config = json.loads(decrypted_data.decode('utf-8'))
            else:
                self.config = {}
        except Exception as e:
            self.logger.error(f"Failed to load encrypted config: {e}")
            self.config = {}
    
    def load(self) -> None:
        """Load configuration from file."""
        # Try to load encryption key first
        key = self._load_encryption_key()
        if key:
            try:
                self._encryption_key = key
                self._fernet = Fernet(key)
                self._load_encrypted()
                self.logger.info("Loaded encrypted configuration")
                return
            except Exception:
                # If decryption fails, fall back to unencrypted
                self.logger.warning("Failed to decrypt configuration, trying unencrypted")
        
        # Load unencrypted configuration
        self._load_unencrypted()
        self.logger.info("Loaded unencrypted configuration")
    
    def save(self) -> None:
        """Save configuration to file."""
        if self._fernet:
            self._save_encrypted()
        else:
            self._save_unencrypted()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.save()
    
    def delete(self, key: str) -> bool:
        """Delete a configuration value."""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if isinstance(config, dict) and k in config:
                config = config[k]
            else:
                return False
        
        if isinstance(config, dict) and keys[-1] in config:
            del config[keys[-1]]
            self.save()
            return True
        
        return False
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get an entire configuration section."""
        return self.get(section, {})
    
    def set_section(self, section: str, values: Dict[str, Any]) -> None:
        """Set an entire configuration section."""
        self.set(section, values)
    
    def backup_config(self, backup_path: str) -> bool:
        """Backup configuration to a file."""
        try:
            backup_file = Path(backup_path)
            backup_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Create backup data
            backup_data = {
                "config": self.config,
                "encrypted": self.is_encrypted(),
                "timestamp": str(datetime.now())
            }
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Configuration backed up to {backup_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to backup configuration: {e}")
            return False
    
    def restore_config(self, backup_path: str) -> bool:
        """Restore configuration from a backup file."""
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            self.config = backup_data.get("config", {})
            
            # Handle encryption restoration
            if backup_data.get("encrypted", False):
                # If backup was encrypted, we need to re-enable encryption
                # This would require the user to provide the password
                self.logger.warning("Cannot restore encrypted configuration without password")
                return False
            
            self.save()
            self.logger.info(f"Configuration restored from {backup_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to restore configuration: {e}")
            return False
    
    def reset_config(self) -> None:
        """Reset configuration to defaults."""
        self.config = {}
        self.save()
        self.logger.info("Configuration reset to defaults")
    
    def get_all_keys(self) -> list:
        """Get all configuration keys."""
        def flatten_keys(d, parent_key="", sep="."):
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(flatten_keys(v, new_key, sep=sep).items())
                else:
                    items.append((new_key, v))
            return dict(items)
        
        return list(flatten_keys(self.config).keys())
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate configuration and return any issues."""
        issues = []
        warnings = []
        
        # Check for required keys
        required_keys = [
            "providers.ollama.enabled",
            "ui.theme",
            "chat.stream_responses"
        ]
        
        for key in required_keys:
            if self.get(key) is None:
                issues.append(f"Missing required key: {key}")
        
        # Check for deprecated keys
        deprecated_keys = [
            "old_api_key_format",
            "legacy_settings"
        ]
        
        for key in deprecated_keys:
            if self.get(key) is not None:
                warnings.append(f"Deprecated key found: {key}")
        
        # Check provider configurations
        for provider in ["groq", "huggingface", "openrouter"]:
            if self.get(f"providers.{provider}.enabled") and not self.get(f"providers.{provider}.api_key"):
                warnings.append(f"Provider {provider} is enabled but no API key is set")
        
        return {
            "issues": issues,
            "warnings": warnings,
            "valid": len(issues) == 0
        }
    
    def migrate_config(self, from_version: str, to_version: str) -> bool:
        """Migrate configuration between versions."""
        try:
            if from_version == "1.0" and to_version == "2.0":
                # Example migration logic
                if self.get("ui.font_size"):
                    self.set("ui.settings.font_size", self.get("ui.font_size"))
                    self.delete("ui.font_size")
                
                self.logger.info(f"Migrated configuration from {from_version} to {to_version}")
                return True
            
            # Add more migration logic as needed
            return False
        
        except Exception as e:
            self.logger.error(f"Failed to migrate configuration: {e}")
            return False
