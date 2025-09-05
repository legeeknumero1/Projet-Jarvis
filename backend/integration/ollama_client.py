import asyncio
import json
import logging
import os
from typing import Dict, Any, Optional, List, AsyncGenerator
import httpx
from contextlib import asynccontextmanager

class OllamaClient:
    def __init__(self, base_url: str = None):
        # Utiliser variables d'environnement ou fallback dynamique
        if base_url is None:
            ollama_ip = os.getenv('OLLAMA_IP', '172.20.0.30')
            ollama_port = os.getenv('OLLAMA_INTERNAL_PORT', '11434')
            base_url = f"http://{ollama_ip}:{ollama_port}"
        
        self.base_url = base_url
        self.client = None
        self.logger = logging.getLogger(__name__)
        self._client_lock = asyncio.Lock()
        self.max_retries = 3
        self.retry_delay = 1.0
    
    async def _ensure_client(self):
        """Assurer la présence du client HTTP avec protection contre les accès concurrents"""
        async with self._client_lock:
            if self.client is None or self.client.is_closed:
                # Configuration sécurisée du client HTTP
                timeout = httpx.Timeout(
                    timeout=120.0,
                    connect=10.0,
                    read=110.0,
                    write=10.0,
                    pool=5.0
                )
                
                limits = httpx.Limits(
                    max_keepalive_connections=5,
                    max_connections=10,
                    keepalive_expiry=30.0
                )
                
                self.client = httpx.AsyncClient(
                    timeout=timeout,
                    limits=limits,
                    follow_redirects=True,
                    verify=False  # Pour environnements internes
                )
    
    async def __aenter__(self):
        await self._ensure_client()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def close(self):
        """Fermer proprement le client HTTP"""
        async with self._client_lock:
            if self.client and not self.client.is_closed:
                try:
                    await self.client.aclose()
                    self.logger.debug("Ollama client closed")
                except Exception as e:
                    self.logger.error(f"Error closing Ollama client: {e}")
                finally:
                    self.client = None
    
    async def _execute_with_retry(self, operation_name: str, operation_func, *args, **kwargs):
        """Exécuter une opération avec retry automatique"""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                await self._ensure_client()
                return await operation_func(*args, **kwargs)
                
            except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    self.logger.warning(f"Ollama {operation_name} failed (attempt {attempt + 1}), retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    self.logger.error(f"Ollama {operation_name} failed after {self.max_retries} attempts")
                    
            except Exception as e:
                self.logger.error(f"Ollama {operation_name} error: {e}")
                last_error = e
                break
        
        raise last_error if last_error else Exception(f"Ollama {operation_name} failed")
    
    async def is_available(self) -> bool:
        """Vérifie si Ollama est disponible avec retry"""
        try:
            async def check_version():
                response = await self.client.get(f"{self.base_url}/api/version")
                return response.status_code == 200
            
            return await self._execute_with_retry("health_check", check_version)
            
        except Exception as e:
            self.logger.error(f"Ollama not available: {e}")
            return False
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """Liste les modèles disponibles avec gestion d'erreurs améliorée"""
        try:
            async def get_models():
                response = await self.client.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    return data.get("models", [])
                else:
                    raise httpx.HTTPStatusError(f"HTTP {response.status_code}", request=response.request, response=response)
            
            return await self._execute_with_retry("list_models", get_models)
            
        except Exception as e:
            self.logger.error(f"Error listing models: {e}")
            return []
    
    async def pull_model(self, model_name: str) -> bool:
        """Télécharge un modèle"""
        try:
            await self._ensure_client()
            self.logger.info(f"Starting to pull model: {model_name}")
            
            async with self.client.stream(
                "POST",
                f"{self.base_url}/api/pull",
                json={"name": model_name}
            ) as response:
                if response.status_code != 200:
                    self.logger.error(f"Failed to pull model: {response.status_code}")
                    return False
                
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            data = json.loads(line)
                            if "status" in data:
                                self.logger.info(f"Pull status: {data['status']}")
                            if data.get("status") == "success":
                                self.logger.info(f"Model {model_name} pulled successfully")
                                return True
                        except json.JSONDecodeError:
                            continue
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error pulling model {model_name}: {e}")
            return False
    
    async def generate(
        self,
        model: str,
        prompt: str,
        context: Optional[List[int]] = None,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> Optional[str]:
        """Génère une réponse avec le modèle"""
        try:
            await self._ensure_client()
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            if context:
                payload["context"] = context
            
            if system:
                payload["system"] = system
            
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "")
            else:
                self.logger.error(f"Generation failed: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return None
    
    async def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> Optional[str]:
        """Interface de chat avec historique"""
        try:
            await self._ensure_client()
            payload = {
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/chat",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("message", {}).get("content", "")
            else:
                self.logger.error(f"Chat failed: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error in chat: {e}")
            return None
    
    async def stream_generate(
        self,
        model: str,
        prompt: str,
        context: Optional[List[int]] = None,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> AsyncGenerator[str, None]:
        """Génère une réponse en streaming"""
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            if context:
                payload["context"] = context
            
            if system:
                payload["system"] = system
            
            async with self.client.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json=payload
            ) as response:
                if response.status_code != 200:
                    self.logger.error(f"Stream generation failed: {response.status_code}")
                    return
                
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            data = json.loads(line)
                            if "response" in data:
                                yield data["response"]
                            if data.get("done", False):
                                break
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            self.logger.error(f"Error in stream generation: {e}")
    
    async def ensure_model_available(self, model_name: str) -> bool:
        """S'assure qu'un modèle est disponible, le télécharge si nécessaire"""
        models = await self.list_models()
        model_names = [m["name"] for m in models]
        
        if model_name not in model_names:
            self.logger.info(f"Model {model_name} not found locally, downloading...")
            return await self.pull_model(model_name)
        
        return True
    
    async def test_connection(self) -> bool:
        """Teste la connexion à Ollama"""
        try:
            await self._ensure_client()
            response = await self.client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Error testing Ollama connection: {e}")
            return False
    
    async def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Récupère les informations d'un modèle"""
        try:
            await self._ensure_client()
            response = await self.client.post(
                f"{self.base_url}/api/show",
                json={"name": model_name}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting model info: {e}")
            return None