Server Setup Guide

This guide covers server setup and management for Chat Linux Client.

Ollama Server

Installation

Starting the Server

Method 1: Automatic (Recommended)
The run script starts Ollama automatically:

Method 2: Manual

Method 3: Background Service

Server Configuration

Default Settings
Port: 11434
Host: 127.0.0.1 (localhost)
Models Directory: ~/.ollama/models

Environment Variables

Server Status

Check if running

Check available models

Server logs

Model Management

Download models

Remove models

Update models

Performance Tuning

Memory Usage
1B models: ~1-2GB RAM
3B models: ~3-4GB RAM  
7B models: ~5-8GB RAM

CPU Usage
Smaller models use less CPU
Consider system load when choosing models

Storage
Models stored in ~/.ollama/models
Each model takes 1-5GB disk space
Remove unused models to free space

Troubleshooting

Connection Issues

Model Issues

Performance Issues

Cloud Provider Setup

OpenAI
Get API key from https://platform.openai.com/api-keys
Add key in Settings → Providers → OpenAI

Groq
Get API key from https://console.groq.com/keys
Add key in Settings → Providers → Groq

OpenRouter
Get API key from https://openrouter.ai/keys
Add key in Settings → Providers → OpenRouter

HuggingFace
Get API key from https://huggingface.co/settings/tokens
Add key in Settings → Providers → HuggingFace

Security Considerations

Local Server
Ollama runs on localhost by default (secure)
Change to 0.0.0.0 only if network access is needed
Use firewall rules to restrict access

API Keys
Store API keys securely in the application
Keys are encrypted when saved
Never share API keys or commit them to version control

Network Access
Default: localhost only (most secure)
LAN access: Set OLLAMAHOST=0.0.0.0
Consider VPN for remote access

Advanced Configuration

Custom Server Script
Create ~/.local/bin/ollama-serve:

Make executable:

Systemd Service (Optional)
Create /etc/systemd/user/ollama.service:

Enable and start:

For more details, see SYSTEMSTARTUPGUIDE.md.