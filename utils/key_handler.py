"""
Key handler for managing API keys and secure storage.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Optional, List
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import getpass
from datetime import datetime


class KeyHandler:
    """Manages secure storage and retrieval of API keys."""
    
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir or self._get_default_config_dir())
        self.keys_file = self.config_dir / "api_keys.enc"
        self.key_salt_file = self.config_dir / ".key_salt"
        
        self.logger = logging.getLogger(__name__)
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize encryption
        self._master_key = None
        self._fernet = None
        self._salt = self._load_or_create_salt()
        self._keys_cache = None
        self._key_store_status = "uninitialized"
    
    def _get_default_config_dir(self) -> str:
        """Get default configuration directory."""
        home = Path.home()
        if os.name == 'nt':  # Windows
            return str(home / "AppData" / "Local" / "ChatLinuxClient")
        else:  # Linux/Mac
            return str(home / ".config" / "chat-linux-client")
    
    def _load_or_create_salt(self) -> bytes:
        """Load or create encryption salt."""
        try:
            if self.key_salt_file.exists():
                with open(self.key_salt_file, 'rb') as f:
                    return f.read()
            else:
                # Generate new salt
                salt = os.urandom(16)
                with open(self.key_salt_file, 'wb') as f:
                    f.write(salt)
                # Set file permissions
                os.chmod(self.key_salt_file, 0o600)
                return salt
        except Exception as e:
            self.logger.error(f"Failed to load/create salt: {e}")
            # Fallback to a fixed salt (not ideal but ensures functionality)
            return b'chat_linux_client_fallback_salt'
    
    def _derive_key(self, password: str) -> bytes:
        """Derive encryption key from password."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self._salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode('utf-8')))
        return key
    
    def initialize_encryption(self, password: Optional[str] = None, require_password: bool = False) -> bool:
        """Initialize encryption with password."""
        try:
            if password is None:
                # Try to get password from environment
                password = os.getenv('CHAT_CLIENT_PASSWORD')
                if not password and require_password:
                    password = getpass.getpass("Enter password for API key encryption: ")
                elif not password:
                    # No password available and not required - use a local fallback key
                    password = "chat-linux-client-default-password"
                    self.logger.warning(
                        "No password provided for API key encryption; using a local fallback key. "
                        "Set CHAT_CLIENT_PASSWORD to enable password-based encryption."
                    )
            
            self._master_key = self._derive_key(password)
            self._fernet = Fernet(self._master_key)
            
            self.logger.info("Encryption initialized successfully")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to initialize encryption: {e}")
            return False
    
    def set_key(self, provider: str, api_key: str) -> bool:
        """Store an API key for a provider."""
        if not self._fernet:
            if not self.initialize_encryption():
                return False
        
        try:
            # Load existing keys
            keys = self._load_keys()
            
            # Add or update the key
            keys[provider] = api_key
            
            # Save encrypted keys and update cache
            self._save_keys(keys)
            self._keys_cache = keys
            
            self.logger.info(f"API key stored for provider: {provider}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to store API key for {provider}: {e}")
            return False
    
    def get_key(self, provider: str) -> Optional[str]:
        """Retrieve an API key for a provider."""
        if not self._fernet:
            if not self.initialize_encryption():
                return None
        
        try:
            if self._keys_cache is None:
                self._keys_cache = self._load_keys()
            return self._keys_cache.get(provider)
        except Exception as e:
            self.logger.error(f"Failed to retrieve API key for {provider}: {e}")
            return None
    
    def delete_key(self, provider: str) -> bool:
        """Delete an API key for a provider."""
        if not self._fernet:
            if not self.initialize_encryption():
                return False
        
        try:
            keys = self._load_keys()
            
            if provider in keys:
                del keys[provider]
                self._save_keys(keys)
                self._keys_cache = keys
                self.logger.info(f"API key deleted for provider: {provider}")
                return True
            else:
                self.logger.warning(f"No API key found for provider: {provider}")
                return False
        
        except Exception as e:
            self.logger.error(f"Failed to delete API key for {provider}: {e}")
            return False
    
    def list_providers(self) -> List[str]:
        """List all providers with stored keys."""
        if not self._fernet:
            if not self.initialize_encryption():
                return []
        
        try:
            if self._keys_cache is None:
                self._keys_cache = self._load_keys()
            return list(self._keys_cache.keys())
        except Exception as e:
            self.logger.error(f"Failed to list providers: {e}")
            return []
    
    def _load_keys(self) -> Dict[str, str]:
        """Load encrypted keys from file."""
        try:
            if not self.keys_file.exists():
                self._key_store_status = "missing-file"
                return {}

            with open(self.keys_file, 'rb') as f:
                encrypted_data = f.read()

            decrypted_data = self._fernet.decrypt(encrypted_data)
            keys = json.loads(decrypted_data.decode('utf-8'))
            self._keys_cache = keys
            self._key_store_status = "ok"
            return keys

        except InvalidToken:
            self.logger.warning(
                "Stored API keys could not be decrypted with the current encryption key. "
                "If you have changed the encryption password, please restore or re-enter your keys."
            )
            self._keys_cache = {}
            self._key_store_status = "invalid-token"
            return {}
        except json.JSONDecodeError:
            self.logger.warning(
                "Stored API keys are corrupt or not valid JSON. The key store will be ignored."
            )
            self._keys_cache = {}
            self._key_store_status = "corrupt-json"
            return {}
        except Exception as e:
            self.logger.error(f"Failed to load keys: {e}")
            self._keys_cache = {}
            self._key_store_status = "load-error"
            return {}

    def get_key_store_status(self) -> str:
        """Return last key-store load status for UI recovery messaging."""
        return self._key_store_status
    
    def _save_keys(self, keys: Dict[str, str]) -> None:
        """Save encrypted keys to file."""
        try:
            keys_json = json.dumps(keys, ensure_ascii=False)
            encrypted_data = self._fernet.encrypt(keys_json.encode('utf-8'))
            
            with open(self.keys_file, 'wb') as f:
                f.write(encrypted_data)
            
            # Set file permissions
            os.chmod(self.keys_file, 0o600)
        
        except Exception as e:
            self.logger.error(f"Failed to save keys: {e}")
            raise
    
    def change_password(self, old_password: str, new_password: str) -> bool:
        """Change the encryption password."""
        try:
            # Initialize with old password
            old_key = self._derive_key(old_password)
            old_fernet = Fernet(old_key)
            
            # Load keys with old password
            if self.keys_file.exists():
                with open(self.keys_file, 'rb') as f:
                    encrypted_data = f.read()
                
                decrypted_data = old_fernet.decrypt(encrypted_data)
                keys = json.loads(decrypted_data.decode('utf-8'))
            else:
                keys = {}
            
            # Re-initialize with new password
            self._master_key = self._derive_key(new_password)
            self._fernet = Fernet(self._master_key)
            
            # Save keys with new password
            self._save_keys(keys)
            
            self.logger.info("Password changed successfully")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to change password: {e}")
            return False
    
    def export_keys(self, export_path: str, password: Optional[str] = None) -> bool:
        """Export keys to a file (unencrypted for backup purposes)."""
        if not self._fernet:
            if not self.initialize_encryption(password):
                return False
        
        try:
            keys = self._load_keys()
            
            # Create export data
            export_data = {
                "version": "1.0",
                "exported_at": str(datetime.now()),
                "keys": keys
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            # Set restrictive permissions
            os.chmod(export_path, 0o600)
            
            self.logger.info(f"Keys exported to {export_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to export keys: {e}")
            return False
    
    def import_keys(self, import_path: str, password: Optional[str] = None) -> bool:
        """Import keys from a file."""
        if not self._fernet:
            if not self.initialize_encryption(password):
                return False
        
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            keys = import_data.get("keys", {})
            
            # Merge with existing keys
            existing_keys = self._load_keys()
            existing_keys.update(keys)
            
            # Save merged keys
            self._save_keys(existing_keys)
            
            self.logger.info(f"Keys imported from {import_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to import keys: {e}")
            return False
    
    def clear_all_keys(self) -> bool:
        """Clear all stored API keys."""
        try:
            if self.keys_file.exists():
                self.keys_file.unlink()
            
            self.logger.info("All API keys cleared")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to clear keys: {e}")
            return False
    
    def validate_key_format(self, provider: str, api_key: str) -> bool:
        """Validate API key format for specific providers."""
        if not api_key:
            return False
        
        # Basic format validation for different providers
        formats = {
            "openai": lambda k: k.startswith("sk-") and len(k) >= 20,
            "groq": lambda k: k.startswith("gsk_") and len(k) >= 20,
            "huggingface": lambda k: len(k) >= 20,  # HF keys vary in format
            "openrouter": lambda k: k.startswith("sk-or-") and len(k) >= 20,
        }
        
        validator = formats.get(provider.lower(), lambda k: len(k) >= 10)
        return validator(api_key)
    
    def get_key_info(self) -> Dict[str, any]:
        """Get information about stored keys."""
        if not self._fernet:
            if not self.initialize_encryption():
                return {}
        
        try:
            keys = self._load_keys()
            return {
                "total_keys": len(keys),
                "providers": list(keys.keys()),
                "encryption_enabled": self._fernet is not None,
                "keys_file_exists": self.keys_file.exists(),
                "salt_file_exists": self.key_salt_file.exists()
            }
        except Exception as e:
            self.logger.error(f"Failed to get key info: {e}")
            return {}
    
    def test_key(self, provider: str, api_key: Optional[str] = None) -> bool:
        """Test if an API key is valid (basic format check only)."""
        if api_key is None:
            api_key = self.get_key(provider)
        
        if not api_key:
            return False
        
        return self.validate_key_format(provider, api_key)
