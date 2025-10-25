"""Router Health - endpoints de base et monitoring"""
from fastapi import APIRouter, Request, HTTPException
from datetime import datetime
from schemas.common import HealthResponse, MetricsResponse
from utils.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

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
    """Liveness probe - processus vivant"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="1.2.0-hardened"
    )

@router.get("/ready")
async def readiness_check(request: Request):
    """Readiness probe - services externes disponibles"""
    try:
        services_status = {}
        all_ready = True
        
        # Check Ollama LLM
        if hasattr(request.app.state, 'llm'):
            llm_ready = await request.app.state.llm.ping()
            services_status["llm"] = llm_ready
            all_ready = all_ready and llm_ready
        
        # Check Voice services (STT/TTS)  
        if hasattr(request.app.state, 'voice'):
            voice_ready = await request.app.state.voice.ping()
            services_status["voice"] = voice_ready
            all_ready = all_ready and voice_ready
        
        # Check Home Assistant (optionnel)
        if hasattr(request.app.state, 'home_assistant'):
            try:
                ha_ready = await request.app.state.home_assistant.ping()
                services_status["home_assistant"] = ha_ready
                # HA n'est pas critique pour readiness
            except:
                services_status["home_assistant"] = False
        
        # Check Memory service
        if hasattr(request.app.state, 'memory'):
            memory_ready = request.app.state.memory.is_available()
            services_status["memory"] = memory_ready
            all_ready = all_ready and memory_ready
        
        status_code = 200 if all_ready else 503
        
        return {
            "ready": all_ready,
            "services": services_status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ [READY] Erreur readiness check: {e}")
        raise HTTPException(status_code=503, detail="Readiness check failed")

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