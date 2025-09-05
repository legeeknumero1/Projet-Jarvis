from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, File, UploadFile, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, PlainTextResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, Field, validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import uvicorn
import asyncio
import json
import logging
import io
import re
from typing import List, Dict, Any
import os
import time
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import Request

from config.config import Config
from config.secrets import secrets_manager
from db.database import Database
from memory.brain_memory_system import BrainMemorySystem
from profile.profile_manager import ProfileManager
from speech.speech_manager import SpeechManager
from integration.home_assistant import HomeAssistantIntegration
# Suppression import OllamaClient - utilisation bibliothèque officielle Ollama
from auth.dependencies import get_current_user, get_optional_current_user
from auth.models import User
from auth.routes import router as auth_router

# Configuration globale sécurisée
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
config = Config()
db = Database(config)

# Rate limiting sécurisé différencié
def get_user_identifier(request: Request) -> str:
    """Identifiant pour rate limiting basé sur user authentifié ou IP"""
    try:
        # Essayer d'extraire le user_id depuis le JWT token
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            from auth.dependencies import decode_jwt_token
            token = auth_header.split(" ")[1]
            payload = decode_jwt_token(token)
            if payload and payload.get("sub"):
                return f"user:{payload['sub']}"
    except:
        pass
    # Fallback sur l'IP
    return f"ip:{get_remote_address(request)}"

limiter = Limiter(key_func=get_user_identifier)

# Log security status
secrets_manager.log_security_status()

# Variables globales pour les services
brain_memory_system = None
profile_manager = None
speech_manager = None
home_assistant = None
# ollama_client = None  # Supprimé - utilisation directe bibliothèque officielle
_services_initialized = False

# Database monitoring
db_monitoring_middleware = None

# Métriques Prometheus simples
class Metrics:
    def __init__(self):
        self.requests_total = 0
        self.requests_errors = 0
        self.response_times = []
        self.active_connections = 0
        self.start_time = time.time()
    
    def increment_requests(self):
        self.requests_total += 1
    
    def increment_errors(self):
        self.requests_errors += 1
    
    def add_response_time(self, duration):
        self.response_times.append(duration)
        # Garder seulement les 100 dernières mesures
        if len(self.response_times) > 100:
            self.response_times = self.response_times[-100:]
    
    def get_avg_response_time(self):
        return sum(self.response_times) / len(self.response_times) if self.response_times else 0
    
    def get_uptime(self):
        return time.time() - self.start_time

metrics = Metrics()

@asynccontextmanager
async def lifespan(app: FastAPI):
    global brain_memory_system, profile_manager, speech_manager, home_assistant, _services_initialized, db_monitoring_middleware
    
    # Startup
    logging.info("🚀 [STARTUP] Jarvis démarrage...")
    
    # Initialisation des services globaux
    brain_memory_system = BrainMemorySystem(db)
    profile_manager = ProfileManager(db)
    speech_manager = SpeechManager(config)
    home_assistant = HomeAssistantIntegration(config)
    # ollama_client = OllamaClient(base_url=config.ollama_base_url)  # Supprimé - utilisation directe bibliothèque officielle
    
    # Vérification et initialisation base de données
    if db and hasattr(db, 'connect'):
        try:
            logging.info("📊 [DB] Connexion base de données...")
            await db.connect()
            logging.info("✅ [DB] Base de données connectée")
            
            # Initialiser monitoring de base de données
            from middleware.database_middleware import DatabaseMonitoringMiddleware
            from monitoring.query_monitor import db_monitor
            
            # Configurer le middleware de monitoring
            db_monitoring_middleware = DatabaseMonitoringMiddleware(db.engine)
            
            # Initialiser le pool d'analyse si URL disponible
            try:
                await db_monitor.initialize_analysis_pool(config.database_url)
                logging.info("✅ [DB] Monitoring des requêtes initialisé")
            except Exception as monitor_error:
                logging.warning(f"⚠️ [DB] Monitoring non disponible: {monitor_error}")
            
        except Exception as e:
            logging.error(f"❌ [DB] Erreur connexion: {e}")
    
    _services_initialized = True
    logging.info("✅ [STARTUP] Services initialisés")
    
    yield
    
    # Shutdown
    logging.info("🛑 [SHUTDOWN] Arrêt des services...")
    
    # Nettoyer le monitoring de base de données
    try:
        from monitoring.query_monitor import db_monitor
        await db_monitor.cleanup()
        logging.info("✅ [SHUTDOWN] Monitoring DB nettoyé")
    except Exception as e:
        logging.warning(f"⚠️ [SHUTDOWN] Erreur nettoyage monitoring: {e}")
    
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

