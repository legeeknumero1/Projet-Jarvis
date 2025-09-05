# 📚 DOCUMENTATION TECHNIQUE COMPLÈTE JARVIS v1.3.2

## 📋 **SOMMAIRE TECHNIQUE**

1. [Architecture Système](#architecture-système)
2. [Composants Core](#composants-core)  
3. [Microservices](#microservices)
4. [Base de Données](#base-de-données)
5. [Sécurité](#sécurité)
6. [APIs & Endpoints](#apis--endpoints)
7. [DevOps & Monitoring](#devops--monitoring)
8. [Déploiement](#déploiement)
9. [Troubleshooting](#troubleshooting)
10. [Patterns & Best Practices](#patterns--best-practices)

---

## 🏗️ **ARCHITECTURE SYSTÈME**

### **Vue d'Ensemble Enterprise**
```
┌─────────────────── JARVIS ENTERPRISE ARCHITECTURE v1.3.2 ───────────────────┐
│                                                                              │
│  ┌─── FRONTEND LAYER ────┐    ┌─── API GATEWAY ────┐    ┌─── DATA LAYER ───┐ │
│  │                       │    │                    │    │                   │ │
│  │ React Cyberpunk UI    │◄──►│ FastAPI Backend    │◄──►│ PostgreSQL 15     │ │
│  │ Port: 3000            │    │ Port: 8000         │    │ Port: 5432        │ │
│  │ WebSocket Support     │    │ JWT Authentication │    │ ACID Compliance   │ │
│  │ Speech Recognition    │    │ Rate Limiting      │    │ Backup Ready      │ │
│  │ Error Boundaries      │    │ CORS Security      │    │                   │ │
│  └───────────────────────┘    │ Prometheus Metrics │    ├───────────────────┤ │
│                               │ Health Checks      │    │ TimescaleDB       │ │
│  ┌─── MICROSERVICES ────┐    │ Input Validation   │    │ Port: 5433        │ │
│  │                       │    └────────────────────┘    │ Time Series Data  │ │
│  │ STT API (Port: 8003)  │◄─────────┐                   │ Metrics Storage   │ │
│  │ TTS API (Port: 8002)  │◄─────────┤                   │                   │ │
│  │ Interface (Port: 8000)│◄─────────┤                   ├───────────────────┤ │
│  │                       │          │                   │ Redis Cache       │ │
│  │ All with /metrics     │          │                   │ Port: 6379        │ │
│  │ Health checks         │          │                   │ Memory Store      │ │
│  │ Docker isolated       │          │                   │ Session Cache     │ │
│  └───────────────────────┘          │                   │                   │ │
│                                      │                   ├───────────────────┤ │
│  ┌─── AI & MEMORY ──────┐           │                   │ Qdrant Vector DB  │ │
│  │                       │◄──────────┘                   │ Port: 6333/6334   │ │
│  │ Ollama LLM           │                               │ AI Memory Store   │ │
│  │ Port: 11434          │                               │ Embeddings        │ │
│  │ llama3.1 + 3.2:1b    │                               │ Neural Patterns   │ │
│  │ Context Memory       │                               │                   │ │
│  │ Retry Patterns       │                               └───────────────────┘ │
│  │                      │                                                    │ │
│  │ Brain Memory System  │    ┌─── DEVOPS STACK ──────────────────────────┐  │ │
│  │ Neuromorphic Logic   │    │                                          │  │ │
│  │ Context Awareness    │    │ Jenkins CI/CD      Prometheus Monitoring │  │ │
│  │ Emotional Analysis   │    │ Port: 8080         Port: 9090            │  │ │
│  └──────────────────────┘    │                                          │  │ │
│                               │ ArgoCD GitOps      Grafana Dashboards    │  │ │
│  ┌─── EXTERNAL APIs ────┐    │ K3s Port: 8081     Port: 3001            │  │ │
│  │                       │    │                                          │  │ │
│  │ MCP Multi-Search      │    │ Loki Logs          AlertManager          │  │ │
│  │ Brave + DuckDuckGo    │    │ Port: 3100         Port: 9093            │  │ │
│  │ Tavily + Google       │    │                                          │  │ │
│  │                       │    │ K3s Kubernetes     Node Exporter         │  │ │
│  │ Browserbase Web       │    │ Local Cluster      System Metrics        │  │ │
│  │ Automated Navigation  │    │                                          │  │ │
│  └───────────────────────┘    └──────────────────────────────────────────┘  │ │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### **Patterns Architecturaux**
- **Microservices Pattern** : Services découplés avec responsabilités uniques
- **API Gateway Pattern** : Point d'entrée centralisé avec authentification
- **Circuit Breaker** : Résistance aux pannes avec retry exponential
- **Event-Driven Architecture** : WebSocket temps réel + message queuing
- **CQRS** : Séparation lecture/écriture pour performance
- **Hexagonal Architecture** : Ports et adaptateurs pour flexibilité

---

## 🔧 **COMPOSANTS CORE**

### **Backend FastAPI (`/backend/main.py`)**
```python
# Architecture modulaire avec lifespan async
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialisation services
    global brain_memory_system, profile_manager, speech_manager
    brain_memory_system = BrainMemorySystem(db)
    profile_manager = ProfileManager(db)
    speech_manager = SpeechManager(config)
    
    yield
    
    # Shutdown: Cleanup propre
    await db.disconnect()

# Application sécurisée
app = FastAPI(
    title="Jarvis API",
    version="1.3.2",
    lifespan=lifespan
)
```

**Middlewares Sécurité :**
```python
# CORS restrictif
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.secure_cors_origins,  # Pas de wildcard
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"]
)

# Rate Limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

### **Configuration Système (`/backend/config/config.py`)**
```python
class Config(BaseSettings):
    # Base de données
    database_url: str = Field(..., env="DATABASE_URL")
    redis_url: str = Field(..., env="REDIS_URL") 
    timescale_url: str = Field(..., env="TIMESCALE_URL")
    qdrant_url: str = Field(..., env="QDRANT_URL")
    
    # Services
    ollama_base_url: str = Field(..., env="OLLAMA_BASE_URL")
    tts_api_url: str = Field(..., env="TTS_API_URL")
    stt_api_url: str = Field(..., env="STT_API_URL")
    
    # Sécurité
    jarvis_secret_key: str = Field(..., env="JARVIS_SECRET_KEY")
    cors_origins: str = Field(..., env="CORS_ORIGINS")
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
```

---

## 🔬 **MICROSERVICES**

### **STT API - Speech to Text (`/services/stt/main.py`)**
```python
# Service de reconnaissance vocale
@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    start_time = time.time()
    
    try:
        # Validation format audio
        if not file.content_type.startswith('audio/'):
            raise HTTPException(400, "Format audio requis")
            
        # Transcription avec Whisper
        audio_data = await file.read()
        result = whisper_model.transcribe(audio_data)
        
        # Métriques
        metrics.transcribe_requests.inc()
        metrics.response_time.observe(time.time() - start_time)
        
        return {"text": result["text"], "confidence": result["confidence"]}
        
    except Exception as e:
        metrics.transcribe_errors.inc()
        logger.error(f"Erreur transcription: {e}")
        raise HTTPException(500, "Erreur transcription")

# Endpoint métriques Prometheus
@app.get("/metrics")
async def get_metrics():
    return PlainTextResponse(generate_latest())
```

### **TTS API - Text to Speech (`/services/tts/main.py`)**
```python
# Service de synthèse vocale
@app.post("/synthesize")
async def synthesize_text(request: TTSRequest):
    start_time = time.time()
    
    try:
        # Validation input
        if len(request.text) > 1000:
            raise HTTPException(400, "Texte trop long (max 1000 chars)")
            
        # Synthèse avec Piper
        audio_stream = piper_model.synthesize(
            text=request.text,
            voice=request.voice or "french-female",
            speed=request.speed or 1.0
        )
        
        # Métriques
        metrics.synthesis_requests.inc()
        metrics.synthesis_time.observe(time.time() - start_time)
        
        return StreamingResponse(
            audio_stream, 
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=speech.wav"}
        )
        
    except Exception as e:
        metrics.synthesis_errors.inc()
        logger.error(f"Erreur synthèse: {e}")
        raise HTTPException(500, "Erreur synthèse vocale")
```

### **Interface Hybride (`/services/interface/hybrid_server.py`)**
```python
# Serveur hybride React + Python
class HybridServer:
    def __init__(self):
        self.app = FastAPI()
        self.setup_routes()
        
    async def serve_react(self, request):
        """Servir l'application React buildée"""
        # Servir les fichiers statiques React
        static_files = StaticFiles(directory="build", html=True)
        return static_files
    
    @app.websocket("/ws")
    async def websocket_endpoint(self, websocket: WebSocket):
        await websocket.accept()
        try:
            while True:
                data = await websocket.receive_text()
                # Traiter message et répondre
                response = await self.process_message(data)
                await websocket.send_text(response)
        except WebSocketDisconnect:
            logger.info("Client disconnected")
```

---

## 💾 **BASE DE DONNÉES**

### **PostgreSQL - Base Principale (`/backend/db/database.py`)**
```python
class Database:
    def __init__(self, config: Config):
        self.config = config
        self.engine = None
        self.async_session = None
    
    async def connect(self):
        # Pool de connexions optimisé
        self.engine = create_async_engine(
            self.config.database_url,
            pool_size=10,
            max_overflow=20,
            pool_timeout=30,
            pool_pre_ping=True  # Validation connexions
        )
        
        # Factory sessions
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    @asynccontextmanager
    async def get_session_context(self):
        async with self.async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
```

### **TimescaleDB - Métriques Temporelles**
```sql
-- Table hypertable pour métriques temporelles
CREATE TABLE IF NOT EXISTS metrics_time_series (
    timestamp TIMESTAMPTZ NOT NULL,
    service_name TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value FLOAT NOT NULL,
    labels JSONB
);

-- Hypertable TimescaleDB
SELECT create_hypertable('metrics_time_series', 'timestamp');

-- Index pour performance
CREATE INDEX idx_metrics_service_time ON metrics_time_series (service_name, timestamp DESC);
CREATE INDEX idx_metrics_name_time ON metrics_time_series (metric_name, timestamp DESC);

-- Rétention automatique (1 an)
SELECT add_retention_policy('metrics_time_series', INTERVAL '1 year');
```

### **Redis - Cache & Sessions (`/backend/utils/redis_manager.py`)**
```python
class RedisManager:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        
    async def set_with_expiry(self, key: str, value: Any, expiry_seconds: int):
        """Set avec expiration automatique selon type de données"""
        serialized = json.dumps(value)
        await self.redis.setex(key, expiry_seconds, serialized)
    
    async def get_cached_session(self, session_id: str):
        """Récupération session utilisateur"""
        data = await self.redis.get(f"session:{session_id}")
        return json.loads(data) if data else None
    
    async def cache_ollama_response(self, prompt_hash: str, response: str):
        """Cache réponses IA (24h)"""
        await self.set_with_expiry(
            f"ollama:{prompt_hash}", 
            response, 
            86400  # 24h
        )
```

### **Qdrant - Mémoire Vectorielle (`/backend/memory/qdrant_adapter.py`)**
```python
class QdrantAdapter:
    def __init__(self, qdrant_url: str):
        self.client = QdrantClient(url=qdrant_url)
        self.setup_collections()
    
    async def setup_collections(self):
        """Initialiser collections mémoire"""
        collections = [
            ("conversations", 384),  # Embeddings conversations
            ("knowledge", 768),      # Base de connaissances
            ("emotions", 128)        # États émotionnels
        ]
        
        for collection_name, vector_size in collections:
            try:
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=vector_size, 
                        distance=Distance.COSINE
                    )
                )
            except Exception:
                pass  # Collection exists
    
    async def store_memory(self, memory_type: str, content: str, metadata: dict):
        """Stocker mémoire vectorielle"""
        embedding = await self.get_embedding(content)
        
        self.client.upsert(
            collection_name=memory_type,
            points=[PointStruct(
                id=uuid.uuid4().hex,
                vector=embedding,
                payload={
                    "content": content,
                    "timestamp": datetime.utcnow().isoformat(),
                    **metadata
                }
            )]
        )
```

---

## 🔐 **SÉCURITÉ**

### **Authentification JWT (`/backend/auth/security.py`)**
```python
class SecurityManager:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.pwd_context = CryptContext(
            schemes=["bcrypt"], 
            deprecated="auto"
        )
    
    def create_access_token(self, data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
        to_encode.update({"exp": expire})
        
        return jwt.encode(to_encode, self.secret_key, algorithm="HS256")
    
    def verify_token(self, token: str):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(401, "Token invalide")
            return username
        except JWTError:
            raise HTTPException(401, "Token invalide")
    
    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)
```

### **Validation Input (`/backend/auth/models.py`)**
```python
class UserCreateRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    
    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username invalide')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        # Au moins 1 majuscule, 1 minuscule, 1 chiffre
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$', v):
            raise ValueError('Mot de passe trop faible')
        return v

class MessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)
    user_id: str = Field(..., regex=r'^[a-zA-Z0-9_-]+$')
    
    @validator('message')
    def sanitize_message(cls, v):
        # Anti-XSS basique
        dangerous_patterns = [
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'data:text/html'
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError('Contenu dangereux détecté')
        
        return v
```

### **Secrets Management (`/backend/config/secrets.py`)**
```python
class SecretsManager:
    def __init__(self):
        self.secrets = {}
        self.load_secrets()
    
    def load_secrets(self):
        """Charger secrets depuis environnement avec validation"""
        required_secrets = [
            "JARVIS_SECRET_KEY",
            "POSTGRES_PASSWORD", 
            "REDIS_PASSWORD"
        ]
        
        for secret_name in required_secrets:
            value = os.getenv(secret_name)
            if not value:
                logger.warning(f"Secret {secret_name} manquant - génération automatique")
                value = self.generate_secure_secret()
                
            self.secrets[secret_name] = value
    
    def generate_secure_secret(self, length: int = 32) -> str:
        """Générer secret sécurisé"""
        return secrets.token_urlsafe(length)
    
    def get_secret(self, name: str) -> str:
        """Récupérer secret avec masquage logs"""
        secret = self.secrets.get(name)
        if secret:
            # Log masqué pour audit
            logger.info(f"Secret {name} utilisé: {secret[:4]}***{secret[-2:]}")
        return secret
```

---

## 🌐 **APIs & ENDPOINTS**

### **Endpoints Principaux**

#### **Authentification (`/auth/*`)**
```python
# POST /auth/register
{
    "username": "utilisateur",
    "email": "user@example.com", 
    "password": "MotDePasse123"
}
→ Response: {"user_id": "uuid", "access_token": "jwt_token"}

# POST /auth/login
{
    "username": "utilisateur",
    "password": "MotDePasse123"
}
→ Response: {"access_token": "jwt_token", "refresh_token": "refresh_jwt"}

# POST /auth/refresh
Headers: {"Authorization": "Bearer refresh_token"}
→ Response: {"access_token": "new_jwt_token"}
```

#### **Chat IA (`/chat`)**
```python
# POST /chat
Headers: {"Authorization": "Bearer jwt_token"}
{
    "message": "Salut Jarvis, comment ça va ?",
    "user_id": "user_uuid",
    "context": {"conversation_id": "conv_uuid"}
}
→ Response: {
    "response": "Bonjour ! Je vais très bien, merci. Comment puis-je vous aider ?",
    "confidence": 0.95,
    "processing_time": 145,
    "tokens_used": 42
}
```

#### **WebSocket Temps Réel (`/ws`)**
```javascript
// Connexion WebSocket sécurisée
const ws = new WebSocket(`ws://localhost:8000/ws?token=${jwt_token}`);

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Réponse Jarvis:', data.response);
};

// Envoi message
ws.send(JSON.stringify({
    "type": "chat",
    "message": "Quelle est la météo ?",
    "user_id": "user_uuid"
}));
```

#### **Recherche Internet (`/search/*`)**
```python
# POST /search/web
{
    "query": "actualités technologie 2025",
    "provider": "brave",  # brave, duckduckgo, tavily, google
    "max_results": 10
}
→ Response: {
    "results": [
        {
            "title": "Innovations Tech 2025",
            "url": "https://example.com/tech-2025",
            "snippet": "Les dernières innovations...",
            "score": 0.92
        }
    ],
    "provider": "brave",
    "query_time": 0.234
}

# POST /search/parallel  
{
    "query": "intelligence artificielle",
    "providers": ["brave", "tavily", "google"]
}
→ Response: {
    "aggregated_results": [...],
    "provider_results": {
        "brave": [...],
        "tavily": [...],
        "google": [...]
    },
    "best_sources": [...]
}
```

### **Endpoints Monitoring**
```python
# GET /health
→ Response: {
    "status": "healthy",
    "timestamp": "2025-08-23T10:30:00Z",
    "services": {
        "database": "connected",
        "redis": "connected", 
        "ollama": "ready",
        "qdrant": "ready"
    },
    "uptime": 86400
}

# GET /metrics (Prometheus)
→ Response: (PlainText)
# HELP jarvis_requests_total Total requests
# TYPE jarvis_requests_total counter
jarvis_requests_total{method="POST",endpoint="/chat"} 1234

# HELP jarvis_response_time_seconds Response time
# TYPE jarvis_response_time_seconds histogram
jarvis_response_time_seconds_sum 45.67
jarvis_response_time_seconds_count 1234
```

---

## 🚀 **DEVOPS & MONITORING**

### **Docker Compose Configuration**
```yaml
# docker-compose.yml - Production Ready
version: '3.8'

networks:
  jarvis_network:
    driver: bridge
    ipam:
      config:
        - subnet: ${DOCKER_SUBNET:-172.20.0.0/16}

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '2.0'
    environment:
      - DATABASE_URL=postgresql+asyncpg://...
      - REDIS_URL=redis://...
      - JARVIS_SECRET_KEY=${JARVIS_SECRET_KEY}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### **Kubernetes Manifests (`/devops-tools/k8s/`)**
```yaml
# backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jarvis-backend
  namespace: jarvis
spec:
  replicas: 2
  selector:
    matchLabels:
      app: jarvis-backend
  template:
    metadata:
      labels:
        app: jarvis-backend
    spec:
      containers:
      - name: backend
        image: jarvis-backend:1.3.2
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: jarvis-secrets
              key: database-url
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi" 
            cpu: "2000m"
```

### **Prometheus Configuration (`/devops-tools/monitoring/prometheus/`)**
```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

scrape_configs:
  - job_name: 'jarvis-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: /metrics
    scrape_interval: 30s
    
  - job_name: 'jarvis-services'
    static_configs:
      - targets: 
        - 'stt-api:8003'
        - 'tts-api:8002'
        - 'interface:8000'
    
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
```

### **Grafana Dashboards**
```json
{
  "dashboard": {
    "title": "Jarvis Enterprise Monitoring",
    "panels": [
      {
        "title": "API Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(jarvis_response_time_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Active Connections", 
        "type": "stat",
        "targets": [
          {
            "expr": "jarvis_active_connections",
            "legendFormat": "WebSocket Connections"
          }
        ]
      }
    ]
  }
}
```

### **Jenkins Pipeline (`Jenkinsfile`)**
```groovy
pipeline {
    agent any
    
    stages {
        stage('Build') {
            steps {
                script {
                    docker.build("jarvis-backend:${env.BUILD_ID}", "./backend")
                    docker.build("jarvis-frontend:${env.BUILD_ID}", "./frontend")
                }
            }
        }
        
        stage('Test') {
            parallel {
                stage('Unit Tests') {
                    steps {
                        sh 'python -m pytest backend/tests/ -v --cov=backend'
                    }
                }
                stage('Security Scan') {
                    steps {
                        sh 'bandit -r backend/ -f json -o security-report.json'
                    }
                }
            }
        }
        
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                script {
                    // Tag et push images
                    docker.withRegistry('', 'docker-hub-credentials') {
                        docker.image("jarvis-backend:${env.BUILD_ID}").push("latest")
                    }
                    
                    // Déploiement ArgoCD
                    sh 'kubectl patch application jarvis -n argocd -p \'{"spec":{"source":{"targetRevision":"main"}}}\''
                }
            }
        }
    }
    
    post {
        always {
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'htmlcov',
                reportFiles: 'index.html',
                reportName: 'Coverage Report'
            ])
        }
    }
}
```

---

## 🔧 **TROUBLESHOOTING**

### **Problèmes Courants & Solutions**

#### **1. Backend ne démarre pas**
```bash
# Vérification logs
docker logs jarvis_backend --tail 50

# Problèmes courants:
# - Variables environnement manquantes
export JARVIS_SECRET_KEY=$(openssl rand -base64 32)
export POSTGRES_PASSWORD="secure-password"

# - Base de données non accessible
docker exec -it jarvis_postgres pg_isready -U jarvis

# - Port déjà utilisé
sudo netstat -tulpn | grep :8000
```

#### **2. WebSocket se déconnecte**
```python
# Vérification connection probing
async def connection_probe():
    try:
        await asyncio.wait_for(websocket.receive_text(), timeout=0.001)
    except asyncio.TimeoutError:
        pass  # Normal
    except Exception:
        raise WebSocketDisconnect()

# Logs WebSocket
tail -f logs/jarvis_backend.log | grep WebSocket
```

#### **3. Ollama ne répond pas**
```bash
# Vérification modèles
docker exec jarvis_ollama ollama list

# Test direct API
curl http://localhost:11434/api/generate \
  -d '{"model":"llama3.2:1b","prompt":"test","stream":false}'

# Redémarrage avec cleanup
docker-compose down ollama
docker volume rm jarvis_ollama_data
docker-compose up -d ollama
```

#### **4. Métriques Prometheus manquantes**
```bash
# Vérification endpoints
curl http://localhost:8000/metrics
curl http://localhost:8003/metrics
curl http://localhost:8002/metrics

# Configuration Prometheus
docker exec jarvis_prometheus promtool check config /etc/prometheus/prometheus.yml

# Reload configuration
curl -X POST http://localhost:9090/-/reload
```

### **Scripts de Diagnostic**
```bash
#!/bin/bash
# health-check.sh - Diagnostic complet

echo "=== DIAGNOSTIC JARVIS v1.3.2 ==="

# Services Docker
echo "1. Status containers:"
docker-compose ps

# Health checks
echo "2. Health checks:"
curl -s http://localhost:8000/health | jq .
curl -s http://localhost:8003/health | jq .
curl -s http://localhost:8002/health | jq .

# Base de données
echo "3. Connexions DB:"
docker exec jarvis_postgres psql -U jarvis -d jarvis_db -c "SELECT COUNT(*) FROM pg_stat_activity;"

# Métriques
echo "4. Métriques actives:"
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets | length'

# Logs erreurs récentes
echo "5. Erreurs récentes:"
docker logs jarvis_backend --since 1h | grep ERROR | tail -5

echo "=== FIN DIAGNOSTIC ==="
```

---

## 🎯 **PATTERNS & BEST PRACTICES**

### **Patterns de Code**

#### **Repository Pattern**
```python
# /backend/repositories/user_repository.py
class UserRepository:
    def __init__(self, db: Database):
        self.db = db
    
    async def create_user(self, user_data: UserCreateRequest) -> User:
        async with self.db.get_session_context() as session:
            user = User(**user_data.dict())
            session.add(user)
            await session.flush()
            return user
    
    async def get_by_username(self, username: str) -> Optional[User]:
        async with self.db.get_session_context() as session:
            result = await session.execute(
                select(User).where(User.username == username)
            )
            return result.scalar_one_or_none()
```

#### **Service Layer Pattern**
```python
# /backend/services/chat_service.py
class ChatService:
    def __init__(self, user_repo: UserRepository, ollama_client: OllamaClient):
        self.user_repo = user_repo
        self.ollama_client = ollama_client
    
    async def process_message(self, user_id: str, message: str) -> ChatResponse:
        # Validation utilisateur
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(404, "Utilisateur non trouvé")
        
        # Traitement message avec IA
        ai_response = await self.ollama_client.generate(
            model="llama3.2:1b",
            prompt=message,
            context=user.context
        )
        
        # Sauvegarde conversation
        await self.save_conversation(user_id, message, ai_response)
        
        return ChatResponse(
            response=ai_response,
            user_id=user_id,
            timestamp=datetime.utcnow()
        )
```

#### **Factory Pattern**
```python
# /backend/factories/service_factory.py
class ServiceFactory:
    def __init__(self, config: Config):
        self.config = config
        self._services = {}
    
    def get_chat_service(self) -> ChatService:
        if 'chat' not in self._services:
            user_repo = UserRepository(self.get_database())
            ollama_client = OllamaClient(self.config.ollama_base_url)
            self._services['chat'] = ChatService(user_repo, ollama_client)
        return self._services['chat']
    
    def get_database(self) -> Database:
        if 'database' not in self._services:
            self._services['database'] = Database(self.config)
        return self._services['database']
```

### **Best Practices Sécurité**

1. **Validation à tous les niveaux**
   - Frontend: Validation côté client
   - API Gateway: Validation middleware 
   - Service: Validation métier
   - Database: Contraintes DB

2. **Principe du moindre privilège**
   - Utilisateurs: Rôles granulaires
   - Services: Permissions minimales
   - Database: Utilisateurs dédiés
   - Network: Firewalls restrictifs

3. **Defense in Depth**
   - WAF (Web Application Firewall)
   - Rate limiting multi-niveaux
   - Input sanitization
   - Output encoding
   - SQL injection prevention

### **Best Practices Performance**

1. **Caching Strategy**
   ```python
   # Cache L1: In-memory (LRU)
   # Cache L2: Redis (distributed)
   # Cache L3: Database query cache
   
   @cached(ttl=300)  # 5 minutes
   async def get_user_profile(user_id: str):
       # Expensive operation
       return await user_repo.get_with_preferences(user_id)
   ```

2. **Database Optimization**
   ```sql
   -- Index composites pour requêtes fréquentes
   CREATE INDEX idx_conversations_user_time 
   ON conversations (user_id, created_at DESC);
   
   -- Partitioning pour gros volumes
   CREATE TABLE conversations_2025 PARTITION OF conversations
   FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
   ```

3. **Async Programming**
   ```python
   # Parallélisation des opérations I/O
   async def process_batch_requests(requests: List[Request]):
       tasks = [process_single_request(req) for req in requests]
       results = await asyncio.gather(*tasks, return_exceptions=True)
       return results
   ```

### **Monitoring & Observability**

1. **Three Pillars of Observability**
   - **Metrics**: Prometheus + Grafana
   - **Logs**: Loki + Promtail  
   - **Traces**: OpenTelemetry (future)

2. **SLI/SLO Definition**
   ```yaml
   # Service Level Indicators/Objectives
   slis:
     - name: api_availability
       target: 99.9%
       measurement: successful_requests / total_requests
     
     - name: api_latency
       target: p95 < 200ms
       measurement: histogram_quantile(0.95, response_time)
   ```

3. **Alerting Rules**
   ```yaml
   # /devops-tools/monitoring/prometheus/rules/jarvis-alerts.yml
   groups:
   - name: jarvis-critical
     rules:
     - alert: ServiceDown
       expr: up{job=~"jarvis-.*"} == 0
       for: 1m
       labels:
         severity: critical
       annotations:
         summary: "Service {{ $labels.job }} is down"
   ```

---

## 📝 **CONCLUSION TECHNIQUE**

Cette documentation technique complète couvre tous les aspects de Jarvis v1.3.2, de l'architecture high-level aux détails d'implémentation. Elle sert de référence pour :

- **Développeurs** : Compréhension architecture et patterns
- **Ops Teams** : Déploiement et monitoring
- **Security Teams** : Audit et conformité
- **Management** : Vision technique et roadmap

**Mise à jour** : 23 août 2025  
**Version** : 1.3.2 Enterprise  
**Statut** : Production-Ready avec Excellence Opérationnelle