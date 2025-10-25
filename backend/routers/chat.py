"""Router Chat - endpoints de conversation"""
from fastapi import APIRouter, HTTPException, Depends, Request
from schemas.chat import MessageRequest, MessageResponse
from security.deps import api_key_required
from security.rate_limit import check_chat_rate_limit
from utils.logging import get_logger
import re
import json
from datetime import datetime

router = APIRouter()
logger = get_logger(__name__)

@router.get("/models")
async def get_available_models(request: Request):
    """
    Endpoint pour récupérer la liste des modèles Ollama disponibles
    Compatible avec l'interface frontend
    """
    try:
        llm_service = request.app.state.llm
        
        if not llm_service.is_available():
            raise HTTPException(status_code=503, detail="Service LLM non disponible")
        
        # Appel direct à Ollama pour lister les modèles
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{llm_service.settings.ollama_base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return {"models": data.get("models", [])}
            else:
                raise HTTPException(status_code=502, detail="Erreur accès Ollama")
                
    except Exception as e:
        logger.error(f"❌ [MODELS] Erreur récupération modèles: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=MessageResponse)
async def chat(
    message_request: MessageRequest, 
    request: Request,
    _: None = Depends(check_chat_rate_limit)
):
    """
    Endpoint chat public avec rate limiting anti-abus
    Authentification par IP locale uniquement
    """
    try:
        # Anti-abus: limite taille message
        if len(message_request.message) > 4096:
            raise HTTPException(status_code=413, detail="Message trop long (max 4096 caractères)")
        
        logger.info(f"💬 [CHAT] Nouveau message de {message_request.user_id}: {message_request.message[:50]}...")
        
        # Services depuis app.state (injection de dépendance)
        memory_service = request.app.state.memory
        llm_service = request.app.state.llm
        weather_service = request.app.state.weather
        
        # Vérification service mémoire (comme dans main.py:337-338)
        if not memory_service.is_available():
            raise HTTPException(status_code=503, detail="Service de mémoire non disponible")
        
        # Récupération contexte neuromorphique (main.py:340-342)
        logger.debug(f"🧠 [CHAT] Récupération contexte neuromorphique {message_request.user_id}")
        user_context = await memory_service.get_contextual_memories(
            message_request.user_id, 
            message_request.message
        )
        logger.debug(f"✅ [CHAT] Contexte neuromorphique récupéré: {len(user_context)} éléments")
        
        # Traitement du message avec l'IA (main.py:345-347)
        response_text = await process_message_with_services(
            message_request, user_context, llm_service, weather_service
        )
        
        logger.info(f"✅ [CHAT] Réponse générée: {response_text[:50]}...")
        
        # Sauvegarde neuromorphique (main.py:350-356)
        logger.debug("💾 [CHAT] Sauvegarde conversation neuromorphique...")
        memory_saved = await memory_service.store_interaction(
            message_request.user_id,
            message_request.message,
            response_text
        )
        logger.debug("✅ [CHAT] Conversation sauvegardée en mémoire neuromorphique")
        
        return MessageResponse(
            response=response_text,
            timestamp=datetime.now(),
            user_id=message_request.user_id,
            model="llama3.2:1b",
            memory_saved=memory_saved
        )
        
    except Exception as e:
        logger.error(f"❌ [CHAT] Erreur: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/secure", response_model=MessageResponse)
async def chat_secure(
    message_request: MessageRequest, 
    request: Request,
    api_key: str = Depends(api_key_required)
):
    """
    Endpoint chat sécurisé pour intégrations externes
    Extrait de main.py:366-369
    """
    return await chat(message_request, request)

async def process_message_with_services(
    request: MessageRequest, 
    user_context: list, 
    llm_service, 
    weather_service
) -> str:
    """
    Logique de traitement complète des messages avec vrais services
    Extrait de process_message() de main.py:530-696
    """
    message = request.message
    user_id = request.user_id
    
    # Détection données météo données par Enzo (main.py:537-556)
    weather_data_pattern = r"(\\d+)°?c.*?(\\d+)%.*?(\\d+)\\s*k?m?h"
    weather_match = re.search(weather_data_pattern, message.lower())
    
    if weather_match:
        temp = weather_match.group(1)
        humidity = weather_match.group(2)
        wind = weather_match.group(3)
        
        # Retour de confirmation (déjà sauvé par le router parent)
        return f"📝 Noté et sauvegardé en base ! Météo : {temp}°C, {humidity}% humidité, vent à {wind} km/h."
    
    # Détection jeu du pendu (main.py:558-564)
    hangman_keywords = ["pendu", "jeu", "jouer", "hangman"]
    if any(keyword in message.lower() for keyword in hangman_keywords):
        # Import dynamique du jeu
        from games.hangman import play_hangman
        return play_hangman(message)
    
    # Détection demande météo (main.py:566-582)
    if weather_service.detect_weather_request(message):
        city = weather_service.extract_city(message)
        weather_data = await weather_service.get_weather(city)
        weather_info = weather_service.format_weather_info(weather_data, city)
    else:
        weather_info = ""
    
    # Formation contexte pour LLM avec mémoire neuromorphique
    context_str = ""
    if user_context:
        # Format comme dans main.py:599-605
        context_str = "\\nMÉMOIRES CONTEXTUELLES (SYSTÈME NEUROMORPHIQUE) :\\n"
        for memory in user_context[:3]:
            content = memory.get('content', '')[:80]
            importance = memory.get('importance_score', 0.0)
            emotion = memory.get('emotional_context', {}).get('detected_emotion', 'neutre')
            context_str += f"- [{emotion}|{importance:.1f}] {content}...\\n"
    
    # Construction du contexte complet
    context = {
        'weather_info': weather_info,
        'user_context_str': context_str
    }
    
    # Génération réponse avec Ollama LLM
    response = await llm_service.generate_response(message, context, user_id)
    return response