# Jarvis - Polyglot AI Assistant v1.9.0

> Intelligent voice assistant, 9-phase distributed architecture, production-ready.

## Quick Start

```bash
# Clone and start
git clone <repo>
cd Projet-Jarvis
docker-compose up -d

# Access
Frontend:    http://localhost:3000
API Core:    http://localhost:8100
Health:      http://localhost:8100/health
Monitoring:  http://localhost:9090/metrics
```

## 9-Phase Architecture

| Phase | Tech | Port | Status |
|-------|------|------|--------|
| 1 | Rust (Axum) | 8100 | Complete |
| 2 | C++ (DSP) | 8004 | Complete |
| 3 | Python (IA) | 8005 | Complete |
| 4 | Rust (DB) | - | Complete |
| 5 | Rust (MQTT) | - | Complete |
| 6 | Go (Monitor) | 9090 | Complete |
| 7 | React (UI) | 3000 | In Progress |
| 8 | Lua (Plugins) | - | Pending |
| 9 | Elixir (HA) | 8007 | Pending |

## Documentation

See [INDEX.md](INDEX.md) for complete navigation

**Essential Documents:**
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical design
- [API.md](API.md) - API Documentation
- [SECURITY.md](SECURITY.md) - Security policy
- [DEPLOYMENT_GUIDE_MULTI_ENV.md](DEPLOYMENT_GUIDE_MULTI_ENV.md) - Deployment
- [CHANGELOG.md](CHANGELOG.md) - Version history

## Configuration

```bash
# Required environment variables
JWT_SECRET=<secret-key>
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
```

See `config/` for examples.

## Bugs & Support

- [BUGS.md](BUGS.md) - Known issues
- [PROFIL_JARVIS.md](PROFIL_JARVIS.md) - Project context

## License

MIT

---

**Documentation updated 2025-10-25**
