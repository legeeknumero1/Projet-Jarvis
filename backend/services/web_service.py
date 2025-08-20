"""
Service Web pour Jarvis utilisant MCP (Model Context Protocol)
Permet à Jarvis d'accéder à internet via le serveur MCP Browserbase
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from integration.mcp_client import MCPClient, create_default_mcp_servers

class WebService:
    """Service web de Jarvis utilisant MCP pour l'accès internet"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.mcp_client = MCPClient()
        self.is_initialized = False
        
    async def initialize(self) -> bool:
        """Initialise le service web avec les serveurs MCP"""
        try:
            # Enregistrer les serveurs MCP par défaut
            servers = create_default_mcp_servers()
            self.logger.info(f"🔌 [WebService] {len(servers)} serveurs MCP trouvés")
            
            for server in servers:
                self.mcp_client.register_server(server)
                self.logger.info(f"📡 [WebService] Serveur {server.name} enregistré")
            
            # Démarrer le serveur Browserbase si disponible
            if "browserbase_web_automation" in [s.name for s in servers]:
                success = await self.mcp_client.start_server("browserbase_web_automation")
                if success:
                    self.logger.info("✅ [WebService] Serveur MCP Browserbase démarré")
                    self.is_initialized = True
                else:
                    self.logger.error("❌ [WebService] Échec démarrage serveur Browserbase")
                    return False
            else:
                self.logger.warning("⚠️  [WebService] Serveur Browserbase non trouvé")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ [WebService] Erreur initialisation: {e}")
            return False
    
    async def search_web(self, query: str) -> Optional[Dict[str, Any]]:
        """Recherche sur le web"""
        if not self.is_initialized:
            self.logger.error("❌ [WebService] Service non initialisé")
            return None
        
        try:
            # Utiliser DuckDuckGo pour la recherche
            search_url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}"
            
            result = await self.mcp_client.browse_web(
                search_url, 
                "extract",
                selector=".results .result",
                instruction="Extraire les résultats de recherche"
            )
            
            if result:
                self.logger.info(f"✅ [WebService] Recherche web réussie: {query}")
                return {
                    "query": query,
                    "url": search_url,
                    "results": result
                }
            else:
                self.logger.warning(f"⚠️  [WebService] Pas de résultats pour: {query}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ [WebService] Erreur recherche web: {e}")
            return None
    
    async def get_web_content(self, url: str) -> Optional[Dict[str, Any]]:
        """Récupère le contenu d'une page web"""
        if not self.is_initialized:
            self.logger.error("❌ [WebService] Service non initialisé")
            return None
        
        try:
            # Naviguer vers l'URL et extraire le contenu
            result = await self.mcp_client.browse_web(
                url, 
                "extract",
                instruction="Extraire le contenu principal de la page"
            )
            
            if result:
                self.logger.info(f"✅ [WebService] Contenu récupéré: {url}")
                return {
                    "url": url,
                    "content": result,
                    "timestamp": asyncio.get_event_loop().time()
                }
            else:
                self.logger.warning(f"⚠️  [WebService] Impossible de récupérer: {url}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ [WebService] Erreur récupération contenu: {e}")
            return None
    
    async def take_screenshot(self, url: str, full_page: bool = True) -> Optional[Dict[str, Any]]:
        """Prend une capture d'écran d'une page web"""
        if not self.is_initialized:
            self.logger.error("❌ [WebService] Service non initialisé")
            return None
        
        try:
            result = await self.mcp_client.browse_web(
                url,
                "screenshot", 
                full_page=full_page
            )
            
            if result:
                self.logger.info(f"✅ [WebService] Capture d'écran prise: {url}")
                return {
                    "url": url,
                    "screenshot": result,
                    "full_page": full_page,
                    "timestamp": asyncio.get_event_loop().time()
                }
            else:
                self.logger.warning(f"⚠️  [WebService] Impossible de capturer: {url}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ [WebService] Erreur capture d'écran: {e}")
            return None
    
    async def interact_with_page(self, url: str, instruction: str) -> Optional[Dict[str, Any]]:
        """Interagit avec une page web selon les instructions"""
        if not self.is_initialized:
            self.logger.error("❌ [WebService] Service non initialisé")
            return None
        
        try:
            # Naviguer d'abord vers la page
            await self.mcp_client.browse_web(url, "navigate")
            
            # Effectuer l'action demandée
            result = await self.mcp_client.browse_web(
                url,
                "act",
                instruction=instruction
            )
            
            if result:
                self.logger.info(f"✅ [WebService] Interaction réussie: {url}")
                return {
                    "url": url,
                    "instruction": instruction,
                    "result": result,
                    "timestamp": asyncio.get_event_loop().time()
                }
            else:
                self.logger.warning(f"⚠️  [WebService] Interaction échouée: {url}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ [WebService] Erreur interaction: {e}")
            return None
    
    async def get_capabilities(self) -> Dict[str, List[str]]:
        """Retourne les capacités web disponibles"""
        if not self.is_initialized:
            return {}
        
        return self.mcp_client.get_available_capabilities()
    
    async def shutdown(self):
        """Arrête le service web et ferme les connexions MCP"""
        try:
            await self.mcp_client.stop_all_servers()
            self.is_initialized = False
            self.logger.info("🛑 [WebService] Service web arrêté")
        except Exception as e:
            self.logger.error(f"❌ [WebService] Erreur arrêt: {e}")

# Instance globale du service web
web_service = WebService()

async def get_web_service() -> WebService:
    """Récupère l'instance du service web (singleton)"""
    if not web_service.is_initialized:
        await web_service.initialize()
    return web_service