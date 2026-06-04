Chat Linux Client

A modern, feature-rich AI chat client for Linux with support for both local and cloud-based AI models.

Features

🤖 Multi-Provider Support
Local Models: Ollama integration for privacy-focused local AI
Cloud Models: OpenAI, Groq, OpenRouter, HuggingFace
Hybrid Approach: Mix local and cloud models seamlessly

💬 Advanced Chat Features
Real-time streaming responses
Chat history with full search functionality and highlighting
Enhanced model information display with real-time metadata
Export conversations (JSON, text, markdown)
Customizable chat settings
Performance metrics tracking for models

🎨 Modern UI/UX
Dark and light themes with professional styling
Responsive design with accessibility features
Comprehensive keyboard shortcuts (Ctrl+L, Ctrl+F, Ctrl+T, Ctrl+M, Ctrl+P, Ctrl+K, Ctrl+U, F12)
Advanced search toolbar with highlighting and navigation
Professional provider health monitoring dashboard
Real-time status bar tooltips with detailed provider information

🔧 System Integration
System health checks with one-click remediation fixes
Real-time performance monitoring and metrics tracking
Configuration persistence with validation
Comprehensive error handling and logging
Automated dependency installation and permission fixes
Ollama service management and startup

Quick Start

One-Command Startup

Requirements
Linux with GTK3 support
Python 3.8+
Ollama (optional, for local models)

Documentation

📚 Getting Started
QUICKSTART.md - Get running in minutes
INSTALLATIONGUIDE.md - Complete setup instructions
SYSTEMSTARTUPGUIDE.md - Detailed startup procedures

⚙️ Configuration
SERVERSETUP.md - Server and model setup
MODELSETUP.md - Model configuration
[SECURITY](SECURITY.md) - Security considerations

🛠️ Development
[CONTRIBUTING](CONTRIBUTING.md) - How to contribute
CODEOFCONDUCT.md - Community guidelines
[CHANGELOG](CHANGELOG.md) - Version history

📋 Technical Details
IMPLEMENTATIONSUMMARY.md - Architecture overview
UIIMPLEMENTATIONFIXES.md - UI improvements
SETTINGSDIALOGENHANCEMENTS.md - Settings system
THEMESYSTEMIMPLEMENTATION.md - Theme system
ERRORLOGGINGIMPROVEMENTS.md - Error handling

🚀 Enhanced Features
ENHANCEDMODELINFORMATION.md - Model metadata and performance tracking
KEYBOARDSHORTCUTSANDSEARCH.md - Keyboard shortcuts and search functionality
PROVIDERHEALTHMONITORING.md - Health monitoring dashboard
SYSTEMREMEDIATIONANDPERFORMANCE.md - System remediation and performance tracking

🌐 Cloud Providers
CLOUDPROVIDERSSTATUS.md - Provider compatibility

Available Models

Local Models (Ollama)
llama3.2:1b - Fast, lightweight (1.3GB)
qwen2.5:3b - Balanced performance (1.9GB)
phi3.5:3.8b - Good capability (2.2GB)
mistral:7b - High quality (4.4GB)

Cloud Models
OpenAI: GPT-3.5-turbo, GPT-4, GPT-4-turbo
Groq: Llama2-70b-4096, Mixtral-8x7b
OpenRouter: Various models
HuggingFace: Open-source models

System Architecture

Installation

Prerequisites

Quick Install

Usage

Basic Chat
Launch the application
Select a model from the dropdown
Type your message and press Enter
View the AI response in real-time

Advanced Features
Search: Use Ctrl+F to search chat history
Export: Save conversations via File menu
Settings: Configure providers, UI, and chat options
System Check: Run diagnostics via Help menu

Performance Tips
Use lightweight models: llama3.2:1b for fastest responses
Enable streaming: Real-time response display
Clear history: Reduce context size for better performance
Local models: Use Ollama for privacy and offline access

Troubleshooting

Common Issues
Ollama not found: export PATH="$HOME/.local/bin:$PATH"
Connection errors: Start Ollama with ollama serve &
GTK warnings: Non-fatal, can be ignored

Getting Help
Check the documentation in /docs/
Review system logs in ~/.local/share/chat-linux-client/logs/
Report issues on the project repository

Development

Project Structure

Running Tests

Contributing
Fork the repository
Create a feature branch
Make your changes
Add tests if applicable
Submit a pull request

License

This project is licensed under the MIT License - see the LICENSE file for details.

Support

For support and questions:
📖 Check the documentation in /docs/
🐛 Report issues on the project repository
💬 Join the community discussions

Chat Linux Client - Your gateway to AI-powered conversations on Linux.