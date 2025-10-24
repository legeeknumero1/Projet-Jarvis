"""
Configuration de base de données avec gestion des dépendances FastAPI
"""

from sqlalchemy.ext.asyncio import AsyncSession
from db.database import Database
from config.config import Config

# Instance globale de configuration et base de données
config = Config()
database = Database(config)

async def get_db() -> AsyncSession:
    """
    Dépendance FastAPI pour obtenir une session de base de données
    Utilise le context manager pour gestion automatique
    """
    async with database.get_session_context() as session:
        yield session

async def init_database():
    """Initialiser la connexion à la base de données"""
    await database.connect()

async def close_database():
    """Fermer la connexion à la base de données"""
    await database.disconnect()