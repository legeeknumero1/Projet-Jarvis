"""Router WebSocket - connexions temps réel"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request
from ..utils.logging import get_logger
import json
from datetime import datetime

router = APIRouter()
logger = get_logger(__name__)

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, request: Request):
    """
    WebSocket public pour frontend local
    Extrait de main.py:371-452
    """
    client_id = f"client_{id(websocket)}"
    logger.info(f"🔌 [WS] Nouvelle connexion WebSocket: {client_id}")
    
    await websocket.accept()
    logger.info(f"✅ [WS] {client_id} connecté")
    
    # Services depuis app.state
    memory_service = request.app.state.memory
    llm_service = request.app.state.llm  
    weather_service = request.app.state.weather
    
    try:
        while True:
            logger.debug(f"📡 [WS] {client_id} en attente de message...")
            data = await websocket.receive_text()
            logger.info(f"📨 [WS] {client_id} message reçu: {data[:100]}...")
            
            try:
                message_data = json.loads(data)
                logger.debug(f"✅ [WS] {client_id} JSON parsé: {message_data.keys()}")
                
                # Validation des données (comme main.py:391-402)
                if not isinstance(message_data, dict):
                    raise ValueError("Les données doivent être un objet JSON")
                
                if "message" not in message_data:
                    raise ValueError("Le champ 'message' est requis")
                
                message = message_data["message"]
                if not message or not isinstance(message, str) or len(message.strip()) == 0:
                    raise ValueError("Le message ne peut pas être vide")
                
                if len(message) > 5000:
                    raise ValueError("Message trop long (max 5000 caractères)")
                
            except json.JSONDecodeError as e:
                logger.error(f"❌ [WS] {client_id} Erreur JSON: {e}")
                await websocket.send_text(json.dumps({
                    "error": "Format JSON invalide",
                    "timestamp": datetime.now().isoformat()
                }))
                continue
            except ValueError as e:
                logger.error(f"❌ [WS] {client_id} Validation erreur: {e}")
                await websocket.send_text(json.dumps({
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }))
                continue
            
            # Traitement neuromorphique du message en temps réel (main.py:419-446)
            try:
                logger.debug(f"🤖 [WS] {client_id} Traitement avec IA neuromorphique...")
                user_id = message_data.get("user_id", "default")
                
                # Contexte neuromorphique
                user_context = await memory_service.get_contextual_memories(
                    user_id, 
                    message_data["message"]
                )
                
                # Import de la logique de traitement chat
                from .chat import process_message_with_services
                from ..schemas.chat import MessageRequest
                
                # Création d'un MessageRequest pour réutiliser la logique
                message_request = MessageRequest(
                    message=message_data["message"],
                    user_id=user_id,
                    save_memory=message_data.get("save_memory", True)
                )
                
                response = await process_message_with_services(
                    message_request,
                    user_context,
                    llm_service,
                    weather_service
                )
                logger.info(f"✅ [WS] {client_id} Réponse générée: {response[:50]}...")
                
                # Sauvegarde en mémoire neuromorphique
                await memory_service.store_interaction(user_id, message, response)
                
                response_data = {
                    "response": response,
                    "timestamp": datetime.now().isoformat()
                }
                
                await websocket.send_text(json.dumps(response_data))
                logger.debug(f"📤 [WS] {client_id} Réponse envoyée")
                
            except Exception as processing_error:
                logger.error(f"❌ [WS] {client_id} Erreur traitement: {processing_error}")
                await websocket.send_text(json.dumps({
                    "error": "Erreur interne du serveur",
                    "timestamp": datetime.now().isoformat()
                }))
            
    except WebSocketDisconnect:
        logger.info(f"🔌 [WS] {client_id} déconnecté")
    except Exception as e:
        logger.error(f"❌ [WS] {client_id} Erreur: {e}")

@router.websocket("/ws/secure")
async def websocket_secure_endpoint(websocket: WebSocket, request: Request):
    """
    WebSocket sécurisé pour intégrations externes
    Extrait de main.py:453-472
    """
    client_id = f"secure_client_{id(websocket)}"
    logger.info(f"🔌 [WS-SEC] Nouvelle connexion WebSocket sécurisée: {client_id}")
    
    # Vérification de l'authentification via query params
    query_params = dict(websocket.query_params)
    api_key = query_params.get('api_key')
    
    # TODO: Récupérer API_KEY depuis settings
    settings = request.app.state.settings
    expected_api_key = settings.api_key
    
    if not api_key or api_key != expected_api_key:
        logger.warning(f"❌ [WS-SEC] {client_id} Authentification échouée - API key invalide")
        await websocket.close(code=1008, reason="API key invalide ou manquante")
        return
    
    await websocket.accept()
    logger.info(f"✅ [WS-SEC] {client_id} connecté et authentifié")
    
    # Réutiliser la même logique que le WebSocket public
    await websocket_endpoint(websocket, request)