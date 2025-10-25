# 🔍 Multi-Search MCP Integration - Documentation

## Overview
Système de recherche multi-providers intégré dans Jarvis via MCP (Model Context Protocol).

## Providers Disponibles
- **Brave Search** ✅ - Recherche sans tracking avec API key
- **DuckDuckGo** ⚠️  - Recherche privée (parfois bloquée)
- **Tavily** ⭕ - Recherche optimisée AI (nécessite clé API)
- **Google Custom Search** ⭕ - Google officiel (nécessite configuration)

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
# Brave Search (Configuré ✅)
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

✅ **Terminé:**
- Configuration des clés API Brave
- Système de fallback multi-provider
- Endpoints API REST
- Documentation complète

⭕ **À faire:**
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
