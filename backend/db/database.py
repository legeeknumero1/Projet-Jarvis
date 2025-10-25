import asyncio
try:
    import asyncpg  # noqa: F401
except ModuleNotFoundError:
    asyncpg = None
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, Text, Integer, JSON, select
from datetime import datetime
from typing import Any, Dict, List, Optional
import logging
import os
from cryptography.fernet import Fernet
import base64

Base = declarative_base()

class EncryptionManager:
    """Gestionnaire de chiffrement pour les données sensibles"""
    
    def __init__(self):
        # Récupérer ou générer une clé de chiffrement
        self.encryption_key = os.getenv('JARVIS_ENCRYPTION_KEY')
        if not self.encryption_key:
            # Générer une nouvelle clé si elle n'existe pas
            self.encryption_key = Fernet.generate_key().decode()
            logging.warning("⚠️ [ENCRYPTION] Clé de chiffrement générée automatiquement")
            logging.warning("🔒 [ENCRYPTION] Définissez JARVIS_ENCRYPTION_KEY en variable d'environnement pour la production")
        
        # Convertir en bytes si nécessaire
        if isinstance(self.encryption_key, str):
            self.encryption_key = self.encryption_key.encode()
            
        self.cipher = Fernet(self.encryption_key)
    
    def encrypt(self, data: str) -> str:
        """Chiffrer des données"""
        if not data:
            return data
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Déchiffrer des données"""
        if not encrypted_data:
            return encrypted_data
        try:
            return self.cipher.decrypt(encrypted_data.encode()).decode()
        except Exception as e:
            logging.error(f"❌ [ENCRYPTION] Erreur déchiffrement: {e}")
            return encrypted_data  # Retourner les données originales en cas d'erreur

# Instance globale du gestionnaire de chiffrement
encryption_manager = EncryptionManager()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    preferences = Column(JSON, default={})

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False)
    message = Column(Text, nullable=False)  # Chiffré via propriétés
    response = Column(Text, nullable=False)  # Chiffré via propriétés
    timestamp = Column(DateTime, default=datetime.utcnow)
    context = Column(JSON, default={})
    
    @property
    def decrypted_message(self):
        """Récupérer le message déchiffré"""
        return encryption_manager.decrypt(self.message)
    
    @decrypted_message.setter
    def decrypted_message(self, value):
        """Stocker le message chiffré"""
        self.message = encryption_manager.encrypt(value)
    
    @property
    def decrypted_response(self):
        """Récupérer la réponse déchiffrée"""
        return encryption_manager.decrypt(self.response)
    
    @decrypted_response.setter
    def decrypted_response(self, value):
        """Stocker la réponse chiffrée"""
        self.response = encryption_manager.encrypt(value)

class Memory(Base):
    __tablename__ = "memories"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False)
    content = Column(Text, nullable=False)  # Chiffré via propriétés
    embedding = Column(JSON, nullable=True)
    category = Column(String, nullable=True)
    importance = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    
    @property
    def decrypted_content(self):
        """Récupérer le contenu déchiffré"""
        return encryption_manager.decrypt(self.content)
    
    @decrypted_content.setter
    def decrypted_content(self, value):
        """Stocker le contenu chiffré"""
        self.content = encryption_manager.encrypt(value)

class Database:
    def __init__(self, config):
        self.config = config
        self.engine = None
        self.session_maker = None
        self.logger = logging.getLogger(__name__)
    
    async def connect(self):
        try:
            self.engine = create_async_engine(
                self.config.database_url,
                echo=self.config.debug,
                pool_pre_ping=True,
                pool_recycle=3600
            )
            
            self.session_maker = sessionmaker(
                self.engine, 
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Créer les tables
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            self.logger.info("Database connected successfully")
        except Exception as e:
            self.logger.error(f"Database connection failed: {e}")
            raise
    
    async def disconnect(self):
        if self.engine:
            await self.engine.dispose()
            self.logger.info("Database disconnected")
    
    def _normalize_importance(self, raw_score: Optional[Any]) -> int:
        """Convertit un score float 0-1 en importance 1-5."""
        try:
            if raw_score is None:
                return 1
            if isinstance(raw_score, int):
                return max(1, min(5, raw_score))
            score = float(raw_score)
            return max(1, min(5, int(round(score * 5))))
        except (TypeError, ValueError):
            return 1

    def _denormalize_importance(self, value: Optional[int]) -> float:
        """Convertit l'importance stockée (1-5) en score 0-1."""
        if value is None:
            return 0.2
        return max(0.0, min(1.0, value / 5.0))

    def _parse_datetime(self, value: Optional[Any]) -> Optional[datetime]:
        """Parsing tolérant pour les dates ISO."""
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            iso_value = value.replace("Z", "+00:00")
            try:
                return datetime.fromisoformat(iso_value)
            except ValueError:
                self.logger.warning(f"Unable to parse datetime value '{value}', fallback to now().")
        return datetime.utcnow()

    async def save_memory_fragment(self, fragment: Dict[str, Any]) -> bool:
        """Persiste un fragment de mémoire produit par BrainMemorySystem."""
        async with self.get_session() as session:
            try:
                memory = Memory(
                    user_id=fragment.get("user_id", "default"),
                    embedding=fragment.get("embedding"),
                    category=fragment.get("category")
                    or fragment.get("metadata", {}).get("category"),
                    importance=self._normalize_importance(
                        fragment.get("importance_score")
                    ),
                    created_at=self._parse_datetime(fragment.get("created_at")),
                    last_accessed=self._parse_datetime(fragment.get("last_accessed")),
                )
                memory.decrypted_content = fragment.get("content", "")
                session.add(memory)
                await session.commit()
                return True
            except Exception as exc:
                await session.rollback()
                self.logger.error(f"[MEMORY] Failed to save fragment: {exc}")
                return False

    async def search_memories_hybrid(
        self, user_id: str, query: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Recherche textuelle simple dans les souvenirs stockés."""
        async with self.get_session() as session:
            try:
                stmt = (
                    select(Memory)
                    .where(Memory.user_id == user_id)
                    .order_by(Memory.importance.desc(), Memory.last_accessed.desc())
                    .limit(max(limit * 3, limit))
                )
                result = await session.execute(stmt)
                scored_entries: List[tuple] = []
                query_lower = (query or "").lower()

                for mem in result.scalars().all():
                    content = mem.decrypted_content or ""
                    if query_lower:
                        query_terms = {token for token in query_lower.split() if token}
                        content_terms = {token for token in content.lower().split() if token}
                        overlap = query_terms & content_terms
                        if query_terms:
                            match_score = len(overlap) / len(query_terms)
                        else:
                            match_score = 0.0
                        if match_score == 0.0:
                            match_score = 0.1  # Laisser une chance via importance
                    else:
                        match_score = 0.5

                    importance_score = self._denormalize_importance(mem.importance)
                    combined_score = match_score + importance_score

                    scored_entries.append(
                        (
                            combined_score,
                            mem,
                            {
                                "content": content,
                                "importance_score": importance_score,
                                "created_at": mem.created_at.isoformat()
                                if mem.created_at
                                else None,
                                "last_accessed": mem.last_accessed.isoformat()
                                if mem.last_accessed
                                else None,
                                "memory_type": "episodic",
                                "emotional_context": {},
                                "metadata": {"id": mem.id, "category": mem.category},
                            },
                        )
                    )

                scored_entries.sort(key=lambda item: item[0], reverse=True)

                now = datetime.utcnow()
                top_entries = scored_entries[:limit]
                for _, mem_obj, _ in top_entries:
                    mem_obj.last_accessed = now
                await session.commit()

                return [entry[2] for entry in top_entries]
            except Exception as exc:
                await session.rollback()
                self.logger.error(f"[MEMORY] Failed hybrid search: {exc}")
                return []

    async def delete_memory(self, memory_id: int) -> bool:
        """Suppression d'une mémoire par identifiant."""
        async with self.get_session() as session:
            try:
                memory = await session.get(Memory, memory_id)
                if not memory:
                    return False
                await session.delete(memory)
                await session.commit()
                return True
            except Exception as exc:
                await session.rollback()
                self.logger.error(f"[MEMORY] Failed to delete memory: {exc}")
                return False

    def get_session(self) -> AsyncSession:
        if not self.session_maker:
            raise RuntimeError("Database not connected")
        return self.session_maker()
    
    async def execute_query(self, query: str, params: dict = None):
        async with self.get_session() as session:
            try:
                result = await session.execute(query, params or {})
                await session.commit()
                return result
            except Exception as e:
                await session.rollback()
                raise
