# Packaging and Distribution

This guide covers how to package and distribute Chat Linux Client for different platforms and distribution methods.

## Table of Contents

- [Overview](#overview)
- [AppImage](#appimage)
- [Desktop Entry](#desktop-entry)
- [Distribution Methods](#distribution-methods)
- [Versioning](#versioning)
- [Release Process](#release-process)

## Overview

Chat Linux Client supports multiple packaging formats for easy distribution:

- **AppImage**: Universal Linux package format
- **Desktop Entry**: Integration with Linux desktop environments
- **Source Distribution**: For manual installation
- **Package Managers**: Future support for snap, flatpak, etc.

## AppImage

AppImage is a universal Linux package format that works on most Linux distributions without installation.

### Building AppImage

Use the provided build script:

```bash
./scripts/build_appimage.sh
```

### AppImage Configuration

The AppImage is configured using `packaging/AppImageBuilder.yml`:

```yaml
version: 1.0.0
app:
  id: chat-linux-client
  name: Chat Linux Client
  icon: assets/icon.png
  version: 1.0.0
  exec: python main.py
runtime:
  env:
    PYTHONPATH: $APPDIR/usr/lib/python3.9/site-packages
```

### AppImage Structure

The AppImage includes:
- Python runtime
- All dependencies
- Application code
- Assets and resources
- Desktop entry file

### Running AppImage

```bash
chmod +x Chat-Linux-Client-1.0.0-x86_64.AppImage
./Chat-Linux-Client-1.0.0-x86_64.AppImage
```

### AppImage Advantages

- **No installation required**: Run directly
- **Universal**: Works on most Linux distributions
- **Self-contained**: Includes all dependencies
- **Sandboxed**: Isolated from system

### AppImage Limitations

- **Size**: Larger than native packages (includes runtime)
- **Updates**: Manual update process
- **Integration**: Limited desktop integration

## Desktop Entry

The desktop entry file integrates the application with Linux desktop environments.

### Desktop Entry File

Located at `packaging/chatgpt-client.desktop`:

```ini
[Desktop Entry]
Version=1.0
Type=Application
Name=Chat Linux Client
Comment=Privacy-first multi-provider AI desktop client
Exec=/usr/bin/chat-linux-client
Icon=chat-linux-client
Terminal=false
Categories=Utility;Network;
Keywords=AI;Chat;Assistant;
StartupNotify=true
```

### Installing Desktop Entry

```bash
# Copy to applications directory
sudo cp packaging/chatgpt-client.desktop /usr/share/applications/

# Copy icon
sudo cp assets/icon.png /usr/share/icons/hicolor/256x256/apps/chat-linux-client.png

# Update desktop database
sudo update-desktop-database /usr/share/applications/
```

### Desktop Entry Fields

- **Name**: Application name
- **Comment**: Short description
- **Exec**: Command to run
- **Icon**: Icon name or path
- **Terminal**: Whether to run in terminal
- **Categories**: Application categories
- **Keywords**: Search keywords

## Distribution Methods

### Source Distribution

Distribute source code for manual installation:

```bash
# Create source distribution
python setup.py sdist

# Or use git archive
git archive --format=tar.gz --prefix=chat-linux-client-1.0.0/ HEAD > chat-linux-client-1.0.0.tar.gz
```

### GitHub Releases

1. Tag the release:
```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

2. Create release on GitHub
3. Upload artifacts:
   - AppImage file
   - Source tarball
   - Installation script

### Direct Download

Host files for direct download:
- AppImage for quick download
- Installation script
- Source code archive

### Package Managers (Future)

#### Snap

```yaml
# snap/snapcraft.yaml
name: chat-linux-client
version: '1.0.0'
summary: Privacy-first AI client
description: Multi-provider AI desktop client
confinement: strict
grade: stable

apps:
  chat-linux-client:
    command: python3 main.py
    plugs:
      - network
      - home

parts:
  chat-linux-client:
    plugin: python
    source: .
```

#### Flatpak

```xml
<!-- com.github.username.chat-linux-client.json -->
{
  "app-id": "com.github.username.chat-linux-client",
  "runtime": "org.freedesktop.Platform",
  "runtime-version": "22.08",
  "sdk": "org.freedesktop.Sdk",
  "command": "python3 main.py",
  "finish-args": [
    "--share=network",
    "--filesystem=home"
  ],
  "modules": [
    {
      "name": "chat-linux-client",
      "buildsystem": "simple",
      "build-commands": [
        "pip3 install --prefix=/app ."
      ],
      "sources": [
        {
          "type": "dir",
          "path": "."
        }
      ]
    }
  ]
}
```

## Versioning

Chat Linux Client follows Semantic Versioning (SemVer): `MAJOR.MINOR.PATCH`

- **MAJOR**: Incompatible API changes
- **MINOR**: Backwards-compatible functionality additions
- **PATCH**: Backwards-compatible bug fixes

### Version Examples

- `1.0.0`: Initial stable release
- `1.1.0`: New feature (backwards compatible)
- `1.1.1`: Bug fix
- `2.0.0`: Breaking changes

### Updating Version

Update version in:
1. `packaging/AppImageBuilder.yml`
2. Desktop entry file
3. README.md
4. CHANGELOG.md
5. Application code (if version is displayed)

## Release Process

### Pre-Release Checklist

- [ ] All tests passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version numbers updated
- [ ] AppImage builds successfully
- [ ] Installation script tested
- [ ] Security review completed
- [ ] Dependencies updated

### Release Steps

1. **Update Version**
   ```bash
   # Update version in all files
   # Update CHANGELOG.md
   git commit -am "Bump version to X.Y.Z"
   ```

2. **Create Tag**
   ```bash
   git tag -a vX.Y.Z -m "Release version X.Y.Z"
   git push origin vX.Y.Z
   ```

3. **Build Artifacts**
   ```bash
   ./scripts/build_appimage.sh
   ```

4. **Create GitHub Release**
   - Go to GitHub Releases
   - Click "Create new release"
   - Select tag
   - Add release notes
   - Upload artifacts

5. **Announce**
   - Update README with latest version
   - Post announcement
   - Update documentation

### Post-Release

- [ ] Monitor for issues
- [ ] Gather feedback
- [ ] Plan next release
- [ ] Update roadmap

## Signing Packages

### GPG Signing

Sign packages for verification:

```bash
# Sign AppImage
gpg --output Chat-Linux-Client-1.0.0-x86_64.AppImage.sig --detach-sign Chat-Linux-Client-1.0.0-x86_64.AppImage

# Verify signature
gpg --verify Chat-Linux-Client-1.0.0-x86_64.AppImage.sig Chat-Linux-Client-1.0.0-x86_64.AppImage
```

### Checksums

Generate checksums for integrity verification:

```bash
# Generate SHA256 checksum
sha256sum Chat-Linux-Client-1.0.0-x86_64.AppImage > SHA256SUMS

# Verify checksum
sha256sum -c SHA256SUMS
```

## Troubleshooting Packaging

### AppImage Won't Run

```bash
# Make executable
chmod +x Chat-Linux-Client-1.0.0-x86_64.AppImage

# Extract to debug
./Chat-Linux-Client-1.0.0-x86_64.AppImage --appimage-extract

# Run extracted
./squashfs-root/AppRun
```

### Desktop Entry Not Showing

```bash
# Verify desktop entry syntax
desktop-file-validate packaging/chatgpt-client.desktop

# Update desktop database
update-desktop-database /usr/share/applications/

# Check icon path
ls /usr/share/icons/hicolor/256x256/apps/
```

### Missing Dependencies in AppImage

Ensure all dependencies are listed in `requirements.txt` and included in AppImage configuration.

## Next Steps

- [Read Installation guide](Installation)
- [Read Development guide](Development)
- [View packaging files](https://github.com/yourusername/chat-linux-client/tree/main/packaging)
