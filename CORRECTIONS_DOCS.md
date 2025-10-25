# 📝 CORRECTIONS DOCS - Issues à Fixer

**Liste complète des infos FAUSSES à corriger dans la documentation**

---

## 🔴 ERREURS CRITIQUES À FIXER

### README.md Racine (Erreurs Majeures)

| # | Ligne | Erreur | Fix |
|----|-------|--------|-----|
| 1 | 6 | Badge FastAPI mais backend est Rust | Remplacer par badge Rust |
| 2 | 5 | "v1.3 Production Hardening" mais c'est Phases 4-9 | Mettre à jour titre |
| 3 | 55 | URL git username/Projet-Jarvis | Mettre legeeknumero1/Projet-Jarvis |
| 4 | 60-67 | Production compose files inexistants | Supprimer ou documenter réellement |
| 5 | 71 | Port 8000 (FastAPI) n'existe plus | Utiliser port 8100 (Rust) |
| 6 | 72 | Métriques sur port 8000 | Port 8100 ou N/A selon phase |
| 7 | 80 | Architecture avec Port 8000 | Actualiser architecture |
| 8 | 113-124 | Backend Python dev au lieu de Rust | Utiliser backend-rust |
| 9 | 126-166 | Architecture v1.3 obsolète | Remplacer par Phases 4-9 |

### docs/README.md (Très Obsolète)

| # | Ligne | Erreur | Fix |
|----|-------|--------|-----|
| 1 | 1 | "v1.3.0 Production Hardening" | Dire "v1.9.0 - Architecture Polyglotte Phases 4-9" |
| 2 | 19-33 | Architecture v1.2.0 vs v2.0 obsolète | Remplacer par structure Phases 4-9 réelle |
| 3 | 35-114 | Rust backend mentionné mais ports faux | Port 8100 partout, pas 8000 |
| 4 | 156-168 | Ports Docker faux | Vérifier ports réels |
| 5 | 164 | Port 8000 pour FastAPI | Port 8100 pour Rust |
| 6 | 196-235 | Commandes dev Python/FastAPI | Utiliser Rust commands |
| 7 | 238-259 | Services dans docker-compose | Documenter services réels |
| 8 | 261-271 | Endpoints API incorrects | Mettre à jour endpoints réels |
| 9 | 313-375 | Roadmap phases confuse | Clarifier Phases 1-9 réelles |

### backend-rust/README.md (Infos Fausses)

| # | Ligne | Erreur | Fix |
|----|-------|--------|-----|
| 1 | 177 | PORT=8000 | Changer à PORT=8100 |
| 2 | 29-46 | Structure dossiers inexistante | Les handlers/ et services/ n'existent pas |
| 3 | 64-81 | Endpoints /api/chat et /ws | Vérifier si réellement implémentés |
| 4 | 110-111 | Migrations SQL | Aucune migration trouvée |
| 5 | 190-195 | Services externes (STT/TTS/Qdrant) | Clarifier qu'ils sont en Phase 3+ |

### frontend-phase7/README.md (À Vérifier)

| # | Issue | Fix |
|----|-------|-----|
| 1 | .env.example existe mais pas utilisé | Documenter configuration réelle |
| 2 | Ports statiques | Vérifier avec env variables |
| 3 | API URLs pointent sur 8100 | Vérifier correct |

### backend-lua-plugins/README.md et backend-rust-mqtt/README.md

| # | Issue | Fix |
|----|-------|-----|
| 1 | Exemples de code Lua corrects ? | Vérifier que APIs existent |
| 2 | Imports dans Cargo.toml corrects ? | Vérifier dépendances |

### clustering-elixir/README.md (À Vérifier)

| # | Issue | Fix |
|----|-------|-----|
| 1 | Services réellement implémentés ? | Vérifier code existe |

---

## 📋 INFOS À METTRE À JOUR

### Ports Corrects (À Documenter)

```
Port 8100 : Rust Backend (Phase 1, 4-6)
Port 3000 : Frontend React (Phase 7)
Port 8004 : C++ Audio Engine (Phase 2)
Port 8005 : Python Bridges IA (Phase 3)
Port 8006 : Go Monitor (Phase 6)
Port 8007 : Elixir HA Health (Phase 9)
Port 5432 : PostgreSQL
Port 6379 : Redis
Port 11434: Ollama
```

### Architecture Réelle à Documenter

```
Phase 1: Rust Backend Core (Port 8100)
Phase 2: C++ Audio Engine (Port 8004)
Phase 3: Python Bridges (Port 8005)
Phase 4: Rust DB Layer (Interne)
Phase 5: MQTT Automations (Interne)
Phase 6: Go Monitoring (Port 8006)
Phase 7: Frontend TypeScript (Port 3000)
Phase 8: Lua Plugins (Interne)
Phase 9: Elixir HA (Port 8007)
```

### Services Réellement Implémentés vs Documentés

| Service | Documenté | Réel | Status |
|---------|-----------|------|--------|
| Rust Backend Core | ✅ | ⚠️ Partiel | Port 8100 OK |
| C++ Audio | ✅ | ✅ | Port 8004 |
| Python Bridges | ✅ | ⚠️ Partiel | Port 8005 |
| Rust DB | ✅ | ✅ | Interne |
| MQTT | ✅ | ✅ | Interne |
| Go Monitor | ✅ | ✅ | Port 8006 |
| Frontend | ✅ | ✅ | Port 3000 |
| Lua Plugins | ✅ | ✅ | Interne |
| Elixir HA | ✅ | ⚠️ Partiel | Port 8007 |

---

## 🔧 PLAN DE CORRECTIONS

### PRIORITÉ 1 (URGENT - Docs Racine)

1. ✅ Corriger README.md racine (badges, ports, architecture)
2. ✅ Corriger docs/README.md (architecture globale)
3. ✅ Créer nouvelle section "Phases 4-9" dans README

### PRIORITÉ 2 (HAUTE - Chaque Phase)

4. ✅ Corriger backend-rust/README.md (port 8100, structures vraies)
5. ✅ Corriger frontend-phase7/README.md (config réelle)
6. ✅ Corriger backend-lua-plugins/README.md (APIs vraies)
7. ✅ Corriger backend-rust-mqtt/README.md (endpoints vrais)
8. ✅ Corriger clustering-elixir/README.md (services vrais)

### PRIORITÉ 3 (DOCUMENTATION)

9. ✅ Créer ARCHITECTURE.md avec structure complète Phases 4-9
10. ✅ Créer DEPLOYMENT.md avec ports et configuration
11. ✅ Mettre à jour CHANGELOG.md avec Phases 4-9

---

## ✅ CORRECTIONS À FAIRE IMMÉDIATEMENT

**Ne pas laisser ces infos fausses:**
- ❌ Port 8000 (FastAPI) → ✅ Port 8100 (Rust)
- ❌ "v1.3.0 Production" → ✅ "v1.9.0 Architecture Polyglotte"
- ❌ Architecture FastAPI/Python → ✅ Phases 1-9 réelles
- ❌ Services inexistants documentés → ✅ Supprimer ou implémenter
- ❌ Endpoints non-implémentés → ✅ Vérifier et corriger

---

## 🎯 RÉSULTAT FINAL

Après corrections:
- ✅ Tous les ports corrects
- ✅ Architecture à jour (Phases 1-9)
- ✅ Seulement les services réellement implémentés
- ✅ Documentation cohérente et précise
- ✅ Pas d'infos obsolètes ou fausses

---

**Status: À CORRIGER IMMÉDIATEMENT**
