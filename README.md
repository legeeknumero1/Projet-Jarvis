# 🤖 Jarvis - Assistant IA Personnel v1.2.0

[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Ollama](https://img.shields.io/badge/Ollama-llama3.2:1b-purple)](https://ollama.ai/)
[![MCP](https://img.shields.io/badge/MCP-Internet%20Access-orange)](https://modelcontextprotocol.io/)

## 🚀 **STATUS: JARVIS OPÉRATIONNEL + INTERNET ACCESS !** 

**🌐 NOUVELLE FONCTIONNALITÉ : Jarvis peut maintenant accéder à Internet !**

**Architecture 9/9 services déployée avec succès :**
- ✅ STT (Speech-to-Text) - Port 8003 - Reconnaissance vocale
- ✅ TTS (Text-to-Speech) - Port 8002 - Synthèse vocale
- ✅ Ollama LLM - Port 11434 - Intelligence artificielle locale
- ✅ Backend API - Port 8000 - **Nouveau : Endpoints Internet MCP**
- ✅ Interface Web - Port 3000 - React cyberpunk avec WebSocket
- ✅ PostgreSQL - Base de données principale  
- ✅ Redis - Cache et sessions
- ✅ Qdrant - Mémoire vectorielle neuromorphique
- ✅ TimescaleDB - Métriques temporelles
- 🌐 **MCP Browserbase** - **NOUVEAU** - Navigation web automatisée

---

## 🌐 **NOUVELLES CAPACITÉS INTERNET**

### 🔍 **Jarvis peut maintenant :**
- **Naviguer sur le web** : Accéder à n'importe quelle page internet
- **Rechercher en temps réel** : Effectuer des recherches automatiques
- **Prendre des captures d'écran** : Screenshots de sites web
- **Extraire des données** : Analyser et extraire contenu web
- **Interagir avec les pages** : Cliquer, remplir des formulaires, actions automatisées

### 🔧 **Endpoints Internet API**
```bash
# Recherche web
curl -X POST http://localhost:8000/web/search \
  -H "Content-Type: application/json" \
  -d '{"query": "actualités technologie 2025"}'

# Récupérer contenu d'une page
curl -X POST http://localhost:8000/web/content \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# Capture d'écran
curl -X POST http://localhost:8000/web/screenshot \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "full_page": true}'
```

### ⚙️ **Configuration MCP (Optionnel)**
Pour activer toutes les capacités internet :
```bash
# 1. Créer un compte sur https://www.browserbase.com/
# 2. Ajouter vos clés dans .env
BROWSERBASE_API_KEY=votre_clé_ici
BROWSERBASE_PROJECT_ID=votre_projet_ici
GEMINI_API_KEY=votre_clé_gemini  # Optionnel
```

---

## 💬 **COMMENT PARLER À JARVIS**

### 🎯 **API Backend Complète**
```bash
# Chat avec Jarvis (API principale)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Bonjour Jarvis!", "user_id": "enzo"}'

# Chat avec Ollama direct
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3.2:1b", "prompt": "Bonjour!", "stream": false}' \
  | jq -r '.response'
```

### 🌐 **Interfaces Disponibles**
- **Interface React** : http://localhost:3000 - Interface cyberpunk principale
- **API Backend** : http://localhost:8000 - Documentation Swagger
- **WebSocket** : ws://localhost:8001/ws - Communication temps réel
- **Documentation STT** : http://localhost:8003/docs
- **Documentation TTS** : http://localhost:8002/docs

---

## 🐳 **DÉMARRAGE DOCKER**

### **Lancement Complet**
```bash
# Méthode simple
docker-compose up -d

# Ou méthode avec tests
./scripts/test-docker.sh
```

### **Gestion Avancée**
```bash
# Script intelligent (évite doublons)
./scripts/manage-containers.sh rebuild

# Nettoyage si problèmes
./scripts/manage-containers.sh clean-all
```

---

## 🧠 **CAPACITÉS TESTÉES DE JARVIS**

### ✅ **Forces**
- **Conversation naturelle** en français
- **Programmation** Python avec documentation
- **Créativité** poésie, écriture
- **Explications techniques** vulgarisées
- **Assistant personnel** proactif

### ⚠️ **Limitations Connues**
- **Mémoire conversationnelle** : absente
- **Calculs complexes** : erreurs fréquentes  
- **Logique multi-étapes** : approximative
- **Contexte** : perdu entre interactions

### 🎯 **Usage Recommandé**
- ✅ Questions simples et explications
- ✅ Aide à la programmation basique
- ✅ Brainstorming et créativité
- ❌ Éviter : calculs, analyses de données, suivi contextuel

---

## 🏗️ **ARCHITECTURE TECHNIQUE**

### **Services Docker (Architecture "Poupée Russe")**
```
┌─ Interface (3000/8001) ─────┐
├─ Backend API (8000) ───────┤  
├─ STT API (8003) ──────────┤
├─ TTS API (8002) ──────────┤
├─ Ollama LLM (11434) ──────┤
├─ Qdrant Vector (6333) ────┤
├─ PostgreSQL (5432) ───────┤
└─ Redis Cache (6379) ──────┘
```

### **Technologies**
- **IA** : Ollama llama3.2:1b (CPU), OpenAI Whisper, Coqui-TTS
- **Backend** : FastAPI + SQLAlchemy + AsyncPG
- **Databases** : PostgreSQL, Redis, Qdrant Vector DB
- **Frontend** : React + WebSocket temps réel
- **Infrastructure** : Docker Compose 7 services

---

## 📁 **STRUCTURE PROJET**

```
Projet Jarvis/
├── 🐳 docker-compose.yml     # Architecture complète
├── 📜 scripts/              # Scripts de gestion
│   ├── chat-jarvis.sh       # Chat simple avec Jarvis
│   ├── manage-containers.sh # Gestion containers
│   └── test-docker.sh       # Tests architecture
├── 🧠 services/             # Services IA
│   ├── stt/                 # Speech-to-Text (Whisper)
│   ├── tts/                 # Text-to-Speech (Coqui)
│   └── interface/           # Interface utilisateur
├── ⚡ backend/              # API principale (Factory Pattern)
├── 📚 docs/                 # Documentation complète
└── 🔧 config/              # Configurations
```

---

## 🚦 **TESTS & VALIDATION**

### **Tests Réussis ✅**
- Architecture Docker 7/7 services
- Conversation française fluide  
- Programmation Python
- Services STT/TTS opérationnels
- Intégration LLM Ollama

### **En Cours de Correction 🔄**
- Backend API Factory Pattern
- Interface Web React
- Système de mémoire contextuelle
- WebSocket temps réel

---

## 🛠️ **DÉVELOPPEMENT**

### **Contribution**
```bash
# Fork du projet
git clone https://github.com/[user]/Projet-Jarvis.git

# Développement local
docker-compose -f docker-compose.dev.yml up -d

# Tests
./scripts/test-docker.sh
```

### **Standards**
- **Code** : Python 3.12, TypeScript, Factory Pattern
- **Tests** : pytest, Docker health checks
- **Documentation** : Inline + Swagger
- **Git** : Commits conventionnels

---

## 📞 **SUPPORT**

### **Dépannage**
```bash
# Logs détaillés
docker-compose logs -f [service]

# Redémarrage propre
./scripts/manage-containers.sh rebuild

# Nettoyage complet
docker system prune -f
```

### **Liens Utiles**
- 📖 **Documentation complète** : `/docs/`
- 🐛 **Issues** : GitHub Issues
- 💬 **Chat** : `./scripts/chat-jarvis.sh`

---

## 🤖 INSTANCES CLAUDE - AUTO-INITIALISATION ⚡

**Votre instance Claude s'initialise AUTOMATIQUEMENT à l'ouverture du projet !**

### ✅ Auto-initialisation (normal)
- Détection automatique du projet Jarvis
- Lecture de tous les fichiers `/docs/`
- Attribution automatique du numéro d'instance
- Configuration complète en quelques secondes
- **Aucune action requise !**

### 🔧 Initialisation manuelle (fallback)
**Si l'auto-init échoue, tapez :**
```
lis doc
```

---

## 📊 **MÉTRIQUES**

- **Temps de démarrage** : ~2 minutes (avec build)
- **Mémoire Docker** : ~12GB (architecture complète)
- **Réactivité LLM** : 1-10 secondes/réponse
- **Services simultanés** : 7/7 opérationnels

---

## 📝 **CHANGELOG**

### v1.3.0 - Production Hardening (2025-01-17)
- ✅ Architecture Docker 7 services opérationnelle
- ✅ Ollama LLM intégré (llama3.2:1b CPU)
- ✅ Services STT/TTS validés
- ✅ Scripts de gestion intelligents
- 🔄 Corrections Backend/Interface en cours

### v1.2.0 - Refactor Frontend Modulaire
- ✅ Frontend React modulaire atomic design
- ✅ Backend Factory Pattern refactorisé
- ✅ Intégrations multi-services

### v1.1.0 - Services IA
- ✅ Speech-to-Text Whisper
- ✅ Text-to-Speech Coqui
- ✅ Base de données vectorielle

---

**🎉 Jarvis est maintenant opérationnel ! Testez avec `./scripts/chat-jarvis.sh "Bonjour Jarvis"` 🤖**