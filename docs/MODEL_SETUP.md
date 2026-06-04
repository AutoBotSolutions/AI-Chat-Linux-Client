Model Setup Guide

Current Available Models

Local Models (Ollama) - Ready to Use
The following local models are installed and ready to use:
llama3.2:1b - 1.3GB - Lightweight, fast responses
qwen2.5:3b - 1.9GB - Good balance of speed and capability  
phi3.5:3.8b - 2.2GB - Microsoft's small language model
mistral:7b - 4.4GB - More capable for complex tasks

Cloud Providers - Need API Keys
The following providers are configured but require valid API keys:
Groq - Ultra-fast inference (needs API key)
Models: llama-3.1-8b-instant, llama-3.1-70b-versatile, mixtral-8x7b-32768
Get API key: https://console.groq.com/
OpenAI - GPT models (needs API key)
Models: gpt-3.5-turbo, gpt-4, gpt-4-turbo, gpt-4o
Get API key: https://platform.openai.com/
HuggingFace - Open models (needs API key for some models)
Get API key: https://huggingface.co/settings/tokens
OpenRouter - Multiple model access (needs API key)
Get API key: https://openrouter.ai/keys

How to Add More Models

Adding Ollama Models

Configuring Cloud Providers
Edit the configuration file at ~/.config/chat-linux-client/config.json:

Replace the placeholder API keys with your real keys.

Model Selection in UI

The model dropdown in the main interface shows models in format:
provider/model-name

Examples:
ollama/llama3.2:1b
ollama/mistral:7b
groq/llama-3.1-8b-instant (when API key configured)
openai/gpt-4o (when API key configured)

Routing Strategy

The system uses intelligent routing:
OFFLINEFIRST: Prefers local Ollama models
SPEEDOPTIMAL: Prefers Groq for speed
COSTOPTIMAL: Prefers free/local options
QUALITY_OPTIMAL: Prefers larger models

System Status
Local Provider: Ollama running with 4 models
Cloud Providers: Configured but need valid API keys
Total Models Available: 4 local models
UI Integration: All models appear in dropdown

Troubleshooting

Ollama Not Working

Cloud Provider Not Showing Models
Verify API key is correct
Check network connection
Ensure provider is enabled in config
Check application logs for error messages