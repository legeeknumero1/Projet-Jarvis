#!/usr/bin/env python3
"""
Script pour télécharger automatiquement le modèle Ollama
"""

import asyncio
import httpx
import json
import logging
import os
from typing import Dict, Any

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OllamaModelPuller:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def check_ollama_availability(self) -> bool:
        """Vérifie si Ollama est disponible"""
        try:
            response = await self.client.get(f"{self.base_url}/api/version")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama non disponible: {e}")
            return False
    
    async def list_models(self) -> Dict[str, Any]:
        """Liste les modèles installés"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                return response.json()
            return {"models": []}
        except Exception as e:
            logger.error(f"Erreur lors de la liste des modèles: {e}")
            return {"models": []}
    
    async def pull_model(self, model_name: str) -> bool:
        """Télécharge un modèle Ollama"""
        try:
            logger.info(f"🤖 Début téléchargement modèle: {model_name}")
            
            # Requête de téléchargement
            response = await self.client.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name},
                timeout=1800.0  # 30 minutes timeout
            )
            
            if response.status_code == 200:
                # Lire le stream de réponse
                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if "status" in data:
                                if data["status"] == "success":
                                    logger.info(f"✅ Modèle {model_name} téléchargé avec succès")
                                    return True
                                else:
                                    logger.info(f"📥 {data['status']}")
                        except json.JSONDecodeError:
                            continue
            
            logger.error(f"❌ Échec téléchargement modèle {model_name}")
            return False
            
        except Exception as e:
            logger.error(f"Erreur téléchargement modèle {model_name}: {e}")
            return False
    
    async def ensure_model_available(self, model_name: str) -> bool:
        """S'assure qu'un modèle est disponible, le télécharge si nécessaire"""
        # Vérifier si le modèle est déjà installé
        models = await self.list_models()
        installed_models = [m["name"] for m in models.get("models", [])]
        
        if model_name in installed_models:
            logger.info(f"✅ Modèle {model_name} déjà installé")
            return True
        
        # Télécharger le modèle
        logger.info(f"📥 Modèle {model_name} non trouvé, téléchargement...")
        return await self.pull_model(model_name)
    
    async def close(self):
        """Ferme le client HTTP"""
        await self.client.aclose()

async def main():
    """Fonction principale"""
    puller = OllamaModelPuller()
    
    try:
        # Vérifier disponibilité Ollama
        if not await puller.check_ollama_availability():
            logger.error("❌ Ollama n'est pas disponible. Vérifiez qu'il est démarré.")
            return
        
        # Modèles à télécharger
        models_to_pull = [
            "llama3.1:latest",
            "llama3.2:1b"  # Modèle plus léger en backup
        ]
        
        # Télécharger les modèles
        for model in models_to_pull:
            success = await puller.ensure_model_available(model)
            if success:
                logger.info(f"✅ Modèle {model} prêt")
            else:
                logger.error(f"❌ Échec pour le modèle {model}")
        
        logger.info("🎉 Configuration Ollama terminée")
        
    except Exception as e:
        logger.error(f"Erreur générale: {e}")
    finally:
        await puller.close()

if __name__ == "__main__":
    asyncio.run(main())

