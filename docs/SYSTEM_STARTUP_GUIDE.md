# System Startup Guide

This guide covers the recommended startup path for Chat Linux Client on Linux.

## 1) Open a terminal in the project

```bash
cd '/home/robbie/Desktop/Desktop Client/chat-linux-client'
```

## 2) Activate the virtual environment

```bash
source venv/bin/activate
```

## 3) Ensure Ollama is available

The app uses Ollama at `http://127.0.0.1:11434`.

Check version:

```bash
export PATH="$HOME/.local/bin:$PATH"
ollama --version
```

If needed, start Ollama manually:

```bash
export PATH="$HOME/.local/bin:$PATH"
nohup ollama serve >/tmp/ollama-serve.log 2>&1 &
```

Check server and models:

```bash
curl -s http://127.0.0.1:11434/api/tags | head
ollama list
```

## 4) Start the app (recommended)

Use the project run script:

```bash
bash ./scripts/run.sh
```

Notes:
- The run script now adds `$HOME/.local/bin` to `PATH`.
- The run script auto-starts Ollama if installed but not running.

## 5) Verify startup in logs

Healthy startup should include lines like:
- `Ollama connection successful`
- `Ollama provider initialized successfully`
- `Application started successfully`

## 6) If responses are slow

Use the lightweight model in the UI model dropdown:
- `ollama/llama3.2:1b`

Also keep chats shorter or clear chat periodically to reduce context size.

## Troubleshooting

### A) Error: Cannot connect to host localhost:11434

Run:

```bash
export PATH="$HOME/.local/bin:$PATH"
ollama serve
```

Then restart the app.

### B) `ollama: command not found`

Run with local binary path:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

If still missing, reinstall the local binary.

### C) GTK warning about canberra module

`Failed to load module "canberra-gtk3-module"` is a non-fatal desktop warning and does not block chat functionality.

## One-command startup

```bash
cd '/home/robbie/Desktop/Desktop Client/chat-linux-client' && source venv/bin/activate && bash ./scripts/run.sh
```
