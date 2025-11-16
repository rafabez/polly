"""
API client for Pollinations.ai
"""

import requests
import json
from typing import Optional, List, Dict, Generator
from urllib.parse import quote
from .config import get_config, API_BASE_URL, API_TIMEOUT, NEW_API_BASE_URL, AVAILABLE_MODELS, BACKEND_URL


class PollinationsAPI:
    """Client for Pollinations.ai Text Generation API"""

    def __init__(self, use_direct_api: bool = False):
        self.config = get_config()
        self.use_direct_api = use_direct_api
        self.use_backend = self.config.get("use_backend", True) and not use_direct_api
        self.backend_url = BACKEND_URL  # Hardcoded backend URL
        self.base_url = API_BASE_URL  # Old API (fallback)
        self.new_api_url = NEW_API_BASE_URL  # New direct API
        self.timeout = API_TIMEOUT
        self.referrer = self.config.get("referrer", "interzonesec.com")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers with referrer"""
        return {
            "Referer": self.referrer,
            "User-Agent": "Polly/0.1.0",
            "Content-Type": "application/json"
        }
    
    def simple_query(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        stream: bool = False
    ) -> str:
        """
        Simple GET request for quick queries
        
        Args:
            prompt: The user's question/prompt
            model: AI model to use (default from config)
            temperature: Creativity level 0.0-3.0 (default from config)
            stream: Enable streaming response
        
        Returns:
            The AI's response as a string
        """
        model = model or self.config.get("default_model")
        temperature = temperature if temperature is not None else self.config.get("temperature")
        
        # Build URL with encoded prompt
        url = f"{self.base_url}/{quote(prompt)}"
        
        # Build query parameters
        params = {
            "model": model,
            "referer": self.referrer
        }
        
        if temperature is not None:
            params["temperature"] = temperature
        
        if stream:
            params["stream"] = "true"
        
        try:
            response = requests.get(
                url,
                params=params,
                headers=self._get_headers(),
                timeout=self.timeout,
                stream=stream
            )
            response.raise_for_status()
            
            if stream:
                return response.iter_content(chunk_size=1024, decode_unicode=True)
            else:
                return response.text
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        seed: Optional[int] = None,
        stream: bool = False
    ) -> str:
        """
        OpenAI-compatible chat completion for conversations

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: AI model to use
            temperature: Creativity level 0.0-3.0
            seed: Random seed for reproducible/varied responses
            stream: Enable streaming response

        Returns:
            The AI's response as a string
        """
        model = model or self.config.get("default_model")
        temperature = temperature if temperature is not None else self.config.get("temperature")

        # Auto-adjust temperature for models that don't support it
        if model == "openai":
            temperature = 1.0  # openai model only supports temperature=1.0

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream
        }

        # Add seed if provided (for varied responses in motivational mode)
        if seed is not None:
            payload["seed"] = seed

        # Determine which API to use
        if self.use_backend:
            # Use proxy backend (default)
            api_url = f"{self.backend_url}/api/chat/completions"
        else:
            # Use old direct API as fallback
            api_url = f"{self.base_url}/openai"

        try:
            response = requests.post(
                api_url,
                json=payload,
                headers=self._get_headers(),
                timeout=self.timeout,
                stream=stream
            )
            response.raise_for_status()

            if stream:
                return self._handle_streaming_response(response)
            else:
                data = response.json()
                return data["choices"][0]["message"]["content"]

        except requests.exceptions.Timeout:
            raise Exception(
                f"⏱️  Timeout: Model '{model}' took too long to respond.\n"
                f"💡 Try: polly --list-models to see other available models"
            )
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else "unknown"

            if status_code == 503 or status_code == 502:
                raise Exception(
                    f"🔴 Service temporarily unavailable.\n"
                    f"💡 Try another model: polly --list-models"
                )
            elif status_code == 429:
                raise Exception(
                    f"⚠️  Rate limit exceeded.\n"
                    f"💡 Wait a few seconds and try again."
                )
            elif status_code == 500:
                raise Exception(
                    f"❌ Server error (model: {model}).\n"
                    f"💡 Try another model: polly --list-models\n"
                    f"   Suggestion: polly --model mistral <your question>"
                )
            else:
                raise Exception(
                    f"❌ HTTP {status_code} error.\n"
                    f"💡 Try another model: polly --list-models"
                )
        except requests.exceptions.ConnectionError:
            raise Exception(
                f"🌐 Connection error.\n"
                f"💡 Check your internet connection.\n"
                f"   Or try direct API: polly --direct-api <your question>"
            )
        except requests.exceptions.RequestException as e:
            # Don't show URLs in error messages
            error_msg = str(e).split("url:")[0].split("URL:")[0].strip()
            raise Exception(
                f"❌ Request error: {error_msg}\n"
                f"💡 Try another model: polly --list-models"
            )
        except (KeyError, json.JSONDecodeError) as e:
            raise Exception(
                f"⚠️  Invalid API response.\n"
                f"💡 Model '{model}' may be temporarily unavailable.\n"
                f"   Try: polly --model mistral <your question>"
            )
    
    def _handle_streaming_response(self, response) -> Generator[str, None, None]:
        """Handle streaming response from API"""
        for line in response.iter_lines(decode_unicode=True):
            if line and line.startswith("data: "):
                data_str = line[6:]  # Remove "data: " prefix
                if data_str == "[DONE]":
                    break
                try:
                    data = json.loads(data_str)
                    if "choices" in data and len(data["choices"]) > 0:
                        delta = data["choices"][0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
                except json.JSONDecodeError:
                    continue
    
    def get_available_models(self, use_cache: bool = True) -> List[Dict[str, any]]:
        """
        Get list of available models from API (dynamically fetched)

        Args:
            use_cache: If True and fetch fails, return hardcoded models

        Returns:
            List of model information dicts
        """
        try:
            # Try to fetch from backend first, then new API
            if self.use_backend:
                api_url = f"{self.backend_url}/api/models"
            else:
                api_url = f"{self.new_api_url}/models"

            response = requests.get(
                api_url,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            response.raise_for_status()
            models = response.json()

            # Filter out excluded models (already done by backend, but just in case)
            excluded = {"midijourney", "openai-audio"}
            filtered_models = [
                model for model in models
                if model.get("name") not in excluded
            ]

            return filtered_models

        except requests.exceptions.RequestException as e:
            if use_cache:
                # Fallback to hardcoded models if fetch fails
                return [
                    {"name": name, "description": desc}
                    for name, desc in AVAILABLE_MODELS.items()
                ]
            else:
                raise Exception(f"Failed to fetch models: {str(e)}")
