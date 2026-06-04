Installation Guide

Complete installation guide for Chat Linux Client on Linux systems.

System Requirements

Minimum Requirements
Operating System: Linux (Ubuntu 20.04+, Debian 10+, Fedora 35+, Arch Linux)
Python: 3.8 or higher
Memory: 4GB RAM minimum
Storage: 10GB free space minimum
Graphics: GTK3 support

Recommended Requirements
Operating System: Ubuntu 22.04+ or equivalent
Python: 3.10 or higher
Memory: 8GB RAM or more
Storage: 20GB free space for multiple models
Graphics: Modern GTK3 desktop environment

Prerequisites Installation
Python and Development Tools

Ubuntu/Debian

Fedora/CentOS/RHEL

Arch Linux
GTK3 Libraries

Ubuntu/Debian

Fedora/CentOS/RHEL

Arch Linux
Ollama (Optional but Recommended)

Application Installation
Clone or Download the Repository

Option A: Git Clone (Recommended)

Option B: Download and Extract
Create Virtual Environment
Install Dependencies
Verify Installation

Initial Setup
Download Models (if using Ollama)
Create Desktop Entry (Optional)

Create ~/.local/share/applications/chat-linux-client.desktop:
Test Installation

The application should start and display the main window.

Configuration Files

Application Configuration
Location: ~/.config/chat-linux-client/config.json
Created automatically on first run
Contains: UI settings, provider configurations, chat preferences

Data Storage
Location: ~/.local/share/chat-linux-client/
Contains: Chat history, logs, temporary files

Ollama Models
Location: ~/.ollama/models/
Contains: Downloaded AI models

Troubleshooting Installation

Python Issues

ModuleNotFoundError

Permission Denied

GTK Issues

GTK module not found

Theme issues

Ollama Issues

Command not found

Permission denied

Application Issues

Import errors

Configuration errors

Post-Installation Setup
Configure Providers
Open the application
Go to Settings → Providers
Add API keys for cloud providers (OpenAI, Groq, etc.)
Optimize Performance
Go to Settings → Chat
Enable streaming responses
Set appropriate max tokens
Configure temperature
Customize UI
Go to Settings → UI
Choose theme (dark/light)
Adjust font size
Configure timestamps and model info
Test Functionality
Send a test message
Try different models
Test search functionality
Verify chat history saving

Upgrade Guide

From Previous Version

Clean Reinstall

Uninstallation

Remove Application

Remove Ollama (Optional)

Remove Virtual Environment

Support

For additional help:
Check the SYSTEMSTARTUPGUIDE.md
Review the SERVERSETUP.md
Check application logs in ~/.local/share/chat-linux-client/logs/
Report issues on the project repository

Next Steps

After successful installation:
Read the QUICKSTART.md for first-time usage
Configure your preferred AI models
Set up API keys for cloud providers
Start chatting with your AI assistant!