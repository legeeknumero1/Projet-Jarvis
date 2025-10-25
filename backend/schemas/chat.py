"""Schémas Pydantic pour les endpoints de chat"""
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

class MessageRequest(BaseModel):
    """Requête de message chat"""
    message: str = Field(..., min_length=1, max_length=5000, description="Message de l'utilisateur")
    user_id: str = Field(default="default", min_length=1, max_length=50, pattern="^[a-zA-Z0-9_-]+$", description="ID utilisateur")
    context: Optional[str] = Field(None, description="Contexte additionnel")
    save_memory: bool = Field(default=True, description="Sauvegarder en mémoire")
    
    @validator('message')
    def validate_message(cls, v):
        """Validation et sanitisation du message"""
        from ..utils.validators import sanitize_message
        return sanitize_message(v)
    
    @validator('user_id')
    def validate_user_id(cls, v):
        """Validation et sanitisation user_id"""
        from ..utils.validators import sanitize_user_id
        return sanitize_user_id(v)

class MessageResponse(BaseModel):
    """Réponse de message chat"""
    response: str = Field(..., description="Réponse de l'assistant")
    timestamp: datetime = Field(..., description="Horodatage de la réponse")
    user_id: str = Field(..., description="ID utilisateur")
    model: str = Field(default="llama3.2:1b", description="Modèle IA utilisé")
    memory_saved: bool = Field(default=False, description="Conversation sauvée en mémoire")
    conversation_id: Optional[str] = Field(None, description="ID de conversation")