# API Examples - Jarvis v1.9.0

Guide complet avec exemples curl pour chaque endpoint de l'API Jarvis.

## Base URL

```
http://localhost:8100
```

## Authentication

La plupart des endpoints nécessitent un token JWT.

### Obtenir un Token

```bash
curl -X POST http://localhost:8100/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "your_password"
  }'
```

**Réponse:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600
}
```

Utiliser le token dans les requêtes:
```bash
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
curl -H "Authorization: Bearer $TOKEN" http://localhost:8100/api/chat
```

---

## Health Check

### GET /health

Vérifier l'état du service.

```bash
curl http://localhost:8100/health
```

**Réponse:**
```json
{
  "status": "healthy",
  "version": "1.9.0",
  "uptime": 3600,
  "checks": {
    "database": "ok",
    "redis": "ok",
    "ollama": "ok"
  }
}
```

---

## Chat API

### POST /api/chat

Envoyer un message au chatbot.

```bash
curl -X POST http://localhost:8100/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Bonjour, comment vas-tu?"
  }'
```

**Réponse:**
```json
{
  "message": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "role": "assistant",
    "content": "Bonjour! Je vais bien, merci. Comment puis-je vous aider?",
    "timestamp": "2025-10-26T15:30:00Z"
  },
  "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
  "latency_ms": 250
}
```

### GET /api/chat/conversations

Lister toutes les conversations.

```bash
curl http://localhost:8100/api/chat/conversations \
  -H "Authorization: Bearer $TOKEN"
```

**Réponse:**
```json
{
  "conversations": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Discussion générale",
      "created_at": "2025-10-26T10:00:00Z",
      "updated_at": "2025-10-26T15:30:00Z",
      "message_count": 5
    }
  ],
  "total": 1
}
```

### GET /api/chat/conversation/{id}

Obtenir une conversation spécifique.

```bash
curl http://localhost:8100/api/chat/conversation/123e4567-e89b-12d3-a456-426614174000 \
  -H "Authorization: Bearer $TOKEN"
```

**Réponse:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Discussion générale",
  "messages": [
    {
      "id": "msg1",
      "role": "user",
      "content": "Bonjour",
      "timestamp": "2025-10-26T10:00:00Z"
    },
    {
      "id": "msg2",
      "role": "assistant",
      "content": "Bonjour! Comment puis-je vous aider?",
      "timestamp": "2025-10-26T10:00:01Z"
    }
  ]
}
```

### POST /api/chat/conversation

Créer une nouvelle conversation.

```bash
curl -X POST http://localhost:8100/api/chat/conversation \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Nouvelle discussion"
  }'
```

**Réponse:**
```json
{
  "id": "456e8400-e29b-41d4-a716-446655440001",
  "title": "Nouvelle discussion",
  "created_at": "2025-10-26T16:00:00Z"
}
```

### DELETE /api/chat/conversation/{id}

Supprimer une conversation.

```bash
curl -X DELETE http://localhost:8100/api/chat/conversation/123e4567-e89b-12d3-a456-426614174000 \
  -H "Authorization: Bearer $TOKEN"
```

**Réponse:**
```json
{
  "success": true,
  "message": "Conversation deleted"
}
```

---

## Memory API (Tantivy Search)

### POST /api/memory/store

Indexer un message dans la mémoire.

```bash
curl -X POST http://localhost:8100/api/memory/store \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
    "user_message": "Comment installer Rust?",
    "bot_response": "Pour installer Rust, utilisez rustup..."
  }'
```

**Réponse:**
```json
{
  "success": true,
  "indexed": true
}
```

### GET /api/memory/search

Rechercher dans la mémoire.

```bash
curl "http://localhost:8100/api/memory/search?q=Rust&limit=5" \
  -H "Authorization: Bearer $TOKEN"
```

**Réponse:**
```json
{
  "results": [
    {
      "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
      "user_message": "Comment installer Rust?",
      "bot_response": "Pour installer Rust, utilisez rustup...",
      "timestamp": "2025-10-26T15:00:00Z",
      "score": 0.95
    }
  ],
  "total": 1,
  "query_time_ms": 45
}
```

