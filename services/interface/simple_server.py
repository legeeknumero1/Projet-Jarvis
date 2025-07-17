#!/usr/bin/env python3
"""
Simple Server for Jarvis V1 Demo
Interface WebSocket simple pour tester l'interface
"""

import asyncio
import json
import logging
import websockets
from websockets.server import WebSocketServerProtocol
from datetime import datetime
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleJarvisServer:
    def __init__(self):
        self.active_connections = set()
        self.responses = [
            "Bonjour ! Je suis J.A.R.V.I.S, votre assistant personnel.",
            "Comment puis-je vous aider aujourd'hui ?",
            "Système neural activé. Prêt à recevoir vos commandes.",
            "Analyse en cours... Réponse optimisée générée.",
            "Parfait ! J'ai bien reçu votre message.",
            "Intelligence artificielle à votre service.",
            "Base de données consultée. Voici ma réponse.",
            "Traitement terminé. Autre chose ?",
            "Système opérationnel. En attente de nouvelles instructions.",
            "Analyse contextuelle terminée. Réponse adaptée."
        ]
    
    async def register_connection(self, websocket: WebSocketServerProtocol):
        """Register a new WebSocket connection"""
        self.active_connections.add(websocket)
        logger.info(f"New connection registered. Total: {len(self.active_connections)}")
        
        # Send welcome message
        await websocket.send(json.dumps({
            "type": "connection_established",
            "message": "Connexion établie avec J.A.R.V.I.S",
            "timestamp": datetime.now().isoformat()
        }))
    
    async def unregister_connection(self, websocket: WebSocketServerProtocol):
        """Unregister a WebSocket connection"""
        self.active_connections.discard(websocket)
        logger.info(f"Connection unregistered. Total: {len(self.active_connections)}")
    
    async def handle_message(self, websocket: WebSocketServerProtocol, message: str):
        """Handle incoming messages"""
        try:
            data = json.loads(message)
            user_message = data.get("message", "")
            
            logger.info(f"Received message: {user_message}")
            
            # Simulate processing time
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
            # Generate response
            response = random.choice(self.responses)
            if "bonjour" in user_message.lower():
                response = "Bonjour ! Je suis J.A.R.V.I.S, votre assistant personnel. Comment puis-je vous aider ?"
            elif "merci" in user_message.lower():
                response = "De rien ! C'est un plaisir de vous aider."
            elif "comment" in user_message.lower() and "ça va" in user_message.lower():
                response = "Tous mes systèmes sont opérationnels. Merci de demander !"
            elif "météo" in user_message.lower():
                response = "La météo est ensoleillée aujourd'hui à Perpignan. Température: 24°C."
            elif "heure" in user_message.lower():
                response = f"Il est actuellement {datetime.now().strftime('%H:%M:%S')}."
            elif "date" in user_message.lower():
                response = f"Nous sommes le {datetime.now().strftime('%d/%m/%Y')}."
            
            # Send response
            await websocket.send(json.dumps({
                "type": "ai_response",
                "response": response,
                "timestamp": datetime.now().isoformat(),
                "processing_time": random.uniform(200, 800)
            }))
            
        except json.JSONDecodeError:
            logger.error("Invalid JSON received")
            await websocket.send(json.dumps({
                "type": "error",
                "message": "Format de message invalide"
            }))
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await websocket.send(json.dumps({
                "type": "error",
                "message": "Erreur de traitement"
            }))
    
    async def handle_websocket(self, websocket: WebSocketServerProtocol, path: str):
        """Handle WebSocket connections"""
        await self.register_connection(websocket)
        
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            await self.unregister_connection(websocket)

# Global server instance
jarvis_server = SimpleJarvisServer()

async def websocket_handler(websocket: WebSocketServerProtocol, path: str):
    """WebSocket endpoint handler"""
    await jarvis_server.handle_websocket(websocket, path)

async def start_server():
    """Start the simple Jarvis server"""
    server = await websockets.serve(
        websocket_handler,
        "localhost",
        8000,
        ping_interval=20,
        ping_timeout=10
    )
    logger.info("Simple Jarvis server started on ws://localhost:8000")
    logger.info("Frontend should connect to ws://localhost:8000/ws")
    await server.wait_closed()

if __name__ == "__main__":
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        logger.info("Server shutting down...")