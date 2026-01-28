DXVK_HUD=compiler PROTON_ENABLE_WAYLAND=1 PROTON_USE_NTSYNC=1 gamemoderun gamescope -f --mangoapp --backend wayland --force-grab-cursor --adaptive-sync --immediate-flips -w 1920 -h 1080 -r 240 -- %command%
















#  Jarvis AI Assistant - v1.9.0

**Assistant IA polyglotte local** avec intégration domotique, reconnaissance vocale, et mémoire neuromorphique.

[![Rust](https://img.shields.io/badge/Rust-1.83-orange?logo=rust)](https://www.rust-lang.org/)
[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3-blue?logo=typescript)](https://www.typescriptlang.org/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black?logo=next.js)](https://nextjs.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](https://www.docker.com/)

> **Note**: Architecture polyglotte expérimentale - 9 phases de développement, 5 langages de programmation.

---

##  Quick Start

```bash
# 1. Clone le projet
git clone https://github.com/votre-repo/jarvis.git
cd jarvis

# 2. Configuration
cp .env.example .env
# Éditer .env avec vos credentials

# 3. Lancer les services
docker-compose up -d

# 4. Vérifier la santé
curl http://localhost:8100/health

# 5. Accéder à l'interface
open http://localhost:3000
```

**Prérequis**:
- Docker 24+ & Docker Compose v2
- 8GB RAM minimum
- 20GB espace disque

---

##  Architecture - 9 Phases Polyglotte

| Phase | Technologie | Port | Status | Description |
|-------|-------------|------|--------|-------------|
| **1** |  Rust/Axum | 8100 |  Prod | API core, orchestration |
| **2** |  C++20/DSP | 8004 |  Prod | Audio ultra-faible latence (<1ms) |
| **3** |  Python/Flask | 8005 |  Prod | LLM/STT/TTS (Ollama, Whisper, Piper) |
| **4** |  Rust/sqlx | - |  Prod | Base de données type-safe |
| **5** |  Rust/MQTT | - |  Prod | Domotique Home Assistant |
| **6** |  Go/Prometheus | 8006 |  Dev | Monitoring & metrics |
| **7** |  Next.js/React | 3000 |  Prod | Interface web moderne |
| **8** |  Lua/mlua | - |  Dev | Système de plugins |
| **9** |  Elixir/OTP | 8007 |  Dev | Clustering distribué |

**Statut**: 5/9 phases en production | 4/9 en développement

---

##  Fonctionnalités

###  Disponibles
-  **Chat conversationnel** avec mémoire contextuelle
-  **Reconnaissance vocale** (Whisper) multilingue
-  **Synthèse vocale** (Piper TTS) en français
-  **Domotique** via MQTT/Home Assistant
-  **Mémoire neuromorphique** (Qdrant vectors)
-  **Recherche sémantique** full-text (Tantivy)
-  **Monitoring** Prometheus + Grafana
-  **Gestion secrets** (jarvis-secretsd)

###  En développement
-  Système de plugins Lua
-  Clustering Elixir multi-nœuds
-  UI améliorée (animations, themes)
-  Application mobile (React Native)

---

##  Structure du Projet

```
jarvis/
 core/                    # Phase 1 - Rust API backend
    src/
       handlers/       # Handlers HTTP/WebSocket
       middleware/     # Auth, rate limit, validation
       services/       # Services métier
    Cargo.toml
 backend-audio-cpp/       # Phase 2 - Moteur audio C++
 backend-python-bridges/  # Phase 3 - Bridges Python IA
    ollama_client.py    # Client LLM
    whisper_client.py   # STT
    piper_client.py     # TTS
 backend-rust-db/         # Phase 4 - Couche DB
 backend-rust-mqtt/       # Phase 5 - Client MQTT/HA
 monitoring-go/           # Phase 6 - Monitoring
 frontend/                # Phase 7 - Interface Next.js
    app/                # Pages (App Router)
    components/         # Composants React
    store/              # Zustand stores
 backend-lua-plugins/     # Phase 8 - Plugins Lua
 clustering-elixir/       # Phase 9 - Clustering
 jarvis-secretsd/         # Daemon gestion secrets
 devops-tools/            # Jenkins, ArgoCD, K8s
 docs/                    # Documentation complète
```

---

##  Documentation

- **[Documentation complète](docs/README.md)** - Index de toute la documentation
- **[Architecture](docs/ARCHITECTURE.md)** - Design système 9-phases
- **[API](docs/API.md)** - Documentation API REST/WebSocket
- **[Déploiement](docs/DEPLOYMENT_GUIDE_MULTI_ENV.md)** - Guide multi-environnements
- **[Sécurité](docs/SECURITY.md)** - Guide sécurité & hardening
- **[DevOps](docs/DEVOPS_GUIDE.md)** - CI/CD, K8s, monitoring

---

##  Sécurité

**Statut**:  **En cours de hardening** (voir [SECURITY.md](docs/SECURITY.md))

### Implémenté
-  JWT authentication (Axum middleware)
-  Rate limiting (par endpoint + global)
-  Input validation (regex + sanitization)
-  Secrets encryption (AES-256-GCM)
-  Audit logging (Ed25519 signed)

### En cours
-  HTTPS/TLS (certificats prêts)
-  PostgreSQL SSL
-  RBAC complet
-  CSP headers

**Score sécurité**: 7/10 → Target: 9/10

---

##  Performance

| Métrique | FastAPI (v1.2) | Rust/Axum (v1.9) | Gain |
|----------|----------------|------------------|------|
| Latence API | 150ms | 5ms | **30x** |
| Throughput | 1K req/s | 30K req/s | **30x** |
| Mémoire | 200 MB | 50 MB | **4x** moins |
| Audio latency | 50ms | <1ms | **50x** |

**Target production**:
- API: <100ms (p95)
- Chat: <2s (complet)
- Memory footprint: <500MB

---

##  Stack Technique

### Backend
- **Rust 1.83**: Axum, Tokio, sqlx, Tantivy
- **Python 3.11**: Flask, Transformers, Whisper, Piper
- **C++20**: PortAudio, FFmpeg
- **Go 1.21**: Prometheus client
- **Elixir 1.15**: Phoenix, Horde

### Frontend
- **Next.js 14** (App Router)
- **React 19**
- **TypeScript 5.3**
- **Zustand** (state)
- **Tailwind CSS**

### Infrastructure
- **PostgreSQL 15** + TimescaleDB
- **Redis 7** (cache)
- **Qdrant** (vectors)
- **Ollama** (LLM local)
- **Docker Compose** / **Kubernetes**

---

##  Tests

```bash
# Tests unitaires Rust
cargo test

# Tests Python
pytest tests/

# Tests frontend
cd frontend && npm test

# Tests d'intégration
./scripts/test-integration.sh

# Tests de charge
k6 run tests/load/chat_load.js
```

**Coverage**: 85% (target: 95%)

---

##  Roadmap v2.0

- [ ] Plugin marketplace (Lua)
- [ ] Multi-instance clustering (Elixir)
- [ ] Mobile app (React Native)
- [ ] Voice assistants (Alexa, Google Home)
- [ ] Advanced analytics dashboard
- [ ] API GraphQL

Voir [ROADMAP_POLYGLOTTE.md](docs/ROADMAP_POLYGLOTTE.md) pour détails.

---

##  Contribution

Les contributions sont bienvenues ! Voir [CONTRIBUTING.md](CONTRIBUTING.md).

### Guidelines
1. Fork le projet
2. Créer une branche (`git checkout -b feature/amazing`)
3. Commit (`git commit -m 'Add amazing feature'`)
4. Push (`git push origin feature/amazing`)
5. Pull Request

**Standards**:
- Code formaté (`cargo fmt`, `black`, `prettier`)
- Tests passants
- Documentation à jour

---

##  Licence

MIT License - voir [LICENSE](LICENSE)

---

## ‍ Auteur

**Enzo** (21 ans, Perpignan)

- GitHub: [@votre-username](https://github.com/votre-username)
- Email: votre@email.com

---

##  Remerciements

- **Anthropic** (Claude Code & assistance architecture)
- **Communauté Rust** (crates exceptionnels)
- **Home Assistant** (intégration domotique)
- **Ollama** (LLM local)

---

**Version**: v1.9.0 | **Dernière mise à jour**: 2025-11-30
