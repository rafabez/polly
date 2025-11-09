"""
API client for Pollinations.ai
"""

import requests
import json
from typing import Optional, List, Dict, Generator
from urllib.parse import quote
from .config import get_config, API_BASE_URL, API_TIMEOUT


class PollinationsAPI:
    """Client for Pollinations.ai Text Generation API"""
    
    def __init__(self):
        self.config = get_config()
        self.base_url = API_BASE_URL
        self.timeout = API_TIMEOUT
        self.referrer = self.config.get("referrer", "deepentest.com")
    
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
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream
        }
        
        # Add seed if provided (for varied responses in motivational mode)
        if seed is not None:
            payload["seed"] = seed
        
        try:
            response = requests.post(
                f"{self.base_url}/openai",
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
                f"⏱️  Timeout: O modelo '{model}' demorou muito para responder.\n"
                f"💡 Tente: polly --list-models para ver outros modelos disponíveis\n"
                f"   Ou use: --model gemini (geralmente mais rápido)"
            )
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else "desconhecido"
            if status_code == 503 or status_code == 502:
                raise Exception(
                    f"🔴 Serviço indisponível: O modelo '{model}' está temporariamente fora do ar.\n"
                    f"💡 Tente outro modelo:\n"
                    f"   polly --model gemini <sua pergunta>\n"
                    f"   polly --model openai <sua pergunta>\n"
                    f"   polly --list-models  # Ver todos os modelos"
                )
            elif status_code == 429:
                raise Exception(
                    f"⚠️  Rate limit: Muitas requisições.\n"
                    f"💡 Aguarde alguns segundos e tente novamente."
                )
            else:
                raise Exception(
                    f"❌ Erro HTTP {status_code}: {str(e)}\n"
                    f"💡 Tente outro modelo: polly --list-models"
                )
        except requests.exceptions.ConnectionError:
            raise Exception(
                f"🌐 Erro de conexão: Não foi possível conectar à API Pollinations.\n"
                f"💡 Verifique sua conexão com a internet."
            )
        except requests.exceptions.RequestException as e:
            raise Exception(
                f"❌ Erro na requisição: {str(e)}\n"
                f"💡 Tente outro modelo: polly --list-models"
            )
        except (KeyError, json.JSONDecodeError) as e:
            raise Exception(
                f"⚠️  Resposta inválida da API: {str(e)}\n"
                f"💡 O modelo '{model}' pode estar com problemas.\n"
                f"   Tente: polly --model gemini (geralmente mais estável)"
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
    
    def get_available_models(self) -> List[Dict[str, any]]:
        """
        Get list of available models from API
        
        Returns:
            List of model information dicts
        """
        try:
            response = requests.get(
                f"{self.base_url}/models",
                headers=self._get_headers(),
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch models: {str(e)}")
