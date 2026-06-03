"""
API client for Pollinations.ai
"""

import time
import random
import requests
import json
from typing import Optional, List, Dict, Generator
from urllib.parse import quote
from .config import get_config, API_BASE_URL, API_TIMEOUT, NEW_API_BASE_URL, BACKEND_URL, fetch_text_models, get_provider_base_url
from .i18n import get_text

# HTTP status codes that warrant a retry (transient errors only)
_RETRY_STATUSES = {429, 502, 503}


class PollinationsAPI:
    """Client for Pollinations.ai Text Generation API"""

    def __init__(self, use_direct_api: bool = False):
        self.config = get_config()
        self.use_direct_api = use_direct_api
        self.timeout = API_TIMEOUT
        self.referrer = self.config.get("referrer", "interzonesec.com")

        # Provider routing
        self.provider_type = self.config.get("provider_type", "pollinations")
        self.use_custom_provider = (
            self.provider_type != "pollinations"
            and bool(get_provider_base_url(self.config))
        )

        # Pollinations-specific URLs (used when provider_type == "pollinations")
        self.use_backend = (
            self.config.get("use_backend", True)
            and not use_direct_api
            and not self.use_custom_provider
        )
        self.backend_url = BACKEND_URL
        self.base_url = API_BASE_URL
        self.new_api_url = NEW_API_BASE_URL

    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers — adds Bearer auth for custom providers."""
        if self.use_custom_provider:
            api_key = self.config.get("provider_api_key", "").strip()
            h = {"Content-Type": "application/json", "User-Agent": "Polly/0.1.0"}
            if api_key:
                h["Authorization"] = f"Bearer {api_key}"
            return h
        return {
            "Referer": self.referrer,
            "User-Agent": "Polly/0.1.0",
            "Content-Type": "application/json",
        }

    def _custom_provider_url(self) -> str:
        """Return the /chat/completions URL for the custom provider."""
        base = get_provider_base_url(self.config)
        return f"{base}/chat/completions"

    def list_local_models(self) -> List[Dict]:
        """
        Fetch the model list from the custom provider's /models endpoint.
        Returns [] on failure. Useful for Ollama / LM Studio.
        """
        base = get_provider_base_url(self.config)
        if not base:
            return []
        try:
            resp = requests.get(
                f"{base}/models",
                headers=self._get_headers(),
                timeout=5,
            )
            resp.raise_for_status()
            data = resp.json()
            models = data.get("data", data) if isinstance(data, dict) else data
            return [{"name": m.get("id") or m.get("name", ""), "description": ""} for m in models]
        except Exception:
            return []

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

    def _post_with_retry(self, url: str, payload: dict, headers: dict) -> requests.Response:
        """
        POST with exponential backoff on transient errors (429/502/503/conn/timeout).
        Deterministic errors (400/401/402/404/500) are NOT retried.
        """
        config = get_config()
        max_attempts = int(config.get("retry_max_attempts", 3))
        base_delay = float(config.get("retry_base_delay", 1.0))

        last_exc = None
        last_resp = None

        for attempt in range(1, max_attempts + 1):
            try:
                resp = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
                if resp.status_code not in _RETRY_STATUSES:
                    return resp  # success or deterministic error — return immediately

                # Transient HTTP error
                last_resp = resp
                if attempt == max_attempts:
                    break

                # Honour Retry-After if present (cap at 30s)
                retry_after = resp.headers.get("Retry-After")
                if retry_after:
                    delay = min(float(retry_after), 30.0)
                else:
                    delay = base_delay * (2 ** (attempt - 1))
                    delay *= 1 + random.uniform(-0.25, 0.25)  # ±25% jitter

                time.sleep(delay)

            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                last_exc = e
                if attempt == max_attempts:
                    break
                delay = base_delay * (2 ** (attempt - 1)) * (1 + random.uniform(-0.25, 0.25))
                time.sleep(delay)

        if last_resp is not None:
            return last_resp
        raise last_exc

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
        if self.use_custom_provider:
            # Generic OpenAI-compatible endpoint (Ollama, OpenAI, LM Studio, etc.)
            api_url = self._custom_provider_url()
        elif self.use_backend:
            # Polly proxy backend (default)
            api_url = f"{self.backend_url}/api/chat/completions"
        else:
            # Legacy direct Pollinations API
            api_url = f"{self.base_url}/openai"

        try:
            if stream:
                # Streaming: use plain requests (no retry mid-stream)
                response = requests.post(
                    api_url,
                    json=payload,
                    headers=self._get_headers(),
                    timeout=None,
                    stream=True,
                )
            else:
                response = self._post_with_retry(api_url, payload, self._get_headers())
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
        except (KeyError, json.JSONDecodeError):
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
        Return available models.
        - Custom provider: fetch from the provider's /models endpoint.
        - Pollinations: fetch from gen.pollinations.ai with health filter + cache.
        """
        if self.use_custom_provider:
            local = self.list_local_models()
            if local:
                return local
        from pathlib import Path
        config_dir = Path.home() / ".config" / "polly"
        return fetch_text_models(config_dir)
