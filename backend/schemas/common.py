"""Schémas communs utilisés dans toute l'API"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any

class APIResponse(BaseModel):
    """Réponse API standardisée"""
    success: bool = Field(..., description="Succès de l'opération")
    message: str = Field(..., description="Message de retour")
    data: Optional[Dict[str, Any]] = Field(None, description="Données de réponse")
    timestamp: datetime = Field(default_factory=datetime.now, description="Horodatage")

class HealthResponse(BaseModel):
    """Réponse du health check"""
    status: str = Field(..., description="Statut de l'API")
    timestamp: datetime = Field(default_factory=datetime.now, description="Horodatage")
    version: str = Field(default="1.1.0", description="Version API")
    services: Optional[Dict[str, str]] = Field(None, description="Statut des services")

class ErrorResponse(BaseModel):
    """Réponse d'erreur standardisée"""
    error: str = Field(..., description="Type d'erreur")
    message: str = Field(..., description="Message d'erreur")
    details: Optional[Dict[str, Any]] = Field(None, description="Détails supplémentaires")
    timestamp: datetime = Field(default_factory=datetime.now, description="Horodatage")

class MetricsResponse(BaseModel):
    """Réponse des métriques système"""
    jarvis_requests_total: int = Field(..., description="Nombre total de requêtes")
    jarvis_response_time_seconds: float = Field(..., description="Temps de réponse moyen")
    jarvis_active_connections: int = Field(..., description="Connexions actives")
    jarvis_memory_usage_bytes: int = Field(..., description="Usage mémoire")
    jarvis_cpu_usage_percent: float = Field(..., description="Usage CPU")