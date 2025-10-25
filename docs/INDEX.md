# 🤖 JARVIS - Documentation Complète

## 📚 Structure Documentation

### 🚀 **Démarrage Rapide**
- **[README.md](README.md)** - Vue d'ensemble du projet

### 🏗️ **Architecture & Design**
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Architecture polyglotte 9 phases
- **[ROADMAP_POLYGLOTTE.md](ROADMAP_POLYGLOTTE.md)** - Roadmap détaillée des phases

### 🔧 **Déploiement & Opérations**
- **[DEPLOYMENT_GUIDE_MULTI_ENV.md](DEPLOYMENT_GUIDE_MULTI_ENV.md)** - Guide déploiement multi-environnements
- **[DEVOPS_GUIDE.md](DEVOPS_GUIDE.md)** - Guide DevOps complet
- **[RUNBOOKS_OPERATIONNELS.md](RUNBOOKS_OPERATIONNELS.md)** - Runbooks pour opérations
- **[MONITORING_DATABASE_GUIDE.md](MONITORING_DATABASE_GUIDE.md)** - Guide monitoring

### 🔐 **Sécurité**
- **[SECURITY.md](SECURITY.md)** - Politique de sécurité
- **[PLAN_ACTION_SECURITE.md](PLAN_ACTION_SECURITE.md)** - Plan d'action sécurité

### 📡 **API & Intégrations**
- **[API.md](API.md)** - Documentation API complète

### 🐛 **Maintenance**
- **[BUGS.md](BUGS.md)** - Bugs connus et résolutions
- **[CHANGELOG.md](CHANGELOG.md)** - Historique des changements

### 👥 **Collaboration**
- **[PROFIL_JARVIS.md](PROFIL_JARVIS.md)** - Profil/contexte du projet
- **[CLAUDE.md](CLAUDE.md)** - Instructions Claude Code
- **[CLAUDE_PARAMS.md](CLAUDE_PARAMS.md)** - Paramètres Claude Code

---

## 📊 État du Projet

**Phase actuelle:** Phase 6 - Go Monitoring (COMPLÈTE)
**Phases implémentées:** 1-6
**Phases en cours:** 7 (Frontend React)
**Phases pendantes:** 8 (Lua), 9 (Elixir)

---

## 🔗 Répertoires du Projet

```
Projet-Jarvis/
├── core/                         # Phase 1: Rust Backend (Axum)
├── backend-audio-cpp/            # Phase 2: C++ Audio Engine
├── backend-python-bridges/       # Phase 3: Python Bridges
├── backend-rust-db/              # Phase 4: Rust DB Layer
├── backend-rust-mqtt/            # Phase 5: MQTT Automations
├── monitoring-go/                # Phase 6: Go Monitoring
├── frontend/                     # Phase 7: React Frontend
├── backend-lua-plugins/          # Phase 8: Lua Plugins
├── clustering-elixir/            # Phase 9: Elixir Clustering
│
├── docs/                         # Documentation (CE FICHIER)
├── config/                       # Configuration files
├── scripts/                      # Utilitaires et scripts
├── tests/                        # Tests intégrés
├── docker-compose.yml            # Orchestration conteneurs
└── certs/                        # Certificats TLS
```

---

## ⚡ Commandes Essentielles

### Démarrage
```bash
docker-compose up -d
```

### Vérification
```bash
curl http://localhost:8100/health      # Backend Core
curl http://localhost:3000             # Frontend
curl http://localhost:9090/metrics     # Monitoring
```

### Arrêt
```bash
docker-compose down
```

---

## 📝 Notes

- Toute la documentation est à jour (nettoyée le 2025-10-25)
- Les fichiers obsolètes ont été supprimés
- Structure simplifiée pour meilleure navigation
- Voir [CHANGELOG.md](CHANGELOG.md) pour l'historique récent

