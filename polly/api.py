"""
API client for Pollinations.ai
"""

import requests
import json
from typing import Optional, List, Dict, Generator
from urllib.parse import quote
from .config import get_config, API_BASE_URL, API_TIMEOUT, NEW_API_BASE_URL, AVAILABLE_MODELS, BACKEND_URL, GEN_API_BASE_URL, fetch_text_models
from .i18n import get_text


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
                timeout=None if stream else self.timeout,
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
                timeout=None if stream else self.timeout,
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
                f"⏱️  {get_text('error.timeout', model=model)}\n"
                f"💡 {get_text('error.timeout_tip')}"
            )
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else "unknown"

            # Try to extract a specific message from the backend's JSON error body
            backend_msg = ""
            if e.response is not None:
                try:
                    body = e.response.json()
                    backend_msg = body.get("error", {}).get("message", "")
                except Exception:
                    pass

            if backend_msg:
                raise Exception(f"❌ {backend_msg}")
            elif status_code == 429:
                raise Exception(
                    f"⚠️  {get_text('error.rate_limit')}\n"
                    f"💡 {get_text('error.rate_limit_tip')}"
                )
            elif status_code == 500:
                raise Exception(
                    f"❌ {get_text('error.server_error', model=model)}\n"
                    f"💡 {get_text('error.server_tip')}\n"
                    f"   {get_text('error.server_suggestion')}"
                )
            elif status_code in (502, 503):
                raise Exception(
                    f"🔴 {get_text('error.service_down')}\n"
                    f"💡 {get_text('error.service_tip')}"
                )
            else:
                raise Exception(
                    f"❌ {get_text('error.http_error', status_code=status_code)}\n"
                    f"💡 {get_text('error.http_tip')}"
                )
        except requests.exceptions.ConnectionError:
            raise Exception(
                f"🌐 {get_text('error.connection')}\n"
                f"💡 {get_text('error.connection_tip')}\n"
                f"   {get_text('error.connection_direct')}"
            )
        except requests.exceptions.RequestException as e:
            # Don't show URLs in error messages
            error_msg = str(e).split("url:")[0].split("URL:")[0].strip()
            raise Exception(
                f"❌ {get_text('error.request', error_msg=error_msg)}\n"
                f"💡 {get_text('error.request_tip')}"
            )
        except (KeyError, json.JSONDecodeError) as e:
            raise Exception(
                f"⚠️  {get_text('error.invalid_response')}\n"
                f"💡 {get_text('error.model_unavailable', model=model)}\n"
                f"   {get_text('error.model_suggestion')}"
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
        Get text models from gen.pollinations.ai (with 24h file cache).
        Returns full model metadata: name, description, aliases, paid_only, reasoning, etc.
        """
        from pathlib import Path
        config_dir = Path.home() / ".config" / "polly"
        return fetch_text_models(config_dir)
