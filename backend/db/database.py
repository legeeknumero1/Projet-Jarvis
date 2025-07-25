import asyncio
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, Text, Integer, JSON
from datetime import datetime
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