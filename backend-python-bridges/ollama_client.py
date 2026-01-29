"""
Client Ollama LLM - Phase 3 Python Bridges
Intégration avec LLaMA locale via HTTP
"""

import httpx
import json
from typing import Optional, AsyncGenerator, Dict, Any, Generator
from dataclasses import dataclass
from loguru import logger
import os


@dataclass
class OllamaResponse:
    """Réponse Ollama structurée"""
    text: str
    model: str
    stop_reason: str
    tokens_generated: int
    tokens_prompt: int
    duration_ms: float


class OllamaClient:
    """Client HTTP asynchrone pour Ollama LLM local"""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama2:7b",
        timeout: int = 120
    ):
        self.base_url = os.getenv("OLLAMA_URL", base_url)
        self.model = os.getenv("OLLAMA_MODEL", model)
        self.timeout = timeout
        logger.info(f" Ollama Async Client initialized: {self.base_url} | Model: {self.model}")

    async def health_check(self) -> bool:
        """Vérifier si Ollama est accessible (Asynchrone)"""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                is_healthy = response.status_code == 200
                if is_healthy:
                    logger.info(" Ollama service healthy")
                return is_healthy
        except Exception as e:
            logger.error(f" Ollama connection error: {e}")
            return False

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        top_p: float = 0.9,
        max_tokens: int = 512,
    ) -> OllamaResponse:
        """Générer une réponse complète (Asynchrone)"""
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\nUser: {prompt}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": full_prompt,
                        "stream": False,
                        "temperature": temperature,
                        "top_p": top_p,
                        "num_predict": max_tokens,
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    return OllamaResponse(
                        text=data.get("response", "").strip(),
                        model=self.model,
                        stop_reason=data.get("stop_reason", "length"),
                        tokens_generated=data.get("eval_count", 0),
                        tokens_prompt=data.get("prompt_eval_count", 0),
                        duration_ms=data.get("total_duration", 0) / 1_000_000,
                    )
                else:
                    return OllamaResponse(text=f"Error: {response.status_code}", model=self.model, stop_reason="error", tokens_generated=0, tokens_prompt=0, duration_ms=0)
        except Exception as e:
            logger.error(f" Ollama generation error: {e}")
            return OllamaResponse(text=f"Error: {str(e)}", model=self.model, stop_reason="error", tokens_generated=0, tokens_prompt=0, duration_ms=0)


    def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ) -> Generator[str, None, None]:
        """
        Générer une réponse en streaming (token par token)

        Args:
            prompt: Prompt utilisateur
            system_prompt: Prompt système
            temperature: Contrôle créativité
            top_p: Nucleus sampling

        Yields:
            Tokens générés un par un
        """
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\nUser: {prompt}"

        try:
            logger.debug(f" Ollama stream: {self.model}")

            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": True,
                    "temperature": temperature,
                    "top_p": top_p,
                },
                stream=True,
                timeout=self.timeout
            )

            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            token = data.get("response", "")
                            if token:
                                yield token
                        except json.JSONDecodeError:
                            continue
            else:
                logger.error(f" Ollama stream error: {response.status_code}")
                yield f"Error: {response.status_code}"

        except requests.Timeout:
            logger.error(f" Ollama stream timeout")
            yield "Error: Ollama timeout"
        except Exception as e:
            logger.error(f" Ollama stream error: {e}")
            yield f"Error: {str(e)}"

    def set_model(self, model: str):
        """Changer de modèle"""
        self.model = model
        logger.info(f" Ollama model changed to: {model}")


# Instance globale
_ollama_client: Optional[OllamaClient] = None


def get_ollama_client() -> OllamaClient:
    """Obtenir instance singleton Ollama"""
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = OllamaClient()
    return _ollama_client


def init_ollama(base_url: str = "http://localhost:11434", model: str = "llama2:7b"):
    """Initialiser Ollama avec paramètres personnalisés"""
    global _ollama_client
    _ollama_client = OllamaClient(base_url=base_url, model=model)
