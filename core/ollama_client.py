"""
Ollama client for local AI model inference.
"""

import logging
import aiohttp
import json
from typing import Dict, List, Optional, AsyncGenerator
from .api_client import BaseAPIClient


class OllamaClient(BaseAPIClient):
    """Client for Ollama local AI models."""
    
    def __init__(self, base_url: str = "http://localhost:11434", timeout: int = 30, max_retries: int = 3):
        super().__init__(base_url=base_url)
        self.is_available = False
        self.logger = logging.getLogger(__name__)
        # Large local models can require longer first-token times.
        self.request_timeout = max(120, int(timeout or 30))
        self.max_retries = max(1, int(max_retries or 1))
    
    async def test_connection(self) -> bool:
        """Test if Ollama server is running."""
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(f"{self.base_url}/api/tags") as response:
                    self.is_available = response.status == 200
                    if self.is_available:
                        self.logger.info("Ollama connection successful")
                    return self.is_available
        except Exception as e:
            self.logger.error(f"Ollama connection test failed: {e}")
            self.is_available = False
            return False
    
    async def list_models(self) -> List[str]:
        """Get list of available Ollama models."""
        if not self.is_available:
            return []
        
        try:
            timeout = aiohttp.ClientTimeout(total=20)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(f"{self.base_url}/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        return [model["name"] for model in data.get("models", [])]
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Ollama list models error: {response.status} - {error_text}")
        except Exception as e:
            self.logger.error(f"Ollama list models failed: {e}")
        return []
    
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        model: str,
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ):
        """Send chat completion request to Ollama."""
        if stream:
            async for chunk in self._chat_completion_stream(messages, model, temperature, max_tokens):
                yield chunk
        else:
            # For non-streaming, yield the complete response as a single chunk
            response = await self._chat_completion_non_stream(messages, model, temperature, max_tokens)
            yield response
    
    async def _chat_completion_stream(
        self, 
        messages: List[Dict[str, str]], 
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ):
        """Handle streaming chat completion."""
        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": True,
            "keep_alive": "30m",
            "options": {
                "temperature": temperature,
                "num_ctx": 2048,
            }
        }
        
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens
        
        timeout = aiohttp.ClientTimeout(total=self.request_timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(f"{self.base_url}/api/chat", json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Ollama API error: {response.status} - {error_text}")
                
                async for line in response.content:
                    if line:
                        try:
                            data = json.loads(line.decode('utf-8'))
                            if "error" in data:
                                raise Exception(f"Ollama stream error: {data['error']}")
                            if "message" in data and "content" in data["message"]:
                                yield data["message"]["content"]
                            elif "response" in data:
                                # Some models/endpoints emit chunks in "response".
                                yield data["response"]
                        except json.JSONDecodeError:
                            continue
    
    async def _chat_completion_non_stream(
        self, 
        messages: List[Dict[str, str]], 
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ):
        """Handle non-streaming chat completion."""
        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": False,
            "keep_alive": "30m",
            "options": {
                "temperature": temperature,
                "num_ctx": 2048,
            }
        }
        
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens
        
        timeout = aiohttp.ClientTimeout(total=self.request_timeout)
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(f"{self.base_url}/api/chat", json=payload) as response:
                        if response.status != 200:
                            error_text = await response.text()
                            raise Exception(f"Ollama API error: {response.status} - {error_text}")

                        data = await response.json()
                        if "error" in data:
                            raise Exception(f"Ollama API error: {data['error']}")

                        # Standard /api/chat response
                        content = data.get("message", {}).get("content", "")
                        if content and str(content).strip():
                            return str(content)

                        # Some server/model combinations may return a "response" field.
                        alt_content = data.get("response", "")
                        if alt_content and str(alt_content).strip():
                            return str(alt_content)

                        # Fallback to /api/generate for models that do not return chat content.
                        generated = await self._generate_fallback(session, messages, model, temperature, max_tokens)
                        return generated
            except Exception as e:
                last_error = e
                self.logger.warning(
                    "Ollama non-stream attempt %s/%s failed for model %s: %s",
                    attempt,
                    self.max_retries,
                    model,
                    e,
                )

        raise Exception(f"Ollama request failed after {self.max_retries} attempts: {last_error}")

    async def _generate_fallback(
        self,
        session: aiohttp.ClientSession,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: Optional[int],
    ) -> str:
        """Fallback path for models that respond better on /api/generate."""
        prompt = self._messages_to_prompt(messages)
        payload: Dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "keep_alive": "30m",
            "options": {
                "temperature": temperature,
                "num_ctx": 2048,
            },
        }
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens

        async with session.post(f"{self.base_url}/api/generate", json=payload) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Ollama generate fallback error: {response.status} - {error_text}")

            data = await response.json()
            if "error" in data:
                raise Exception(f"Ollama generate fallback error: {data['error']}")
            return str(data.get("response", ""))

    @staticmethod
    def _messages_to_prompt(messages: List[Dict[str, str]]) -> str:
        """Convert chat-style messages into a simple prompt for /api/generate."""
        lines = []
        for message in messages:
            role = (message.get("role") or "user").strip().lower()
            content = (message.get("content") or "").strip()
            if not content:
                continue
            if role == "system":
                lines.append(f"System: {content}")
            elif role == "assistant":
                lines.append(f"Assistant: {content}")
            else:
                lines.append(f"User: {content}")
        lines.append("Assistant:")
        return "\n".join(lines)
    
    def get_provider_name(self) -> str:
        """Get the provider name."""
        return "Ollama"
    
    async def warm_model(self, model: str) -> None:
        """Load a model into VRAM without running inference.

        Ollama treats a /api/generate request with no prompt and
        num_predict=0 as a pure model-load call, returning quickly once
        the weights are resident.  This eliminates the cold-start penalty
        on the first real request.
        """
        try:
            payload = {
                "model": model,
                "prompt": "",
                "stream": False,
                "keep_alive": "30m",
                "options": {"num_predict": 0},
            }
            timeout = aiohttp.ClientTimeout(total=60)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{self.base_url}/api/generate", json=payload
                ) as response:
                    if response.status == 200:
                        self.logger.info("Model warm-up complete: %s", model)
                    else:
                        body = await response.text()
                        self.logger.warning(
                            "Model warm-up got HTTP %s for %s: %s",
                            response.status, model, body[:200],
                        )
        except Exception as e:
            self.logger.warning("Model warm-up failed for %s: %s", model, e)

    async def pull_model(self, model: str) -> bool:
        """Pull a model from Ollama registry."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/api/pull", json={"name": model}) as response:
                    return response.status == 200
        except Exception:
            return False
