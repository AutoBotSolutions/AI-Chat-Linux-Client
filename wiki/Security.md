[Security](Security)

This guide covers security features, best practices, and security architecture of Chat Linux Client.

Table of Contents
Overview
Security Features
API Key Security
Data Encryption
Network Security
Privacy Features
Security Best Practices
Security Auditing

Overview

Chat Linux Client is designed with security and privacy as core principles:
No telemetry: No data collection or analytics
Local-first: Data stored locally
Encryption: Optional encryption for sensitive data
HTTPS-only: All API communications use HTTPS
Open source: Fully auditable code

Security Features

No Telemetry

Chat Linux Client collects zero telemetry data:
No usage statistics
No crash reports
No analytics
No user tracking
No phone home

Local Data Storage

All data is stored locally on your machine:
Configuration: ~/.config/chat-linux-client/
Chat history: ~/.local/share/chat-linux-client/
Logs: ~/.local/share/chat-linux-client/logs/

Data is never sent to external servers except for AI API requests.

HTTPS-Only Communications

All API communications use HTTPS with certificate validation:

Input Validation

All user inputs are validated before processing:
API key format validation
Model name validation
Configuration validation
Path traversal prevention

API Key Security

Encryption at Rest

API keys are encrypted using Fernet symmetric encryption:

Key Derivation

Encryption keys are derived from passwords using PBKDF2:

Key Storage

Encrypted keys are stored at:

Password Protection

Set a password for key encryption:

Without a password, a local fallback key is used (less secure).

Key Validation

API keys are validated before use:

Data Encryption

Chat History Encryption

Enable encryption for chat history:
Open Settings
Navigate to Privacy tab
Enable "Encrypt Chats"
Set a password
Click Save

Important: Remember your password. Lost passwords cannot be recovered.

Encryption Implementation

Chat history is encrypted using SQLite encryption extensions:

Configuration Encryption

Sensitive configuration can be encrypted:

Network Security

HTTPS Enforcement

All API requests use HTTPS:

Certificate Validation

SSL certificates are validated by default:

No Proxy Intermediaries

No intermediate proxy servers are used. Direct connection to provider APIs.

Request Headers

Security headers are included in requests:

Privacy Features

Local Model Privacy

Using Ollama local models ensures:
Data never leaves your machine
No network requests
Complete privacy
No API costs

No Data Retention

Chat Linux Client does not:
Store data on cloud servers
Share data with third parties
Use data for training
Retain data beyond local storage

Optional Data Deletion

Delete data on exit:
Open Settings
Navigate to Privacy tab
Enable "Delete API Keys on Exit"
Enable "Clear Chat History on Exit"

Data Export Control

You have full control over your data:
Export chat history anytime
Delete specific chats
Clear all history
Backup encrypted data

Security Best Practices

For Users

API Key Management
Never share your API keys
Rotate keys regularly
Revoke unused keys
Use environment variables when possible
Enable encryption for key storage

Password Security
Use strong passwords for encryption
Don't reuse passwords
Store passwords securely
Remember encryption passwords (cannot be recovered)

Network Security
Use secure networks for cloud API calls
Avoid public WiFi for sensitive conversations
Keep software updated
Use VPN if needed

Local Models
Download from trusted sources (Ollama)
Keep models updated
Verify model integrity
Use local models for sensitive data

For Developers

Secret Management
Never hardcode secrets in code
Use environment variables
Add secrets to .gitignore
Validate all inputs
Use secure storage APIs

Dependency Management
Keep dependencies updated
Review security advisories
Use pip-audit to check vulnerabilities
Pin dependency versions
Review third-party code

Code Security
Follow secure coding practices
Use type hints
Handle errors properly
Sanitize user inputs
Use parameterized queries

[Testing](Testing)
Write security tests
Test edge cases
Test encryption/decryption
Test input validation
Perform security reviews

Security Auditing

Code Review

Regular security reviews should cover:
API key handling
Encryption implementation
Input validation
Error handling
Network security

Dependency Scanning

Scan for vulnerabilities:

Static Analysis

Use static analysis tools:

Penetration Testing

Test for:
SQL injection
XSS (if web interface added)
Path traversal
Command injection
Buffer overflows

Known Limitations

Encryption Password Recovery

Encryption passwords cannot be recovered. If lost:
Encrypted data is inaccessible
Must delete encrypted files
Start fresh with new password

Local Fallback Key

Without a password, a local fallback key is used:
Less secure than password-based encryption
Key is stored on the machine
Consider setting a password for better security

Cloud Provider Security

When using cloud providers:
Data is sent to provider servers
Subject to provider's privacy policy
Provider may store data temporarily
Review provider's security practices

Security Updates

Keeping Updated
Update application regularly
Review changelog for security fixes
Update dependencies
Monitor security advisories

Reporting Security Issues

If you find a security vulnerability:
Do NOT open a public issue
Email: security@example.com
Include details and reproduction steps
Allow time for fix before disclosure

Security Checklist

Before First Use
  Set encryption password
  Enable chat encryption (optional)
  Review privacy settings
  Understand data storage locations
  Configure API keys securely

Regular Maintenance
  Rotate API keys periodically
  Update application
  Update dependencies
  Review security settings
  Clear unnecessary chat history

For Sensitive Use
  Use local models (Ollama)
  Enable chat encryption
  Use strong encryption password
  Disable cloud providers
  Clear data after use

Next Steps
Read Configuration guide
Read Privacy section in FAQ
Review SECURITY.md in project root