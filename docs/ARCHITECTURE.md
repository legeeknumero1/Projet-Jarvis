# Architecture Polyglotte Complète v1.9.0

**Documentation détaillée des 9 phases de l'architecture distribuée Jarvis**

---

## Vue d'Ensemble Global

```
┌─────────────────────────────────────────────────────────┐
│         Frontend React/TypeScript v19/Next14            │
│                  (Port 3000)                            │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬─────────────┐
        │            │            │             │
┌───────▼───────┐ ┌──▼───┐ ┌─────▼──┐ ┌──────▼───┐
│  Rust Core    │ │Lua   │ │Python  │ │C++      │
│  (8100)       │ │Plugins│ │Bridges │ │Audio    │
│ Phase 1       │ │Phase 8│ │Phase 3 │ │Phase 2  │
│ Axum+Tokio    │ │       │ │        │ │(8004)   │
└───────┬───────┘ └──────┘ └────┬───┘ └─────┬───┘
        │                       │           │
   ┌────▼──────────┬────────────▼──┬────────▼──┐
   │               │                │          │
┌──▼──────┐  ┌─────▼──────┐  ┌─────▼───┐ ┌──▼──────┐
│Rust DB  │  │MQTT        │  │Go       │ │Elixir  │
│Tantivy  │  │Home        │  │Monitor  │ │HA      │
│Redis    │  │Assistant   │  │(8006)   │ │(8007)  │
│Phase 4-5│  │Automations │  │Phase 6  │ │Phase 9 │
│         │  │Phase 5     │  │         │ │        │
└─────────┘  └────────────┘  └─────────┘ └────────┘
     │
  PostgreSQL + Redis + Ollama
```

---

## Les 9 Phases Détaillées

### **Phase 1: Rust Backend Core** (Port 8100)

**Technologie:** Rust + Axum + Tokio

**Responsabilités:**
- ✅ API REST haute performance
- ✅ WebSocket temps réel bidirectionnel
- ✅ Orchestration des autres services
- ✅ Gestion des conversations
- ✅ Rate limiting + CORS

**Endpoints Principaux:**
```
GET  /health                    # Santé système
GET  /ready                     # Readiness probe K8s
POST /api/chat                  # Envoyer message
GET  /api/chat/conversations   # Lister conversations
GET  /api/chat/history/:id     # Historique
WS   /ws                       # Chat temps réel
```

**Points de Connexion:**
- ⬅️ Frontend (Port 3000)
- ➡️ Phase 3: Python Bridges (8005)
- ➡️ Phase 2: C++ Audio (8004)
- ➡️ Phase 4-5: Rust Libs (DB, MQTT)
- ➡️ Phase 8: Lua (interne)

---

### **Phase 2: C++ Audio Engine** (Port 8004)

**Technologie:** C++17 + CMake + Boost

**Responsabilités:**
- ✅ DSP temps réel <1ms latence
- ✅ Audio buffering circulaire zero-copy
- ✅ High-pass filter + AGC
- ✅ Echo cancellation

**Performance:**
```
Latence:    <1ms (vs Python 50ms)
Jitter:     ±0.1ms stable
Throughput: 1M samples/s
CPU:        5% vs Python 25%
```

**Points de Connexion:**
- ⬅️ Phase 3: Whisper/Piper (Python)
- ➡️ Phase 1: Rust Core

---

### **Phase 3: Python Bridges IA** (Port 8005)

**Technologie:** Python + Flask + Async

**Services:**
- 🤖 **Ollama Client** - LLM local (LLaMA 3.2:1b)
- 🎤 **Whisper Client** - Speech-to-Text multilingue
- 🔊 **Piper Client** - Text-to-Speech français
- 🧠 **Embeddings** - Sentence Transformers

**Endpoints:**
```
POST /api/llm/generate          # Génération LLM
POST /api/voice/transcribe      # STT Whisper
POST /api/voice/synthesize      # TTS Piper
POST /api/embeddings/encode     # Vecteurs sémantiques
```

**Dépendances Externes:**
- Ollama (localhost:11434)
- Whisper model
- Piper TTS voice files

---

### **Phase 4: Rust DB Layer** (Interne - Lib)

**Technologie:** Rust + sqlx + Tantivy + Redis

**Composants:**

1. **PostgreSQL Service**
   - Conversations, Messages, Users
   - Type-safe SQL avec sqlx (compile-time verification)
   - Migrations versionnées

2. **Tantivy Full-Text Search**
   - Index inversé en-mémoire
   - BM25 ranking algorithm
   - Recherche rapide <10ms

3. **Redis Cache**
   - Cache distribué avec TTL
   - Pattern-based invalidation
   - Lazy loading

**Models:**
```rust
Conversation { id, user_id, title, summary, messages_count, ... }
Message { id, conversation_id, role, content, embedding, ... }
MemoryEntry { id, user_id, content, vector, importance, ... }
```

