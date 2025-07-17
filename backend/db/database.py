import asyncio
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, Text, Integer, JSON
from datetime import datetime
import logging

Base = declarative_base()

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
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    context = Column(JSON, default={})

class Memory(Base):
    __tablename__ = "memories"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(JSON, nullable=True)
    category = Column(String, nullable=True)
    importance = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow)

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
    
    async def get_session(self) -> AsyncSession:
        if not self.session_maker:
            raise RuntimeError("Database not connected")
        return self.session_maker()
    
    async def execute_query(self, query: str, params: dict = None):
        async with self.get_session() as session:
            result = await session.execute(query, params or {})
            await session.commit()
            return result