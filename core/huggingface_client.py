"""
HuggingFace client for open-source model access.
"""

import logging
import aiohttp
import json
from typing import Dict, List, Optional, AsyncGenerator
from .api_client import BaseAPIClient


class HuggingFaceClient(BaseAPIClient):
    """Client for HuggingFace models."""
    
    def __init__(self, api_key: str, base_url: str = "https://api-inference.huggingface.co"):
        super().__init__(api_key=api_key, base_url=base_url)
        self.logger = logging.getLogger(__name__)
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def test_connection(self) -> bool:
        """Test if HuggingFace API is accessible."""
        if not self.api_key or len(self.api_key) < 10:
            self.logger.warning("Invalid HuggingFace API key format")
            self.is_available = False
            return False
            
        try:
            # Test with a simple model endpoint
            test_model = "microsoft/DialoGPT-medium"
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/models/{test_model}", 
                    headers=self.headers, 
                    timeout=10
                ) as response:
                    self.is_available = response.status == 200
                    if self.is_available:
                        self.logger.info("HuggingFace connection successful")
                    else:
                        error_text = await response.text()
                        self.logger.error(f"HuggingFace API error: {response.status} - {error_text}")
                    return self.is_available
        except Exception as e:
            self.logger.error(f"HuggingFace connection test failed: {e}")
            self.is_available = False
            return False
    
    async def list_models(self) -> List[str]:
        """Get list of available HuggingFace models."""
        if not self.is_available:
            return []
        
        # Curated set of popular, chat-capable instruction models.
        return [
            "meta-llama/Llama-3.1-8B-Instruct",
            "meta-llama/Llama-3.1-70B-Instruct",
            "Qwen/Qwen2.5-7B-Instruct",
            "Qwen/Qwen2.5-14B-Instruct",
            "Qwen/Qwen2.5-32B-Instruct",
            "Qwen/Qwen2.5-Coder-32B-Instruct",
            "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "mistralai/Mistral-Nemo-Instruct-2407",
            "mistralai/Mistral-7B-Instruct-v0.2",
            "google/gemma-2-9b-it",
            "google/gemma-2-27b-it",
            "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
            "deepseek-ai/DeepSeek-R1-Distill-Llama-70B",
            "microsoft/DialoGPT-medium",
            "microsoft/DialoGPT-large",
            "facebook/blenderbot-400M-distill",
            "google/flan-t5-large",
            "tiiuae/falcon-7b-instruct"
        ]
    
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        model: str,
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ):
        """Send chat completion request to HuggingFace."""
        if not self.is_available:
            yield "Error: HuggingFace provider not available"
            return
            
        try:
            # Convert messages to a single prompt
            prompt = self._messages_to_prompt(messages)
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "temperature": temperature,
                    "max_new_tokens": max_tokens or 500,
                    "return_full_text": False,
                    "do_sample": True
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/models/{model}", 
                    headers=self.headers, 
                    json=payload,
                    timeout=60
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if isinstance(data, list) and len(data) > 0:
                            text = data[0].get("generated_text", "")
                            # Remove the input prompt from the response
                            if text.startswith(prompt):
                                text = text[len(prompt):].strip()
                            
                            if stream:
                                # Simulate streaming by yielding chunks
                                for i in range(0, len(text), 10):
                                    yield text[i:i+10]
                            else:
                                yield text if text else "I apologize, but I couldn't generate a response."
                        else:
                            yield "I apologize, but I couldn't generate a response."
                    else:
                        error_text = await response.text()
                        try:
                            error_data = json.loads(error_text)
                            error_msg = error_data.get('error', error_text)
                        except:
                            error_msg = error_text
                        self.logger.error(f"HuggingFace API error: {response.status} - {error_msg}")
                        yield f"Error: HuggingFace API returned {response.status}: {error_msg}"
                        
        except Exception as e:
            self.logger.error(f"HuggingFace chat completion failed: {e}")
            yield f"Error: {str(e)}"
    
    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert message list to a single prompt string."""
        prompt = ""
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            if role == "system":
                prompt += f"System: {content}\n"
            elif role == "user":
                prompt += f"Human: {content}\n"
            elif role == "assistant":
                prompt += f"Assistant: {content}\n"
        prompt += "Assistant: "
        return prompt
    
    def get_provider_name(self) -> str:
        """Get the provider name."""
        return "HuggingFace"
