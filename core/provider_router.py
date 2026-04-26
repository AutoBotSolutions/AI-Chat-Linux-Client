"""
Provider router for intelligent model selection and request routing.
"""

import asyncio
from typing import Dict, List, Optional, Tuple, AsyncGenerator
from enum import Enum
import logging

from .api_client import BaseAPIClient
from .ollama_client import OllamaClient
from .groq_client import GroqClient
from .huggingface_client import HuggingFaceClient
from .openrouter_client import OpenRouterClient
from .openai_client import OpenAIClient


class RoutingStrategy(Enum):
    """Routing strategies for model selection."""
    COST_OPTIMAL = "cost_optimal"
    SPEED_OPTIMAL = "speed_optimal"
    QUALITY_OPTIMAL = "quality_optimal"
    OFFLINE_FIRST = "offline_first"
    USER_PREFERRED = "user_preferred"


class ProviderRouter:
    """Intelligent routing engine for AI providers."""
    
    def __init__(self, settings_manager=None):
        self.providers: Dict[str, BaseAPIClient] = {}
        self.settings_manager = settings_manager
        self.routing_strategy = RoutingStrategy.OFFLINE_FIRST
        self.user_preferences: Dict[str, str] = {}
        self.logger = logging.getLogger(__name__)
    
    async def initialize_providers(self, config: Dict) -> None:
        """Initialize all configured providers."""
        # Initialize Ollama if enabled in configuration
        ollama_config = config.get("ollama", {})
        if ollama_config.get("enabled", True):
            ollama_client = OllamaClient(
                base_url=ollama_config.get("base_url", "http://localhost:11434"),
                timeout=ollama_config.get("timeout", 30),
                max_retries=ollama_config.get("max_retries", 3),
            )
            try:
                if await ollama_client.test_connection():
                    ollama_client.is_available = True
                    self.providers["ollama"] = ollama_client
                    self.logger.info("Ollama provider initialized successfully")
                else:
                    ollama_client.is_available = False
                    self.providers["ollama"] = ollama_client
                    self.logger.warning(f"Ollama provider not available: connection test failed")
            except Exception as e:
                ollama_client.is_available = False
                self.providers["ollama"] = ollama_client
                self.logger.warning(f"Ollama provider not available: {e}")
        else:
            self.logger.info("Ollama provider is disabled in configuration")
        
        # Initialize Groq if API key is provided and enabled
        groq_config = config.get("groq", {})
        if groq_config.get("api_key") and groq_config.get("enabled", True):
            groq_client = GroqClient(groq_config["api_key"])
            try:
                if await groq_client.test_connection():
                    groq_client.is_available = True
                    self.providers["groq"] = groq_client
                    self.logger.info("Groq provider initialized successfully")
                else:
                    groq_client.is_available = False
                    self.providers["groq"] = groq_client
                    self.logger.warning(f"Groq provider not available: connection test failed")
            except Exception as e:
                groq_client.is_available = False
                self.providers["groq"] = groq_client
                self.logger.warning(f"Groq provider not available: {e}")
        else:
            self.logger.info("Groq provider skipped - no API key or disabled")
        
        # Initialize HuggingFace if API key is provided and enabled
        hf_config = config.get("huggingface", {})
        if hf_config.get("api_key") and hf_config.get("enabled", True):
            hf_client = HuggingFaceClient(hf_config["api_key"])
            try:
                if await hf_client.test_connection():
                    hf_client.is_available = True
                    self.providers["huggingface"] = hf_client
                    self.logger.info("HuggingFace provider initialized successfully")
                else:
                    hf_client.is_available = False
                    self.providers["huggingface"] = hf_client
                    self.logger.warning(f"HuggingFace provider not available: connection test failed")
            except Exception as e:
                hf_client.is_available = False
                self.providers["huggingface"] = hf_client
                self.logger.warning(f"HuggingFace provider not available: {e}")
        else:
            self.logger.info("HuggingFace provider skipped - no API key or disabled")
        
        # Initialize OpenRouter if API key is provided and enabled
        or_config = config.get("openrouter", {})
        if or_config.get("api_key") and or_config.get("enabled", True):
            or_client = OpenRouterClient(or_config["api_key"])
            try:
                if await or_client.test_connection():
                    or_client.is_available = True
                    self.providers["openrouter"] = or_client
                    self.logger.info("OpenRouter provider initialized successfully")
                else:
                    or_client.is_available = False
                    self.providers["openrouter"] = or_client
                    self.logger.warning(f"OpenRouter provider not available: connection test failed")
            except Exception as e:
                or_client.is_available = False
                self.providers["openrouter"] = or_client
                self.logger.warning(f"OpenRouter provider not available: {e}")
        else:
            self.logger.info("OpenRouter provider skipped - no API key or disabled")
        
        # Initialize OpenAI if API key is provided and enabled
        openai_config = config.get("openai", {})
        if openai_config.get("api_key") and openai_config.get("enabled", True):
            openai_client = OpenAIClient(openai_config["api_key"])
            try:
                if await openai_client.test_connection():
                    openai_client.is_available = True
                    self.providers["openai"] = openai_client
                    self.logger.info("OpenAI provider initialized successfully")
                else:
                    openai_client.is_available = False
                    self.providers["openai"] = openai_client
                    self.logger.warning(f"OpenAI provider not available: connection test failed")
            except Exception as e:
                openai_client.is_available = False
                self.providers["openai"] = openai_client
                self.logger.warning(f"OpenAI provider not available: {e}")
        else:
            self.logger.info("OpenAI provider skipped - no API key or disabled")
        
        self.logger.info(f"Initialized {len(self.providers)} providers: {list(self.providers.keys())}")
    
    async def get_available_providers(self) -> List[str]:
        """Get list of available and connected providers."""
        available = [name for name, provider in self.providers.items() if provider.is_available]
        return available

    async def get_all_models(self) -> Dict[str, List[str]]:
        """Get all models from all configured providers."""
        models = {}
        tasks = []
        
        # Get models from available providers
        for name, provider in self.providers.items():
            if provider.is_available:
                tasks.append((name, provider.list_models()))
        
        if tasks:
            results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
            
            for (name, _), result in zip(tasks, results):
                fallback = self._get_fallback_models(name)
                if isinstance(result, list) and result:
                    # Prefer live provider models so selections remain functional.
                    models[name] = self._merge_models(result, [])
                else:
                    models[name] = fallback
                    self.logger.error(f"Failed to get models from {name}: {result}")
        
        # Add fallback models for configured but unavailable providers
        for name, provider in self.providers.items():
            if name not in models:
                models[name] = self._get_fallback_models(name)
                self.logger.info(f"Added fallback models for unavailable provider: {name}")
        
        return models
    
    def _get_fallback_models(self, provider_name: str) -> List[str]:
        """Get fallback model list for unavailable providers."""
        fallback_models = {
            "ollama": [
                "llama3.2:1b",
                "llama3.2:3b",
                "llama3.1:8b",
                "llama3.1:70b",
                "llama3:8b",
                "llama3:70b",
                "qwen2.5:0.5b",
                "qwen2.5:1.5b",
                "qwen2.5:3b",
                "qwen2.5:7b",
                "phi3.5:3.8b",
                "phi3:mini",
                "gemma2:2b",
                "gemma2:9b",
                "gemma2:27b",
                "deepseek-r1:7b",
                "deepseek-r1:8b",
                "deepseek-r1:14b",
                "deepseek-r1:32b",
                "deepseek-r1:70b",
                "deepseek-coder-v2:16b",
                "mistral:7b",
                "mixtral:8x7b",
                "nous-hermes2:10.7b",
                "command-r:35b",
                "codellama:7b",
                "codellama:13b",
                "starcoder2:15b",
                "llama2",
                "llama2:7b",
                "llama2:13b",
                "llama2:70b",
                "mistral",
                "phi",
                "phi:latest",
                "gemma:7b"
            ],
            "openai": [
                "gpt-5",
                "gpt-5-mini",
                "gpt-5-nano",
                "gpt-4.1",
                "gpt-4.1-mini",
                "gpt-4.1-nano",
                "gpt-4o-realtime-preview",
                "gpt-4o-audio-preview",
                "gpt-3.5-turbo",
                "gpt-3.5-turbo-16k", 
                "gpt-4",
                "gpt-4-turbo",
                "gpt-4o",
                "gpt-4o-mini"
            ],
            "groq": [
                "llama-3.3-70b-versatile",
                "llama-3.1-8b-instant",
                "llama-3.1-70b-versatile",
                "llama3-8b-8192",
                "llama3-70b-8192",
                "mixtral-8x7b-32768",
                "gemma-7b-it",
                "gemma2-9b-it",
                "qwen/qwen3-32b",
                "qwen/qwen-2.5-32b",
                "moonshotai/kimi-k2-instruct",
                "deepseek-r1-distill-llama-70b",
                "deepseek-r1-distill-qwen-32b"
            ],
            "huggingface": [
                "meta-llama/Llama-3.1-8B-Instruct",
                "meta-llama/Llama-3.1-70B-Instruct",
                "Qwen/Qwen2.5-7B-Instruct",
                "Qwen/Qwen2.5-14B-Instruct",
                "Qwen/Qwen2.5-32B-Instruct",
                "mistralai/Mixtral-8x7B-Instruct-v0.1",
                "mistralai/Mistral-Nemo-Instruct-2407",
                "google/gemma-2-9b-it",
                "google/gemma-2-27b-it",
                "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
                "deepseek-ai/DeepSeek-R1-Distill-Llama-70B",
                "microsoft/DialoGPT-medium",
                "microsoft/DialoGPT-large",
                "facebook/blenderbot-400M-distill",
                "google/flan-t5-large",
                "mistralai/Mistral-7B-Instruct-v0.2"
            ],
            "openrouter": [
                "openai/gpt-5",
                "openai/gpt-5-mini",
                "openai/gpt-4.1",
                "openai/gpt-4.1-mini",
                "openai/gpt-3.5-turbo",
                "openai/gpt-4",
                "openai/gpt-4-turbo",
                "openai/gpt-4o",
                "openai/gpt-4o-mini",
                "meta-llama/llama-3.1-8b-instruct",
                "meta-llama/llama-3.1-70b-instruct",
                "meta-llama/llama-3.3-70b-instruct",
                "qwen/qwen-2.5-72b-instruct",
                "qwen/qwen-2.5-coder-32b-instruct",
                "anthropic/claude-3-haiku",
                "anthropic/claude-3.5-sonnet",
                "anthropic/claude-3.7-sonnet",
                "anthropic/claude-sonnet-4",
                "google/gemini-2.0-flash-001",
                "google/gemini-2.0-pro-exp-02-05",
                "deepseek/deepseek-r1",
                "x-ai/grok-2",
                "mistralai/mistral-large"
            ]
        }
        return fallback_models.get(provider_name, [])

    @staticmethod
    def _merge_models(primary: List[str], fallback: List[str]) -> List[str]:
        """Merge model lists while preserving order and removing duplicates."""
        merged = []
        seen = set()
        for model in (primary or []) + (fallback or []):
            if not isinstance(model, str):
                continue
            value = model.strip()
            if not value or value in seen:
                continue
            seen.add(value)
            merged.append(value)
        return merged
    
    async def select_best_provider(
        self, 
        model: Optional[str] = None,
        strategy: Optional[RoutingStrategy] = None,
        task_complexity: str = "medium"
    ) -> Tuple[str, BaseAPIClient]:
        """Select the best provider based on strategy and requirements."""
        strategy = strategy or self.routing_strategy
        available_providers = await self.get_available_providers()
        
        if not available_providers:
            # If no providers are active, allow Ollama fallback if it is configured.
            if "ollama" in self.providers:
                return "ollama", self.providers["ollama"]
            configured_providers = list(self.providers.keys())
            if configured_providers:
                raise Exception(
                    "No AI providers are currently available. "
                    "Please ensure Ollama is running at the configured base URL or configure another enabled provider."
                )
            else:
                raise Exception("No AI providers configured. Please configure at least one provider in settings.")
        
        # If specific model is requested, find its provider
        if model:
            # Extract provider name from model if it's in format "provider/model"
            if '/' in model:
                requested_provider, model_name = model.split('/', 1)
                
                # Check if the requested provider is available
                if requested_provider in available_providers:
                    provider = self.providers[requested_provider]
                    models = await provider.list_models()
                    if model_name in models:
                        return requested_provider, provider
                else:
                    # Provider is not available, give clear error
                    raise Exception(f"Provider '{requested_provider}' is not available. Please check your API key configuration for {requested_provider}.")
            else:
                # Model name without provider prefix, search in available providers
                for provider_name in available_providers:
                    provider = self.providers[provider_name]
                    models = await provider.list_models()
                    if model in models:
                        return provider_name, provider
        
        # Apply routing strategy
        if strategy == RoutingStrategy.OFFLINE_FIRST:
            if "ollama" in available_providers:
                return "ollama", self.providers["ollama"]
            # Fallback to next available
            return available_providers[0], self.providers[available_providers[0]]
        
        elif strategy == RoutingStrategy.SPEED_OPTIMAL:
            # Prefer Groq for speed, then Ollama
            if "groq" in available_providers:
                return "groq", self.providers["groq"]
            elif "ollama" in available_providers:
                return "ollama", self.providers["ollama"]
            else:
                return available_providers[0], self.providers[available_providers[0]]
        
        elif strategy == RoutingStrategy.COST_OPTIMAL:
            # Prefer Ollama (free), then others
            if "ollama" in available_providers:
                return "ollama", self.providers["ollama"]
            else:
                return available_providers[0], self.providers[available_providers[0]]
        
        elif strategy == RoutingStrategy.QUALITY_OPTIMAL:
            # Prefer OpenRouter or HuggingFace for quality
            if "openrouter" in available_providers:
                return "openrouter", self.providers["openrouter"]
            elif "huggingface" in available_providers:
                return "huggingface", self.providers["huggingface"]
            else:
                return available_providers[0], self.providers[available_providers[0]]
        
        elif strategy == RoutingStrategy.USER_PREFERRED:
            # Use user's preferred provider if available
            preferred = self.user_preferences.get("default_provider")
            if preferred and preferred in available_providers:
                return preferred, self.providers[preferred]
            else:
                return available_providers[0], self.providers[available_providers[0]]
        
        # Default fallback
        return available_providers[0], self.providers[available_providers[0]]
    
    async def route_request(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        strategy: Optional[RoutingStrategy] = None
    ):
        """Route a request to the best available provider."""
        provider_name, provider = await self.select_best_provider(model, strategy)
        
        # Extract model name if in provider/model format
        actual_model = model
        if model and '/' in model:
            _, actual_model = model.split('/', 1)
        
        # If no specific model requested, get the first available from provider
        if not actual_model:
            models = await provider.list_models()
            if models:
                actual_model = models[0]
            else:
                raise Exception(f"No models available for provider {provider_name}")
        
        self.logger.info(f"Routing request to {provider_name} with model {actual_model}")
        
        # Handle streaming by yielding chunks
        if stream:
            async for chunk in provider.chat_completion(
                messages=messages,
                model=actual_model,
                stream=stream,
                temperature=temperature,
                max_tokens=max_tokens
            ):
                yield chunk
        else:
            # For non-streaming, collect all chunks and yield the complete response
            response = ""
            async for chunk in provider.chat_completion(
                messages=messages,
                model=actual_model,
                stream=stream,
                temperature=temperature,
                max_tokens=max_tokens
            ):
                response += chunk
            yield response
    
    def set_routing_strategy(self, strategy: RoutingStrategy) -> None:
        """Set the default routing strategy."""
        self.routing_strategy = strategy
    
    def set_user_preference(self, key: str, value: str) -> None:
        """Set user preference."""
        self.user_preferences[key] = value
    
    def get_provider_info(self) -> Dict[str, Dict]:
        """Get information about all providers."""
        info = {}
        for name, provider in self.providers.items():
            info[name] = {
                "name": provider.get_provider_name(),
                "available": provider.is_available,
                "models": []  # Would need async call to populate
            }
        return info
