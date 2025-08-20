from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, File, UploadFile, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
import uvicorn
import asyncio
import json
import logging
import io
import re
from typing import List, Dict, Any
import os
from datetime import datetime
from contextlib import asynccontextmanager

from config.config import Config
from db.database import Database
from memory.brain_memory_system import BrainMemorySystem
from profile.profile_manager import ProfileManager
from speech.speech_manager import SpeechManager
from integration.home_assistant import HomeAssistantIntegration
from integration.ollama_client import OllamaClient

# Configuration globale
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
config = Config()
db = Database(config)

# Variables globales pour les services
brain_memory_system = None
profile_manager = None
speech_manager = None
home_assistant = None
ollama_client = None
_services_initialized = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    global brain_memory_system, profile_manager, speech_manager, home_assistant, ollama_client, _services_initialized
    
    # Startup
    logging.info("🚀 [STARTUP] Jarvis démarrage...")
    
    # Initialisation des services globaux
    brain_memory_system = BrainMemorySystem(db)
    profile_manager = ProfileManager(db)
    speech_manager = SpeechManager(config)
    home_assistant = HomeAssistantIntegration(config)
    ollama_client = OllamaClient(base_url=config.ollama_base_url)
    
    # Vérification et initialisation base de données
    if db and hasattr(db, 'connect'):
        try:
            logging.info("📊 [DB] Connexion base de données...")
            await db.connect()
            logging.info("✅ [DB] Base de données connectée")
        except Exception as e:
            logging.error(f"❌ [DB] Erreur connexion: {e}")
    
    _services_initialized = True
    logging.info("✅ [STARTUP] Services initialisés")
    
    yield
    
    # Shutdown
    logging.info("🛑 [SHUTDOWN] Arrêt des services...")
    if db and hasattr(db, 'disconnect'):
        await db.disconnect()
    logging.info("✅ [SHUTDOWN] Services arrêtés")

# Application FastAPI
app = FastAPI(
    title="Jarvis API",
    description="Assistant IA Personnel - Version Simplifiée",
    version="2.0.0",
    lifespan=lifespan
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models Pydantic
class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)
    user_id: str = Field(default="default", max_length=100)

class ChatResponse(BaseModel):
    response: str
    timestamp: str
    user_id: str

# Endpoints principaux
@app.get("/")
async def root():
    """Point de santé de l'API"""
    return {"status": "Jarvis API v2.0 - Running", "timestamp": datetime.now().isoformat()}

@app.get("/health")
async def health_check():
    """Vérification de l'état des services"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "database": "ok" if db else "error",
            "ollama": "unknown",
            "brain_memory": "ok" if brain_memory_system else "error"
        }
    }
    
    # Test Ollama
    try:
        if ollama_client:
            await ollama_client.test_connection()
            health_status["services"]["ollama"] = "ok"
    except Exception as e:
        health_status["services"]["ollama"] = "error"
        logging.warning(f"Ollama connection check failed: {e}")
    
    return health_status

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_request: ChatMessage):
    """Endpoint principal pour les conversations - VERSION SIMPLIFIÉE"""
    try:
        logging.info(f"💬 [CHAT] Message reçu: {chat_request.message[:50]}...")
        
        # Traitement simplifié du message
        response_text = await process_message_simple(
            chat_request.message, 
            chat_request.user_id
        )
        
        return ChatResponse(
            response=response_text,
            timestamp=datetime.now().isoformat(),
            user_id=chat_request.user_id
        )
        
    except Exception as e:
        logging.error(f"❌ [CHAT] Erreur traitement: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur traitement message: {str(e)}")

async def process_message_simple(message: str, user_id: str = "default") -> str:
    """
    Traitement simplifié des messages - PLUS DE LOGIQUE HARDCODÉE
    Laisse Ollama répondre naturellement sans interférence
    """
    try:
        logging.info(f"🤖 [PROCESS] Traitement message pour user: {user_id}")
        
        # Récupération minimale du contexte mémoire
        context_memories = []
        if brain_memory_system:
            try:
                context_memories = await brain_memory_system.get_contextual_memories(user_id, message, limit=3)
            except Exception as e:
                logging.warning(f"⚠️ [MEMORY] Erreur récupération mémoire: {e}")
        
        # Préparation du contexte minimal pour Ollama
        context_text = ""
        if context_memories:
            context_text = "Contexte récent:\n" + "\n".join(context_memories) + "\n\n"
        
        # Appel direct à Ollama - SANS RÈGLES HARDCODÉES
        full_prompt = f"{context_text}Utilisateur: {message}"
        
        if not ollama_client:
            return "❌ Service IA non disponible"
        
        # Génération de la réponse par Ollama
        response = await ollama_client.generate_response(full_prompt)
        
        # Sauvegarde simple de l'interaction
        if brain_memory_system:
            try:
                await brain_memory_system.store_interaction(user_id, message, response)
            except Exception as e:
                logging.warning(f"⚠️ [MEMORY] Erreur sauvegarde: {e}")
        
        logging.info(f"✅ [PROCESS] Réponse générée: {len(response)} caractères")
        return response
        
    except Exception as e:
        logging.error(f"❌ [PROCESS] Erreur traitement: {e}")
        return f"❌ Désolé, une erreur s'est produite lors du traitement de votre message: {str(e)}"

# WebSocket pour communication temps réel
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket simplifié pour communication temps réel"""
    await websocket.accept()
    logging.info("🔌 [WS] Nouvelle connexion WebSocket")
    
    try:
        while True:
            # Recevoir le message
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            user_message = message_data.get("message", "")
            user_id = message_data.get("user_id", "default")
            
            if not user_message.strip():
                await websocket.send_text(json.dumps({
                    "error": "Message vide"
                }))
                continue
            
            logging.info(f"🔌 [WS] Message reçu: {user_message[:50]}...")
            
            # Traitement du message
            response_text = await process_message_simple(user_message, user_id)
            
            # Envoi de la réponse
            response_data = {
                "response": response_text,
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id
            }
            
            await websocket.send_text(json.dumps(response_data))
            logging.info(f"✅ [WS] Réponse envoyée")
            
    except WebSocketDisconnect:
        logging.info("🔌 [WS] Connexion fermée")
    except Exception as e:
        logging.error(f"❌ [WS] Erreur WebSocket: {e}")
        try:
            await websocket.close()
        except:
            pass

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("BACKEND_PORT", 8000)),
        reload=config.debug,
        log_level=config.log_level.lower()
    )