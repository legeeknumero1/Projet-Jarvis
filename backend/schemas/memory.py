"""Schémas Pydantic pour le système de mémoire neuromorphique"""
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import List, Dict, Any, Optional

class MemoryQuery(BaseModel):
    """Requête de recherche en mémoire"""
    query: str = Field(..., min_length=1, max_length=500, description="Requête de recherche")
    user_id: str = Field(..., min_length=1, max_length=50, description="ID utilisateur")
    limit: int = Field(default=5, ge=1, le=20, description="Nombre maximum de résultats")
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Seuil de similarité")
    
    @validator('query')
    def validate_query(cls, v):
        """Validation et sanitisation de la requête"""
        from ..utils.validators import sanitize_message
        return sanitize_message(v)
    
    @validator('user_id')
    def validate_user_id(cls, v):
        """Validation user_id"""
        from ..utils.validators import sanitize_user_id
        return sanitize_user_id(v)

class MemoryItem(BaseModel):
    """Item de mémoire avec métadonnées"""
    content: str = Field(..., description="Contenu du souvenir")
    importance_score: float = Field(..., ge=0.0, le=1.0, description="Score d'importance")
    emotional_context: Dict[str, Any] = Field(default_factory=dict, description="Contexte émotionnel")
    timestamp: datetime = Field(..., description="Horodatage")
    memory_type: str = Field(..., description="Type de mémoire")
    user_id: str = Field(..., description="ID utilisateur")

class MemoryResponse(BaseModel):
    """Réponse de recherche en mémoire"""
    memories: List[MemoryItem] = Field(..., description="Liste des souvenirs trouvés")
    total_count: int = Field(..., description="Nombre total de résultats")
    query_processed: str = Field(..., description="Requête traitée")

class ConversationSaveRequest(BaseModel):
    """Requête de sauvegarde de conversation"""
    user_id: str = Field(..., min_length=1, max_length=50, description="ID utilisateur")
    user_message: str = Field(..., min_length=1, max_length=5000, description="Message utilisateur")
    assistant_response: str = Field(..., min_length=1, max_length=10000, description="Réponse assistant")
    context: Optional[Dict[str, Any]] = Field(None, description="Contexte additionnel")
    
    @validator('user_id')
    def validate_user_id(cls, v):
        from ..utils.validators import sanitize_user_id
        return sanitize_user_id(v)
    
    @validator('user_message')
    def validate_user_message(cls, v):
        from ..utils.validators import sanitize_message
        return sanitize_message(v)
    
    @validator('assistant_response')
    def validate_assistant_response(cls, v):
        from ..utils.validators import sanitize_message
        return sanitize_message(v)