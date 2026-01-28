#  Jarvis Go Monitoring - Phase 6

**Watchdog et monitoring pour l'infrastructure Jarvis avec Prometheus**

Agent léger en Go pour supervision des services, health checks et redémarrages automatiques.

---

##  Architecture

### Stack Technique

- **Go 1.21** : Binaires statiques, gestion concurrence légère
- **Docker API** : Gestion containers pour watchdog
- **Prometheus** : Exposition des métriques
- **Health Checks** : API REST pour probes

---

##  Prometheus Metrics

### Container Monitoring
```
jarvis_container_health{container="..."}       # 1=healthy, 0=unhealthy
jarvis_container_restarts_total{container="..."} # Total restarts
```

### Service Monitoring
```
jarvis_service_uptime_seconds{service="..."}   # Uptime en secondes
```

### API Metrics
```
jarvis_api_latency_ms{endpoint="..."}          # Latence requêtes (histogram)
jarvis_requests_total{method,endpoint,status}  # Compteur requêtes
```

### System Metrics
```
jarvis_system_memory_bytes{type="..."}         # Mémoire utilisée
jarvis_system_cpu_percent{cpu="..."}           # CPU usage
```

---

##  Watchdog Features

### Health Checks
Vérifie régulièrement la santé de :
-  Rust Backend (8100)
-  Audio Engine (8004)
-  Python Bridges (8005)
-  Ollama (11434)
-  PostgreSQL (5432)
-  Redis (6379)

### Auto-Restart
Redémarre automatiquement les services down :
```
Interval: 30 secondes
Services: Rust, Python, Audio
```

### Metrics Export
Exposes métriques Prometheus sur :
```
HTTP://localhost:8006/metrics
```

---

##  Endpoints

### Health Check
```bash
GET /health
# {"status":"healthy","services":{"...":"healthy"}}

HTTP 200 - All services healthy
HTTP 503 - Some services degraded
```

### Prometheus Metrics
```bash
GET /metrics
# Prometheus format
```

---

##  Docker Integration

Services monitored:
```
jarvis_rust_backend
jarvis_audio_engine
jarvis_python_bridges
jarvis_ollama
postgres (jarvis_postgres)
redis (jarvis_redis)
```

---

##  Monitoring Dashboard

Recommandations Prometheus :

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'jarvis'
    static_configs:
      - targets: ['localhost:8006']
```

### Alertes Recommandées

```yaml
- alert: JarvisServiceDown
  expr: jarvis_container_health == 0
  for: 2m

- alert: HighRestartRate
  expr: rate(jarvis_container_restarts_total[5m]) > 0.1

- alert: HighAPILatency
  expr: histogram_quantile(0.95, jarvis_api_latency_ms) > 1000
```

---

##  Utilisation

### Installation
```bash
cd monitoring-go
go build -o jarvis-monitoring main.go
```

### Démarrage
```bash
./jarvis-monitoring
#  Jarvis Monitoring v1.6.0
#  Prometheus metrics on :8006/metrics
#  Health check on :8006/health
```

### Comme service Docker
```yaml
jarvis-monitoring:
  image: golang:1.21
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock
  ports:
    - "8006:8006"
  networks:
    - jarvis_network
```

---

##  Performance

```
Health check: ~50ms par service
Metrics export: <10ms
Memory usage: ~20MB
CPU: <1% idle
```

---

##  Sécurité

-  Docker socket access (local only)
-  No root required
-  Prometheus auth (via reverse proxy)
-  Service isolation

---

##  Intégration Architecture

**Phase 6 dans l'architecture :**
-  Phase 1-5: Core + Audio + Python + DB + MQTT
-  Phase 6: **Go Monitoring** (YOU ARE HERE)
-  Phase 7+: Frontend + Plugins

**Phase 6 apporte :**
-  Supervision centralisée de tous les services
-  Auto-redémarrage en cas de crash
-  Métriques Prometheus pour dashboards
-  Alertes sur anomalies

---

##  Fichiers

```
monitoring-go/
 main.go        # Watchdog + HTTP server
 go.mod         # Go dependencies
 go.sum         # Dependency lock
 README.md      # Cette doc
```

---

** Jarvis Monitoring - Lightweight supervision with Prometheus**

*Architecture Polyglotte Phase 6 pour Jarvis AI Assistant*
