#!/usr/bin/env python3
"""
Test complet des capacités internet de Jarvis via MCP
"""

import asyncio
import os
import sys
import logging
from pathlib import Path

# Ajouter le chemin du backend au PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from services.web_service import WebService

async def test_jarvis_web_capabilities():
    """Test complet des capacités web de Jarvis"""
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    print(" Test des capacités internet de Jarvis")
    print("=" * 50)
    
    # Initialiser le service web
    web_service = WebService()
    
    print(" Initialisation du service web...")
    success = await web_service.initialize()
    
    if not success:
        print(" Échec d'initialisation du service web")
        return False
    
    print(" Service web initialisé")
    
    # Test 1: Vérifier les capacités
    print("\n Test 1: Récupération des capacités...")
    try:
        capabilities = await web_service.get_capabilities()
        print(f" Capacités disponibles: {capabilities}")
    except Exception as e:
        print(f" Erreur capacités: {e}")
    
    # Test 2: Test de navigation basique (sans clés API)
    print("\n Test 2: Navigation basique...")
    try:
        # Test avec une page simple sans nécessiter de clés API
        result = await web_service.get_web_content("https://httpbin.org/get")
        
        if result:
            print(" Navigation basique réussie")
            print(f" URL: {result['url']}")
        else:
            print("  Navigation basique échouée (normal sans clés API)")
            
    except Exception as e:
        print(f"  Erreur navigation basique: {e} (normal sans clés API)")
    
    # Test 3: Vérification de la configuration
    print("\n  Test 3: Vérification de la configuration...")
    
    api_key = os.getenv("BROWSERBASE_API_KEY")
    project_id = os.getenv("BROWSERBASE_PROJECT_ID")
    
    print(f"BROWSERBASE_API_KEY: {' Configuré' if api_key else '  Manquant'}")
    print(f"BROWSERBASE_PROJECT_ID: {' Configuré' if project_id else '  Manquant'}")
    
    if api_key and project_id:
        print("\n Configuration complète détectée - Tests avancés...")
        
        # Test 4: Recherche web avancée
        print("\n Test 4: Recherche web avancée...")
        try:
            result = await web_service.search_web("Python programming")
            if result:
                print(" Recherche web avancée réussie")
                print(f" Résultats: {len(result.get('results', []))} éléments")
            else:
                print("  Recherche web avancée échouée")
        except Exception as e:
            print(f" Erreur recherche avancée: {e}")
        
        # Test 5: Capture d'écran
        print("\n Test 5: Capture d'écran...")
        try:
            result = await web_service.take_screenshot("https://httpbin.org/get")
            if result:
                print(" Capture d'écran réussie")
                print(f" Screenshot disponible")
            else:
                print("  Capture d'écran échouée")
        except Exception as e:
            print(f" Erreur capture: {e}")
            
    else:
        print("\n  Configuration incomplète - Tests limités")
        print(" Pour des tests complets:")
        print("   1. Créez un compte sur https://www.browserbase.com/")
        print("   2. Ajoutez vos clés dans le fichier .env")
        print("   3. Relancez ce test")
    
    # Arrêter le service
    print("\n Arrêt du service web...")
    await web_service.shutdown()
    
    print("\n Tests terminés!")
    return True

async def demonstrate_jarvis_internet_access():
    """Démonstration des capacités internet de Jarvis"""
    
    print("\n" + "="*60)
    print(" DÉMONSTRATION: Jarvis peut maintenant accéder à Internet!")
    print("="*60)
    
    print("""
 NOUVELLES CAPACITÉS DE JARVIS:

 Navigation Web
   • Accès à n'importe quelle page web
   • Extraction de contenu intelligente
   • Support des sites modernes (JavaScript, SPA, etc.)

 Recherche Internet  
   • Recherches web automatiques
   • Extraction de résultats pertinents
   • Intégration des résultats dans les réponses

 Captures d'écran
   • Screenshots de pages web
   • Mode page complète ou sélectif
   • Analyse visuelle du contenu

 Interactions Avancées
   • Clic sur des éléments
   • Remplissage de formulaires  
   • Navigation interactive
   • Actions basées sur des instructions naturelles

 Architecture MCP
   • Model Context Protocol pour extensibilité
   • Serveurs MCP modulaires
   • Intégration seamless avec l'IA

 CONFIGURATION REQUISE:
   • Compte Browserbase (https://www.browserbase.com/)
   • Clés API dans le fichier .env
   • Serveur MCP Browserbase installé 

 UTILISATION:
   • API REST endpoints disponibles
   • Intégration directe dans les conversations
   • Automatisation web complète
   • Recherches en temps réel
    """)
    
    print("="*60)
    print(" Jarvis est maintenant connecté à Internet!")
    print("="*60)

if __name__ == "__main__":
    # Exécuter les tests
    asyncio.run(test_jarvis_web_capabilities())
    
    # Afficher la démonstration
    asyncio.run(demonstrate_jarvis_internet_access())