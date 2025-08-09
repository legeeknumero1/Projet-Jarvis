# 🤖 Jarvis - Assistant IA Personnel v1.3 "Production Hardening"

> Assistant vocal intelligent local production-ready développé par Enzo, avec reconnaissance vocale, synthèse vocale, IA locale et observabilité complète.

[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)](https://reactjs.org)
[![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)](https://prometheus.io)

## ✨ Fonctionnalités v1.3

### 🎯 Core Features
- 🎤 **Reconnaissance vocale** avec Whisper  
- 🔊 **Synthèse vocale** avec Piper TTS
- 🧠 **IA locale** via Ollama (LLaMA 3.2:1b)
- 💬 **Interface web** moderne style ChatGPT
- 🏠 **Domotique** Home Assistant intégrée
- 🧠 **Mémoire contextuelle** neuromorphique

### 🚀 Production Ready v1.3
- 📊 **Observabilité complète** Prometheus + logs JSON
- 🔒 **Sécurité renforcée** rate limiting + scrubbing secrets  
- ⚡ **Graceful shutdown** WebSocket drain mode
- 🔍 **Request tracing** correlation logs bout-en-bout
- 🛡️ **Nginx hardened** headers sécurité + TLS
- 🎯 **Health checks** Kubernetes ready
- 📈 **Métriques temps réel** /metrics endpoint
- 🐳 **Stack monitoring** Grafana + ELK intégrés

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
- Interface : `http://localhost:3000`
- API : `http://localhost:8000`
- Métriques : `http://localhost:8000/metrics`
- Grafana : `http://localhost:3000` (prod stack)

## 🏗️ Architecture

```
┌─────────────────────┐    ┌─────────────────────┐
│   Interface React   │    │     Brain API       │
│     Port 3000       │◄──►│     Port 8000       │
└─────────────────────┘    └─────────────────────┘
                                       │
        ┌──────────────────────────────┼──────────────────────────────┐
        │                              │                              │
┌───────▼────────┐    ┌────────▼───────┐    ┌────────▼───────┐
│   STT Service  │    │  Ollama LLM    │    │   TTS Service  │
│   Port 8003    │    │  Port 11434    │    │   Port 8002    │
└────────────────┘    └────────────────┘    └────────────────┘
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

```bash
# Backend (Architecture Refactorisée v1.2.0)
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload  # Nouveau point d'entrée app factory

# Frontend  
cd frontend
npm install
npm start
```

## 🏗️ Architecture Backend v1.3 Production

```
backend/
├── app.py                    # 🏭 App Factory + Lifespan + Config
├── config.py                 # ⚙️ Pydantic Settings
├── schemas/                  # 📋 Validation Pydantic
│   ├── chat.py               # 💬 Messages & Conversations
│   ├── voice.py              # 🎤 STT/TTS
│   ├── memory.py             # 🧠 Mémoire neuromorphique  
│   └── common.py             # 🔧 Réponses standardisées
├── services/                 # 🎯 Business Logic
│   ├── llm.py                # 🤖 Ollama LLM + Retry + Metrics
│   ├── memory.py             # 🧠 Memory Service
│   ├── voice.py              # 🎤 Voice STT/TTS
│   ├── weather.py            # 🌤️ Weather Service
│   └── home_assistant.py     # 🏠 Domotique
├── routers/                  # 🌐 API Endpoints
│   ├── health.py             # ✅ Health & Readiness Probes
│   ├── chat.py               # 💬 Chat + Memory + Rate Limit
│   ├── voice.py              # 🎤 STT/TTS
│   └── websocket.py          # ⚡ WebSocket + Graceful Shutdown
├── middleware/               # 🔧 Production Middleware  
│   └── request_context.py    # 🔍 Request-ID + Correlation
├── observability/            # 📊 Métriques + Monitoring
│   └── metrics.py            # 📈 Prometheus Metrics
├── security/                 # 🛡️ Sécurité Renforcée
│   ├── deps.py               # 🔑 API Keys + CORS
│   └── rate_limit.py         # 🚫 Rate Limiting Anti-abus
├── utils/                    # 🛠️ Utilitaires Production
│   ├── validators.py         # 🔒 Sanitisation XSS
│   ├── logging.py            # 📝 JSON Logs + Contextvars
│   └── ws_manager.py         # 🔌 WebSocket Manager + Metrics
└── prod/                     # 🚀 Configuration Production
    ├── logs-config.json      # 📊 Logging JSON Production
    ├── logs-config-k8s.json  # ☸️ Logging Kubernetes
    ├── nginx-security.conf   # 🛡️ Nginx Sécurisé + Rate Limit
    ├── docker-compose.prod.yml # 🐳 Stack Production
    ├── docker-compose.logs.yml # 📊 Stack Monitoring
    └── test-patches.py       # 🧪 Tests Automatisés
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