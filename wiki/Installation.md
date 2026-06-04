[Installation](Installation)

This guide covers how to install and set up Chat Linux Client on your Linux system.

Table of Contents
System Requirements
Quick Installation
Manual Installation
Docker Installation
Package Manager Installation
Installing Ollama (Optional)
Building AppImage
Verifying Installation
Troubleshooting Installation

System Requirements
Python: 3.8+ (tested with Python 3.13.5)
Operating System: Linux (Ubuntu 18.04+, Fedora 30+, Arch Linux)
Memory: 4GB RAM minimum (8GB+ recommended for larger models)
Storage: 10GB+ free space for models
Dependencies: PyQt6 6.8.2+, cryptography 43.0.0+
Optional: Ollama 0.20.7+ for local AI models

Quick Installation

Using the Installation Script

The easiest way to install Chat Linux Client is using the provided installation script:

The installation script will:
Check Python version
Create a virtual environment
Install all dependencies
Set up the application structure

Docker Installation

Using Docker Compose (Recommended)

Create docker-compose.yml:

Deploy with Docker

Dockerfile

Create Dockerfile:

Package Manager Installation

Ubuntu/Debian (.deb)

Fedora/RHEL (.rpm)

Arch Linux (AUR)

Manual Installation

If you prefer manual installation or need more control:

Step 1: Clone the Repository

Step 2: Create Virtual Environment

Step 3: Install Dependencies

Step 4: Run the Application

Installing Ollama (Optional)

For offline AI support with local models, install Ollama:

Install Ollama

Start Ollama Service

Pull Models

Verify Ollama Installation

You should see the models you've pulled listed.

Building AppImage

To create a distributable AppImage:

This will create an AppImage file in the build/ directory that can be run on any Linux system without installation.

Verifying Installation

Run System Checks

This will verify:
Python version compatibility
Required dependencies
Ollama availability (if installed)
System resources

Test the Application

The application window should open with:
Model dropdown showing available models
Chat input field
Settings menu accessible

Common Installation Issues

Python Version Too Old

Error: Python 3.8 or higher required

Solution: Install a newer Python version:

Missing Dependencies

Error: ModuleNotFoundError: No module named '...'

Solution: Ensure you installed dependencies:

Permission Errors

Error: Permission denied when running scripts

Solution: Make scripts executable:

PyQt6 Installation Fails

Error: PyQt6 installation fails on some systems

Solution: Install system dependencies first:

Uninstallation

To remove Chat Linux Client:

Next Steps

After installation:
Configure API keys
Learn how to use the application