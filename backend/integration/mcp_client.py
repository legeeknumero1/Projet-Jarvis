"""
Client MCP pour Jarvis - Intégration avec serveurs MCP externes
Permet à Jarvis d'accéder à internet via des serveurs MCP comme Browserbase
"""
import asyncio
import json
import logging
import subprocess
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class MCPServer:
    """Configuration d'un serveur MCP"""
    name: str
    command: str
    args: List[str]
    env: Dict[str, str]
    description: str
    capabilities: List[str]

class MCPClient:
    """Client pour communiquer avec les serveurs MCP"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.servers: Dict[str, MCPServer] = {}
        self.processes: Dict[str, subprocess.Popen] = {}
        
    def register_server(self, server: MCPServer):
        """Enregistre un serveur MCP"""
        self.servers[server.name] = server
        self.logger.info(f"🔌 [MCP] Serveur {server.name} enregistré : {server.description}")
    
    async def start_server(self, server_name: str) -> bool:
        """Démarre un serveur MCP"""
        try:
            if server_name not in self.servers:
                self.logger.error(f"❌ [MCP] Serveur {server_name} non trouvé")
                return False
            
            server = self.servers[server_name]
            
            # Démarrer le processus du serveur MCP
            process = subprocess.Popen(
                [server.command] + server.args,
                env={**os.environ, **server.env},
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0
            )
            
            self.processes[server_name] = process
            self.logger.info(f"✅ [MCP] Serveur {server_name} démarré (PID: {process.pid})")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ [MCP] Erreur démarrage {server_name}: {e}")
            return False
    
    async def send_request(self, server_name: str, method: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Envoie une requête JSON-RPC à un serveur MCP"""
        try:
            if server_name not in self.processes:
                self.logger.error(f"❌ [MCP] Serveur {server_name} non démarré")
                return None
            
            process = self.processes[server_name]
            
            # Préparer la requête JSON-RPC
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": method,
                "params": params
            }
            
            # Envoyer la requête
            request_json = json.dumps(request) + "\n"
            process.stdin.write(request_json)
            process.stdin.flush()
            
            # Lire la réponse
            response_line = process.stdout.readline()
            if not response_line:
                self.logger.error(f"❌ [MCP] Pas de réponse de {server_name}")
                return None
            
            response = json.loads(response_line.strip())
            
            if "error" in response:
                self.logger.error(f"❌ [MCP] Erreur serveur {server_name}: {response['error']}")
                return None
            
            return response.get("result")
            
        except Exception as e:
            self.logger.error(f"❌ [MCP] Erreur requête {server_name}: {e}")
            return None
    
    async def browse_web(self, url: str, action: str = "navigate", **kwargs) -> Optional[Dict[str, Any]]:
        """Interface simplifiée pour naviguer sur le web via MCP Browserbase"""
        try:
            if "browserbase_web_automation" not in self.servers:
                self.logger.error("❌ [MCP] Serveur Browserbase Web Automation non configuré")
                return None
            
            # Paramètres selon l'action
            if action == "navigate":
                params = {"url": url}
            elif action == "screenshot":
                params = {"url": url, "fullPage": kwargs.get("full_page", True)}
            elif action == "extract":
                params = {"url": url, "selector": kwargs.get("selector", "body")}
            else:
                params = {"url": url, **kwargs}
            
            # Envoyer la requête au serveur Browserbase
            result = await self.send_request("browserbase_web_automation", action, params)
            
            if result:
                self.logger.info(f"✅ [MCP] Navigation {action} réussie : {url}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ [MCP] Erreur navigation web: {e}")
            return None
    
    async def stop_server(self, server_name: str):
        """Arrête un serveur MCP"""
        try:
            if server_name in self.processes:
                process = self.processes[server_name]
                process.terminate()
                process.wait(timeout=5)
                del self.processes[server_name]
                self.logger.info(f"🛑 [MCP] Serveur {server_name} arrêté")
        except Exception as e:
            self.logger.error(f"❌ [MCP] Erreur arrêt {server_name}: {e}")
    
    async def stop_all_servers(self):
        """Arrête tous les serveurs MCP"""
        for server_name in list(self.processes.keys()):
            await self.stop_server(server_name)
    
    def get_available_capabilities(self) -> Dict[str, List[str]]:
        """Retourne les capacités disponibles de tous les serveurs"""
        return {
            name: server.capabilities 
            for name, server in self.servers.items()
        }

# Configuration des serveurs MCP par défaut
def create_default_mcp_servers() -> List[MCPServer]:
    """Crée la configuration par défaut des serveurs MCP"""
    
    # Chemin vers le serveur Browserbase Web Automation
    browserbase_path = Path(__file__).parent.parent.parent / "MCP" / "servers" / "browserbase_web_automation" / "dist" / "cli.js"
    
    servers = []
    
    # Serveur Browserbase pour l'accès internet
    if browserbase_path.exists():
        servers.append(MCPServer(
            name="browserbase_web_automation",
            command="node",
            args=[str(browserbase_path)],
            env={
                "BROWSERBASE_API_KEY": os.getenv("BROWSERBASE_API_KEY", ""),
                "BROWSERBASE_PROJECT_ID": os.getenv("BROWSERBASE_PROJECT_ID", ""),
                "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY", ""),
                "MODEL_API_KEY": os.getenv("GEMINI_API_KEY", "")  # Alias pour MODEL_API_KEY
            },
            description="Navigation internet et automation web via Browserbase",
            capabilities=["navigate", "screenshot", "extract", "click", "fill", "search", "observe", "act"]
        ))
    
    return servers

# Import os à ajouter en haut du fichier
import os