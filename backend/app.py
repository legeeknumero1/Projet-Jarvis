"""App Factory - Création et configuration de l'application FastAPI"""
from fastapi import FastAPI
from contextlib import asynccontextmanager
from .config import Settings
from .utils.logging import configure_logging, get_logger
from .security.deps import setup_cors

# Import des services
from .services import LLMService, MemoryService, VoiceService, WeatherService, HomeAssistantService

logger = get_logger(__name__)

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
    logger.info("🛑 [SHUTDOWN] Arrêt services...")
    
    # Nettoyage async
    await app.state.llm.close()
    await app.state.home_assistant.close()
    
    logger.info("✅ [SHUTDOWN] Services arrêtés proprement")

def create_app(settings: Settings = None) -> FastAPI:
    """Factory pour créer l'application FastAPI"""
    settings = settings or Settings()
    
    # Configuration logging en premier
    configure_logging(settings)
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
    
    # TODO: Ajouter singletons services dans étapes suivantes
    # app.state.llm = None  # sera créé dans lifespan
    # app.state.memory = None
    # etc.
    
    # === MIDDLEWARES ===
    setup_cors(app, settings.allowed_origins)
    
    # === ROUTERS ===
    from .routers import health, chat, voice, websocket
    app.include_router(health.router, prefix="", tags=["health"])
    app.include_router(chat.router, prefix="/chat", tags=["chat"])
    app.include_router(voice.router, prefix="/voice", tags=["voice"])
    app.include_router(websocket.router, prefix="", tags=["websocket"])
    
    
    logger.info("🎯 [FACTORY] Application créée avec succès")
    return app

# Pour compatibilité avec uvicorn main:app
app = create_app()