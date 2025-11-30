# API Reference - Jarvis v1.9.0

REST + WebSocket API for the polyglot intelligent assistant.

## Current Status

- **Backend API**: Operational (port 8100)
- **Health Endpoint**: Available
- **Connected Services**: Rust Backend, Python Bridges, C++ Audio, Databases
- **Architecture**: 9-phase polyglot system

## Base URL

```
Production: http://localhost:8100
Development: http://localhost:8100
WebSocket: ws://localhost:8100/ws
```

## Authentication

```bash
# JWT Token (required for protected endpoints)
Authorization: Bearer <jwt_token>

# API Key header (optional)
X-API-Key: <api_key>
```

---

## Health & Status

### GET `/health`

Complete system status check with all services.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-25T12:00:00Z",
  "services": {
    "database": {
      "status": "connected",
      "response_time_ms": 15
    },
    "cache": {
      "status": "ready",
      "type": "redis"
    },
    "llm": {
      "status": "ready",
      "model": "llama3.2:1b"
    },
    "audio": {
      "status": "operational"
    }
  }
}
```

### GET `/ready`

Kubernetes readiness probe endpoint.

**Response:** 200 OK if ready, 503 if not ready

---

## Chat API

### POST `/api/chat`

Send message to the assistant.

**Request:**
```json
{
  "content": "Hello, how are you?",
  "conversation_id": "uuid-optional",
  "metadata": {
    "source": "web"
  }
}
```

**Response:**
```json
{
  "id": "message-uuid",
  "status": "success",
  "response": "I'm doing well, thank you for asking!",
  "conversation_id": "uuid",
  "timestamp": "2025-10-25T12:00:00Z"
}
```

### GET `/api/chat/conversations`

List all conversations.

**Response:**
```json
{
  "conversations": [
    {
      "id": "uuid",
      "title": "Hello World",
      "created_at": "2025-10-25T10:00:00Z",
      "updated_at": "2025-10-25T12:00:00Z"
    }
  ]
}
```

### GET `/api/chat/history/:conversation_id`

Get conversation history.

**Response:**
```json
{
  "conversation_id": "uuid",
  "messages": [
    {
      "id": "uuid",
      "role": "user",
      "content": "Hello",
      "timestamp": "2025-10-25T10:00:00Z"
    },
    {
      "id": "uuid",
      "role": "assistant",
      "content": "Hi there!",
      "timestamp": "2025-10-25T10:00:01Z"
    }
  ]
}
```

---

## WebSocket

### WS `/ws`

Real-time chat connection.

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8100/ws');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received:', message);
};

ws.send(JSON.stringify({
  type: 'message',
  content: 'Hello'
}));
```

---

## Error Handling

All errors return standard format:

```json
{
  "status": "error",
  "code": "VALIDATION_ERROR",
  "message": "Invalid request format",
  "details": {
    "field": "content",
    "reason": "Field cannot be empty"
  }
}
```

**Common Status Codes:**
- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error
- 503: Service Unavailable

---

## Rate Limiting

- Rate limit: 100 requests per minute per IP
- Headers returned:
  - `X-RateLimit-Limit`: 100
  - `X-RateLimit-Remaining`: 99
  - `X-RateLimit-Reset`: Unix timestamp

---

## Versioning

Current API version: 1.9.0

Breaking changes will increment major version.
New features will increment minor version.
Bug fixes will increment patch version.

---

## Endpoints Summary

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | /health | No | System health check |
| GET | /ready | No | Readiness probe |
| POST | /api/chat | Yes | Send message |
| GET | /api/chat/conversations | Yes | List conversations |
| GET | /api/chat/history/:id | Yes | Get history |
| WS | /ws | Yes | WebSocket chat |

---

Last Updated: 2025-10-25
Version: 1.9.0
