# Architecture

This document describes the system architecture and design of Chat Linux Client.

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Component Architecture](#component-architecture)
- [Data Flow](#data-flow)
- [Provider Architecture](#provider-architecture)
- [Storage Architecture](#storage-architecture)
- [Security Architecture](#security-architecture)
- [Extension Points](#extension-points)

## Overview

Chat Linux Client follows a modular, layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────────┐
│           UI Layer (PyQt6)              │
│  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │ Main     │  │ Settings │  │ Other  │ │
│  │ Window   │  │ Dialog   │  │ UI     │ │
│  └──────────┘  └──────────┘  └────────┘ │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Routing Layer                   │
│  ┌──────────────────────────────────┐  │
│  │     Provider Router              │  │
│  │  - Model Selection               │  │
│  │  - Request Routing               │  │
│  │  - Fallback Logic                │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│        Provider Layer                   │
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐  │
│  │API │ │Oll│ │Groq│ │HF  │ │OR  │  │
│  │    │ │ama │ │    │ │    │ │    │  │
│  └────┘ └────┘ └────┘ └────┘ └────┘  │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Storage Layer                   │
│  ┌──────────┐  ┌──────────┐           │
│  │ Config   │  │ History  │           │
│  │ Manager  │  │ Manager  │           │
│  └──────────┘  └──────────┘           │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Utility Layer                   │
│  ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │Markdown  │ │Key       │ │System  │ │
│  │Renderer  │ │Handler   │ │Checks  │ │
│  └──────────┘ └──────────┘ └────────┘ │
└─────────────────────────────────────────┘
```

## System Architecture

### Layered Design

The system is organized into five distinct layers:

1. **UI Layer**: PyQt6-based desktop interface
2. **Routing Layer**: Intelligent model selection and request routing
3. **Provider Layer**: Multiple AI provider implementations
4. **Storage Layer**: Persistent configuration and chat history
5. **Utility Layer**: Helper functions and system integration

### Design Principles

- **Separation of Concerns**: Each layer has a distinct responsibility
- **Dependency Injection**: Components receive dependencies through constructors
- **Interface-Based Design**: Providers implement common interfaces
- **Async/Await**: I/O operations use async for performance
- **Error-First**: Errors are handled gracefully with fallbacks

## Component Architecture

### UI Layer (`ui/`)

**Main Window** (`main_window.py`)
- Manages the primary application window
- Handles user interactions
- Coordinates between UI and backend
- Manages chat sessions

**Settings Dialog** (`settings_dialog.py`)
- Configuration interface
- API key management
- Provider settings
- Privacy settings

### Routing Layer (`core/provider_router.py`)

**Provider Router**
- Selects appropriate provider based on strategy
- Manages provider availability
- Implements fallback logic
- Handles request routing

**Routing Strategies**
- `OFFLINE_FIRST`: Prefer local models
- `SPEED_OPTIMAL`: Prefer fast models
- `COST_OPTIMAL`: Prefer free options
- `QUALITY_OPTIMAL`: Prefer capable models

### Provider Layer (`core/`)

**Base API Client** (`api_client.py`)
- Abstract base class for all providers
- Defines common interface
- Implements shared functionality

**Provider Implementations**
- `ollama_client.py`: Local Ollama models
- `groq_client.py`: Groq API
- `huggingface_client.py`: HuggingFace API
- `openrouter_client.py`: OpenRouter API
- `openai_client.py`: OpenAI API

**Model Manager** (`model_manager.py`)
- Manages model information
- Provides model selection logic
- Handles model metadata

### Storage Layer (`storage/`)

**Config Manager** (`config_manager.py`)
- Manages application configuration
- Handles provider settings
- Supports encryption
- Persists to JSON

**History Manager** (`history_manager.py`)
- Manages chat history
- SQLite database storage
- Export functionality
- Search capabilities

### Utility Layer (`utils/`)

**Markdown Renderer** (`markdown_renderer.py`)
- Converts Markdown to HTML
- Syntax highlighting for code
- Sanitizes output

**Key Handler** (`key_handler.py`)
- Secure API key storage
- Encryption/decryption
- Key validation
- Password management

**System Checks** (`system_checks.py`)
- Validates system requirements
- Checks dependencies
- Verifies resources

## Data Flow

### Chat Request Flow

```
User Input
    ↓
UI Layer (main_window.py)
    ↓
Chat Worker (async task)
    ↓
Provider Router (selects provider)
    ↓
Provider Client (API call)
    ↓
API Response
    ↓
Markdown Renderer (formatting)
    ↓
UI Layer (display)
```

### Configuration Flow

```
Settings Dialog
    ↓
Config Manager
    ↓
Encryption (if enabled)
    ↓
File System (config.json)
```

### History Flow

```
Chat Message
    ↓
History Manager
    ↓
SQLite Database
    ↓
Query/Search
    ↓
Display/Export
```

## Provider Architecture

### Provider Interface

All providers implement the `APIClient` interface:

```python
class APIClient(ABC):
    @abstractmethod
    async def chat_completion(self, messages, model, temperature, max_tokens):
        """Generate a chat completion."""
        pass
        
    @abstractmethod
    async def chat_completion_stream(self, messages, model, temperature, max_tokens):
        """Generate a streaming chat completion."""
        pass
        
    @abstractmethod
    async def test_connection(self):
        """Test API connectivity."""
        pass
```

### Provider Lifecycle

1. **Initialization**: Provider created with API key and base URL
2. **Availability Check**: Router tests provider connection
3. **Model Registration**: Provider registers available models
4. **Request Handling**: Provider handles chat requests
5. **Streaming**: Provider streams responses if supported
6. **Error Handling**: Provider handles errors gracefully

### Streaming Implementation

Providers use Server-Sent Events (SSE) for streaming:

```python
async def chat_completion_stream(self, messages, model, temperature, max_tokens):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            async for line in response.content:
                if line.startswith(b"data: "):
                    data = json.loads(line[6:])
                    if data.get("choices"):
                        yield data["choices"][0]["delta"].get("content", "")
```

## Storage Architecture

### Configuration Storage

**Location**: `~/.config/chat-linux-client/config.json`

**Structure**:
```json
{
  "providers": {
    "provider_name": {
      "enabled": true,
      "api_key": "encrypted_key",
      "base_url": "https://api.example.com"
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

### History Storage

**Location**: `~/.local/share/chat-linux-client/chat_history.db`

**Schema**:
```sql
CREATE TABLE chats (
    id INTEGER PRIMARY KEY,
    title TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    chat_id INTEGER,
    role TEXT,
    content TEXT,
    timestamp TIMESTAMP,
    FOREIGN KEY (chat_id) REFERENCES chats(id)
);
```

### Key Storage

**Location**: `~/.config/chat-linux-client/api_keys.enc`

**Encryption**: Fernet symmetric encryption

**Key Derivation**: PBKDF2 with SHA-256

## Security Architecture

### API Key Security

- **Encryption**: Keys encrypted at rest using Fernet
- **Memory**: Keys kept in memory only when needed
- **Transmission**: HTTPS for all API calls
- **Validation**: Key format validation before use

### Chat History Security

- **Optional Encryption**: Chat history can be encrypted
- **Local Storage**: Data stored locally, not in cloud
- **Access Control**: File system permissions protect data
- **No Telemetry**: No data collection or analytics

### Network Security

- **HTTPS Only**: All API communications use HTTPS
- **Certificate Validation**: SSL certificate validation enabled
- **No Proxy**: No intermediate proxy servers
- **Direct Connection**: Direct connection to provider APIs

## Extension Points

### Adding New Providers

1. Implement `APIClient` interface
2. Add provider configuration to `settings.py`
3. Register in `provider_router.py`
4. Add model information to `model_manager.py`
5. Add tests and documentation

### Adding New Routing Strategies

1. Define strategy in `provider_router.py`
2. Implement selection logic
3. Add to strategy enum
4. Update UI to include option
5. Add tests

### Adding New Storage Backends

1. Implement storage interface
2. Add configuration option
3. Update `config_manager.py` or `history_manager.py`
4. Handle migration if needed
5. Add tests

### Adding New UI Components

1. Create component in `ui/`
2. Integrate with main window
3. Add to settings if configurable
4. Add styling to `dark.qss`
5. Test with pytest-qt

## Performance Considerations

### Async/Await

All I/O operations use async/await for non-blocking execution:

```python
async def generate_response(self, prompt):
    response = await self.client.chat_completion(prompt)
    return response
```

### Connection Pooling

HTTP clients use connection pooling for efficiency:

```python
self.session = aiohttp.ClientSession(
    connector=aiohttp.TCPConnector(limit=10)
)
```

### Caching

Model information is cached to reduce API calls:

```python
@lru_cache(maxsize=128)
def get_model_info(self, provider, model):
    return self._fetch_model_info(provider, model)
```

### Lazy Loading

Providers are loaded only when needed:

```python
if provider_config.get("enabled"):
    provider = self._create_provider(provider_config)
```

## Technology Stack

- **GUI Framework**: PyQt6
- **HTTP Client**: aiohttp
- **Database**: SQLite (built-in)
- **Encryption**: cryptography (Fernet)
- **Markdown**: markdown-it-py
- **Testing**: pytest, pytest-qt
- **Code Quality**: black, flake8, mypy

## Design Patterns Used

- **Strategy Pattern**: Routing strategies
- **Factory Pattern**: Provider creation
- **Observer Pattern**: UI updates
- **Singleton Pattern**: Configuration manager
- **Template Method**: API client base class
- **Adapter Pattern**: Provider adapters

## Future Enhancements

- Plugin system for custom providers
- Multi-window support
- Voice interface
- RAG knowledge system
- Agent-based task automation
- System tray mode
- Custom themes
- Mobile version

## Next Steps

- [Read Development guide](Development)
- [Read API Providers guide](API-Providers)
- [Review the codebase](https://github.com/yourusername/chat-linux-client)
