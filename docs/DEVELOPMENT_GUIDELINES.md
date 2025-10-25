# Development Guidelines - Jarvis v1.9.0

> For all developers working on the Jarvis project

---

## Entry Points

**Start by reading:** [INDEX.md](INDEX.md)

---

## Documentation Order

For a complete understanding of the project, read in this order:

1. [INDEX.md](INDEX.md)
2. [README.md](README.md) - Quick overview
3. [ARCHITECTURE.md](ARCHITECTURE.md) - Complete architecture
4. [ROADMAP_POLYGLOTTE.md](ROADMAP_POLYGLOTTE.md) - Phases 1-9
5. [API.md](API.md) - API Documentation
6. [SECURITY.md](SECURITY.md) - Security policy
7. [BUGS.md](BUGS.md) - Known issues
8. [CHANGELOG.md](CHANGELOG.md) - History

Other documents:
- [DEPLOYMENT_GUIDE_MULTI_ENV.md](DEPLOYMENT_GUIDE_MULTI_ENV.md) - Deployment
- [DEVOPS_GUIDE.md](DEVOPS_GUIDE.md) - DevOps
- [MONITORING_DATABASE_GUIDE.md](MONITORING_DATABASE_GUIDE.md) - Monitoring
- [RUNBOOKS_OPERATIONNELS.md](RUNBOOKS_OPERATIONNELS.md) - Operations
- [SECURITY.md](SECURITY.md) - Security policy
- [PLAN_ACTION_SECURITE.md](PLAN_ACTION_SECURITE.md) - Security action plan
- [PROFIL_JARVIS.md](PROFIL_JARVIS.md) - Project context

---

## Current Architecture (Phase 6)

**Fully Implemented (Phases 1-6):**
- Phase 1: Rust Backend Core (Axum + Tokio) - Port 8100
- Phase 2: C++ Audio Engine (DSP real-time) - Port 8004
- Phase 3: Python Bridges (Whisper, Piper, Ollama) - Port 8005
- Phase 4: Rust DB Layer (PostgreSQL, Tantivy, Redis)
- Phase 5: MQTT Automations (rumqttc, Home Assistant)
- Phase 6: Go Monitoring (Prometheus, HTTP Watchdog) - Port 9090

**In Development (Phases 7-9):**
- Phase 7: React Frontend (Next.js 14, TypeScript) - Port 3000
- Phase 8: Lua Plugins (mlua sandbox, hot-reload)
- Phase 9: Elixir Clustering (OTP, Raft HA) - Port 8007

---

## Technology Stack

| Phase | Language | Framework | Status |
|-------|----------|-----------|--------|
| 1 | Rust | Axum + Tokio | Complete |
| 2 | C++ | FFmpeg + PortAudio | Complete |
| 3 | Python | FastAPI | Complete |
| 4 | Rust | sqlx + Tantivy + Redis | Complete |
| 5 | Rust | rumqttc | Complete |
| 6 | Go | Prometheus + HTTP | Complete |
| 7 | TypeScript/React | Next.js 14 + Zustand | In Progress |
| 8 | Lua | mlua + Sandbox | Pending |
| 9 | Elixir | OTP + Raft | Pending |

---

## Essential Rules

### Code Quality
1. Type Safety - Use type system maximum
2. Validation - Validate ALL inputs (client AND server)
3. Error Handling - Handle errors explicitly, never panic
4. Testing - Write tests for each feature
5. Documentation - Comment complex code

### Security
1. JWT Authentication - Required for API
2. Strict CORS - Whitelist origins only
3. Rate Limiting - DoS protection
4. TLS/HTTPS - Encryption in transit
5. Secrets - Never in code, use .env

### Performance
1. Latency < 100ms - For critical endpoints
2. Cache - Use Redis for frequent data
3. Async - For long I/O operations
4. Profiling - Check bottlenecks

---

## Useful Commands

### Startup
docker-compose up -d

### Health Check
curl http://localhost:8100/health      # Backend Core
curl http://localhost:3000             # Frontend
curl http://localhost:9090/metrics     # Monitoring

### Development
cd core && cargo run                # Rust Backend
cd frontend && npm run dev          # Frontend
docker-compose up                   # With Docker

### Testing
cargo test --lib        # Rust tests
npm test               # Frontend tests
python -m pytest       # Python tests

---

## Project Structure

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
├── docs/                      # Documentation
├── config/                    # Configuration files
├── scripts/                   # Utilities
├── tests/                     # Tests
├── docker-compose.yml         # Orchestration
└── certs/                     # TLS certificates

---

Last updated: 2025-10-25
Version: 1.9.0
Status: Phase 6 complete, Phase 7 in progress
