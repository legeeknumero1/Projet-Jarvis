#  Quick Start - Jarvis Rust Backend

**Démarrer le backend Rust en 5 minutes**

---

##  Prérequis

-  Rust 1.90+ ([installer ici](https://rustup.rs/))
-  Docker & Docker Compose (optionnel)
-  Quelques GBs d'espace disque pour les dépendances

---

##  Option 1: Démarrage Local (Rapide)

###  Cloner et configurer

```bash
cd Projet-Jarvis/core

# Copier la configuration exemple
cp .env.example .env
```

###  Compiler et lancer

```bash
# Compilation (première fois ~30-60s)
cargo build --release

# Lancer le serveur
./target/release/jarvis-core
```

###  Vérifier que ça marche

```bash
# Dans un autre terminal
curl http://localhost:8100/health

# Réponse attendue:
# {
#   "status": "healthy",
#   "version": "1.9.0",
#   ...
# }
```

 **Le serveur écoute sur `http://localhost:8100`**

---

##  Option 2: Démarrage Docker (Recommandé)

###  Construire l'image

```bash
cd Projet-Jarvis/core

docker build -t jarvis-core:1.9.0 .
```

###  Lancer avec Docker Compose

```bash
docker-compose up -d
```

###  Vérifier que c'est opérationnel

```bash
# Voir les logs
docker logs -f jarvis-core

# Health check
curl http://localhost:8100/health
```

 **Stack complète lancée:**
- Port 8100 : Rust Backend
- Port 8005 : Python Bridges (placeholder)
- Port 8004 : Audio Engine (placeholder)
- Port 3000 : Frontend (placeholder)
- Port 5432 : PostgreSQL
- Port 6379 : Redis

---

##  Tester les Endpoints

### Health Check

```bash
curl http://localhost:8100/health
```

### Envoyer un message Chat

```bash
curl -X POST http://localhost:8100/api/chat \
  -H "Content-Type: application/json" \
  -d '{"content":"Bonjour Jarvis"}'
```

### Lister les conversations

```bash
curl http://localhost:8100/api/chat/conversations
```

### Transcription vocale (STT)

```bash
curl -X POST http://localhost:8100/api/voice/transcribe \
  -H "Content-Type: application/json" \
  -d '{"audio_data":"base64_encoded_audio","language":"fr"}'
```

### Synthèse vocale (TTS)

```bash
curl -X POST http://localhost:8100/api/voice/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text":"Bonjour comment allez-vous?","voice":"fr_FR-upmc-medium"}'
```

### Ajouter à la mémoire

```bash
curl -X POST http://localhost:8100/api/memory/add \
  -H "Content-Type: application/json" \
  -d '{"content":"Information à retenir","importance":0.8}'
```

---

##  Monitoring

### Logs détaillés

```bash
# Mode développement avec logs débug
RUST_LOG=debug cargo run
```

### Voir le statut des services

```bash
curl http://localhost:8100/health | jq .
```

### Métriques Prometheus (futur)

```bash
curl http://localhost:8100/metrics
```

---

##  Arrêter les services

### Local

```bash
# Ctrl+C dans le terminal où tourne le serveur
```

### Docker

```bash
docker-compose down
```

---

##  Configuration

Modifier `.env` pour changer les paramètres:

```bash
# Serveur
HOST=0.0.0.0
PORT=8100
RUST_LOG=info

# Services externes
PYTHON_BRIDGES_URL=http://localhost:8005
AUDIO_ENGINE_URL=http://localhost:8004
```

---

##  Prochaines étapes

1. **Lire la [documentation complète](./README.md)**
2. **Explorer le code source** dans `src/`
3. **Implémenter les routes** manquantes
4. **Connecter au frontend** React (Port 3000)
5. **Intégrer Phase 2** (C++ Audio Engine)
6. **Intégrer Phase 3** (Python Bridges réelles)

---

##  Troubleshooting

### Port 8100 déjà utilisé

```bash
# Chercher le processus
lsof -i :8100

# Tuer le processus (sur Linux/Mac)
kill -9 <PID>

# Sur Windows (PowerShell)
netstat -ano | findstr :8100
taskkill /PID <PID> /F
```

### Dépendances qui tardent

```bash
# Forcer une recompilation complète
cargo clean
cargo build --release
```

### Erreurs de compilation Rust

```bash
# Mettre à jour Rust
rustup update

# Vérifier la version
rustc --version
cargo --version
```

---

##  Ressources

-  [Documentation Rust officielle](https://doc.rust-lang.org)
-  [Axum Web Framework](https://github.com/tokio-rs/axum)
-  [Tokio Async Runtime](https://tokio.rs)
-  [Docker Documentation](https://docs.docker.com)

---

** Bienvenue dans le futur du backend Rust avec Jarvis! **
