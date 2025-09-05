"""
Client MCP pour Jarvis - Intégration avec serveurs MCP externes
Permet à Jarvis d'accéder à internet via des serveurs MCP comme Browserbase et Brave Search
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
async def search_web(self, query: str, count: int = 10, search_type: str = "web", 
                        privacy_preference: str = "medium") -> Dict[str, Any]:
        """Recherche web avec le système multi-provider - timeout robuste 2025"""
        if not MULTI_SEARCH_AVAILABLE:
            return {
                "error": "Multi-search system not available",
                "query": query,
                "results": []
            }
        
        try:
            # Timeout adapté selon le type de recherche (meilleures pratiques 2025)
            search_timeout = 90.0 if search_type == "deep" else 45.0
            
            manager = MultiSearchManagerMCP()
            result = await asyncio.wait_for(
                manager.smart_search(
                    query=query,
                    search_type=search_type,
                    count=count,
                    privacy_preference=privacy_preference
                ),
                timeout=search_timeout
            )
            await manager.close()
            return result
            
        except asyncio.TimeoutError:
            self.logger.error(f"Search timeout after {search_timeout}s for query: {query[:50]}...")
            return {
                "error": f"Search timeout after {search_timeout}s",
                "query": query,
                "results": []
            }
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            return {
                "error": str(e),
                "query": query,
                "results": []
            }
    
    async def search_parallel(self, query: str, providers: List[str] = None, 
                             count: int = 5) -> Dict[str, Any]:
        """Recherche parallèle sur plusieurs providers - timeout et stabilité 2025"""
        if not MULTI_SEARCH_AVAILABLE:
            return {
                "error": "Multi-search system not available",
                "query": query,
                "combined_results": []
            }
        
        try:
            # Timeout adapté pour recherche parallèle selon meilleures pratiques
            parallel_timeout = 120.0  # Plus long car multiple providers
            
            manager = MultiSearchManagerMCP()
            result = await asyncio.wait_for(
                manager.parallel_search(
                    query=query,
                    providers=providers,
                    count=count
                ),
                timeout=parallel_timeout
            )
            await manager.close()
            return result
            
        except asyncio.TimeoutError:
            self.logger.error(f"Parallel search timeout after {parallel_timeout}s for query: {query[:50]}...")
            return {
                "error": f"Parallel search timeout after {parallel_timeout}s",
                "query": query,
                "combined_results": []
            }
        except Exception as e:
            self.logger.error(f"Parallel search failed: {e}")
            return {
                "error": str(e),
                "query": query,
                "combined_results": []
            }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.servers: Dict[str, MCPServer] = {}
        self.processes: Dict[str, subprocess.Popen] = {}
        
    def register_server(self, server: MCPServer):
        """Enregistre un serveur MCP"""
        self.servers[server.name] = server
        self.logger.info(f"🔌 [MCP] Serveur {server.name} enregistré : {server.description}")
    
    async def start_server(self, server_name: str, startup_timeout: float = 30.0) -> bool:
        """Démarre un serveur MCP avec monitoring de santé selon meilleures pratiques 2025"""
        try:
            if server_name not in self.servers:
                self.logger.error(f"❌ [MCP] Serveur {server_name} non trouvé")
                return False
            
            server = self.servers[server_name]
            
            # Vérifier si un processus existe déjà
            if server_name in self.processes:
                existing_process = self.processes[server_name]
                if existing_process.poll() is None:  # Processus encore vivant
                    self.logger.info(f"✅ [MCP] Serveur {server_name} déjà actif (PID: {existing_process.pid})")
                    return True
                else:
                    self.logger.warning(f"⚠️ [MCP] Nettoyage processus mort {server_name}")
                    del self.processes[server_name]
            
            # Configuration environnement robuste selon recherche internet 2025
            env = {**os.environ, **server.env}
            
            # Pour Node.js/nvm selon problèmes doc 2025
            if server.command in ['node', 'npm', 'npx']:
                if 'NVM_DIR' in os.environ and 'PATH' in env:
                    nvm_node_path = f"{os.environ['NVM_DIR']}/current/bin"
                    env['PATH'] = f"{nvm_node_path}:{env['PATH']}"
                    self.logger.info(f"🔧 [MCP] Configuration NVM pour {server_name}")
            
            # Démarrer le processus du serveur MCP avec configuration optimisée
            process = subprocess.Popen(
                [server.command] + server.args,
                env=env,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0,  # Unbuffered pour réactivité
                preexec_fn=os.setsid if hasattr(os, 'setsid') else None  # Process group pour cleanup
            )
            
            self.processes[server_name] = process
            self.logger.info(f"✅ [MCP] Serveur {server_name} démarré (PID: {process.pid})")
            
            # Vérification startup avec timeout selon meilleures pratiques 2025
            startup_success = False
            for check_attempt in range(int(startup_timeout / 2)):
                await asyncio.sleep(2)
                
                # Vérifier que le processus est toujours vivant
                if process.poll() is not None:
                    stderr_output = process.stderr.read() if process.stderr else "N/A"
                    self.logger.error(f"❌ [MCP] Processus {server_name} arrêté prématurément: {stderr_output[:200]}")
                    if server_name in self.processes:
                        del self.processes[server_name]
                    return False
                
                # Test basique de communication selon spec MCP 2025
                try:
                    test_result = await asyncio.wait_for(
                        self.send_request(server_name, "initialize", {
                            "protocolVersion": "2025-03-26",
                            "capabilities": {"roots": {"listChanged": True}}
                        }, timeout=10.0, retry_count=1),
                        timeout=12.0
                    )
                    
                    if test_result is not None:
                        startup_success = True
                        self.logger.info(f"✅ [MCP] Serveur {server_name} répond aux requêtes (startup ok)")
                        break
                        
                except Exception as test_error:
                    self.logger.debug(f"🔍 [MCP] Test startup {server_name}: {test_error}")
                    continue
            
            if not startup_success:
                self.logger.warning(f"⚠️ [MCP] Serveur {server_name} démarré mais ne répond pas encore (timeout {startup_timeout}s)")
                # Ne pas arrêter le serveur, il peut encore devenir réactif
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ [MCP] Erreur démarrage {server_name}: {e}")
            return False
    
    async def send_request(self, server_name: str, method: str, params: Dict[str, Any], 
                          timeout: float = 120.0, retry_count: int = 3) -> Optional[Dict[str, Any]]:
        """Envoie une requête JSON-RPC à un serveur MCP avec timeout et retry selon meilleures pratiques 2025"""
        for attempt in range(retry_count):
            try:
                if server_name not in self.processes:
                    self.logger.error(f"❌ [MCP] Serveur {server_name} non démarré")
                    return None
                
                process = self.processes[server_name]
                
                # Vérifier que le processus est toujours vivant
                if process.poll() is not None:
                    self.logger.error(f"❌ [MCP] Processus {server_name} fermé inattendu (returncode: {process.returncode})")
                    # Nettoyer le processus mort
                    if server_name in self.processes:
                        del self.processes[server_name]
                    return None
                
                # Préparer la requête JSON-RPC avec ID unique
                import time
                request = {
                    "jsonrpc": "2.0",
                    "id": int(time.time() * 1000) % 2147483647,  # ID unique basé sur timestamp
                    "method": method,
                    "params": params
                }
                
                # Envoyer la requête avec timeout selon best practices 2025
                request_json = json.dumps(request) + "\n"
                
                # Utiliser asyncio.wait_for pour timeout robuste
                try:
                    # Envoi avec timeout
                    await asyncio.wait_for(
                        asyncio.to_thread(lambda: (
                            process.stdin.write(request_json),
                            process.stdin.flush()
                        )[1]),  # flush() est le retour que nous voulons
                        timeout=5.0  # Timeout envoi court
                    )
                    
                    # Lecture avec timeout principal
                    response_line = await asyncio.wait_for(
                        asyncio.to_thread(process.stdout.readline),
                        timeout=timeout
                    )
                    
                    if not response_line:
                        self.logger.warning(f"⚠️ [MCP] Pas de réponse de {server_name} (tentative {attempt + 1}/{retry_count})")
                        if attempt < retry_count - 1:
                            await asyncio.sleep(2 ** attempt)  # Exponential backoff
                            continue
                        return None
                    
                    response = json.loads(response_line.strip())
                    
                    if "error" in response:
                        error_info = response['error']
                        self.logger.error(f"❌ [MCP] Erreur serveur {server_name}: {error_info}")
                        # Certaines erreurs MCP ne nécessitent pas de retry
                        if isinstance(error_info, dict) and error_info.get('code') in [-32601, -32602]:  # Method not found, Invalid params
                            return None
                        if attempt < retry_count - 1:
                            await asyncio.sleep(1.5 ** attempt)
                            continue
                        return None
                    
                    # Succès - log performance si lent
                    if timeout > 30:
                        self.logger.info(f"✅ [MCP] Requête {method} réussie après {attempt + 1} tentative(s)")
                    
                    return response.get("result")
                    
                except asyncio.TimeoutError:
                    self.logger.warning(f"⏱️ [MCP] Timeout {timeout}s sur {server_name}.{method} (tentative {attempt + 1}/{retry_count})")
                    if attempt < retry_count - 1:
                        timeout *= 1.5  # Augmenter timeout progressivement
                        await asyncio.sleep(2 ** attempt)
                        continue
                    return None
                    
            except json.JSONDecodeError as e:
                self.logger.error(f"❌ [MCP] JSON invalide de {server_name}: {e}")
                if attempt < retry_count - 1:
                    await asyncio.sleep(1)
                    continue
                return None
            except Exception as e:
                self.logger.error(f"❌ [MCP] Erreur requête {server_name}.{method} (tentative {attempt + 1}/{retry_count}): {e}")
                if attempt < retry_count - 1:
                    await asyncio.sleep(1.5 ** attempt)
                    continue
                return None
        
        self.logger.error(f"❌ [MCP] Échec définitif après {retry_count} tentatives pour {server_name}.{method}")
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
            
            # Envoyer la requête au serveur Browserbase avec timeout adapté selon action
            timeout = 180.0 if action in ["screenshot", "extract", "navigate"] else 120.0
            result = await self.send_request("browserbase_web_automation", action, params, timeout=timeout)
            
            if result:
                self.logger.info(f"✅ [MCP] Navigation {action} réussie : {url}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ [MCP] Erreur navigation web: {e}")
            return None
    
    async def stop_server(self, server_name: str, graceful_timeout: float = 10.0):
        """Arrête un serveur MCP avec shutdown gracieux selon meilleures pratiques 2025"""
        try:
            if server_name not in self.processes:
                self.logger.info(f"🔍 [MCP] Serveur {server_name} déjà arrêté")
                return
                
            process = self.processes[server_name]
            
            # Vérifier si le processus est encore vivant
            if process.poll() is not None:
                self.logger.info(f"🔍 [MCP] Processus {server_name} déjà terminé (returncode: {process.returncode})")
                del self.processes[server_name]
                return
            
            # Shutdown gracieux selon spec MCP 2025
            try:
                # Envoyer notification de shutdown si possible
                shutdown_request = {
                    "jsonrpc": "2.0",
                    "method": "notifications/cancelled",
                    "params": {"reason": "server_shutdown"}
                }
                process.stdin.write(json.dumps(shutdown_request) + "\n")
                process.stdin.flush()
                process.stdin.close()  # Fermer stdin proprement
                
                # Attendre arrêt gracieux
                try:
                    await asyncio.wait_for(
                        asyncio.to_thread(process.wait),
                        timeout=graceful_timeout
                    )
                    self.logger.info(f"✅ [MCP] Serveur {server_name} arrêté gracieusement")
                except asyncio.TimeoutError:
                    self.logger.warning(f"⚠️ [MCP] Timeout graceful shutdown {server_name}, force kill")
                    process.terminate()
                    
                    # Force kill si nécessaire
                    try:
                        await asyncio.wait_for(
                            asyncio.to_thread(process.wait),
                            timeout=5.0
                        )
                    except asyncio.TimeoutError:
                        if hasattr(process, 'kill'):
                            process.kill()
                            self.logger.warning(f"🗡️ [MCP] Force kill {server_name}")
                        
            except Exception as shutdown_error:
                self.logger.warning(f"⚠️ [MCP] Erreur shutdown gracieux {server_name}: {shutdown_error}")
                process.terminate()
                process.wait(timeout=5)
            
            # Nettoyer les références
            del self.processes[server_name]
            self.logger.info(f"🛑 [MCP] Serveur {server_name} arrêté et nettoyé")
            
        except Exception as e:
            self.logger.error(f"❌ [MCP] Erreur arrêt {server_name}: {e}")
            # Cleanup forcé en cas d'erreur
            if server_name in self.processes:
                try:
                    self.processes[server_name].kill()
                except:
                    pass
                del self.processes[server_name]
    
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
    
    # Serveur Brave Search pour la recherche web sécurisée
    brave_search_path = Path(__file__).parent.parent.parent / "MCP" / "servers" / "brave_search_mcp.py"
    
    if brave_search_path.exists() and os.getenv("BRAVE_API_KEY"):
        servers.append(MCPServer(
            name="brave_search",
            command="python3", 
            args=[str(brave_search_path)],
            env={
                "BRAVE_API_KEY": os.getenv("BRAVE_API_KEY", ""),
                "BRAVE_API_KEY_BACKUP": os.getenv("BRAVE_API_KEY_BACKUP", "")
            },
            description="Recherche web sécurisée et sans tracking via Brave Search API",
            capabilities=["web_search", "news_search", "image_search", "video_search", "privacy_search"]
        ))
    
    return servers

# Import os à ajouter en haut du fichier
import os

# Multi-Search MCP Integration
try:
    sys.path.append('/home/enzo/Projet-Jarvis/MCP/servers')
    from multi_search_manager import MultiSearchManagerMCP
    MULTI_SEARCH_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Multi-Search MCP not available: {e}")
    MULTI_SEARCH_AVAILABLE = False
