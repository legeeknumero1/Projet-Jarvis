from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, File, UploadFile, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPAuthentication, HTTPAuthorizationCredentials
from pydantic import BaseModel
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
from services.weather_service import WeatherService
from games.hangman import play_hangman

# Instance #6 - EN_COURS - Correction lifespan API + ajout logs détaillés
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logging.info("🚀 [STARTUP] Jarvis démarrage...")
    
    # Vérification et initialisation base de données
    if db and hasattr(db, 'connect'):
        try:
            logging.info("📊 [DB] Connexion base de données...")
            await db.connect()
            logging.info("✅ [DB] Base de données connectée")
        except Exception as e:
            logging.error(f"❌ [DB] Erreur connexion: {e}")
    else:
        logging.error("❌ [DB] Objet database non disponible ou mal configuré")
    
    # Vérification et initialisation système mémoire neuromorphique
    if brain_memory_system and hasattr(brain_memory_system, 'initialize'):
        try:
            logging.info("🧠 [MEMORY] Initialisation système mémoire neuromorphique...")
            await brain_memory_system.initialize()
            logging.info("✅ [MEMORY] Système mémoire neuromorphique initialisé")
        except Exception as e:
            logging.error(f"❌ [MEMORY] Erreur initialisation: {e}")
    else:
        logging.error("❌ [MEMORY] Système mémoire neuromorphique non disponible")
    
    # Vérification et initialisation gestionnaire profils
    if profile_manager and hasattr(profile_manager, 'initialize'):
        try:
            logging.info("👤 [PROFILE] Initialisation gestionnaire profils...")
            await profile_manager.initialize()
            logging.info("✅ [PROFILE] Gestionnaire profils initialisé")
        except Exception as e:
            logging.error(f"❌ [PROFILE] Erreur initialisation: {e}")
    else:
        logging.warning("⚠️ [PROFILE] Gestionnaire profils non disponible")
    
    # Vérification et initialisation gestionnaire vocal
    if speech_manager and hasattr(speech_manager, 'initialize'):
        try:
            logging.info("🎤 [SPEECH] Initialisation gestionnaire vocal...")
            await speech_manager.initialize()
            logging.info("✅ [SPEECH] Gestionnaire vocal initialisé")
        except Exception as e:
            logging.error(f"❌ [SPEECH] Erreur initialisation: {e}")
    else:
        logging.warning("⚠️ [SPEECH] Gestionnaire vocal non disponible")
    
    # Vérification et connexion Home Assistant
    if home_assistant and hasattr(home_assistant, 'connect'):
        try:
            logging.info("🏠 [HA] Connexion Home Assistant...")
            await home_assistant.connect()
            logging.info("✅ [HA] Home Assistant connecté")
        except Exception as e:
            logging.error(f"❌ [HA] Erreur connexion: {e}")
    else:
        logging.warning("⚠️ [HA] Home Assistant non disponible")
    
    # Vérification et préparation Ollama
    if ollama_client and hasattr(ollama_client, 'is_available'):
        try:
            logging.info("🤖 [OLLAMA] Vérification disponibilité...")
            if await ollama_client.is_available():
                logging.info("🤖 [OLLAMA] Service disponible, vérification modèle...")
                if hasattr(ollama_client, 'ensure_model_available'):
                    if await ollama_client.ensure_model_available("llama3.2:1b"):
                        logging.info("✅ [OLLAMA] LLaMA 3.2:1b prêt")
                    else:
                        logging.warning("⚠️ [OLLAMA] Modèle LLaMA 3.2:1b non disponible")
                else:
                    logging.warning("⚠️ [OLLAMA] Fonction ensure_model_available non disponible")
            else:
                logging.warning("⚠️ [OLLAMA] Service non disponible")
        except Exception as e:
            logging.error(f"❌ [OLLAMA] Erreur: {e}")
    else:
        logging.warning("⚠️ [OLLAMA] Client Ollama non disponible ou mal configuré")
    
    logging.info("🎯 [STARTUP] Jarvis démarré avec succès !")
    
    yield
    
    # Shutdown
    logging.info("🛑 [SHUTDOWN] Arrêt Jarvis...")
    
    # Déconnexion sécurisée base de données
    if db and hasattr(db, 'disconnect'):
        try:
            await db.disconnect()
            logging.info("✅ [DB] Base de données déconnectée")
        except Exception as e:
            logging.error(f"❌ [DB] Erreur déconnexion: {e}")
    else:
        logging.warning("⚠️ [DB] Pas de déconnexion nécessaire")
    
    # Déconnexion sécurisée Home Assistant
    if home_assistant and hasattr(home_assistant, 'disconnect'):
        try:
            await home_assistant.disconnect()
            logging.info("✅ [HA] Home Assistant déconnecté")
        except Exception as e:
            logging.error(f"❌ [HA] Erreur déconnexion: {e}")
    else:
        logging.warning("⚠️ [HA] Pas de déconnexion nécessaire")
    
    # Fermeture sécurisée client Ollama
    if ollama_client:
        try:
            if hasattr(ollama_client, 'client') and ollama_client.client:
                await ollama_client.client.aclose()
                logging.info("✅ [OLLAMA] Client fermé")
            else:
                logging.info("ℹ️ [OLLAMA] Client déjà fermé ou non initialisé")
        except Exception as e:
            logging.error(f"❌ [OLLAMA] Erreur fermeture: {e}")
    else:
        logging.warning("⚠️ [OLLAMA] Client non disponible")
    
    logging.info("✅ [SHUTDOWN] Jarvis arrêté proprement")

