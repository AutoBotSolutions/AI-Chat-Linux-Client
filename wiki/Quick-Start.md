Quick Start Guide

This guide provides the fastest way to get Chat Linux Client up and running on your Linux system.

One-Command Startup

The fastest way to start the application:

Manual Quick Start
System Check

First, verify your system meets the requirements:
Navigate to Project
Activate Virtual Environment
Start Ollama (if not running)
Start Chat Linux Client

First Steps
Launch Application: Use one of the methods above
Select Model: Choose from the dropdown (recommended: ollama/llama3.2:1b)
Type Message: Enter your message in the input box
Send Message: Press Enter or click Send button
View Response: Response appears in real-time with streaming

Essential Shortcuts
Ctrl+L - Clear chat history
Ctrl+F - Toggle search
Ctrl+P - Open settings
F12 - Run system check

Quick Troubleshooting

Application Won't Start

Ollama Connection Failed

Performance Issues
Use llama3.2:1b model for fastest responses
Clear chat history with Ctrl+L
Check system resources with F12

Model Recommendations

 Model  Size  Speed  Use Case 

 llama3.2:1b  1.3 GB  ⚡⚡⚡⚡⚡  Quick responses, testing 
 qwen2.5:3b  1.9 GB  ⚡⚡⚡⚡  General purpose 
 phi3.5:3.8b  2.2 GB  ⚡⚡⚡  Complex tasks 
 mistral:7b  4.4 GB  ⚡⚡  High quality 

Service Status Check

Verify all services are running:

Next Steps
Configure API keys for cloud providers
Explore enhanced features
Learn keyboard shortcuts
Read troubleshooting guide

Support

For issues:
Run system check: python3 main.py --check-system
Check logs: tail -f chatclient.log
View FAQ for common questions