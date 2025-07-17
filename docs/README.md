# Jarvis - Assistant IA Personnel

Assistant vocal intelligent local développé par Enzo, avec des capacités de compréhension du langage, de reconnaissance vocale, de synthèse vocale, d'actions domotiques, d'automatisation et d'interaction multimodale.

## 🎯 Objectifs

- Assistant vocal local et privé
- Intégration complète avec Home Assistant
- Mémoire contextuelle personnalisée
- Interface web moderne et responsive
- Modularité et extensibilité

## 🏗️ Architecture

### Backend (FastAPI + Python)
- **API REST** et **WebSocket** pour la communication temps réel
- **Reconnaissance vocale** avec Whisper
- **Synthèse vocale** avec Piper TTS
- **LLM local** via Ollama (LLaMA 3.1)
- **Mémoire vectorielle** avec PostgreSQL et embeddings
- **Intégration domotique** via Home Assistant et MQTT

### Frontend (React)
- Interface utilisateur moderne et intuitive
- Support vocal temps réel
- Visualisation des conversations
- Contrôles domotiques intégrés

### Infrastructure
- **Docker Compose** pour le déploiement
- **PostgreSQL** pour la persistance
- **Redis** pour le cache et les sessions
- **Ollama** pour l'IA locale

## 🚀 Installation

### Prérequis
- Docker et Docker Compose
- Node.js 18+
- Python 3.11+
- Ollama (optionnel, inclus dans Docker)

### Démarrage rapide

1. **Clonez le projet**
```bash
git clone <repository-url>
cd "Projet Jarvis"
```

2. **Configuration**
```bash
cp .env.example .env
# Éditez .env avec vos paramètres
```

3. **Démarrage avec Docker**
```bash
docker-compose up -d
```

4. **Ou développement local**

Backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

Frontend:
```bash
cd frontend
npm install
npm start
```

## 📁 Structure du projet

```
Projet Jarvis/
├── backend/
│   ├── api/              # Routes API
│   ├── config/           # Configuration
│   ├── db/              # Base de données
│   ├── integration/     # Intégrations externes
│   ├── memory/          # Gestion mémoire
│   ├── profile/         # Profils utilisateurs
│   ├── search/          # Recherche
│   ├── speech/          # Reconnaissance/synthèse vocale
│   └── main.py          # Application principale
├── frontend/
│   ├── src/
│   │   ├── components/  # Composants React
│   │   ├── hooks/       # Hooks personnalisés
│   │   ├── services/    # Services API
│   │   └── utils/       # Utilitaires
│   └── public/          # Fichiers statiques
├── models/              # Modèles IA
├── logs/                # Logs
├── data/                # Données
└── docker-compose.yml   # Configuration Docker
```

## 🎮 Utilisation

### Interface Web
- Accédez à `http://localhost:3000`
- Utilisez le chat textuel ou vocal
- Configurez vos préférences

### Commandes vocales
- "Jarvis, allume la lumière du salon"
- "Jarvis, quelle est la température ?"
- "Jarvis, rappelle-moi de sortir le chien à 15h"

### API REST
- `GET /health` - Statut du système
- `POST /chat` - Envoi de message
- `WS /ws` - WebSocket temps réel

## 🔧 Configuration

### Variables d'environnement
Voir le fichier `.env` pour toutes les options de configuration.

### Workflow de développement
Ce projet suit un workflow strict défini dans `CLAUDE.md` :
1. Consultation des fichiers .md
2. Recherche des meilleures pratiques
3. Planification avec TodoWrite
4. Implémentation et test
5. Mise à jour documentation

### Modèles IA
- **Whisper** : Reconnaissance vocale (base, small, medium, large)
- **Piper** : Synthèse vocale française
- **LLaMA** : Modèle de langage local

### Home Assistant
Configurez votre token et URL Home Assistant dans `.env` pour l'intégration domotique.

## 🎯 Fonctionnalités

### ✅ Implémentées
- [x] Interface web React
- [x] API FastAPI avec WebSocket
- [x] Architecture modulaire
- [x] Configuration Docker
- [x] Base de données PostgreSQL
- [x] Intégration Ollama avec LLaMA 3.1
- [x] Gestion des profils utilisateurs
- [x] Système de mémoire vectorielle
- [x] Reconnaissance vocale Whisper (backend)
- [x] API endpoints vocaux (/voice/transcribe, /voice/synthesize)
- [x] Interface vocale React (Speech Recognition API)
- [x] Chat en temps réel avec WebSocket
- [x] Synthèse vocale Piper (backend, partiellement)

### 🔄 En cours
- [ ] Intégration Home Assistant complète
- [ ] Système de plugins/modules
- [ ] Amélioration de la synthèse vocale
- [ ] Installation complète des dépendances audio

### 📋 Planifiées
- [ ] Reconnaissance de contexte ambiant
- [ ] Gestion multi-utilisateurs
- [ ] Interface mobile
- [ ] Intégration caméras
- [ ] Automatisation avancée

## 🏠 Intégration Domotique

### Home Assistant
- Contrôle des lumières, chauffage, capteurs
- Automatisations basées sur le contexte
- Notifications et alertes

### MQTT
- Communication temps réel avec les appareils
- Capteurs environnementaux
- Actionneurs domotiques

## 🔒 Sécurité et Confidentialité

- **Traitement local** : Toutes les données restent sur votre infrastructure
- **Chiffrement** : Communications sécurisées
- **Isolation** : Conteneurisation Docker
- **Authentification** : Système de tokens

## 📊 Performance

- **Temps de réponse** : <500ms pour les requêtes simples
- **Mémoire** : Optimisée pour les environnements contraints
- **Scalabilité** : Architecture modulaire extensible

## 🛠️ Développement

### Tests
```bash
# Backend
cd backend
python -m pytest

# Frontend
cd frontend
npm test
```

### Contribution
1. Fork le projet
2. Créez une branche (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commitez vos changements (`git commit -m 'Ajoute nouvelle fonctionnalité'`)
4. Pushez vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrez une Pull Request

## 📝 License

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 👨‍💻 Auteur

**Enzo** - Développeur passionné d'IA et domotique
- Âge: 21 ans
- Localisation: Perpignan, France
- Objectif: Ingénieur réseau et cybersécurité

## 🙏 Remerciements

- OpenAI pour Whisper
- Ollama pour l'IA locale
- Home Assistant pour l'écosystème domotique
- La communauté open-source