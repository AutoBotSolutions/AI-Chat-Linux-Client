"""
Base API client interface for all AI providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import json


class BaseAPIClient(ABC):
    """Abstract base class for all AI provider clients."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key
        self.base_url = base_url
        self.is_available = False
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """Test if the provider is accessible."""
        pass
    
    @abstractmethod
    async def list_models(self) -> List[str]:
        """Get list of available models from this provider."""
        pass
    
    @abstractmethod
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        model: str,
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ):
        """Send chat completion request."""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the provider name."""
        pass
    
    def get_model_info(self, model: str) -> Dict[str, any]:
        """Get information about a specific model."""
        return {
            "name": model,
            "provider": self.get_provider_name(),
            "supports_streaming": True,
            "max_tokens": None,
            "context_length": None
        }
