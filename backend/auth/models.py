"""
Modèles d'authentification pour Jarvis
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, EmailStr
from typing import Optional

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Jarvis specific fields
    jarvis_permissions = Column(Text, nullable=True)  # JSON string
    preferred_voice = Column(String(50), default="default")
    ui_theme = Column(String(20), default="cyberpunk")

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserRead(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool
    is_superuser: bool
    is_verified: bool
    created_at: datetime
    preferred_voice: Optional[str] = "default"
    ui_theme: Optional[str] = "cyberpunk"
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    preferred_voice: Optional[str] = None
    ui_theme: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: UserRead

class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None