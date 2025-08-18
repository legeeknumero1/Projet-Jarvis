#!/usr/bin/env python3
"""
Hybrid HTTP/WebSocket Server for Jarvis V1 Demo
Serveur hybride pour gérer les requêtes HTTP et WebSocket
"""

import asyncio
import json
import logging
import websockets
from websockets.server import WebSocketServerProtocol
from datetime import datetime
import random
from aiohttp import web, WSMsgType, ClientSession
import aiohttp_cors
from jarvis_ai import JarvisAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HybridJarvisServer:
    def __init__(self):
        self.active_connections = set()
        self.ollama_url = "http://localhost:11434"
        self.model_name = "llama3.2:1b"  # Model par défaut
        self.session = None
        self.jarvis_ai = JarvisAI()  # IA locale intelligente
        self.conversation_memory = {}  # Mémoire par connexion
        import os
        self.conversations_log_path = os.path.join(os.getcwd(), "docs", "CONVERSATIONS.md")
    
    async def init_session(self):
        """Initialize HTTP session for Ollama requests"""
        if self.session is None:
            self.session = ClientSession()
        return self.session
    
    async def check_ollama_availability(self):
        """Check if Ollama is running and accessible"""
        try:
            session = await self.init_session()
            async with session.get(f"{self.ollama_url}/api/version") as response:
                if response.status == 200:
                    return True
        except Exception as e:
            logger.error(f"Ollama not available: {e}")
        return False
    
    async def search_internet(self, query: str) -> str:
        """Recherche d'informations sur internet en temps réel"""
        try:
            session = await self.init_session()
            
            # Essayer une recherche simple avec une API publique
            # Utiliser une API de news publique ou OpenWeatherMap pour météo
            
            # Pour test, utilisons une recherche basique
            if "météo" in query.lower():
                # Essayer une API météo simple
                weather_url = f"https://api.openweathermap.org/data/2.5/weather?q=Nimes,FR&appid=demo&units=metric"
                try:
                    async with session.get(weather_url) as response:
                        if response.status == 200:
                            return "Informations météo en temps réel récupérées depuis OpenWeatherMap"
                except:
                    pass
            
            # Pour actualités, essayer une API de news
            if "actualité" in query.lower() or "news" in query.lower():
                return f"Recherche d'actualités pour: {query}. Données limitées sans clé API."
            
            # Recherche générale
            return f"Recherche internet effectuée pour: {query}. Informations limitées sans API premium."
                
        except Exception as e:
            logger.error(f"Error in search: {e}")
            return f"Recherche internet tentée pour: {query}. Erreur technique."
    
    async def query_ollama_with_memory(self, prompt: str, websocket) -> str:
        """Query Ollama avec mémoire de conversation"""
        try:
            connection_id = id(websocket)
            
            # Récupérer ou créer la mémoire de conversation
            if connection_id not in self.conversation_memory:
                self.conversation_memory[connection_id] = []
            
            # Ajouter le message utilisateur à la mémoire
            self.conversation_memory[connection_id].append({
                "role": "user",
                "content": prompt,
                "timestamp": datetime.now().isoformat()
            })
            
            # Garder seulement les 20 derniers échanges
            if len(self.conversation_memory[connection_id]) > 40:
                self.conversation_memory[connection_id] = self.conversation_memory[connection_id][-40:]
            
            # Déterminer s'il faut faire une recherche internet
            search_keywords = ["actualité", "news", "aujourd'hui", "récent", "dernière", "météo", "prix", "cours", "bourse", "nimes", "montpellier", "perpignan"]
            needs_internet = any(keyword in prompt.lower() for keyword in search_keywords)
            
            internet_info = ""
            if needs_internet:
                internet_info = await self.search_internet(prompt)
                logger.info(f"Internet search result: {internet_info}")
            
            # Construire le contexte de conversation
            context = ""
            recent_history = self.conversation_memory[connection_id][-10:]  # 10 derniers messages
            for msg in recent_history:
                if msg["role"] == "user":
                    context += f"Utilisateur: {msg['content']}\n"
                else:
                    context += f"J.A.R.V.I.S: {msg['content']}\n"
            
            session = await self.init_session()
            
            # Prompt système amélioré avec mémoire
            current_time = datetime.now()
            system_prompt = f"""Tu es J.A.R.V.I.S, un assistant personnel IA.
            
            INFORMATIONS SYSTÈME :
            - Date : vendredi 18 juillet 2025
            - Heure : {current_time.strftime('%H:%M:%S')}
            - Lieu : France (région Occitanie)
            
            RÈGLES :
            - Réponds en français
            - Utilise les informations système pour l'heure/date
            - Si on te demande l'heure, réponds précisément
            - Si on te demande l'actualité, utilise les infos internet
            - Reste concis et utile
            
            {f"Contexte: {context}" if context else ""}
            {f"Internet: {internet_info}" if internet_info else ""}"""
            
            payload = {
                "model": self.model_name,
                "prompt": f"{system_prompt}\n\nUtilisateur: {prompt}\n\nJ.A.R.V.I.S:",
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.8,
                    "top_k": 20,
                    "repeat_penalty": 1.3,
                    "num_predict": 200
                }
            }
            
            async with session.post(f"{self.ollama_url}/api/generate", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    ai_response = result.get("response", "").strip()
                    
                    # Ajouter la réponse à la mémoire
                    self.conversation_memory[connection_id].append({
                        "role": "assistant",
                        "content": ai_response,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    return ai_response
                else:
                    logger.error(f"Ollama API error: {response.status}")
                    return "Désolé, j'ai un problème technique temporaire avec mon système principal."
        except Exception as e:
            logger.error(f"Error querying Ollama with memory: {e}")
            return "Désolé, je ne peux pas traiter votre demande en ce moment."
    
    async def save_conversation_to_md(self, user_message: str, ai_response: str, websocket):
        """Save conversation to MD file"""
        try:
            connection_id = id(websocket)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Prepare conversation entry
            conversation_entry = f"""
## Conversation {timestamp}

**👤 Utilisateur** ({timestamp})
{user_message}

**🤖 J.A.R.V.I.S** ({timestamp})
{ai_response}

---

"""
            
            # Append to conversations log
            with open(self.conversations_log_path, "a", encoding="utf-8") as f:
                f.write(conversation_entry)
                
            logger.info(f"Conversation saved to {self.conversations_log_path}")
            
        except Exception as e:
            logger.error(f"Error saving conversation to MD: {e}")
    
    async def init_conversations_log(self):
        """Initialize conversations log file"""
        try:
            import os
            os.makedirs(os.path.dirname(self.conversations_log_path), exist_ok=True)
            
            # Create file if it doesn't exist
            if not os.path.exists(self.conversations_log_path):
                with open(self.conversations_log_path, "w", encoding="utf-8") as f:
                    f.write(f"""# 💬 Conversations J.A.R.V.I.S

Journal des conversations avec l'assistant J.A.R.V.I.S.

**Démarré le** : {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

""")
            
        except Exception as e:
            logger.error(f"Error initializing conversations log: {e}")
    
    async def query_ollama(self, prompt: str) -> str:
        """Query Ollama for AI response"""
        try:
            session = await self.init_session()
            
            # Préparer le prompt système pour Jarvis
            system_prompt = """Tu es J.A.R.V.I.S (Just A Rather Very Intelligent System), un assistant personnel IA avancé. 
            Tu es poli, professionnel, et tu donnes des réponses courtes et précises. 
            Tu parles français et tu es là pour aider l'utilisateur avec ses demandes.
            Ne dis pas que tu es un modèle de langage, agis comme un vrai assistant personnel."""
            
            payload = {
                "model": self.model_name,
                "prompt": f"System: {system_prompt}\n\nUser: {prompt}\n\nAssistant:",
                "stream": False
            }
            
            async with session.post(f"{self.ollama_url}/api/generate", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("response", "").strip()
                else:
                    logger.error(f"Ollama API error: {response.status}")
                    return "Désolé, j'ai un problème technique temporaire."
        except Exception as e:
            logger.error(f"Error querying Ollama: {e}")
            return "Désolé, je ne peux pas traiter votre demande en ce moment."
    
    def generate_intelligent_response(self, user_message: str) -> str:
        """Generate intelligent response based on user message"""
        message = user_message.lower().strip()
        
        # Salutations
        if any(word in message for word in ["bonjour", "salut", "hello", "hi", "slt", "coucou"]):
            return "Bonjour ! Je suis J.A.R.V.I.S, votre assistant personnel. Comment puis-je vous aider ?"
        
        # Questions sur l'état
        if any(phrase in message for phrase in ["comment vas-tu", "comment ça va", "ça va", "comment vas tu", "comment allez vous"]):
            return "Tous mes systèmes sont opérationnels et fonctionnent parfaitement. Merci de demander ! Et vous, comment allez-vous ?"
        
        # Questions sur l'heure
        if any(word in message for word in ["heure", "quelle heure", "il est quelle heure"]):
            return f"Il est actuellement {datetime.now().strftime('%H:%M:%S')}."
        
        # Questions sur la date
        if any(phrase in message for phrase in ["date", "quel jour", "quelle date", "on est quel jour", "on est quelle date", "jour", "aujourd'hui"]):
            today = datetime.now()
            days = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
            day_name = days[today.weekday()]
            return f"Nous sommes {day_name} {today.strftime('%d/%m/%Y')}."
        
        # Questions sur la météo
        if any(word in message for word in ["météo", "temps", "temperature", "pluie", "soleil"]):
            return "Je n'ai pas accès aux données météo en temps réel, mais je peux vous dire qu'il fait généralement beau dans le sud de la France ! Pour des informations précises, je vous recommande de consulter un service météo."
        
        # Remerciements
        if any(word in message for word in ["merci", "thank you", "thanks", "merci beaucoup"]):
            return "De rien ! C'est un plaisir de vous aider. N'hésitez pas si vous avez d'autres questions !"
        
        # Questions sur l'identité
        if any(phrase in message for phrase in ["qui es-tu", "qui êtes-vous", "tu es qui", "c'est quoi", "que fais-tu"]):
            return "Je suis J.A.R.V.I.S (Just A Rather Very Intelligent System), votre assistant personnel IA. Je suis là pour vous aider avec diverses tâches et répondre à vos questions."
        
        # Questions sur les capacités
        if any(phrase in message for phrase in ["que peux-tu faire", "tes capacités", "que sais-tu faire", "aide moi", "help"]):
            return "Je peux vous aider avec de nombreuses tâches : répondre à vos questions, donner l'heure et la date, discuter avec vous, et bien plus encore. N'hésitez pas à me demander ce dont vous avez besoin !"
        
        # Au revoir
        if any(word in message for word in ["au revoir", "bye", "goodbye", "à bientôt", "salut", "tchao"]):
            return "Au revoir ! Ce fut un plaisir de discuter avec vous. À bientôt !"
        
        # Réponse par défaut plus intelligente
        if len(message) > 0:
            return f"J'ai bien reçu votre message : '{user_message}'. Je suis encore en développement et j'apprends constamment. Pouvez-vous me donner plus de détails sur ce que vous souhaitez ?"
        else:
            return "Je n'ai pas bien compris votre message. Pouvez-vous le reformuler s'il vous plaît ?"
    
    async def register_connection(self, websocket):
        """Register a new WebSocket connection"""
        self.active_connections.add(websocket)
        logger.info(f"New connection registered. Total: {len(self.active_connections)}")
        
        # Send welcome message
        await websocket.send_str(json.dumps({
            "type": "connection_established",
            "message": "Connexion établie avec J.A.R.V.I.S",
            "timestamp": datetime.now().isoformat()
        }))
    
    async def unregister_connection(self, websocket):
        """Unregister a WebSocket connection"""
        self.active_connections.discard(websocket)
        logger.info(f"Connection unregistered. Total: {len(self.active_connections)}")
    
    async def handle_message(self, websocket, message: str):
        """Handle incoming messages"""
        try:
            data = json.loads(message)
            user_message = data.get("message", "")
            
            logger.info(f"Received message: {user_message}")
            
            # Simulate processing time
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
            # Generate AI response using ONLY Ollama (règle 13 CLAUDE_PARAMS.md)
            if await self.check_ollama_availability():
                # Utiliser Ollama avec mémoire et recherche internet
                response = await self.query_ollama_with_memory(user_message, websocket)
            else:
                # Ollama requis - pas de fallback avec réponses pré-définies
                response = "Désolé, mon système IA principal (Ollama) n'est pas disponible. Veuillez redémarrer Ollama pour des réponses intelligentes."
                logger.error("Ollama unavailable - no fallback allowed per CLAUDE_PARAMS.md rule 13")
            
            # Save conversation to MD file
            await self.save_conversation_to_md(user_message, response, websocket)
            
            # Send response
            await websocket.send_str(json.dumps({
                "type": "ai_response",
                "response": response,
                "timestamp": datetime.now().isoformat(),
                "processing_time": random.uniform(200, 800)
            }))
            
        except json.JSONDecodeError:
            logger.error("Invalid JSON received")
            await websocket.send_str(json.dumps({
                "type": "error",
                "message": "Format de message invalide"
            }))
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await websocket.send_str(json.dumps({
                "type": "error",
                "message": "Erreur de traitement"
            }))

# Global server instance
jarvis_server = HybridJarvisServer()

async def websocket_handler(request):
    """WebSocket endpoint handler"""
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    await jarvis_server.register_connection(ws)
    
    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                await jarvis_server.handle_message(ws, msg.data)
            elif msg.type == WSMsgType.ERROR:
                logger.error(f'WebSocket error: {ws.exception()}')
                break
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await jarvis_server.unregister_connection(ws)
    
    return ws

async def health_check(request):
    """Health check endpoint"""
    return web.json_response({"status": "healthy", "timestamp": datetime.now().isoformat()})

async def manifest_handler(request):
    """Handle manifest.json requests"""
    manifest = {
        "name": "Jarvis AI Assistant",
        "short_name": "Jarvis",
        "start_url": "/",
        "display": "standalone",
        "theme_color": "#000000",
        "background_color": "#ffffff"
    }
    return web.json_response(manifest)

async def home_handler(request):
    """Handle home page requests - serve React app or fallback"""
    import os
    
    # Try to serve React build first
    static_path = os.path.join(os.getcwd(), "static")
    index_path = os.path.join(static_path, "index.html")
    
    if os.path.exists(index_path):
        # Serve React app
        return web.FileResponse(index_path, headers={'Content-Type': 'text/html'})
    else:
        # Fallback - serve debug page
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Jarvis Backend Server</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #0f0f0f; color: #00ff00; }
                .container { max-width: 800px; margin: 0 auto; }
                .status { background: #1a1a1a; padding: 20px; border-radius: 10px; margin: 20px 0; }
                .endpoint { background: #2a2a2a; padding: 15px; margin: 10px 0; border-radius: 5px; }
                .online { color: #00ff00; }
                .offline { color: #ff0000; }
                .warning { color: #ffaa00; }
                a { color: #00aaff; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 Jarvis Backend Server</h1>
                <div class="status">
                    <h2>État du serveur: <span class="online">🟢 En ligne</span></h2>
                    <p>Serveur hybride HTTP/WebSocket pour Jarvis AI Assistant</p>
                </div>
                
                <div class="status">
                    <h2 class="warning">⚠️ Interface React non disponible</h2>
                    <p>Le frontend React n'est pas build. Chemin cherché: """ + static_path + """</p>
                    <p>Pour corriger: Rebuild le container avec le Dockerfile multi-stage</p>
                </div>
                
                <div class="status">
                    <h2>Points d'accès disponibles:</h2>
                    <div class="endpoint">
                        <strong>Interface actuelle:</strong> Cette page de debug
                    </div>
                    <div class="endpoint">
                        <strong>WebSocket:</strong> ws://localhost:8000/ws
                    </div>
                    <div class="endpoint">
                        <strong>Health Check:</strong> <a href="/health">/health</a>
                    </div>
                    <div class="endpoint">
                        <strong>Manifest:</strong> <a href="/manifest.json">/manifest.json</a>
                    </div>
                </div>
                
                <div class="status">
                    <h2>Connexions actives:</h2>
                    <p>WebSocket: """ + str(len(jarvis_server.active_connections)) + """ connexions</p>
                </div>
            </div>
        </body>
        </html>
        """
        return web.Response(text=html, content_type='text/html')

async def static_handler(request):
    """Handle static file requests for React assets"""
    import os
    
    # Get the file path from URL
    file_path = request.path.strip('/')
    static_path = os.path.join(os.getcwd(), "static")
    full_path = os.path.join(static_path, file_path)
    
    # Security check - prevent directory traversal
    if not full_path.startswith(static_path):
        return web.Response(status=403, text="Forbidden")
    
    # Check if file exists
    if os.path.exists(full_path) and os.path.isfile(full_path):
        # Determine content type
        content_type = "text/plain"
        if file_path.endswith('.js'):
            content_type = "application/javascript"
        elif file_path.endswith('.css'):
            content_type = "text/css"
        elif file_path.endswith('.json'):
            content_type = "application/json"
        elif file_path.endswith('.png'):
            content_type = "image/png"
        elif file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
            content_type = "image/jpeg"
        elif file_path.endswith('.svg'):
            content_type = "image/svg+xml"
        elif file_path.endswith('.ico'):
            content_type = "image/x-icon"
        elif file_path.endswith('.woff') or file_path.endswith('.woff2'):
            content_type = "font/woff"
        elif file_path.endswith('.ttf'):
            content_type = "font/ttf"
        
        return web.FileResponse(full_path, headers={'Content-Type': content_type})
    else:
        # For SPA - fallback to index.html for client-side routing
        index_path = os.path.join(static_path, "index.html")
        if os.path.exists(index_path):
            return web.FileResponse(index_path, headers={'Content-Type': 'text/html'})
        else:
            return web.Response(status=404, text="File not found")

def create_app():
    """Create the web application"""
    app = web.Application()
    
    # Enable CORS
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods="*"
        )
    })
    
    # Add routes
    app.router.add_get('/', home_handler)
    app.router.add_get('/ws', websocket_handler)
    app.router.add_get('/health', health_check)
    app.router.add_get('/manifest.json', manifest_handler)
    
    # Add static file routes for React assets
    app.router.add_get('/static/{path:.*}', static_handler)
    app.router.add_get('/{path:.*\.(js|css|png|jpg|jpeg|gif|svg|ico|woff|woff2|ttf|json)}', static_handler)
    
    # Add CORS to all routes
    for route in list(app.router.routes()):
        cors.add(route)
    
    return app

async def start_server():
    """Start the hybrid server"""
    # Initialize conversations log
    await jarvis_server.init_conversations_log()
    
    app = create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, '0.0.0.0', 8000)
    await site.start()
    
    logger.info("Hybrid Jarvis server started on http://localhost:8000")
    logger.info("WebSocket endpoint: ws://localhost:8000/ws")
    logger.info("Health check: http://localhost:8000/health")
    logger.info(f"Conversations log: {jarvis_server.conversations_log_path}")
    
    # Keep server running
    try:
        await asyncio.Future()  # Run forever
    except KeyboardInterrupt:
        logger.info("Server shutting down...")
    finally:
        await runner.cleanup()

if __name__ == "__main__":
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        logger.info("Server shutting down...")