[Scripts](Scripts)

This guide covers the utility scripts provided with Chat Linux Client for installation, running, and building.

Table of Contents
Overview
Installation Script
Run Script
AppImage Build Script
Custom Scripts
Troubleshooting Scripts

Overview

Chat Linux Client includes several utility scripts in the scripts/ directory:
install.sh - Automated installation
run.sh - Application launcher
buildappimage.sh - AppImage builder

These scripts simplify common tasks and ensure consistency across different systems.

Installation Script

Location

scripts/install.sh

Purpose

Automates the installation process including:
Python version check
Virtual environment creation
Dependency installation
Directory setup
Permission configuration

[Usage](Usage)

What It Does
Checks Python version
Creates virtual environment
Installs dependencies
Sets up directories
Sets permissions

Options

The script can be customized with environment variables:

[Troubleshooting](Troubleshooting)

Python version too old

Permission denied

Dependency installation fails

Run Script

Location

scripts/run.sh

Purpose

Simple launcher for the application that:
Activates virtual environment
Runs the application
Handles errors gracefully

[Usage](Usage)

What It Does
Activates virtual environment
Runs the application
Passes arguments
   Any command-line arguments are passed to the application:

Options

Pass arguments to the application:

Creating Desktop Shortcut

Create a desktop entry that uses the run script:

AppImage Build Script

Location

scripts/buildappimage.sh

Purpose

Builds a distributable AppImage package that:
Includes all dependencies
Works on most Linux distributions
Requires no installation
Is self-contained

[Usage](Usage)

What It Does
Checks dependencies
AppImage tools
Python
Required packages
Creates build directory
Copies application files
Installs dependencies
Creates AppImage
Signs AppImage (optional)

Requirements

The script requires:
appimage-builder
patchelf
desktop-file-validate
zsyncmake

Install on Ubuntu/Debian:

Options

Output

The script produces:
Chat-Linux-Client-VERSION-x8664.AppImage - The AppImage file
Chat-Linux-Client-VERSION-x8664.AppImage.sig - Signature (if signing enabled)
Chat-Linux-Client-VERSION-x8664.AppImage.zsync - Update info (for delta updates)

Running the AppImage

[Troubleshooting](Troubleshooting)

Missing appimage-builder

Build fails with dependency errors

AppImage won't run

Custom Scripts

System Check Script

Create a custom system check script:

Backup Script

Create a backup script for configuration and data:

Cleanup Script

Create a cleanup script to remove old data:

Troubleshooting Scripts

Script Not Executable

If scripts won't run:

Wrong Python Version

If script complains about Python version:

Virtual Environment Issues

If virtual environment has problems:

Dependency Installation Fails

If dependencies won't install:

Script Best Practices

When Writing Custom Scripts
Use shebang: #!/bin/bash
Set permissions: chmod +x script.sh
Check dependencies: Verify required tools
Handle errors: Use set -e for error handling
Log actions: Echo what's happening
Clean up: Remove temporary files
Use variables: Make scripts configurable

Example Template

Next Steps
Read Installation guide
Read Packaging guide
View script files