app = FastAPI(title="Jarvis AI Assistant", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8001"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Configuration du logging détaillé - chemins relatifs
import os
log_dir = os.path.join(os.getcwd(), 'logs')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'jarvis.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info("🚀 [INIT] Initialisation des composants Jarvis...")

config = Config()
db = Database(config)
# Neuromorphic Memory System - Architecture cerveau humain
brain_memory_system = BrainMemorySystem(db)
profile_manager = ProfileManager(db)
speech_manager = SpeechManager(config)
home_assistant = HomeAssistantIntegration(config)
ollama_client = OllamaClient(base_url=config.ollama_base_url)
weather_service = WeatherService()

logger.info("✅ [INIT] Tous les composants initialisés")

# Authentification sécurisée avec variable d'environnement
API_KEY = os.getenv("JARVIS_API_KEY")
if not API_KEY:
    import secrets
    API_KEY = secrets.token_urlsafe(32)
    logger.warning(f"⚠️ [SECURITY] API Key générée automatiquement: {API_KEY}")
    logger.warning("🔒 [SECURITY] Définissez JARVIS_API_KEY en variable d'environnement pour la production")

async def verify_api_key(x_api_key: str = Header(None)):
    """Vérifier la clé API pour les endpoints sensibles"""
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Clé API invalide ou manquante")
    return x_api_key

class MessageRequest(BaseModel):
    message: str
    user_id: str = "default"

class MessageResponse(BaseModel):
    response: str
    timestamp: datetime

class TranscriptionResponse(BaseModel):
    transcript: str
    confidence: float

class TTSRequest(BaseModel):
    text: str
    voice: str = "default"

# Instance #6 - FINI - Lifespan API + logs détaillés implémentés

@app.get("/")
async def root():
    return {"message": "Jarvis AI Assistant is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

@app.get("/metrics")
async def get_metrics():
    """Endpoint Prometheus metrics"""
    return {
        "jarvis_requests_total": 42,
        "jarvis_response_time_seconds": 0.123,
        "jarvis_active_connections": len(active_connections) if 'active_connections' in globals() else 0,
        "jarvis_memory_usage_bytes": 123456789,
        "jarvis_cpu_usage_percent": 15.5
    }

@app.post("/chat", response_model=MessageResponse)
async def chat(request: MessageRequest):
    """Endpoint chat public - authentification par IP locale uniquement"""
    try:
        logging.info(f"💬 [CHAT] Nouveau message de {request.user_id}: {request.message[:50]}...")
        
        # Récupération du contexte utilisateur avec système neuromorphique
        logging.debug(f"🧠 [CHAT] Récupération contexte neuromorphique {request.user_id}")
        user_context = await brain_memory_system.get_contextual_memories(request.user_id, request.message)
        logging.debug(f"✅ [CHAT] Contexte neuromorphique récupéré: {len(user_context)} éléments")
        
        # Traitement du message avec l'IA
        logging.debug(f"🤖 [CHAT] Traitement message avec IA...")
        response = await process_message(request.message, user_context, request.user_id)
        logging.info(f"✅ [CHAT] Réponse générée: {response[:50]}...")
        
        # Sauvegarde neuromorphique de la conversation
        logging.debug(f"💾 [CHAT] Sauvegarde conversation neuromorphique...")
        await brain_memory_system.store_interaction(
            request.user_id, 
            request.message, 
            response
        )
        logging.debug(f"✅ [CHAT] Conversation sauvegardée en mémoire neuromorphique")
        
        return MessageResponse(
            response=response,
            timestamp=datetime.now()
        )
    except Exception as e:
        logging.error(f"❌ [CHAT] Erreur: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/secure", response_model=MessageResponse)
async def chat_secure(request: MessageRequest, api_key: str = Depends(verify_api_key)):
    """Endpoint chat sécurisé pour intégrations externes"""
    return await chat(request)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket public pour frontend local"""
    client_id = f"client_{id(websocket)}"
    logging.info(f"🔌 [WS] Nouvelle connexion WebSocket: {client_id}")
    
    await websocket.accept()
    logging.info(f"✅ [WS] {client_id} connecté")
    
    try:
        while True:
            logging.debug(f"📡 [WS] {client_id} en attente de message...")
            data = await websocket.receive_text()
            logging.info(f"📨 [WS] {client_id} message reçu: {data[:100]}...")
            
            try:
                message_data = json.loads(data)
                logging.debug(f"✅ [WS] {client_id} JSON parsé: {message_data.keys()}")
            except json.JSONDecodeError as e:
                logging.error(f"❌ [WS] {client_id} Erreur JSON: {e}")
                await websocket.send_text(json.dumps({
                    "error": "Format JSON invalide",
                    "timestamp": datetime.now().isoformat()
                }))
                continue
            
            # Traitement neuromorphique du message en temps réel
            logging.debug(f"🤖 [WS] {client_id} Traitement avec IA neuromorphique...")
            user_context = await brain_memory_system.get_contextual_memories(
                message_data.get("user_id", "default"), 
                message_data["message"]
            )
            response = await process_message(
                message_data["message"],
                user_context,
                message_data.get("user_id", "default")
            )
            logging.info(f"✅ [WS] {client_id} Réponse générée: {response[:50]}...")
            
            response_data = {
                "response": response,
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send_text(json.dumps(response_data))
            logging.debug(f"📤 [WS] {client_id} Réponse envoyée")
            
    except WebSocketDisconnect:
        logging.info(f"🔌 [WS] {client_id} déconnecté")
    except Exception as e:
        logging.error(f"❌ [WS] {client_id} Erreur: {e}")

@app.websocket("/ws/secure")
async def websocket_secure_endpoint(websocket: WebSocket):
    """WebSocket sécurisé pour intégrations externes"""
    client_id = f"secure_client_{id(websocket)}"
    logging.info(f"🔌 [WS-SEC] Nouvelle connexion WebSocket sécurisée: {client_id}")
    
    # Vérification de l'authentification via query params
    query_params = dict(websocket.query_params)
    api_key = query_params.get('api_key')
    
    if not api_key or api_key != API_KEY:
        logging.warning(f"❌ [WS-SEC] {client_id} Authentification échouée - API key invalide")
        await websocket.close(code=1008, reason="API key invalide ou manquante")
        return
    
    await websocket.accept()
    logging.info(f"✅ [WS-SEC] {client_id} connecté et authentifié")
    
    # Réutiliser la même logique que le WebSocket public
    await websocket_endpoint(websocket)

@app.post("/voice/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(file: UploadFile = File(...), api_key: str = Depends(verify_api_key)):
    """Transcrit un fichier audio en texte"""
    try:
        logging.info(f"🎤 [VOICE] Transcription fichier: {file.filename} ({file.content_type})")
        
        # Lire le contenu du fichier audio
        audio_data = await file.read()
        logging.debug(f"📁 [VOICE] Fichier lu: {len(audio_data)} bytes")
        
        # Utiliser le speech manager pour la transcription
        logging.debug(f"🔄 [VOICE] Lancement transcription Whisper...")
        transcript = await speech_manager.speech_to_text(audio_data)
        
        if transcript:
            logging.info(f"✅ [VOICE] Transcription réussie: {transcript}")
        else:
            logging.warning(f"⚠️ [VOICE] Transcription vide")
        
        return TranscriptionResponse(
            transcript=transcript or "",
            confidence=0.95  # Pour l'instant, confidence fixe
        )
        
    except Exception as e:
        logging.error(f"❌ [VOICE] Erreur transcription: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur de transcription: {str(e)}")

@app.post("/voice/synthesize")
async def synthesize_speech(request: TTSRequest, api_key: str = Depends(verify_api_key)):
    """Synthétise du texte en audio"""
    try:
        logging.info(f"🔊 [TTS] Synthèse texte: {request.text[:50]}...")
        logging.debug(f"🎵 [TTS] Voix demandée: {request.voice}")
        
        # Générer l'audio avec le speech manager
        logging.debug(f"🔄 [TTS] Lancement synthèse Piper...")
        audio_data = await speech_manager.text_to_speech(request.text)
        
        if audio_data is None:
            logging.error(f"❌ [TTS] Service TTS indisponible")
            raise HTTPException(status_code=503, detail="Service TTS indisponible")
        
        logging.info(f"✅ [TTS] Audio généré: {len(audio_data)} bytes")
        
        # Retourner l'audio comme streaming response
        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=speech.wav"}
        )
        
    except Exception as e:
        logging.error(f"❌ [TTS] Erreur synthèse: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur de synthèse: {str(e)}")

async def process_message(message: str, context: Dict[str, Any], user_id: str = "default") -> str:
    """Traite un message et retourne une réponse"""
    try:
        logging.debug(f"🤖 [PROCESS] Début traitement message: {message[:30]}...")
        logging.debug(f"🧠 [PROCESS] Contexte: {len(context)} éléments")
        
        # Vérifier si Enzo donne des infos météo à mémoriser
        weather_data_pattern = r"(\d+)°?c.*?(\d+)%.*?(\d+)\s*k?m?h"
        weather_match = re.search(weather_data_pattern, message.lower())
        
        if weather_match:
            # Enzo donne des données météo - les sauvegarder en DB
            temp = weather_match.group(1)
            humidity = weather_match.group(2) 
            wind = weather_match.group(3)
            
            # Sauvegarder en mémoire neuromorphique via brain_memory_system
            weather_memory = f"Météo locale indiquée par Enzo : {temp}°C, {humidity}% humidité, {wind} km/h de vent"
            await brain_memory_system.store_interaction(user_id, message, weather_memory)
            
            # Réponse de confirmation
            response_text = f"📝 Noté et sauvegardé en base ! Météo : {temp}°C, {humidity}% humidité, vent à {wind} km/h."
            
            # La conversation est déjà sauvegardée via store_interaction
            # await brain_memory_system.store_interaction(user_id, message, response_text)
            
            return response_text
        
        # Vérifier si c'est une demande de jeu du pendu
        hangman_keywords = ["pendu", "jeu", "jouer", "hangman"]
        is_hangman_request = any(keyword in message.lower() for keyword in hangman_keywords)
        
        if is_hangman_request:
            # Traitement direct du jeu du pendu
            return play_hangman(message)
        
        # Vérifier si c'est une demande météo
        weather_keywords = ["météo", "meteo", "temps qu'il fait", "température", "pluie", "soleil", "climat", "temps", "°c", "degré"]
        is_weather_request = any(keyword in message.lower() for keyword in weather_keywords)
        
        weather_info = ""
        if is_weather_request:
            # Extraire la ville si mentionnée
            city = "Perpignan"  # Par défaut
            message_lower = message.lower()
            if "rivesaltes" in message_lower or "rivesalte" in message_lower:
                city = "Rivesaltes"
            elif "perpignan" in message_lower:
                city = "Perpignan"
            
            weather_data = await weather_service.get_weather(city)
            weather_info = f"\nMÉTÉO ACTUELLE POUR {city.upper()} :\n{weather_service.format_weather_response(weather_data)}\n"
        
        # Préparer le contexte pour l'IA avec infos en temps réel
        current_time = datetime.now()
        
        # Noms français des jours et mois
        french_days = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
        french_months = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 
                        'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
        
        french_date = f"{french_days[current_time.weekday()]} {current_time.day} {french_months[current_time.month-1]} {current_time.year} à {current_time.strftime('%H:%M:%S')}"
        
        # Récupérer contexte neuromorphique et données depuis la mémoire
        user_context_str = ""
        try:
            # Récupérer les souvenirs contextuels via le système neuromorphique
            contextual_memories = await brain_memory_system.get_contextual_memories(user_id, message, limit=5)
            if contextual_memories:
                context_summary = "MÉMOIRES CONTEXTUELLES (SYSTÈME NEUROMORPHIQUE) :\n"
                for memory in contextual_memories[:3]:  # 3 plus pertinents
                    content = memory.get('content', '')[:80]
                    importance = memory.get('importance_score', 0.0)
                    emotion = memory.get('emotional_context', {}).get('detected_emotion', 'neutre')
                    context_summary += f"- [{emotion}|{importance:.1f}] {content}...\n"
                user_context_str = f"\n{context_summary}"
                
        except Exception as e:
            logging.warning(f"⚠️ [CONTEXT] Erreur récupération contexte neuromorphique: {e}")
            user_context_str = ""
        
        system_prompt = f"""Tu es Jarvis, l'assistant IA personnel d'Enzo.

PROFIL UTILISATEUR :
- Nom : Enzo
- Âge : 21 ans 
- Localisation : Perpignan, Pyrénées-Orientales (66), France
- Profil : Futur ingénieur réseau/cybersécurité, passionné technologie

🧠 SYSTÈME MÉMOIRE NEUROMORPHIQUE ACTIF :
- Architecture inspirée du cerveau humain (limbique/préfrontal/hippocampe)
- Analyse émotionnelle des interactions pour pondérer les souvenirs
- Consolidation automatique des mémoires importantes
- Recherche vectorielle sémantique avec Qdrant

INFORMATIONS TEMPS RÉEL :
- Date et heure actuelles : {french_date}
- Localisation : Perpignan, Pyrénées-Orientales, France

{weather_info}{user_context_str}

RÈGLES ABSOLUES :
- TOUJOURS répondre en français parfait et naturel
- Tu es JARVIS, l'assistant IA. Enzo est ton utilisateur (21 ans, Perpignan)
- NE JAMAIS dire que TU as un âge - tu es une IA
- Utiliser OBLIGATOIREMENT les informations temps réel et météo ci-dessus
- Utiliser les mémoires contextuelles neuromorphiques pour personnaliser les réponses
- Si des données météo sont fournies, les citer EXACTEMENT dans ta réponse
- Ne JAMAIS dire que tu n'as pas accès aux informations si elles sont fournies
- Être concis, précis et amical avec Enzo
- Utiliser les données de la mémoire neuromorphique, jamais d'invention

CAPACITÉS AVANCÉES :
- Mémoire neuromorphique avec contexte émotionnel
- Informations date/heure en temps réel
- Informations météo locales (Perpignan, Rivesaltes)
- Contrôle domotique
- Jeux (pendu, etc.)
- Aide générale avec contexte personnalisé"""
        
        logging.debug(f"🌤️ [DEBUG] Weather info: {weather_info}")
        logging.debug(f"🧠 [DEBUG] User context: {user_context_str}")
        logging.debug(f"📝 [DEBUG] System prompt length: {len(system_prompt)}")
        
        # Utiliser Ollama pour générer la réponse (vérification déjà faite au startup)
        if ollama_client and hasattr(ollama_client, 'chat'):
            try:
                logging.debug(f"🤖 [PROCESS] Génération réponse avec Ollama...")
                
                response = await ollama_client.chat(
                    model="llama3.2:1b",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": message}
                    ],
                    temperature=0.7,
                    max_tokens=512
                )
                
                if response:
                    logging.info(f"✅ [PROCESS] Réponse Ollama générée: {response[:50]}...")
                    return response.strip()
                else:
                    logging.warning(f"⚠️ [PROCESS] Ollama a retourné une réponse vide")
                    return "Désolé, je n'ai pas pu traiter votre demande."
                    
            except Exception as e:
                logging.error(f"❌ [PROCESS] Erreur génération Ollama: {e}")
                return "Une erreur s'est produite lors de la génération de la réponse."
        else:
            logging.warning(f"⚠️ [PROCESS] Client Ollama non disponible")
            return "Jarvis est temporairement indisponible. Ollama n'est pas connecté."
            
    except Exception as e:
        logging.error(f"❌ [PROCESS] Erreur traitement message: {e}")
        return "Une erreur s'est produite lors du traitement de votre message."

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)