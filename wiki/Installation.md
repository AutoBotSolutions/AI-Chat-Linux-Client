# Installation

This guide covers how to install and set up Chat Linux Client on your Linux system.

## Table of Contents

- [System Requirements](#system-requirements)
- [Quick Installation](#quick-installation)
- [Manual Installation](#manual-installation)
- [Installing Ollama (Optional)](#installing-ollama-optional)
- [Building AppImage](#building-appimage)
- [Verifying Installation](#verifying-installation)

## System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Linux (Ubuntu 20.04+, Fedora 35+, Arch Linux)
- **Memory**: 4GB RAM minimum (8GB recommended)
- **Storage**: 500MB free space
- **Optional**: Ollama for local AI models

## Quick Installation

### Using the Installation Script

The easiest way to install Chat Linux Client is using the provided installation script:

```bash
# Clone the repository
git clone https://github.com/yourusername/chat-linux-client.git
cd chat-linux-client

# Run the installation script
./scripts/install.sh

# Run the application
./scripts/run.sh
```

The installation script will:
- Check Python version
- Create a virtual environment
- Install all dependencies
- Set up the application structure

## Manual Installation

If you prefer manual installation or need more control:

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/chat-linux-client.git
cd chat-linux-client
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run the Application

```bash
python main.py
```

## Installing Ollama (Optional)

For offline AI support with local models, install Ollama:

### Install Ollama

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Start Ollama Service

```bash
ollama serve
```

### Pull Models

```bash
# Lightweight model for fast responses
ollama pull llama3.2:1b

# Balanced model
ollama pull qwen2.5:3b

# More capable model
ollama pull mistral:7b
```

### Verify Ollama Installation

```bash
ollama list
```

You should see the models you've pulled listed.

## Building AppImage

To create a distributable AppImage:

```bash
./scripts/build_appimage.sh
```

This will create an AppImage file in the `build/` directory that can be run on any Linux system without installation.

## Verifying Installation

### Run System Checks

```bash
python main.py --check-system
```

This will verify:
- Python version compatibility
- Required dependencies
- Ollama availability (if installed)
- System resources

### Test the Application

```bash
python main.py
```

The application window should open with:
- Model dropdown showing available models
- Chat input field
- Settings menu accessible

## Common Installation Issues

### Python Version Too Old

**Error**: `Python 3.8 or higher required`

**Solution**: Install a newer Python version:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.9 python3.9-venv

# Fedora
sudo dnf install python39

# Arch Linux
sudo pacman -S python
```

### Missing Dependencies

**Error**: `ModuleNotFoundError: No module named '...'`

**Solution**: Ensure you installed dependencies:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Permission Errors

**Error**: `Permission denied` when running scripts

**Solution**: Make scripts executable:
```bash
chmod +x scripts/*.sh
```

### PyQt6 Installation Fails

**Error**: PyQt6 installation fails on some systems

**Solution**: Install system dependencies first:
```bash
# Ubuntu/Debian
sudo apt install libxcb-xinerama0

# Fedora
sudo dnf install libxcb

# Arch Linux
sudo pacman -S libxcb
```

## Uninstallation

To remove Chat Linux Client:

```bash
# Deactivate virtual environment
deactivate

# Remove the application directory
cd ..
rm -rf chat-linux-client

# Remove configuration and data (optional)
rm -rf ~/.config/chat-linux-client
rm -rf ~/.local/share/chat-linux-client
```

## Next Steps

After installation:
1. [Configure API keys](Configuration)
2. [Learn how to use the application](Usage)
