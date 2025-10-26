# Jarvis - Complete Documentation

## Documentation Structure

### Quick Start
- [README.md](README.md) - Project overview

### Architecture & Design
- [ARCHITECTURE.md](ARCHITECTURE.md) - Polyglot architecture 9 phases
- [ROADMAP_POLYGLOTTE.md](ROADMAP_POLYGLOTTE.md) - Detailed phases roadmap

### Deployment & Operations
- [DEPLOYMENT_GUIDE_MULTI_ENV.md](DEPLOYMENT_GUIDE_MULTI_ENV.md) - Multi-environment deployment guide
- [DEVOPS_GUIDE.md](DEVOPS_GUIDE.md) - Complete DevOps guide
- [RUNBOOKS_OPERATIONNELS.md](RUNBOOKS_OPERATIONNELS.md) - Operational runbooks
- [MONITORING_DATABASE_GUIDE.md](MONITORING_DATABASE_GUIDE.md) - Monitoring guide

### Security
- [SECURITY.md](SECURITY.md) - Security policy
- [PLAN_ACTION_SECURITE.md](PLAN_ACTION_SECURITE.md) - Security action plan

### API & Integrations
- [API.md](API.md) - Complete API documentation

### Maintenance
- [BUGS.md](BUGS.md) - Known issues and resolutions
- [CHANGELOG.md](CHANGELOG.md) - Change history

### Development
- [PROFIL_JARVIS.md](PROFIL_JARVIS.md) - Project profile/context
- [DEVELOPMENT_GUIDELINES.md](DEVELOPMENT_GUIDELINES.md) - Development guidelines
- [DEVELOPMENT_PARAMETERS.md](DEVELOPMENT_PARAMETERS.md) - Development parameters

---

## Project Status

Current Phase: Phase 7 - Frontend React
Implemented Phases: 1-5, 7
In Progress Phases: 6 (Go Monitoring - not deployed)
Pending Phases: 8 (Lua), 9 (Elixir)

---

## Project Directories

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
├── docs/                         # Documentation
├── config/                       # Configuration files
├── scripts/                      # Utilities and scripts
├── tests/                        # Integrated tests
├── docker-compose.yml            # Container orchestration
└── certs/                        # TLS certificates
```

---

## Essential Commands

### Startup
```bash
docker-compose up -d
```

### Health Check
```bash
curl http://localhost:8100/health      # Backend Core
curl http://localhost:3000             # Frontend
curl http://localhost:9090/metrics     # Monitoring
```

### Shutdown
```bash
docker-compose down
```

---

## Notes

- All documentation updated 2025-10-25
- Obsolete files have been removed
- Simplified structure for better navigation
- See [CHANGELOG.md](CHANGELOG.md) for recent history
