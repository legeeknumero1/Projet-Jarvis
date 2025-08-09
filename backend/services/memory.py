"""Service Memory neuromorphique - wrapper pour brain_memory_system"""
import logging
from typing import Dict, List, Any, Optional
from ..schemas.memory import MemoryItem, MemoryQuery, ConversationSaveRequest

logger = logging.getLogger(__name__)

class MemoryService:
    """Service centralisé pour le système de mémoire neuromorphique"""
    
    def __init__(self, settings):
        self.settings = settings
        self.brain_memory_system = None
        
    async def initialize(self, database):
        """Initialise le système de mémoire neuromorphique"""
        try:
            # Import dynamique pour éviter dépendance au démarrage
            from memory.brain_memory_system import BrainMemorySystem
            
            self.brain_memory_system = BrainMemorySystem(database)
            
            logger.info("🧠 [MEMORY] Initialisation système mémoire neuromorphique...")
            await self.brain_memory_system.initialize()
            logger.info("✅ [MEMORY] Système mémoire neuromorphique initialisé")
            
        except Exception as e:
            logger.error(f"❌ [MEMORY] Erreur initialisation: {e}")
    
    def is_available(self) -> bool:
        """Vérifie si le service Memory est disponible"""
        return self.brain_memory_system is not None
    
    async def get_contextual_memories(
        self, 
        user_id: str, 
        message: str, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Récupère les souvenirs contextuels pour un message
        Wrapper pour brain_memory_system.get_contextual_memories()
        """
        try:
            if not self.is_available():
                logger.warning("⚠️ [MEMORY] Système mémoire non disponible")
                return []
            
            logger.debug(f"🧠 [MEMORY] Récupération contexte neuromorphique {user_id}")
            memories = await self.brain_memory_system.get_contextual_memories(
                user_id, message, limit=limit
            )
            logger.debug(f"✅ [MEMORY] Contexte récupéré: {len(memories)} éléments")
            return memories
            
        except Exception as e:
            logger.error(f"❌ [MEMORY] Erreur récupération contexte: {e}")
            return []
    
    async def store_interaction(
        self, 
        user_id: str, 
        user_message: str, 
        assistant_response: str
    ) -> bool:
        """
        Sauvegarde une interaction en mémoire neuromorphique
        Wrapper pour brain_memory_system.store_interaction()
        """
        try:
            if not self.is_available():
                logger.warning("⚠️ [MEMORY] Système mémoire non disponible pour sauvegarde")
                return False
            
            logger.debug("💾 [MEMORY] Sauvegarde conversation neuromorphique...")
            await self.brain_memory_system.store_interaction(
                user_id, user_message, assistant_response
            )
            logger.debug("✅ [MEMORY] Conversation sauvegardée en mémoire neuromorphique")
            return True
            
        except Exception as e:
            logger.error(f"❌ [MEMORY] Erreur sauvegarde: {e}")
            return False
    
    async def search_memories(self, query: MemoryQuery) -> List[MemoryItem]:
        """
        Recherche dans la mémoire neuromorphique avec query structurée
        """
        try:
            if not self.is_available():
                logger.warning("⚠️ [MEMORY] Système mémoire non disponible pour recherche")
                return []
            
            # Utilise la même méthode que get_contextual_memories
            raw_memories = await self.brain_memory_system.get_contextual_memories(
                query.user_id, 
                query.query, 
                limit=query.limit
            )
            
            # Conversion vers MemoryItem pour typage fort
            memories = []
            for raw_memory in raw_memories:
                memory_item = MemoryItem(
                    content=raw_memory.get('content', ''),
                    importance_score=raw_memory.get('importance_score', 0.0),
                    emotional_context=raw_memory.get('emotional_context', {}),
                    timestamp=raw_memory.get('timestamp', ''),
                    memory_type=raw_memory.get('memory_type', 'unknown'),
                    user_id=query.user_id
                )
                memories.append(memory_item)
            
            return memories
            
        except Exception as e:
            logger.error(f"❌ [MEMORY] Erreur recherche mémoire: {e}")
            return []
    
    def format_context_summary(
        self, 
        memories: List[Dict[str, Any]], 
        max_memories: int = 3
    ) -> str:
        """
        Formate les souvenirs en contexte texte pour le LLM
        Extrait de main.py:599-605
        """
        if not memories:
            return ""
            
        context_summary = "MÉMOIRES CONTEXTUELLES (SYSTÈME NEUROMORPHIQUE) :\\n"
        for memory in memories[:max_memories]:
            content = memory.get('content', '')[:80]
            importance = memory.get('importance_score', 0.0)
            emotion = memory.get('emotional_context', {}).get('detected_emotion', 'neutre')
            context_summary += f"- [{emotion}|{importance:.1f}] {content}...\\n"
        
        return f"\\n{context_summary}"