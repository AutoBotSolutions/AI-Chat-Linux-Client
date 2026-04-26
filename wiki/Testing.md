# Testing

This guide covers testing practices, test structure, and how to run tests for Chat Linux Client.

## Table of Contents

- [Overview](#overview)
- [Running Tests](#running-tests)
- [Test Structure](#test-structure)
- [Writing Tests](#writing-tests)
- [Test Coverage](#test-coverage)
- [Continuous Integration](#continuous-integration)
- [Best Practices](#best-practices)

## Overview

Chat Linux Client uses pytest for testing with pytest-qt for UI testing. The test suite covers:

- API client implementations
- Provider routing logic
- Configuration management
- Key storage and encryption
- UI components
- System checks
- Integration tests

## Running Tests

### Install Test Dependencies

```bash
pip install pytest pytest-qt pytest-cov pytest-asyncio
```

### Run All Tests

```bash
pytest tests/
```

### Run Specific Test File

```bash
pytest tests/test_api_client.py
```

### Run Specific Test Function

```bash
pytest tests/test_api_client.py::test_client_initialization
```

### Run with Verbose Output

```bash
pytest -v tests/
```

### Run with Coverage

```bash
pytest --cov=. --cov-report=html tests/
```

This generates an HTML coverage report in `htmlcov/index.html`.

### Run with Coverage Summary

```bash
pytest --cov=. --cov-report=term-missing tests/
```

### Run Only Fast Tests

```bash
pytest -m "not slow" tests/
```

### Run Only Slow Tests

```bash
pytest -m "slow" tests/
```

## Test Structure

### Test Directory Layout

```
tests/
├── conftest.py                    # Shared fixtures and configuration
├── test_api_client.py             # Base API client tests
├── test_groq_client.py            # Groq client tests
├── test_huggingface_client.py     # HuggingFace client tests
├── test_ollama_client.py          # Ollama client tests
├── test_openai_client.py          # OpenAI client tests
├── test_openrouter_client.py     # OpenRouter client tests
├── test_provider_router.py        # Provider routing tests
├── test_model_manager.py          # Model management tests
├── test_settings.py               # Settings tests
├── test_config_manager.py         # Configuration management tests
├── test_history_manager.py        # Chat history tests
├── test_key_handler.py            # Key storage tests
├── test_markdown_renderer.py      # Markdown rendering tests
├── test_system_checks.py          # System validation tests
├── test_main_window.py            # Main window UI tests
├── test_settings_dialog.py        # Settings dialog UI tests
└── test_integration.py            # Integration tests
```

### conftest.py

The `conftest.py` file contains shared fixtures:

```python
import pytest
from core.groq_client import GroqClient
from core.settings import Settings

@pytest.fixture
def sample_api_key():
    return "test_api_key_12345"

@pytest.fixture
def groq_client(sample_api_key):
    return GroqClient(api_key=sample_api_key)

@pytest.fixture
def settings():
    return Settings()
```

## Writing Tests

### Basic Test Structure

```python
import pytest
from core.groq_client import GroqClient

def test_client_initialization():
    """Test that GroqClient initializes correctly."""
    client = GroqClient(api_key="test_key")
    assert client.api_key == "test_key"
    assert client.base_url == "https://api.groq.com/openai/v1"
```

### Using Fixtures

```python
def test_client_with_fixture(groq_client):
    """Test client using fixture."""
    assert groq_client.api_key == "test_api_key_12345"
```

### Async Tests

```python
import pytest

@pytest.mark.asyncio
async def test_async_method():
    """Test async methods."""
    result = await some_async_function()
    assert result is not None
```

### UI Tests with pytest-qt

```python
from PyQt6.QtWidgets import QApplication
import pytest

@pytest.fixture
def app(qtbot):
    test_app = QApplication([])
    yield test_app
    test_app.quit()

def test_main_window(app, qtbot):
    """Test main window creation."""
    from ui.main_window import MainWindow
    window = MainWindow()
    qtbot.addWidget(window)
    assert window.isVisible()
```

### Parametrized Tests

```python
@pytest.mark.parametrize("temperature,expected", [
    (0.0, "very_focused"),
    (0.5, "balanced"),
    (1.0, "creative"),
])
def test_temperature_classification(temperature, expected):
    """Test temperature classification logic."""
    result = classify_temperature(temperature)
    assert result == expected
```

### Mocking External Dependencies

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_api_call_with_mock():
    """Test API call with mocked response."""
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {"result": "success"}
        mock_post.return_value.__aenter__.return_value = mock_response
        
        result = await api_call()
        assert result == "success"
```

### Testing Error Handling

```python
def test_invalid_api_key():
    """Test that invalid API key raises error."""
    with pytest.raises(ValueError, match="API key too short"):
        client = GroqClient(api_key="short")
```

## Test Coverage

### Coverage Goals

- **Overall coverage**: Aim for 80%+
- **Core modules**: Aim for 90%+
- **UI components**: Aim for 70%+ (harder to test)
- **Critical paths**: 100% coverage

### Coverage Reports

Generate coverage report:

```bash
pytest --cov=. --cov-report=html tests/
```

View report:
```bash
open htmlcov/index.html
```

### Excluding from Coverage

Add exclusions in `.coveragerc` or pytest configuration:

```ini
[coverage:omit]
*/tests/*
*/venv/*
*/__pycache__/*
setup.py
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-qt pytest-cov pytest-asyncio
      - name: Run tests
        run: pytest --cov=. --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Best Practices

### Test Organization

1. **One test per function**: Each test should test one thing
2. **Descriptive names**: Test names should describe what they test
3. **Arrange-Act-Assert**: Structure tests in AAA pattern
4. **Independent tests**: Tests should not depend on each other
5. **Fast tests**: Keep tests fast for quick feedback

### Test Data

1. **Use fixtures**: Share test data via fixtures
2. **Factory pattern**: Use factories for complex objects
3. **Minimal data**: Use only necessary test data
4. **Cleanup**: Clean up resources after tests

### Async Testing

1. **Use pytest-asyncio**: For async test support
2. **Mock async calls**: Mock external async calls
3. **Await results**: Always await async operations
4. **Timeout handling**: Add timeouts for async operations

### UI Testing

1. **Use pytest-qt**: For PyQt6 testing
2. **qtbot fixture**: Use qtbot for UI interaction
3. **Minimal UI**: Test logic, not just UI
4. **Headless when possible**: Run UI tests without display

### Error Testing

1. **Test exceptions**: Test that errors are raised
2. **Test error messages**: Verify error messages
3. **Test edge cases**: Test boundary conditions
4. **Test invalid inputs**: Test with invalid data

### Integration Testing

1. **Test workflows**: Test complete user workflows
2. **Use real components**: Test with real components when possible
3. **Mock external services**: Mock external APIs
4. **Test configuration**: Test with different configurations

## Common Test Patterns

### API Client Testing

```python
def test_api_client_headers():
    """Test that API client sets correct headers."""
    client = GroqClient(api_key="test_key")
    headers = client._get_headers()
    assert headers["Authorization"] == "Bearer test_key"
```

### Configuration Testing

```python
def test_config_loading(tmp_path):
    """Test configuration loading from file."""
    config_file = tmp_path / "config.json"
    config_file.write_text('{"test": "value"}')
    config = load_config(config_file)
    assert config["test"] == "value"
```

### Encryption Testing

```python
def test_encryption_roundtrip():
    """Test that encryption and decryption work."""
    original = "secret_data"
    encrypted = encrypt(original)
    decrypted = decrypt(encrypted)
    assert decrypted == original
```

### Streaming Testing

```python
@pytest.mark.asyncio
async def test_streaming_response():
    """Test streaming response handling."""
    chunks = ["Hello", " ", "World"]
    async def mock_stream():
        for chunk in chunks:
            yield chunk
    
    result = []
    async for chunk in mock_stream():
        result.append(chunk)
    
    assert "".join(result) == "Hello World"
```

## Debugging Tests

### Running with pdb

```bash
pytest --pdb tests/test_specific.py
```

### Stopping on first failure

```bash
pytest -x tests/
```

### Showing local variables on failure

```bash
pytest -l tests/
```

### Running with print statements

```bash
pytest -s tests/
```

## Performance Testing

### Benchmarking Tests

```python
import time

def test_performance():
    """Test that operation completes within time limit."""
    start = time.time()
    result = expensive_operation()
    duration = time.time() - start
    assert duration < 1.0  # Should complete in under 1 second
    assert result is not None
```

## Next Steps

- [Read Development guide](Development)
- [Read Architecture guide](Architecture)
- [Review test files in tests/](https://github.com/yourusername/chat-linux-client/tree/main/tests)
