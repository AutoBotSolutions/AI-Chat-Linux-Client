Server Startup Guide

This guide covers starting and managing the Chat Linux Client servers and services.

Overview

The Chat Linux Client requires two main services:
Ollama Server - Local AI model service (optional but recommended)
Chat Linux Client Application - Main desktop application

Quick Start

One-Command Startup

Manual Startup

Ollama Server Management

Check Ollama Installation

Expected Output:

Start Ollama Server

Verify Ollama Server

Expected Models:

Stop Ollama Server

Chat Linux Client Application

Start Application

Start Application in Background

Verify Application Startup

Check the application logs:

Expected Log Output:

Stop Application

Service Status Monitoring

Check All Services

Monitor Logs

Advanced Configuration

Ollama Configuration

Set Custom Ollama Host

Configure Ollama Models Directory

Chat Client Configuration

Environment Variables

Command Line Arguments

Troubleshooting

Common Issues
Ollama Server Not Starting

Symptoms:
curl: Connection refused on localhost:11434
ollama list returns error

Solutions:
Chat Client Not Connecting to Ollama

Symptoms:
"Cannot connect to host localhost:11434" error
No models available in dropdown

Solutions:
Application Not Starting

Symptoms:
No GUI window appears
Process exits immediately

Solutions:
GTK Module Warnings

Symptoms:
Failed to load module "canberra-gtk3-module" warnings

Solutions:

Performance Issues
Slow Response Times

Solutions:
High Memory Usage

Solutions:

Automation Scripts

Start All Services

Create startall.sh:

Stop All Services

Create stopall.sh:

Service Status Script

Create status.sh:

System Integration

Desktop Entry (Linux)

Create ~/.local/share/applications/chat-linux-client.desktop:

Autostart Configuration

Create ~/.config/autostart/chat-linux-client.desktop:

Security Considerations

Network Security
Ollama server runs on localhost only (secure)
No external network exposure required
API keys are encrypted when stored

File Permissions
Configuration files: ~/.config/chat-linux-client/
Data files: ~/.local/share/chat-linux-client/
Logs: Application directory with user permissions

API Key Management
Keys are encrypted using Fernet encryption
Password can be set via CHATCLIENT_PASSWORD environment variable
Keys are stored in encrypted configuration files

Last Updated: June 3, 2026  
System Status: All services operational