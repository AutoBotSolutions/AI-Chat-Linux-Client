# Troubleshooting

This guide covers common issues and their solutions for Chat Linux Client.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Configuration Issues](#configuration-issues)
- [API Provider Issues](#api-provider-issues)
- [Performance Issues](#performance-issues)
- [UI Issues](#ui-issues)
- [Data Issues](#data-issues)
- [Getting Help](#getting-help)

## Installation Issues

### Python Version Error

**Error**: `Python 3.8 or higher required`

**Solution**: Install a newer Python version:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.9 python3.9-venv

# Fedora
sudo dnf install python39

# Arch Linux
sudo pacman -S python
```

### Dependency Installation Fails

**Error**: `pip install` fails with various errors

**Solution**: Update pip and try again:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### PyQt6 Installation Fails

**Error**: PyQt6 installation fails

**Solution**: Install system dependencies:
```bash
# Ubuntu/Debian
sudo apt install libxcb-xinerama0

# Fedora
sudo dnf install libxcb

# Arch Linux
sudo pacman -S libxcb
```

### Permission Errors

**Error**: `Permission denied` when running scripts

**Solution**: Make scripts executable:
```bash
chmod +x scripts/*.sh
```

## Configuration Issues

### API Key Not Working

**Symptoms**: API key accepted but provider not working

**Solutions**:
1. Verify the key is correct (no extra spaces)
2. Check the key has proper permissions in the provider dashboard
3. Ensure the provider account is active
4. Check network connectivity
5. Try regenerating the API key

### Models Not Showing in Dropdown

**Symptoms**: Model dropdown is empty or missing models

**Solutions**:
1. Verify the provider is enabled in settings
2. Check API key is configured (for cloud providers)
3. Ensure Ollama is running (for local models)
4. Run system checks: `python main.py --check-system`
5. Check application logs for errors

### Configuration Not Saving

**Symptoms**: Settings don't persist after restart

**Solutions**:
1. Check write permissions for `~/.config/chat-linux-client/`
2. Ensure the directory exists: `mkdir -p ~/.config/chat-linux-client`
3. Check disk space
4. Verify no other process is locking the config file

### Encryption Password Issues

**Symptoms**: Cannot access encrypted chats or keys

**Solutions**:
1. Ensure you're using the correct password
2. If password was changed, use the old password to decrypt
3. If password is lost, encrypted data cannot be recovered
4. Consider starting fresh (delete encrypted files)

## API Provider Issues

### OpenAI: 401 Unauthorized

**Error**: `401 Unauthorized` when using OpenAI

**Solutions**:
1. Verify API key is correct
2. Check account has credits
3. Ensure API key has proper permissions
4. Try regenerating the API key

### Groq: Rate Limit Exceeded

**Error**: `Rate limit exceeded` when using Groq

**Solutions**:
1. Wait a few minutes before trying again
2. Upgrade to paid tier if needed
3. Use local models as fallback
4. Implement retry logic in your usage

### HuggingFace: Model Not Found

**Error**: `Model not found` or `Model loading error`

**Solutions**:
1. Verify model name is correct
2. Check if model is available on HuggingFace
3. Some models require approval
4. Try a different model

### OpenRouter: Insufficient Credits

**Error**: `Insufficient credits` when using OpenRouter

**Solutions**:
1. Add credits to your OpenRouter account
2. Check credit balance in dashboard
3. Use cheaper models
4. Switch to free providers

### Ollama: Connection Refused

**Error**: `Connection refused` when using Ollama

**Solutions**:
1. Ensure Ollama is running: `ollama serve`
2. Check Ollama is installed correctly
3. Verify default URL: `http://localhost:11434`
4. Restart Ollama service

## Performance Issues

### Slow Response Times

**Symptoms**: AI responses take a long time

**Solutions**:
1. Use a faster model (lighter local model or Groq)
2. Reduce max tokens in settings
3. Check network connection for cloud models
4. Close other applications to free resources
5. Use offline-first routing

### High Memory Usage

**Symptoms**: Application uses too much RAM

**Solutions**:
1. Use lighter models (e.g., llama3.2:1b)
2. Clear chat history regularly
3. Close unused chat sessions
4. Reduce max tokens setting
5. Restart application periodically

### Application Freezes

**Symptoms**: Application becomes unresponsive

**Solutions**:
1. Wait a moment (may be processing large response)
2. Check if network is responsive (for cloud models)
3. Kill and restart the application
4. Check system logs for errors
5. Ensure sufficient system resources

### Streaming Issues

**Symptoms**: Streaming responses don't appear smoothly

**Solutions**:
1. Check network stability
2. Try non-streaming mode in settings
3. Use a different provider
4. Check if provider supports streaming

## UI Issues

### Window Not Appearing

**Symptoms**: Application starts but no window appears

**Solutions**:
1. Check if window is on another desktop
2. Check system logs for errors
3. Verify PyQt6 is installed correctly
4. Try running from terminal to see errors
5. Check display environment variables

### UI Elements Not Responsive

**Symptoms**: Buttons or inputs don't respond

**Solutions**:
1. Restart the application
2. Check if application is frozen
3. Look for error messages in terminal
4. Verify all dependencies are installed
5. Try running system checks

### Dark Theme Not Working

**Symptoms**: UI doesn't use dark theme

**Solutions**:
1. Ensure dark theme is enabled in settings
2. Check if stylesheet file exists: `styles/dark.qss`
3. Verify PyQt6 Qt6 is installed
4. Try reinstalling dependencies

### Markdown Rendering Issues

**Symptoms**: Markdown not rendering correctly

**Solutions**:
1. Check markdown library is installed
2. Verify markdown renderer is working
3. Try simpler markdown to test
4. Check for markdown syntax errors

## Data Issues

### Chat History Not Saving

**Symptoms**: Chats not saved after closing

**Solutions**:
1. Check write permissions for data directory
2. Ensure `~/.local/share/chat-linux-client/` exists
3. Check disk space
4. Verify database is not corrupted
5. Check application logs for errors

### Cannot Export Chats

**Symptoms**: Export function fails

**Solutions**:
1. Check write permissions for export location
2. Ensure sufficient disk space
3. Try different export format
4. Check if chat has content to export
5. Verify export directory exists

### Database Corruption

**Symptoms**: Application crashes on startup, database errors

**Solutions**:
1. Backup existing database if possible
2. Delete corrupted database: `rm ~/.local/share/chat-linux-client/chat_history.db`
3. Restart application (will create new database)
4. Import backup if available

### API Key Storage Issues

**Symptoms**: Cannot save or load API keys

**Solutions**:
1. Check encryption password is correct
2. Verify key file permissions
3. Try resetting encryption
4. Delete key storage and reconfigure
5. Check application logs for specific errors

## Getting Help

### Run System Checks

```bash
python main.py --check-system
```

This will verify:
- Python version compatibility
- Required dependencies
- Ollama availability
- System resources
- Configuration integrity

### Check Logs

Application logs are stored at:
```
~/.local/share/chat-linux-client/logs/
```

### Enable Debug Mode

Set environment variable:
```bash
DEBUG=true
python main.py
```

### Collect Diagnostic Information

1. Run system checks
2. Check application logs
3. Note error messages
4. Document steps to reproduce
5. Include system information

### Report Issues

When reporting issues, include:
- OS and version
- Python version
- Application version
- Error messages
- Steps to reproduce
- System check output
- Relevant log excerpts

## Common Error Messages

### "No module named 'PyQt6'"

**Solution**: Install PyQt6:
```bash
pip install PyQt6 PyQt6-Qt6
```

### "API key not found"

**Solution**: Configure API key in settings or environment variables

### "Connection timeout"

**Solution**: Check network connection and provider status

### "Model not available"

**Solution**: Verify model is installed or provider is configured

### "Encryption key invalid"

**Solution**: Use correct encryption password or reset encryption

## Next Steps

- [Read Configuration guide](Configuration)
- [Read API Providers guide](API-Providers)
- [Read Development guide](Development)
