# 🧑‍💻 GUIDE DÉVELOPPEURS JARVIS V1.3.2 - 2025

## 🎯 **POUR NOUVEAUX DÉVELOPPEURS**

### **Bienvenue sur Jarvis !**
Ce guide vous accompagne pour contribuer efficacement au projet **Jarvis v1.3.2**, un assistant IA personnel enterprise-grade avec une stack DevOps complète.

**⚡ Démarrage rapide : 15 minutes pour être opérationnel !**

---

## 📋 **PRÉREQUIS & SETUP INITIAL**

### **Environnement Recommandé**
```yaml
OS: Linux (Ubuntu 20.04+ recommandé)
Docker: v24.0+
Docker Compose: v2.20+
Node.js: v18+ (pour frontend)
Python: 3.11+
Kubernetes: K3s v1.33+ (pour DevOps)
RAM: 16GB minimum (32GB recommandé)
Storage: 50GB minimum
```

### **Installation Rapide**
```bash
# 1. Clone du projet
git clone https://github.com/user/Projet-Jarvis.git
cd Projet-Jarvis

# 2. Setup permissions
chmod +x scripts/*.sh
chmod +x devops-tools/*.sh

# 3. Configuration environnement
cp .env.example .env
nano .env  # Éditer avec vos paramètres

# 4. Premier démarrage
./scripts/setup-dev.sh
```

### **Variables Environnement Dev**
```bash
# .env pour développement
JARVIS_SECRET_KEY="dev-secret-key-32-characters-min"
POSTGRES_PASSWORD="dev-password-secure"
REDIS_PASSWORD="dev-cache-password"
CORS_ORIGINS="http://localhost:3000,http://127.0.0.1:3000"
ENVIRONMENT="development"
DATABASE_URL="postgresql://jarvis:dev-password-secure@localhost:5432/jarvis_dev"
REDIS_URL="redis://:dev-cache-password@localhost:6379/0"
```

---

## 🏗️ **ARCHITECTURE POUR DÉVELOPPEURS**

### **Vue d'Ensemble Technique**
```
Jarvis v1.3.2 = Microservices + DevOps + Sécurité Enterprise

┌─ Frontend React (Port 3000) ─────────────────────┐
│ • Interface cyberpunk TypeScript                 │
│ • WebSocket temps réel                          │
│ • Error Boundaries + Recovery                   │
└─────────────────┬─────────────────────────────────┘
                  │ HTTP/WS + JWT Auth
┌─ Backend FastAPI (Port 8000) ────────────────────┐
│ • API REST + WebSocket sécurisé                 │
│ • JWT/OAuth2 + Rate limiting                    │
│ • Métriques Prometheus intégrées                │
│ • Validation Pydantic stricte                   │
└─────────────────┬─────────────────────────────────┘
                  │ Microservices
┌─ Services Core ──┴───────────────────────────────┐
│ • STT API (8003): Whisper recognition           │
│ • TTS API (8002): Piper synthesis               │
│ • Ollama LLM (11434): IA locale                 │
│ • PostgreSQL (5432): DB principale              │
│ • Redis (6379): Cache + sessions                │
│ • Qdrant (6333): Mémoire vectorielle            │
└──────────────────────────────────────────────────┘

┌─ Stack DevOps (Monitoring) ──────────────────────┐
│ • Prometheus (9090): Métriques                  │
│ • Grafana (3001): Dashboards                    │
│ • Loki (3100): Logs centralisés                 │
│ • Jenkins (8080): CI/CD                         │
│ • ArgoCD (8081): GitOps K8s                     │
└──────────────────────────────────────────────────┘
```

