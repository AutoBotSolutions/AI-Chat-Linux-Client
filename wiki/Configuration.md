# Configuration

This guide covers how to configure Chat Linux Client, including API keys, local models, and application settings.

## Table of Contents

- [API Keys](#api-keys)
- [Local Models (Ollama)](#local-models-ollama)
- [Application Settings](#application-settings)
- [Privacy Settings](#privacy-settings)
- [Configuration File Location](#configuration-file-location)
- [Environment Variables](#environment-variables)

## API Keys

Chat Linux Client supports multiple AI providers. Configure API keys through the application settings or environment variables.

### Supported Providers

- **Groq** - Ultra-low latency inference
- **HuggingFace** - Open-source models
- **OpenRouter** - Multi-model routing
- **OpenAI** - GPT models

### Setting API Keys via Application UI

1. Open the application
2. Click on **Settings** in the menu bar
3. Navigate to the **Providers** tab
4. Select a provider from the dropdown
5. Enter your API key in the key field
6. Click **Save**

### Setting API Keys via Environment Variables

Create a `.env` file in the project root (copy from `.env.example`):

```bash
cp .env.example .env
nano .env
```

Add your API keys:

```bash
# Groq API Key
GROQ_API_KEY=gsk_your_actual_api_key_here

# HuggingFace API Key
HUGGINGFACE_API_KEY=hf_your_actual_api_key_here

# OpenRouter API Key
OPENROUTER_API_KEY=sk-or-your_actual_api_key_here

# OpenAI API Key
OPENAI_API_KEY=sk-your_actual_api_key_here
```

### Getting API Keys

- **Groq**: https://console.groq.com/ (Free tier available)
- **HuggingFace**: https://huggingface.co/settings/tokens (Free for many models)
- **OpenRouter**: https://openrouter.ai/keys (Pay-per-use)
- **OpenAI**: https://platform.openai.com/account/api-keys (Pay-per-use)

## Local Models (Ollama)

Ollama provides local AI models that work offline without API keys.

### Installing Ollama

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Pulling Models

```bash
# Lightweight model (1.3GB)
ollama pull llama3.2:1b

# Balanced model (1.9GB)
ollama pull qwen2.5:3b

# Capable model (2.2GB)
ollama pull phi3.5:3.8b

# Large model (4.4GB)
ollama pull mistral:7b
```

### Configuring Ollama

Ollama is automatically detected by Chat Linux Client if:
- Ollama is running (`ollama serve`)
- Models are installed
- Default URL is `http://localhost:11434`

To use a custom Ollama URL, set the environment variable:

```bash
OLLAMA_BASE_URL=http://your-custom-url:11434
```

## Application Settings

Configure application behavior through the Settings dialog.

### Chat Settings

- **Temperature**: Controls response randomness (0.0 - 2.0)
  - Lower: More focused, deterministic responses
  - Higher: More creative, varied responses
- **Max Tokens**: Maximum response length (0 = unlimited)

### Model Selection

Choose your preferred model from the dropdown:
- Models are listed as `provider/model-name`
- Local models start with `ollama/`
- Cloud models show their provider prefix

### Routing Strategy

Select how models are chosen:
- **OFFLINE_FIRST**: Prefer local Ollama models
- **SPEED_OPTIMAL**: Prefer Groq for speed
- **COST_OPTIMAL**: Prefer free/local options
- **QUALITY_OPTIMAL**: Prefer larger models

## Privacy Settings

### Chat Encryption

Enable encryption for chat history:

1. Open Settings
2. Navigate to **Privacy** tab
3. Enable **Encrypt Chats**
4. Set a password when prompted
5. Click **Save**

**Important**: Remember your encryption password. Lost passwords cannot be recovered.

### API Key Storage

API keys are encrypted and stored locally. To enhance security:

1. Set the `CHAT_CLIENT_PASSWORD` environment variable
2. Or enable password-based encryption in Settings

### Delete API Keys on Exit

Automatically delete API keys when the application closes:

1. Open Settings
2. Navigate to **Privacy** tab
3. Enable **Delete API Keys on Exit**
4. Click **Save**

**Note**: You'll need to re-enter keys on next launch.

## Configuration File Location

Configuration is stored at:

```
~/.config/chat-linux-client/config.json
```

### Manual Configuration (Advanced)

You can edit the configuration file directly:

```json
{
  "providers": {
    "groq": {
      "enabled": true,
      "api_key": "your_api_key_here",
      "base_url": "https://api.groq.com/openai/v1"
    },
    "ollama": {
      "enabled": true,
      "base_url": "http://localhost:11434"
    }
  },
  "chat": {
    "temperature": 0.7,
    "max_tokens": null,
    "routing_strategy": "offline_first"
  },
  "privacy": {
    "encrypt_chats": false,
    "delete_api_keys_on_exit": false
  }
}
```

**Warning**: Manual editing may cause issues. Use the UI settings when possible.

## Environment Variables

Override configuration with environment variables:

```bash
# API Keys
GROQ_API_KEY=your_key
HUGGINGFACE_API_KEY=your_key
OPENROUTER_API_KEY=your_key
OPENAI_API_KEY=your_key

# Ollama
OLLAMA_BASE_URL=http://localhost:11434

# Application
LOG_LEVEL=INFO
THEME=dark
FONT_SIZE=12

# Privacy
ENCRYPT_CHATS=false
DISABLE_TELEMETRY=true

# Development
DEBUG=false
LOG_TO_FILE=true
```

## Troubleshooting Configuration

### API Key Not Working

1. Verify the key is correct
2. Check the key has proper permissions
3. Ensure the provider account is active
4. Check network connectivity

### Models Not Showing in Dropdown

1. Verify the provider is enabled in settings
2. Check API key is configured (for cloud providers)
3. Ensure Ollama is running (for local models)
4. Run system checks: `python main.py --check-system`

### Configuration Not Saving

1. Check write permissions for `~/.config/chat-linux-client/`
2. Ensure the directory exists
3. Check disk space

## Next Steps

- [Learn how to use the application](Usage)
- [Read about API Providers](API-Providers)
