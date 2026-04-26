# Contributing to Chat Linux Client

Thank you for your interest in contributing to Chat Linux Client! This document provides guidelines and instructions for contributing to the project.

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When creating a bug report, include:

- **Description**: A clear and concise description of the bug
- **Steps to reproduce**: Detailed steps to reproduce the behavior
- **Expected behavior**: What you expected to happen
- **Actual behavior**: What actually happened
- **Environment**: 
  - OS and version
  - Python version
  - Application version (if known)
- **Logs**: Relevant log entries if available
- **Screenshots**: If applicable, add screenshots to help explain the problem

### Suggesting Enhancements

Enhancement suggestions are welcome! Please include:

- **Description**: A clear and concise description of the enhancement
- **Motivation**: Why this enhancement would be useful
- **Use cases**: Specific scenarios where this enhancement would be beneficial
- **Alternatives**: Any alternative solutions or features you've considered

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following the code style guidelines
3. **Add tests** if your change adds or modifies functionality
4. **Update documentation** if needed
5. **Ensure all tests pass** by running `pytest tests/`
6. **Submit a pull request** with a clear description of your changes

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment (recommended)

### Setting Up Development Environment

```bash
# Clone your fork
git clone https://github.com/yourusername/chat-linux-client.git
cd chat-linux-client

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install pytest pytest-qt black flake8 mypy
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_specific_file.py

# Run with coverage
pytest --cov=.
```

### Code Style

We follow standard Python code style:

- **Formatting**: Use `black .` to format code
- **Linting**: Use `flake8 .` to check for issues
- **Type checking**: Use `mypy .` for static type checking

Please run these tools before submitting a pull request.

## Project Structure

```
chat-linux-client/
├── core/           # Core AI provider logic
├── ui/             # User interface components
├── storage/        # Data persistence
├── utils/          # Utility modules
├── tests/          # Test suite
└── scripts/        # Build and run scripts
```

## Coding Guidelines

### General Principles

- Write clear, readable code with descriptive variable and function names
- Add docstrings to all functions, classes, and modules
- Keep functions focused and small
- Follow the existing code style and patterns
- Add error handling where appropriate
- Log important events and errors

### Specific Guidelines

- **Async/Await**: Use async/await for I/O operations
- **Type Hints**: Include type hints for function signatures
- **Error Handling**: Use specific exception types
- **Logging**: Use the logging module, not print statements
- **Configuration**: Use the config manager, don't hardcode values

### Adding New AI Providers

When adding a new AI provider:

1. Create a new client file in `core/` (e.g., `newprovider_client.py`)
2. Inherit from `APIClient` base class
3. Implement required methods: `chat_completion`, `chat_completion_stream`, `test_connection`
4. Add provider configuration to `core/settings.py`
5. Register the provider in `core/provider_router.py`
6. Add tests in `tests/`
7. Update documentation

## Documentation

- Keep README.md up to date with new features
- Add docstrings to all public APIs
- Update relevant documentation files for new features
- Include examples in docstrings where helpful

## License

By contributing to Chat Linux Client, you agree that your contributions will be licensed under the MIT License.

## Questions?

If you have questions about contributing, feel free to:

- Open an issue with your question
- Check existing issues and discussions
- Review the codebase for similar patterns

Thank you for contributing to Chat Linux Client!
