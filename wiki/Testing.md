[Testing](Testing)

This guide covers testing practices, test structure, and how to run tests for Chat Linux Client.

Table of Contents
Overview
Running Tests
Test Structure
Writing Tests
Test Coverage
Continuous Integration
Best Practices

Overview

Chat Linux Client uses pytest for testing with pytest-qt for UI testing. The test suite covers:
API client implementations
Provider routing logic
Configuration management
Key storage and encryption
UI components
System checks
Integration tests

Running Tests

Install Test Dependencies

Run All Tests

Run Specific Test File

Run Specific Test Function

Run with Verbose Output

Run with Coverage

This generates an HTML coverage report in htmlcov/index.html.

Run with Coverage Summary

Run Only Fast Tests

Run Only Slow Tests

Test Structure

Test Directory Layout

conftest.py

The conftest.py file contains shared fixtures:

Writing Tests

Basic Test Structure

Using Fixtures

Async Tests

UI Tests with pytest-qt

Parametrized Tests

Mocking External Dependencies

Testing Error Handling

Test Coverage

Coverage Goals
Overall coverage: Aim for 80%+
Core modules: Aim for 90%+
UI components: Aim for 70%+ (harder to test)
Critical paths: 100% coverage

Coverage Reports

Generate coverage report:

View report:

Excluding from Coverage

Add exclusions in .coveragerc or pytest configuration:

Continuous Integration

GitHub Actions Example

Best Practices

Test Organization
One test per function: Each test should test one thing
Descriptive names: Test names should describe what they test
Arrange-Act-Assert: Structure tests in AAA pattern
Independent tests: Tests should not depend on each other
Fast tests: Keep tests fast for quick feedback

Test Data
Use fixtures: Share test data via fixtures
Factory pattern: Use factories for complex objects
Minimal data: Use only necessary test data
Cleanup: Clean up resources after tests

Async Testing
Use pytest-asyncio: For async test support
Mock async calls: Mock external async calls
Await results: Always await async operations
Timeout handling: Add timeouts for async operations

UI Testing
Use pytest-qt: For PyQt6 testing
qtbot fixture: Use qtbot for UI interaction
Minimal UI: Test logic, not just UI
Headless when possible: Run UI tests without display

Error Testing
Test exceptions: Test that errors are raised
Test error messages: Verify error messages
Test edge cases: Test boundary conditions
Test invalid inputs: Test with invalid data

Integration Testing
Test workflows: Test complete user workflows
Use real components: Test with real components when possible
Mock external services: Mock external APIs
Test configuration: Test with different configurations

Common Test Patterns

API Client Testing

Configuration Testing

Encryption Testing

Streaming Testing

Debugging Tests

Running with pdb

Stopping on first failure

Showing local variables on failure

Running with print statements

Performance Testing

Benchmarking Tests

Next Steps
Read Development guide
Read Architecture guide
Review test files in tests/