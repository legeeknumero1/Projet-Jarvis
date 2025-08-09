"""Schémas Pydantic pour les endpoints vocaux (STT/TTS)"""
from pydantic import BaseModel, Field, validator
from typing import Optional

class TranscriptionResponse(BaseModel):
    """Réponse de transcription vocale"""
    transcript: str = Field(..., description="Texte transcrit")
    confidence: float = Field(default=0.95, ge=0.0, le=1.0, description="Score de confiance")
    duration: Optional[float] = Field(None, description="Durée audio en secondes")

class TTSRequest(BaseModel):
    """Requête de synthèse vocale"""
    text: str = Field(..., min_length=1, max_length=2000, description="Texte à synthétiser")
    voice: str = Field(default="default", pattern="^[a-zA-Z0-9_-]+$", description="Voix à utiliser")
    speed: Optional[float] = Field(default=1.0, ge=0.5, le=2.0, description="Vitesse de lecture")
    
    @validator('text')
    def validate_text(cls, v):
        """Validation et sanitisation du texte TTS"""
        from ..utils.validators import sanitize_text
        return sanitize_text(v)
    
    @validator('voice')
    def validate_voice(cls, v):
        """Validation du nom de voix"""
        from ..utils.validators import sanitize_voice_name
        return sanitize_voice_name(v)