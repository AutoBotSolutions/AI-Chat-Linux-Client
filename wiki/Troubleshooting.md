[Troubleshooting](Troubleshooting)

This guide covers common issues and their solutions for Chat Linux Client.

Table of Contents
Installation Issues
Configuration Issues
API Provider Issues
Performance Issues
UI Issues
Data Issues
Getting Help

Installation Issues

Python Version Error

Error: Python 3.8 or higher required

Solution: Install a newer Python version:

Dependency Installation Fails

Error: pip install fails with various errors

Solution: Update pip and try again:

PyQt6 Installation Fails

Error: PyQt6 installation fails

Solution: Install system dependencies:

Permission Errors

Error: Permission denied when running scripts

Solution: Make scripts executable:

Configuration Issues

API Key Not Working

Symptoms: API key accepted but provider not working

Solutions:
Verify the key is correct (no extra spaces)
Check the key has proper permissions in the provider dashboard
Ensure the provider account is active
Check network connectivity
Try regenerating the API key

Models Not Showing in Dropdown

Symptoms: Model dropdown is empty or missing models

Solutions:
Verify the provider is enabled in settings
Check API key is configured (for cloud providers)
Ensure Ollama is running (for local models)
Run system checks: python main.py --check-system
Check application logs for errors

Configuration Not Saving

Symptoms: Settings don't persist after restart

Solutions:
Check write permissions for ~/.config/chat-linux-client/
Ensure the directory exists: mkdir -p ~/.config/chat-linux-client
Check disk space
Verify no other process is locking the config file

Encryption Password Issues

Symptoms: Cannot access encrypted chats or keys

Solutions:
Ensure you're using the correct password
If password was changed, use the old password to decrypt
If password is lost, encrypted data cannot be recovered
Consider starting fresh (delete encrypted files)

API Provider Issues

OpenAI: 401 Unauthorized

Error: 401 Unauthorized when using OpenAI

Solutions:
Verify API key is correct
Check account has credits
Ensure API key has proper permissions
Try regenerating the API key

Groq: Rate Limit Exceeded

Error: Rate limit exceeded when using Groq

Solutions:
Wait a few minutes before trying again
Upgrade to paid tier if needed
Use local models as fallback
Implement retry logic in your usage

HuggingFace: Model Not Found

Error: Model not found or Model loading error

Solutions:
Verify model name is correct
Check if model is available on HuggingFace
Some models require approval
Try a different model

OpenRouter: Insufficient Credits

Error: Insufficient credits when using OpenRouter

Solutions:
Add credits to your OpenRouter account
Check credit balance in dashboard
Use cheaper models
Switch to free providers

Ollama: Connection Refused

Error: Connection refused when using Ollama

Solutions:
Ensure Ollama is running: ollama serve
Check Ollama is installed correctly
Verify default URL: http://localhost:11434
Restart Ollama service

Performance Issues

Slow Response Times

Symptoms: AI responses take a long time

Solutions:
Use a faster model (lighter local model or Groq)
Reduce max tokens in settings
Check network connection for cloud models
Close other applications to free resources
Use offline-first routing

High Memory Usage

Symptoms: Application uses too much RAM

Solutions:
Use lighter models (e.g., llama3.2:1b)
Clear chat history regularly
Close unused chat sessions
Reduce max tokens setting
Restart application periodically

Application Freezes

Symptoms: Application becomes unresponsive

Solutions:
Wait a moment (may be processing large response)
Check if network is responsive (for cloud models)
Kill and restart the application
Check system logs for errors
Ensure sufficient system resources

Streaming Issues

Symptoms: Streaming responses don't appear smoothly

Solutions:
Check network stability
Try non-streaming mode in settings
Use a different provider
Check if provider supports streaming

UI Issues

Window Not Appearing

Symptoms: Application starts but no window appears

Solutions:
Check if window is on another desktop
Check system logs for errors
Verify PyQt6 is installed correctly
Try running from terminal to see errors
Check display environment variables

UI Elements Not Responsive

Symptoms: Buttons or inputs don't respond

Solutions:
Restart the application
Check if application is frozen
Look for error messages in terminal
Verify all dependencies are installed
Try running system checks

Dark Theme Not Working

Symptoms: UI doesn't use dark theme

Solutions:
Ensure dark theme is enabled in settings
Check if stylesheet file exists: styles/dark.qss
Verify PyQt6 Qt6 is installed
Try reinstalling dependencies

Markdown Rendering Issues

Symptoms: Markdown not rendering correctly

Solutions:
Check markdown library is installed
Verify markdown renderer is working
Try simpler markdown to test
Check for markdown syntax errors

Data Issues

Chat History Not Saving

Symptoms: Chats not saved after closing

Solutions:
Check write permissions for data directory
Ensure ~/.local/share/chat-linux-client/ exists
Check disk space
Verify database is not corrupted
Check application logs for errors

Cannot Export Chats

Symptoms: Export function fails

Solutions:
Check write permissions for export location
Ensure sufficient disk space
Try different export format
Check if chat has content to export
Verify export directory exists

Database Corruption

Symptoms: Application crashes on startup, database errors

Solutions:
Backup existing database if possible
Delete corrupted database: rm ~/.local/share/chat-linux-client/chat_history.db
Restart application (will create new database)
Import backup if available

API Key Storage Issues

Symptoms: Cannot save or load API keys

Solutions:
Check encryption password is correct
Verify key file permissions
Try resetting encryption
Delete key storage and reconfigure
Check application logs for specific errors

Getting Help

Run System Checks

This will verify:
Python version compatibility
Required dependencies
Ollama availability
System resources
Configuration integrity

Check Logs

Application logs are stored at:

Enable Debug Mode

Set environment variable:

Collect Diagnostic Information
Run system checks
Check application logs
Note error messages
Document steps to reproduce
Include system information

Report Issues

When reporting issues, include:
OS and version
Python version
Application version
Error messages
Steps to reproduce
System check output
Relevant log excerpts

Common Error Messages

"No module named 'PyQt6'"

Solution: Install PyQt6:

"API key not found"

Solution: Configure API key in settings or environment variables

"Connection timeout"

Solution: Check network connection and provider status

"Model not available"

Solution: Verify model is installed or provider is configured

"Encryption key invalid"

Solution: Use correct encryption password or reset encryption

Next Steps
Read Configuration guide
Read API Providers guide
Read Development guide