# Configuration CORS sécurisée
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.secure_cors_origins,  # Utilise les origines validées
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],  # Spécifique, pas wildcard
    allow_headers=["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],  # Headers spécifiques
    expose_headers=["X-Total-Count", "X-Rate-Limit-Remaining", "X-Rate-Limit-Reset"]
)

# Trusted hosts sécurisé - Réactivé avec support Docker
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=[
        "localhost", "127.0.0.1", 
        "*.jarvis.local",
        # Docker network containers pour monitoring
        "jarvis_backend", "backend",
        "jarvis-backend",  # Nom Kubernetes
        # IPs spécifiques du réseau Docker Jarvis
        "172.20.0.8",   # Prometheus
        "172.20.0.1",   # Gateway
        "172.20.0.40",  # Backend IP
        # Prometheus et monitoring
        "jarvis_prometheus", "prometheus",
        "jarvis-prometheus",  # Nom Kubernetes
        "jarvis_grafana", "grafana",
        "jarvis-grafana",    # Nom Kubernetes
        # Nginx et autres services
        "nginx", "jarvis-nginx"
    ]
)

# Rate limiting middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Database monitoring middleware
from middleware.database_middleware import QueryAnalysisMiddleware
app.add_middleware(QueryAnalysisMiddleware)

# Inclure les routes d'authentification
app.include_router(auth_router)

# Inclure les routes de monitoring
from api.monitoring import router as monitoring_router
app.include_router(monitoring_router)

# app.include_router(search_router)  # Désactivé temporairement pour tester Ollama

# Models Pydantic
class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000, description="Message utilisateur")
    user_id: str = Field(default="default", max_length=100, pattern=r"^[a-zA-Z0-9_-]+$")
    
    @validator('message')
    def validate_message(cls, v):
        # Validation basique contre injection
        dangerous_patterns = ['<script', 'javascript:', 'data:', 'vbscript:', 'onload=', 'onerror=']
        v_lower = v.lower()
        for pattern in dangerous_patterns:
            if pattern in v_lower:
                raise ValueError('Message contains potentially dangerous content')
        return v.strip()

class ChatResponse(BaseModel):
    response: str
    timestamp: str
    user_id: str

# Endpoints principaux
@app.get("/")
@limiter.limit("60/minute")  # Rate limiting public endpoints
async def root(request: Request):
    """Point de santé de l'API"""
    return {"status": "Jarvis API v2.0 - Running", "timestamp": datetime.now().isoformat()}

