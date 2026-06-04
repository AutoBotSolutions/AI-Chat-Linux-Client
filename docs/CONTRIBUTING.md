Contributing to Chat Linux Client

Thank you for your interest in contributing to Chat Linux Client! This document provides guidelines and instructions for contributing to the project.

How to Contribute

Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When creating a bug report, include:
Description: A clear and concise description of the bug
Steps to reproduce: Detailed steps to reproduce the behavior
Expected behavior: What you expected to happen
Actual behavior: What actually happened
Environment: 
OS and version
Python version
Application version (if known)
Logs: Relevant log entries if available
Screenshots: If applicable, add screenshots to help explain the problem

Suggesting Enhancements

Enhancement suggestions are welcome! Please include:
Description: A clear and concise description of the enhancement
Motivation: Why this enhancement would be useful
Use cases: Specific scenarios where this enhancement would be beneficial
Alternatives: Any alternative solutions or features you've considered

Pull Requests
Fork the repository and create your branch from main
Make your changes following the code style guidelines
Add tests if your change adds or modifies functionality
Update documentation if needed
Ensure all tests pass by running pytest tests/
Submit a pull request with a clear description of your changes

Development Setup

Prerequisites
Python 3.8 or higher
Git
Virtual environment (recommended)

Setting Up Development Environment

Running Tests

Code Style

We follow standard Python code style:
Formatting: Use black . to format code
Linting: Use flake8 . to check for issues
Type checking: Use mypy . for static type checking

Please run these tools before submitting a pull request.

Project Structure

Coding Guidelines

General Principles
Write clear, readable code with descriptive variable and function names
Add docstrings to all functions, classes, and modules
Keep functions focused and small
Follow the existing code style and patterns
Add error handling where appropriate
Log important events and errors

Specific Guidelines
Async/Await: Use async/await for I/O operations
Type Hints: Include type hints for function signatures
Error Handling: Use specific exception types
Logging: Use the logging module, not print statements
Configuration: Use the config manager, don't hardcode values

Adding New AI Providers

When adding a new AI provider:
Create a new client file in core/ (e.g., newproviderclient.py)
Inherit from APIClient base class
Implement required methods: chatcompletion, chatcompletionstream, testconnection
Add provider configuration to core/settings.py
Register the provider in core/providerrouter.py
Add tests in tests/
Update documentation

Documentation
Keep [README](README.md) up to date with new features
Add docstrings to all public APIs
Update relevant documentation files for new features
Include examples in docstrings where helpful

License

By contributing to Chat Linux Client, you agree that your contributions will be licensed under the MIT License.

Questions?

If you have questions about contributing, feel free to:
Open an issue with your question
Check existing issues and discussions
Review the codebase for similar patterns

Thank you for contributing to Chat Linux Client!