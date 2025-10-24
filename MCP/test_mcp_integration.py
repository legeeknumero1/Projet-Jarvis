#!/usr/bin/env python3
"""
Test d'intégration MCP pour Jarvis
Vérifie que le serveur MCP Browserbase peut être utilisé par Jarvis
"""

import asyncio
import os
import sys
import logging
from pathlib import Path

# Ajouter le chemin du backend au PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from integration.mcp_client import MCPClient, create_default_mcp_servers

async def test_mcp_integration():
    """Test de l'intégration MCP avec Jarvis"""
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    print("🔌 Test d'intégration MCP pour Jarvis")
    print("=" * 50)
    
    # Initialiser le client MCP
    mcp_client = MCPClient()
    
    # Enregistrer les serveurs par défaut
    servers = create_default_mcp_servers()
    print(f"📡 Serveurs MCP trouvés: {len(servers)}")
    
    for server in servers:
        mcp_client.register_server(server)
        print(f"  • {server.name}: {server.description}")
        print(f"    Capacités: {', '.join(server.capabilities)}")
    
    if not servers:
        print("❌ Aucun serveur MCP disponible")
        return False
    
    # Tester le démarrage du serveur Browserbase
    browserbase_name = "browserbase_web_automation"
    if browserbase_name in [s.name for s in servers]:
        print(f"\n🚀 Test de démarrage du serveur {browserbase_name}...")
        
        success = await mcp_client.start_server(browserbase_name)
        if success:
            print(f"✅ Serveur {browserbase_name} démarré avec succès")
            
            # Test basique de communication
            print("\n🔍 Test de communication avec le serveur...")
            
            # Attendre un peu pour que le serveur soit prêt
            await asyncio.sleep(2)
            
            # Tester une requête simple (liste des outils disponibles)
            result = await mcp_client.send_request(browserbase_name, "tools/list", {})
            
            if result:
                print("✅ Communication avec le serveur MCP réussie")
                print(f"📋 Outils disponibles: {result}")
            else:
                print("⚠️  Communication avec le serveur MCP échouée")
            
            # Arrêter le serveur
            await mcp_client.stop_server(browserbase_name)
            print(f"🛑 Serveur {browserbase_name} arrêté")
            
        else:
            print(f"❌ Échec du démarrage du serveur {browserbase_name}")
            return False
    
    print("\n🎉 Test d'intégration MCP terminé avec succès!")
    return True

async def test_web_capabilities():
    """Test des capacités web de Jarvis via MCP"""
    
    print("\n🌐 Test des capacités web de Jarvis")
    print("=" * 40)
    
    # Vérifier les variables d'environnement nécessaires
    api_key = os.getenv("BROWSERBASE_API_KEY")
    project_id = os.getenv("BROWSERBASE_PROJECT_ID")
    
    if not api_key or not project_id:
        print("⚠️  Variables d'environnement Browserbase non configurées")
        print("   BROWSERBASE_API_KEY:", "✅" if api_key else "❌")
        print("   BROWSERBASE_PROJECT_ID:", "✅" if project_id else "❌")
        print("🔗 Créez un compte sur https://www.browserbase.com/")
        print("📝 Ajoutez vos clés dans le fichier .env")
        return False
    
    print("✅ Configuration Browserbase trouvée")
    
    # Initialiser le client MCP
    mcp_client = MCPClient()
    servers = create_default_mcp_servers()
    
    for server in servers:
        mcp_client.register_server(server)
    
    # Démarrer le serveur
    browserbase_name = "browserbase_web_automation"
    await mcp_client.start_server(browserbase_name)
    
    # Test de navigation web
    print("\n🔍 Test de navigation web...")
    
    try:
        # Tester une navigation simple
        result = await mcp_client.browse_web("https://httpbin.org/get", "navigate")
        
        if result:
            print("✅ Navigation web réussie!")
            print(f"📋 Résultat: {result}")
        else:
            print("❌ Navigation web échouée")
            
    except Exception as e:
        print(f"❌ Erreur lors du test web: {e}")
    
    finally:
        # Arrêter le serveur
        await mcp_client.stop_server(browserbase_name)
    
    return True

if __name__ == "__main__":
    # Test d'intégration de base
    success = asyncio.run(test_mcp_integration())
    
    if success:
        # Test des capacités web (nécessite configuration Browserbase)
        asyncio.run(test_web_capabilities())