@app.get("/health")
@limiter.limit("120/minute")  # Rate limiting santé - plus permissif
async def health_check(request: Request):
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
    
    # Test Ollama avec meilleures pratiques 2025 selon recherche internet
    try:
        import ollama
        import time
        
        # Configuration client optimisée selon standards 2025
        client = ollama.Client(
            host='http://ollama:11434',
            headers={'User-Agent': 'Jarvis-HealthCheck/1.3.1'}
        )
        
        # Health check robuste avec timeout selon meilleures pratiques
        start_time = time.time()
        models = client.list()
        check_duration = time.time() - start_time
        
        # Validation approfondie selon standards internet 2025
        if isinstance(models, dict) and 'models' in models:
            available_models = models['models']
            if len(available_models) > 0:
                # Vérifier présence du modèle requis
                model_names = [model.get('name', '') for model in available_models]
                if 'llama3.2:1b' in model_names:
                    health_status["services"]["ollama"] = "ok"
                    logging.info(f"✅ [HEALTH] Ollama OK - {len(available_models)} modèle(s), llama3.2:1b disponible ({check_duration:.2f}s)")
                else:
                    health_status["services"]["ollama"] = "warning"
                    logging.warning(f"⚠️ [HEALTH] Ollama API OK mais modèle llama3.2:1b manquant dans: {model_names}")
            else:
                health_status["services"]["ollama"] = "error"
                logging.warning("⚠️ [HEALTH] Ollama API répond mais aucun modèle disponible")
        else:
            health_status["services"]["ollama"] = "error"
            logging.warning(f"⚠️ [HEALTH] Ollama réponse invalide: {type(models)}")
            
    except Exception as e:
        health_status["services"]["ollama"] = "error"
        error_type = type(e).__name__
        logging.warning(f"❌ [HEALTH] Ollama health check échoué ({error_type}): {str(e)[:100]}...")
    
    return health_status

@app.get("/metrics")
@limiter.limit("10/minute")  # Rate limiting metrics - restrictif
async def prometheus_metrics(request: Request):
    """Endpoint pour les métriques Prometheus"""
    # Get current health status
    current_health = await health_check()
    
    ollama_status = 1 if current_health.get("services", {}).get("ollama") == "ok" else 0
    db_status = 1 if current_health.get("services", {}).get("database") == "ok" else 0
    memory_status = 1 if current_health.get("services", {}).get("brain_memory") == "ok" else 0
    
    metrics_text = f"""# HELP jarvis_requests_total Total number of requests
# TYPE jarvis_requests_total counter
jarvis_requests_total {metrics.requests_total}

# HELP jarvis_requests_errors_total Total number of request errors
# TYPE jarvis_requests_errors_total counter
jarvis_requests_errors_total {metrics.requests_errors}

# HELP jarvis_response_time_seconds Average response time in seconds
# TYPE jarvis_response_time_seconds gauge
jarvis_response_time_seconds {metrics.get_avg_response_time():.3f}

# HELP jarvis_uptime_seconds Uptime in seconds
# TYPE jarvis_uptime_seconds gauge
jarvis_uptime_seconds {metrics.get_uptime():.0f}

# HELP jarvis_active_connections Current active WebSocket connections
# TYPE jarvis_active_connections gauge
jarvis_active_connections {metrics.active_connections}

# HELP jarvis_service_status Service status (1=up, 0=down)
# TYPE jarvis_service_status gauge
jarvis_service_status{{service="ollama"}} {ollama_status}
jarvis_service_status{{service="database"}} {db_status}
jarvis_service_status{{service="memory"}} {memory_status}
"""
    
    return PlainTextResponse(content=metrics_text, media_type="text/plain")

