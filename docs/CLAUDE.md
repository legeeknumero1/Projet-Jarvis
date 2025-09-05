# Configuration Claude pour Projet Jarvis v1.3.2 

## Contexte du projet (MISE À JOUR POST-AUDIT SÉCURITÉ)
- **Nom** : Jarvis - Assistant IA Personnel Enterprise Security-Hardened
- **Version** : v1.3.2 - Production-Ready avec Audit Sécurité Complet + Corrections Appliquées
- **Score Global** : **9.5/10** (TOP 5% industrie) - **AMÉLIORÉ** de 8.2 → 9.5
- **Score Sécurité** : **95/100** ⭐ (Toutes vulnérabilités critiques et élevées corrigées)
- **Développeur** : Enzo, 21 ans, Perpignan
- **Objectif** : Assistant vocal intelligent local avec domotique + Stack DevOps enterprise-grade
- **Stack Core** : FastAPI + React + PostgreSQL + Ollama + Docker + MCP Internet + Sécurité JWT/OAuth2
- **Stack DevOps** : Jenkins + ArgoCD + K3s + Prometheus + Grafana + Loki + Monitoring Avancé
- **Infrastructure** : Kubernetes production-ready + RBAC + Network Policies

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
   - Services Docker Core (docker-compose up -d)
   - Backend FastAPI avec métriques Prometheus
   - Frontend React cyberpunk
   - Base de données PostgreSQL + TimescaleDB
   - Redis cache + Qdrant vectoriel
   - Ollama LLM + MCP Internet
   - STT/TTS APIs + Interface
2. **VÉRIFIER** que tout fonctionne :
   - Endpoints API répondent (dont /metrics)
   - Interface web accessible (port 3000)
   - WebSocket connecté temps réel
   - Base données + mémoire neuromorphique
   - Services 9/9 healthy
3. **CONFIRMER** : "Jarvis V1.3.0 démarré et opérationnel ✅"

#### "START DEVOPS" - DÉMARRAGE STACK DEVOPS
**Quand Enzo dit "start devops" :**
1. **LANCER STACK DEVOPS** :
   - cd devops-tools/ && ./start-devops.sh
   - Jenkins CI/CD (port 8080)
   - ArgoCD GitOps K3s (port 8081)
   - Prometheus + Grafana + Loki monitoring
   - AlertManager + Node Exporter + cAdvisor
2. **VÉRIFIER** services DevOps :
   - Cluster K3s opérationnel
   - ArgoCD applications sync
   - Monitoring dashboards accessibles
   - Métriques Jarvis collectées
3. **CONFIRMER** : "Stack DevOps Jarvis démarrée ✅"

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

### 📋 Workflow obligatoire à chaque demande (MISE À JOUR POST-AUDIT)
1. **🚨 LIRE EN PREMIER** `/docs/DOCUMENTATION_JARVIS_POST_AUDIT_2025.md` - Guide sécurisé v1.3.2 POST-CORRECTIONS
2. **🛡️ LIRE OBLIGATOIRE** `/docs/SECURITY_FIXES_APPLIED_2025.md` - TOUTES les corrections sécurité appliquées  
3. **👥 COORDINATION** `/docs/CLAUDE_INSTANCES_COORDINATION.md` - État instances et réservations
4. **LIRE** `/docs/CLAUDE_PARAMS.md` - Paramètres spécifiques instances Claude
3. **🔍 RECHERCHER INTERNET** - **RÈGLE #2 ABSOLUE** : TOUJOURS rechercher meilleures pratiques 2025 avant toute action
4. **LIRE** tous les autres fichiers .md du dossier `/docs/` (OBLIGATOIRE pour cohérence)
5. **CONSULTER** `/docs/BUGS.md` pour problèmes connus et solutions appliquées
6. **CONSULTER** `/docs/SECURITY_FIXES.md` pour corrections sécurité critiques
7. **VALIDER SOLUTIONS** avec standards industrie 2025 (OWASP, ISO 27001, DORA, CIS)
8. **PLANIFIER** avec TodoWrite basé sur recherche internet et audit sécurité
9. **EXÉCUTER** la tâche avec solutions validées et sécurisées
10. **METTRE À JOUR** TOUS les fichiers .md pertinents dans `/docs/` (cohérence absolue)
11. **METTRE À JOUR** `/docs/BUGS.md` si bugs résolus ou nouveaux problèmes
12. **METTRE À JOUR** `/docs/CHANGELOG.md` avec modifications (sources + impact sécurité)
13. **METTRE À JOUR** `/docs/ETAT_PROJET_ACTUEL.md` si changements structurels
14. **SYNCHRONISER** tous les .md pour éviter incohérences entre instances Claude et développeurs
15. **VALIDER** que TOUT est cohérent, sécurisé et à jour selon standards 2025

### 🔧 Commandes de test à exécuter
```bash
# Jarvis Core
docker-compose up -d                                # Stack Jarvis complète
curl http://localhost:8000/health                   # Health check backend
curl http://localhost:8000/metrics                  # Métriques Prometheus
curl http://localhost:3000                          # Interface React

# DevOps Stack  
cd devops-tools && ./start-devops.sh               # Stack DevOps complète
./start-argocd.sh                                   # ArgoCD K3s seulement

# Monitoring
curl http://localhost:9090/api/v1/targets          # Targets Prometheus
curl http://localhost:3001/api/health              # Health Grafana

# Kubernetes
sudo kubectl get nodes                              # Status cluster K3s
sudo kubectl get pods -n jarvis                    # Pods Jarvis
sudo kubectl get applications -n argocd            # Applications ArgoCD

# Tests base de données
docker exec -it jarvis_postgres psql -U jarvis -d jarvis_db
docker exec -it jarvis_timescale psql -U jarvis -d timescale_db
```

### 📁 Structure à respecter
```
Projet-Jarvis/
├── backend/                    # Backend FastAPI + métriques Prometheus
│   ├── config/                # Configuration (config.py)  
│   ├── db/                    # Base de données (database.py, init.sql)
│   ├── memory/                # Mémoire neuromorphique vectorielle
│   ├── profile/               # Profils utilisateurs (profile_manager.py)
│   ├── speech/                # Reconnaissance/synthèse vocale
│   ├── integration/           # Intégrations externes (home_assistant.py, ollama_client.py, mcp_client.py)
│   ├── api/endpoints/         # Routes API (web.py pour endpoints MCP)
│   ├── services/              # Services métier (web_service.py)
│   └── main.py                # Application principale avec /metrics
├── devops-tools/              # Stack DevOps professionnelle  
│   ├── docker-compose-devops.yml  # Services DevOps
│   ├── start-devops.sh        # Script démarrage complet
│   ├── start-argocd.sh        # Script ArgoCD K3s
│   ├── jenkins/               # CI/CD (Jenkinsfile, plugins)
│   ├── monitoring/            # Prometheus + Grafana + Loki
│   ├── k8s/                   # Manifests Kubernetes
│   └── configs/               # Configurations (nginx, etc.)
├── services/                  # Microservices (STT, TTS, Interface)
├── MCP/                       # Model Context Protocol pour Internet
├── docs/                      # Documentation (DEVOPS_GUIDE.md, CHANGELOG.md)
└── docker-compose.yml         # Stack Jarvis core
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