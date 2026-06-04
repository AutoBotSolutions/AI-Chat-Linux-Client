System Startup Guide

This guide covers the recommended startup path for Chat Linux Client on Linux.

1) Open a terminal in the project

2) Activate the virtual environment

3) Ensure Ollama is available

The app uses Ollama at http://localhost:11434 for local AI model support.

Check version:

If needed, start Ollama manually:

Check server and models:

Available models should include:
phi3.5:3.8b (2.2 GB)
mistral:7b (4.4 GB)
qwen2.5:3b (1.9 GB)
llama3.2:1b (1.3 GB) - Recommended for performance

4) Start the app (recommended)

Use the project run script:

Notes:
The run script automatically adds $HOME/.local/bin to PATH
The run script auto-starts Ollama if installed but not running
The run script sets proper environment variables for GTK modules

5) Verify startup in logs

Healthy startup should include lines like:
Ollama connection successful
Ollama provider initialized successfully
Application started successfully
Providers initialized: 'ollama', 'groq', 'openai'
Models discovered: number models

6) If responses are slow

Use the lightweight model in the UI model dropdown:
ollama/llama3.2:1b (recommended for best performance)

Also keep chats shorter or clear chat periodically to reduce context size.

Troubleshooting

A) Error: Cannot connect to host localhost:11434

Run:

Then restart the app.

B) ollama: command not found

Run with local binary path:

If still missing, reinstall the local binary.

C) GTK warning about canberra module

Failed to load module "canberra-gtk3-module" is a non-fatal desktop warning and does not block chat functionality.

One-command startup

Manual Startup (Alternative)

If you prefer manual startup:

Current System Status (Last Verified: June 3, 2026)

✅ Verified Working Components
Platform: Linux 6.19.11-2-liquorix-amd64 (x86_64)
Python: 3.13.5
PyQt6: 6.8.2 (GUI Framework)
Cryptography: 43.0.0 (Security)
Ollama: 0.20.7 (Local AI Provider)
Available Models: 4 local models installed
Application Status: Running successfully with 70 total models

🚀 Active Services
Ollama Server: Running on http://localhost:11434
Chat Linux Client: Running (Process ID: 14567)
Model Warmup: Completed for llama3.2:1b

📊 Model Availability
Local Models: 4 models (phi3.5:3.8b, mistral:7b, qwen2.5:3b, llama3.2:1b)
Cloud Models: 66 models available (API keys required)
Total Models: 70 models across 5 providers
Live Models: 31 models from 1 available provider (Ollama)

System Requirements
Python: 3.8+ (tested with Python 3.13.5)
Ollama: 0.20.7+ for local AI model support (optional but recommended)
PyQt6: 6.8.2+ for GUI components
Cryptography: 43.0.0+ for secure key storage
Memory: Minimum 4GB RAM, 8GB+ recommended for larger models
Storage: Minimum 10GB free space for models

Available Models

The application supports both local and cloud models:

Local Models (via Ollama)
phi3.5:3.8b - 2.2 GB - Good balance of speed and capability
mistral:7b - 4.4 GB - Higher quality, slower
qwen2.5:3b - 1.9 GB - Fast, good for general use
llama3.2:1b - 1.3 GB - Fastest, basic capability

Cloud Models (API keys required)
OpenAI: GPT-3.5-turbo, GPT-4, GPT-4-turbo
Groq: Llama2-70b-4096, Mixtral-8x7b
OpenRouter: Various models
HuggingFace: Open-source models

Performance Tips
Use lightweight models: llama3.2:1b for fastest responses
Clear chat history: Reduces context size and improves speed
Configure streaming: Enable in settings for real-time responses
Monitor system resources: Check CPU and memory usage during operation