### **Structure Code Détaillée**
```
backend/
├── main.py                 # FastAPI app + middlewares + routes
├── auth/                   # 🔐 Authentification complète
│   ├── models.py          # User model + Pydantic schemas  
│   ├── security.py        # JWT + bcrypt + validation
│   ├── dependencies.py    # FastAPI auth dependencies
│   └── routes.py          # Endpoints /auth/* (login/logout)
├── config/                # ⚙️ Configuration centralisée
│   ├── config.py         # Settings Pydantic avec validation
│   ├── logging_config.py  # Logs sécurisés + sanitization
│   └── secrets.py        # Gestionnaire secrets chiffrés
├── memory/                # 🧠 Mémoire neuromorphique
│   ├── brain_memory_system.py  # Système central
│   ├── hippocampus.py          # Stockage mémoire
│   ├── limbic_system.py        # Analyse émotions
│   └── prefrontal_cortex.py    # Planification actions
├── integration/           # 🔌 Intégrations externes
│   ├── ollama_client.py  # Client LLM avec retry + metrics
│   ├── home_assistant.py  # API domotique
│   └── mcp_client.py     # Model Context Protocol web
├── services/              # 🛠️ Services métier
│   ├── weather_service.py # API météo
│   └── web_service.py    # Services web
├── utils/                 # 🔧 Utilitaires
│   ├── redis_manager.py  # Cache Redis sécurisé
│   └── logging_sanitizer.py # Nettoyage logs
└── db/                    # 💾 Base de données
    ├── database.py       # Configuration DB + pool
    └── init.sql         # Schema initial

frontend/src/
├── App.js                # Application React principale
├── components/           # Composants React
│   └── CyberpunkJarvisInterface.js  # Interface principale
├── utils/               # Utilitaires React  
│   └── errorBoundary.js # Error boundary avec recovery
├── hooks/               # Hooks personnalisés
├── contexts/            # Contexts React (auth, theme)
└── api/                 # Clients API (fetch, WebSocket)

services/                # 🎙️ Microservices
├── stt/main.py         # Service reconnaissance vocale
├── tts/main.py         # Service synthèse vocale
└── interface/hybrid_server.py  # Serveur WebSocket

devops-tools/           # 🚀 Stack DevOps
├── docker-compose-devops.yml
├── start-devops.sh     # Script démarrage complet
├── monitoring/         # Prometheus + Grafana + Loki
├── jenkins/           # CI/CD pipelines
├── k8s/              # Manifests Kubernetes
└── configs/          # Configurations (nginx, etc.)
```

---

## 🔧 **DÉVELOPPEMENT LOCAL**

### **Démarrage Développement**
```bash
# Option 1: Développement complet (recommandé)
docker-compose up -d postgres redis qdrant timescaledb ollama
cd backend && python main.py &
cd frontend && npm start &

# Option 2: Développement avec services Docker
docker-compose up -d
# Puis modifier et redémarrer seulement les services modifiés

# Option 3: Développement backend seul
cd backend
pip install -r requirements.txt
python main.py
# Backend disponible sur http://localhost:8000
```

### **Tests en Développement**
```bash
# Backend tests
cd backend
python -m pytest tests/ -v

# Frontend tests  
cd frontend
npm test

# Tests d'intégration
docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# Tests sécurité (recommandé avant PR)
bandit -r backend/
npm audit
docker scout cves
```

### **Debugging**
```bash
# Logs en temps réel
docker-compose logs -f backend
docker-compose logs -f frontend

# Debug backend avec breakpoints
cd backend
python -m debugpy --listen 5678 --wait-for-client main.py

# Debug frontend avec React DevTools
# Installer React DevTools dans navigateur
# http://localhost:3000

# Métriques en développement
curl http://localhost:8000/metrics
curl http://localhost:8000/health
```

---

## 📝 **STANDARDS CODE & CONTRIBUTION**

### **Standards Python (Backend)**
```python
# Types obligatoires
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    """Schéma création utilisateur."""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    password: str = Field(..., min_length=8)

# Docstrings françaises
def create_user(user_data: UserCreate) -> Optional[User]:
    """
    Créer un nouvel utilisateur.
    
    Args:
        user_data: Données utilisateur validées
        
    Returns:
        Utilisateur créé ou None si erreur
        
    Raises:
        ValidationError: Si données invalides
        DatabaseError: Si erreur base de données
    """
    pass

# Gestion d'erreurs robuste
try:
    result = risky_operation()
    return {"success": True, "data": result}
except SpecificError as e:
    logger.error(f"Erreur spécifique: {e}")
    raise HTTPException(status_code=400, detail="Erreur validation")
except Exception as e:
    logger.error(f"Erreur inattendue: {e}")
    raise HTTPException(status_code=500, detail="Erreur serveur")
```

