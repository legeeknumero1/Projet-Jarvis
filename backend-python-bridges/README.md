# 🐍 Jarvis Python Bridges IA - Phase 3

**Microservices Python pour services IA : Ollama (LLM), Whisper (STT), Piper (TTS), Embeddings**

Remplace les appels directs par une API HTTP centralisée et découplée.

---

## ⚡ Architecture Phase 3

### Services Exposés

```
Python Bridges API (Port 8005)
├── /api/llm/*          → Ollama LLM client
├── /api/stt/*          → Whisper STT client
├── /api/tts/*          → Piper TTS client
└── /api/embeddings/*   → Sentence Transformers
```

### Communication

```
Rust Backend (8100)
    ↓
Python Bridges (8005) ← HTTP REST JSON
    ↓
├── Ollama (11434)      ← LLM local
├── Whisper (memory)    ← STT in-memory
├── Piper (memory)      ← TTS in-memory
└── S-BERT (memory)     ← Embeddings in-memory
```

---

## 🎯 Endpoints API

### Health & Status

```bash
GET /health
# {
#   "status": "healthy",
#   "service": "python-bridges",
#   "version": "1.3.0",
#   "services": {
#     "ollama_llm": "✅",
#     "whisper_stt": "✅",
#     "piper_tts": "✅",
#     "embeddings": "✅"
#   }
# }

GET /ready
# {"status": "ready", "version": "1.3.0"}
```

### LLM - Ollama

```bash
POST /api/llm/generate
Content-Type: application/json

{
  "prompt": "Explique Python en français",
  "system_prompt": "Tu es un expert Python français",
  "temperature": 0.7,
  "max_tokens": 512
}

# Response
{
  "text": "Python est un langage...",
  "model": "llama2:7b",
  "tokens_generated": 128,
  "tokens_prompt": 15,
  "duration_ms": 2500
}
```

```bash
GET /api/llm/models
# {"models": ["llama2:7b", "neural-chat:7b", ...]}
```

### STT - Whisper

```bash
POST /api/stt/transcribe
Content-Type: application/json

{
  "audio_data": "base64_encoded_pcm_float32",
  "language": "fr"
}

# Response
{
  "text": "Bonjour, ceci est un test",
  "language": "fr",
  "confidence": 0.95,
  "duration_ms": 1200,
  "segments": [
    {
      "id": 0,
      "start": 0.0,
      "end": 2.5,
      "text": "Bonjour, ceci est un test",
      "confidence": 0.95
    }
  ]
}
```

### TTS - Piper

```bash
POST /api/tts/synthesize
Content-Type: application/json

{
  "text": "Bonjour, comment allez-vous ?",
  "voice": "fr_FR-upmc-medium",
  "speed": 1.0
}

# Response
{
  "audio_data": "base64_encoded_float32",
  "sample_rate": 22050,
  "duration_ms": 2800,
  "voice": "fr_FR-upmc-medium"
}
```

```bash
GET /api/tts/voices
# {
#   "voices": {
#     "fr_FR-upmc-medium": "Français UPMC (femme) - Recommandé",
#     "fr_FR-siwis-medium": "Français Siwis (femme)",
#     "fr_FR-tom-medium": "Français Tom (homme)"
#   }
# }
```

### Embeddings - Sentence Transformers

```bash
POST /api/embeddings/embed
Content-Type: application/json

{
  "text": "Ceci est un texte à vectoriser"
}

# Response
{
  "text": "Ceci est un texte à vectoriser",
  "vector": "base64_encoded_float32_vector",
  "dimension": 384
}
```

```bash
POST /api/embeddings/embed-batch
Content-Type: application/json

{
  "texts": [
    "Premier texte",
    "Deuxième texte",
    "Troisième texte"
  ]
}

# Response
{
  "embeddings": [
    {"text": "...", "vector": "...", "dimension": 384},
    ...
  ],
  "count": 3
}
```

---

## 🐳 Docker Integration

### Démarrer le service

```bash
cd backend-python-bridges
docker-compose up -d

# Vérifier santé
curl http://localhost:8005/health
```

### Configuration

Le service s'intègre dans l'infrastructure existante :
- Port 8005 pour API HTTP
- Même réseau `jarvis_network` que Rust backend
- Dépendances Ollama uniquement (autres services en mémoire)
- Limite mémoire 4GB (Whisper + embeddings)

---

## 📊 Caractéristiques Principales

### ✅ Implémenté

