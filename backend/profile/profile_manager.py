import json
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy import select, update
import logging

from db.database import Database, User

class ProfileManager:
    def __init__(self, database: Database):
        self.db = database
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self):
        self.logger.info("Profile manager initialized")
    
    async def create_user(self, user_id: str, name: str, preferences: Dict[str, Any] = None) -> User:
        async with self.db.get_session() as session:
            try:
                user = User(
                    id=user_id,
                    name=name,
                    preferences=preferences or {},
                    created_at=datetime.utcnow()
                )
                session.add(user)
                await session.commit()
                
                self.logger.info(f"User {user_id} created successfully")
                return user
                
            except Exception as e:
                await session.rollback()
                self.logger.error(f"Failed to create user {user_id}: {e}")
                raise
    
    async def get_user(self, user_id: str) -> Optional[User]:
        async with self.db.get_session() as session:
            try:
                result = await session.execute(
                    select(User).where(User.id == user_id)
                )
                user = result.scalars().first()
                return user
                
            except Exception as e:
                self.logger.error(f"Failed to get user {user_id}: {e}")
                return None
    
    async def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        async with self.db.get_session() as session:
            try:
                result = await session.execute(
                    update(User)
                    .where(User.id == user_id)
                    .values(preferences=preferences)
                )
                await session.commit()
                
                if result.rowcount > 0:
                    self.logger.info(f"Updated preferences for user {user_id}")
                    return True
                else:
                    self.logger.warning(f"No user found with id {user_id}")
                    return False
                
            except Exception as e:
                await session.rollback()
                self.logger.error(f"Failed to update preferences for user {user_id}: {e}")
                return False
    
    async def get_user_preference(self, user_id: str, key: str, default: Any = None) -> Any:
        user = await self.get_user(user_id)
        if user and user.preferences:
            return user.preferences.get(key, default)
        return default
    
    async def set_user_preference(self, user_id: str, key: str, value: Any) -> bool:
        user = await self.get_user(user_id)
        if user:
            preferences = user.preferences or {}
            preferences[key] = value
            return await self.update_user_preferences(user_id, preferences)
        return False
    
    async def get_or_create_user(self, user_id: str, name: str = None) -> User:
        user = await self.get_user(user_id)
        if not user:
            user = await self.create_user(user_id, name or user_id)
        return user