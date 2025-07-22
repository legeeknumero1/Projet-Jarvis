# Configuration Claude pour Projet Jarvis

## Contexte du projet
- **Nom** : Jarvis - Assistant IA Personnel
- **Développeur** : Enzo, 21 ans, Perpignan
- **Objectif** : Assistant vocal intelligent local avec domotique
- **Stack** : FastAPI + React + PostgreSQL + Ollama + Docker

## Instructions permanentes

### 🎯 Toujours faire (ORDRE OBLIGATOIRE)
1. **LIRE D'ABORD** : Consulter TOUS les fichiers .md du projet (README.md, CLAUDE.md, etc.)
2. **RECHERCHER** : Vérifier sur internet si ma solution/approche est optimale et à jour
3. **PLANIFIER** : Utiliser le TodoWrite pour planifier et suivre les tâches
4. **IMPLÉMENTER** : Respecter l'architecture modulaire existante
5. **TESTER** : Tester les fonctionnalités après implémentation
6. **DOCUMENTER** : Documenter le code en français
7. **METTRE À JOUR** : Toujours mettre à jour les fichiers .md concernés après chaque action
8. **PRIVILÉGIER** : Solutions locales (pas de cloud)
9. **MAINTENIR** : Compatibilité avec Home Assistant
10. **📝 CHATGPT.md** : **RÈGLE ABSOLUE** - Documenter TOUT dans `/docs/CHATGPT.md` à 100% (pensées, bugs, recherches, demandes Enzo, actions, tests, décisions)

### 🚀 Commandes spéciales Enzo

#### "START JARVIS" - DÉMARRAGE COMPLET
**Quand Enzo dit "start jarvis" :**
1. **LANCER IMMÉDIATEMENT** tous les services Jarvis :
   - Backend FastAPI (uvicorn main:app)
   - Frontend React (npm start)
   - Services Docker (docker-compose up -d)
   - Base de données PostgreSQL
   - Redis cache
   - Ollama LLM
2. **VÉRIFIER** que tout fonctionne :
   - Endpoints API répondent
   - Interface web accessible
   - WebSocket connecté
   - Base données connectée
3. **CONFIRMER** : "Jarvis V1.1.0 démarré et opérationnel ✅"

#### "STOP JARVIS" - ARRÊT PROPRE
**Quand Enzo dit "stop jarvis" :**
1. **ARRÊTER PROPREMENT** tous les services :
   - Fermer connexions base données
   - Arrêter serveurs web
   - docker-compose down (graceful)
   - Sauvegarder état si nécessaire
2. **VÉRIFIER** arrêt complet :
   - Ports libérés
   - Processus terminés
   - Pas de corruption
3. **CONFIRMER** : "Jarvis arrêté proprement ✅"

### 📋 Workflow obligatoire à chaque demande
1. **LIRE** `/docs/CLAUDE_PARAMS.md` EN PREMIER ABSOLU
2. **LIRE** tous les autres fichiers .md du dossier `/docs/` (OBLIGATOIRE)
3. **CONSULTER** `/docs/BUGS.md` pour les problèmes connus
4. **RECHERCHER** sur internet les meilleures pratiques/solutions récentes
5. **PLANIFIER** avec TodoWrite
6. **EXÉCUTER** la tâche
7. **METTRE À JOUR** les fichiers .md pertinents dans `/docs/`
8. **METTRE À JOUR** `/docs/BUGS.md` si bugs résolus ou nouveaux bugs
9. **METTRE À JOUR** `/docs/CHANGELOG.md` avec les modifications
10. **VALIDER** que tout est cohérent et à jour

### 🔧 Commandes de test à exécuter
```bash
# Backend
cd backend && source venv/bin/activate && python -m uvicorn main:app --reload

# Frontend  
cd frontend && npm start

# Docker
docker-compose up -d

# Tests base de données
docker exec -it jarvis_postgres psql -U jarvis -d jarvis_db
```

### 📁 Structure à respecter
```
backend/
├── config/         # Configuration (config.py)
├── db/             # Base de données (database.py, init.sql)
├── memory/         # Mémoire vectorielle (memory_manager.py)
├── profile/        # Profils utilisateurs (profile_manager.py)
├── speech/         # Reconnaissance/synthèse vocale (speech_manager.py)
├── integration/    # Intégrations externes (home_assistant.py, ollama_client.py)
├── api/            # Routes API (si besoin)
└── main.py         # Application principale
```

### 🎨 Préférences de développement
- **Langue** : Français pour les commentaires et logs
- **Style** : Code propre, modulaire, bien documenté
- **Sécurité** : Toujours valider les entrées utilisateur
- **Performance** : Optimiser pour du matériel local
- **Monitoring** : Logs détaillés pour debug

### 🏠 Intégrations prioritaires
1. **Home Assistant** : Contrôle lumières, chauffage, capteurs
2. **MQTT** : Communication temps réel
3. **Ollama** : LLM local (LLaMA 3.1)
4. **Whisper** : Reconnaissance vocale
5. **Piper** : Synthèse vocale française

### 🚀 Fonctionnalités à implémenter (ordre de priorité)
1. Reconnaissance vocale avec Whisper
2. Synthèse vocale avec Piper
3. Intégration Ollama complète
4. Connexion Home Assistant
5. Système de mémoire contextuelle
6. Interface domotique dans le frontend
7. Automatisations basées sur le contexte
8. Système de plugins/modules

### 💡 Cas d'usage typiques
- "Jarvis, allume la lumière du salon"
- "Jarvis, quelle est la température ?"
- "Jarvis, rappelle-moi de sortir le chien à 15h"
- "Jarvis, lance la musique dans la cuisine"
- "Jarvis, active le mode nuit"

### 🔍 Debugging
- Toujours vérifier les logs dans `./logs/`
- Tester les endpoints avec curl ou Postman
- Utiliser les outils de développement React
- Monitorer les performances avec les métriques intégrées

### 📊 Métriques importantes
- Temps de réponse < 500ms
- Précision reconnaissance vocale > 95%
- Disponibilité > 99.5%
- Utilisation mémoire < 2GB

### 🔒 Sécurité
- Jamais de secrets dans le code
- Validation stricte des entrées
- Logs sécurisés (pas de données sensibles)
- Chiffrement des communications

### 📝 Documentation (MISE À JOUR OBLIGATOIRE)
- **README.md** : Toujours à jour avec les nouvelles fonctionnalités
- **CLAUDE.md** : Mis à jour avec les nouvelles instructions/configurations
- **Fichiers techniques** : Documentation API, guides d'installation, etc.
- **Commentaires** : En français, mis à jour à chaque modification
- **Changelog** : Documenter chaque changement important

### 🔄 Règles de mise à jour des fichiers .md
- **Après chaque implémentation** : Mettre à jour `/docs/README.md` section concernée
- **Après chaque configuration** : Mettre à jour `/docs/CLAUDE.md` si nécessaire
- **Après chaque test** : Documenter les résultats et procédures
- **Après chaque debug** : Ajouter les solutions trouvées dans `/docs/BUGS.md`
- **Après chaque modification** : Mettre à jour `/docs/CHANGELOG.md`
- **JAMAIS SUPPRIMER** : Ne jamais supprimer de contenu sauf ordre explicite d'Enzo
- **Cohérence** : Vérifier que tous les .md sont cohérents entre eux

## Notes spéciales
- Environnement : Arch Linux avec Hyprland
- Matériel : i9-14900KF, RTX 4080, 32GB RAM
- Réseau : Infrastructure haute performance avec VLANs
- Préférence pour l'auto-hébergement et la vie privée