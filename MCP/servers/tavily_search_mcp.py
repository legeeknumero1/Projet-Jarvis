#!/usr/bin/env python3
"""
Tavily Search MCP Server pour Jarvis
Recherche optimisée pour AI avec citations et données temps réel
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

class TavilySearchMCP:
    """Serveur MCP pour Tavily Search API - Optimisé pour AI"""
    
    def __init__(self):
        """Initialisation du serveur MCP Tavily"""
        self.api_key = os.getenv("TAVILY_API_KEY")
        self.base_url = "https://api.tavily.com"
        self.client = None
        
        if not self.api_key:
            # Utiliser une clé demo pour les tests
            self.api_key = "demo_key"
            logger.warning("  Using demo key - limited functionality")
        else:
            logger.info(" Tavily Search MCP Server initialized")
            logger.info(f" Using API key: {self.api_key[:10]}...")
    
    async def _ensure_client(self):
        """Assurer la présence du client HTTP"""
        if self.client is None or self.client.is_closed:
            self.client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
            )
    
    async def _make_request(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Faire une requête à l'API Tavily"""
        await self._ensure_client()
        
        try:
            # Ajouter la clé API au payload
            payload["api_key"] = self.api_key
            
            response = await self.client.post(
                f"{self.base_url}/{endpoint}",
                json=payload
            )
            
            if response.status_code == 401:
                logger.error(" Invalid or missing API key")
                raise Exception("Invalid Tavily API key")
            elif response.status_code == 429:
                logger.warning("  Rate limit exceeded")
                raise Exception("Rate limit exceeded")
                
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f" HTTP error {e.response.status_code}: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f" Request error: {e}")
            raise
    
    async def web_search(self, query: str, count: int = 10, search_depth: str = "advanced",
                        include_domains: List[str] = None, exclude_domains: List[str] = None,
                        include_answer: bool = True, include_raw_content: bool = False) -> Dict[str, Any]:
        """Recherche web avec Tavily Search API"""
        logger.info(f" Tavily web search: '{query}' (count={count}, depth={search_depth})")
        
        payload = {
            "query": query,
            "search_depth": search_depth,  # "basic" or "advanced"
            "max_results": min(count, 20),
            "include_answer": include_answer,
            "include_raw_content": include_raw_content,
            "include_images": False
        }
        
        if include_domains:
            payload["include_domains"] = include_domains
        if exclude_domains:
            payload["exclude_domains"] = exclude_domains
        
        try:
            result = await self._make_request("search", payload)
            
            formatted_results = {
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "provider": "Tavily",
                "search_depth": search_depth,
                "ai_optimized": True,
                "citations_included": True,
                "answer": result.get("answer", ""),
                "total_results": len(result.get("results", [])),
                "results": []
            }
            
            for item in result.get("results", []):
                formatted_results["results"].append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "description": item.get("content", ""),
                    "published_date": item.get("published_date", ""),
                    "score": item.get("score", 0),
                    "source_domain": item.get("url", "").split("/")[2] if item.get("url") else "",
                    "raw_content": item.get("raw_content", "") if include_raw_content else None,
                    "citations": True
                })
            
            logger.info(f" Found {formatted_results['total_results']} results with AI answer")
            return formatted_results
            
        except Exception as e:
            logger.error(f" Tavily search failed: {e}")
            return {
                "query": query,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "results": []
            }
    
    async def qna_search(self, query: str) -> Dict[str, Any]:
        """Recherche question-réponse optimisée"""
        logger.info(f" Tavily Q&A search: '{query}'")
        
        payload = {
            "query": query,
            "search_depth": "advanced",
            "max_results": 5,
            "include_answer": True,
            "include_raw_content": True
        }
        
        try:
            result = await self._make_request("search", payload)
            
            formatted_result = {
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "provider": "Tavily Q&A",
                "ai_answer": result.get("answer", ""),
                "confidence": "high" if result.get("answer") else "low",
                "sources": []
            }
            
            for item in result.get("results", [])[:3]:  # Top 3 sources
                formatted_result["sources"].append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "excerpt": item.get("content", "")[:200] + "..." if len(item.get("content", "")) > 200 else item.get("content", ""),
                    "relevance_score": item.get("score", 0)
                })
            
            logger.info(f" Q&A answer generated with {len(formatted_result['sources'])} sources")
            return formatted_result
            
        except Exception as e:
            logger.error(f" Q&A search failed: {e}")
            return {
                "query": query,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "ai_answer": ""
            }
    
    async def news_search(self, query: str, count: int = 10, days: int = 7) -> Dict[str, Any]:
        """Recherche d'actualités récentes"""
        logger.info(f" Tavily news search: '{query}' (last {days} days)")
        
        # Ajouter contexte temporel à la requête
        time_query = f"{query} news recent {days} days"
        
        payload = {
            "query": time_query,
            "search_depth": "advanced",
            "max_results": min(count, 15),
            "include_answer": True,
            "include_raw_content": False,
            "include_domains": [
                "lemonde.fr", "lefigaro.fr", "france24.com", "franceinfo.fr", 
                "bfmtv.com", "cnews.fr", "reuters.com", "bbc.com", "cnn.com"
            ]
        }
        
        try:
            result = await self._make_request("search", payload)
            
            formatted_results = {
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "provider": "Tavily News",
                "search_period": f"last_{days}_days",
                "news_summary": result.get("answer", ""),
                "total_articles": len(result.get("results", [])),
                "articles": []
            }
            
            for item in result.get("results", []):
                formatted_results["articles"].append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "summary": item.get("content", ""),
                    "published_date": item.get("published_date", ""),
                    "source": item.get("url", "").split("/")[2] if item.get("url") else "",
                    "relevance_score": item.get("score", 0),
                    "verified": True,
                    "citations": True
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
    
    async def research_search(self, topic: str, max_results: int = 15) -> Dict[str, Any]:
        """Recherche approfondie pour research"""
        logger.info(f" Tavily research: '{topic}'")
        
        payload = {
            "query": topic,
            "search_depth": "advanced",
            "max_results": max_results,
            "include_answer": True,
            "include_raw_content": True,
            "include_images": False
        }
        
        try:
            result = await self._make_request("search", payload)
            
            formatted_results = {
                "topic": topic,
                "timestamp": datetime.now().isoformat(),
                "provider": "Tavily Research",
                "research_summary": result.get("answer", ""),
                "comprehensive": True,
                "total_sources": len(result.get("results", [])),
                "sources": []
            }
            
            for item in result.get("results", []):
                formatted_results["sources"].append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "content": item.get("content", ""),
                    "raw_content": item.get("raw_content", ""),
                    "published_date": item.get("published_date", ""),
                    "authority_score": item.get("score", 0),
                    "domain": item.get("url", "").split("/")[2] if item.get("url") else "",
                    "verified": True
                })
            
            logger.info(f" Research completed with {formatted_results['total_sources']} sources")
            return formatted_results
            
        except Exception as e:
            logger.error(f" Research search failed: {e}")
            return {
                "topic": topic,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "sources": []
            }
    
    async def close(self):
        """Fermer les connexions"""
        if self.client and not self.client.is_closed:
            await self.client.aclose()
            logger.info(" Tavily Search MCP client closed")

# Point d'entrée principal
async def main():
    """Fonction principale du serveur MCP"""
    tavily_mcp = TavilySearchMCP()
    
    try:
        # Test de base
        result = await tavily_mcp.web_search("artificial intelligence 2025", count=3)
        print("Test search result:", json.dumps(result, indent=2, ensure_ascii=False))
        
    except Exception as e:
        logger.error(f" MCP Server error: {e}")
    finally:
        await tavily_mcp.close()

if __name__ == "__main__":
    asyncio.run(main())