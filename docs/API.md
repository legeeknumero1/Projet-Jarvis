# 🔌 API Reference - Jarvis v1.2.0

**API REST + WebSocket** pour l'assistant IA personnel avec architecture modulaire.

## ✅ **État Actuel** (24/10/2025 18:40)
- **Backend API** : ✅ Opérationnel (port 8000)
- **Health Endpoint** : ✅ Réponse healthy
- **Services connectés** : ✅ LLM, PostgreSQL, Redis, Qdrant
- **Architecture** : ✅ Factory Pattern avec 1622 fichiers Python

## 🌐 Base URL

```
Production: http://localhost:8000
Développement: http://localhost:8000
WebSocket: ws://localhost:8000/ws
```

## 🔐 Authentification

```bash
# Optionnel - JWT pour fonctionnalités avancées
Authorization: Bearer <jwt_token>

# Header API Key (développement)
X-API-Key: <jarvis_api_key>
```

---

## 🏥 Health & Status

### GET `/health`

Vérification complète du statut système avec tous les services.

**Réponse :**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-24T16:00:00Z",
  "services": {
    "database": {
      "status": "connected",
      "response_time_ms": 12
    },
    "llm": {
      "status": "ready", 
      "model": "llama3.2:1b",
      "ollama_url": "http://172.20.0.30:11434"
    },
    "memory": {
      "status": "initialized",
      "storage": "postgresql+qdrant"
    },
    "voice": {
      "stt_status": "ready",
      "tts_status": "ready"
    }
  },
  "uptime": "2h 15m 30s"
}
```

### GET `/ready`

**Kubernetes readiness probe** - vérification rapide.

**Réponse :**
```json
{
  "status": "ready",
  "timestamp": "2025-10-24T16:00:00Z"
}
```

---

## 💬 Chat & Conversation

### POST `/chat`

Conversation textuelle avec IA locale + mémoire contextuelle.

**Request :**
```json
{
  "message": "Bonjour Jarvis, comment ça va ?",
  "user_id": "default",           // optionnel
  "context": "",                  // optionnel
  "save_memory": true,           // optionnel, défaut: true
  "model": "llama3.2:1b"        // optionnel
}
```

**Response :**
```json
{
  "response": "Bonjour ! Je vais très bien merci. Comment puis-je vous aider aujourd'hui ?",
  "timestamp": "2025-10-24T16:00:00Z",
  "user_id": "default",
  "model": "llama3.2:1b",
  "memory_saved": true,
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "context_used": [
    {
      "content": "L'utilisateur préfère les explications techniques détaillées",
      "importance_score": 0.8,
      "memory_type": "preference"
    }
  ]
}
```

**Codes d'erreur :**
- `400` : Message manquant ou invalide
- `500` : Erreur LLM ou base de données
- `503` : Service Ollama indisponible

---

## 🎤 Voice & Speech

### POST `/voice/transcribe`

**Reconnaissance vocale** Whisper STT multilingue.

**Request :**
```bash
curl -X POST http://localhost:8000/voice/transcribe \
  -F "audio=@recording.wav" \
  -F "language=fr" \
  -F "user_id=default"
```

**Response :**
```json
{
  "transcript": "Bonjour Jarvis comment ça va",
  "confidence": 0.94,
  "language": "fr",
  "duration": 2.3,
  "timestamp": "2025-10-24T16:00:00Z",
  "user_id": "default"
}
```

**Formats supportés :** wav, mp3, m4a, ogg, flac

### POST `/voice/synthesize`

**Synthèse vocale** Piper TTS français haute qualité.

**Request :**
```json
{
  "text": "Bonjour ! Comment allez-vous aujourd'hui ?",
  "voice": "fr_FR-upmc-medium",  // optionnel
  "speed": 1.0,                  // optionnel, 0.5-2.0
  "user_id": "default"           // optionnel
}
```

**Response :** Fichier audio WAV
```
Content-Type: audio/wav
Content-Disposition: attachment; filename="synthesis.wav"
Content-Length: 45632
```

---

## 🧠 Memory & Context

### GET `/memory/search`

**Recherche hybride** dans les souvenirs (SQL + vectorielle).

**Request :**
```json
{
  "query": "préférences utilisateur",
  "user_id": "default",
  "limit": 5,                    // optionnel, défaut: 5
  "threshold": 0.7               // optionnel, défaut: 0.7
}
```

**Response :**
```json
{
  "results": [
    {
      "content": "L'utilisateur préfère les explications techniques détaillées",
      "importance_score": 0.8,
      "created_at": "2025-10-23T14:30:00Z",
      "last_accessed": "2025-10-24T15:45:00Z",
      "memory_type": "preference",
      "emotional_context": {},
      "metadata": {
        "id": 123,
        "category": "user_preference"
      }
    }
  ],
  "query": "préférences utilisateur",
  "total_found": 1
}
```

### POST `/memory/store`

**Stockage manuel** d'une mémoire (usage avancé).

**Request :**
```json
{
  "content": "L'utilisateur développe en Python et préfère FastAPI",
  "user_id": "default",
  "category": "preference",
  "importance_score": 0.9,       // 0.0-1.0
  "emotional_context": {
    "valence": 0.7,
    "arousal": 0.3
  }
}
```

**Response :**
```json
{
  "id": 124,
  "status": "stored",
  "embedding_created": true,
  "timestamp": "2025-10-24T16:00:00Z"
}
```

---

## 🌐 WebSocket Real-time

### WebSocket `/ws`

**Communication bidirectionnelle** temps réel pour chat interactif.

**Connexion :**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
  console.log('Connecté à Jarvis');
};

// Envoi message
ws.send(JSON.stringify({
  type: "message",
  message: "Salut Jarvis !",
  user_id: "default",
  timestamp: new Date().toISOString()
}));

// Réception réponse
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Jarvis:', data.response);
};
```

