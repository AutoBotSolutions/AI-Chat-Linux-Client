"""
OpenAI API client for GPT models.
"""

import logging
import aiohttp
import json
from typing import Dict, List, Optional, AsyncGenerator
from .api_client import BaseAPIClient


class OpenAIClient(BaseAPIClient):
    """OpenAI API client for GPT models."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1"):
        super().__init__()
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.logger = logging.getLogger(__name__)
        self.is_available = False
        self.models_cache = []
    
    async def test_connection(self) -> bool:
        """Test if OpenAI API is accessible."""
        if not self.api_key or len(self.api_key) < 20:
            self.logger.warning("Invalid OpenAI API key format")
            self.is_available = False
            return False
            
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/models",
                    headers=headers,
                    timeout=10
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.models_cache = [model["id"] for model in data.get("data", [])]
                        self.is_available = True
                        self.logger.info(f"OpenAI connection successful. Found {len(self.models_cache)} models")
                        return True
                    else:
                        error_text = await response.text()
                        self.logger.error(f"OpenAI API error: {response.status} - {error_text}")
                        self.is_available = False
                        return False
                        
        except Exception as e:
            self.logger.error(f"OpenAI connection test failed: {e}")
            self.is_available = False
            return False
    
    async def list_models(self) -> List[str]:
        """List available OpenAI models."""
        if not self.is_available:
            await self.test_connection()
        
        return self.models_cache if self.models_cache else [
            "gpt-5",
            "gpt-5-mini",
            "gpt-5-nano",
            "gpt-4.1",
            "gpt-4.1-mini",
            "gpt-4.1-nano",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k",
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4o-realtime-preview",
            "gpt-4o-audio-preview"
        ]
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-3.5-turbo",
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ):
        """Send chat completion request to OpenAI."""
        if not self.is_available:
            yield "Error: OpenAI provider not available"
            return
            
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "stream": stream
            }
            
            if max_tokens:
                payload["max_tokens"] = max_tokens
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=60
                ) as response:
                    if response.status == 200:
                        if stream:
                            # Handle streaming response
                            async for line in response.content:
                                line_str = line.decode('utf-8').strip()
                                if line_str.startswith('data: '):
                                    line_data = line_str[6:]  # Remove 'data: '
                                    if line_data != '[DONE]':
                                        try:
                                            json_data = json.loads(line_data)
                                            if 'choices' in json_data and len(json_data['choices']) > 0:
                                                delta = json_data['choices'][0].get('delta', {})
                                                if 'content' in delta:
                                                    yield delta['content']
                                        except json.JSONDecodeError:
                                            continue
                        else:
                            # Non-streaming response
                            data = await response.json()
                            if 'choices' in data and len(data['choices']) > 0:
                                yield data['choices'][0]['message']['content']
                            else:
                                yield "I apologize, but I couldn't generate a response."
                    else:
                        error_text = await response.text()
                        try:
                            error_data = json.loads(error_text)
                            error_msg = error_data.get('error', {}).get('message', error_text)
                        except:
                            error_msg = error_text
                        self.logger.error(f"OpenAI API error: {response.status} - {error_msg}")
                        yield f"Error: OpenAI API returned {response.status}: {error_msg}"
                        
        except Exception as e:
            self.logger.error(f"OpenAI chat completion failed: {e}")
            yield f"Error: {str(e)}"
    
    def get_provider_name(self) -> str:
        """Get provider name."""
        return "OpenAI"
