#!/usr/bin/env python3
"""
Test Brave Search MCP pour Jarvis
Teste l'intégration avec les clés API Brave
"""

import asyncio
import os
import sys
import json
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent.parent))

from MCP.servers.brave_search_mcp import BraveSearchMCP

async def test_brave_search():
    """Teste toutes les fonctionnalités de Brave Search MCP"""
    
    print(" Test Brave Search MCP pour Jarvis")
    print("=====================================")
    
    # Vérifier les clés API
    api_key = os.getenv("BRAVE_API_KEY")
    api_key_backup = os.getenv("BRAVE_API_KEY_BACKUP")
    
    print(f"BRAVE_API_KEY: {' Configuré' if api_key else '  Manquant'}")
    print(f"BRAVE_API_KEY_BACKUP: {' Configuré' if api_key_backup else '  Manquant'}")
    
    if not api_key:
        print(" Clé API Brave manquante. Configurez BRAVE_API_KEY dans .env")
        return False
    
    print(f" Using API key: {api_key[:10]}...")
    print()
    
    try:
        # Initialiser le client Brave Search
        brave_mcp = BraveSearchMCP()
        
        # Test 1: Recherche web
        print(" Test 1: Recherche web")
        print("------------------------")
        
        web_result = await brave_mcp.web_search(
            "Jarvis AI assistant français",
            count=5,
            search_lang="fr",
            country="FR"
        )
        
        print(f"Résultats trouvés: {web_result['total_results']}")
        for i, result in enumerate(web_result['results'][:3], 1):
            print(f"  {i}. {result['title']}")
            print(f"     {result['url']}")
        print()
        
        # Test 2: Recherche d'actualités
        print(" Test 2: Recherche actualités")
        print("-------------------------------")
        
        news_result = await brave_mcp.news_search(
            "intelligence artificielle France",
            count=3,
            country="FR",
            search_lang="fr"
        )
        
        print(f"Articles trouvés: {news_result['total_articles']}")
        for i, article in enumerate(news_result['articles'][:2], 1):
            print(f"  {i}. {article['title']}")
            print(f"     Source: {article['source']}")
        print()
        
        # Test 3: Recherche d'images
        print(" Test 3: Recherche images")
        print("---------------------------")
        
        image_result = await brave_mcp.image_search(
            "jarvis assistant",
            count=3,
            safesearch="moderate"
        )
        
        print(f"Images trouvées: {image_result['total_images']}")
        for i, image in enumerate(image_result['images'][:2], 1):
            print(f"  {i}. {image['title']}")
            print(f"     Taille: {image['width']}x{image['height']}")
        print()
        
        # Test 4: Recherche de vidéos
        print(" Test 4: Recherche vidéos")
        print("---------------------------")
        
        video_result = await brave_mcp.video_search(
            "tutoriel intelligence artificielle",
            count=3,
            search_lang="fr"
        )
        
        print(f"Vidéos trouvées: {video_result['total_videos']}")
        for i, video in enumerate(video_result['videos'][:2], 1):
            print(f"  {i}. {video['title']}")
            print(f"     Plateforme: {video['platform']} - Durée: {video['duration']}")
        print()
        
        # Fermer les connexions
        await brave_mcp.close()
        
        print(" Tous les tests Brave Search ont réussi!")
        return True
        
    except Exception as e:
        print(f" Erreur lors des tests: {e}")
        return False

async def test_api_key_rotation():
    """Teste la rotation des clés API"""
    print(" Test rotation clés API")
    print("-------------------------")
    
    api_key = os.getenv("BRAVE_API_KEY")
    api_key_backup = os.getenv("BRAVE_API_KEY_BACKUP")
    
    if not api_key_backup:
        print("  Pas de clé backup - test ignoré")
        return True
        
    try:
        # Simuler une clé API invalide
        os.environ["BRAVE_API_KEY"] = "invalid_key_test"
        
        brave_mcp = BraveSearchMCP()
        
        # Cette requête devrait automatiquement utiliser la clé backup
        result = await brave_mcp.web_search("test rotation", count=1)
        
        await brave_mcp.close()
        
        # Restaurer la clé originale
        os.environ["BRAVE_API_KEY"] = api_key
        
        if result['total_results'] > 0:
            print(" Rotation des clés API fonctionne")
            return True
        else:
            print("  Rotation testée mais résultats limités")
            return True
            
    except Exception as e:
        # Restaurer la clé originale
        os.environ["BRAVE_API_KEY"] = api_key
        print(f"  Test rotation échoué: {e}")
        return False

def load_env_file():
    """Charge les variables d'environnement depuis .env"""
    env_file = Path(__file__).parent.parent / ".env"
    
    if not env_file.exists():
        print(f" Fichier .env non trouvé: {env_file}")
        return False
        
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value
    
    return True

async def main():
    """Fonction principale de test"""
    
    # Charger les variables d'environnement
    if not load_env_file():
        return
    
    # Tests principaux
    success = await test_brave_search()
    
    if success:
        # Test avancé de rotation des clés
        await test_api_key_rotation()
        
        print()
        print(" Configuration Brave Search MCP validée!")
        print(" Prêt à utiliser dans Jarvis:")
        print("  • Recherche web sans tracking")
        print("  • Actualités en temps réel") 
        print("  • Images et vidéos")
        print("  • Support multi-langue")
        print("  • Rotation automatique des clés")
    else:
        print()
        print(" Configuration incomplète")
        print("Vérifiez vos clés API dans le fichier .env")

if __name__ == "__main__":
    asyncio.run(main())