**Message types :**

**Envoi :**
```json
{
  "type": "message",
  "message": "string",
  "user_id": "string",
  "timestamp": "2025-10-24T16:00:00Z"
}
```

**Réception :**
```json
{
  "type": "response", 
  "response": "string",
  "timestamp": "2025-10-24T16:00:00Z",
  "user_id": "string",
  "conversation_id": "uuid",
  "model": "llama3.2:1b"
}
```

**Events spéciaux :**
- `typing_start` / `typing_stop` - Indicateur de frappe
- `error` - Erreurs de traitement
- `system` - Messages système

---

## 🏠 Home Assistant Integration

### GET `/homeassistant/status`

**Statut connexion** Home Assistant (si configuré).

**Response :**
```json
{
  "connected": true,
  "ha_url": "http://localhost:8123",
  "version": "2024.10.1",
  "entities_count": 47,
  "last_sync": "2025-10-24T15:30:00Z"
}
```

### GET `/homeassistant/entities`

**Liste entités** disponibles (lumières, capteurs, etc.).

**Response :**
```json
{
  "entities": [
    {
      "entity_id": "light.salon",
      "state": "on",
      "attributes": {
        "brightness": 180,
        "friendly_name": "Lumière Salon"
      }
    },
    {
      "entity_id": "sensor.temperature_salon", 
      "state": "22.1",
      "attributes": {
        "unit_of_measurement": "°C",
        "friendly_name": "Température Salon"
      }
    }
  ],
  "total": 47
}
```

### POST `/homeassistant/control`

**Contrôle appareils** domotiques via HA.

**Request :**
```json
{
  "entity_id": "light.salon",
  "action": "turn_on",
  "params": {
    "brightness": 200,
    "color_name": "blue"
  }
}
```

**Response :**
```json
{
  "success": true,
  "entity_id": "light.salon",
  "previous_state": "off",
  "new_state": "on",
  "timestamp": "2025-10-24T16:00:00Z"
}
```

---

## 🌤️ Weather Service

### GET `/weather/current`

**Météo actuelle** (si API key configurée).

**Request :**
```json
{
  "location": "Perpignan, FR",  // optionnel, défaut depuis config
  "units": "metric"             // optionnel
}
```

**Response :**
```json
{
  "location": "Perpignan, France",
  "temperature": 23.5,
  "feels_like": 25.1,
  "humidity": 65,
  "description": "Partly cloudy",
  "wind_speed": 12.3,
  "timestamp": "2025-10-24T16:00:00Z"
}
```

---

## ⚙️ System & Admin

### GET `/services/status`

**Statut détaillé** tous les microservices.

**Response :**
```json
{
  "services": {
    "llm": {
      "status": "healthy",
      "model_loaded": "llama3.2:1b",
      "ollama_version": "0.1.17",
      "memory_usage": "1.3GB"
    },
    "memory": {
      "status": "healthy", 
      "postgres_connected": true,
      "qdrant_connected": true,
      "total_memories": 1247
    },
    "voice": {
      "status": "healthy",
      "stt_ready": true,
      "tts_ready": true
    },
    "database": {
      "status": "healthy",
      "connection_pool": "5/10",
      "response_time_ms": 8
    }
  },
  "overall_status": "healthy"
}
```

