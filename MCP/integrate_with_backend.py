#!/usr/bin/env python3
"""
Script d'intégration du Multi-Search MCP avec le backend Jarvis
Intègre les nouveaux providers de recherche dans l'architecture MCP existante
"""

import json
import logging
import os
import sys
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_mcp_client_config():
    """Met à jour la configuration du client MCP pour inclure les nouveaux providers"""
    logger.info(" Mise à jour de la configuration MCP client...")
    
    backend_path = Path("/home/enzo/Projet-Jarvis/backend")
    mcp_client_path = backend_path / "integration" / "mcp_client.py"
    
    if not mcp_client_path.exists():
        logger.error(f" MCP client non trouvé: {mcp_client_path}")
        return False
    
    # Lire le fichier existant
    with open(mcp_client_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ajouter l'import du multi-search manager
    search_import = """
# Multi-Search MCP Integration
try:
    sys.path.append('/home/enzo/Projet-Jarvis/MCP/servers')
    from multi_search_manager import MultiSearchManagerMCP
    MULTI_SEARCH_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Multi-Search MCP not available: {e}")
    MULTI_SEARCH_AVAILABLE = False
"""
    
    # Vérifier si l'import existe déjà
    if "MultiSearchManagerMCP" not in content:
        # Ajouter après les imports existants
        import_position = content.find("import logging")
        if import_position != -1:
            # Trouver la fin de la section imports
            lines = content.split('\n')
            insert_line = 0
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    insert_line = i + 1
            
            lines.insert(insert_line, search_import)
            content = '\n'.join(lines)
            
            logger.info(" Import MultiSearchManagerMCP ajouté")
        else:
            logger.warning("  Position d'insertion non trouvée")
    
    # Ajouter méthode de recherche dans la classe MCPClient
    search_method = '''
    async def search_web(self, query: str, count: int = 10, search_type: str = "web", 
                        privacy_preference: str = "medium") -> Dict[str, Any]:
        """Recherche web avec le système multi-provider"""
        if not MULTI_SEARCH_AVAILABLE:
            return {
                "error": "Multi-search system not available",
                "query": query,
                "results": []
            }
        
        try:
            manager = MultiSearchManagerMCP()
            result = await manager.smart_search(
                query=query,
                search_type=search_type,
                count=count,
                privacy_preference=privacy_preference
            )
            await manager.close()
            return result
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {
                "error": str(e),
                "query": query,
                "results": []
            }
    
    async def search_parallel(self, query: str, providers: List[str] = None, 
                             count: int = 5) -> Dict[str, Any]:
        """Recherche parallèle sur plusieurs providers"""
        if not MULTI_SEARCH_AVAILABLE:
            return {
                "error": "Multi-search system not available",
                "query": query,
                "combined_results": []
            }
        
        try:
            manager = MultiSearchManagerMCP()
            result = await manager.parallel_search(
                query=query,
                providers=providers,
                count=count
            )
            await manager.close()
            return result
            
        except Exception as e:
            logger.error(f"Parallel search failed: {e}")
            return {
                "error": str(e),
                "query": query,
                "combined_results": []
            }
'''
    
    # Vérifier si les méthodes existent déjà
    if "async def search_web(" not in content:
        # Trouver la classe MCPClient et ajouter les méthodes
        class_position = content.find("class MCPClient")
        if class_position != -1:
            # Trouver la fin de la classe (approximatif)
            lines = content.split('\n')
            class_line = 0
            for i, line in enumerate(lines):
                if "class MCPClient" in line:
                    class_line = i
                    break
            
            # Trouver une position appropriée dans la classe
            insert_position = class_line + 1
            for i in range(class_line + 1, len(lines)):
                if lines[i].strip() == "" or (not lines[i].startswith(' ') and lines[i].strip()):
                    insert_position = i
                    break
            
            # Insérer les méthodes
            method_lines = search_method.strip().split('\n')
            for j, method_line in enumerate(method_lines):
                lines.insert(insert_position + j, method_line)
            
            content = '\n'.join(lines)
            logger.info(" Méthodes de recherche ajoutées à MCPClient")
        else:
            logger.warning("  Classe MCPClient non trouvée")
    
    # Sauvegarder le fichier mis à jour
    try:
        with open(mcp_client_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(" Configuration MCP client mise à jour")
        return True
    except Exception as e:
        logger.error(f" Erreur sauvegarde: {e}")
        return False

def create_mcp_search_endpoint():
    """Crée un endpoint API pour la recherche via MCP"""
    logger.info(" Création des endpoints de recherche...")
    
    backend_path = Path("/home/enzo/Projet-Jarvis/backend")
    api_path = backend_path / "api"
    
    if not api_path.exists():
        logger.error(f" Dossier API non trouvé: {api_path}")
        return False
    
    # Créer le fichier d'endpoint de recherche
    search_endpoint_content = '''"""
Endpoints API pour la recherche web via MCP Multi-Search
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging

from ..integration.mcp_client import MCPClient

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/search", tags=["search"])

class SearchRequest(BaseModel):
    query: str
    count: Optional[int] = 10
    search_type: Optional[str] = "web"
    privacy_preference: Optional[str] = "medium"

class ParallelSearchRequest(BaseModel):
    query: str
    providers: Optional[List[str]] = None
    count: Optional[int] = 5

@router.post("/web")
async def search_web(request: SearchRequest):
    """Recherche web avec le système multi-provider"""
    try:
        mcp_client = MCPClient()
        result = await mcp_client.search_web(
            query=request.query,
            count=request.count,
            search_type=request.search_type,
            privacy_preference=request.privacy_preference
        )
        
        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Search API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/parallel")
async def search_parallel(request: ParallelSearchRequest):
    """Recherche parallèle sur plusieurs providers"""
    try:
        mcp_client = MCPClient()
        result = await mcp_client.search_parallel(
            query=request.query,
            providers=request.providers,
            count=request.count
        )
        
        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Parallel search API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/providers")
async def get_search_providers():
    """Obtenir la liste des providers de recherche disponibles"""
    try:
        # Import du manager pour obtenir le statut
        import sys
        sys.path.append('/home/enzo/Projet-Jarvis/MCP/servers')
        from multi_search_manager import MultiSearchManagerMCP
        
        manager = MultiSearchManagerMCP()
        status = await manager.get_provider_status()
        await manager.close()
        
        return {
            "success": True,
            "data": status
        }
        
    except Exception as e:
        logger.error(f"Provider status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
'''
    
    search_endpoint_path = api_path / "search.py"
    
    try:
        with open(search_endpoint_path, 'w', encoding='utf-8') as f:
            f.write(search_endpoint_content)
        logger.info(f" Endpoint de recherche créé: {search_endpoint_path}")
        return True
    except Exception as e:
        logger.error(f" Erreur création endpoint: {e}")
        return False

def update_main_api():
    """Met à jour le fichier principal de l'API pour inclure les endpoints de recherche"""
    logger.info(" Mise à jour de l'API principale...")
    
    backend_path = Path("/home/enzo/Projet-Jarvis/backend")
    main_path = backend_path / "main.py"
    
    if not main_path.exists():
        logger.error(f" Fichier main.py non trouvé: {main_path}")
        return False
    
    # Lire le fichier existant
    with open(main_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ajouter l'import du router de recherche
    search_import = "from .api.search import router as search_router"
    
    if search_import not in content:
        # Trouver où ajouter l'import
        import_position = content.find("from .api.")
        if import_position != -1:
            lines = content.split('\n')
            # Trouver la ligne d'import appropriée
            for i, line in enumerate(lines):
                if "from .api." in line:
                    lines.insert(i + 1, search_import)
                    break
            content = '\n'.join(lines)
            logger.info(" Import search router ajouté")
    
    # Ajouter l'inclusion du router
    router_include = "app.include_router(search_router)"
    
    if router_include not in content:
        # Trouver où ajouter l'inclusion
        include_position = content.find("app.include_router(")
        if include_position != -1:
            lines = content.split('\n')
            # Trouver la dernière inclusion de router
            last_include_line = 0
            for i, line in enumerate(lines):
                if "app.include_router(" in line:
                    last_include_line = i
            
            lines.insert(last_include_line + 1, router_include)
            content = '\n'.join(lines)
            logger.info(" Search router inclus dans l'app")
    
    # Sauvegarder
    try:
        with open(main_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(" API principale mise à jour")
        return True
    except Exception as e:
        logger.error(f" Erreur mise à jour API: {e}")
        return False

def create_integration_documentation():
    """Crée la documentation d'intégration"""
    logger.info(" Création de la documentation d'intégration...")
    
    mcp_path = Path("/home/enzo/Projet-Jarvis/MCP")
    doc_content = '''#  Multi-Search MCP Integration - Documentation

## Overview
Système de recherche multi-providers intégré dans Jarvis via MCP (Model Context Protocol).

## Providers Disponibles
- **Brave Search**  - Recherche sans tracking avec API key
- **DuckDuckGo**   - Recherche privée (parfois bloquée)
- **Tavily**  - Recherche optimisée AI (nécessite clé API)
- **Google Custom Search**  - Google officiel (nécessite configuration)

## API Endpoints

### POST /search/web
Recherche web intelligente avec fallback automatique.

```json
{
  "query": "Python FastAPI tutorial",
  "count": 10,
  "search_type": "web",
  "privacy_preference": "high"
}
```

### POST /search/parallel
Recherche parallèle sur plusieurs providers.

```json
{
  "query": "machine learning",
  "providers": ["brave", "duckduckgo"],
  "count": 5
}
```

### GET /search/providers
Statut des providers disponibles.

## Configuration

### Variables d'environnement requises:
```bash
# Brave Search (Configuré )
BRAVE_API_KEY=BSAQwlfLLN...
BRAVE_API_KEY_BACKUP=BSAt9z9JKc...

# Tavily (À configurer)
TAVILY_API_KEY=

# Google Custom Search (À configurer)
GOOGLE_API_KEY=
GOOGLE_SEARCH_ENGINE_ID=
```

## Utilisation depuis Jarvis

```python
# Dans le backend Jarvis
from integration.mcp_client import MCPClient

mcp_client = MCPClient()

# Recherche simple
result = await mcp_client.search_web("intelligence artificielle 2025")

# Recherche parallèle
parallel_result = await mcp_client.search_parallel("Python", ["brave", "duckduckgo"])
```

## Sécurité et Privacy

- **Brave Search**: Privacy-focused, pas de tracking
- **DuckDuckGo**: Privacy maximum, pas de clé API requise
- **Fallback intelligent**: Utilise le provider le plus approprié
- **Rate limiting**: Gestion automatique des limites API

## État de l'intégration

 **Terminé:**
- Configuration des clés API Brave
- Système de fallback multi-provider
- Endpoints API REST
- Documentation complète

 **À faire:**
- Obtenir clés API Tavily et Google
- Tests d'intégration complets
- Monitoring des performances

## Troubleshooting

### DuckDuckGo 403 Forbidden
- Normal, utilise le fallback vers Brave
- DuckDuckGo bloque souvent les requêtes automatisées

### Rate Limits
- Brave: 2000 requêtes/mois (gratuit)
- Système de rotation automatique des clés

### Provider indisponible
- Le système utilise automatiquement le provider suivant
- Ordre de fallback: brave → tavily → google → duckduckgo
'''
    
    doc_path = mcp_path / "INTEGRATION_GUIDE.md"
    
    try:
        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write(doc_content)
        logger.info(f" Documentation créée: {doc_path}")
        return True
    except Exception as e:
        logger.error(f" Erreur création documentation: {e}")
        return False

def main():
    """Fonction principale d'intégration"""
    print(" JARVIS MCP MULTI-SEARCH INTEGRATION")
    print("=" * 50)
    
    success_count = 0
    total_steps = 4
    
    # Étape 1: Mise à jour MCP client
    if update_mcp_client_config():
        success_count += 1
    
    # Étape 2: Création endpoints
    if create_mcp_search_endpoint():
        success_count += 1
    
    # Étape 3: Mise à jour API principale
    if update_main_api():
        success_count += 1
    
    # Étape 4: Documentation
    if create_integration_documentation():
        success_count += 1
    
    print("\n" + "=" * 50)
    print(f" INTÉGRATION TERMINÉE: {success_count}/{total_steps} étapes réussies")
    
    if success_count == total_steps:
        print(" Intégration complète réussie!")
        print("\n Prochaines étapes:")
        print("1. Redémarrer le backend Jarvis")
        print("2. Tester les endpoints /search/web et /search/parallel")
        print("3. Configurer les clés API manquantes (Tavily, Google)")
    else:
        print("  Intégration partielle - vérifier les erreurs ci-dessus")
    
    print("=" * 50)

if __name__ == "__main__":
    main()