# 🤖 Instructions Claude Code - Jarvis v1.9.0

> **Pour tous les assistants IA (Claude, GPT, etc.) travaillant sur le projet Jarvis**

---

## 📍 Point d'Entrée Principal

**👉 Commencez TOUJOURS par lire:** [INDEX.md](INDEX.md)

---

## 📋 Ordre de Lecture Recommandé

Pour bien comprendre le projet, lisez dans cet ordre:

1. **[INDEX.md](INDEX.md)** ← COMMENCER ICI
2. **[README.md](README.md)** - Vue d'ensemble rapide
3. **[CLAUDE_PARAMS.md](CLAUDE_PARAMS.md)** - Règles absolues
4. **[ARCHITECTURE.md](ARCHITECTURE.md)** - Architecture complète
5. **[ROADMAP_POLYGLOTTE.md](ROADMAP_POLYGLOTTE.md)** - Phases 1-9
6. **[API.md](API.md)** - Documentation API
7. **[SECURITY.md](SECURITY.md)** - Politique sécurité
8. **[BUGS.md](BUGS.md)** - Problèmes connus
9. **[CHANGELOG.md](CHANGELOG.md)** - Historique

**Autres documents:**
- [DEPLOYMENT_GUIDE_MULTI_ENV.md](DEPLOYMENT_GUIDE_MULTI_ENV.md) - Déploiement
- [DEVOPS_GUIDE.md](DEVOPS_GUIDE.md) - DevOps
- [MONITORING_DATABASE_GUIDE.md](MONITORING_DATABASE_GUIDE.md) - Monitoring
- [RUNBOOKS_OPERATIONNELS.md](RUNBOOKS_OPERATIONNELS.md) - Opérations
- [PLAN_ACTION_SECURITE.md](PLAN_ACTION_SECURITE.md) - Sécurité
- [PROFIL_JARVIS.md](PROFIL_JARVIS.md) - Contexte du projet

---

## ⚙️ Architecture Actuelle (Phase 6)

**Phases Complètement Implémentées (1-6):**
- ✅ Phase 1: Rust Backend Core (Axum + Tokio) - Port 8100
- ✅ Phase 2: C++ Audio Engine (DSP temps réel) - Port 8004
- ✅ Phase 3: Python Bridges (Whisper, Piper, Ollama) - Port 8005
- ✅ Phase 4: Rust DB Layer (PostgreSQL, Tantivy, Redis)
- ✅ Phase 5: MQTT Automations (rumqttc, Home Assistant)
- ✅ Phase 6: Go Monitoring (Prometheus, HTTP Watchdog) - Port 9090

**Phases en Développement (7-9):**
- 🟡 Phase 7: React Frontend (Next.js 14, TypeScript) - Port 3000
- ⏳ Phase 8: Lua Plugins (mlua sandbox, hot-reload)
- ⏳ Phase 9: Elixir Clustering (OTP, Raft HA) - Port 8007

---

## 🔧 Technologies par Phase

| Phase | Langage | Framework | Statut |
|-------|---------|-----------|--------|
| 1 | Rust | Axum + Tokio | ✅ Complete |
| 2 | C++ | FFmpeg + PortAudio | ✅ Complete |
| 3 | Python | FastAPI | ✅ Complete |
| 4 | Rust | sqlx + Tantivy + Redis | ✅ Complete |
| 5 | Rust | rumqttc | ✅ Complete |
| 6 | Go | Prometheus + HTTP | ✅ Complete |
| 7 | TypeScript/React | Next.js 14 + Zustand | 🟡 In Progress |
| 8 | Lua | mlua + Sandbox | ⏳ Pending |
| 9 | Elixir | OTP + Raft | ⏳ Pending |

---

## 📁 Structure du Projet

```
Projet-Jarvis/
├── core/                      # Phase 1: Rust Backend
├── backend-audio-cpp/         # Phase 2: C++ Audio
├── backend-python-bridges/    # Phase 3: Python IA
├── backend-rust-db/           # Phase 4: DB Layer
├── backend-rust-mqtt/         # Phase 5: MQTT
├── monitoring-go/             # Phase 6: Go Monitoring
├── frontend/                  # Phase 7: React Frontend
├── backend-lua-plugins/       # Phase 8: Lua Plugins
├── clustering-elixir/         # Phase 9: Elixir HA
│
├── docs/                      # Documentation (16 fichiers .md)
├── config/                    # Configuration files
├── scripts/                   # Utilitaires
├── tests/                     # Tests
├── docker-compose.yml         # Orchestration
└── certs/                     # Certificats TLS
```

---

## 🎯 Règles Essentielles à Respecter

**VOIR [CLAUDE_PARAMS.md](CLAUDE_PARAMS.md) POUR DÉTAILS COMPLETS**

### Règles de Code

1. **Type Safety** - Utiliser le type system au maximum
2. **Validation** - Valider TOUTES les entrées (côté client ET serveur)
3. **Erreurs** - Gérer les erreurs explicitement, jamais de panic
4. **Tests** - Écrire des tests pour chaque feature
5. **Documentation** - Commenter le code complexe

### Règles de Sécurité

1. ✅ **JWT authentification** - Obligatoire pour API
2. ✅ **CORS strict** - Whitelist des origins
3. ✅ **Rate limiting** - Protection DoS
4. ✅ **TLS/HTTPS** - Chiffrage en transit
5. ✅ **Secrets** - Jamais en code, utiliser .env

### Règles de Performance

1. **Latence < 100ms** - Pour endpoints critiques
2. **Cache** - Utiliser Redis pour données fréquentes
3. **Async** - Pour opérations I/O longues
4. **Profiling** - Vérifier les bottlenecks

---

## 🔗 Commandes Utiles

### Démarrage
```bash
docker-compose up -d
```

### Vérification Santé
```bash
# Backend Core
curl http://localhost:8100/health

# Frontend
curl http://localhost:3000

# Monitoring
curl http://localhost:9090/metrics
```

### Développement
```bash
# Backend Rust
cd core && cargo run

# Frontend
cd frontend && npm run dev

# Avec Docker
docker-compose up
```

### Tests
```bash
cargo test --lib        # Rust tests
npm test               # Frontend tests
python -m pytest       # Python tests
```

---

## 🚨 Problèmes Connus

Voir **[BUGS.md](BUGS.md)** pour liste complète

**Actuels:**
- Phase 7 (Frontend) en cours de build - dépendances TypeScript complexes
- Phase 8-9 pas encore commencées

---

## 📊 Documentation à Jour

✅ **Dernière mise à jour:** 2025-10-25
✅ **Fichiers .md:** 16 (consolidated)
✅ **Taille doc:** 360KB (réduite de 99.4%)
✅ **Cohérence:** Vérifiée

---

## 💡 Pour Commencer

1. **Nouveaux développeurs:** [INDEX.md](INDEX.md) → [README.md](README.md)
2. **Contributeurs:** [CLAUDE_PARAMS.md](CLAUDE_PARAMS.md) → [ARCHITECTURE.md](ARCHITECTURE.md)
3. **DevOps/Production:** [DEPLOYMENT_GUIDE_MULTI_ENV.md](DEPLOYMENT_GUIDE_MULTI_ENV.md)
4. **Support:** [BUGS.md](BUGS.md) → [PROFIL_JARVIS.md](PROFIL_JARVIS.md)

---

**Dernière mise à jour:** 2025-10-25
**Version du projet:** 1.9.0
**Status global:** Phase 6 complète, Phase 7 en cours
