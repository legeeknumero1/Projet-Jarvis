#!/usr/bin/env python3
"""
Test script for Multi-Search MCP Integration
Test avec les vraies clés API configurées dans .env
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path

# Ajouter le dossier parent pour les imports
sys.path.append(str(Path(__file__).parent.parent))

# Charger les variables d'environnement depuis .env
from dotenv import load_dotenv
load_dotenv('/home/enzo/Projet-Jarvis/.env')

# Imports des serveurs MCP
sys.path.append(str(Path(__file__).parent / "servers"))
from servers.brave_search_mcp import BraveSearchMCP
from servers.duckduckgo_search_mcp import DuckDuckGoSearchMCP
from servers.tavily_search_mcp import TavilySearchMCP
from servers.google_search_mcp import GoogleSearchMCP
from servers.multi_search_manager import MultiSearchManagerMCP

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_individual_providers():
    """Test chaque provider individuellement"""
    print("=" * 50)
    print(" TESTS INDIVIDUELS DES PROVIDERS")
    print("=" * 50)
    
    # Test Brave Search
    print("\n Test Brave Search API")
    print(f"API Key available: {bool(os.getenv('BRAVE_API_KEY'))}")
    if os.getenv('BRAVE_API_KEY'):
        try:
            brave = BraveSearchMCP()
            result = await brave.web_search("Jarvis AI assistant 2025", count=2)
            print(f" Brave Search: {len(result.get('results', []))} résultats")
            await brave.close()
        except Exception as e:
            print(f" Brave Search failed: {e}")
    else:
        print("  Brave API key not configured")
    
    # Test DuckDuckGo
    print("\n Test DuckDuckGo Search")
    try:
        ddg = DuckDuckGoSearchMCP()
        result = await ddg.web_search("Python programming", count=2)
        print(f" DuckDuckGo: {len(result.get('results', []))} résultats")
    except Exception as e:
        print(f" DuckDuckGo failed: {e}")
    
    # Test Tavily
    print("\n Test Tavily Search")
    print(f"API Key available: {bool(os.getenv('TAVILY_API_KEY'))}")
    if os.getenv('TAVILY_API_KEY'):
        try:
            tavily = TavilySearchMCP()
            result = await tavily.web_search("machine learning trends", count=2)
            print(f" Tavily Search: {len(result.get('results', []))} résultats")
            await tavily.close()
        except Exception as e:
            print(f" Tavily Search failed: {e}")
    else:
        print("  Tavily API key not configured")
    
    # Test Google Custom Search
    print("\n Test Google Custom Search")
    print(f"API Key available: {bool(os.getenv('GOOGLE_API_KEY'))}")
    print(f"Search Engine ID available: {bool(os.getenv('GOOGLE_SEARCH_ENGINE_ID'))}")
    if os.getenv('GOOGLE_API_KEY') and os.getenv('GOOGLE_SEARCH_ENGINE_ID'):
        try:
            google = GoogleSearchMCP()
            result = await google.web_search("data science", count=2)
            print(f" Google Search: {len(result.get('results', []))} résultats")
            await google.close()
        except Exception as e:
            print(f" Google Search failed: {e}")
    else:
        print("  Google API credentials not configured")

async def test_multi_search_manager():
    """Test le gestionnaire multi-search"""
    print("\n" + "=" * 50)
    print(" TEST MULTI-SEARCH MANAGER")
    print("=" * 50)
    
    try:
        manager = MultiSearchManagerMCP()
        
        # Statut des providers
        status = await manager.get_provider_status()
        print(f"\n Providers disponibles: {status['available_providers']}")
        print(f" Ordre de fallback: {status['fallback_order']}")
        
        # Test recherche intelligente
        print("\n Test Smart Search...")
        result = await manager.smart_search("Python FastAPI tutorial", count=3, privacy_preference="high")
        
        if result.get('results'):
            print(f" Smart Search réussie avec {result.get('provider_used', 'unknown')}")
            print(f" {len(result['results'])} résultats trouvés")
            
            # Afficher le premier résultat
            if result['results']:
                first = result['results'][0]
                print(f" Premier résultat: {first.get('title', 'No title')[:50]}...")
        else:
            print(f" Smart Search échouée: {result.get('error', 'Unknown error')}")
        
        # Test recherche parallèle si plusieurs providers
        if len(manager.providers) > 1:
            print("\n Test Parallel Search...")
            parallel_result = await manager.parallel_search("machine learning", count=2)
            print(f" Parallel Search: {parallel_result.get('total_combined_results', 0)} résultats combinés")
            print(f" Providers utilisés: {parallel_result.get('providers_used', [])}")
        
        await manager.close()
        
    except Exception as e:
        print(f" Multi-Search Manager failed: {e}")

async def test_specific_search_types():
    """Test des types de recherche spécifiques"""
    print("\n" + "=" * 50)
    print(" TEST TYPES DE RECHERCHE SPÉCIFIQUES")
    print("=" * 50)
    
    manager = MultiSearchManagerMCP()
    
    if not manager.providers:
        print(" Aucun provider disponible pour les tests")
        return
    
    try:
        # Test Q&A
        print("\n Test Q&A Search...")
        qna_result = await manager.smart_search(
            "What is artificial intelligence?", 
            search_type="qna", 
            count=3
        )
        if qna_result.get('results'):
            print(f" Q&A: {len(qna_result['results'])} résultats")
        else:
            print(f" Q&A failed: {qna_result.get('error')}")
        
        # Test News
        print("\n Test News Search...")
        news_result = await manager.smart_search(
            "latest AI developments", 
            search_type="news", 
            count=3
        )
        if news_result.get('results'):
            print(f" News: {len(news_result['results'])} résultats")
        else:
            print(f" News failed: {news_result.get('error')}")
        
        await manager.close()
        
    except Exception as e:
        print(f" Specific search types failed: {e}")

async def test_api_key_integration():
    """Test l'intégration des clés API du fichier api-key"""
    print("\n" + "=" * 50)
    print(" TEST INTÉGRATION CLÉS API")
    print("=" * 50)
    
    # Vérifier les clés API dans l'environnement
    api_keys = {
        "BRAVE_API_KEY": os.getenv("BRAVE_API_KEY"),
        "BRAVE_API_KEY_BACKUP": os.getenv("BRAVE_API_KEY_BACKUP"),
        "WEATHER_API_KEY": os.getenv("WEATHER_API_KEY"),
        "TAVILY_API_KEY": os.getenv("TAVILY_API_KEY"),
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
        "GOOGLE_SEARCH_ENGINE_ID": os.getenv("GOOGLE_SEARCH_ENGINE_ID")
    }
    
    print("\n État des clés API:")
    for key, value in api_keys.items():
        status = " Configurée" if value else " Manquante"
        masked_value = f"{value[:10]}..." if value and len(value) > 10 else value
        print(f"  {key}: {status} ({masked_value})")
    
    # Compter les providers fonctionnels
    functional_count = 0
    if api_keys["BRAVE_API_KEY"]:
        functional_count += 1
    if api_keys["TAVILY_API_KEY"]:
        functional_count += 1
    if api_keys["GOOGLE_API_KEY"] and api_keys["GOOGLE_SEARCH_ENGINE_ID"]:
        functional_count += 1
    
    functional_count += 1  # DuckDuckGo ne nécessite pas de clé
    
    print(f"\n Providers potentiellement fonctionnels: {functional_count}/4")
    
    # Recommandations
    print("\n Recommandations:")
    if not api_keys["TAVILY_API_KEY"]:
        print("  - Obtenir une clé Tavily API pour la recherche optimisée AI")
    if not api_keys["GOOGLE_API_KEY"]:
        print("  - Configurer Google Custom Search pour une couverture maximale")
    if functional_count >= 2:
        print("  - Configuration suffisante pour un système de fallback robuste ")

async def main():
    """Fonction principale de test"""
    print(" JARVIS MCP MULTI-SEARCH INTEGRATION TEST")
    print("=" * 60)
    
    # Vérifier que le .env est chargé
    print(f" .env chargé: {bool(os.getenv('BRAVE_API_KEY'))}")
    
    try:
        # Tests individuels
        await test_individual_providers()
        
        # Test manager
        await test_multi_search_manager()
        
        # Tests spécifiques
        await test_specific_search_types()
        
        # Test intégration clés API
        await test_api_key_integration()
        
        print("\n" + "=" * 60)
        print(" TESTS TERMINÉS")
        print("=" * 60)
        
    except Exception as e:
        print(f" Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())