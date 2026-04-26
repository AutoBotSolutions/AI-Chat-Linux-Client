"""
Model manager for handling AI model information and capabilities.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class ModelType(Enum):
    """Types of AI models."""
    CHAT = "chat"
    COMPLETION = "completion"
    INSTRUCTION = "instruction"
    CODE = "code"
    MULTIMODAL = "multimodal"


@dataclass
class ModelInfo:
    """Information about an AI model."""
    name: str
    provider: str
    model_type: ModelType
    context_length: Optional[int] = None
    max_tokens: Optional[int] = None
    supports_streaming: bool = True
    supports_function_calling: bool = False
    cost_per_1k_tokens: Optional[float] = None
    speed_rating: int = 3  # 1-5, 5 being fastest
    quality_rating: int = 3  # 1-5, 5 being highest quality
    description: str = ""
    is_local: bool = False


class ModelManager:
    """Manages AI model information and selection logic."""
    
    def __init__(self):
        self.models: Dict[str, ModelInfo] = {}
        self._register_default_models()
    
    def _register_default_models(self) -> None:
        """Register default models for each provider."""
        
        # Ollama models (local)
        self.models.update({
            "llama2": ModelInfo(
                name="llama2",
                provider="ollama",
                model_type=ModelType.CHAT,
                context_length=4096,
                supports_streaming=True,
                speed_rating=2,
                quality_rating=4,
                description="Meta's Llama 2 model",
                is_local=True
            ),
            "codellama": ModelInfo(
                name="codellama",
                provider="ollama",
                model_type=ModelType.CODE,
                context_length=4096,
                supports_streaming=True,
                speed_rating=2,
                quality_rating=4,
                description="Code-specialized Llama model",
                is_local=True
            ),
            "mistral": ModelInfo(
                name="mistral",
                provider="ollama",
                model_type=ModelType.CHAT,
                context_length=8192,
                supports_streaming=True,
                speed_rating=3,
                quality_rating=4,
                description="Mistral AI model",
                is_local=True
            )
        })
        
        # Groq models
        self.models.update({
            "llama3-8b-8192": ModelInfo(
                name="llama3-8b-8192",
                provider="groq",
                model_type=ModelType.CHAT,
                context_length=8192,
                supports_streaming=True,
                speed_rating=5,
                quality_rating=4,
                cost_per_1k_tokens=0.05,
                description="Llama 3 8B model on Groq"
            ),
            "mixtral-8x7b-32768": ModelInfo(
                name="mixtral-8x7b-32768",
                provider="groq",
                model_type=ModelType.CHAT,
                context_length=32768,
                supports_streaming=True,
                speed_rating=5,
                quality_rating=5,
                cost_per_1k_tokens=0.24,
                description="Mixtral 8x7B model on Groq"
            ),
            "gemma-7b-it": ModelInfo(
                name="gemma-7b-it",
                provider="groq",
                model_type=ModelType.CHAT,
                context_length=8192,
                supports_streaming=True,
                speed_rating=5,
                quality_rating=3,
                cost_per_1k_tokens=0.07,
                description="Gemma 7B instruction-tuned model on Groq"
            )
        })
        
        # HuggingFace models
        self.models.update({
            "microsoft/DialoGPT-medium": ModelInfo(
                name="microsoft/DialoGPT-medium",
                provider="huggingface",
                model_type=ModelType.CHAT,
                context_length=1024,
                supports_streaming=False,
                speed_rating=2,
                quality_rating=3,
                description="Microsoft's conversational AI model"
            ),
            "mistralai/Mistral-7B-Instruct-v0.2": ModelInfo(
                name="mistralai/Mistral-7B-Instruct-v0.2",
                provider="huggingface",
                model_type=ModelType.INSTRUCTION,
                context_length=8192,
                supports_streaming=False,
                speed_rating=2,
                quality_rating=4,
                description="Mistral 7B instruction-tuned model"
            )
        })
        
        # OpenRouter models (representative sample)
        self.models.update({
            "openai/gpt-4": ModelInfo(
                name="openai/gpt-4",
                provider="openrouter",
                model_type=ModelType.CHAT,
                context_length=8192,
                supports_streaming=True,
                supports_function_calling=True,
                speed_rating=2,
                quality_rating=5,
                cost_per_1k_tokens=0.03,
                description="OpenAI GPT-4 via OpenRouter"
            ),
            "openai/gpt-3.5-turbo": ModelInfo(
                name="openai/gpt-3.5-turbo",
                provider="openrouter",
                model_type=ModelType.CHAT,
                context_length=4096,
                supports_streaming=True,
                supports_function_calling=True,
                speed_rating=4,
                quality_rating=4,
                cost_per_1k_tokens=0.002,
                description="OpenAI GPT-3.5 Turbo via OpenRouter"
            ),
            "anthropic/claude-3-haiku": ModelInfo(
                name="anthropic/claude-3-haiku",
                provider="openrouter",
                model_type=ModelType.CHAT,
                context_length=200000,
                supports_streaming=True,
                speed_rating=4,
                quality_rating=4,
                cost_per_1k_tokens=0.00025,
                description="Anthropic Claude 3 Haiku via OpenRouter"
            )
        })
    
    def get_model_info(self, model_name: str) -> Optional[ModelInfo]:
        """Get information about a specific model."""
        return self.models.get(model_name)
    
    def get_models_by_provider(self, provider: str) -> List[ModelInfo]:
        """Get all models from a specific provider."""
        return [model for model in self.models.values() if model.provider == provider]
    
    def get_models_by_type(self, model_type: ModelType) -> List[ModelInfo]:
        """Get all models of a specific type."""
        return [model for model in self.models.values() if model.model_type == model_type]
    
    def get_local_models(self) -> List[ModelInfo]:
        """Get all local models."""
        return [model for model in self.models.values() if model.is_local]
    
    def get_cloud_models(self) -> List[ModelInfo]:
        """Get all cloud-based models."""
        return [model for model in self.models.values() if not model.is_local]
    
    def filter_models(
        self,
        provider: Optional[str] = None,
        model_type: Optional[ModelType] = None,
        supports_streaming: Optional[bool] = None,
        supports_function_calling: Optional[bool] = None,
        min_speed_rating: Optional[int] = None,
        min_quality_rating: Optional[int] = None,
        is_local: Optional[bool] = None
    ) -> List[ModelInfo]:
        """Filter models based on criteria."""
        filtered = list(self.models.values())
        
        if provider:
            filtered = [m for m in filtered if m.provider == provider]
        
        if model_type:
            filtered = [m for m in filtered if m.model_type == model_type]
        
        if supports_streaming is not None:
            filtered = [m for m in filtered if m.supports_streaming == supports_streaming]
        
        if supports_function_calling is not None:
            filtered = [m for m in filtered if m.supports_function_calling == supports_function_calling]
        
        if min_speed_rating is not None:
            filtered = [m for m in filtered if m.speed_rating >= min_speed_rating]
        
        if min_quality_rating is not None:
            filtered = [m for m in filtered if m.quality_rating >= min_quality_rating]
        
        if is_local is not None:
            filtered = [m for m in filtered if m.is_local == is_local]
        
        return filtered
    
    def get_best_model_for_task(
        self,
        task_type: str,
        priority_speed: bool = False,
        priority_cost: bool = False,
        local_only: bool = False
    ) -> Optional[ModelInfo]:
        """Get the best model for a specific task."""
        
        # Filter based on local preference
        models = self.get_local_models() if local_only else list(self.models.values())
        
        if not models:
            return None
        
        # Task-specific model selection
        if task_type == "code":
            code_models = [m for m in models if m.model_type == ModelType.CODE]
            if code_models:
                models = code_models
        
        elif task_type == "chat":
            chat_models = [m for m in models if m.model_type in [ModelType.CHAT, ModelType.INSTRUCTION]]
            if chat_models:
                models = chat_models
        
        # Sort based on priority
        if priority_speed:
            models.sort(key=lambda m: (-m.speed_rating, m.quality_rating))
        elif priority_cost:
            # Prefer local models (free), then by cost
            models.sort(key=lambda m: (0 if m.is_local else 1, m.cost_per_1k_tokens or float('inf')))
        else:
            # Balance speed and quality
            models.sort(key=lambda m: (-(m.speed_rating + m.quality_rating), m.cost_per_1k_tokens or float('inf')))
        
        return models[0] if models else None
    
    def add_model(self, model_info: ModelInfo) -> None:
        """Add a new model to the manager."""
        self.models[model_info.name] = model_info
    
    def remove_model(self, model_name: str) -> bool:
        """Remove a model from the manager."""
        if model_name in self.models:
            del self.models[model_name]
            return True
        return False
    
    def get_all_models(self) -> List[ModelInfo]:
        """Get all registered models."""
        return list(self.models.values())
    
    def get_model_summary(self) -> Dict[str, Any]:
        """Get a summary of available models."""
        total = len(self.models)
        local = len(self.get_local_models())
        cloud = len(self.get_cloud_models())
        
        providers = {}
        for model in self.models.values():
            if model.provider not in providers:
                providers[model.provider] = 0
            providers[model.provider] += 1
        
        return {
            "total_models": total,
            "local_models": local,
            "cloud_models": cloud,
            "providers": providers,
            "supports_streaming": len([m for m in self.models.values() if m.supports_streaming]),
            "supports_function_calling": len([m for m in self.models.values() if m.supports_function_calling])
        }
