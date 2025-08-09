# 🧪 Tests de Validation - Observabilité v1.3

## ✅ Checklist Rapide

### 1. Configuration Logs JSON
```bash
# Validation syntaxe JSON
jq . prod/logs-config.json >/dev/null
echo "✅ Config logs valide"

# Test avec backend
JARVIS_LOG_CONFIG=prod/logs-config.json uvicorn backend.app:app
```

### 2. Test Request-ID Correlation
```bash
# Requête avec ID custom
curl -H "X-Request-ID: test-123" http://localhost:8000/health

# Vérifier logs console
# Doit afficher: ... | req=test-123

# Vérifier response header  
curl -I http://localhost:8000/health
# Doit contenir: x-request-id: abc123def
```

### 3. Test Logs JSON Structurés
```bash
# Démarrer avec config JSON
mkdir -p /tmp/test-logs
sed 's|/var/log/jarvis|/tmp/test-logs|' prod/logs-config.json > /tmp/config-test.json
JARVIS_LOG_CONFIG=/tmp/config-test.json uvicorn backend.app:app

# Faire requêtes
curl http://localhost:8000/health
curl -X POST -H "Content-Type: application/json" -d '{"message":"test","user_id":"enzo"}' http://localhost:8000/chat

# Vérifier logs JSON
tail -f /tmp/test-logs/app.jsonl | jq
```

### 4. Test WebSocket Correlation
```bash
# Connexion WebSocket
websocat ws://localhost:8000/ws

# Envoyer message
{"message": "ping", "user_id": "test"}

# Observer logs console
# Chaque message WS doit avoir même request_id
```

## 🔍 Tests Détaillés

### Test 1: Middleware HTTP

**Objectif**: Vérifier injection request-id automatique

```python
import requests

# Sans request-id
resp = requests.get("http://localhost:8000/health")
print(f"Generated ID: {resp.headers.get('x-request-id')}")

# Avec request-id custom
resp = requests.get(
    "http://localhost:8000/health", 
    headers={"X-Request-ID": "custom-test-001"}
)
print(f"Custom ID: {resp.headers.get('x-request-id')}")
# Doit être: custom-test-001
```

### Test 2: Format Logs JSON

**Exemple attendu**:
```json
{
  "ts": "2025-01-17T15:30:45Z",
  "lvl": "INFO",
  "logger": "backend.http",
  "msg": "request served",
  "request_id": "abc123def456",
  "path": "/health",
  "method": "GET",
  "status_code": 200,
  "latency_ms": 1.23,
  "client_ip": "127.0.0.1",
  "component": "api"
}
```

**Validation**:
```bash
# Tous les logs doivent avoir ces champs
cat /var/log/jarvis/app.jsonl | jq -r '.request_id' | head -5
# Ne doit pas contenir "-" ou null

# Latence > 0
cat /var/log/jarvis/app.jsonl | jq -r 'select(.latency_ms > 0) | .latency_ms' | head -5
```

### Test 3: WebSocket Correlation

**Script test**:
```python
import asyncio
import websockets
import json

async def test_ws_correlation():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        # Envoyer 3 messages
        for i in range(3):
            msg = {"message": f"test {i}", "user_id": "test"}
            await websocket.send(json.dumps(msg))
            resp = await websocket.recv()
            print(f"Response {i}: {resp}")

# Observer logs - même request_id pour toute la connexion
asyncio.run(test_ws_correlation())
```

### Test 4: Error Handling

**Test exception handling**:
```bash
# Message invalide (trigger exception)
curl -X POST -H "Content-Type: application/json" \
  -d '{"message": "x" * 5000}' \  # Message trop long
  http://localhost:8000/chat

# Vérifier log d'erreur avec request_id
# JSON doit contenir: "lvl": "ERROR", "request_id": "...", "exc": "..."
```

### Test 5: Contextvars Isolation

**Test concurrence**:
```python
import asyncio
import httpx

async def concurrent_requests():
    async with httpx.AsyncClient() as client:
        # Lancer 10 requêtes parallèles avec IDs différents
        tasks = []
        for i in range(10):
            task = client.get(
                "http://localhost:8000/health",
                headers={"X-Request-ID": f"concurrent-{i:03d}"}
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        
        # Vérifier que chaque réponse a gardé son ID
        for i, resp in enumerate(responses):
            expected_id = f"concurrent-{i:03d}"
            actual_id = resp.headers.get("x-request-id")
            assert actual_id == expected_id, f"ID mismatch: {actual_id} != {expected_id}"
        
        print("✅ Isolation contextvars OK")

asyncio.run(concurrent_requests())
```

## 🚀 Tests Automatisés

### Script global
```bash
# Lancer tous les tests
chmod +x prod/test-logs.sh
./prod/test-logs.sh
```

### CI/CD Integration

**GitHub Actions**:
```yaml
- name: Test observability
  run: |
    # Config logs temporaire
    export JARVIS_LOG_CONFIG=/tmp/logs-test.json
    cp prod/logs-config.json $JARVIS_LOG_CONFIG
    sed -i 's|/var/log/jarvis|/tmp|g' $JARVIS_LOG_CONFIG
    
    # Test démarrage
    uvicorn backend.app:app --host 127.0.0.1 --port 8001 &
    sleep 3
    
    # Tests API
    curl -f http://127.0.0.1:8001/health
    curl -f http://127.0.0.1:8001/metrics
    
    # Vérifier logs JSON
    test -f /tmp/app.jsonl
    jq empty /tmp/app.jsonl  # Validate JSON
    grep -q '"request_id"' /tmp/app.jsonl
```

## 📊 Métriques de Validation

### KPIs attendus
- **Logs JSON**: 100% des requêtes HTTP loggées
- **Request-ID**: 100% des logs avec correlation 
- **Latence logging**: < 1ms overhead
- **WebSocket**: Correlation maintenue sur toute la session
- **Error rate**: < 0.1% d'erreurs de logging

### Monitoring continu
```bash
# Logs sans request_id (ne devrait jamais arriver)
grep -v '"request_id"' /var/log/jarvis/app.jsonl | wc -l
# Doit être: 0

# Logs malformés JSON
while read line; do echo "$line" | jq empty >/dev/null 2>&1 || echo "BAD: $line"; done < /var/log/jarvis/app.jsonl
```

---

## 🎯 Validation OK si:

✅ **Tous les logs JSON sont valides**  
✅ **100% des requêtes ont request-id**  
✅ **WebSocket garde correlation**  
✅ **Pas d'erreurs de contextvars**  
✅ **Performance acceptable (< 1ms overhead)**  

---

L'observabilité v1.3 est prête pour production ! 🚀