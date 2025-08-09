"""Router Health - endpoints de base et monitoring"""
from fastapi import APIRouter
from datetime import datetime
from ..schemas.common import HealthResponse, MetricsResponse

router = APIRouter()

@router.get("/", response_model=dict)
async def root():
    """Endpoint racine - extrait de main.py:312-313"""
    return {
        "message": "Jarvis AI Assistant is running",
        "version": "1.1.0-refactor",
        "status": "operational"
    }

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check - extrait de main.py:315-317"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="1.1.0-refactor"
    )

@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Endpoint Prometheus metrics - extrait de main.py:319-328"""
    # Note: active_connections sera accessible via app.state dans une vraie implémentation
    return MetricsResponse(
        jarvis_requests_total=42,  # TODO: vraies métriques
        jarvis_response_time_seconds=0.123,
        jarvis_active_connections=0,  # TODO: compter vraies connexions WS
        jarvis_memory_usage_bytes=123456789,
        jarvis_cpu_usage_percent=15.5
    )