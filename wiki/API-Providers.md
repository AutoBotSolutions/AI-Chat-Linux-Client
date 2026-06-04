[API Providers](API-Providers)

This guide covers all supported AI providers, their features, and how to configure them.

Table of Contents
Overview
Ollama (Local)
Groq
HuggingFace
OpenRouter
OpenAI
Provider Comparison
Adding Custom Providers

Overview

Chat Linux Client supports multiple AI providers, giving you flexibility in choosing the best model for your needs:

 Provider  Type  Cost  Speed  Quality  Offline 

 Ollama  Local  Free  Variable  Good  Yes 
 Groq  Cloud  Free tier  Very Fast  Good  No 
 HuggingFace  Cloud  Free tier  Medium  Variable  No 
 OpenRouter  Cloud  Pay-per-use  Fast  Excellent  No 
 OpenAI  Cloud  Pay-per-use  Fast  Excellent  No 

Ollama (Local)

Ollama provides local AI models that run entirely on your machine.

Advantages
Free: No API costs
Privacy: Data never leaves your machine
Offline: Works without internet
No Rate Limits: Use as much as you want

Disadvantages
Hardware: Requires capable CPU/GPU
Model Size: Models take disk space (1-5GB each)
Speed: Slower than cloud for large models
Model Selection: Limited to available models

[Installation](Installation)

Available Models

[Configuration](Configuration)

Ollama is automatically detected. Ensure it's running:

Best For
Privacy-sensitive conversations
Offline work
Cost-sensitive users
Development and testing

Groq

Groq provides ultra-low latency inference using their LPU (Language Processing Unit).

Advantages
Speed: Fastest inference available
Free Tier: Generous free usage
Quality: Good model selection
Latency: Sub-100ms response times

Disadvantages
Rate Limits: Free tier has limits
Internet Required: Cloud-based
Privacy: Data sent to Groq servers

Getting an API Key
Visit https://console.groq.com/
Sign up or log in
Navigate to API Keys section
Create a new API key

[Configuration](Configuration)

Add to .env file or settings:

Available Models
llama-3.1-8b-instant - Fast, balanced
llama-3.1-70b-versatile - Capable
mixtral-8x7b-32768 - Large context

Best For
Real-time applications
Speed-critical tasks
Free tier usage
Interactive conversations

HuggingFace

HuggingFace provides access to thousands of open-source models.

Advantages
Variety: Thousands of models available
Free Tier: Many models are free
Open Source: Community-driven models
Customization: Can use custom models

Disadvantages
Variable Quality: Quality varies by model
Speed: Slower than dedicated providers
Complexity: More configuration options
Rate Limits: Free tier has limits

Getting an API Key
Visit https://huggingface.co/settings/tokens
Sign up or log in
Create a new token
Copy the token

[Configuration](Configuration)

Add to .env file or settings:

Popular Models
meta-llama/Llama-2-7b-chat-hf
mistralai/Mistral-7B-Instruct-v0.2
google/gemma-7b

Best For
Experimenting with different models
Using specialized models
Open-source preference
Custom model deployment

OpenRouter

OpenRouter provides access to multiple models from various providers through a single API.

Advantages
Variety: Access to many models
Unified API: Single key for multiple models
Comparison: Easy to compare models
Flexible: Pay-per-use pricing

Disadvantages
Cost: Pay-per-use (no free tier)
Complexity: Many options to choose from
Internet Required: Cloud-based
Privacy: Data sent to OpenRouter

Getting an API Key
Visit https://openrouter.ai/keys
Sign up or log in
Add credits to your account
Create an API key

[Configuration](Configuration)

Add to .env file or settings:

Available Models
anthropic/claude-3-opus
openai/gpt-4-turbo
google/gemini-pro
And many more

Best For
Accessing premium models
Comparing different models
Production use
Flexible model selection

OpenAI

OpenAI provides state-of-the-art GPT models.

Advantages
Quality: Best-in-class models
Reliability: Highly reliable service
Documentation: Excellent documentation
Ecosystem: Large ecosystem of tools

Disadvantages
Cost: Most expensive option
Rate Limits: Strict rate limits
Internet Required: Cloud-based
Privacy: Data sent to OpenAI

Getting an API Key
Visit https://platform.openai.com/account/api-keys
Sign up or log in
Create a new API key
Add credits to your account

[Configuration](Configuration)

Add to .env file or settings:

Available Models
gpt-4o - Latest, most capable
gpt-4-turbo - High quality
gpt-3.5-turbo - Cost-effective

Best For
Highest quality requirements
Professional use
Complex tasks
Production applications

Provider Comparison

Speed Comparison
Groq - Fastest (sub-100ms)
OpenAI - Fast (200-500ms)
OpenRouter - Fast (200-500ms)
HuggingFace - Medium (500-1000ms)
Ollama - Variable (depends on hardware)

Cost Comparison
Ollama - Free (hardware cost only)
Groq - Free tier available
HuggingFace - Free tier available
OpenRouter - Pay-per-use (moderate)
OpenAI - Pay-per-use (expensive)

Quality Comparison
OpenAI - Best overall
OpenRouter - Excellent (depends on model)
Groq - Good
HuggingFace - Variable
Ollama - Good (depends on model)

Adding Custom Providers

Chat Linux Client has an extensible architecture for adding custom providers.

Steps to Add a Provider
Create a new client file in core/ (e.g., customprovider.py)
Inherit from APIClient base class
Implement required methods:
chatcompletion()
chatcompletionstream()
testconnection()
Add provider configuration to core/settings.py
Register in core/providerrouter.py
Add tests in tests/

Example

See existing providers in core/ for reference:
core/groqclient.py
core/huggingfaceclient.py
core/openrouterclient.py
core/openaiclient.py

Next Steps
Configure your API keys
Learn how to use the application
Read troubleshooting guide