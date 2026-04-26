# Security

This guide covers security features, best practices, and security architecture of Chat Linux Client.

## Table of Contents

- [Overview](#overview)
- [Security Features](#security-features)
- [API Key Security](#api-key-security)
- [Data Encryption](#data-encryption)
- [Network Security](#network-security)
- [Privacy Features](#privacy-features)
- [Security Best Practices](#security-best-practices)
- [Security Auditing](#security-auditing)

## Overview

Chat Linux Client is designed with security and privacy as core principles:

- **No telemetry**: No data collection or analytics
- **Local-first**: Data stored locally
- **Encryption**: Optional encryption for sensitive data
- **HTTPS-only**: All API communications use HTTPS
- **Open source**: Fully auditable code

## Security Features

### No Telemetry

Chat Linux Client collects **zero** telemetry data:

- No usage statistics
- No crash reports
- No analytics
- No user tracking
- No phone home

### Local Data Storage

All data is stored locally on your machine:

- **Configuration**: `~/.config/chat-linux-client/`
- **Chat history**: `~/.local/share/chat-linux-client/`
- **Logs**: `~/.local/share/chat-linux-client/logs/`

Data is never sent to external servers except for AI API requests.

### HTTPS-Only Communications

All API communications use HTTPS with certificate validation:

```python
# aiohttp with SSL verification
async with aiohttp.ClientSession() as session:
    async with session.post(url, ssl=True) as response:
        # Process response
```

### Input Validation

All user inputs are validated before processing:

- API key format validation
- Model name validation
- Configuration validation
- Path traversal prevention

## API Key Security

### Encryption at Rest

API keys are encrypted using Fernet symmetric encryption:

```python
from cryptography.fernet import Fernet

# Generate encryption key
key = Fernet.generate_key()
cipher = Fernet(key)

# Encrypt API key
encrypted = cipher.encrypt(api_key.encode())

# Decrypt API key
decrypted = cipher.decrypt(encrypted).decode()
```

### Key Derivation

Encryption keys are derived from passwords using PBKDF2:

```python
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=480000,
)
key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
```

### Key Storage

Encrypted keys are stored at:

```
~/.config/chat-linux-client/api_keys.enc
```

### Password Protection

Set a password for key encryption:

```bash
# Environment variable
export CHAT_CLIENT_PASSWORD=your_password

# Or through settings
```

Without a password, a local fallback key is used (less secure).

### Key Validation

API keys are validated before use:

```python
def validate_key_format(provider, api_key):
    validators = {
        "openai": lambda k: k.startswith("sk-") and len(k) >= 20,
        "groq": lambda k: k.startswith("gsk_") and len(k) >= 20,
        "openrouter": lambda k: k.startswith("sk-or-") and len(k) >= 20,
    }
    return validators[provider](api_key)
```

## Data Encryption

### Chat History Encryption

Enable encryption for chat history:

1. Open Settings
2. Navigate to Privacy tab
3. Enable "Encrypt Chats"
4. Set a password
5. Click Save

**Important**: Remember your password. Lost passwords cannot be recovered.

### Encryption Implementation

Chat history is encrypted using SQLite encryption extensions:

```python
# Encrypt before storing
encrypted_data = cipher.encrypt(chat_content.encode())

# Store in database
cursor.execute("INSERT INTO messages (content) VALUES (?)", (encrypted_data,))

# Decrypt when retrieving
decrypted_data = cipher.decrypt(encrypted_data).decode()
```

### Configuration Encryption

Sensitive configuration can be encrypted:

```python
# Encrypt sensitive fields
config["api_key"] = encrypt(config["api_key"])

# Save encrypted config
save_config(config)
```

## Network Security

### HTTPS Enforcement

All API requests use HTTPS:

```python
base_urls = {
    "openai": "https://api.openai.com/v1",
    "groq": "https://api.groq.com/openai/v1",
    # All URLs use HTTPS
}
```

### Certificate Validation

SSL certificates are validated by default:

```python
# Certificate validation enabled
session = aiohttp.ClientSession()
```

### No Proxy Intermediaries

No intermediate proxy servers are used. Direct connection to provider APIs.

### Request Headers

Security headers are included in requests:

```python
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "User-Agent": "Chat-Linux-Client/1.0.0"
}
```

## Privacy Features

### Local Model Privacy

Using Ollama local models ensures:

- Data never leaves your machine
- No network requests
- Complete privacy
- No API costs

### No Data Retention

Chat Linux Client does not:

- Store data on cloud servers
- Share data with third parties
- Use data for training
- Retain data beyond local storage

### Optional Data Deletion

Delete data on exit:

1. Open Settings
2. Navigate to Privacy tab
3. Enable "Delete API Keys on Exit"
4. Enable "Clear Chat History on Exit"

### Data Export Control

You have full control over your data:

- Export chat history anytime
- Delete specific chats
- Clear all history
- Backup encrypted data

## Security Best Practices

### For Users

#### API Key Management

- **Never share** your API keys
- **Rotate keys** regularly
- **Revoke unused** keys
- **Use environment variables** when possible
- **Enable encryption** for key storage

#### Password Security

- **Use strong passwords** for encryption
- **Don't reuse** passwords
- **Store passwords** securely
- **Remember** encryption passwords (cannot be recovered)

#### Network Security

- **Use secure networks** for cloud API calls
- **Avoid public WiFi** for sensitive conversations
- **Keep software updated**
- **Use VPN** if needed

#### Local Models

- **Download from trusted sources** (Ollama)
- **Keep models updated**
- **Verify model integrity**
- **Use local models** for sensitive data

### For Developers

#### Secret Management

- **Never hardcode** secrets in code
- **Use environment variables**
- **Add secrets to .gitignore**
- **Validate all inputs**
- **Use secure storage APIs**

#### Dependency Management

- **Keep dependencies updated**
- **Review security advisories**
- **Use `pip-audit`** to check vulnerabilities
- **Pin dependency versions**
- **Review third-party code**

#### Code Security

- **Follow secure coding practices**
- **Use type hints**
- **Handle errors properly**
- **Sanitize user inputs**
- **Use parameterized queries**

#### Testing

- **Write security tests**
- **Test edge cases**
- **Test encryption/decryption**
- **Test input validation**
- **Perform security reviews**

## Security Auditing

### Code Review

Regular security reviews should cover:

- API key handling
- Encryption implementation
- Input validation
- Error handling
- Network security

### Dependency Scanning

Scan for vulnerabilities:

```bash
pip-audit
```

### Static Analysis

Use static analysis tools:

```bash
# Bandit for security issues
bandit -r .

# Safety for dependency vulnerabilities
safety check
```

### Penetration Testing

Test for:

- SQL injection
- XSS (if web interface added)
- Path traversal
- Command injection
- Buffer overflows

## Known Limitations

### Encryption Password Recovery

Encryption passwords **cannot** be recovered. If lost:
- Encrypted data is inaccessible
- Must delete encrypted files
- Start fresh with new password

### Local Fallback Key

Without a password, a local fallback key is used:
- Less secure than password-based encryption
- Key is stored on the machine
- Consider setting a password for better security

### Cloud Provider Security

When using cloud providers:
- Data is sent to provider servers
- Subject to provider's privacy policy
- Provider may store data temporarily
- Review provider's security practices

## Security Updates

### Keeping Updated

- Update application regularly
- Review changelog for security fixes
- Update dependencies
- Monitor security advisories

### Reporting Security Issues

If you find a security vulnerability:

1. **Do NOT** open a public issue
2. Email: security@example.com
3. Include details and reproduction steps
4. Allow time for fix before disclosure

## Security Checklist

### Before First Use

- [ ] Set encryption password
- [ ] Enable chat encryption (optional)
- [ ] Review privacy settings
- [ ] Understand data storage locations
- [ ] Configure API keys securely

### Regular Maintenance

- [ ] Rotate API keys periodically
- [ ] Update application
- [ ] Update dependencies
- [ ] Review security settings
- [ ] Clear unnecessary chat history

### For Sensitive Use

- [ ] Use local models (Ollama)
- [ ] Enable chat encryption
- [ ] Use strong encryption password
- [ ] Disable cloud providers
- [ ] Clear data after use

## Next Steps

- [Read Configuration guide](Configuration)
- [Read Privacy section in FAQ](FAQ#privacy-and-security)
- [Review SECURITY.md in project root](https://github.com/yourusername/chat-linux-client/blob/main/SECURITY.md)
