# Chat Linux Client

A privacy-first, multi-provider AI desktop client for Linux systems that unifies multiple AI providers and local models into a single conversational interface.

## Features

- **Multi-Provider Support**: OpenAI, Ollama (local), Groq, HuggingFace, OpenRouter
- **Offline Capability**: Full functionality with local Ollama models
- **Streaming Responses**: Real-time token-by-token response rendering
- **Privacy-First**: No telemetry, local key storage, optional encryption
- **Intelligent Routing**: Automatic model selection based on requirements
- **Extensible Architecture**: Plugin system for custom providers and tools
- **Modern UI**: Dark theme with PyQt6 interface

## Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/chat-linux-client.git
cd chat-linux-client
```

2. Run the installation script:
```bash
./scripts/install.sh
```

3. Run the application:
```bash
./scripts/run.sh
```

### Manual Installation

1. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

## Configuration

### API Keys

Configure API keys through the application settings or by setting environment variables:

- `GROQ_API_KEY`: Groq API key
- `HUGGINGFACE_API_KEY`: HuggingFace API key
- `OPENROUTER_API_KEY`: OpenRouter API key

### Local Models

For offline AI support, install Ollama:

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

Then pull models:
```bash
ollama pull llama2
ollama pull mistral
```

## Usage

1. **Select Model**: Choose your preferred AI provider and model from the dropdown
2. **Configure Settings**: Set up API keys and preferences in the settings menu
3. **Start Chatting**: Type your message and press Enter or click Send
4. **View History**: Chat history is automatically saved and can be exported

## Project Structure

```
chat-linux-client/
|
|--- main.py                 # Application entry point
|--- requirements.txt        # Python dependencies
|--- README.md              # This file
|
|--- core/                  # Core AI provider logic
|    |--- api_client.py     # Base API client interface
|    |--- ollama_client.py  # Ollama local AI client
|    |--- groq_client.py    # Groq API client
|    |--- huggingface_client.py # HuggingFace API client
|    |--- openrouter_client.py  # OpenRouter API client
|    |--- provider_router.py    # Intelligent routing engine
|    |--- settings.py       # Configuration management
|    |--- model_manager.py  # Model information and selection
|
|--- ui/                    # User interface
|    |--- main_window.py    # Main PyQt6 window
|
|--- storage/               # Data persistence
|    |--- history_manager.py # Chat history storage
|    |--- config_manager.py # Application configuration
|
|--- utils/                 # Utility modules
|    |--- markdown_renderer.py # Markdown to HTML rendering
|    |--- key_handler.py    # Secure API key storage
|    |--- system_checks.py  # Environment validation
|
|--- styles/                # UI styling
|    |--- dark.qss         # Dark theme stylesheet
|
|--- assets/                # Static assets
|    |--- icon.png         # Application icon
|
|--- scripts/               # Build and run scripts
|    |--- install.sh       # Installation script
|    |--- run.sh          # Application launcher
|    |--- build_appimage.sh # AppImage build script
|
|--- packaging/             # Distribution packaging
|    |--- chatgpt-client.desktop # Desktop entry
|    |--- AppImageBuilder.yml   # AppImage configuration
```

## Architecture

The system follows a modular architecture with clear separation of concerns:

1. **UI Layer**: PyQt6 desktop interface with dark theme
2. **Routing Engine**: Intelligent model selection and request routing
3. **Provider Layer**: Multiple AI provider implementations
4. **Storage Layer**: Persistent chat history and configuration
5. **Utility Layer**: Helper functions and system integration

## Development

### Running Tests

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/
```

### Building AppImage

```bash
./scripts/build_appimage.sh
```

### Code Style

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

## System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Linux (Ubuntu 20.04+, Fedora 35+, Arch Linux)
- **Memory**: 4GB RAM minimum (8GB recommended)
- **Storage**: 500MB free space
- **Optional**: Ollama for local AI models

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure virtual environment is activated
2. **API Connection**: Check internet connectivity and API keys
3. **Ollama Not Found**: Install Ollama for local model support
4. **Permission Errors**: Check file permissions for config/data directories

### System Checks

Run comprehensive system checks:

```bash
python main.py --check-system
```

### Logging

Application logs are stored in:
- Linux: `~/.local/share/chat-linux-client/logs/`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Check the troubleshooting section
- Run system checks for diagnostics
- Create an issue on the project repository

## Roadmap

Future features planned:
- [ ] Voice interface (speech-to-text + TTS)
- [ ] Local RAG knowledge system
- [ ] Multi-window chat sessions
- [ ] Agent-based task automation
- [ ] System tray background assistant mode
- [ ] Plugin marketplace
- [ ] Custom theme support
