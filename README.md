# 🤖 Jarvis - Assistant IA Personnel

> Assistant vocal intelligent local développé par Enzo, avec reconnaissance vocale, synthèse vocale, IA locale et intégration domotique.

[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)](https://reactjs.org)

## ✨ Fonctionnalités

- 🎤 **Reconnaissance vocale** avec Whisper  
- 🔊 **Synthèse vocale** avec Piper TTS
- 🧠 **IA locale** via Ollama (LLaMA 3.2:1b)
- 💬 **Interface web** moderne style ChatGPT
- 🏠 **Domotique** Home Assistant intégrée
- 🧠 **Mémoire contextuelle** neuromorphique
- 🐳 **Architecture Docker** microservices  
- 🏗️ **Backend modulaire** Factory Pattern + Services
- ⚡ **WebSocket temps réel** avec authentification

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
```bash
git clone https://github.com/username/Projet-Jarvis.git
cd Projet-Jarvis
./start_jarvis_docker.sh
```

**Accès :** `http://localhost:3000`

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

- 📖 **[Guide Utilisateur](docs/GUIDE_UTILISATEUR.md)** - Comment utiliser Jarvis
- 🔧 **[API Documentation](docs/API.md)** - Endpoints disponibles  
- 🏗️ **[Architecture](docs/ARCHITECTURE_DOCKER.md)** - Détails techniques
- 🐛 **[Bugs Connus](docs/BUGS.md)** - Problèmes en cours
- 📋 **[Changelog](docs/CHANGELOG.md)** - Historique versions

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

## 🏗️ Architecture Backend v1.2.0

```
backend/
├── app.py              # 🏭 App Factory + Lifespan
├── config.py           # ⚙️ Pydantic Settings
├── schemas/            # 📋 Validation Pydantic
│   ├── chat.py         # 💬 Messages & Conversations
│   ├── voice.py        # 🎤 STT/TTS
│   ├── memory.py       # 🧠 Mémoire neuromorphique  
│   └── common.py       # 🔧 Réponses standardisées
├── services/           # 🎯 Business Logic
│   ├── llm.py          # 🤖 Ollama LLM Service
│   ├── memory.py       # 🧠 Memory Service
│   ├── voice.py        # 🎤 Voice STT/TTS
│   ├── weather.py      # 🌤️ Weather Service
│   └── home_assistant.py # 🏠 Domotique
├── routers/            # 🌐 API Endpoints
│   ├── health.py       # ✅ Health & Metrics
│   ├── chat.py         # 💬 Chat + Memory
│   ├── voice.py        # 🎤 STT/TTS
│   └── websocket.py    # ⚡ WebSocket temps réel
├── utils/              # 🛠️ Utilitaires
│   ├── validators.py   # 🔒 Sanitisation XSS
│   └── logging.py      # 📝 Logs structurés
└── security/           # 🛡️ Authentification
    └── deps.py         # 🔑 API Keys + CORS
```

## 🎯 Cas d'Usage

- **"Jarvis, allume la lumière du salon"** - Contrôle domotique
- **"Explique-moi Python"** - Assistant développement  
- **"Rappelle-moi RDV à 15h"** - Gestion planning
- **Chat vocal temps réel** - Interface conversationnelle

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