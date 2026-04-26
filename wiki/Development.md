# Development

This guide covers development setup, coding standards, and contribution guidelines for Chat Linux Client.

## Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Adding Features](#adding-features)
- [Adding Providers](#adding-providers)
- [Building and Packaging](#building-and-packaging)
- [Debugging](#debugging)

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment (recommended)

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/chat-linux-client.git
cd chat-linux-client

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-qt black flake8 mypy
```

### Running the Application

```bash
# Run directly
python main.py

# Run with system checks
python main.py --check-system

# Run in debug mode
DEBUG=true python main.py
```

## Project Structure

```
chat-linux-client/
├── core/                   # Core AI provider logic
│   ├── api_client.py      # Base API client interface
│   ├── ollama_client.py   # Ollama local AI client
│   ├── groq_client.py     # Groq API client
│   ├── huggingface_client.py  # HuggingFace API client
│   ├── openrouter_client.py   # OpenRouter API client
│   ├── openai_client.py   # OpenAI API client
│   ├── provider_router.py # Intelligent routing engine
│   ├── settings.py        # Configuration management
│   └── model_manager.py   # Model information and selection
├── ui/                     # User interface
│   ├── main_window.py     # Main PyQt6 window
│   └── settings_dialog.py # Settings dialog
├── storage/                # Data persistence
│   ├── history_manager.py # Chat history storage
│   └── config_manager.py # Application configuration
├── utils/                  # Utility modules
│   ├── markdown_renderer.py  # Markdown to HTML rendering
│   ├── key_handler.py     # Secure API key storage
│   └── system_checks.py  # Environment validation
├── tests/                  # Test suite
│   ├── test_*.py          # Test files
│   └── conftest.py        # Pytest configuration
├── styles/                 # UI styling
│   └── dark.qss          # Dark theme stylesheet
├── assets/                 # Static assets
│   └── icon.png          # Application icon
├── scripts/                # Build and run scripts
│   ├── install.sh        # Installation script
│   ├── run.sh           # Application launcher
│   └── build_appimage.sh # AppImage build script
├── packaging/             # Distribution packaging
│   ├── chatgpt-client.desktop  # Desktop entry
│   └── AppImageBuilder.yml     # AppImage configuration
├── main.py               # Application entry point
├── requirements.txt      # Python dependencies
├── pytest.ini          # Test configuration
└── README.md           # Project documentation
```

## Coding Standards

### Code Style

We follow standard Python conventions:

```bash
# Format code with Black
black .

# Lint with Flake8
flake8 .

# Type check with MyPy
mypy .
```

### General Principles

- Write clear, readable code with descriptive names
- Add docstrings to all functions, classes, and modules
- Keep functions focused and small
- Follow existing code patterns
- Add error handling where appropriate
- Use logging, not print statements

### Type Hints

Include type hints for function signatures:

```python
async def chat_completion(
    self,
    messages: List[Dict[str, str]],
    model: str,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None
) -> Dict[str, Any]:
    """Generate a chat completion."""
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def generate_response(self, prompt: str) -> str:
    """Generate a response for the given prompt.
    
    Args:
        prompt: The input prompt to generate a response for.
        
    Returns:
        The generated response text.
        
    Raises:
        APIError: If the API request fails.
    """
    pass
```

### Error Handling

Use specific exception types:

```python
try:
    response = await self.api_call()
except aiohttp.ClientError as e:
    logger.error(f"API request failed: {e}")
    raise APIError(f"Failed to connect to API: {e}")
```

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_api_client.py

# Run with coverage
pytest --cov=.

# Run with verbose output
pytest -v tests/
```

### Test Structure

Tests are organized by module:

```
tests/
├── conftest.py              # Shared fixtures
├── test_api_client.py       # API client tests
├── test_provider_router.py  # Router tests
├── test_key_handler.py      # Key storage tests
└── ...
```

### Writing Tests

Use pytest fixtures and follow naming convention `test_*.py`:

```python
import pytest
from core.groq_client import GroqClient

@pytest.fixture
def groq_client():
    return GroqClient(api_key="test_key")

def test_client_initialization(groq_client):
    assert groq_client.api_key == "test_key"
    assert groq_client.base_url == "https://api.groq.com/openai/v1"
```

## Adding Features

### Adding a New Feature

1. Create a feature branch:
```bash
git checkout -b feature/your-feature-name
```

2. Implement the feature following coding standards

3. Add tests for the new feature

4. Update documentation if needed

5. Run tests to ensure nothing breaks:
```bash
pytest tests/
```

6. Commit changes:
```bash
git add .
git commit -m "Add feature: description"
```

7. Push and create pull request

### Adding UI Components

UI components are in the `ui/` directory using PyQt6:

```python
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton

class CustomWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        button = QPushButton("Click me")
        layout.addWidget(button)
        self.setLayout(layout)
```

## Adding Providers

### Steps to Add a New Provider

1. **Create the client file** in `core/`:
```python
# core/newprovider_client.py
from core.api_client import APIClient

class NewProviderClient(APIClient):
    def __init__(self, api_key: str, base_url: str = "https://api.newprovider.com/v1"):
        super().__init__(api_key=api_key, base_url=base_url)
        
    async def chat_completion(self, messages, model, temperature=0.7, max_tokens=None):
        # Implement non-streaming completion
        pass
        
    async def chat_completion_stream(self, messages, model, temperature=0.7, max_tokens=None):
        # Implement streaming completion
        pass
        
    async def test_connection(self):
        # Test API connectivity
        pass
```

2. **Add provider configuration** to `core/settings.py`:
```python
@dataclass
class NewProviderConfig:
    enabled: bool = False
    api_key: Optional[str] = None
    base_url: str = "https://api.newprovider.com/v1"
```

3. **Register provider** in `core/provider_router.py`:
```python
from core.newprovider_client import NewProviderClient

# In __init__ method
newprovider_config = config.get("newprovider", {})
if newprovider_config.get("api_key") and newprovider_config.get("enabled", True):
    newprovider_client = NewProviderClient(newprovider_config["api_key"])
    # Add to providers dict
```

4. **Add tests** in `tests/`:
```python
# tests/test_newprovider_client.py
import pytest
from core.newprovider_client import NewProviderClient

@pytest.fixture
def client():
    return NewProviderClient(api_key="test_key")

def test_client_initialization(client):
    assert client.api_key == "test_key"
```

5. **Update documentation**:
   - Add to README.md
   - Update API-Providers wiki page
   - Add model information to `core/model_manager.py`

## Building and Packaging

### Building AppImage

```bash
./scripts/build_appimage.sh
```

This creates an AppImage in the `build/` directory.

### Creating Desktop Entry

The desktop entry is in `packaging/chatgpt-client.desktop`:

```ini
[Desktop Entry]
Name=Chat Linux Client
Exec=/path/to/chat-linux-client
Icon=/path/to/assets/icon.png
Type=Application
Categories=Utility;
```

### Running Installation Script

```bash
./scripts/install.sh
```

## Debugging

### Enable Debug Logging

```bash
DEBUG=true python main.py
```

### View Logs

Logs are stored at:
```
~/.local/share/chat-linux-client/logs/
```

### Use Python Debugger

```bash
python -m pdb main.py
```

### Common Debugging Techniques

1. **Add logging statements**:
```python
import logging
logger = logging.getLogger(__name__)
logger.debug(f"Debug info: {variable}")
```

2. **Use print statements** (for quick debugging):
```python
print(f"Debug: {value}")
```

3. **Check configuration**:
```python
python main.py --check-system
```

4. **Test individual components**:
```python
python -c "from core.groq_client import GroqClient; print('Import successful')"
```

## Performance Profiling

### Profile with cProfile

```bash
python -m cProfile -o profile.stats main.py
python -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumulative').print_stats(20)"
```

### Memory Profiling

```bash
pip install memory_profiler
python -m memory_profiler main.py
```

## Contributing

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Ensure all tests pass
6. Update documentation
7. Submit a pull request

### Code Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No hardcoded secrets
- [ ] Error handling is appropriate
- [ ] Logging is added where needed

## Next Steps

- [Read Architecture guide](Architecture)
- [Read API Providers guide](API-Providers)
- [Review the codebase](https://github.com/yourusername/chat-linux-client)