---

## Voice API

### POST /api/voice/synthesize

Convertir du texte en audio (TTS).

```bash
curl -X POST http://localhost:8100/api/voice/synthesize \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Bonjour, je suis Jarvis",
    "language": "fr"
  }'
```

**Réponse:**
```json
{
  "audio_data": "base64_encoded_audio...",
  "format": "wav",
  "duration_ms": 1500,
  "sample_rate": 22050
}
```

### POST /api/voice/transcribe

Convertir de l'audio en texte (STT).

```bash
curl -X POST http://localhost:8100/api/voice/transcribe \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "audio_data": "base64_encoded_audio..."
  }'
```

**Réponse:**
```json
{
  "text": "Bonjour, comment vas-tu?",
  "confidence": 0.98,
  "language": "fr",
  "duration_ms": 850
}
```

---

## Metrics

### GET /metrics

Obtenir les métriques Prometheus.

```bash
curl http://localhost:8100/metrics
```

**Réponse (format Prometheus):**
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",endpoint="/health",status="200"} 1234

# HELP http_request_duration_seconds HTTP request latency
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{le="0.005"} 100
http_request_duration_seconds_bucket{le="0.01"} 250
http_request_duration_seconds_sum 12.5
http_request_duration_seconds_count 500
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid input",
  "message": "Field 'content' is required",
  "code": "VALIDATION_ERROR"
}
```

### 401 Unauthorized
```json
{
  "error": "Unauthorized",
  "message": "Invalid or expired token",
  "code": "AUTH_ERROR"
}
```

### 429 Too Many Requests
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests, please slow down",
  "code": "RATE_LIMIT_ERROR",
  "retry_after": 60
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred",
  "code": "INTERNAL_ERROR",
  "request_id": "req_12345"
}
```

---

## Rate Limits

| Endpoint | Limite | Fenêtre |
|----------|--------|---------|
| /api/chat | 60 req | 1 minute |
| /api/voice/* | 30 req | 1 minute |
| /api/memory/search | 100 req | 1 minute |
| /health | Illimité | - |

---

## WebSocket API

### Connection

```javascript
const ws = new WebSocket('ws://localhost:8100/ws');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'auth',
    token: 'your_jwt_token'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Message reçu:', data);
};
```

### Envoyer un message

```javascript
ws.send(JSON.stringify({
  type: 'chat',
  content: 'Bonjour Jarvis'
}));
```

### Réception de message

```json
{
  "type": "chat_response",
  "content": "Bonjour! Comment puis-je vous aider?",
  "timestamp": "2025-10-26T16:00:00Z"
}
```

---

## Testing avec curl

### Script de test complet:

```bash
#!/bin/bash

API_URL="http://localhost:8100"

# 1. Health check
echo "1. Health check..."
curl -s $API_URL/health | jq

# 2. Login
echo -e "\n2. Login..."
TOKEN=$(curl -s -X POST $API_URL/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}' \
  | jq -r '.token')

echo "Token: ${TOKEN:0:50}..."

# 3. Send chat message
echo -e "\n3. Send chat message..."
curl -s -X POST $API_URL/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content":"Hello Jarvis!"}' | jq

# 4. List conversations
echo -e "\n4. List conversations..."
curl -s $API_URL/api/chat/conversations \
  -H "Authorization: Bearer $TOKEN" | jq

# 5. Search memory
echo -e "\n5. Search memory..."
curl -s "$API_URL/api/memory/search?q=test&limit=5" \
  -H "Authorization: Bearer $TOKEN" | jq

echo -e "\n✅ Tests completed!"
```

---

## Collection Postman

Importez cette collection pour tester tous les endpoints:

```json
{
  "info": {
    "name": "Jarvis API v1.9.0",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/health"
      }
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8100"
    }
  ]
}
```

---

**Documentation générée le**: 2025-10-26
**Version API**: 1.9.0
