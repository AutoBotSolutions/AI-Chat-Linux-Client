# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| Current main branch | ✅ Yes |
| Previous releases | ❌ No |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly.

### How to Report

**Do NOT** open a public issue for security vulnerabilities.

Instead, please send an email to: [security@example.com](mailto:security@example.com)

Please include:

- **Description**: A clear description of the vulnerability
- **Impact**: Potential impact of the vulnerability
- **Steps to reproduce**: Steps to reproduce the issue (if applicable)
- **Proof of concept**: Any proof of concept or exploit code (if available)

### What to Expect

- You will receive an acknowledgment of your report within 48 hours
- We will investigate the vulnerability and assess the impact
- We will work on a fix and coordinate disclosure with you
- We will notify you when a fix is released
- We will credit you in the release notes (unless you wish to remain anonymous)

### Disclosure Timeline

We aim to:

- Acknowledge vulnerabilities within 48 hours
- Provide initial assessment within 7 days
- Release a fix within 30 days for critical vulnerabilities
- Coordinate public disclosure based on severity and fix availability

## Security Best Practices

### For Users

1. **API Keys**: 
   - Never share your API keys
   - Use environment variables or the secure key storage
   - Rotate keys regularly
   - Revoke unused keys

2. **Encryption**:
   - Enable chat encryption for sensitive conversations
   - Use strong passwords for encryption
   - Keep your encryption password secure

3. **Updates**:
   - Keep the application updated to the latest version
   - Review changelog for security fixes

4. **Local Models**:
   - Only download models from trusted sources (Ollama)
   - Keep local models updated

### For Developers

1. **Secrets Management**:
   - Never hardcode API keys or secrets in code
   - Use environment variables for sensitive configuration
   - Ensure `.env` is in `.gitignore`
   - Validate all user inputs

2. **Dependencies**:
   - Keep dependencies updated
   - Review security advisories for dependencies
   - Use `pip-audit` or similar tools to check for vulnerabilities

3. **Code Review**:
   - Have security-focused code reviews
   - Use static analysis tools
   - Test with security-focused test cases

## Known Security Considerations

### API Key Storage

- API keys are encrypted and stored locally
- Keys are encrypted using Fernet symmetric encryption
- Encryption password can be set via `CHAT_CLIENT_PASSWORD` environment variable
- Without a password, a local fallback key is used (less secure)

### Chat History

- Chat history is stored locally in SQLite database
- Optional encryption is available for chat history
- No data is sent to external servers except AI API requests

### Network Traffic

- All API requests use HTTPS
- No telemetry or analytics are collected
- Only necessary data is sent to AI providers

### Local Model Security

- Local models run via Ollama on localhost
- Ollama manages model isolation and security
- Ensure Ollama is kept updated

## Security Features

- **Encrypted API Key Storage**: Keys are encrypted at rest
- **Optional Chat Encryption**: Chat history can be encrypted
- **No Telemetry**: No data collection or analytics
- **HTTPS Only**: All API communications use HTTPS
- **Input Validation**: User inputs are validated before processing
- **Local-First**: Primary functionality works offline with local models

## Security Audits

This project has not undergone a formal security audit. We welcome security researchers to review the code and report vulnerabilities responsibly.

## Contact

For security-related questions not involving vulnerability reports, please open an issue with the "security" label.
