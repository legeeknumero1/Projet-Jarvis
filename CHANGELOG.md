# 📋 CHANGELOG - Projet Jarvis

## [v1.3.0] - 2025-01-17 - "Production Hardening" 🚀

### ✨ Nouvelles fonctionnalités
- **Observabilité complète production-ready**
- **Graceful shutdown WebSocket avec drain mode**
- **Métriques Prometheus intégrées** (/metrics endpoint)
- **Logs JSON structurés avec request-id correlation**
- **Rate limiting anti-abus** (30 req/min chat, 10 conn/min WS)
- **Middleware request tracing** (X-Request-ID headers)
- **Configuration multi-environnements** (dev/prod)

### 🔒 Sécurité
- **Scrubbing automatique des secrets** dans les logs (regex robustes)
- **Headers sécurité Nginx** (CSP, HSTS, XSS Protection)
- **Rate limiting différencié** par endpoint
- **Validation stricte taille messages** (max 4096 chars)
- **Timeouts robustes** pour services externes
- **Docker secrets management** avec Gitleaks scanning

### ⚡ Performance & Reliability  
- **WSManager centralisé** pour connexions WebSocket
- **Task cancellation propre** (pas de Event loop closed)
- **Retry avec backoff exponentiel** pour LLM/services
- **Connection pooling HTTP** avec limites
- **Prometheus instrumentator** automatique
- **Health vs Readiness probes** pour Kubernetes

### 📊 Observabilité
- **Métriques WebSocket**: `ws_active_connections`, `ws_connections_total`
- **Métriques Chat/LLM**: `chat_requests_total`, `llm_generate_seconds`
- **Métriques Services**: `service_health_status`, `service_response_seconds`
- **Métriques Rate Limiting**: `rate_limit_hits_total`
- **Logs JSON avec correlation**: timestamp ISO, request_id, user_id, latence
- **Contextvars isolation**: pas de fuite contexte entre requêtes

### 🐛 Correctifs Critiques
- **PATCH 1**: Scrubbing secrets - regex robustes vs getattr() inefficace
- **PATCH 2**: Reset user_id par message WebSocket - évite persistence
- **PATCH 3**: Config logging avant création loggers - dictConfig correct  
- **PATCH 4**: Gauge WebSocket synchronisée avec register/unregister

### 🔧 Amélioration Technique
- **Middleware production** avec contextvars pour isolation
- **Configuration JSON logging** pour production (rotation + stdout)
- **Nginx reverse proxy** avec TLS termination
- **Docker Compose production** avec secrets et healthchecks
- **Scripts validation automatisés** (tests + sanity checks)

### 📁 Nouveaux fichiers
```
prod/
├── logs-config.json              # Config logging production (fichiers)
├── logs-config-k8s.json         # Config logging Kubernetes (stdout)
├── docker-compose.prod.yml      # Stack production complète
├── docker-compose.logs.yml      # Stack avec observabilité
├── nginx-security.conf          # Nginx sécurisé + rate limiting
├── CHECKLIST_VALIDATION.md      # Procédures validation prod
├── OBSERVABILITE.md             # Guide observabilité complet
├── OBSERVABILITE_COMPLETE.md    # Documentation finale
├── PATCHES_CRITIQUES.md         # Corrections critiques appliquées
├── TESTS_VALIDATION.md          # Tests de validation détaillés
├── test-logs.sh                 # Script validation observabilité
├── test-patches.py              # Tests automatisés patches
└── fluent-bit.conf              # Collecte logs pour ELK

backend/
├── observability/
│   └── metrics.py               # Métriques Prometheus personnalisées
├── middleware/
│   └── request_context.py       # Middleware correlation logs
├── security/
│   └── rate_limit.py            # Rate limiting en mémoire
└── utils/
    ├── ws_manager.py            # Gestionnaire WebSocket centralisé
    └── logging.py               # JsonFormatter + contextvars
```

### 🧪 Tests & Validation
- **100% patches critiques validés** (4/4)
- **Tests automatisés scrubbing, contextvars, métriques**
- **Validation configs JSON** (syntaxe + structure)
- **Scripts CI/CD ready** avec exit codes
- **Tests concurrence WebSocket** (isolation contexts)

### 📈 Métriques Production
- **Overhead logging**: < 1ms par requête
- **Isolation contextvars**: 100% sans fuites
- **Graceful shutdown**: SIGTERM → drain → close clean
- **Rate limiting**: 429 avec métriques automatiques
- **Health checks**: 200ms timeout prêt Kubernetes

### 🔄 Migrations
- **Variables environnement**: `JARVIS_LOG_CONFIG` pour config JSON
- **Volumes Docker**: `/var/log/jarvis` pour logs persistants  
- **Headers requis**: X-Request-ID pour correlation (optionnel)
- **Métriques endpoint**: GET /metrics (Prometheus scraping)

---

## [v1.2.0] - 2025-01-16 - "Refactoring Modulaire"

### 🏗️ Refactoring Architecture
- **Séparation services** (LLM, Memory, Voice, Weather, HomeAssistant)
- **Factory pattern** pour FastAPI (create_app)
- **Injection de dépendances** via app.state
- **Routers modulaires** (chat, websocket, voice, health)
- **Schemas Pydantic** pour validation
- **Configuration centralisée** (Settings)

### ⚡ Améliorations
- **Lifespan manager** pour startup/shutdown services
- **Error handling** robuste avec HTTPException
- **CORS configuré** pour frontend local
- **API Key authentication** pour endpoints sécurisés
- **Health checks** pour monitoring

### 🔧 Technique  
- **Import dynamique** des services pour éviter dépendances
- **Logging structuré** avec get_logger
- **Async/await** partout pour performance
- **Type hints** Python 3.11+
- **Validation Pydantic** sur tous les inputs

---

## [v1.1.0] - 2025-01-15 - "Stabilisation"

### 🔧 Corrections
- **Gestion erreurs** améliorée
- **Logging** plus détaillé  
- **Performance** optimisée
- **Tests** ajoutés

---

## [v1.0.0] - 2025-01-10 - "Release Initiale"

### 🎉 Fonctionnalités Initiales
- **Assistant IA conversationnel** avec Ollama
- **Mémoire neuromorphique** avec Qdrant  
- **WebSocket temps réel** pour chat
- **API REST** pour intégrations
- **Services météo** et domotique
- **Jeux intégrés** (pendu)

### 🏗️ Architecture
- **Backend FastAPI** Python
- **Base vectorielle** Qdrant
- **LLM local** Ollama (llama3.2:1b)
- **WebSocket** bidirectionnel
- **Docker** containerisé

---

**Légende**:
- 🎉 Nouvelle fonctionnalité majeure
- ✨ Amélioration fonctionnelle  
- 🔒 Sécurité
- ⚡ Performance
- 📊 Observabilité
- 🐛 Correctif
- 🔧 Technique
- 🧪 Tests