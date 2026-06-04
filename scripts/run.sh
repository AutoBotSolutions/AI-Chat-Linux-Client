#!/bin/bash

# Chat Linux Client Run Script
# This script activates the virtual environment and runs the application

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Change to project directory
cd "$PROJECT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run the install script first:"
    echo "  ./scripts/install.sh"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Set PYTHONPATH to include the project directory
export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"

# Ensure user-local binaries are discoverable (e.g., rootless Ollama install)
export PATH="$HOME/.local/bin:$PATH"

# Avoid optional GTK module lookup noise on systems without canberra module.
export GTK_MODULES=""

# Start Ollama automatically if installed but not running
if command -v ollama >/dev/null 2>&1; then
    if ! pgrep -af "ollama serve" >/dev/null 2>&1; then
        echo "Starting Ollama service..."
        nohup ollama serve >/tmp/ollama-serve.log 2>&1 &
        sleep 1
    fi
fi

# Run the application
echo "Starting Chat Linux Client..."
python3 main.py "$@"
