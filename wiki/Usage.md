# Usage

This guide covers how to use Chat Linux Client for your daily AI interactions.

## Table of Contents

- [Getting Started](#getting-started)
- [Basic Chat](#basic-chat)
- [Model Selection](#model-selection)
- [Advanced Features](#advanced-features)
- [Chat History](#chat-history)
- [Keyboard Shortcuts](#keyboard-shortcuts)
- [Tips and Best Practices](#tips-and-best-practices)

## Getting Started

### Launching the Application

```bash
# Using the run script
./scripts/run.sh

# Or directly with Python
python main.py
```

### First Run

On first launch:
1. The application will check system requirements
2. Available models will be loaded into the dropdown
3. You'll see the main chat interface

## Basic Chat

### Sending a Message

1. Type your message in the input field at the bottom
2. Press **Enter** or click the **Send** button
3. The AI response will appear in the chat area

### Reading Responses

- Responses are rendered with Markdown formatting
- Code blocks are highlighted
- Streaming responses appear token-by-token in real-time

### Starting a New Chat

Click the **New Chat** button in the toolbar or:
- Press `Ctrl+N` (Linux)
- Select **File > New Chat** from the menu

## Model Selection

### Choosing a Model

1. Click the model dropdown in the toolbar
2. Select your preferred model from the list
3. Models are listed as `provider/model-name`

### Model Types

- **Local Models** (`ollama/*`): Work offline, no API key needed
- **Cloud Models**: Require API keys, often more capable

### Recommended Models by Use Case

**For Speed:**
- `ollama/llama3.2:1b` - Fastest, lightweight
- `groq/llama-3.1-8b-instant` - Ultra-fast cloud

**For Quality:**
- `ollama/mistral:7b` - Best local model
- `openai/gpt-4o` - Best cloud model (requires API key)

**For Cost:**
- `ollama/*` - Free, runs locally
- `huggingface/*` - Many free models

## Advanced Features

### Intelligent Routing

Enable automatic model selection based on your needs:

1. Open Settings
2. Choose a **Routing Strategy**:
   - **OFFLINE_FIRST**: Prefer local models
   - **SPEED_OPTIMAL**: Prefer fast models
   - **COST_OPTIMAL**: Prefer free options
   - **QUALITY_OPTIMAL**: Prefer capable models

### Temperature Control

Adjust response creativity:

1. Open Settings
2. Set **Temperature** (0.0 - 2.0):
   - **0.0-0.3**: Focused, deterministic
   - **0.4-0.7**: Balanced (default)
   - **0.8-1.0**: Creative, varied
   - **1.0+**: Very creative, less predictable

### Max Tokens

Limit response length:

1. Open Settings
2. Set **Max Tokens**:
   - **0**: Unlimited (default)
   - **100-500**: Short responses
   - **1000-2000**: Medium responses
   - **4000+**: Long responses

## Chat History

### Viewing Past Chats

1. Click **History** in the menu
2. Select a chat from the list
3. The conversation will load in the main window

### Exporting Chats

1. Open the chat you want to export
2. Select **File > Export Chat**
3. Choose a location and format (Markdown, JSON, or Plain Text)

### Deleting Chats

1. Open the History panel
2. Right-click on a chat
3. Select **Delete**
4. Confirm the deletion

### Search History

1. Open the History panel
2. Use the search box
3. Type keywords to find specific conversations

## Keyboard Shortcuts

### Chat

- `Enter` - Send message
- `Shift+Enter` - New line in message
- `Ctrl+N` - New chat
- `Ctrl+W` - Close current chat

### Navigation

- `Ctrl+H` - Open history
- `Ctrl+,` - Open settings
- `Ctrl+Q` - Quit application

### Editing

- `Ctrl+C` - Copy selected text
- `Ctrl+V` - Paste text
- `Ctrl+A` - Select all

## Tips and Best Practices

### For Better Responses

- **Be specific**: Clear, detailed prompts get better answers
- **Provide context**: Include relevant background information
- **Use examples**: Show what you want with examples
- **Iterate**: Refine your question based on responses

### For Privacy

- **Use local models** for sensitive information
- **Enable chat encryption** for private conversations
- **Review chat history** before exporting
- **Clear history** periodically if needed

### For Performance

- **Use lightweight models** for simple queries
- **Use capable models** for complex tasks
- **Close unused chats** to free memory
- **Restart application** if it becomes slow

### For Cost Management

- **Use local models** when possible (free)
- **Monitor token usage** with cloud providers
- **Set max tokens** to limit response length
- **Use cost-optimal routing** for automatic savings

## Common Use Cases

### Coding Assistance

```
You: Write a Python function to sort a list of dictionaries by a specific key
AI: [Provides code with explanation]
```

### Writing Help

```
You: Help me write a professional email about project delays
AI: [Drafts email with appropriate tone]
```

### Learning

```
You: Explain quantum computing in simple terms
AI: [Provides accessible explanation]
```

### Brainstorming

```
You: Give me 10 ideas for a mobile app that helps people learn languages
AI: [Lists creative ideas with brief descriptions]
```

## Troubleshooting

### Response is Slow

- Try a faster model (lighter local model or Groq)
- Reduce max tokens in settings
- Check network connection for cloud models
- Close other applications to free resources

### Response is Poor Quality

- Increase temperature for more creativity
- Try a more capable model
- Provide more context in your prompt
- Use examples to guide the AI

### Application Crashes

- Check system logs: `~/.local/share/chat-linux-client/logs/`
- Run system checks: `python main.py --check-system`
- Ensure all dependencies are installed
- Try reinstalling the application

## Next Steps

- [Configure API keys](Configuration)
- [Learn about API Providers](API-Providers)
- [Read Troubleshooting guide](Troubleshooting)
