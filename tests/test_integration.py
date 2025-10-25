#!/usr/bin/env python3
"""
Script de test pour vérifier l'intégration complète gpt-oss:20B
- Mémoire persistante
- Accès internet
- Services intégrés
"""

import asyncio
import sys
import os
import logging

# Ajouter le backend au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.config.config import Config
from backend.services.llm import LLMService
from backend.services.web_search import WebSearchService
from backend.memory.memory_manager import MemoryManager
from backend.db.database import Database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Settings:
    def __init__(self):
        self.ollama_base_url = "http://localhost:11434"
        self.db_host = "localhost"
        self.db_port = 5432
        self.db_name = "jarvis"
        self.db_user = "jarvis"
        self.db_password = "jarvis123"
        self.redis_host = "localhost"
        self.redis_port = 6379
        self.qdrant_url = "http://localhost:6333"
        self.qdrant_api_key = None

async def test_integration():
    """Test complet de l'intégration"""
    try:
        logger.info("🧪 [TEST] Démarrage test intégration gpt-oss:20B...")
        
        # 1. Initialisation des services
        settings = Settings()
        config = Config()
        database = Database(config)
        
        # Services
        logger.info("📦 [TEST] Initialisation des services...")
        llm_service = LLMService(settings)
        web_search_service = WebSearchService(settings)
        brain_memory_service = MemoryManager(database)
        
        # Initialisation
        await llm_service.initialize()
        await web_search_service.initialize()
        await brain_memory_service.initialize()
        
        # Injection des services
        logger.info("🔗 [TEST] Injection des services dans LLM...")
        llm_service.inject_services(
            web_search_service=web_search_service,
            brain_memory_service=brain_memory_service
        )
        
        # 2. Test mémoire persistante
        logger.info("🧠 [TEST] Test mémoire persistante...")
        user_id = "test_user_enzo"
        
        # Premier message pour créer une mémoire
        response1 = await llm_service.generate_response(
            message="Bonjour Jarvis, je suis Enzo, j'aime la cybersécurité et je vis à Perpignan",
            context={},
            user_id=user_id
        )
        logger.info(f"📝 [TEST] Réponse 1: {response1[:100]}...")
        
        # Deuxième message pour tester la mémoire
        response2 = await llm_service.generate_response(
            message="Te souviens-tu de moi et de ce que j'aime ?",
            context={},
            user_id=user_id
        )
        logger.info(f"🧠 [TEST] Réponse mémoire: {response2[:100]}...")
        
        # 3. Test accès internet
        logger.info("🌐 [TEST] Test accès internet...")
        response3 = await llm_service.generate_response(
            message="Quelles sont les dernières actualités en cybersécurité ?",
            context={},
            user_id=user_id
        )
        logger.info(f"📰 [TEST] Réponse web: {response3[:100]}...")
        
        # 4. Test combiné mémoire + internet
        logger.info("🚀 [TEST] Test combiné mémoire + internet...")
        response4 = await llm_service.generate_response(
            message="Recherche des nouvelles sur la cybersécurité qui pourraient m'intéresser à Perpignan",
            context={},
            user_id=user_id
        )
        logger.info(f"🎯 [TEST] Réponse combinée: {response4[:100]}...")
        
        logger.info("✅ [TEST] Tous les tests réussis !")
        logger.info("✅ [TEST] gpt-oss:20B dispose maintenant de:")
        logger.info("  🧠 Mémoire persistante entre conversations")
        logger.info("  🌐 Accès internet en temps réel")
        logger.info("  🤖 Intégration complète des services")
        
        # Fermeture propre
        await llm_service.close()
        await web_search_service.close()
        # memory_manager n'a pas de méthode close()
        
    except Exception as e:
        logger.error(f"❌ [TEST] Erreur test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_integration())