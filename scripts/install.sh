#!/bin/bash

# Chat Linux Client Installation Script
# This script installs dependencies and sets up the application

set -e

echo "=== Chat Linux Client Installation ==="

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python 3.8 or higher is required. Found: $python_version"
    exit 1
fi

echo "Python version check passed: $python_version"

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed. Please install pip3 first."
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create desktop entry
echo "Creating desktop entry..."
desktop_file="$HOME/.local/share/applications/chat-linux-client.desktop"
cat > "$desktop_file" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Chat Linux Client
Comment=Private multi-provider AI desktop client
Exec=$(pwd)/scripts/run.sh
Icon=$(pwd)/assets/icon.png
Terminal=false
Categories=Network;Chat;
Keywords=AI;Chat;Assistant;LLM;
EOF

# Make run script executable
chmod +x scripts/run.sh

# Check for Ollama
if command -v ollama &> /dev/null; then
    echo "Ollama is already installed"
else
    echo "Ollama not found. For local AI models, consider installing Ollama:"
    echo "  curl -fsSL https://ollama.ai/install.sh | sh"
fi

# Create config directory if it doesn't exist
config_dir="$HOME/.config/chat-linux-client"
mkdir -p "$config_dir"

# Create data directory if it doesn't exist
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    data_dir="$HOME/.local/share/chat-linux-client"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    data_dir="$HOME/Library/Application Support/chat-linux-client"
else
    data_dir="$HOME/AppData/Local/ChatLinuxClient/data"
fi
mkdir -p "$data_dir"

echo ""
echo "=== Installation Complete ==="
echo "To run the application:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run: python main.py"
echo "  Or use the run script: ./scripts/run.sh"
echo ""
echo "Desktop entry created. You can find 'Chat Linux Client' in your application menu."
echo ""
echo "Next steps:"
echo "  1. Configure API keys in the application settings"
echo "  2. Install Ollama for local models (optional)"
echo "  3. Select your preferred AI provider and start chatting!"
