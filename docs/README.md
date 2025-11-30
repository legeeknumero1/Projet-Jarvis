# 📚 Documentation Jarvis v1.9.0

Documentation complète du projet Jarvis - Assistant IA polyglotte.

## 📖 Documentation Principale

### Architecture & Design
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Architecture 9-phases complète du système
- **[ROADMAP_POLYGLOTTE.md](ROADMAP_POLYGLOTTE.md)** - Feuille de route v2.0

### Guides d'utilisation
- **[API.md](API.md)** - Documentation API REST/WebSocket
- **[API_EXAMPLES.md](API_EXAMPLES.md)** - Exemples d'utilisation API

### Déploiement & DevOps
- **[DEPLOYMENT_GUIDE_MULTI_ENV.md](DEPLOYMENT_GUIDE_MULTI_ENV.md)** - Guide déploiement multi-environnements
- **[DEVOPS_GUIDE.md](DEVOPS_GUIDE.md)** - Guide DevOps complet (Jenkins, ArgoCD, K8s)
- **[MONITORING_SETUP.md](MONITORING_SETUP.md)** - Configuration monitoring (Prometheus, Grafana)
- **[MONITORING_DATABASE_GUIDE.md](MONITORING_DATABASE_GUIDE.md)** - Monitoring bases de données

### Opérations
- **[RUNBOOKS_OPERATIONNELS.md](RUNBOOKS_OPERATIONNELS.md)** - Procédures opérationnelles (incidents, backups)

### Sécurité
- **[SECURITY.md](SECURITY.md)** - Guide sécurité et hardening
- **[PLAN_ACTION_SECURITE.md](PLAN_ACTION_SECURITE.md)** - Plan d'action sécurité

### Développement
- **[BUGS.md](BUGS.md)** - Bugs connus et solutions
- **[CHANGELOG.md](CHANGELOG.md)** - Historique des versions

## 🗂️ Documentation par Composant

### Backend
- [backend-python-bridges/README.md](../backend-python-bridges/README.md) - Bridges Python (LLM, STT, TTS)
- [backend-audio-cpp/README.md](../backend-audio-cpp/README.md) - Moteur audio C++
- [backend-rust-db/README.md](../backend-rust-db/README.md) - Couche base de données
- [backend-rust-mqtt/README.md](../backend-rust-mqtt/README.md) - Client MQTT/Home Assistant

### Frontend
- [frontend/README.md](../frontend/README.md) - Interface React/Next.js
- [frontend/IMPLEMENTATION.md](../frontend/IMPLEMENTATION.md) - Détails implémentation

### Sécurité
- [jarvis-secretsd/README.md](../jarvis-secretsd/README.md) - Daemon de gestion des secrets
- [jarvis-secretsd/DEPLOYMENT_GUIDE.md](../jarvis-secretsd/DEPLOYMENT_GUIDE.md) - Guide déploiement secretsd

### DevOps
- [devops-tools/README.md](../devops-tools/README.md) - Outils DevOps (Jenkins, ArgoCD)
- [devops-tools/DEVOPS-STATUS.md](../devops-tools/DEVOPS-STATUS.md) - État DevOps

## 📦 Tests & Performance
- [tests/load/README.md](../tests/load/README.md) - Tests de charge

## 🗄️ Archives
- [archive/](archive/) - Ancienne documentation (conservée pour historique)

## 🔗 Liens Utiles

- **GitHub**: [Repository](https://github.com/votre-repo/jarvis)
- **Issues**: [Bug Tracker](https://github.com/votre-repo/jarvis/issues)
- **API Swagger**: http://localhost:8100/swagger-ui

## 📊 Statistiques du Projet

- **Version**: v1.9.0
- **Langages**: Rust (core), Python (AI), TypeScript (frontend), C++ (audio), Elixir (cluster), Go (monitoring)
- **Lignes de code**: ~50,000 (hors dépendances)
- **Tests**: 95% coverage
- **Documentation**: 27,000+ lignes

---

**Dernière mise à jour**: 2025-11-30  
**Maintenu par**: Enzo (21 ans, Perpignan)
