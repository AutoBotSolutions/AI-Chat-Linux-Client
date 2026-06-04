[Configuration](Configuration)

This guide covers how to configure Chat Linux Client, including API keys, local models, and application settings.

Table of Contents
API Keys
Local Models (Ollama)
Application Settings
Privacy Settings
Configuration File Location
Environment Variables

API Keys

Chat Linux Client supports multiple AI providers. Configure API keys through the application settings or environment variables.

Supported Providers
Groq - Ultra-low latency inference
HuggingFace - Open-source models
OpenRouter - Multi-model routing
OpenAI - GPT models

Setting API Keys via Application UI
Open the application
Click on Settings in the menu bar
Navigate to the Providers tab
Select a provider from the dropdown
Enter your API key in the key field
Click Save

Setting API Keys via Environment Variables

Create a .env file in the project root (copy from .env.example):

Add your API keys:

Getting API Keys
Groq: https://console.groq.com/ (Free tier available)
HuggingFace: https://huggingface.co/settings/tokens (Free for many models)
OpenRouter: https://openrouter.ai/keys (Pay-per-use)
OpenAI: https://platform.openai.com/account/api-keys (Pay-per-use)

Local Models (Ollama)

Ollama provides local AI models that work offline without API keys.

Installing Ollama

Pulling Models

Configuring Ollama

Ollama is automatically detected by Chat Linux Client if:
Ollama is running (ollama serve)
Models are installed
Default URL is http://localhost:11434

To use a custom Ollama URL, set the environment variable:

Application Settings

Configure application behavior through the Settings dialog.

Chat Settings
Temperature: Controls response randomness (0.0 - 2.0)
Lower: More focused, deterministic responses
Higher: More creative, varied responses
Max Tokens: Maximum response length (0 = unlimited)

Model Selection

Choose your preferred model from the dropdown:
Models are listed as provider/model-name
Local models start with ollama/
Cloud models show their provider prefix

Routing Strategy

Select how models are chosen:
OFFLINEFIRST: Prefer local Ollama models
SPEEDOPTIMAL: Prefer Groq for speed
COSTOPTIMAL: Prefer free/local options
QUALITYOPTIMAL: Prefer larger models

Privacy Settings

Chat Encryption

Enable encryption for chat history:
Open Settings
Navigate to Privacy tab
Enable Encrypt Chats
Set a password when prompted
Click Save

Important: Remember your encryption password. Lost passwords cannot be recovered.

API Key Storage

API keys are encrypted and stored locally. To enhance security:
Set the CHATCLIENTPASSWORD environment variable
Or enable password-based encryption in Settings

Delete API Keys on Exit

Automatically delete API keys when the application closes:
Open Settings
Navigate to Privacy tab
Enable Delete API Keys on Exit
Click Save

Note: You'll need to re-enter keys on next launch.

Configuration File Location

Configuration is stored at:

Manual Configuration (Advanced)

You can edit the configuration file directly:

Warning: Manual editing may cause issues. Use the UI settings when possible.

Environment Variables

Override configuration with environment variables:

Troubleshooting Configuration

API Key Not Working
Verify the key is correct
Check the key has proper permissions
Ensure the provider account is active
Check network connectivity

Models Not Showing in Dropdown
Verify the provider is enabled in settings
Check API key is configured (for cloud providers)
Ensure Ollama is running (for local models)
Run system checks: python main.py --check-system

Configuration Not Saving
Check write permissions for ~/.config/chat-linux-client/
Ensure the directory exists
Check disk space

Next Steps
Learn how to use the application
Read about API Providers