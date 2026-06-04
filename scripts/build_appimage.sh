#!/bin/bash

# Chat Linux Client AppImage Build Script
# This script creates an AppImage for easy distribution

set -e

echo "=== Building Chat Linux Client AppImage ==="

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="$PROJECT_DIR/build"
APPDIR="$BUILD_DIR/ChatLinuxClient.AppDir"

# Clean previous build
echo "Cleaning previous build..."
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# Install AppImageTool if not present
if ! command -v appimagetool &> /dev/null; then
    echo "Downloading AppImageTool..."
    wget -q https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
    chmod +x appimagetool-x86_64.AppImage
    sudo mv appimagetool-x86_64.AppImage /usr/local/bin/appimagetool
fi

# Create AppDir structure
echo "Creating AppDir structure..."
mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/lib"
mkdir -p "$APPDIR/usr/share/applications"
mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"

# Copy application files
echo "Copying application files..."
mkdir -p "$APPDIR/usr/bin/chat-linux-client"
cp -r "$PROJECT_DIR"/ui "$APPDIR/usr/bin/chat-linux-client/"
cp -r "$PROJECT_DIR"/core "$APPDIR/usr/bin/chat-linux-client/"
cp -r "$PROJECT_DIR"/storage "$APPDIR/usr/bin/chat-linux-client/"
cp -r "$PROJECT_DIR"/utils "$APPDIR/usr/bin/chat-linux-client/"
cp -r "$PROJECT_DIR"/site "$APPDIR/usr/bin/chat-linux-client/"
cp "$PROJECT_DIR"/main.py "$APPDIR/usr/bin/chat-linux-client/"
cp "$PROJECT_DIR"/requirements.txt "$APPDIR/usr/bin/chat-linux-client/"

# Create virtual environment in AppDir
echo "Creating virtual environment..."
cd "$APPDIR/usr/bin/chat-linux-client"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create launcher script
echo "Creating launcher script..."
cat > "$APPDIR/usr/bin/chat-linux-client/launcher.sh" << 'EOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
export PATH="${HERE}/venv/bin:${PATH}"
export PYTHONPATH="${HERE}:${PYTHONPATH}"
cd "${HERE}"
exec python3 main.py "$@"
EOF

chmod +x "$APPDIR/usr/bin/chat-linux-client/launcher.sh"

# Create desktop file
echo "Creating desktop file..."
cat > "$APPDIR/usr/share/applications/chat-linux-client.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Chat Linux Client
Comment=Private multi-provider AI desktop client
Exec=launcher.sh
Icon=chat-linux-client
Terminal=false
Categories=Network;Chat;
Keywords=AI;Chat;Assistant;LLM;
EOF

# Copy icon (create a simple one if not present)
if [ -f "$PROJECT_DIR/assets/icon.png" ]; then
    cp "$PROJECT_DIR/assets/icon.png" "$APPDIR/usr/share/icons/hicolor/256x256/apps/chat-linux-client.png"
else
    echo "Creating placeholder icon..."
    # Create a simple SVG icon
    cat > "$APPDIR/usr/share/icons/hicolor/256x256/apps/chat-linux-client.svg" << 'ICON_EOF'
<?xml version="1.0" encoding="UTF-8"?>
<svg width="256" height="256" viewBox="0 0 256 256" xmlns="http://www.w3.org/2000/svg">
  <rect width="256" height="256" fill="#2b2b2b"/>
  <rect x="20" y="20" width="216" height="216" rx="20" fill="#3c3c3c" stroke="#7ee0ff" stroke-width="2"/>
  <text x="128" y="140" font-family="Arial, sans-serif" font-size="24" fill="#7ee0ff" text-anchor="middle">AI</text>
  <text x="128" y="170" font-family="Arial, sans-serif" font-size="16" fill="#cfe9ff" text-anchor="middle">Chat</text>
</svg>
ICON_EOF
fi

# Create AppRun script
echo "Creating AppRun script..."
cat > "$APPDIR/AppRun" << 'EOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
export PATH="${HERE}/usr/bin:${PATH}"
exec "${HERE}/usr/bin/chat-linux-client/launcher.sh" "$@"
EOF
chmod +x "$APPDIR/AppRun"

# Download and integrate AppImage dependencies
echo "Downloading AppImage dependencies..."
cd "$BUILD_DIR"

# Download linuxdeploy
if [ ! -f "linuxdeploy-x86_64.AppImage" ]; then
    wget -q https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage
    chmod +x linuxdeploy-x86_64.AppImage
fi

# Create AppImage
echo "Creating AppImage..."
cd "$BUILD_DIR"
export ARCH=x86_64
./linuxdeploy-x86_64.AppImage --appdir="$APPDIR" --output appimage

# Move AppImage to project directory
APPIMAGE_FILE=$(find "$BUILD_DIR" -name "*.AppImage" -type f | head -n1)
if [ -n "$APPIMAGE_FILE" ]; then
    mv "$APPIMAGE_FILE" "$PROJECT_DIR/ChatLinuxClient-x86_64.AppImage"
    echo "AppImage created: $PROJECT_DIR/ChatLinuxClient-x86_64.AppImage"
else
    echo "Error: AppImage creation failed"
    exit 1
fi

# Clean up build directory
echo "Cleaning up build directory..."
rm -rf "$BUILD_DIR"

echo ""
echo "=== AppImage Build Complete ==="
echo "AppImage created: ChatLinuxClient-x86_64.AppImage"
echo ""
echo "To run the AppImage:"
echo "  1. Make it executable: chmod +x ChatLinuxClient-x86_64.AppImage"
echo "  2. Run it: ./ChatLinuxClient-x86_64.AppImage"
echo ""
echo "The AppImage is portable and should work on most Linux distributions."
