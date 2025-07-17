import asyncio
import json
import logging
from typing import Dict, Any, Optional, List, AsyncGenerator
import httpx

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=120.0)
        self.logger = logging.getLogger(__name__)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def is_available(self) -> bool:
        """Vérifie si Ollama est disponible"""
        try:
            response = await self.client.get(f"{self.base_url}/api/version")
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Ollama not available: {e}")
            return False
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """Liste les modèles disponibles"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return data.get("models", [])
            else:
                self.logger.error(f"Failed to list models: {response.status_code}")
                return []
        except Exception as e:
            self.logger.error(f"Error listing models: {e}")
            return []
    
    async def pull_model(self, model_name: str) -> bool:
        """Télécharge un modèle"""
        try:
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
    
    async def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Récupère les informations d'un modèle"""
        try:
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