---

### **Phase 5: MQTT Automations** (Interne - Lib)

**Technologie:** Rust + rumqttc

**Responsabilités:**
- ✅ Automations Home Assistant
- ✅ MQTT pub/sub
- ✅ Triggers/Conditions/Actions
- ✅ Smart home intégration

**Automation Types:**
```
Triggers:  TimeOfDay, StateChange, MotionDetected, DoorOpened, Webhook
Conditions: TimeRange, StateEquals, Temperature, Brightness, DayOfWeek
Actions:   TurnOn/Off Light, SetTemperature, SendNotification, PublishMQTT
```

**Exemples:**
```
"Allume les lumières du salon si motion détectée entre 20h et 6h"
"Réduis la température à 18°C la nuit"
"Envoie notification si porte d'entrée ouverte"
```

---

### **Phase 6: Go Monitoring** (Port 8006)

**Technologie:** Go + Prometheus

**Services:**
- 🔍 **Watchdog** - Supervise tous les services
- 📊 **Metrics** - Prometheus format
- ✅ **Health Checks** - Status agregé
- 🔄 **Auto-Restart** - Services

**Métriques:**
```
container_health{service="rust-backend"}    # 0-1 health status
container_restarts{service="rust-backend"}  # Counter
api_latency_ms{endpoint="/api/chat"}        # Histogram
system_memory_usage_percent                 # Gauge
```

**Endpoints:**
```
GET /health        # Santé globale
GET /metrics       # Prometheus format
GET /ready         # Readiness
```

---

### **Phase 7: Frontend TypeScript** (Port 3000)

**Technologie:** React 19 + Next.js 14 + TypeScript

**Architecture:**
```
app/                          # Next.js App Router
├── layout.tsx              # RootLayout
├── page.tsx                # Page d'accueil
├── login/                  # Auth pages
├── chat/                   # Chat pages
└── api/                    # API routes (optionnel)

components/                  # Composants réutilisables
├── chat/
│   ├── ChatLayout          # Layout principal
│   ├── MessageList         # Affichage messages
│   ├── MessageInput        # Textarea + send
│   └── MessageItem         # Message individuel
├── auth/
│   ├── LoginForm
│   └── RegisterForm
└── layout/
    ├── Header
    ├── Sidebar
    └── RootLayout

hooks/
├── useChat                 # Chat logic
├── useWebSocket            # WS connection
└── useForm                 # Form validation

store/
├── chatStore              # Zustand
└── userStore              # Auth + prefs

types/                      # TypeScript types
lib/
├── api.ts                 # Axios client
└── utils/                 # Helpers
```

**Dépendances Clés:**
- Zustand (state)
- Axios (HTTP)
- React Hook Form (forms)
- Zod (validation)
- Tailwind CSS
- Lucide React (icons)

---

### **Phase 8: Lua Plugins** (Interne - Lib)

**Technologie:** Rust + mlua

**Système de Plugins:**
- 🔒 Sandbox sécurisé (bloque os, io, load, debug)
- 🔄 Hot-reload sans recompilation
- 🪝 Hooks système extensibles
- 📦 Gestion de métadata

**Hooks Disponibles:**
```lua
on_chat(message)           # Message reçu
on_command(cmd)            # Commande utilisateur
on_automation(automation)  # Automation exécutée
on_startup()               # Démarrage plugin
on_shutdown()              # Arrêt plugin
filter_message(msg)        # Filtrer message
filter_response(resp)      # Filtrer réponse
```

**API Lua:**
```lua
jarvis.log(msg)
jarvis.http.get(url)
jarvis.http.post(url, data)
jarvis.config.get(key)
jarvis.config.set(key, value)
jarvis.state.set(key, value)
jarvis.state.get(key)
jarvis.events.emit(event, data)
jarvis.events.on(event, callback)
```

**Exemple Plugin:**
```lua
-- @id welcome
-- @name Welcome
-- @version 1.0.0

function on_chat(message)
    if message.role == "user" then
        jarvis.log("👋 User: " .. message.content)
    end
    return { ok = true }
end

function filter_message(msg)
    msg.content = string.trim(msg.content)
    return msg
end
```

---

### **Phase 9: Elixir HA** (Port 8007)

**Technologie:** Elixir/Erlang + OTP

**Features:**
- 🔗 Clustering multi-nœuds
- 📊 Horde Registry (service discovery)
- 🎯 Horde DynamicSupervisor (distribution)
- 🔄 Raft consensus (state)
- 📡 Broadway (event processing)

**Stratégies Clustering:**
```
Static:     Configuration fichier (dev/test)
Kubernetes: Découverte via labels (prod)
EPMD:       Erlang Port Mapper Daemon
```

