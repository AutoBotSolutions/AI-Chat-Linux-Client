# API Providers

This guide covers all supported AI providers, their features, and how to configure them.

## Table of Contents

- [Overview](#overview)
- [Ollama (Local)](#ollama-local)
- [Groq](#groq)
- [HuggingFace](#huggingface)
- [OpenRouter](#openrouter)
- [OpenAI](#openai)
- [Provider Comparison](#provider-comparison)
- [Adding Custom Providers](#adding-custom-providers)

## Overview

Chat Linux Client supports multiple AI providers, giving you flexibility in choosing the best model for your needs:

| Provider | Type | Cost | Speed | Quality | Offline |
|----------|------|------|-------|---------|---------|
| Ollama | Local | Free | Variable | Good | Yes |
| Groq | Cloud | Free tier | Very Fast | Good | No |
| HuggingFace | Cloud | Free tier | Medium | Variable | No |
| OpenRouter | Cloud | Pay-per-use | Fast | Excellent | No |
| OpenAI | Cloud | Pay-per-use | Fast | Excellent | No |

## Ollama (Local)

Ollama provides local AI models that run entirely on your machine.

### Advantages

- **Free**: No API costs
- **Privacy**: Data never leaves your machine
- **Offline**: Works without internet
- **No Rate Limits**: Use as much as you want

### Disadvantages

- **Hardware**: Requires capable CPU/GPU
- **Model Size**: Models take disk space (1-5GB each)
- **Speed**: Slower than cloud for large models
- **Model Selection**: Limited to available models

### Installation

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Available Models

```bash
# Lightweight (1.3GB)
ollama pull llama3.2:1b

# Balanced (1.9GB)
ollama pull qwen2.5:3b

# Capable (2.2GB)
ollama pull phi3.5:3.8b

# Large (4.4GB)
ollama pull mistral:7b
```

### Configuration

Ollama is automatically detected. Ensure it's running:

```bash
ollama serve
```

### Best For

- Privacy-sensitive conversations
- Offline work
- Cost-sensitive users
- Development and testing

## Groq

Groq provides ultra-low latency inference using their LPU (Language Processing Unit).

### Advantages

- **Speed**: Fastest inference available
- **Free Tier**: Generous free usage
- **Quality**: Good model selection
- **Latency**: Sub-100ms response times

### Disadvantages

- **Rate Limits**: Free tier has limits
- **Internet Required**: Cloud-based
- **Privacy**: Data sent to Groq servers

### Getting an API Key

1. Visit https://console.groq.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key

### Configuration

Add to `.env` file or settings:

```bash
GROQ_API_KEY=gsk_your_actual_api_key_here
```

### Available Models

- `llama-3.1-8b-instant` - Fast, balanced
- `llama-3.1-70b-versatile` - Capable
- `mixtral-8x7b-32768` - Large context

### Best For

- Real-time applications
- Speed-critical tasks
- Free tier usage
- Interactive conversations

## HuggingFace

HuggingFace provides access to thousands of open-source models.

### Advantages

- **Variety**: Thousands of models available
- **Free Tier**: Many models are free
- **Open Source**: Community-driven models
- **Customization**: Can use custom models

### Disadvantages

- **Variable Quality**: Quality varies by model
- **Speed**: Slower than dedicated providers
- **Complexity**: More configuration options
- **Rate Limits**: Free tier has limits

### Getting an API Key

1. Visit https://huggingface.co/settings/tokens
2. Sign up or log in
3. Create a new token
4. Copy the token

### Configuration

Add to `.env` file or settings:

```bash
HUGGINGFACE_API_KEY=hf_your_actual_api_key_here
```

### Popular Models

- `meta-llama/Llama-2-7b-chat-hf`
- `mistralai/Mistral-7B-Instruct-v0.2`
- `google/gemma-7b`

### Best For

- Experimenting with different models
- Using specialized models
- Open-source preference
- Custom model deployment

## OpenRouter

OpenRouter provides access to multiple models from various providers through a single API.

### Advantages

- **Variety**: Access to many models
- **Unified API**: Single key for multiple models
- **Comparison**: Easy to compare models
- **Flexible**: Pay-per-use pricing

### Disadvantages

- **Cost**: Pay-per-use (no free tier)
- **Complexity**: Many options to choose from
- **Internet Required**: Cloud-based
- **Privacy**: Data sent to OpenRouter

### Getting an API Key

1. Visit https://openrouter.ai/keys
2. Sign up or log in
3. Add credits to your account
4. Create an API key

### Configuration

Add to `.env` file or settings:

```bash
OPENROUTER_API_KEY=sk-or-your_actual_api_key_here
```

### Available Models

- `anthropic/claude-3-opus`
- `openai/gpt-4-turbo`
- `google/gemini-pro`
- And many more

### Best For

- Accessing premium models
- Comparing different models
- Production use
- Flexible model selection

## OpenAI

OpenAI provides state-of-the-art GPT models.

### Advantages

- **Quality**: Best-in-class models
- **Reliability**: Highly reliable service
- **Documentation**: Excellent documentation
- **Ecosystem**: Large ecosystem of tools

### Disadvantages

- **Cost**: Most expensive option
- **Rate Limits**: Strict rate limits
- **Internet Required**: Cloud-based
- **Privacy**: Data sent to OpenAI

### Getting an API Key

1. Visit https://platform.openai.com/account/api-keys
2. Sign up or log in
3. Create a new API key
4. Add credits to your account

### Configuration

Add to `.env` file or settings:

```bash
OPENAI_API_KEY=sk-your_actual_api_key_here
```

### Available Models

- `gpt-4o` - Latest, most capable
- `gpt-4-turbo` - High quality
- `gpt-3.5-turbo` - Cost-effective

### Best For

- Highest quality requirements
- Professional use
- Complex tasks
- Production applications

## Provider Comparison

### Speed Comparison

1. **Groq** - Fastest (sub-100ms)
2. **OpenAI** - Fast (200-500ms)
3. **OpenRouter** - Fast (200-500ms)
4. **HuggingFace** - Medium (500-1000ms)
5. **Ollama** - Variable (depends on hardware)

### Cost Comparison

1. **Ollama** - Free (hardware cost only)
2. **Groq** - Free tier available
3. **HuggingFace** - Free tier available
4. **OpenRouter** - Pay-per-use (moderate)
5. **OpenAI** - Pay-per-use (expensive)

### Quality Comparison

1. **OpenAI** - Best overall
2. **OpenRouter** - Excellent (depends on model)
3. **Groq** - Good
4. **HuggingFace** - Variable
5. **Ollama** - Good (depends on model)

## Adding Custom Providers

Chat Linux Client has an extensible architecture for adding custom providers.

### Steps to Add a Provider

1. Create a new client file in `core/` (e.g., `custom_provider.py`)
2. Inherit from `APIClient` base class
3. Implement required methods:
   - `chat_completion()`
   - `chat_completion_stream()`
   - `test_connection()`
4. Add provider configuration to `core/settings.py`
5. Register in `core/provider_router.py`
6. Add tests in `tests/`

### Example

See existing providers in `core/` for reference:
- `core/groq_client.py`
- `core/huggingface_client.py`
- `core/openrouter_client.py`
- `core/openai_client.py`

## Next Steps

- [Configure your API keys](Configuration)
- [Learn how to use the application](Usage)
- [Read troubleshooting guide](Troubleshooting)