@app.post("/chat", response_model=ChatResponse)
@limiter.limit("30/minute")  # Rate limiting différencié: 30 req/min pour users authentifiés
async def chat_endpoint(
    request: Request,  # Nécessaire pour rate limiting
    chat_request: ChatMessage,
    current_user: User = Depends(get_current_user)  # Authentification JWT OBLIGATOIRE selon audit 2025
):
    """Endpoint principal pour les conversations - SÉCURISÉ JWT"""
    start_time = time.time()
    metrics.increment_requests()
    
    try:
        logging.info(f"💬 [CHAT] Message reçu de {current_user.username}: {chat_request.message[:50]}...")
        
        # Traitement message avec utilisateur authentifié
        response_text = await process_message_simple(
            chat_request.message, 
            current_user.username  # Utiliser username authentifié au lieu de user_id fourni
        )
        
        # Track response time
        duration = time.time() - start_time
        metrics.add_response_time(duration)
        
        return ChatResponse(
            response=response_text,
            timestamp=datetime.now().isoformat(),
            user_id=chat_request.user_id
        )
        
    except Exception as e:
        metrics.increment_errors()
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
        
        # Préparation du contexte minimal pour Ollama - FIX: Gestion dict/str selon recherche internet 2025
        context_text = ""
        if context_memories:
            # Conversion sécurisée des mémoires selon meilleures pratiques
            context_list = []
            for memory in context_memories:
                if isinstance(memory, dict):
                    # Extraire le contenu textuel des dictionnaires
                    memory_text = memory.get('content', '') or memory.get('text', '') or str(memory)
                elif isinstance(memory, str):
                    memory_text = memory
                else:
                    memory_text = str(memory)
                context_list.append(memory_text)
            context_text = "Contexte récent:\n" + "\n".join(context_list) + "\n\n"
        
        # Appel direct à Ollama - SANS RÈGLES HARDCODÉES
        full_prompt = f"{context_text}Utilisateur: {message}"
        
        # Vérification Ollama via bibliothèque officielle (plus de client custom)
        
        # Génération de la réponse par Ollama - BEST PRACTICES 2025 SELON RECHERCHE INTERNET
        try:
            import ollama
            import json
            import time
            import asyncio
            
            logging.info(f"🤖 [OLLAMA] Génération avec modèle llama3.2:1b")
            logging.info(f"📝 [OLLAMA] Prompt: {full_prompt[:100]}...")
            
            # Configuration client officielle Ollama optimisée 2025 (selon recherche internet)
            client = ollama.Client(
                host='http://ollama:11434',
                headers={
                    'User-Agent': 'Jarvis-Backend/1.3.1',
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            )
            
            # Vérification préalable de la disponibilité selon meilleures pratiques 2025
            health_check_attempts = 3
            health_check_success = False
            
            for health_attempt in range(health_check_attempts):
                try:
                    models_check = client.list()
                    if isinstance(models_check, dict) and 'models' in models_check:
                        available_models = models_check.get('models', [])
                        logging.info(f"✅ [OLLAMA] Connexion saine, {len(available_models)} modèle(s) disponible(s)")
                        
                        # Vérifier que le modèle requis est disponible
                        model_names = [model.get('name', '') for model in available_models]
                        if 'llama3.2:1b' in model_names:
                            logging.info(f"✅ [OLLAMA] Modèle llama3.2:1b confirmé disponible")
                            health_check_success = True
                            break
                        else:
                            logging.warning(f"⚠️ [OLLAMA] Modèle llama3.2:1b non trouvé dans: {model_names}")
                except Exception as e:
                    if health_attempt < health_check_attempts - 1:
                        delay = 2 ** health_attempt  # 1s, 2s, 4s
                        logging.warning(f"⚠️ [OLLAMA] Health check {health_attempt+1}/{health_check_attempts} échoué: {str(e)[:80]}...")
                        logging.warning(f"⏳ [OLLAMA] Retry health check dans {delay}s...")
                        time.sleep(delay)
                    else:
                        logging.warning(f"⚠️ [OLLAMA] Tous les health checks échoués, tentative génération directe")
            
            # Pattern retry robuste optimisé selon standards internet 2025
            max_retries = 7  # Augmenté selon recommandations Docker networking 2025
            base_delay = 0.5  # Délai initial réduit pour réactivité
            max_delay = 16   # Délai maximum pour éviter timeouts trop longs
            response_data = None
            
            for attempt in range(max_retries):
                try:
                    # Configuration génération optimisée selon meilleures pratiques 2025
                    response_data = client.generate(
                        model="llama3.2:1b", 
                        prompt=full_prompt,
                        options={
                            'temperature': 0.7,
                            'top_p': 0.9,
                            'num_ctx': 2048,  # Context window optimisé
                            'num_predict': 256  # Limite tokens pour performance
                        }
                    )
                    
                    logging.info(f"✅ [OLLAMA] Génération réussie à la tentative {attempt + 1}")
                    break  # Si succès, sortir immédiatement
                    
                except Exception as e:
                    if attempt < max_retries - 1:
                        # Exponential backoff avec jitter selon best practices 2025
                        delay = min(base_delay * (2 ** attempt), max_delay)
                        jitter = delay * 0.1 * (time.time() % 1)  # Random jitter 0-10%
                        final_delay = delay + jitter
                        
                        error_type = type(e).__name__
                        logging.warning(f"🔄 [OLLAMA] Tentative {attempt + 1}/{max_retries} échouée ({error_type}): {str(e)[:100]}...")
                        logging.warning(f"⏳ [OLLAMA] Retry dans {final_delay:.1f}s (exponential backoff + jitter)...")
                        time.sleep(final_delay)
                    else:
                        logging.error(f"❌ [OLLAMA] Échec définitif après {max_retries} tentatives robustes")
                        raise e  # Relancer pour gestion d'erreur appropriée
            
            # Vérification que response_data existe après retry
            if response_data is None:
                logging.error("❌ [OLLAMA] Aucune réponse obtenue après tous les retries")
                return "❌ Service temporairement indisponible. Veuillez réessayer dans quelques secondes."
            
            logging.info(f"📊 [OLLAMA] Response raw data: {response_data}")
            
            # Extraire la réponse de la structure officielle (debug enhanced)
            if isinstance(response_data, dict):
                response = response_data.get('response', '')
                done = response_data.get('done', False)
                done_reason = response_data.get('done_reason', 'unknown')
                
                logging.info(f"✅ [OLLAMA] Response extracted: '{response}', done: {done}, reason: {done_reason}")
            else:
                response = str(response_data)
                logging.info(f"✅ [OLLAMA] Response direct: {response}")
            
            # Validation de la réponse selon standards 2025
            if not response or response.strip() == "":
                logging.error("❌ [OLLAMA] Réponse vide ou null")
                logging.error(f"❌ [OLLAMA] Raw data debug: {json.dumps(response_data, indent=2) if isinstance(response_data, dict) else response_data}")
                return "❌ Désolé, je n'ai pas pu générer de réponse. Veuillez réessayer."
                
        except ollama.ResponseError as e:
            logging.error(f"❌ [OLLAMA] ResponseError: {e.error}, status: {e.status_code}")
            if e.status_code == 404:
                logging.info("🔄 [OLLAMA] Modèle non trouvé, tentative de téléchargement...")
                try:
                    client.pull("llama3.2:1b")
                    response_data = client.generate(model="llama3.2:1b", prompt=full_prompt)
                    response = response_data.get('response', '') if isinstance(response_data, dict) else str(response_data)
                except Exception as retry_error:
                    logging.error(f"❌ [OLLAMA] Retry failed: {retry_error}")
                    return f"❌ Erreur téléchargement modèle: {str(retry_error)}"
            else:
                return f"❌ Erreur API Ollama: {e.error}"
        except Exception as ollama_error:
            logging.error(f"❌ [OLLAMA] Erreur génération: {ollama_error}")
            return f"❌ Erreur IA: {str(ollama_error)}"
        
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

# WebSocket pour communication temps réel - SÉCURISÉ JWT SELON MEILLEURES PRATIQUES 2025
@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket
):
    """WebSocket sécurisé JWT via Authorization header selon meilleures pratiques sécurité 2025"""
    
    # 1. Extraction token JWT depuis Authorization header - SÉCURISÉ
    token = None
    try:
        auth_header = websocket.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    except Exception:
        pass
    
    if not token:
        logging.warning("🚨 [WS] Tentative connexion sans token JWT")
        await websocket.close(code=4001, reason="Token JWT requis")
        return
    
    try:
        # Import de la validation JWT
        from auth.security import SecurityManager
        security = SecurityManager(config.jarvis_secret_key)
        
        # Validation du token JWT selon standards 2025
        username = security.verify_token(token)
        if not username:
            logging.warning("🚨 [WS] Token JWT invalide ou expiré")
            await websocket.close(code=4003, reason="Token JWT invalide")
            return
            
        logging.info(f"✅ [WS] Authentification JWT réussie pour utilisateur: {username}")
        
    except Exception as e:
        logging.error(f"🚨 [WS] Erreur validation JWT: {e}")
        await websocket.close(code=4002, reason="Erreur authentification")
        return
    
    # 2. Accepter connexion APRÈS validation sécurisée
    await websocket.accept()
    logging.info(f"🔌 [WS] Connexion WebSocket sécurisée acceptée - Utilisateur: {username}")
    
    connection_id = id(websocket)
    metrics.active_connections += 1
    
    async def connection_probe():
        """Sonde de connexion selon best practices 2025 pour détecter les déconnexions"""
        try:
            await asyncio.wait_for(websocket.receive_text(), timeout=0.001)
        except asyncio.TimeoutError:
            pass  # Timeout normal, connexion active
        except Exception:
            raise WebSocketDisconnect()  # Connexion fermée détectée
    
    try:
        while True:
            # Probe périodique de l'état de connexion selon recherche internet 2025
            try:
                await connection_probe()
            except WebSocketDisconnect:
                logging.warning("🔌 [WS] Déconnexion détectée via probe")
                break
            
            # Recevoir le message avec timeout robuste
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(), 
                    timeout=300  # 5 minutes timeout selon standards 2025
                )
                message_data = json.loads(data)
            except asyncio.TimeoutError:
                # Ping keepalive selon meilleures pratiques
                try:
                    await websocket.send_text(json.dumps({"type": "ping"}))
                    continue
                except Exception:
                    logging.warning("🔌 [WS] Échec ping keepalive")
                    break
            except json.JSONDecodeError as e:
                logging.warning(f"🔌 [WS] JSON invalide: {e}")
                await websocket.send_text(json.dumps({
                    "error": "Format JSON invalide"
                }))
                continue
            
            user_message = message_data.get("message", "")
            user_id = message_data.get("user_id", "default")
            
            if not user_message.strip():
                await websocket.send_text(json.dumps({
                    "error": "Message vide"
                }))
                continue
            
            logging.info(f"🔌 [WS] Message reçu (conn {connection_id}): {user_message[:50]}...")
            
            # Traitement du message avec timeout pour éviter blocage
            try:
                response_text = await asyncio.wait_for(
                    process_message_simple(user_message, user_id),
                    timeout=120  # 2 minutes max pour éviter déconnexions
                )
            except asyncio.TimeoutError:
                logging.error(f"⏱️ [WS] Timeout traitement message")
                await websocket.send_text(json.dumps({
                    "error": "Timeout de traitement - message trop complexe",
                    "timestamp": datetime.now().isoformat()
                }))
                continue
            
            # Envoi de la réponse avec vérification connexion
            response_data = {
                "response": response_text,
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id
            }
            
            try:
                await websocket.send_text(json.dumps(response_data))
                logging.info(f"✅ [WS] Réponse envoyée (conn {connection_id})")
            except Exception as e:
                logging.warning(f"❌ [WS] Échec envoi réponse: {e}")
                break  # Connexion fermée
            
    except WebSocketDisconnect:
        logging.info(f"🔌 [WS] Déconnexion normale (conn {connection_id})")
    except Exception as e:
        logging.error(f"❌ [WS] Erreur WebSocket (conn {connection_id}): {e}")
    finally:
        # Cleanup robuste selon meilleures pratiques 2025
        metrics.active_connections = max(0, metrics.active_connections - 1)
        try:
            if websocket.client_state.name != 'DISCONNECTED':
                await websocket.close(code=1000, reason="Server cleanup")
        except Exception as cleanup_error:
            logging.debug(f"🔧 [WS] Cleanup error (attendu): {cleanup_error}")
        logging.info(f"🔌 [WS] Connexion fermée proprement (conn {connection_id})")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("BACKEND_PORT", 8000)),
        reload=config.debug,
        log_level=config.log_level.lower()
    )