- **Ollama LLM Client** : HTTP interface vers LLM local
- **Whisper STT** : Speech-to-Text en-mémoire (modèles tiny-large)
- **Piper TTS** : Text-to-Speech français haute qualité
- **Embeddings** : Vectorisation Sentence Transformers multilingue
- **API Flask** : REST HTTP pour tous les services
- **Health Checks** : Monitoring détaillé
- **CORS** : Accès cross-origin configuré
- **Logging** : Logs structurés avec rotation

### 🔄 En Développement

- **Streaming Ollama** : Réponses streaming token-par-token
- **Caching Embeddings** : Cache vecteurs pour perf
- **Model Management** : Changer modèles à runtime
- **Rate Limiting** : Contrôle débit API

### 📋 Roadmap

- **v1.3.2** : Streaming Ollama complète
- **v1.4.0** : Caching distributed avec Redis
- **v1.5.0** : GPU acceleration (CUDA)

---

## 🔌 Communication avec Rust Backend

Le backend Rust appelle les services Python via HTTP :

```rust
// Dans le backend Rust
let client = reqwest::Client::new();

// LLM generation
let response = client
    .post("http://jarvis_python_bridges:8005/api/llm/generate")
    .json(&json!({"prompt": "..."}))
    .send()
    .await?;

// STT transcription
let response = client
    .post("http://jarvis_python_bridges:8005/api/stt/transcribe")
    .json(&json!({"audio_data": "..."}))
    .send()
    .await?;

// TTS synthesis
let response = client
    .post("http://jarvis_python_bridges:8005/api/tts/synthesize")
    .json(&json!({"text": "..."}))
    .send()
    .await?;

// Text embeddings
let response = client
    .post("http://jarvis_python_bridges:8005/api/embeddings/embed")
    .json(&json!({"text": "..."}))
    .send()
    .await?;
```

---

## 📁 Fichiers du Projet

```
backend-python-bridges/
├── app.py                 # 🚀 Application Flask principale
├── ollama_client.py       # 🤖 Client Ollama LLM
├── whisper_client.py      # 🎤 Client Whisper STT
├── piper_client.py        # 🔊 Client Piper TTS
├── embeddings_service.py  # 🧠 Service Embeddings
├── requirements.txt       # 📦 Dépendances Python
├── Dockerfile             # 🐳 Build Docker
├── docker-compose.yml     # 🐳 Service integration
├── README.md              # 📖 Ce fichier
└── logs/                  # 📝 Logs applicatif
```

---

## 🚀 Performance

### Benchmarks

```
STT (Whisper base):      ~5-10s pour 30s audio
TTS (Piper):             ~2-3s pour phrase
LLM (Ollama llama2:7b):  ~2-3 tokens/s
Embeddings:              ~0.2s pour 10 textes
```

### Optimisations

- Modèles chargés en mémoire (pas de latence I/O)
- Batch processing pour embeddings
- Connection pooling pour Ollama
- Lazy loading des modèles

---

## 🔧 Installation Locale

### Prérequis

- Python 3.11+
- FFmpeg pour Whisper/Piper
- Service Ollama accessible (http://localhost:11434)

### Setup

```bash
# Clone et environnement
cd backend-python-bridges
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sur Windows

# Installer dépendances
pip install -r requirements.txt

# Lancer API
python app.py
# 🚀 Accessible sur http://localhost:8005
```

---

## 📝 Fichiers du Projet

```
backend-python-bridges/
├── app.py                 # Application Flask
├── ollama_client.py       # Client LLM
├── whisper_client.py      # Client STT
├── piper_client.py        # Client TTS
├── embeddings_service.py  # Service embeddings
├── requirements.txt       # Dépendances
├── Dockerfile             # Build Docker
├── docker-compose.yml     # Orchestration
└── README.md              # Cette doc
```

---

## 🤝 Intégration Architecture Polyglotte

**Phase 3 dans le contexte global :**

- 🦀 **Phase 1 (DONE)** : Rust API Core
- ⚙️ **Phase 2 (DONE)** : C++ Audio Engine
- 🐍 **Phase 3 (YOU ARE HERE)** : Python IA Bridges
- 🦀 **Phase 4** : Rust DB Layer
- 🐹 **Phase 5** : Go Monitoring
- 🌐 **Phase 6+** : Frontend + Plugins

**Phase 3 apporte :**
- ✅ Découplage services IA via HTTP
- ✅ Facilité de remplacement (swap modèles)
- ✅ Scaling indépendant
- ✅ Monitoring centralisé

---

**🐍 Python Bridges IA - Services découplés haute performance**

*Architecture Polyglotte Phase 3 pour Jarvis AI Assistant*
