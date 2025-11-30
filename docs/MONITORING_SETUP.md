# Monitoring Setup - Prometheus + Grafana

## Quick Start

### Démarrer le stack de monitoring:

```bash
docker-compose -f docker-compose.monitoring.yml up -d
```

### Accès aux services:

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001
  - User: `admin`
  - Password: `jarvis2025`

## Services Monitorés

| Service | Endpoint | Métriques |
|---------|----------|-----------|
| Jarvis Core (Rust) | 172.20.0.40:8100/metrics | CPU, RAM, Requests, Latency |
| PostgreSQL | 172.20.0.203:9187 | Connections, Queries, DB size |
| Redis | 172.20.0.202:9121 | Keys, Memory, Hit rate |
| System (Node) | 172.20.0.204:9100 | CPU, RAM, Disk, Network |

## Métriques Principales

### Backend (Rust)

- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request latency
- `active_connections` - Active WebSocket connections
- `cache_hits_total` - Cache hit rate
- `db_query_duration_seconds` - Database query time

### PostgreSQL

- `pg_stat_database_numbackends` - Active connections
- `pg_stat_database_tup_inserted` - Inserts per second
- `pg_stat_database_tup_fetched` - Selects per second
- `pg_database_size_bytes` - Database size

### Redis

- `redis_connected_clients` - Connected clients
- `redis_memory_used_bytes` - Memory usage
- `redis_keyspace_hits_total` - Cache hits
- `redis_keyspace_misses_total` - Cache misses

## Dashboards Recommandés

### Dashboard 1: Overview
- Request rate (RPS)
- Latency (P50, P95, P99)
- Error rate
- System resources (CPU, RAM)

### Dashboard 2: Database
- Connection pool status
- Query performance
- Table sizes
- Slow queries

### Dashboard 3: Cache
- Hit/Miss ratio
- Memory usage
- Evictions
- Keys count

## Alertes

### Critiques
- Backend down > 1 min
- Database connections > 90%
- Disk space < 10%
- Memory usage > 90%

### Warnings
- Request latency P95 > 500ms
- Cache hit rate < 80%
- Error rate > 1%

## Maintenance

### Rétention des données:
- Prometheus: 30 jours
- Grafana: Illimitée

### Backup:
```bash
# Backup Grafana dashboards
docker exec jarvis_grafana grafana-cli admin export-dashboard

# Backup Prometheus data
docker run --rm -v prometheus_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/prometheus-backup.tar.gz /data
```

## Troubleshooting

### Prometheus ne scrappe pas:
1. Vérifier que le service cible expose `/metrics`
2. Vérifier les targets dans Prometheus UI
3. Vérifier la connectivité réseau

### Grafana ne se connecte pas:
1. Vérifier le datasource Prometheus
2. Test connection dans Settings > Datasources
3. Vérifier les logs: `docker logs jarvis_grafana`