### GET `/metrics`

**Métriques Prometheus** (si activé).

**Response :** Format OpenMetrics
```
# HELP jarvis_requests_total Total HTTP requests
# TYPE jarvis_requests_total counter
jarvis_requests_total{method="POST",endpoint="/chat"} 1247

# HELP jarvis_response_time_seconds Response time
# TYPE jarvis_response_time_seconds histogram
jarvis_response_time_seconds_bucket{le="0.1"} 892
jarvis_response_time_seconds_bucket{le="0.5"} 1205
```

---

## 🚨 Error Handling

### Codes d'erreur standards

| Code | Description | Exemple |
|------|------------|---------|
| `400` | Bad Request | Message manquant, format invalide |
| `401` | Unauthorized | JWT expiré ou invalide |
| `404` | Not Found | Endpoint inexistant |
| `422` | Validation Error | Schéma Pydantic non respecté |
| `500` | Internal Error | Erreur base de données, LLM crash |
| `503` | Service Unavailable | Ollama déconnecté, PostgreSQL down |

### Format d'erreur standard

```json
{
  "detail": "Description de l'erreur",
  "error_code": "JARVIS_ERROR_001",
  "timestamp": "2025-10-24T16:00:00Z",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Erreurs spécifiques

**Service LLM indisponible :**
```json
{
  "detail": "Ollama service unavailable",
  "error_code": "LLM_UNAVAILABLE", 
  "service": "ollama",
  "suggested_action": "Check docker-compose ps and ollama container logs"
}
```

**Mémoire saturée :**
```json
{
  "detail": "Memory storage limit reached",
  "error_code": "MEMORY_FULL",
  "current_usage": "95%",
  "suggested_action": "Clean old memories or increase storage"
}
```

---

## 🔧 Configuration & Development

### Variables d'environnement

```bash
# Core API
JARVIS_API_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
ALLOWED_ORIGINS=["http://localhost:3000"]

# Services URLs
OLLAMA_URL=http://localhost:11434
STT_API_URL=http://localhost:8003  
TTS_API_URL=http://localhost:8002

# Base de données
DATABASE_URL=postgresql+asyncpg://jarvis:password@localhost:5432/jarvis_db
REDIS_URL=redis://localhost:6379

# Home Assistant (optionnel)
HOME_ASSISTANT_URL=http://localhost:8123
HOME_ASSISTANT_TOKEN=your-long-lived-token

# Monitoring (optionnel)
ENABLE_PROMETHEUS_METRICS=true
```

### Rate Limiting

| Endpoint | Limite | Fenêtre |
|----------|--------|---------|
| `/chat` | 30 req/min | Par IP |
| `/voice/*` | 10 req/min | Par IP |
| `/memory/*` | 60 req/min | Par user_id |
| `/ws` | 1 connexion | Par IP |

### Formats de données

**Timestamps :** ISO 8601 UTC (`2025-10-24T16:00:00Z`)
**UUIDs :** RFC 4122 v4
**Encoding :** UTF-8
**Content-Type :** `application/json` (sauf audio)

---

## 📚 Exemples d'usage

### Chat simple

```python
import requests

response = requests.post('http://localhost:8000/chat', json={
    'message': 'Explique-moi FastAPI en 2 phrases',
    'user_id': 'developer_001'
})

print(response.json()['response'])
```

### Chat vocal complet

```python
import requests
import io

# 1. Transcription
with open('question.wav', 'rb') as f:
    transcript = requests.post(
        'http://localhost:8000/voice/transcribe',
        files={'audio': f}
    ).json()

# 2. Chat IA
chat_response = requests.post('http://localhost:8000/chat', json={
    'message': transcript['transcript'],
    'user_id': 'voice_user'
}).json()

# 3. Synthèse vocale
audio = requests.post('http://localhost:8000/voice/synthesize', json={
    'text': chat_response['response']
}).content

with open('response.wav', 'wb') as f:
    f.write(audio)
```

### WebSocket interactif

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
    // Conversation continue
    ws.send(JSON.stringify({
        type: 'message',
        message: 'Peux-tu me rappeler mes tâches du jour ?',
        user_id: 'assistant_user'
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.type === 'response') {
        console.log('🤖 Jarvis:', data.response);
        
        // Afficher dans l'interface
        displayMessage(data.response, 'bot');
    }
};
```

---

**📡 Architecture modulaire • 🧠 Mémoire persistante • 🎤 Vocal temps réel • 🏠 Domotique intégrée**