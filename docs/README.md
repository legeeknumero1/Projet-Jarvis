# 🤖 Jarvis - Assistant IA Polyglotte v1.9.0

> Assistant vocal intelligent, architecture distribuée 9 phases, production-ready.

## 🚀 Démarrage Rapide

```bash
# Cloner et démarrer
git clone <repo>
cd Projet-Jarvis
docker-compose up -d

# Accès
Frontend:    http://localhost:3000
API Core:    http://localhost:8100
Health:      http://localhost:8100/health
Monitoring:  http://localhost:9090/metrics
```

## 🏗️ Architecture 9 Phases

| Phase | Tech | Port | Status |
|-------|------|------|--------|
| 1 | Rust (Axum) | 8100 | ✅ Complete |
| 2 | C++ (DSP) | 8004 | ✅ Complete |
| 3 | Python (IA) | 8005 | ✅ Complete |
| 4 | Rust (DB) | - | ✅ Complete |
| 5 | Rust (MQTT) | - | ✅ Complete |
| 6 | Go (Monitor) | 9090 | ✅ Complete |
| 7 | React (UI) | 3000 | 🟡 In Progress |
| 8 | Lua (Plugins) | - | ⏳ Pending |
| 9 | Elixir (HA) | 8007 | ⏳ Pending |

## 📚 Documentation

👉 **[Voir INDEX.md](INDEX.md)** pour la navigation complète

**Documents essentiels:**
- [ARCHITECTURE.md](ARCHITECTURE.md) - Design technique
- [API.md](API.md) - Documentation API
- [SECURITY.md](SECURITY.md) - Politique sécurité
- [DEPLOYMENT_GUIDE_MULTI_ENV.md](DEPLOYMENT_GUIDE_MULTI_ENV.md) - Déploiement
- [CHANGELOG.md](CHANGELOG.md) - Historique versions

## ⚙️ Configuration

```bash
# Variables d'environnement requises
JWT_SECRET=<secret-key>
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
```

Voir `config/` pour exemples.

## 🐛 Bugs & Support

- [BUGS.md](BUGS.md) - Problèmes connus
- [PROFIL_JARVIS.md](PROFIL_JARVIS.md) - Contexte projet

## 📄 Licence

MIT

---

**Documentation nettoyée et consolidée le 2025-10-25**