**Services:**
- 🔍 NodeMonitor - Santé du cluster
- 📡 EventBus - Pub/Sub
- 💾 StateManager - Raft state
- ✅ HealthCheck - Endpoint 8007
- 📊 MetricsServer - Prometheus

**Endpoints:**
```
GET /health        # Cluster health
GET /metrics       # Prometheus metrics
```

---

## Ports et Services

```
Phase 1:  Port 8100  - Rust Backend Core
Phase 2:  Port 8004  - C++ Audio Engine
Phase 3:  Port 8005  - Python Bridges IA
Phase 6:  Port 8006  - Go Monitoring
Phase 7:  Port 3000  - Frontend React
Phase 9:  Port 8007  - Elixir HA

External:
Port 5432         - PostgreSQL
Port 6379         - Redis
Port 11434        - Ollama
Port 8123         - Home Assistant
```

---

## Flux de Données

### Chat Message Complet

```
1. Frontend (3000)
   └─→ POST /api/chat

2. Rust Core (8100)
   ├─→ Phase 4: DB insert message
   ├─→ Phase 4: Cache update
   ├─→ Phase 5: Trigger automations
   └─→ Phase 3: Python Bridges (LLM)

3. Python Bridges (8005)
   └─→ Ollama (11434): Generate response

4. Rust Core (8100)
   ├─→ Phase 4: DB insert response
   ├─→ Phase 8: Lua filter_response
   └─→ WebSocket broadcast

5. Frontend (3000)
   └─→ Display message
```

### Voice Processing

```
1. Frontend: Record audio
   └─→ POST /api/voice/transcribe (Phase 3)

2. Python Bridges (8005)
   └─→ Whisper: STT

3. Result → Rust Core (8100)
   └─→ Send as text message (same flow as chat)

Response Generation:
   Rust Core → Python Bridges (Ollama) → Response

TTS:
   POST /api/voice/synthesize (Phase 3)
   └─→ Python Bridges (Piper TTS)
   └─→ Return audio stream
```

### Automation Trigger

```
1. Event occurs (motion, door, time, etc)
   └─→ Phase 5: MQTT/Home Assistant

2. Rust Core evaluates triggers/conditions
   ├─→ Phase 4: Check state in DB
   ├─→ Phase 8: Lua plugins for custom logic
   └─→ Execute actions if matched

3. Actions executed
   ├─→ Home Assistant API call
   ├─→ MQTT publish
   ├─→ Notification
   └─→ Conversation update
```

---

## Security Model

### Authentication
- JWT tokens (Phase 1)
- httpOnly cookies (production)
- User validation on every request

### Data Protection
- PostgreSQL encryption (Phase 4)
- Redis encrypted cache
- Type-safe SQL (no SQL injection)
- Input validation + sanitization

### Lua Sandbox
- Blocks: os, io, load, debug modules
- Memory limits: 10MB per plugin
- Execution timeout: 5 seconds
- Resource exhaustion protection

### Communication
- TLS/HTTPS in production
- CORS strict configuration
- Rate limiting on all endpoints
- Request-ID correlation

---

## Deployment

### Docker Compose (Local Dev)
```bash
docker-compose up -d
```

### Kubernetes (Production)
```yaml
StatefulSet: 3 nodes minimum
Persistent Volumes: PVC PostgreSQL + Redis
ConfigMaps: Configuration
Secrets: API keys, JWT secrets
Services: ClusterIP + LoadBalancer
```

### Environment Variables
```bash
# Phase 1
RUST_LOG=info
DATABASE_URL=postgresql://...
REDIS_URL=redis://localhost:6379

# Phase 3
OLLAMA_URL=http://localhost:11434
WHISPER_MODEL=base.en
PIPER_VOICE=fr_FR-gilles-medium

# Phase 6
PROMETHEUS_SCRAPE_INTERVAL=15s

# Phase 9
CLUSTER_STRATEGY=kubernetes
NAMESPACE=default
```

---

## Performance Targets

| Métrique | Target |
|----------|--------|
| API Latency | <100ms |
| Chat Response | <2s |
| STT Transcription | <1s |
| TTS Synthesis | <500ms |
| Memory Usage | <500MB |
| CPU Usage | <20% |
| Uptime | >99.5% |

---

## Development Workflow

1. **Code Changes**
   - Modify relevant phase (Rust/Python/TypeScript/etc)
   - Run local tests

2. **Build**
   ```bash
   cargo build --release        # Rust
   npm run build                # Frontend
   python -m pytest             # Python
   ```

3. **Deploy**
   - Docker build + push
   - K8s apply manifests
   - Verify health checks

4. **Monitor**
   - Prometheus metrics
   - Logs aggregation
   - Error tracking

---

**Architecture moderne, distribué, résilient et haute performance 🚀**

*Version: 1.9.0 | Phases: 9 complètes | Status: Production-ready*
