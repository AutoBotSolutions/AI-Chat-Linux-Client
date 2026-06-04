[Architecture](Architecture)

This document describes the system architecture and design of Chat Linux Client.

Table of Contents
Overview
System Architecture
Component Architecture
Data Flow
Provider Architecture
Storage Architecture
Security Architecture
Extension Points

Overview

Chat Linux Client follows a modular, layered architecture with clear separation of concerns:

System Architecture

Layered Design

The system is organized into five distinct layers:
UI Layer: PyQt6-based desktop interface
Routing Layer: Intelligent model selection and request routing
Provider Layer: Multiple AI provider implementations
Storage Layer: Persistent configuration and chat history
Utility Layer: Helper functions and system integration

Design Principles
Separation of Concerns: Each layer has a distinct responsibility
Dependency Injection: Components receive dependencies through constructors
Interface-Based Design: Providers implement common interfaces
Async/Await: I/O operations use async for performance
Error-First: Errors are handled gracefully with fallbacks

Component Architecture

UI Layer (ui/)

Main Window (mainwindow.py)
Manages the primary application window
Handles user interactions
Coordinates between UI and backend
Manages chat sessions

Settings Dialog (settingsdialog.py)
Configuration interface
API key management
Provider settings
Privacy settings

Routing Layer (core/providerrouter.py)

Provider Router
Selects appropriate provider based on strategy
Manages provider availability
Implements fallback logic
Handles request routing

Routing Strategies
OFFLINEFIRST: Prefer local models
SPEEDOPTIMAL: Prefer fast models
COSTOPTIMAL: Prefer free options
QUALITYOPTIMAL: Prefer capable models

Provider Layer (core/)

Base API Client (apiclient.py)
Abstract base class for all providers
Defines common interface
Implements shared functionality

Provider Implementations
ollamaclient.py: Local Ollama models
groqclient.py: Groq API
huggingfaceclient.py: HuggingFace API
openrouterclient.py: OpenRouter API
openaiclient.py: OpenAI API

Model Manager (modelmanager.py)
Manages model information
Provides model selection logic
Handles model metadata

Storage Layer (storage/)

Config Manager (configmanager.py)
Manages application configuration
Handles provider settings
Supports encryption
Persists to JSON

History Manager (historymanager.py)
Manages chat history
SQLite database storage
Export functionality
Search capabilities

Utility Layer (utils/)

Markdown Renderer (markdownrenderer.py)
Converts Markdown to HTML
Syntax highlighting for code
Sanitizes output

Key Handler (keyhandler.py)
Secure API key storage
Encryption/decryption
Key validation
Password management

System Checks (systemchecks.py)
Validates system requirements
Checks dependencies
Verifies resources

Data Flow

Chat Request Flow

Configuration Flow

History Flow

Provider Architecture

Provider Interface

All providers implement the APIClient interface:

Provider Lifecycle
Initialization: Provider created with API key and base URL
Availability Check: Router tests provider connection
Model Registration: Provider registers available models
Request Handling: Provider handles chat requests
Streaming: Provider streams responses if supported
Error Handling: Provider handles errors gracefully

Streaming Implementation

Providers use Server-Sent Events (SSE) for streaming:

Storage Architecture

Configuration Storage

Location: ~/.config/chat-linux-client/config.json

Structure:

History Storage

Location: ~/.local/share/chat-linux-client/chathistory.db

Schema:

Key Storage

Location: ~/.config/chat-linux-client/apikeys.enc

Encryption: Fernet symmetric encryption

Key Derivation: PBKDF2 with SHA-256

Security Architecture

API Key Security
Encryption: Keys encrypted at rest using Fernet
Memory: Keys kept in memory only when needed
Transmission: HTTPS for all API calls
Validation: Key format validation before use

Chat History Security
Optional Encryption: Chat history can be encrypted
Local Storage: Data stored locally, not in cloud
Access Control: File system permissions protect data
No Telemetry: No data collection or analytics

Network Security
HTTPS Only: All API communications use HTTPS
Certificate Validation: SSL certificate validation enabled
No Proxy: No intermediate proxy servers
Direct Connection: Direct connection to provider APIs

Extension Points

Adding New Providers
Implement APIClient interface
Add provider configuration to settings.py
Register in providerrouter.py
Add model information to modelmanager.py
Add tests and documentation

Adding New Routing Strategies
Define strategy in providerrouter.py
Implement selection logic
Add to strategy enum
Update UI to include option
Add tests

Adding New Storage Backends
Implement storage interface
Add configuration option
Update configmanager.py or historymanager.py
Handle migration if needed
Add tests

Adding New UI Components
Create component in ui/
Integrate with main window
Add to settings if configurable
Add styling to dark.qss
Test with pytest-qt

Performance Considerations

Async/Await

All I/O operations use async/await for non-blocking execution:

Connection Pooling

HTTP clients use connection pooling for efficiency:

Caching

Model information is cached to reduce API calls:

Lazy Loading

Providers are loaded only when needed:

Technology Stack
GUI Framework: PyQt6
HTTP Client: aiohttp
Database: SQLite (built-in)
Encryption: cryptography (Fernet)
Markdown: markdown-it-py
Testing: pytest, pytest-qt
Code Quality: black, flake8, mypy

Design Patterns Used
Strategy Pattern: Routing strategies
Factory Pattern: Provider creation
Observer Pattern: UI updates
Singleton Pattern: Configuration manager
Template Method: API client base class
Adapter Pattern: Provider adapters

Future Enhancements
Plugin system for custom providers
Multi-window support
Voice interface
RAG knowledge system
Agent-based task automation
System tray mode
Custom themes
Mobile version

Next Steps
Read Development guide
Read API Providers guide
Review the codebase