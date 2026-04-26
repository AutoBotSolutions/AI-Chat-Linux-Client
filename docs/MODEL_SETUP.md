# Model Setup Guide

## Current Available Models

### Local Models (Ollama) - Ready to Use
The following local models are installed and ready to use:

1. **llama3.2:1b** - 1.3GB - Lightweight, fast responses
2. **qwen2.5:3b** - 1.9GB - Good balance of speed and capability  
3. **phi3.5:3.8b** - 2.2GB - Microsoft's small language model
4. **mistral:7b** - 4.4GB - More capable for complex tasks

### Cloud Providers - Need API Keys
The following providers are configured but require valid API keys:

1. **Groq** - Ultra-fast inference (needs API key)
   - Models: llama-3.1-8b-instant, llama-3.1-70b-versatile, mixtral-8x7b-32768
   - Get API key: https://console.groq.com/

2. **OpenAI** - GPT models (needs API key)
   - Models: gpt-3.5-turbo, gpt-4, gpt-4-turbo, gpt-4o
   - Get API key: https://platform.openai.com/

3. **HuggingFace** - Open models (needs API key for some models)
   - Get API key: https://huggingface.co/settings/tokens

4. **OpenRouter** - Multiple model access (needs API key)
   - Get API key: https://openrouter.ai/keys

## How to Add More Models

### Adding Ollama Models
```bash
# List available models
ollama list

# Pull new models
ollama pull llama3.2:3b
ollama pull codellama:7b
ollama pull gemma2:9b

# Remove models
ollama remove model-name
```

### Configuring Cloud Providers
Edit the configuration file at `~/.config/chat-linux-client/config.json`:

```json
{
  "providers": {
    "groq": {
      "enabled": true,
      "api_key": "gsk_your_real_groq_api_key_here",
      "base_url": "https://api.groq.com/openai/v1"
    },
    "openai": {
      "enabled": true, 
      "api_key": "sk-your_real_openai_api_key_here",
      "base_url": "https://api.openai.com/v1"
    }
  }
}
```

Replace the placeholder API keys with your real keys.

## Model Selection in UI

The model dropdown in the main interface shows models in format:
`provider/model-name`

Examples:
- `ollama/llama3.2:1b`
- `ollama/mistral:7b`
- `groq/llama-3.1-8b-instant` (when API key configured)
- `openai/gpt-4o` (when API key configured)

## Routing Strategy

The system uses intelligent routing:
- **OFFLINE_FIRST**: Prefers local Ollama models
- **SPEED_OPTIMAL**: Prefers Groq for speed
- **COST_OPTIMAL**: Prefers free/local options
- **QUALITY_OPTIMAL**: Prefers larger models

## System Status

- **Local Provider**: Ollama running with 4 models
- **Cloud Providers**: Configured but need valid API keys
- **Total Models Available**: 4 local models
- **UI Integration**: All models appear in dropdown

## Troubleshooting

### Ollama Not Working
```bash
# Check if Ollama is running
ollama list

# Restart Ollama service
ollama serve
```

### Cloud Provider Not Showing Models
1. Verify API key is correct
2. Check network connection
3. Ensure provider is enabled in config
4. Check application logs for error messages