### **Standards React (Frontend)**
```tsx
// TypeScript strict + interfaces
interface JarvisProps {
  isConnected: boolean;
  onMessage: (message: string) => void;
  className?: string;
}

// Composants fonctionnels + hooks
const JarvisInterface: React.FC<JarvisProps> = ({ 
  isConnected, 
  onMessage, 
  className 
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Cleanup mémoire obligatoire
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws');
    
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      setMessages(prev => [...prev, message]);
    };
    
    // Cleanup
    return () => {
      ws.close();
    };
  }, []);

  // Error boundary pour chaque composant critique
  if (error) {
    return <ErrorFallback error={error} onRetry={() => setError(null)} />;
  }

  return (
    <div className={`jarvis-interface ${className}`}>
      {/* JSX avec TypeScript */}
    </div>
  );
};
```

### **Standards Docker**
```dockerfile
# Multi-stage builds obligatoires
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . .

# User non-root pour sécurité
RUN adduser --system --no-create-home jarvis
USER jarvis

# Health check obligatoire
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["python", "main.py"]
```

### **Workflow Git**
```bash
# Branches feature
git checkout -b feature/AUTH-123-implement-2fa
git checkout -b bugfix/JARVIS-456-fix-websocket-memory-leak
git checkout -b refactor/backend-config-management

# Commits conventionnels
git commit -m "feat(auth): ajouter authentification 2FA avec TOTP

- Implémentation pyotp pour génération codes
- Interface React pour setup utilisateur  
- Tests unitaires + e2e complets
- Documentation API mise à jour
- Métriques auth_2fa_* ajoutées

Refs: AUTH-123"

# Pull Request template obligatoire
# Description
# Tests ajoutés
# Screenshots (si UI)
# Checklist sécurité
# Impact performance
# Breaking changes
```

---

## 🔐 **SÉCURITÉ POUR DÉVELOPPEURS**

### **Règles Sécurité Obligatoires**
```python
# ❌ INTERDIT - Secrets en dur
API_KEY = "sk-1234567890abcdef"  # NON !

# ✅ OBLIGATOIRE - Variables environnement
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("OPENAI_API_KEY requis")

# ❌ INTERDIT - SQL direct
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")  # NON !

# ✅ OBLIGATOIRE - ORM + validation
user = session.query(User).filter(User.id == user_id).first()

# ❌ INTERDIT - Logs avec données sensibles
logger.info(f"User login: {username} with password {password}")  # NON !

# ✅ OBLIGATOIRE - Logs sanitizés
logger.info(f"User login attempt: {sanitize_for_logs(username)}")

# ❌ INTERDIT - CORS wildcard en prod
app.add_middleware(CORSMiddleware, allow_origins=["*"])  # NON !

# ✅ OBLIGATOIRE - CORS restrictif
allowed_origins = os.getenv("CORS_ORIGINS", "").split(",")
app.add_middleware(CORSMiddleware, allow_origins=allowed_origins)
```

### **Validation Input Obligatoire**
```python
# Pydantic models pour validation stricte
class UserInput(BaseModel):
    username: str = Field(..., regex=r'^[a-zA-Z0-9_]{3,20}$')
    email: EmailStr
    age: int = Field(..., gt=0, lt=120)

# Sanitization automatique
def sanitize_html(input_str: str) -> str:
    """Nettoyer HTML/XSS des inputs utilisateur."""
    return html.escape(input_str).strip()

# Rate limiting par utilisateur
@limiter.limit("10 per minute")
async def login_endpoint(request: Request, user_data: UserLogin):
    # ...
```

