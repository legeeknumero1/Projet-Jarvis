"""App Factory - Création et configuration de l'application FastAPI"""
import os
import json
import logging.config
from pathlib import Path
from fastapi import FastAPI
from contextlib import asynccontextmanager
from config import Settings
from utils.logging import configure_logging, get_logger
from utils.ws_manager import WSManager
from security.deps import setup_cors

# Import des services
from services import LLMService, MemoryService, VoiceService, WeatherService, HomeAssistantService

logger = logging.getLogger(__name__)

def _configure_logging_from_env():
    """Configuration logging depuis fichier JSON (production)"""
    cfg = os.getenv("JARVIS_LOG_CONFIG")
    if cfg and Path(cfg).is_file():
        try:
            with open(cfg, "r", encoding="utf-8") as f:
                logging.config.dictConfig(json.load(f))
            return True
        except Exception as e:
            print(f"⚠️ Erreur config logging {cfg}: {e}")
    return False

# Import métriques Prometheus (optionnel)
try:
    from prometheus_fastapi_instrumentator import Instrumentator
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logger.info("prometheus_fastapi_instrumentator non disponible - métriques désactivées")

@asynccontextmanager
async def lifespan_manager(app: FastAPI):
    """Gestionnaire du cycle de vie de l'application"""
    settings = app.state.settings
    
    # === STARTUP ===
    logger.info("🚀 [STARTUP] Jarvis Brain API démarrage...")
    
    # Initialisation Database (comme dans main.py original)
    from config.config import Config
    from db.database import Database
    config = Config()
    database = Database(config)
    
    # Initialiser les services
    app.state.llm = LLMService(settings)
    app.state.memory = MemoryService(settings)
    app.state.voice = VoiceService(settings)
    app.state.weather = WeatherService(settings)
    app.state.home_assistant = HomeAssistantService(settings)
    
    # Connexions async
    await app.state.llm.initialize()
    await app.state.memory.initialize(database)
    await app.state.voice.initialize()
    await app.state.weather.initialize()
    await app.state.home_assistant.initialize()
    
    logger.info("✅ [STARTUP] Services initialisés")
    
    yield
    
    # === SHUTDOWN ===
    logger.info("🛑 [SHUTDOWN] Arrêt graceful services...")
    
    # Mode drain : refuser nouvelles connexions
    app.state.draining = True
    logger.info("🚫 [SHUTDOWN] Mode drain activé - nouvelles connexions refusées")
    
    # Fermer connexions WebSocket avec manager
    await app.state.ws.close_all(code=1001, reason="Server shutdown")
    
    # Nettoyage services
    await app.state.llm.close()
    await app.state.voice.close()
    await app.state.home_assistant.close()
    
    logger.info("✅ [SHUTDOWN] Services arrêtés proprement")

def create_app(settings: Settings = None) -> FastAPI:
    """Factory pour créer l'application FastAPI"""
    settings = settings or Settings()
    
    # Configuration logging (prod JSON ou fallback dev) AVANT création loggers
    if not _configure_logging_from_env():
        configure_logging(settings)
    
    # Récupérer logger APRÈS configuration
    logger = get_logger(__name__)
    logger.info("🔧 [FACTORY] Création application FastAPI")
    
    # Création app avec lifespan
    app = FastAPI(
        title="Jarvis Brain API",
        version="1.1.0", 
        description="Assistant IA personnel avec mémoire contextuelle",
        lifespan=lifespan_manager
    )
    
    # === INJECTION DÉPENDANCES ===
    app.state.settings = settings
    
    # Manager WebSocket avec métriques intégrées
    app.state.ws = WSManager()
    app.state.draining = False  # Mode drain pour refuser nouvelles connexions
    
    # === MIDDLEWARES ===
    setup_cors(app, settings.allowed_origins)
    
    # Request-ID middleware production avec contextvars
    from middleware.request_context import RequestIdMiddleware
    app.add_middleware(RequestIdMiddleware)
    
    # === MÉTRIQUES PROMETHEUS ===
    if PROMETHEUS_AVAILABLE:
        instrumentator = Instrumentator()
        instrumentator.instrument(app).expose(app, endpoint="/metrics")
        logger.info("📊 [METRICS] Prometheus metrics activées sur /metrics")
    
    # === ROUTERS ===
    from routers.health import router as health_router
    from routers.chat import router as chat_router
    from routers.voice import router as voice_router
    from routers.websocket import router as websocket_router
    app.include_router(health_router, prefix="", tags=["health"])
    app.include_router(chat_router, prefix="/chat", tags=["chat"])
    app.include_router(voice_router, prefix="/voice", tags=["voice"])
    app.include_router(websocket_router, prefix="", tags=["websocket"])
    
    
    logger.info("🎯 [FACTORY] Application créée avec succès")
    return app

# Pour compatibilité avec uvicorn main:app
app = create_app()
