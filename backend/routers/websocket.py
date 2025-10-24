"""Router WebSocket - connexions temps réel avec graceful shutdown"""
import uuid
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request
from starlette.websockets import WebSocketState
from utils.logging import get_logger, set_context, reset_context
import json
import asyncio
from datetime import datetime

router = APIRouter()
logger = get_logger(__name__)

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, request: Request):
    """
    WebSocket public pour frontend local avec graceful shutdown
    Extrait de main.py:371-452
    """
    # Générer request-id pour correlation logs
    rid = uuid.uuid4().hex[:12]
    client_id = f"client_{rid}"
    
    # Définir contexte logs pour toute la connexion WebSocket
    tokens = set_context(
        request_id=rid,
        path="/ws",
        method="WS", 
        client_ip=websocket.client.host if websocket.client else "-",
        component="ws"
    )
    
    ws_logger = logging.getLogger("backend.ws")
    
    # Vérifier mode drain - refuser nouvelles connexions
    if getattr(request.app.state, "draining", False):
        ws_logger.warning("ws connection refused - server draining")
        await websocket.close(code=1013, reason="Server draining - try again later")
        reset_context(tokens)
        return
    
    try:
        await websocket.accept()
        await request.app.state.ws.register(websocket)
        ws_logger.info("ws connected")
        
        # Services depuis app.state
        memory_service = request.app.state.memory
        llm_service = request.app.state.llm  
        weather_service = request.app.state.weather
        
        # Set de tâches actives pour cette connexion
        active_tasks = set()
        
        while True:
            data = await websocket.receive_text()
            ws_logger.info("ws message received")
            
            user_context_token = None
            try:
                message_data = json.loads(data)
                
                # Validation des données (comme main.py:391-402)
                if not isinstance(message_data, dict):
                    raise ValueError("Les données doivent être un objet JSON")
                
                if "message" not in message_data:
                    raise ValueError("Le champ 'message' est requis")
                
                message = message_data["message"]
                if not message or not isinstance(message, str) or len(message.strip()) == 0:
                    raise ValueError("Le message ne peut pas être vide")
                
                if len(message) > 4096:
                    raise ValueError("Message trop long (max 4096 caractères)")
                
                # Enrichir contexte avec user_id pour ce message
                user_id = message_data.get("user_id", "-")
                user_context_token = set_context(user_id=user_id)
                
            except json.JSONDecodeError as e:
                ws_logger.error(f"ws json decode error: {e}")
                await websocket.send_text(json.dumps({
                    "error": "Format JSON invalide",
                    "timestamp": datetime.now().isoformat()
                }))
                continue
            except ValueError as e:
                ws_logger.error(f"ws validation error: {e}")
                await websocket.send_text(json.dumps({
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }))
                continue
            finally:
                # Reset contexte user_id après chaque message
                if user_context_token:
                    reset_context(user_context_token)
            
            # Traitement neuromorphique du message avec gestion tâches
            try:
                user_id = message_data.get("user_id", "default")
                
                # Créer tâche async pour traitement (pour cancellation propre)
                async def process_message_task():
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
                    
                    # Sauvegarde en mémoire neuromorphique
                    await memory_service.store_interaction(user_id, message_data["message"], response)
                    
                    return response
                
                # Lancer la tâche et la tracker
                task = asyncio.create_task(process_message_task())
                active_tasks.add(task)
                
                try:
                    response = await task
                    
                    response_data = {
                        "response": response,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    await websocket.send_text(json.dumps(response_data))
                    ws_logger.info("ws response sent")
                    
                except asyncio.CancelledError:
                    ws_logger.info("ws task cancelled")
                    raise
                finally:
                    active_tasks.discard(task)
                
            except Exception as processing_error:
                ws_logger.error(f"ws processing error: {processing_error}")
                await websocket.send_text(json.dumps({
                    "error": "Erreur interne du serveur",
                    "timestamp": datetime.now().isoformat()
                }))
            
    except WebSocketDisconnect:
        ws_logger.info("ws disconnected")
    except Exception as e:
        ws_logger.error(f"ws error: {e}")
    finally:
        # Annuler toutes les tâches actives avant fermeture
        if active_tasks:
            ws_logger.info(f"ws cancelling {len(active_tasks)} active tasks")
            for task in active_tasks:
                if not task.done():
                    task.cancel()
            
            # Attendre que toutes les tâches se terminent proprement
            if active_tasks:
                await asyncio.gather(*active_tasks, return_exceptions=True)
                ws_logger.info("ws tasks cancelled cleanly")
        
        # Désenregistrer la connexion du manager
        await request.app.state.ws.unregister(websocket)
        
        # Reset contexte logs
        reset_context(tokens)

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