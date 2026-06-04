Packaging and Distribution

This guide covers how to package and distribute Chat Linux Client for different platforms and distribution methods.

Table of Contents
Overview
AppImage
Desktop Entry
Distribution Methods
Versioning
Release Process

Overview

Chat Linux Client supports multiple packaging formats for easy distribution:
AppImage: Universal Linux package format
Desktop Entry: Integration with Linux desktop environments
Source Distribution: For manual installation
Package Managers: Future support for snap, flatpak, etc.

AppImage

AppImage is a universal Linux package format that works on most Linux distributions without installation.

Building AppImage

Use the provided build script:

AppImage Configuration

The AppImage is configured using packaging/AppImageBuilder.yml:

AppImage Structure

The AppImage includes:
Python runtime
All dependencies
Application code
Assets and resources
Desktop entry file

Running AppImage

AppImage Advantages
No installation required: Run directly
Universal: Works on most Linux distributions
Self-contained: Includes all dependencies
Sandboxed: Isolated from system

AppImage Limitations
Size: Larger than native packages (includes runtime)
Updates: Manual update process
Integration: Limited desktop integration

Desktop Entry

The desktop entry file integrates the application with Linux desktop environments.

Desktop Entry File

Located at packaging/chatgpt-client.desktop:

Installing Desktop Entry

Desktop Entry Fields
Name: Application name
Comment: Short description
Exec: Command to run
Icon: Icon name or path
Terminal: Whether to run in terminal
Categories: Application categories
Keywords: Search keywords

Distribution Methods

Source Distribution

Distribute source code for manual installation:

GitHub Releases
Tag the release:
Create release on GitHub
Upload artifacts:
AppImage file
Source tarball
Installation script

Direct Download

Host files for direct download:
AppImage for quick download
Installation script
Source code archive

Package Managers (Future)

Snap

Flatpak

Versioning

Chat Linux Client follows Semantic Versioning (SemVer): MAJOR.MINOR.PATCH
MAJOR: Incompatible API changes
MINOR: Backwards-compatible functionality additions
PATCH: Backwards-compatible bug fixes

Version Examples
1.0.0: Initial stable release
1.1.0: New feature (backwards compatible)
1.1.1: Bug fix
2.0.0: Breaking changes

Updating Version

Update version in:
packaging/AppImageBuilder.yml
Desktop entry file
README.md
CHANGELOG.md
Application code (if version is displayed)

Release Process

Pre-Release Checklist
  All tests passing
  Documentation updated
  CHANGELOG.md updated
  Version numbers updated
  AppImage builds successfully
  Installation script tested
  Security review completed
  Dependencies updated

Release Steps
Update Version
Create Tag
Build Artifacts
Create GitHub Release
Go to GitHub Releases
Click "Create new release"
Select tag
Add release notes
Upload artifacts
Announce
Update README with latest version
Post announcement
Update documentation

Post-Release
  Monitor for issues
  Gather feedback
  Plan next release
  Update roadmap

Signing Packages

GPG Signing

Sign packages for verification:

Checksums

Generate checksums for integrity verification:

Troubleshooting Packaging

AppImage Won't Run

Desktop Entry Not Showing

Missing Dependencies in AppImage

Ensure all dependencies are listed in requirements.txt and included in AppImage configuration.

Next Steps
Read Installation guide
Read Development guide
View packaging files