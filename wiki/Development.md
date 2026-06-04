[Development](Development)

This guide covers development setup, coding standards, and contribution guidelines for Chat Linux Client.

Table of Contents
Development Setup
Project Structure
Coding Standards
[Testing](Testing)
Adding Features
Adding Providers
Building and Packaging
Debugging

Development Setup

Prerequisites
Python 3.8 or higher
Git
Virtual environment (recommended)

Setting Up Development Environment

Running the Application

Project Structure

Coding Standards

Code Style

We follow standard Python conventions:

General Principles
Write clear, readable code with descriptive names
Add docstrings to all functions, classes, and modules
Keep functions focused and small
Follow existing code patterns
Add error handling where appropriate
Use logging, not print statements

Type Hints

Include type hints for function signatures:

Docstrings

Use Google-style docstrings:

Error Handling

Use specific exception types:

[Testing](Testing)

Running Tests

Test Structure

Tests are organized by module:

Writing Tests

Use pytest fixtures and follow naming convention test.py:

Adding Features

Adding a New Feature
Create a feature branch:
Implement the feature following coding standards
Add tests for the new feature
Update documentation if needed
Run tests to ensure nothing breaks:
Commit changes:
Push and create pull request

Adding UI Components

UI components are in the ui/ directory using PyQt6:

Adding Providers

Steps to Add a New Provider
Create the client file in core/:
Add provider configuration to core/settings.py:
Register provider in core/providerrouter.py:
Add tests in tests/:
Update documentation:
Add to README.md
Update API-Providers wiki page
Add model information to core/modelmanager.py

Building and Packaging

Building AppImage

This creates an AppImage in the build/ directory.

Creating Desktop Entry

The desktop entry is in packaging/chatgpt-client.desktop:

Running Installation Script

Debugging

Enable Debug Logging

View Logs

Logs are stored at:

Use Python Debugger

Common Debugging Techniques
Add logging statements:
Use print statements (for quick debugging):
Check configuration:
Test individual components:

Performance Profiling

Profile with cProfile

Memory Profiling

Contributing

Pull Request Process
Fork the repository
Create a feature branch
Make your changes
Add tests
Ensure all tests pass
Update documentation
Submit a pull request

Code Review Checklist
  Code follows style guidelines
  Tests are included and passing
  Documentation is updated
  No hardcoded secrets
  Error handling is appropriate
  Logging is added where needed

Next Steps
Read Architecture guide
Read API Providers guide
Review the codebase