### **Authentification JWT**
```python
# Configuration JWT sécurisée
JWT_SECRET_KEY = os.getenv("JARVIS_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict) -> str:
    """Créer token JWT sécurisé."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)

# Middleware auth obligatoire pour endpoints protégés
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.url.path.startswith("/api/protected"):
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response(status_code=401)
    response = await call_next(request)
    return response
```

---

## 📊 **MONITORING & DEBUGGING**

### **Métriques Développeur**
```python
# Ajouter métriques custom
from prometheus_client import Counter, Histogram, Gauge

# Compteurs
REQUEST_COUNT = Counter('jarvis_requests_total', 'Total requests', ['method', 'endpoint'])
ERROR_COUNT = Counter('jarvis_errors_total', 'Total errors', ['error_type'])

# Histogrammes pour latence
REQUEST_DURATION = Histogram('jarvis_request_duration_seconds', 'Request duration')

# Gauges pour état
ACTIVE_CONNECTIONS = Gauge('jarvis_active_connections', 'Active WebSocket connections')

# Utilisation dans code
@REQUEST_DURATION.time()
async def api_endpoint():
    REQUEST_COUNT.labels(method='POST', endpoint='/api/chat').inc()
    try:
        # ... logique métier
        return {"success": True}
    except Exception as e:
        ERROR_COUNT.labels(error_type=type(e).__name__).inc()
        raise
```

### **Logs Développeur**
```python
import logging
from utils.logging_sanitizer import sanitize_data

logger = logging.getLogger(__name__)

# Logs structurés avec contexte
def log_user_action(user_id: int, action: str, data: dict = None):
    """Logger action utilisateur avec contexte."""
    log_data = {
        "user_id": user_id,
        "action": action,
        "timestamp": datetime.utcnow().isoformat(),
        "data": sanitize_data(data) if data else None
    }
    logger.info("User action", extra=log_data)

# Logs erreurs avec stack trace
try:
    risky_operation()
except Exception as e:
    logger.error(
        f"Erreur dans {__name__}: {e}",
        extra={
            "function": "risky_operation",
            "error_type": type(e).__name__,
            "stack_trace": traceback.format_exc()
        }
    )
```

### **Debug Performance**
```python
import time
from functools import wraps

def profile_time(func_name: str = None):
    """Décorateur pour profiler temps d'exécution."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.time()
            result = await func(*args, **kwargs)
            duration = time.time() - start
            logger.info(f"{func_name or func.__name__} took {duration:.3f}s")
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start
            logger.info(f"{func_name or func.__name__} took {duration:.3f}s")
            return result
            
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

# Utilisation
@profile_time("database_query")
async def get_user_by_id(user_id: int) -> Optional[User]:
    # Query database
    pass
```

---

## 🚀 **DÉPLOIEMENT & CI/CD**

### **Pipeline CI/CD**
```yaml
# .github/workflows/ci-cd.yml
name: Jarvis CI/CD
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      # Tests sécurité obligatoires
      - name: Security scan
        run: |
          pip install bandit safety
          bandit -r backend/
          safety check
      
      # Tests unitaires
      - name: Run tests
        run: |
          cd backend
          pip install -r requirements.txt
          python -m pytest tests/ -v --cov=./ --cov-report=xml
      
      # Tests e2e
      - name: E2E tests
        run: |
          docker-compose -f docker-compose.test.yml up --abort-on-container-exit

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to staging
        run: |
          # Déploiement automatique avec ArgoCD
          kubectl apply -f k8s/staging/
```

### **Déploiement K8s**
```yaml
# k8s/backend-deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jarvis-backend
  namespace: jarvis
spec:
  replicas: 3
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
        image: jarvis-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: JARVIS_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: jarvis-secrets
              key: secret-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

---

## 🐛 **DEBUGGING AVANCÉ**

### **Problèmes Courants**

#### **Erreur Base de Données**
```bash
# Debug connexion PostgreSQL
docker exec -it jarvis_postgres psql -U jarvis -d jarvis_db
\dt  # Lister tables
\d users  # Schéma table users

