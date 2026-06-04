"""
Groq client for ultra-low latency AI inference.
"""

import logging
import aiohttp
import json
from typing import Dict, List, Optional, AsyncGenerator
from .api_client import BaseAPIClient


class GroqClient(BaseAPIClient):
    """Client for Groq AI models."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.groq.com/openai/v1"):
        super().__init__(api_key=api_key, base_url=base_url)
        self.logger = logging.getLogger(__name__)
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def test_connection(self) -> bool:
        """Test if Groq API is accessible."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/models", 
                    headers=self.headers, 
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    self.is_available = response.status == 200
                    if self.is_available:
                        self.logger.info("Groq connection successful")
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Groq API error: {response.status} - {error_text}")
                    return self.is_available
        except Exception as e:
            self.logger.error(f"Groq connection test failed: {e}")
            self.is_available = False
            return False
    
    async def list_models(self) -> List[str]:
        """Get list of available Groq models."""
        if not self.is_available:
            return []
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/models", headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return [model["id"] for model in data.get("data", [])]
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Groq list models error: {response.status} - {error_text}")
        except Exception as e:
            self.logger.error(f"Groq list models failed: {e}")
        return []
    
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        model: str,
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ):
        """Send chat completion request to Groq."""
        if not self.is_available:
            yield "Error: Groq provider not available"
            return
            
        try:
            payload = {
                "model": model,
                "messages": messages,
                "stream": stream,
                "temperature": temperature
            }
            
            if max_tokens:
                payload["max_tokens"] = max_tokens
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions", 
                    headers=self.headers, 
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        if stream:
                            async for line in response.content:
                                if line:
                                    line_str = line.decode('utf-8').strip()
                                    if line_str.startswith('data: '):
                                        line_data = line_str[6:]  # Remove 'data: '
                                        if line_data != '[DONE]':
                                            try:
                                                data = json.loads(line_data)
                                                if "choices" in data and len(data["choices"]) > 0:
                                                    delta = data["choices"][0].get("delta", {})
                                                    if "content" in delta:
                                                        yield delta["content"]
                                            except json.JSONDecodeError:
                                                continue
                        else:
                            data = await response.json()
                            if "choices" in data and len(data["choices"]) > 0:
                                yield data["choices"][0]["message"]["content"]
                            else:
                                yield "I apologize, but I couldn't generate a response."
                    else:
                        error_text = await response.text()
                        try:
                            error_data = json.loads(error_text)
                            error_msg = error_data.get('error', {}).get('message', error_text)
                        except:
                            error_msg = error_text
                        self.logger.error(f"Groq API error: {response.status} - {error_msg}")
                        yield f"Error: Groq API returned {response.status}: {error_msg}"
                        
        except Exception as e:
            self.logger.error(f"Groq chat completion failed: {e}")
            yield f"Error: {str(e)}"
    
    def get_provider_name(self) -> str:
        """Get the provider name."""
        return "Groq"
