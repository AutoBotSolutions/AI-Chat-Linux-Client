# Chat Linux Client Wiki

Welcome to the Chat Linux Client documentation wiki. This is a privacy-first, multi-provider AI desktop client for Linux systems that unifies multiple AI providers and local models into a single conversational interface.

## Quick Links

- [Installation](Installation) - How to install and set up the application
- [Configuration](Configuration) - Configure API keys and settings
- [Usage](Usage) - How to use the application
- [API Providers](API-Providers) - Supported AI providers and how to use them
- [Troubleshooting](Troubleshooting) - Common issues and solutions
- [Development](Development) - Development setup and contribution guide
- [Architecture](Architecture) - System architecture and design
- [FAQ](FAQ) - Frequently asked questions

## Features

- **Multi-Provider Support**: OpenAI, Ollama (local), Groq, HuggingFace, OpenRouter
- **Offline Capability**: Full functionality with local Ollama models
- **Streaming Responses**: Real-time token-by-token response rendering
- **Privacy-First**: No telemetry, local key storage, optional encryption
- **Intelligent Routing**: Automatic model selection based on requirements
- **Extensible Architecture**: Plugin system for custom providers and tools
- **Modern UI**: Dark theme with PyQt6 interface

## System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Linux (Ubuntu 20.04+, Fedora 35+, Arch Linux)
- **Memory**: 4GB RAM minimum (8GB recommended)
- **Storage**: 500MB free space
- **Optional**: Ollama for local AI models

## Getting Started

1. [Install the application](Installation)
2. [Configure your API keys](Configuration)
3. [Start chatting](Usage)

## Support

For issues and questions:
- Check the [Troubleshooting](Troubleshooting) section
- Run system checks for diagnostics: `python main.py --check-system`
- Create an issue on the project repository

## License

This project is licensed under the MIT License - see the LICENSE file for details.
