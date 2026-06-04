[Model Management](Model-Management)

This guide covers how models are managed, selected, and configured in Chat Linux Client.

Table of Contents
Overview
Model Information
Model Selection
Model Configuration
Custom Models
Model Performance

Overview

Chat Linux Client uses a sophisticated model management system (core/modelmanager.py) to:
Track available models from all providers
Provide model metadata and capabilities
Enable intelligent model selection
Support custom model configurations

Model Properties

Each model has the following properties:
Name: Model identifier (e.g., llama3.2:1b)
Provider: AI provider (e.g., ollama, groq)
Context Window: Maximum input tokens
Max Output: Maximum output tokens
Cost: Cost per 1K tokens (if applicable)
Speed Rating: Relative speed (1-10)
Quality Rating: Relative quality (1-10)
Is Local: Whether model runs locally

Model Information

Built-in Models

The system includes pre-configured models for each provider:

Ollama Models

 Model  Size  Context  Speed  Quality 

 llama3.2:1b  1.3GB  8K  10  6 
 qwen2.5:3b  1.9GB  32K  8  7 
 phi3.5:3.8b  2.2GB  12K  7  8 
 mistral:7b  4.4GB  32K  5  9 

Groq Models

 Model  Context  Speed  Quality  Cost 

 llama-3.1-8b-instant  8K  10  8  Free tier 
 llama-3.1-70b-versatile  8K  7  9  Free tier 
 mixtral-8x7b-32768  32K  6  9  Free tier 

OpenAI Models

 Model  Context  Speed  Quality  Cost 

 gpt-4o  128K  8  10  $5/1M input 
 gpt-4-turbo  128K  7  9  $10/1M input 
 gpt-3.5-turbo  16K  9  7  $0.5/1M input 

HuggingFace Models

 Model  Context  Speed  Quality  Cost 

 meta-llama/Llama-2-7b-chat-hf  4K  6  8  Free tier 
 mistralai/Mistral-7B-Instruct-v0.2  8K  7  9  Free tier 

OpenRouter Models

 Model  Context  Speed  Quality  Cost 

 anthropic/claude-3-opus  200K  5  10  $15/1M input 
 openai/gpt-4-turbo  128K  7  9  $10/1M input 

Model Metadata

Models are represented as data classes:

Model Selection

Automatic Selection

The system can automatically select models based on routing strategy:

OFFLINEFIRST

Prioritizes local models, falls back to cloud:

SPEEDOPTIMAL

Prioritizes fast models:

COSTOPTIMAL

Prioritizes free/cheap models:

QUALITYOPTIMAL

Prioritizes high-quality models:

Manual Selection

Users can manually select models from the dropdown:

Filtering Models

Filter models by criteria:

Model Configuration

Adding Custom Models

Add custom models in core/modelmanager.py:

Model Profiles

Define profiles for specific use cases:

Context Window Management

The system manages context windows to prevent exceeding model limits:

Custom Models

Adding Ollama Models

Pull new models from Ollama:

Then register in modelmanager.py:

Adding Custom Provider Models

For custom providers, implement model listing:

Model Performance

Performance Metrics

Track model performance:

Performance Optimization

For Speed
Use lightweight models (llama3.2:1b)
Reduce max tokens
Use Groq for cloud models
Enable streaming

For Quality
Use capable models (GPT-4, mistral:7b)
Increase temperature slightly
Provide more context
Use larger context windows

For Cost
Use local models (Ollama)
Use free tier cloud models
Limit max tokens
Use cost-optimal routing

Benchmarking Models

Compare model performance:

Model Updates

Updating Model Information

When providers add new models, update modelmanager.py:
Check provider documentation
Add new model to model list
Update model metadata
Test new model
Update documentation

Deprecating Models

Remove or mark deprecated models:

[Troubleshooting](Troubleshooting)

Model Not Showing

If a model doesn't appear in the dropdown:
Verify model is registered in model_manager.py
Check provider is enabled
Ensure Ollama model is pulled (for local models)
Check API key is valid (for cloud models)
Run system checks

Model Performance Poor

If a model performs poorly:
Check system resources
Try a lighter model
Reduce context window
Check network connection (for cloud models)
Update model version

Context Window Exceeded

If you get context window errors:
Reduce input length
Use model with larger context
Enable context truncation
Clear chat history

Best Practices

Model Selection
Simple queries: Use fast, lightweight models
Complex tasks: Use capable, larger models
Privacy-sensitive: Use local models
Cost-sensitive: Use free models
Quality-critical: Use premium models

Context Management
Keep prompts concise
Use relevant context only
Summarize long conversations
Use models with appropriate context windows

Cost Management
Monitor token usage
Set max tokens limits
Use cost-optimal routing
Prefer local models when possible

Next Steps
Read API Providers guide
Read Configuration guide
Read Usage guide