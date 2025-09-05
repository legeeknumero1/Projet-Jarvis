#!/usr/bin/env python3
"""
Multi Search Manager MCP Server pour Jarvis
Gestionnaire intelligent de recherche multi-providers avec fallback automatique
"""

import asyncio
import json
import logging
import os
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import random

# Imports des autres MCP servers
from brave_search_mcp import BraveSearchMCP
from duckduckgo_search_mcp import DuckDuckGoSearchMCP
from tavily_search_mcp import TavilySearchMCP
from google_search_mcp import GoogleSearchMCP

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultiSearchManagerMCP:
    """Gestionnaire intelligent de recherche multi-providers"""
    
    def __init__(self):
        """Initialisation du gestionnaire multi-search"""
        self.providers = {}
        self.fallback_order = []
        
        # Initialiser les providers disponibles
        self._initialize_providers()
        
        logger.info("🔍 Multi Search Manager MCP Server initialized")
        logger.info(f"📊 Active providers: {list(self.providers.keys())}")
    
    def _initialize_providers(self):
        """Initialise tous les providers de recherche disponibles"""
        
        # DuckDuckGo - Toujours disponible (pas de clé API)
        try:
            self.providers["duckduckgo"] = {
                "client": DuckDuckGoSearchMCP(),
                "name": "DuckDuckGo",
                "privacy": "high",
                "cost": "free",
                "rate_limit": "none",
                "requires_api_key": False,
                "status": "available"
            }
            # DuckDuckGo ajouté en dernier car souvent bloqué
            logger.info("✅ DuckDuckGo Search initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize DuckDuckGo: {e}")
        
        # Brave Search
        if os.getenv("BRAVE_API_KEY"):
            try:
                self.providers["brave"] = {
                    "client": BraveSearchMCP(),
                    "name": "Brave Search",
                    "privacy": "high", 
                    "cost": "free_tier",
                    "rate_limit": "2000_per_month",
                    "requires_api_key": True,
                    "status": "available"
                }
                self.fallback_order.append("brave")
                logger.info("✅ Brave Search initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Brave Search: {e}")
        
        # Tavily Search
        if os.getenv("TAVILY_API_KEY"):
            try:
                self.providers["tavily"] = {
                    "client": TavilySearchMCP(),
                    "name": "Tavily Search",
                    "privacy": "medium",
                    "cost": "free_tier",
                    "rate_limit": "1000_per_month",
                    "requires_api_key": True,
                    "status": "available",
                    "ai_optimized": True
                }
                self.fallback_order.append("tavily")
                logger.info("✅ Tavily Search initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Tavily Search: {e}")
        
        # Google Custom Search
        if os.getenv("GOOGLE_API_KEY") and os.getenv("GOOGLE_SEARCH_ENGINE_ID"):
            try:
                self.providers["google"] = {
                    "client": GoogleSearchMCP(),
                    "name": "Google Custom Search",
                    "privacy": "low",
                    "cost": "free_tier",
                    "rate_limit": "100_per_day",
                    "requires_api_key": True,
                    "status": "available"
                }
                self.fallback_order.append("google")
                logger.info("✅ Google Custom Search initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Google Search: {e}")
        
        # Ajouter DuckDuckGo en dernier car souvent bloqué
        if "duckduckgo" in self.providers:
            self.fallback_order.append("duckduckgo")
            
        if not self.providers:
            logger.warning("⚠️  No search providers available!")
    
    def get_best_provider(self, search_type: str = "web", privacy_preference: str = "medium") -> Optional[str]:
        """Sélectionne le meilleur provider selon le type de recherche et préférences"""
        
        if search_type == "qna" and "tavily" in self.providers:
            return "tavily"  # Tavily excellent pour Q&A
        
        if privacy_preference == "high":
            # Priorité aux providers privacy-focused
            for provider in ["duckduckgo", "brave"]:
                if provider in self.providers:
                    return provider
        
        if search_type == "academic" and "google" in self.providers:
            return "google"  # Google bon pour recherche académique
        
        # Fallback vers le premier provider disponible
        return self.fallback_order[0] if self.fallback_order else None
    
    async def smart_search(self, query: str, search_type: str = "web", count: int = 10,
                          privacy_preference: str = "medium", enable_fallback: bool = True,
                          providers_preference: List[str] = None) -> Dict[str, Any]:
        """Recherche intelligente avec sélection automatique du provider"""
        logger.info(f"🧠 Smart search: '{query}' (type={search_type}, privacy={privacy_preference})")
        
        # Sélectionner le provider optimal
        if providers_preference:
            selected_providers = [p for p in providers_preference if p in self.providers]
        else:
            best_provider = self.get_best_provider(search_type, privacy_preference)
            selected_providers = [best_provider] if best_provider else self.fallback_order
        
        # Tenter la recherche avec fallback automatique
        for provider_name in selected_providers:
            if provider_name not in self.providers:
                continue
                
            try:
                provider = self.providers[provider_name]
                client = provider["client"]
                
                logger.info(f"🔍 Trying {provider['name']}...")
                
                if search_type == "web":
                    result = await client.web_search(query, count=count)
                elif search_type == "news":
                    if hasattr(client, 'news_search'):
                        result = await client.news_search(query, count=count)
                    else:
                        result = await client.web_search(f"{query} news", count=count)
                elif search_type == "qna" and hasattr(client, 'qna_search'):
                    result = await client.qna_search(query)
                elif search_type == "images" and hasattr(client, 'image_search'):
                    result = await client.image_search(query, count=count)
                else:
                    result = await client.web_search(query, count=count)
                
                # Enrichir les résultats avec métadonnées du provider
                if result.get("results") or result.get("articles") or result.get("images"):
                    result["provider_used"] = provider_name
                    result["provider_info"] = {
                        "name": provider["name"],
                        "privacy": provider["privacy"],
                        "cost": provider["cost"],
                        "ai_optimized": provider.get("ai_optimized", False)
                    }
                    result["fallback_used"] = provider_name != selected_providers[0]
                    
                    logger.info(f"✅ Search successful with {provider['name']}")
                    return result
                
            except Exception as e:
                logger.warning(f"⚠️  {provider['name']} failed: {e}")
                if not enable_fallback:
                    break
                continue
        
        # Aucun provider n'a fonctionné
        return {
            "query": query,
            "error": "All search providers failed",
            "timestamp": datetime.now().isoformat(),
            "providers_tried": selected_providers,
            "results": []
        }
    
    async def parallel_search(self, query: str, providers: List[str] = None, 
                            count: int = 5) -> Dict[str, Any]:
        """Recherche parallèle sur plusieurs providers"""
        logger.info(f"⚡ Parallel search: '{query}' on multiple providers")
        
        if not providers:
            providers = list(self.providers.keys())[:3]  # Max 3 pour éviter rate limits
        
        # Lancer les recherches en parallèle
        tasks = []
        for provider_name in providers:
            if provider_name in self.providers:
                client = self.providers[provider_name]["client"]
                task = asyncio.create_task(
                    client.web_search(query, count=count),
                    name=provider_name
                )
                tasks.append((provider_name, task))
        
        # Attendre les résultats
        results = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "search_type": "parallel",
            "providers_used": [],
            "combined_results": [],
            "provider_results": {}
        }
        
        for provider_name, task in tasks:
            try:
                provider_result = await task
                
                results["providers_used"].append(provider_name)
                results["provider_results"][provider_name] = provider_result
                
                # Combiner les résultats
                if provider_result.get("results"):
                    for result in provider_result["results"]:
                        result["provider_source"] = provider_name
                        results["combined_results"].append(result)
                
                logger.info(f"✅ {provider_name}: {len(provider_result.get('results', []))} results")
                
            except Exception as e:
                logger.warning(f"⚠️  {provider_name} failed in parallel search: {e}")
                results["provider_results"][provider_name] = {"error": str(e)}
        
        # Trier les résultats combinés par pertinence (simple)
        results["combined_results"] = sorted(
            results["combined_results"],
            key=lambda x: x.get("score", random.random()),  # Score ou random
            reverse=True
        )
        
        results["total_combined_results"] = len(results["combined_results"])
        
        logger.info(f"✅ Parallel search completed: {results['total_combined_results']} total results")
        return results
    
    async def get_provider_status(self) -> Dict[str, Any]:
        """Retourne le statut de tous les providers"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "total_providers": len(self.providers),
            "available_providers": [],
            "fallback_order": self.fallback_order,
            "providers": {}
        }
        
        for name, provider in self.providers.items():
            provider_status = {
                "name": provider["name"],
                "privacy": provider["privacy"],
                "cost": provider["cost"],
                "rate_limit": provider["rate_limit"],
                "requires_api_key": provider["requires_api_key"],
                "status": provider["status"],
                "ai_optimized": provider.get("ai_optimized", False)
            }
            
            status["providers"][name] = provider_status
            if provider["status"] == "available":
                status["available_providers"].append(name)
        
        return status
    
    async def close(self):
        """Fermer toutes les connexions"""
        for provider_name, provider in self.providers.items():
            try:
                if hasattr(provider["client"], 'close'):
                    await provider["client"].close()
                    logger.info(f"🔍 {provider['name']} client closed")
            except Exception as e:
                logger.error(f"❌ Error closing {provider['name']}: {e}")

# Point d'entrée principal
async def main():
    """Fonction principale du gestionnaire multi-search"""
    manager = MultiSearchManagerMCP()
    
    try:
        # Test du statut
        status = await manager.get_provider_status()
        print("Provider Status:", json.dumps(status, indent=2, ensure_ascii=False))
        
        # Test recherche intelligente
        result = await manager.smart_search("artificial intelligence 2025", count=3)
        print("Smart Search Result:", json.dumps(result, indent=2, ensure_ascii=False))
        
        # Test recherche parallèle (si plusieurs providers disponibles)
        if len(manager.providers) > 1:
            parallel_result = await manager.parallel_search("Python programming", count=2)
            print("Parallel Search Result:", json.dumps(parallel_result, indent=2, ensure_ascii=False))
        
    except Exception as e:
        logger.error(f"❌ Manager error: {e}")
    finally:
        await manager.close()

if __name__ == "__main__":
    asyncio.run(main())