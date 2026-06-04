System Startup Guide

This guide covers comprehensive startup procedures for Chat Linux Client, including service management, monitoring, and troubleshooting.

Current System Status

✅ Verified Components (June 3, 2026)
Platform: Linux 6.19.11-2-liquorix-amd64 (x8664)
Python: 3.13.5
PyQt6: 6.8.2
Cryptography: 43.0.0
Ollama: 0.20.7
Available Models: 4 local models installed
Application Status: Running successfully with 70 total models

🚀 Active Services
Ollama Server: Running on http://localhost:11434 (PID: 11769)
Chat Linux Client: Running (PID: 14567)
Model Warmup: Completed for llama3.2:1b

Startup Methods

Method 1: Automated Startup (Recommended)

The run script automatically:
Adds $HOME/.local/bin to PATH
Auto-starts Ollama if installed but not running
Sets proper environment variables for GTK modules
Handles error recovery

Method 2: Manual Startup

Method 3: Service Management

Service Management

Ollama Server Management

Start Ollama

Verify Ollama

Stop Ollama

Chat Client Management

Start Application

Background Mode

Stop Application

Health Monitoring

Quick Status Check

Detailed Health Check

Log Management

Monitor Logs

Log Analysis

Performance Monitoring

Resource Usage

Response Time Monitoring

Troubleshooting Startup Issues

Ollama Issues

Problem: Ollama not found

Problem: Ollama server not responding

Problem: No models available

Application Issues

Problem: Application won't start

Problem: GUI not appearing

Problem: Provider connection issues

Automation Scripts

Complete Startup Script

Health Monitor Script

Configuration Files

Service Configuration
Ollama Config: ~/.ollama/config
Chat Client Config: ~/.config/chat-linux-client/
Data Directory: ~/.local/share/chat-linux-client/
Log Files: chatclient.log, ollamaserver.log

Environment Variables

System Integration

Desktop Entry
Create ~/.local/share/applications/chat-linux-client.desktop:

Autostart Configuration
Create ~/.config/autostart/chat-linux-client.desktop:

Next Steps
Configure providers for cloud services
Set up models for optimal performance
Explore enhanced features
Learn troubleshooting for common issues

Support

For startup issues:
Check logs: tail -f chatclient.log
Run diagnostics: python3 main.py --check-system
View troubleshooting guide
Create issue on project repository