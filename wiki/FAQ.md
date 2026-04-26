# FAQ

Frequently asked questions about Chat Linux Client.

## Table of Contents

- [General](#general)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Providers](#api-providers)
- [Privacy and Security](#privacy-and-security)
- [Troubleshooting](#troubleshooting)

## General

### What is Chat Linux Client?

Chat Linux Client is a privacy-first, multi-provider AI desktop client for Linux that unifies multiple AI providers and local models into a single conversational interface.

### Is Chat Linux Client free?

Yes! Chat Linux Client is open source and free to use. Local models (via Ollama) are completely free. Some cloud providers have free tiers, while others require payment.

### What operating systems are supported?

Currently, Chat Linux Client supports Linux distributions including Ubuntu 20.04+, Fedora 35+, and Arch Linux. Windows and macOS support may be added in the future.

### Can I use Chat Linux Client offline?

Yes! With Ollama installed, you can use local models entirely offline without any internet connection.

### How does Chat Linux Client differ from other AI clients?

- **Multi-provider**: Supports multiple AI providers in one interface
- **Privacy-first**: No telemetry, local storage, optional encryption
- **Local models**: Full offline capability with Ollama
- **Intelligent routing**: Automatic model selection based on needs
- **Open source**: Fully transparent and customizable

## Installation

### How do I install Chat Linux Client?

The easiest way is using the installation script:

```bash
git clone https://github.com/yourusername/chat-linux-client.git
cd chat-linux-client
./scripts/install.sh
./scripts/run.sh
```

See the [Installation](Installation) guide for detailed instructions.

### Can I install Chat Linux Client without sudo?

Yes! The application can be installed in your home directory without sudo privileges.

### Do I need to install Ollama?

Ollama is optional but recommended for offline capability. Without Ollama, you'll need to use cloud providers with API keys.

### What are the system requirements?

- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended)
- 500MB free storage
- Linux (Ubuntu 20.04+, Fedora 35+, Arch Linux)

## Configuration

### How do I add API keys?

You can add API keys through:
1. **Settings dialog**: Open Settings → Providers tab
2. **Environment variables**: Add to `.env` file
3. **Configuration file**: Edit `~/.config/chat-linux-client/config.json`

See the [Configuration](Configuration) guide for details.

### Where are API keys stored?

API keys are encrypted and stored locally at `~/.config/chat-linux-client/api_keys.enc`. They are never sent anywhere except to the AI provider APIs.

### Can I use multiple API keys for the same provider?

Currently, only one API key per provider is supported. You can switch between providers in the settings.

### How do I change the routing strategy?

Open Settings → Chat tab → Select your preferred routing strategy:
- **OFFLINE_FIRST**: Prefer local models
- **SPEED_OPTIMAL**: Prefer fast models
- **COST_OPTIMAL**: Prefer free options
- **QUALITY_OPTIMAL**: Prefer capable models

## Usage

### How do I start a new chat?

Click the **New Chat** button in the toolbar or press `Ctrl+N`.

### Can I have multiple chat sessions?

Currently, Chat Linux Client supports one active chat session at a time. You can switch between past chats using the History panel.

### How do I export my chat history?

Open the chat you want to export → Select **File > Export Chat** → Choose format and location.

### Can I search my chat history?

Yes! Open the History panel and use the search box to find specific conversations.

### What do the different temperature settings do?

- **0.0-0.3**: Focused, deterministic responses
- **0.4-0.7**: Balanced responses (default)
- **0.8-1.0**: Creative, varied responses
- **1.0+**: Very creative, less predictable

### What does max tokens mean?

Max tokens limits the length of AI responses. Set to 0 for unlimited, or specify a number (e.g., 500 for short responses, 2000 for longer ones).

## API Providers

### Which providers are supported?

- **Ollama**: Local models (free, offline)
- **Groq**: Ultra-fast cloud AI (free tier)
- **HuggingFace**: Open-source models (free tier)
- **OpenRouter**: Multi-model access (pay-per-use)
- **OpenAI**: GPT models (pay-per-use)

### Which provider should I use?

- **For privacy**: Use Ollama (local models)
- **For speed**: Use Groq
- **For cost**: Use Ollama or free tiers
- **For quality**: Use OpenAI or OpenRouter

### Do I need API keys for all providers?

No! Ollama works without API keys. Cloud providers require API keys, but many have free tiers.

### Can I use multiple providers at once?

The intelligent routing can automatically select providers based on your strategy. You can also manually select specific models from different providers.

### How do I get a Groq API key?

Visit https://console.groq.com/, sign up, and create an API key. Groq offers a generous free tier.

### How do I get an OpenAI API key?

Visit https://platform.openai.com/account/api-keys, sign up, and create an API key. OpenAI requires payment.

## Privacy and Security

### Is my data private?

Yes! Chat Linux Client is privacy-first:
- No telemetry or analytics
- Local data storage
- Optional encryption for chats and keys
- Direct connection to providers (no intermediaries)

### Does Chat Linux Client collect telemetry?

No! Chat Linux Client collects no telemetry, analytics, or usage data.

### Where is my chat history stored?

Chat history is stored locally at `~/.local/share/chat-linux-client/chat_history.db` (SQLite database).

### Can I encrypt my chat history?

Yes! Enable chat encryption in Settings → Privacy tab. You'll need to set a password.

### What happens if I forget my encryption password?

Encrypted data cannot be recovered without the password. You'll need to delete the encrypted files and start fresh.

### Are API keys secure?

API keys are encrypted using Fernet symmetric encryption and stored locally. They are only sent to provider APIs over HTTPS.

### Does Chat Linux Client work with corporate firewalls?

Yes, but you may need to configure proxy settings if your network requires them.

## Troubleshooting

### The application won't start

Run system checks:
```bash
python main.py --check-system
```

Check logs at `~/.local/share/chat-linux-client/logs/`

### Models aren't showing in the dropdown

- Verify provider is enabled in settings
- Check API key is configured (for cloud providers)
- Ensure Ollama is running (for local models)
- Run system checks

### API key isn't working

- Verify the key is correct (no extra spaces)
- Check provider account is active
- Ensure key has proper permissions
- Try regenerating the key

### Responses are slow

- Use a faster model (lighter local model or Groq)
- Reduce max tokens in settings
- Check network connection
- Close other applications

### Application uses too much memory

- Use lighter models (e.g., llama3.2:1b)
- Clear chat history regularly
- Reduce max tokens setting
- Restart application periodically

### How do I reset the application?

Delete configuration and data:
```bash
rm -rf ~/.config/chat-linux-client
rm -rf ~/.local/share/chat-linux-client
```

Then reconfigure the application.

### Where can I get help?

- Check the [Troubleshooting](Troubleshooting) guide
- Run system checks: `python main.py --check-system`
- Create an issue on GitHub
- Check existing issues and discussions

## Additional Questions

### Can I contribute to Chat Linux Client?

Yes! Contributions are welcome. See the [Development](Development) guide for details.

### Is there a mobile version?

Not yet, but it's on the roadmap. The current focus is on Linux desktop.

### Can I use custom models?

Yes! With Ollama, you can use any model available in the Ollama library. For cloud providers, you can add custom providers by extending the codebase.

### Does Chat Linux Client support voice input/output?

Not yet, but voice interface is planned for a future release.

### Can I run Chat Linux Client on a server?

Currently, Chat Linux Client is designed for desktop use with a GUI. A headless/server version may be developed in the future.

### How often is Chat Linux Client updated?

Updates are released as needed for bug fixes, new features, and provider updates. Watch the repository for releases.

### Can I donate to support development?

Chat Linux Client is open source and free. If you'd like to support development, consider contributing code, reporting issues, or spreading the word.

## Next Steps

- [Read Installation guide](Installation)
- [Read Configuration guide](Configuration)
- [Read Usage guide](Usage)
- [Read API Providers guide](API-Providers)
