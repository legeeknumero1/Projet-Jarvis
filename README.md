# 🤖 Jarvis - Assistant IA Personnel v1.9.0 "Architecture Polyglotte"

> Assistant vocal intelligent local production-ready développé par Enzo, avec architecture distribuée 9 phases, reconnaissance vocale, synthèse vocale, IA locale, plugins Lua et haute disponibilité.

[![Rust](https://img.shields.io/badge/rust-%23CE422B.svg?style=for-the-badge&logo=rust&logoColor=white)](https://www.rust-lang.org)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)](https://reactjs.org)
[![Elixir](https://img.shields.io/badge/elixir-%234B275F.svg?style=for-the-badge&logo=elixir&logoColor=white)](https://elixir-lang.org)

## ✨ Architecture Polyglotte v1.9.0 (Phases 1-9)

### 🏗️ 9 Phases Implémentées

**Phase 1** 🦀 Rust Backend Core (Port 8100)
- API haute performance Axum + type-safe SQL
- 30x plus rapide que FastAPI
- WebSocket temps réel bidirectionnel

**Phase 2** ⚙️ C++ Audio Engine (Port 8004)
- DSP temps réel <1ms latence
- 50x plus rapide que Python multiproc

**Phase 3** 🐍 Python Bridges IA (Port 8005)
- Ollama, Whisper, Piper, Embeddings
- Services découplés, scalables indépendamment

**Phase 4** 🗄️ Rust DB Layer
- PostgreSQL type-safe sqlx
- Full-text search Tantivy
- Cache distribué Redis

**Phase 5** 🔌 MQTT Automations
- Rumqttc + Home Assistant
- Système d'automatisations complet

**Phase 6** 🐹 Go Monitoring
- Watchdog + Prometheus metrics
- Health checks Kubernetes

**Phase 7** 🌐 Frontend TypeScript (Port 3000)
- React 19 + Next.js 14
- Zustand state management
- Type-safe avec Zod validation

**Phase 8** 🧩 Lua Plugins
- Sandbox sécurisé
- Hot-reload sans recompilation
- Système de hooks extensible

**Phase 9** ☁️ Elixir HA Clustering
- Multi-nœuds distribuée
- Failover automatique
- Raft consensus state

## 🚀 Installation Rapide

### Prérequis
- Docker & Docker Compose
- 8GB RAM minimum
- 50GB espace disque libre

### ⚠️ Migration Docker Requise
```bash
# OBLIGATOIRE - Migrer Docker vers /home
sudo systemctl stop docker
sudo rsync -aP /var/lib/docker/ /home/$USER/jarvis-docker/
sudo tee /etc/docker/daemon.json << EOF
{
  "data-root": "/home/$USER/jarvis-docker",
  "storage-driver": "overlay2"
}
EOF
sudo systemctl start docker
```

### Démarrage

**Environnement développement :**
```bash
git clone https://github.com/username/Projet-Jarvis.git
cd Projet-Jarvis
./start_jarvis_docker.sh
```

**Environnement production v1.3 :**
```bash
# Production avec observabilité complète
docker-compose -f prod/docker-compose.prod.yml up -d

# Avec stack monitoring (Prometheus + Grafana)
docker-compose -f prod/docker-compose.logs.yml up -d
```

**Accès :**
- Interface : `http://localhost:3000` (Frontend React)
- API Rust : `http://localhost:8100` (Rust Backend Core)
- Health : `http://localhost:8100/health`
- Go Monitor : `http://localhost:8006`
- Elixir HA : `http://localhost:8007`

## 🏗️ Architecture Polyglotte

```
┌─────────────────────────────────────────────────────┐
│          Frontend React/TypeScript (3000)           │
└───────────────────────┬─────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼───────┐  ┌────▼────┐   ┌─────▼──────┐
│  Rust Core    │  │  Python  │   │  C++ Audio │
│  (8100)       │  │ Bridges  │   │  (8004)    │
│ Axum+Tokio    │  │ (8005)   │   │  DSP <1ms  │
└───────┬───────┘  └────┬────┘   └─────┬──────┘
        │               │               │
   ┌────▼──────────┬────▼──────────┬────▼──────────┐
   │               │               │               │
┌──▼──┐  ┌────────▼────┐  ┌──────┬┴──┐  ┌────────▼─┐
│ Lua │  │ Rust DB     │  │ Home │   │  │ Monitoring│
│ (8) │  │ + MQTT (5)  │  │Assist│   │  │ Go (8006) │
└─────┘  │ Tantivy+    │  └──────┘   │  │+ Prometheus
         │ Redis + Cache│             │  └──────────┘
         └─────────────┘             │
                                     └──HA Cluster
                                       Elixir (9)
```

## 📚 Documentation

### 📋 Utilisateur
- 📖 **[Guide Utilisateur](docs/GUIDE_UTILISATEUR.md)** - Comment utiliser Jarvis
- 🔧 **[API Documentation](docs/API.md)** - Endpoints disponibles  
- 🏗️ **[Architecture](docs/ARCHITECTURE_DOCKER.md)** - Détails techniques
- 📋 **[Changelog](CHANGELOG.md)** - Historique versions

### 🚀 Production v1.3
- 📊 **[Observabilité](prod/OBSERVABILITE_COMPLETE.md)** - Guide complet monitoring
- 🔒 **[Sécurité](prod/nginx-security.conf)** - Configuration Nginx hardened
- ✅ **[Validation](prod/TESTS_VALIDATION.md)** - Tests de validation production
- 🐛 **[Patches Critiques](prod/PATCHES_CRITIQUES.md)** - Corrections appliquées
- 🧪 **[Tests](prod/test-patches.py)** - Suite de tests automatisés

### 🐛 Support
- 🐛 **[Bugs Connus](docs/BUGS.md)** - Problèmes en cours
- 📋 **[Checklist Production](prod/CHECKLIST_VALIDATION.md)** - Procédures déploiement

## 💻 Développement

### Backend Rust (Recommandé)
```bash
cd backend-rust
cp .env.example .env
cargo run  # Mode développement avec hot-reload
```

### Frontend TypeScript
```bash
cd frontend-phase7
npm install
npm run dev  # Next.js dev server
```

### Avec Docker (Stack Complète)
```bash
docker-compose up -d
```

## 🏗️ Structure des Phases

```
backend-rust/           # Phase 1: Core API (Port 8100)
backend-audio/          # Phase 2: C++ Audio (Port 8004)
backend-python-bridges/ # Phase 3: IA Services (Port 8005)
backend-rust-db/        # Phase 4: DB Layer (Lib interne)
backend-rust-mqtt/      # Phase 5: Automations (Lib interne)
monitoring-go/          # Phase 6: Monitoring (Port 8006)
frontend-phase7/        # Phase 7: Frontend (Port 3000)
backend-lua-plugins/    # Phase 8: Plugins (Lib interne)
clustering-elixir/      # Phase 9: HA Cluster (Port 8007)
```

## 🎯 Cas d'Usage

### 💬 Interaction Vocale
- **"Jarvis, allume la lumière du salon"** - Contrôle domotique
- **"Explique-moi Python"** - Assistant développement  
- **"Rappelle-moi RDV à 15h"** - Gestion planning
- **Chat vocal temps réel** - Interface conversationnelle

### 📊 Production v1.3
- **Monitoring temps réel** - Métriques WebSocket, LLM, santé services
- **Debugging distribué** - Request-ID correlation dans tous les logs
- **Alerting intelligent** - Seuils configurables Prometheus
- **Observabilité complète** - De la requête utilisateur aux services internes
- **Sécurité opérationnelle** - Rate limiting + scrubbing secrets automatique

## 🤝 Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit (`git commit -m 'Add: nouvelle fonctionnalité'`)
4. Push (`git push origin feature/nouvelle-fonctionnalite`)  
5. Pull Request

## 📄 Licence

MIT License - voir [LICENSE](LICENSE)

## 👨‍💻 Auteur

**Enzo** - Développeur passionné  
🎓 Ingénierie réseau & cybersécurité  
🏠 Domotique & IA locale

---

### 🔧 Pour développeurs IA

Si vous êtes une IA (Claude, GPT, etc.), consultez d'abord :
1. **[Configuration IA](ai_assistants/CLAUDE_PARAMS.md)** - Paramètres essentiels
2. **[Documentation complète](docs/DOCUMENTATION.md)** - Point d'entrée

---

**⭐ Star ce repo si Jarvis vous intéresse !**