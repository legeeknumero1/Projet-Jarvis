import json
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
# from sentence_transformers import SentenceTransformer
from sqlalchemy import select, update, delete
import logging

from db.database import Database, Memory, Conversation, User

class MemoryManager:
    def __init__(self, database: Database):
        self.db = database
        self.embedding_model = None
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self):
        try:
            # Temporairement désactivé jusqu'à installation sentence-transformers
            # self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.embedding_model = None
            self.logger.info("Memory manager initialized successfully (embeddings disabled)")
        except Exception as e:
            self.logger.error(f"Failed to initialize memory manager: {e}")
            raise
    
    async def save_conversation(self, user_id: str, message: str, response: str, context: Dict[str, Any] = None):
        async with self.db.get_session() as session:
            try:
                conversation = Conversation(
                    user_id=user_id,
                    message=message,
                    response=response,
                    context=context or {},
                    timestamp=datetime.utcnow()
                )
                session.add(conversation)
                await session.commit()
                
                # Créer une mémoire à partir de la conversation
                await self._create_memory_from_conversation(user_id, message, response)
                
            except Exception as e:
                await session.rollback()
                self.logger.error(f"Failed to save conversation: {e}")
                raise
    
    async def _create_memory_from_conversation(self, user_id: str, message: str, response: str):
        # Analyser le contenu pour extraire des informations importantes
        content = f"User: {message}\nJarvis: {response}"
        
        # Générer l'embedding (désactivé temporairement)
        embedding = None
        if self.embedding_model:
            embedding = self.embedding_model.encode(content).tolist()
        
        # Déterminer l'importance (simple heuristique)
        importance = await self._calculate_importance(content)
        
        # Catégoriser le contenu
        category = await self._categorize_content(content)
        
        async with self.db.get_session() as session:
            try:
                memory = Memory(
                    user_id=user_id,
                    content=content,
                    embedding=embedding,
                    category=category,
                    importance=importance,
                    created_at=datetime.utcnow(),
                    last_accessed=datetime.utcnow()
                )
                session.add(memory)
                await session.commit()
                
            except Exception as e:
                await session.rollback()
                self.logger.error(f"Failed to create memory: {e}")
    
    async def get_user_context(self, user_id: str) -> Dict[str, Any]:
        async with self.db.get_session() as session:
            try:
                # Récupérer les conversations récentes
                recent_conversations = await session.execute(
                    select(Conversation)
                    .where(Conversation.user_id == user_id)
                    .order_by(Conversation.timestamp.desc())
                    .limit(10)
                )
                conversations = recent_conversations.scalars().all()
                
                # Récupérer les mémoires pertinentes
                relevant_memories = await session.execute(
                    select(Memory)
                    .where(Memory.user_id == user_id)
                    .order_by(Memory.importance.desc(), Memory.last_accessed.desc())
                    .limit(20)
                )
                memories = relevant_memories.scalars().all()
                
                return {
                    "user_id": user_id,
                    "recent_conversations": [
                        {
                            "message": conv.message,
                            "response": conv.response,
                            "timestamp": conv.timestamp.isoformat()
                        } for conv in conversations
                    ],
                    "relevant_memories": [
                        {
                            "content": mem.content,
                            "category": mem.category,
                            "importance": mem.importance,
                            "created_at": mem.created_at.isoformat()
                        } for mem in memories
                    ]
                }
                
            except Exception as e:
                self.logger.error(f"Failed to get user context: {e}")
                return {"user_id": user_id, "recent_conversations": [], "relevant_memories": []}
    
    async def search_memories(self, user_id: str, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        if not self.embedding_model:
            # Recherche simple par texte si pas d'embeddings
            return await self._text_search_memories(user_id, query, limit)
        
        # Générer l'embedding de la requête
        query_embedding = self.embedding_model.encode(query).tolist()
        
        async with self.db.get_session() as session:
            try:
                # Récupérer toutes les mémoires de l'utilisateur
                memories_result = await session.execute(
                    select(Memory)
                    .where(Memory.user_id == user_id)
                    .where(Memory.embedding.isnot(None))
                )
                memories = memories_result.scalars().all()
                
                # Calculer la similarité cosinus
                similarities = []
                for memory in memories:
                    if memory.embedding:
                        similarity = self._cosine_similarity(query_embedding, memory.embedding)
                        similarities.append((memory, similarity))
                
                # Trier par similarité
                similarities.sort(key=lambda x: x[1], reverse=True)
                
                # Mettre à jour last_accessed pour les mémoires consultées
                for memory, _ in similarities[:limit]:
                    memory.last_accessed = datetime.utcnow()
                
                await session.commit()
                
                return [
                    {
                        "content": mem.content,
                        "category": mem.category,
                        "importance": mem.importance,
                        "similarity": sim,
                        "created_at": mem.created_at.isoformat()
                    } for mem, sim in similarities[:limit]
                ]
                
            except Exception as e:
                self.logger.error(f"Failed to search memories: {e}")
                return []
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    
    async def _calculate_importance(self, content: str) -> int:
        # Heuristique simple pour l'importance
        keywords = ["important", "rappel", "urgent", "ne pas oublier", "rendez-vous"]
        importance = 1
        
        for keyword in keywords:
            if keyword.lower() in content.lower():
                importance += 1
        
        return min(importance, 5)
    
    async def _categorize_content(self, content: str) -> str:
        # Catégorisation simple basée sur des mots-clés
        categories = {
            "domotique": ["lumière", "chauffage", "température", "capteur"],
            "personnel": ["nom", "âge", "préférence"],
            "planning": ["rendez-vous", "rappel", "agenda"],
            "technique": ["code", "programmation", "serveur"],
            "général": []
        }
        
        content_lower = content.lower()
        for category, keywords in categories.items():
            if any(keyword in content_lower for keyword in keywords):
                return category
        
        return "général"
    
    async def _text_search_memories(self, user_id: str, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Recherche simple par texte sans embeddings"""
        async with self.db.get_session() as session:
            try:
                memories_result = await session.execute(
                    select(Memory)
                    .where(Memory.user_id == user_id)
                    .where(Memory.content.ilike(f"%{query}%"))
                    .order_by(Memory.importance.desc(), Memory.last_accessed.desc())
                    .limit(limit)
                )
                memories = memories_result.scalars().all()
                
                return [
                    {
                        "content": mem.content,
                        "category": mem.category,
                        "importance": mem.importance,
                        "similarity": 1.0,  # Score fixe sans embedding
                        "created_at": mem.created_at.isoformat()
                    } for mem in memories
                ]
                
            except Exception as e:
                self.logger.error(f"Failed to text search memories: {e}")
                return []