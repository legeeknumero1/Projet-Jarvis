#!/usr/bin/env python3
"""
Google Custom Search MCP Server pour Jarvis
Recherche Google avec API officielle
"""

import asyncio
import json
import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleSearchMCP:
    """Serveur MCP pour Google Custom Search API"""
    
    def __init__(self):
        """Initialisation du serveur MCP Google Search"""
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID") 
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        self.client = None
        
        if not self.api_key or not self.search_engine_id:
            logger.warning("⚠️  Google API key or Search Engine ID missing")
            logger.info("📋 To setup: https://developers.google.com/custom-search/v1/introduction")
            # Utiliser des valeurs demo pour les tests
            self.api_key = "demo_key"
            self.search_engine_id = "demo_cx"
        else:
            logger.info("🔍 Google Custom Search MCP Server initialized")
            logger.info(f"🔑 Using API key: {self.api_key[:10]}...")
            logger.info(f"🔍 Search Engine ID: {self.search_engine_id[:10]}...")
    
    async def _ensure_client(self):
        """Assurer la présence du client HTTP"""
        if self.client is None or self.client.is_closed:
            self.client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                headers={
                    "Accept": "application/json"
                }
            )
    
    async def _make_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Faire une requête à l'API Google Custom Search"""
        await self._ensure_client()
        
        try:
            # Ajouter les paramètres requis
            params.update({
                "key": self.api_key,
                "cx": self.search_engine_id
            })
            
            response = await self.client.get(self.base_url, params=params)
            
            if response.status_code == 400:
                logger.error("❌ Bad request - check API key and search engine ID")
                raise Exception("Invalid Google API configuration")
            elif response.status_code == 403:
                logger.error("❌ Quota exceeded or API key invalid")
                raise Exception("Google API quota exceeded")
                
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ HTTP error {e.response.status_code}: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"❌ Request error: {e}")
            raise
    
    async def web_search(self, query: str, count: int = 10, language: str = "lang_fr",
                        country: str = "countryFR", safe_search: str = "active",
                        date_restrict: str = "", site_search: str = "") -> Dict[str, Any]:
        """Recherche web avec Google Custom Search API"""
        logger.info(f"🔍 Google web search: '{query}' (count={count}, lang={language})")
        
        params = {
            "q": query,
            "num": min(count, 10),  # Google limite à 10 par requête
            "lr": language,  # lang_fr, lang_en, etc.
            "gl": country.replace("country", "").lower() if country.startswith("country") else country,
            "safe": safe_search  # active, off
        }
        
        if date_restrict:
            params["dateRestrict"] = date_restrict  # d1, w1, m1, y1, etc.
        
        if site_search:
            params["siteSearch"] = site_search
        
        try:
            result = await self._make_request(params)
            
            search_info = result.get("searchInformation", {})
            
            formatted_results = {
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "provider": "Google Custom Search",
                "total_results": int(search_info.get("totalResults", 0)),
                "search_time": float(search_info.get("searchTime", 0)),
                "results": []
            }
            
            for item in result.get("items", []):
                # Extraire les informations d'image si disponibles
                pagemap = item.get("pagemap", {})
                image_info = {}
                
                if "cse_image" in pagemap:
                    image_info = pagemap["cse_image"][0] if pagemap["cse_image"] else {}
                
                formatted_results["results"].append({
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "description": item.get("snippet", ""),
                    "display_url": item.get("displayLink", ""),
                    "formatted_url": item.get("formattedUrl", ""),
                    "cache_id": item.get("cacheId", ""),
                    "image": {
                        "src": image_info.get("src", ""),
                        "width": image_info.get("width", ""),
                        "height": image_info.get("height", "")
                    } if image_info else None,
                    "source": "Google"
                })
            
            logger.info(f"✅ Found {len(formatted_results['results'])} Google results")
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Google search failed: {e}")
            return {
                "query": query,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "results": []
            }
    
    async def image_search(self, query: str, count: int = 10, image_size: str = "",
                          image_type: str = "", safe_search: str = "active") -> Dict[str, Any]:
        """Recherche d'images avec Google Custom Search"""
        logger.info(f"🖼️ Google image search: '{query}' (count={count})")
        
        params = {
            "q": query,
            "searchType": "image",
            "num": min(count, 10),
            "safe": safe_search
        }
        
        if image_size:
            params["imgSize"] = image_size  # icon, small, medium, large, xlarge, xxlarge, huge
        
        if image_type:
            params["imgType"] = image_type  # clipart, face, lineart, stock, photo, animated
        
        try:
            result = await self._make_request(params)
            
            formatted_results = {
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "provider": "Google Images",
                "total_images": len(result.get("items", [])),
                "images": []
            }
            
            for item in result.get("items", []):
                image_info = item.get("image", {})
                
                formatted_results["images"].append({
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "thumbnail": image_info.get("thumbnailLink", ""),
                    "context_url": image_info.get("contextLink", ""),
                    "width": image_info.get("width", 0),
                    "height": image_info.get("height", 0),
                    "byte_size": image_info.get("byteSize", 0),
                    "thumbnail_width": image_info.get("thumbnailWidth", 0),
                    "thumbnail_height": image_info.get("thumbnailHeight", 0),
                    "source_domain": item.get("displayLink", ""),
                    "mime_type": item.get("mime", "")
                })
            
            logger.info(f"✅ Found {formatted_results['total_images']} Google images")
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Google image search failed: {e}")
            return {
                "query": query,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "images": []
            }
    
    async def news_search(self, query: str, count: int = 10, sort_by: str = "date") -> Dict[str, Any]:
        """Recherche d'actualités via Google (site search sur sites news)"""
        logger.info(f"📰 Google news search: '{query}' (count={count})")
        
        # Rechercher sur des sites d'actualités populaires
        news_sites = [
            "lemonde.fr", "lefigaro.fr", "franceinfo.fr", "bfmtv.com",
            "reuters.com", "bbc.com", "cnn.com", "france24.com"
        ]
        
        # Créer une requête avec OR pour les sites
        site_query = f"{query} site:" + " OR site:".join(news_sites[:4])  # Limiter pour ne pas dépasser la limite
        
        params = {
            "q": site_query,
            "num": min(count, 10),
            "dateRestrict": "w1",  # Dernière semaine
            "sort": f"date:{sort_by}" if sort_by == "date" else ""
        }
        
        try:
            result = await self._make_request(params)
            
            formatted_results = {
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "provider": "Google News Search",
                "search_period": "last_week",
                "total_articles": len(result.get("items", [])),
                "articles": []
            }
            
            for item in result.get("items", []):
                formatted_results["articles"].append({
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "description": item.get("snippet", ""),
                    "source": item.get("displayLink", ""),
                    "published_date": "recent",  # Google ne fournit pas de date précise
                    "cache_id": item.get("cacheId", ""),
                    "verified": True
                })
            
            logger.info(f"✅ Found {formatted_results['total_articles']} news articles")
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Google news search failed: {e}")
            return {
                "query": query,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "articles": []
            }
    
    async def site_search(self, query: str, site: str, count: int = 10) -> Dict[str, Any]:
        """Recherche sur un site spécifique"""
        logger.info(f"🌐 Google site search: '{query}' on {site}")
        
        params = {
            "q": query,
            "siteSearch": site,
            "num": min(count, 10)
        }
        
        try:
            result = await self._make_request(params)
            
            formatted_results = {
                "query": query,
                "site": site,
                "timestamp": datetime.now().isoformat(),
                "provider": f"Google Site Search ({site})",
                "total_results": len(result.get("items", [])),
                "results": []
            }
            
            for item in result.get("items", []):
                formatted_results["results"].append({
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "description": item.get("snippet", ""),
                    "display_url": item.get("displayLink", ""),
                    "site_verified": True
                })
            
            logger.info(f"✅ Found {formatted_results['total_results']} results on {site}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Site search failed: {e}")
            return {
                "query": query,
                "site": site,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "results": []
            }
    
    async def close(self):
        """Fermer les connexions"""
        if self.client and not self.client.is_closed:
            await self.client.aclose()
            logger.info("🔍 Google Search MCP client closed")

# Point d'entrée principal
async def main():
    """Fonction principale du serveur MCP"""
    google_mcp = GoogleSearchMCP()
    
    try:
        # Test de base (ne fonctionnera qu'avec de vraies clés)
        result = await google_mcp.web_search("Jarvis AI assistant", count=3)
        print("Test search result:", json.dumps(result, indent=2, ensure_ascii=False))
        
    except Exception as e:
        logger.error(f"❌ MCP Server error: {e}")
    finally:
        await google_mcp.close()

if __name__ == "__main__":
    asyncio.run(main())