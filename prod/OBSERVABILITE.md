#  Observabilité Jarvis v1.3 - Production

##  Stack d'Observabilité Complète

###  Métriques Prometheus
**Endpoint**: `/metrics` (activé automatiquement)

**Métriques WebSocket**:
- `ws_active_connections` - Connexions actives (gauge)
- `ws_connections_total{status}` - Total créées (counter)  
- `ws_messages_total{direction,status}` - Messages (counter)

**Métriques Chat/LLM**:
- `chat_requests_total{secure,status}` - Requêtes chat (counter)
- `chat_errors_total{stage}` - Erreurs par étape (counter)
- `llm_generate_seconds` - Latence LLM (histogram)
- `memory_operations_total{operation,status}` - Opérations mémoire (counter)

**Métriques Services**:
- `service_health_status{service}` - Santé services (gauge)
- `service_response_seconds{service}` - Temps réponse (histogram)

**Métriques Sécurité**:
- `rate_limit_hits_total{endpoint,client_type}` - Rate limiting (counter)

###  Logs JSON Structurés

**Format automatique avec Request-ID**:
```json
{
  "timestamp": 1705123456.789,
  "level": "INFO", 
  "logger": "backend.routers.chat",
  "message": "Message content",
  "request_id": "123e4567-e89b-12d3-a456-426614174000",
  "module": "chat",
  "function": "chat",
  "line": 45,
  "user_id": "enzo",
  "action": "chat_request",
  "message_length": 127
}
```

**Logs d'accès avec correlation**:
- Chaque requête HTTP a un `X-Request-ID` unique
- Tous les logs de la requête portent le même ID
- Tracing complet de bout en bout

###  Request Tracing

**Headers automatiques**:
- `X-Request-ID: uuid4` sur toutes les réponses
- Correlation dans tous les logs de la chaîne
- Support WebSocket avec même principe

**Contexte enrichi**:
```python
# Usage dans le code
from backend.middleware import get_request_id, create_log_context

log_ctx = create_log_context(
    request,
    user_id="enzo",
    action="chat_success",
    response_length=256
)
logger.info(json.dumps(log_ctx))
```

##  Configuration Production

### Docker Compose - Logs externes
```yaml
services:
  jarvis-api:
    volumes:
      - ./logs:/app/logs
    environment:
      - LOG_FILE=/app/logs/jarvis.jsonl
      - LOG_LEVEL=INFO
```

### ELK Stack Integration
**Logstash pipeline** pour parsing JSON :
```ruby
input {
  file {
    path => "/app/logs/jarvis.jsonl"
    codec => "json"
  }
}
filter {
  if [request_id] {
    mutate { add_tag => ["traced"] }
  }
}
output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "jarvis-logs-%{+YYYY.MM.dd}"
  }
}
```

### Grafana Dashboards

**Dashboard WebSocket**:
- Connexions actives en temps réel
- Taux de succès connexions
- Latence messages

**Dashboard Chat/LLM**:
- Requêtes par minute
- Temps de réponse P95/P99 
- Taux d'erreur par étape

**Dashboard Services**:
- Status de santé (Ollama, Memory, etc.)
- Temps réponse services externes
- Rate limiting hits

##  Monitoring Playbook

###  Alertes recommandées

**Critiques**:
- `ws_active_connections > 1000` (surcharge)
- `service_health_status{service="ollama"} == 0` (LLM down)
- `rate_limit_hits_total rate > 100/min` (attaque potentielle)

**Warnings**:
- `llm_generate_seconds P95 > 10s` (LLM lent)
- `chat_errors_total rate > 5/min` (erreurs fréquentes)

###  Debugging avec Request-ID

**1. Rechercher une session utilisateur**:
```bash
# Tous les logs d'une requête
grep "123e4567-e89b-12d3-a456-426614174000" /app/logs/jarvis.jsonl

# Via ELK
GET jarvis-logs-*/_search
{
  "query": {
    "term": { "request_id": "123e4567-e89b-12d3-a456-426614174000" }
  }
}
```

**2. Tracer une session WebSocket**:
- WebSocket garde le request-id initial
- Tous messages/erreurs portent le même ID
- Tracing de A à Z possible

###  Métriques Business

**KPIs automatiques**:
- Messages traités par heure
- Utilisateurs actifs (WebSocket concurrent)
- Temps réponse moyen LLM
- Taux disponibilité services

**Analytics**:
- Top erreurs par utilisateur
- Patterns d'utilisation temporels
- Performance par fonctionnalité

##  Mise en Production

### 1. Variables d'environnement
```bash
LOG_LEVEL=INFO
LOG_FILE=/app/logs/jarvis.jsonl
PROMETHEUS_METRICS=true
REQUEST_ID_HEADER=X-Request-ID
```

### 2. Volumes Docker
```yaml
volumes:
  - ./logs:/app/logs:rw
  - ./prometheus:/prometheus:ro
```

### 3. Health Checks
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### 4. Log rotation
- Fichiers JSON rotatés à 100MB
- 10 backups conservés
- Compression automatique

---

##  Validation

### Tests observabilité

**1. Request-ID propagation**:
```bash
curl -v http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"test","user_id":"enzo"}'
# Vérifier header X-Request-ID dans réponse
# Chercher l'ID dans les logs JSON
```

**2. Métriques Prometheus**:
```bash
curl http://localhost:8000/metrics | grep -E "(ws_|chat_|llm_)"
```

**3. Logs structurés**:
```bash
tail -f logs/jarvis.jsonl | jq .
```

L'observabilité complète est opérationnelle ! 