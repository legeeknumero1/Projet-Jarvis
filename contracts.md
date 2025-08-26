# Contrats d'API Jarvis AI

## Vue d'ensemble
Ce document définit les contrats d'API et le plan d'intégration pour passer du mode mock au backend réel Jarvis AI.

## Variables d'environnement

### Frontend (.env)
```bash
# Mode actuel: mock (par défaut)
REACT_APP_LLM_PROVIDER=mock
# Alternatives: emergent|openai|anthropic|ollama

# URL du backend (déjà configurée)
REACT_APP_BACKEND_URL=<configured_url>

# Clé universelle (quand provider != mock)
REACT_APP_EMERGENT_LLM_KEY=<user_provided_key>
```

### Backend (.env)
```bash
# Fournisseur LLM
LLM_PROVIDER=mock
# Alternatives: emergent|openai|anthropic|ollama

# Clé universelle Emergent
EMERGENT_LLM_KEY=<user_key>

# MongoDB (déjà configurée)
MONGO_URL=<configured_url>
```

## 1. API Contracts - Chat Streaming

### Endpoint: `POST /api/chat/stream`
```typescript
// Request
{
  "messages": [
    {
      "role": "user" | "assistant",
      "content": string,
      "timestamp": string
    }
  ],
  "model": string,           // "gpt-4", "claude-3-opus", etc.
  "temperature": number,     // 0.0 - 1.0
  "topP": number,           // 0.0 - 1.0
  "threadId": string,       // UUID de conversation
  "streamingMode": "sse" | "websocket"
}

// Response (Server-Sent Events)
data: {"type": "start", "messageId": "msg-uuid"}
data: {"type": "token", "content": "Bonjour", "messageId": "msg-uuid"}
data: {"type": "token", "content": " ! Je", "messageId": "msg-uuid"}
data: {"type": "complete", "messageId": "msg-uuid", "totalTokens": 150}
```

### Intégration Frontend
**Fichier**: `/src/lib/api.js`

**Mock actuel**:
```javascript
// Dans store.js - sendMessage()
const response = await generateMockResponse(content, settings);
```

**Intégration réelle**:
```javascript
// Remplacer par:
const streamResponse = await api.streamChat(currentMessages, {
  model: settings.model,
  temperature: settings.temperature,
  topP: settings.topP,
  threadId: currentThreadId
});
```

## 2. API Contracts - Voice Recognition

### Endpoint: `POST /api/voice/transcribe`
```typescript
// Request (multipart/form-data)
{
  "audio": File,           // Audio chunks (WebM/MP3)
  "language": string,      // "fr-FR", "en-US"
  "format": "webm" | "wav" | "mp3"
}

// Response
{
  "transcript": string,
  "confidence": number,    // 0.0 - 1.0
  "language": string,
  "duration": number       // en secondes
}
```

### Intégration Frontend
**Mock actuel** (MicButton.jsx):
```javascript
const transcript = await generateMockTranscription(800);
```

**Intégration réelle**:
```javascript
const transcript = await api.transcribeAudio(audioBlob, {
  language: settings.language
});
```

## 3. API Contracts - Text-to-Speech

### Endpoint: `POST /api/voice/synthesize`
```typescript
// Request
{
  "text": string,
  "voice": "alloy" | "echo" | "fable" | "onyx" | "nova" | "shimmer",
  "language": string,
  "speed": number          // 0.5 - 2.0
}

// Response (binary audio stream)
Content-Type: audio/mpeg
```

## 4. Données mockées à remplacer

### A. Messages simulés (mockNLP.js)
**Localisation**: `/src/lib/mockNLP.js`

**Mock supprimé**:
- `generateMockResponse()` 
- `mockResponses` object
- Command processing logic

**Remplacé par**: Vraies réponses des modèles LLM

### B. Transcription simulée
**Mock supprimé**: 
- `generateMockTranscription()`
- Samples prédéfinis

**Remplacé par**: Vraie STT (Whisper via Emergent)

## 5. Modèles de données Backend

### Thread/Conversation
```python
class Thread(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    model: str
    user_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    message_count: int = 0
```

### Message
```python
class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    thread_id: str
    role: Literal["user", "assistant"]
    content: str
    model: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    token_count: Optional[int] = None
    metadata: Optional[Dict] = {}
```

## 6. Endpoints Backend à implémenter

### Gestion des conversations
- `GET /api/threads` - Lister conversations
- `POST /api/threads` - Créer conversation  
- `PUT /api/threads/{id}` - Modifier titre
- `DELETE /api/threads/{id}` - Supprimer conversation
- `GET /api/threads/{id}/messages` - Messages d'une conversation

### Streaming Chat
- `POST /api/chat/stream` - Chat avec streaming SSE
- `POST /api/chat/complete` - Chat sans streaming (fallback)

### Fonctionnalités vocales
- `POST /api/voice/transcribe` - STT
- `POST /api/voice/synthesize` - TTS

### Paramètres
- `GET /api/settings` - Récupérer paramètres utilisateur
- `PUT /api/settings` - Mettre à jour paramètres

## 7. Plan d'intégration étape par étape

### Phase 1: Backend de base
1. Créer modèles MongoDB (Thread, Message)
2. Implémenter CRUD conversations
3. Intégrer EMERGENT_LLM_KEY avec client unifié
4. Endpoint streaming SSE fonctionnel

### Phase 2: Intégration Frontend
1. Créer `/src/lib/api.js` avec vraies requêtes
2. Remplacer mock dans store.js
3. Gérer les erreurs de connexion
4. Basculer via variable d'environnement

### Phase 3: Fonctionnalités vocales
1. Endpoint STT avec Emergent/Whisper
2. Intégration TTS (optionnel)
3. Gestion des formats audio
4. Interface push-to-talk améliorée

### Phase 4: Optimisations
1. Mise en cache des réponses
2. Persistance état utilisateur
3. Analytics et métriques
4. Rate limiting et quotas

## 8. Points d'attention

### Sécurité
- ❌ Jamais de clés API côté client
- ✅ EMERGENT_LLM_KEY stockée côté backend uniquement
- ✅ Validation des entrées utilisateur
- ✅ Rate limiting par utilisateur

### Performance  
- Streaming SSE optimal (pas WebSocket sauf besoin)
- Compression des réponses longues
- Pagination des conversations (50 par page)
- Nettoyage automatique des anciennes données

### UX/UI
- Indicateurs de connexion réseau
- Mode hors-ligne gracieux
- Retry automatique sur échec
- Messages d'erreur contextuels

## 9. Tests d'intégration

### Backend
```bash
# Test streaming
curl -X POST /api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hello"}],"model":"gpt-4"}'

# Test STT
curl -X POST /api/voice/transcribe \
  -F "audio=@test.webm" \
  -F "language=fr-FR"
```

### Frontend
- Tests de basculement mock→réel
- Gestion des déconnexions réseau
- Validation des réponses streaming
- Interface vocale end-to-end

## 10. Déploiement

### Variables d'environnement de production
```bash
# Frontend
REACT_APP_LLM_PROVIDER=emergent
REACT_APP_BACKEND_URL=https://api.jarvis-ai.example.com

# Backend  
LLM_PROVIDER=emergent
EMERGENT_LLM_KEY=<production_key>
MONGO_URL=<production_mongo>
```

### Commande de basculement
```bash
# Development → Production
export REACT_APP_LLM_PROVIDER=emergent
export LLM_PROVIDER=emergent
yarn build && yarn start
```

---

**Status actuel**: ✅ Frontend complet avec mock
**Prochaine étape**: Implémenter Phase 1 (Backend de base) avec intégration EMERGENT_LLM_KEY