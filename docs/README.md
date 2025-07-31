# Jarvis - Assistant IA Personnel

Assistant vocal intelligent local développé par Enzo, avec des capacités de compréhension du langage, de reconnaissance vocale, de synthèse vocale, d'actions domotiques, d'automatisation et d'interaction multimodale.

## 🎯 Objectifs

**JARVIS V1 - Vision Complète :**
- **Assistant vocal local et privé** 100% offline avec mémoire persistante
- **Intégration domotique** complète avec Home Assistant (Zigbee, MQTT)
- **Mémoire contextuelle** personnalisée avec apprentissage des habitudes
- **Interface web** moderne style ChatGPT ultra-optimisée
- **Architecture modulaire** "poupée russe" avec microservices Docker
- **Comportement intelligent** proactif et adaptatif selon contexte
- **Gaming-aware** avec optimisations performances automatiques
- **Sécurité réseau** intégrée avec monitoring et alertes

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

### ⚠️ PRÉREQUIS CRITIQUES
- **OBLIGATOIRE** : Migration Docker vers /home (voir `docs/MIGRATION_DOCKER_HOME.md`)
- Docker et Docker Compose 
- Node.js 18+
- Python 3.11+
- Ollama (optionnel, inclus dans Docker)
- **Espace disque** : 50GB minimum sur partition /home

### Démarrage rapide

**🚨 ÉTAPE OBLIGATOIRE - Migration Docker :**
```bash  
# Exécuter AVANT tout déploiement
# Voir procédure complète dans docs/MIGRATION_DOCKER_HOME.md
sudo systemctl stop docker
sudo rsync -aP /var/lib/docker/ /home/enzo/jarvis-docker/
sudo tee /etc/docker/daemon.json << EOF
{
  "data-root": "/home/enzo/jarvis-docker",
  "storage-driver": "overlay2"
}
EOF
sudo systemctl start docker
```

**📋 Après migration Docker :**

1. **Configuration**
```bash
cd "Projet Jarvis"
cp .env.example .env
# Éditez .env avec vos paramètres
```

2. **Démarrage architecture complète**
```bash
./start_jarvis_docker.sh
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

### Interface Web ChatGPT Style
- Accédez à `http://localhost:3000`
- **Chat textuel** : Tapez votre message et appuyez Entrée
- **Chat vocal** : Cliquez sur 🎤, parlez, le texte se remplit automatiquement
- **Réponses IA** : Ollama + LLaMA 3.1 en français
- **Performance** : Interface ultra-optimisée, zéro lag

### Commandes vocales
- "Bonjour Jarvis, comment ça va ?"
- "Explique-moi la programmation Python"
- "Aide-moi à organiser ma journée"

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

### ⚠️ V1 PARTIELLEMENT IMPLÉMENTÉE - MIGRATION DOCKER REQUISE

**🚨 PROBLÈME CRITIQUE IDENTIFIÉ (2025-07-31) :**
- **Partition root saturée** : 120GB occupés par Docker
- **Builds impossibles** : Plus d'espace pour Backend/Interface  
- **SOLUTION** : Migration Docker vers /home (voir `docs/MIGRATION_DOCKER_HOME.md`)

**📋 ÉTAT ACTUEL (5/7 containers) :**
- [x] **Interface web React** style ChatGPT ultra-optimisée
- [x] **API FastAPI** avec WebSocket temps réel (compilation OK)
- [x] **Architecture Docker "poupée russe"** 5/7 services actifs
- [x] **Base de données PostgreSQL** + mémoire vectorielle (config partielle)
- [x] **Intégration Ollama** avec LLaMA 3.1 100% fonctionnelle
- [x] **Gestion profils utilisateurs** avec CRUD complet
- [x] **Système mémoire contextuelle** avec embeddings
- [ ] **Reconnaissance vocale Whisper** (services demo uniquement)
- [ ] **API endpoints vocaux** (présents mais non testés)
- [ ] **Interface vocale React** (Speech Recognition API native)
- [ ] **Chat textuel + vocal** en temps réel (backend manquant)
- [ ] **Synthèse vocale TTS** (services demo uniquement)
- [x] **Logs détaillés** avec emojis pour debugging
- [x] **Performance optimisée** (RAM divisée par 10)
- [ ] **WebSocket audio bridge** (non testé)
- [x] **Mémoire conversationnelle** avec flags importance
- [ ] **Auto-update mémoire** (configuration incomplète)
- [ ] **Filtrage hallucinations STT** (non validé)
- [ ] **CORS sécurisé** (à configurer)
- [ ] **Logs conversations** automatiques (non actifs)

**⚠️ AUDIT INSTANCE #1 (21/07/2025) : V1 FONCTIONNELLE MAIS INCOMPLÈTE**

### 🔄 En cours
- [ ] Intégration Home Assistant complète
- [ ] Système de plugins/modules
- [ ] Amélioration synthèse vocale avec vraies voix
- [ ] Optimisations performance avancées

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