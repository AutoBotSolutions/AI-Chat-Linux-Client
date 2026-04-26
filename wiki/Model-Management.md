# Model Management

This guide covers how models are managed, selected, and configured in Chat Linux Client.

## Table of Contents

- [Overview](#overview)
- [Model Information](#model-information)
- [Model Selection](#model-selection)
- [Model Configuration](#model-configuration)
- [Custom Models](#custom-models)
- [Model Performance](#model-performance)

## Overview

Chat Linux Client uses a sophisticated model management system (`core/model_manager.py`) to:

- Track available models from all providers
- Provide model metadata and capabilities
- Enable intelligent model selection
- Support custom model configurations

### Model Properties

Each model has the following properties:

- **Name**: Model identifier (e.g., `llama3.2:1b`)
- **Provider**: AI provider (e.g., `ollama`, `groq`)
- **Context Window**: Maximum input tokens
- **Max Output**: Maximum output tokens
- **Cost**: Cost per 1K tokens (if applicable)
- **Speed Rating**: Relative speed (1-10)
- **Quality Rating**: Relative quality (1-10)
- **Is Local**: Whether model runs locally

## Model Information

### Built-in Models

The system includes pre-configured models for each provider:

#### Ollama Models

| Model | Size | Context | Speed | Quality |
|-------|------|---------|-------|---------|
| llama3.2:1b | 1.3GB | 8K | 10 | 6 |
| qwen2.5:3b | 1.9GB | 32K | 8 | 7 |
| phi3.5:3.8b | 2.2GB | 12K | 7 | 8 |
| mistral:7b | 4.4GB | 32K | 5 | 9 |

#### Groq Models

| Model | Context | Speed | Quality | Cost |
|-------|---------|-------|---------|------|
| llama-3.1-8b-instant | 8K | 10 | 8 | Free tier |
| llama-3.1-70b-versatile | 8K | 7 | 9 | Free tier |
| mixtral-8x7b-32768 | 32K | 6 | 9 | Free tier |

#### OpenAI Models

| Model | Context | Speed | Quality | Cost |
|-------|---------|-------|---------|------|
| gpt-4o | 128K | 8 | 10 | $5/1M input |
| gpt-4-turbo | 128K | 7 | 9 | $10/1M input |
| gpt-3.5-turbo | 16K | 9 | 7 | $0.5/1M input |

#### HuggingFace Models

| Model | Context | Speed | Quality | Cost |
|-------|---------|-------|---------|------|
| meta-llama/Llama-2-7b-chat-hf | 4K | 6 | 8 | Free tier |
| mistralai/Mistral-7B-Instruct-v0.2 | 8K | 7 | 9 | Free tier |

#### OpenRouter Models

| Model | Context | Speed | Quality | Cost |
|-------|---------|-------|---------|------|
| anthropic/claude-3-opus | 200K | 5 | 10 | $15/1M input |
| openai/gpt-4-turbo | 128K | 7 | 9 | $10/1M input |

### Model Metadata

Models are represented as data classes:

```python
@dataclass
class ModelInfo:
    name: str
    provider: str
    context_window: int
    max_output: int
    cost_per_1k_tokens: Optional[float] = None
    speed_rating: int = 5
    quality_rating: int = 5
    is_local: bool = False
```

## Model Selection

### Automatic Selection

The system can automatically select models based on routing strategy:

#### OFFLINE_FIRST

Prioritizes local models, falls back to cloud:

```python
models = model_manager.get_models(strategy="offline_first")
# Returns: [local models first, then cloud models]
```

#### SPEED_OPTIMAL

Prioritizes fast models:

```python
models = model_manager.get_models(strategy="speed_optimal")
# Returns: [Groq, fast local models, others]
```

#### COST_OPTIMAL

Prioritizes free/cheap models:

```python
models = model_manager.get_models(strategy="cost_optimal")
# Returns: [free local models, free cloud models, paid]
```

#### QUALITY_OPTIMAL

Prioritizes high-quality models:

```python
models = model_manager.get_models(strategy="quality_optimal")
# Returns: [GPT-4, Claude, capable local models]
```

### Manual Selection

Users can manually select models from the dropdown:

```python
model = model_manager.get_model("ollama/llama3.2:1b")
```

### Filtering Models

Filter models by criteria:

```python
# Get only local models
local_models = model_manager.filter_models(is_local=True)

# Get models with large context
large_context = model_manager.filter_models(min_context=32000)

# Get fast models
fast_models = model_manager.filter_models(min_speed=8)
```

## Model Configuration

### Adding Custom Models

Add custom models in `core/model_manager.py`:

```python
# In get_all_models() method
ModelInfo(
    name="custom-model",
    provider="ollama",
    context_window=4096,
    max_output=2048,
    cost_per_1k_tokens=0.0,
    speed_rating=7,
    quality_rating=8,
    is_local=True
)
```

### Model Profiles

Define profiles for specific use cases:

```python
profiles = {
    "fast": {
        "model": "ollama/llama3.2:1b",
        "max_tokens": 64,
        "char_budget": 900
    },
    "balanced": {
        "model": "ollama/mistral:7b",
        "max_tokens": 512,
        "char_budget": 3000
    }
}
```

### Context Window Management

The system manages context windows to prevent exceeding model limits:

```python
# Calculate available context
available = model.context_window - used_tokens

# Truncate if necessary
if len(prompt) > available:
    prompt = prompt[-available:]
```

## Custom Models

### Adding Ollama Models

Pull new models from Ollama:

```bash
ollama pull custom-model-name
```

Then register in `model_manager.py`:

```python
ModelInfo(
    name="custom-model-name",
    provider="ollama",
    context_window=4096,
    max_output=2048,
    is_local=True
)
```

### Adding Custom Provider Models

For custom providers, implement model listing:

```python
async def list_models(self):
    """List available models for custom provider."""
    response = await self._get("/models")
    return [ModelInfo(...) for model in response["models"]]
```

## Model Performance

### Performance Metrics

Track model performance:

```python
metrics = {
    "response_time": 1.5,  # seconds
    "tokens_per_second": 50,
    "total_tokens": 75,
    "context_used": 1000
}
```

### Performance Optimization

#### For Speed

- Use lightweight models (llama3.2:1b)
- Reduce max tokens
- Use Groq for cloud models
- Enable streaming

#### For Quality

- Use capable models (GPT-4, mistral:7b)
- Increase temperature slightly
- Provide more context
- Use larger context windows

#### For Cost

- Use local models (Ollama)
- Use free tier cloud models
- Limit max tokens
- Use cost-optimal routing

### Benchmarking Models

Compare model performance:

```python
# Test response time
start = time.time()
response = await client.chat_completion(prompt, model)
duration = time.time() - start

# Test quality
quality_score = evaluate_quality(response)
```

## Model Updates

### Updating Model Information

When providers add new models, update `model_manager.py`:

1. Check provider documentation
2. Add new model to model list
3. Update model metadata
4. Test new model
5. Update documentation

### Deprecating Models

Remove or mark deprecated models:

```python
ModelInfo(
    name="old-model",
    provider="ollama",
    context_window=2048,
    max_output=1024,
    is_local=True,
    deprecated=True  # Mark as deprecated
)
```

## Troubleshooting

### Model Not Showing

If a model doesn't appear in the dropdown:

1. Verify model is registered in `model_manager.py`
2. Check provider is enabled
3. Ensure Ollama model is pulled (for local models)
4. Check API key is valid (for cloud models)
5. Run system checks

### Model Performance Poor

If a model performs poorly:

1. Check system resources
2. Try a lighter model
3. Reduce context window
4. Check network connection (for cloud models)
5. Update model version

### Context Window Exceeded

If you get context window errors:

1. Reduce input length
2. Use model with larger context
3. Enable context truncation
4. Clear chat history

## Best Practices

### Model Selection

- **Simple queries**: Use fast, lightweight models
- **Complex tasks**: Use capable, larger models
- **Privacy-sensitive**: Use local models
- **Cost-sensitive**: Use free models
- **Quality-critical**: Use premium models

### Context Management

- Keep prompts concise
- Use relevant context only
- Summarize long conversations
- Use models with appropriate context windows

### Cost Management

- Monitor token usage
- Set max tokens limits
- Use cost-optimal routing
- Prefer local models when possible

## Next Steps

- [Read API Providers guide](API-Providers)
- [Read Configuration guide](Configuration)
- [Read Usage guide](Usage)
