#!/usr/bin/env python3
"""
Brave Search MCP Server pour Jarvis
Intégration avec Brave Search API pour recherche web sécurisée
"""

import asyncio
import json
import os
import logging
from typing import Dict, Any, List, Optional
import httpx
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BraveSearchMCP:
    """Serveur MCP pour Brave Search API"""
    
    def __init__(self):
        """Initialisation du serveur MCP Brave Search"""
        self.api_key = os.getenv("BRAVE_API_KEY")
        self.api_key_backup = os.getenv("BRAVE_API_KEY_BACKUP") 
        self.base_url = "https://api.search.brave.com/res/v1"
        self.client = None
        self.current_api_key = self.api_key
        
        if not self.api_key:
            raise ValueError("BRAVE_API_KEY not found in environment variables")
            
        logger.info(" Brave Search MCP Server initialized")
        logger.info(f" Using API key: {self.api_key[:10]}...")
        
    async def _ensure_client(self):
        """Assurer la présence du client HTTP"""
        if self.client is None or self.client.is_closed:
            self.client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                headers={
                    "Accept": "application/json",
                    "Accept-Encoding": "gzip",
                    "X-Subscription-Token": self.current_api_key
                }
            )
    
    async def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Faire une requête à l'API Brave Search avec fallback"""
        await self._ensure_client()
        
        try:
            # Tentative avec clé principale
            response = await self.client.get(f"{self.base_url}/{endpoint}", params=params)
            
            if response.status_code == 401 and self.api_key_backup:
                # Fallback vers clé backup si erreur auth
                logger.warning(" Switching to backup API key")
                self.current_api_key = self.api_key_backup
                self.client.headers["X-Subscription-Token"] = self.current_api_key
                response = await self.client.get(f"{self.base_url}/{endpoint}", params=params)
            
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f" HTTP error {e.response.status_code}: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f" Request error: {e}")
            raise
    
    async def web_search(self, query: str, count: int = 10, search_lang: str = "fr", 
                        country: str = "FR", safesearch: str = "moderate", 
                        freshness: str = "") -> Dict[str, Any]:
        """Recherche web avec Brave Search API"""
        logger.info(f" Web search: '{query}' (count={count}, lang={search_lang})")
        
        params = {
            "q": query,
            "count": min(count, 20),
            "search_lang": search_lang,
            "country": country,
            "safesearch": safesearch
        }
        
        if freshness:
            params["freshness"] = freshness
            
        try:
            result = await self._make_request("web/search", params)
            
            # Format des résultats pour Jarvis
            formatted_results = {
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "total_results": len(result.get("web", {}).get("results", [])),
                "results": []
            }
            
            for item in result.get("web", {}).get("results", []):
                formatted_results["results"].append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "description": item.get("description", ""),
                    "published": item.get("age", ""),
                    "language": item.get("language", search_lang),
                    "source_domain": item.get("url", "").split("/")[2] if item.get("url") else ""
                })
                
            logger.info(f" Found {formatted_results['total_results']} web results")
            return formatted_results
            
        except Exception as e:
            logger.error(f" Web search failed: {e}")
            return {
                "query": query,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "results": []
            }
    
    async def news_search(self, query: str, count: int = 10, country: str = "FR", 
                         search_lang: str = "fr", spellcheck: bool = True) -> Dict[str, Any]:
        """Recherche d'actualités avec Brave Search API"""
        logger.info(f" News search: '{query}' (count={count}, country={country})")
        
        params = {
            "q": query,
            "count": min(count, 20),
            "country": country,
            "search_lang": search_lang,
            "spellcheck": spellcheck
        }
        
        try:
            result = await self._make_request("news/search", params)
            
            formatted_results = {
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "total_articles": len(result.get("results", [])),
                "articles": []
            }
            
            for article in result.get("results", []):
                formatted_results["articles"].append({
                    "title": article.get("title", ""),
                    "url": article.get("url", ""),
                    "description": article.get("description", ""),
                    "published_date": article.get("age", ""),
                    "source": article.get("url", "").split("/")[2] if article.get("url") else "",
                    "breaking": article.get("breaking", False),
                    "language": search_lang
                })
                
            logger.info(f" Found {formatted_results['total_articles']} news articles")
            return formatted_results
            
        except Exception as e:
            logger.error(f" News search failed: {e}")
            return {
                "query": query,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "articles": []
            }
    
    async def image_search(self, query: str, count: int = 10, search_lang: str = "fr",
                          country: str = "FR", safesearch: str = "strict") -> Dict[str, Any]:
        """Recherche d'images avec Brave Search API"""
        logger.info(f" Image search: '{query}' (count={count}, safesearch={safesearch})")
        
        params = {
            "q": query,
            "count": min(count, 20),
            "search_lang": search_lang,
            "country": country,
            "safesearch": safesearch
        }
        
        try:
            result = await self._make_request("images/search", params)
            
            formatted_results = {
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "total_images": len(result.get("results", [])),
                "images": []
            }
            
            for image in result.get("results", []):
                formatted_results["images"].append({
                    "title": image.get("title", ""),
                    "url": image.get("url", ""),
                    "thumbnail": image.get("thumbnail", {}).get("src", ""),
                    "source_url": image.get("source", ""),
                    "width": image.get("properties", {}).get("width", 0),
                    "height": image.get("properties", {}).get("height", 0),
                    "format": image.get("properties", {}).get("format", ""),
                    "source_domain": image.get("source", "").split("/")[2] if image.get("source") else ""
                })
                
            logger.info(f" Found {formatted_results['total_images']} images")
            return formatted_results
            
        except Exception as e:
            logger.error(f" Image search failed: {e}")
            return {
                "query": query,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "images": []
            }
    
    async def video_search(self, query: str, count: int = 10, search_lang: str = "fr",
                          country: str = "FR", safesearch: str = "moderate") -> Dict[str, Any]:
        """Recherche de vidéos avec Brave Search API"""
        logger.info(f" Video search: '{query}' (count={count})")
        
        params = {
            "q": query,
            "count": min(count, 20),
            "search_lang": search_lang,
            "country": country,
            "safesearch": safesearch
        }
        
        try:
            result = await self._make_request("videos/search", params)
            
            formatted_results = {
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "total_videos": len(result.get("results", [])),
                "videos": []
            }
            
            for video in result.get("results", []):
                formatted_results["videos"].append({
                    "title": video.get("title", ""),
                    "url": video.get("url", ""),
                    "description": video.get("description", ""),
                    "thumbnail": video.get("thumbnail", {}).get("src", ""),
                    "duration": video.get("duration", ""),
                    "published_date": video.get("age", ""),
                    "view_count": video.get("views", ""),
                    "source": video.get("url", "").split("/")[2] if video.get("url") else "",
                    "platform": self._detect_video_platform(video.get("url", ""))
                })
                
            logger.info(f" Found {formatted_results['total_videos']} videos")
            return formatted_results
            
        except Exception as e:
            logger.error(f" Video search failed: {e}")
            return {
                "query": query,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "videos": []
            }
    
    def _detect_video_platform(self, url: str) -> str:
        """Détecter la plateforme vidéo depuis l'URL"""
        if "youtube.com" in url or "youtu.be" in url:
            return "YouTube"
        elif "vimeo.com" in url:
            return "Vimeo"
        elif "dailymotion.com" in url:
            return "Dailymotion"
        elif "twitch.tv" in url:
            return "Twitch"
        else:
            return "Unknown"
    
    async def close(self):
        """Fermer les connexions"""
        if self.client and not self.client.is_closed:
            await self.client.aclose()
            logger.info(" Brave Search MCP client closed")

# Point d'entrée principal
async def main():
    """Fonction principale du serveur MCP"""
    brave_mcp = BraveSearchMCP()
    
    try:
        # Test de base
        result = await brave_mcp.web_search("Jarvis AI assistant", count=5)
        print("Test search result:", json.dumps(result, indent=2, ensure_ascii=False))
        
    except Exception as e:
        logger.error(f" MCP Server error: {e}")
    finally:
        await brave_mcp.close()

if __name__ == "__main__":
    asyncio.run(main())