[Usage](Usage)

This guide covers how to use Chat Linux Client for your daily AI interactions.

Table of Contents
Getting Started
Basic Chat
Model Selection
[Enhanced Features](Enhanced-Features)
[Search Functionality](Search-Functionality)
Health Monitoring
Performance Tracking
Chat History
[Keyboard Shortcuts](Keyboard-Shortcuts)
Tips and Best Practices

Getting Started

Launching the Application

First Run

On first launch:
The application will check system requirements and validate all components
Available models will be loaded into the dropdown (70 total models available)
You'll see the main chat interface with enhanced features
Health monitoring will start automatically
Model warmup may begin for optimal performance

Basic Chat

Sending a Message
Type your message in the input field at the bottom
Press Enter or click the Send button
The AI response will appear in the chat area

Reading Responses
Responses are rendered with Markdown formatting
Code blocks are highlighted with syntax highlighting
Streaming responses appear token-by-token in real-time
Response time and token generation metrics displayed
Model information shown during generation

Starting a New Chat

Click the New Chat button in the toolbar or:
Press Ctrl+N (Linux)
Select File > New Chat from the menu

Model Selection

Choosing a Model
Click the model dropdown in the toolbar
Select your preferred model from the list
Models are listed as provider/model-name

Model Types
Local Models (ollama/): Work offline, no API key needed
Cloud Models: Require API keys, often more capable

Recommended Models by Use Case

For Speed:
ollama/llama3.2:1b - Fastest, lightweight
groq/llama-3.1-8b-instant - Ultra-fast cloud

For Quality:
ollama/mistral:7b - Best local model
openai/gpt-4o - Best cloud model (requires API key)

For Cost:
ollama/ - Free, runs locally
huggingface/ - Many free models

[Enhanced Features](Enhanced-Features)

[Search Functionality](Search-Functionality)

The advanced search system allows you to find information quickly:

Basic Search
Press Ctrl+F to open search toolbar
Type your search query
Results highlight in real-time
Navigate with Ctrl+G (next) and Ctrl+Shift+G (previous)

Advanced Search Options
Case Sensitivity: Toggle exact case matching
Whole Words: Match complete words only
Regular Expressions: Use regex patterns
Search Scope: Current chat or all history

Health Monitoring

Real-time system health monitoring:

Health Dashboard
Press F12 to open health dashboard
View provider status with color indicators
Monitor system resources and performance
Access remediation tools

Health Indicators
Green: Provider healthy and available
Yellow: Provider slow or degraded
Red: Provider unavailable or error

Performance Tracking

Monitor application performance:

Metrics Displayed
Response time (time to first token)
Token generation rate (tokens/second)
Memory usage by component
CPU utilization during generation
Network latency for cloud providers

Performance Optimization
Use lightweight models for speed
Clear chat history regularly
Monitor system resources
Use performance dashboard for insights

Model Information Display

Detailed model information available:

Model Details
Context window size
Model type and architecture
Provider information
Performance metrics
Cost information (cloud models)

Access Model Info
Click model name in dropdown
Press Ctrl+M to toggle model info panel
View real-time performance data

System Remediation

One-click fixes for common issues:

Available Fixes
Ollama Service: Start/stop Ollama automatically
Permission Fixes: Fix file permission issues
Dependencies: Install missing dependencies
Configuration Repair: Fix corrupted settings
Cache Cleanup: Clear temporary files

Access Remediation
F12 → Remediation tab
Tools → System Remediation menu
Automatic issue detection and fixing

Advanced Features

Intelligent Routing

Enable automatic model selection based on your needs:
Open Settings
Choose a Routing Strategy:
OFFLINEFIRST: Prefer local models
SPEEDOPTIMAL: Prefer fast models
COSTOPTIMAL: Prefer free options
QUALITYOPTIMAL: Prefer capable models

Temperature Control

Adjust response creativity:
Open Settings
Set Temperature (0.0 - 2.0):
0.0-0.3: Focused, deterministic
0.4-0.7: Balanced (default)
0.8-1.0: Creative, varied
1.0+: Very creative, less predictable

Max Tokens

Limit response length:
Open Settings
Set Max Tokens:
0: Unlimited (default)
100-500: Short responses
1000-2000: Medium responses
4000+: Long responses

Chat History

Viewing Past Chats
Click History in the menu
Select a chat from the list
The conversation will load in the main window

Exporting Chats
Open the chat you want to export
Select File > Export Chat
Choose a location and format (Markdown, JSON, or Plain Text)

Deleting Chats
Open the History panel
Right-click on a chat
Select Delete
Confirm the deletion

Search History
Open the History panel
Use the search box
Type keywords to find specific conversations

[Keyboard Shortcuts](Keyboard-Shortcuts)

Chat Management
Enter - Send message
Shift+Enter - New line in message
Ctrl+N - New chat
Ctrl+L - Clear chat history
Ctrl+S - Save chat
Ctrl+E - Export chat

[Search Functionality](Search-Functionality)
Ctrl+F - Toggle search
Ctrl+G - Find next result
Ctrl+Shift+G - Find previous result
Escape - Close search

UI Controls
Ctrl+T - Toggle timestamps
Ctrl+M - Toggle model info
Ctrl+H - Toggle health panel
F11 - Toggle fullscreen

Settings and System
Ctrl+P - Open settings
Ctrl+K - Open settings
Ctrl+U - Open settings
Ctrl+, - Open settings
F12 - Open health dashboard
Ctrl+R - Refresh providers
Ctrl+Shift+R - Restart application
Ctrl+Q - Quit application

Navigation
Ctrl+H - Open history
Tab - Next input field
Shift+Tab - Previous input field

Editing
Ctrl+C - Copy selected text
Ctrl+V - Paste text
Ctrl+A - Select all

Tips and Best Practices

For Better Responses
Be specific: Clear, detailed prompts get better answers
Provide context: Include relevant background information
Use examples: Show what you want with examples
Iterate: Refine your question based on responses

For Privacy
Use local models for sensitive information
Enable chat encryption for private conversations
Review chat history before exporting
Clear history periodically if needed

For Performance
Use lightweight models for simple queries
Use capable models for complex tasks
Close unused chats to free memory
Restart application if it becomes slow

For Cost Management
Use local models when possible (free)
Monitor token usage with cloud providers
Set max tokens to limit response length
Use cost-optimal routing for automatic savings

Common Use Cases

Coding Assistance

Writing Help

Learning

Brainstorming

[Troubleshooting](Troubleshooting)

Response is Slow
Try a faster model (lighter local model or Groq)
Reduce max tokens in settings
Check network connection for cloud models
Close other applications to free resources

Response is Poor Quality
Increase temperature for more creativity
Try a more capable model
Provide more context in your prompt
Use examples to guide the AI

Application Crashes
Check system logs: ~/.local/share/chat-linux-client/logs/
Run system checks: python main.py --check-system
Ensure all dependencies are installed
Try reinstalling the application

Next Steps
Configure API keys
Learn about API Providers
Read Troubleshooting guide