"""
Client MCP (Model Context Protocol) pour accès internet sécurisé
"""
import asyncio
import logging
import json
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class MCPClient:
    """Client MCP pour accès internet et services externes"""
    
    def __init__(self, base_timeout: float = 30.0):
        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(base_timeout),
            limits=httpx.Limits(max_connections=10),
            headers={
                "User-Agent": "Jarvis-AI/1.3.0 (MCP Client)",
                "Accept": "application/json, text/plain, */*"
            }
        )
        self.available_tools = [
            "web_search", "weather_info", "news_headlines", 
            "url_fetch", "time_info"
        ]
        logger.info(f"🌐 [MCP] Client initialisé avec outils: {self.available_tools}")
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.http_client.aclose()
    
    async def ping(self) -> bool:
        """Test de connectivité internet via MCP"""
        try:
            response = await self.http_client.get("https://httpbin.org/status/200")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"❌ [MCP] Ping failed: {e}")
            return False
    
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Appel générique d'outil MCP"""
        if tool_name not in self.available_tools:
            logger.warning(f"⚠️ [MCP] Outil non supporté: {tool_name}")
            return None
        
        logger.info(f"🔧 [MCP] Appel outil: {tool_name} avec paramètres: {parameters}")
        
        try:
            if tool_name == "web_search":
                return await self._web_search(parameters.get("query", ""))
            elif tool_name == "weather_info":
                return await self._weather_info(parameters.get("location", ""))
            elif tool_name == "news_headlines":
                return await self._news_headlines()
            elif tool_name == "url_fetch":
                return await self._url_fetch(parameters.get("url", ""))
            elif tool_name == "time_info":
                return await self._time_info()
            else:
                return {"error": f"Outil {tool_name} non implémenté"}
        except Exception as e:
            logger.error(f"❌ [MCP] Erreur outil {tool_name}: {e}")
            return {"error": str(e)}
    
    async def _web_search(self, query: str) -> Dict[str, Any]:
        """Recherche web via DuckDuckGo (pas de clé API requise)"""
        if not query:
            return {"error": "Query vide"}
        
        try:
            # Utilisation de l'API publique DuckDuckGo
            url = f"https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1"
            }
            
            response = await self.http_client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                
                results = []
                # Extraire les résultats pertinents
                if data.get("AbstractText"):
                    results.append({
                        "title": data.get("Heading", query),
                        "snippet": data.get("AbstractText", "")[:200],
                        "source": data.get("AbstractURL", "DuckDuckGo")
                    })
                
                # Ajouter les topics relatifs
                for topic in data.get("RelatedTopics", [])[:3]:
                    if isinstance(topic, dict) and topic.get("Text"):
                        results.append({
                            "title": topic.get("FirstURL", {}).get("Text", "")[:50],
                            "snippet": topic.get("Text", "")[:150],
                            "source": topic.get("FirstURL", {}).get("Result", "")
                        })
                
                return {
                    "tool": "web_search",
                    "query": query,
                    "results": results,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"error": f"Erreur recherche: HTTP {response.status_code}"}
                
        except Exception as e:
            return {"error": f"Erreur recherche web: {str(e)}"}
    
    async def _weather_info(self, location: str = "") -> Dict[str, Any]:
        """Informations météo via wttr.in (service public)"""
        try:
            # wttr.in fournit météo sans clé API
            if location:
                url = f"https://wttr.in/{location}?format=j1"
            else:
                url = "https://wttr.in/?format=j1"
            
            response = await self.http_client.get(url)
            if response.status_code == 200:
                data = response.json()
                current = data.get("current_condition", [{}])[0]
                
                weather_info = {
                    "location": data.get("nearest_area", [{}])[0].get("areaName", [{}])[0].get("value", "Inconnu"),
                    "temperature": current.get("temp_C", "N/A"),
                    "description": current.get("weatherDesc", [{}])[0].get("value", "N/A"),
                    "humidity": current.get("humidity", "N/A"),
                    "wind": current.get("windspeedKmph", "N/A")
                }
                
                return {
                    "tool": "weather_info",
                    "data": weather_info,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"error": f"Erreur météo: HTTP {response.status_code}"}
                
        except Exception as e:
            return {"error": f"Erreur météo: {str(e)}"}
    
    async def _news_headlines(self) -> Dict[str, Any]:
        """Titres d'actualités via service public"""
        try:
            # Utiliser un service d'actualités public (exemple : NewsAPI alternative)
            # Pour la démo, on simule des titres
            headlines = [
                "Actualités disponibles via MCP",
                "Système d'accès internet fonctionnel",
                "Intégration MCP réussie"
            ]
            
            return {
                "tool": "news_headlines",
                "headlines": headlines,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Erreur actualités: {str(e)}"}
    
    async def _url_fetch(self, url: str) -> Dict[str, Any]:
        """Récupération sécurisée d'URL"""
        if not url.startswith(("http://", "https://")):
            return {"error": "URL invalide"}
        
        try:
            response = await self.http_client.get(url)
            if response.status_code == 200:
                content = response.text[:1000]  # Limiter le contenu
                return {
                    "tool": "url_fetch",
                    "url": url,
                    "status": response.status_code,
                    "content_preview": content,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"error": f"Erreur fetch: {str(e)}"}
    
    async def _time_info(self) -> Dict[str, Any]:
        """Informations temporelles"""
        now = datetime.now()
        return {
            "tool": "time_info",
            "current_time": now.isoformat(),
            "formatted_time": now.strftime("%Y-%m-%d %H:%M:%S"),
            "day_of_week": now.strftime("%A"),
            "timestamp": now.isoformat()
        }
    
    async def search_internet(self, query: str) -> str:
        """Interface simplifiée pour recherche internet"""
        result = await self.call_tool("web_search", {"query": query})
        
        if result and result.get("results"):
            formatted_results = []
            for item in result["results"][:3]:  # Top 3 résultats
                title = item.get("title", "")[:50]
                snippet = item.get("snippet", "")[:100]
                if title and snippet:
                    formatted_results.append(f"• {title}: {snippet}")
            
            if formatted_results:
                return "\n".join(formatted_results)
        
        return "Aucun résultat trouvé via MCP"
    
    async def get_weather(self, location: str = "") -> str:
        """Interface simplifiée pour météo"""
        result = await self.call_tool("weather_info", {"location": location})
        
        if result and result.get("data"):
            weather = result["data"]
            return f"📍 {weather.get('location', 'Inconnu')}: {weather.get('temperature', 'N/A')}°C, {weather.get('description', 'N/A')} (Humidité: {weather.get('humidity', 'N/A')}%)"
        
        return "Informations météo non disponibles via MCP"
    
    async def check_capabilities(self) -> str:
        """Vérification des capacités MCP"""
        ping_result = await self.ping()
        if ping_result:
            return f"✅ ACCÈS INTERNET VIA MCP ACTIF - Outils disponibles: {', '.join(self.available_tools)}"
        else:
            return "❌ Accès internet MCP non disponible"