# Reset DB en développement
docker-compose down postgres
docker volume rm jarvis_postgres_data
docker-compose up -d postgres
# Attendre 10 secondes
cd backend && alembic upgrade head
```

#### **Erreur WebSocket**
```python
# Debug WebSocket avec logs
import logging
logging.getLogger('websocket').setLevel(logging.DEBUG)

# Test connexion WebSocket
import websocket
ws = websocket.create_connection("ws://localhost:8000/ws")
ws.send('{"type": "test", "message": "hello"}')
result = ws.recv()
print(result)
ws.close()
```

#### **Erreur Mémoire React**
```javascript
// Debug memory leaks React
// Chrome DevTools > Memory > Heap Snapshot

// Cleanup obligatoire dans useEffect
useEffect(() => {
  const ws = new WebSocket('ws://localhost:8000/ws');
  const timer = setInterval(() => {
    // Timer logic
  }, 1000);
  
  // OBLIGATOIRE: cleanup
  return () => {
    ws.close();
    clearInterval(timer);
  };
}, []);

// Éviter références circulaires
const handleCallback = useCallback((data) => {
  // Handle data
}, [dependency]);
```

### **Outils Debug**
```bash
# Profiling Python
cd backend
pip install py-spy
py-spy record -o profile.svg -d 30 -s -- python main.py

# Monitoring ressources
docker stats
docker exec jarvis_backend ps aux
htop

# Network debugging
docker network ls
docker network inspect jarvis_jarvis_network
```

---

## 📚 **RESSOURCES & DOCUMENTATION**

### **Documentation Projet**
- 📖 **Guide Complet** : `/docs/DOCUMENTATION_COMPLETE_2025.md`
- 🔧 **Configuration** : `/docs/CLAUDE.md`
- 🐛 **Problèmes Connus** : `/docs/BUGS.md`
- 🚀 **DevOps Guide** : `/docs/DEVOPS_GUIDE.md`
- 🔐 **Sécurité** : `/docs/SECURITY_FIXES.md`

### **API Documentation**
```bash
# Swagger UI interactif
http://localhost:8000/docs

# Schéma OpenAPI
http://localhost:8000/openapi.json

# Redoc alternative
http://localhost:8000/redoc
```

### **Dashboards Monitoring**
- 📊 **Grafana** : http://localhost:3001 (admin/jarvis2025)
- 📈 **Prometheus** : http://localhost:9090
- 📝 **Logs Loki** : http://localhost:3100
- 🔧 **ArgoCD** : https://localhost:8081 (admin/9CKCz7l99S-5skqx)

### **Communauté & Support**
```yaml
📧 Contact Principal:
  - Enzo (Créateur): Perpignan, France
  - Email: [À compléter]
  - GitHub: [À compléter]

🤝 Contribution:
  - Issues: GitHub Issues
  - Discussions: GitHub Discussions  
  - Wiki: /docs/ complet
  - Standards: Respect du guide développeurs

📚 Veille Technologique:
  - FastAPI: https://fastapi.tiangolo.com/
  - React: https://react.dev/
  - Kubernetes: https://kubernetes.io/docs/
  - Security: OWASP, CIS Benchmarks
```

### **Formation Continue**
- 🔐 **Sécurité** : OWASP Top 10, secure coding practices
- ⚛️ **React** : Hooks avancés, performance optimization
- 🐍 **FastAPI** : Async patterns, dependency injection
- ☸️ **Kubernetes** : Operateurs, monitoring, networking
- 📊 **Observabilité** : Metrics, logging, tracing

---

**📅 Guide créé** : 2025-01-23  
**🎯 Version** : Jarvis v1.3.2  
**👥 Public** : Développeurs débutants à experts  
**🔄 Mise à jour** : À chaque nouvelle version  

*Ce guide est votre compagnon pour devenir expert sur Jarvis. Bonne contribution ! 🚀*