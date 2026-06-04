Chat Linux Client Wiki

Welcome to the Chat Linux Client documentation wiki. This is a privacy-first, multi-provider AI desktop client for Linux systems that unifies multiple AI providers and local models into a single conversational interface.

Quick Links

Getting Started
[Installation](Installation) - How to install and set up the application
[Quick Start](Quick-Start) - Fast startup guide
[System Startup](System-Startup) - Complete startup and service management
[Configuration](Configuration) - Configure API keys and settings
[Usage](Usage) - How to use the application

Core Features
[API Providers](API-Providers) - Supported AI providers and how to use them
[Model Management](Model-Management) - Local and cloud model setup
[Enhanced Features](Enhanced-Features) - Search, health monitoring, and more
[Keyboard Shortcuts](Keyboard-Shortcuts) - Complete shortcut reference
[Search Functionality](Search-Functionality) - Advanced search capabilities

Development & System
[Development](Development) - Development setup and contribution guide
[Architecture](Architecture) - System architecture and design
[Testing](Testing) - Test suite and validation
[System Validation](System-Validation) - Comprehensive validation results
[Performance & Remediation](Performance-and-Remediation) - Optimization and troubleshooting

Support
[Troubleshooting](Troubleshooting) - Common issues and solutions
[FAQ](FAQ) - Frequently asked questions
[Security](Security) - Security and privacy information

Features

Core Functionality
Multi-Provider Support: OpenAI, Ollama (local), Groq, HuggingFace, OpenRouter
Offline Capability: Full functionality with local Ollama models
Streaming Responses: Real-time token-by-token response rendering
Privacy-First: No telemetry, local key storage, optional encryption
Intelligent Routing: Automatic model selection based on requirements

Enhanced Features (NEW)
Advanced Search: Full-text search through chat history with highlighting
Health Monitoring: Real-time provider and system health tracking
Performance Metrics: Response time and token generation monitoring
System Remediation: One-click fixes for common issues
Model Information Display: Detailed model metadata and capabilities
Enhanced UI: Improved user experience with modern interface

System Features
Extensible Architecture: Plugin system for custom providers and tools
Modern UI: Dark/light themes with PyQt6 interface
Comprehensive Logging: Detailed application and system logging
Service Management: Automated service startup and monitoring
Site Deployment: Local website with complete documentation

System Requirements
Python: 3.8+ (tested with Python 3.13.5)
Operating System: Linux (Ubuntu 18.04+, Fedora 30+, Arch Linux)
Memory: 4GB RAM minimum (8GB+ recommended for larger models)
Storage: 10GB+ free space for models
Dependencies: PyQt6 6.8.2+, cryptography 43.0.0+
Optional: Ollama 0.20.7+ for local AI models

Current System Status

✅ Validated Components (June 3, 2026)
Top-Down Validation: 96.4% success rate
Bottom-Up Validation: 100% success rate
Core-Outward Validation: 100% success rate
System Status: Production Ready

🚀 Active Services
Ollama Server: Running with 4 local models
Chat Linux Client: Running with 70 total models
Documentation Site: Complete local site available

Getting Started
Install the application
Quick Start guide for fast setup
Configure your API keys
Start chatting with enhanced features

Support

For issues and questions:
Check the Troubleshooting section
Run system checks for diagnostics: python main.py --check-system
Create an issue on the project repository

License

This project is licensed under the MIT License - see the LICENSE file for details.