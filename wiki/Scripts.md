# Scripts

This guide covers the utility scripts provided with Chat Linux Client for installation, running, and building.

## Table of Contents

- [Overview](#overview)
- [Installation Script](#installation-script)
- [Run Script](#run-script)
- [AppImage Build Script](#appimage-build-script)
- [Custom Scripts](#custom-scripts)
- [Troubleshooting Scripts](#troubleshooting-scripts)

## Overview

Chat Linux Client includes several utility scripts in the `scripts/` directory:

- `install.sh` - Automated installation
- `run.sh` - Application launcher
- `build_appimage.sh` - AppImage builder

These scripts simplify common tasks and ensure consistency across different systems.

## Installation Script

### Location

`scripts/install.sh`

### Purpose

Automates the installation process including:
- Python version check
- Virtual environment creation
- Dependency installation
- Directory setup
- Permission configuration

### Usage

```bash
./scripts/install.sh
```

### What It Does

1. **Checks Python version**
   ```bash
   python_version=$(python3 --version 2>&1 | awk '{print $2}')
   # Verifies Python 3.8+
   ```

2. **Creates virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Installs dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Sets up directories**
   ```bash
   mkdir -p ~/.config/chat-linux-client
   mkdir -p ~/.local/share/chat-linux-client/logs
   ```

5. **Sets permissions**
   ```bash
   chmod +x scripts/*.sh
   ```

### Options

The script can be customized with environment variables:

```bash
# Skip Python version check
SKIP_PYTHON_CHECK=1 ./scripts/install.sh

# Use custom Python version
PYTHON_CMD=python3.9 ./scripts/install.sh

# Install to custom location
INSTALL_DIR=/custom/path ./scripts/install.sh
```

### Troubleshooting

**Python version too old**

```bash
# Install newer Python
sudo apt install python3.9
```

**Permission denied**

```bash
# Make script executable
chmod +x scripts/install.sh
```

**Dependency installation fails**

```bash
# Update pip first
pip install --upgrade pip
```

## Run Script

### Location

`scripts/run.sh`

### Purpose

Simple launcher for the application that:
- Activates virtual environment
- Runs the application
- Handles errors gracefully

### Usage

```bash
./scripts/run.sh
```

### What It Does

1. **Activates virtual environment**
   ```bash
   source venv/bin/activate
   ```

2. **Runs the application**
   ```bash
   python main.py "$@"
   ```

3. **Passes arguments**
   Any command-line arguments are passed to the application:
   ```bash
   ./scripts/run.sh --check-system
   ./scripts/run.sh --help
   ```

### Options

Pass arguments to the application:

```bash
# Run with system checks
./scripts/run.sh --check-system

# Run in debug mode
DEBUG=true ./scripts/run.sh

# Run with custom log level
LOG_LEVEL=DEBUG ./scripts/run.sh
```

### Creating Desktop Shortcut

Create a desktop entry that uses the run script:

```ini
[Desktop Entry]
Version=1.0
Type=Application
Name=Chat Linux Client
Exec=/path/to/chat-linux-client/scripts/run.sh
Icon=/path/to/chat-linux-client/assets/icon.png
Terminal=false
Categories=Utility;
```

## AppImage Build Script

### Location

`scripts/build_appimage.sh`

### Purpose

Builds a distributable AppImage package that:
- Includes all dependencies
- Works on most Linux distributions
- Requires no installation
- Is self-contained

### Usage

```bash
./scripts/build_appimage.sh
```

### What It Does

1. **Checks dependencies**
   - AppImage tools
   - Python
   - Required packages

2. **Creates build directory**
   ```bash
   mkdir -p build
   cd build
   ```

3. **Copies application files**
   ```bash
   cp -r ../core .
   cp -r ../ui .
   cp -r ../storage .
   cp -r ../utils .
   cp main.py .
   cp requirements.txt .
   ```

4. **Installs dependencies**
   ```bash
   pip install --target=./usr/lib/python3.9/site-packages -r requirements.txt
   ```

5. **Creates AppImage**
   ```bash
   appimage-builder --recipe ../packaging/AppImageBuilder.yml
   ```

6. **Signs AppImage** (optional)
   ```bash
   gpg --output Chat-Linux-Client.AppImage.sig --detach-sign Chat-Linux-Client.AppImage
   ```

### Requirements

The script requires:
- `appimage-builder`
- `patchelf`
- `desktop-file-validate`
- `zsyncmake`

Install on Ubuntu/Debian:
```bash
sudo apt install appimage-builder patchelf desktop-file-utils zsyncmake
```

### Options

```bash
# Build specific version
VERSION=1.0.0 ./scripts/build_appimage.sh

# Skip signing
SKIP_SIGNING=1 ./scripts/build_appimage.sh

# Custom output directory
OUTPUT_DIR=/custom/path ./scripts/build_appimage.sh
```

### Output

The script produces:
- `Chat-Linux-Client-VERSION-x86_64.AppImage` - The AppImage file
- `Chat-Linux-Client-VERSION-x86_64.AppImage.sig` - Signature (if signing enabled)
- `Chat-Linux-Client-VERSION-x86_64.AppImage.zsync` - Update info (for delta updates)

### Running the AppImage

```bash
# Make executable
chmod +x Chat-Linux-Client-VERSION-x86_64.AppImage

# Run
./Chat-Linux-Client-VERSION-x86_64.AppImage
```

### Troubleshooting

**Missing appimage-builder**

```bash
pip install appimage-builder
```

**Build fails with dependency errors**

```bash
# Install system dependencies
sudo apt install build-essential libssl-dev libffi-dev python3-dev
```

**AppImage won't run**

```bash
# Extract to debug
./Chat-Linux-Client.AppImage --appimage-extract
./squashfs-root/AppRun
```

## Custom Scripts

### System Check Script

Create a custom system check script:

```bash
#!/bin/bash
# scripts/check_system.sh

echo "Checking Chat Linux Client system requirements..."

# Check Python
python3 --version
if [ $? -ne 0 ]; then
    echo "Error: Python 3 not found"
    exit 1
fi

# Check PyQt6
python3 -c "import PyQt6" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Error: PyQt6 not installed"
    exit 1
fi

# Check Ollama (optional)
ollama --version 2>/dev/null
if [ $? -eq 0 ]; then
    echo "Ollama: Installed"
else
    echo "Ollama: Not installed (optional)"
fi

echo "System check complete!"
```

### Backup Script

Create a backup script for configuration and data:

```bash
#!/bin/bash
# scripts/backup.sh

BACKUP_DIR="$HOME/chat-linux-client-backup-$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

# Backup configuration
cp -r ~/.config/chat-linux-client "$BACKUP_DIR/"

# Backup data
cp -r ~/.local/share/chat-linux-client "$BACKUP_DIR/"

echo "Backup created at: $BACKUP_DIR"
```

### Cleanup Script

Create a cleanup script to remove old data:

```bash
#!/bin/bash
# scripts/cleanup.sh

echo "Cleaning up Chat Linux Client data..."

# Clear logs
rm -rf ~/.local/share/chat-linux-client/logs/*

# Clear old chats (older than 30 days)
find ~/.local/share/chat-linux-client -name "*.db" -mtime +30 -delete

echo "Cleanup complete!"
```

## Troubleshooting Scripts

### Script Not Executable

If scripts won't run:

```bash
chmod +x scripts/*.sh
```

### Wrong Python Version

If script complains about Python version:

```bash
# Check Python version
python3 --version

# Install newer Python
sudo apt install python3.9

# Or specify Python in script
PYTHON_CMD=python3.9 ./scripts/install.sh
```

### Virtual Environment Issues

If virtual environment has problems:

```bash
# Remove and recreate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Dependency Installation Fails

If dependencies won't install:

```bash
# Update pip
pip install --upgrade pip

# Try installing individually
pip install PyQt6
pip install aiohttp
pip install cryptography
```

## Script Best Practices

### When Writing Custom Scripts

1. **Use shebang**: `#!/bin/bash`
2. **Set permissions**: `chmod +x script.sh`
3. **Check dependencies**: Verify required tools
4. **Handle errors**: Use `set -e` for error handling
5. **Log actions**: Echo what's happening
6. **Clean up**: Remove temporary files
7. **Use variables**: Make scripts configurable

### Example Template

```bash
#!/bin/bash
set -e  # Exit on error

# Configuration
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$APP_DIR/venv"

# Functions
log() {
    echo "[$(date)] $1"
}

error() {
    echo "ERROR: $1" >&2
    exit 1
}

# Main script
log "Starting script..."
# Your code here
log "Script complete!"
```

## Next Steps

- [Read Installation guide](Installation)
- [Read Packaging guide](Packaging)
- [View script files](https://github.com/yourusername/chat-linux-client/tree/main/scripts)
