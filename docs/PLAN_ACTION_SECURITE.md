# 🚨 PLAN D'ACTION SÉCURITÉ JARVIS - 2025

## 📋 RÉSUMÉ EXÉCUTIF

**Date** : 2025-08-20
**Audit** : CRITIQUE - 350+ valeurs hardcodées identifiées  
**Priorité** : **URGENTE** - Sécurisation requise avant production  

### 🎯 OBJECTIF PRINCIPAL
Transformer Jarvis d'un prototype local hardcodé en système de production sécurisé, configurable et scalable.

### ⚠️ RISQUES ACTUELS CRITIQUES
- **Déploiement impossible** sur autres infrastructures
- **API publique non sécurisée** sans authentification  
- **Vulnérabilité DoS** par absence de rate limiting
- **Configuration figée** empêchant la maintenance

---

## 🚨 PHASE 1: SÉCURITÉ CRITIQUE (3 JOURS)

### **JOUR 1: CONFIGURATION RÉSEAU DYNAMIQUE**

#### **🔧 Variables d'environnement - Toutes les IPs**
```bash
# /home/enzo/Projet-Jarvis/.env - Ajouter section réseau
cat >> .env << 'EOF'

# =====================================
# CONFIGURATION RÉSEAU DOCKER DYNAMIQUE
# =====================================
# Network Core
DOCKER_SUBNET=172.20.0.0/16
DOCKER_GATEWAY=172.20.0.1

# Services IPs - Configurables
STT_API_IP=172.20.0.10
TTS_API_IP=172.20.0.20
OLLAMA_IP=172.20.0.30
BACKEND_IP=172.20.0.40
INTERFACE_IP=172.20.0.50
POSTGRES_IP=172.20.0.100
REDIS_IP=172.20.0.110
QDRANT_IP=172.20.0.120
TIMESCALE_IP=172.20.0.130

# Ports - Configurables
STT_API_PORT=8003
TTS_API_PORT=8002
BACKEND_PORT=8000
INTERFACE_PORT=3000
WEBSOCKET_PORT=8001
POSTGRES_PORT=5432
REDIS_PORT=6379
OLLAMA_PORT=11434
QDRANT_HTTP_PORT=6333
QDRANT_GRPC_PORT=6334
EOF
```

#### **🐳 Docker Compose - Variables partout**
```bash
# Sauvegarde
cp docker-compose.yml docker-compose.yml.backup

# Remplacement automatisé des IPs hardcodées
sed -i 's/172\.20\.0\.10/${STT_API_IP}/g' docker-compose.yml
sed -i 's/172\.20\.0\.20/${TTS_API_IP}/g' docker-compose.yml  
sed -i 's/172\.20\.0\.30/${OLLAMA_IP}/g' docker-compose.yml
sed -i 's/172\.20\.0\.40/${BACKEND_IP}/g' docker-compose.yml
sed -i 's/172\.20\.0\.50/${INTERFACE_IP}/g' docker-compose.yml
sed -i 's/172\.20\.0\.100/${POSTGRES_IP}/g' docker-compose.yml
sed -i 's/172\.20\.0\.110/${REDIS_IP}/g' docker-compose.yml
sed -i 's/172\.20\.0\.120/${QDRANT_IP}/g' docker-compose.yml
sed -i 's/172\.20\.0\.130/${TIMESCALE_IP}/g' docker-compose.yml

# Remplacement subnet et gateway  
sed -i 's/172\.20\.0\.0\/16/${DOCKER_SUBNET}/g' docker-compose.yml
sed -i 's/172\.20\.0\.1/${DOCKER_GATEWAY}/g' docker-compose.yml

# Remplacement ports hardcodés
sed -i 's/"8003:8003"/"${STT_API_PORT}:8003"/g' docker-compose.yml
sed -i 's/"8002:8002"/"${TTS_API_PORT}:8002"/g' docker-compose.yml
sed -i 's/"8000:8000"/"${BACKEND_PORT}:8000"/g' docker-compose.yml
sed -i 's/"3000:8000"/"${INTERFACE_PORT}:8000"/g' docker-compose.yml
sed -i 's/"11434:11434"/"${OLLAMA_PORT}:11434"/g' docker-compose.yml
```

#### **📝 Scripts shell - Variables partout**
```bash
# Identifier tous les scripts avec IPs hardcodées
grep -r "172\.20\.0\." scripts/ | cut -d: -f1 | sort -u

# Correction automatisée des scripts principaux
for script in scripts/*.sh; do
    sed -i 's/172\.20\.0\.10/${STT_API_IP}/g' "$script"
    sed -i 's/172\.20\.0\.20/${TTS_API_IP}/g' "$script"  
    sed -i 's/172\.20\.0\.30/${OLLAMA_IP}/g' "$script"
    sed -i 's/172\.20\.0\.40/${BACKEND_IP}/g' "$script"
    sed -i 's/8000/${BACKEND_PORT}/g' "$script"
    sed -i 's/8003/${STT_API_PORT}/g' "$script"
    sed -i 's/8002/${TTS_API_PORT}/g' "$script"
done
```

#### **🧪 Tests configuration dynamique**
```bash
# Test avec configuration alternative
export DOCKER_SUBNET=192.168.100.0/24
export DOCKER_GATEWAY=192.168.100.1  
export BACKEND_IP=192.168.100.40
export BACKEND_PORT=9000

# Validation déploiement alternatif
docker-compose config | grep -E "192\.168\.100|9000"
```

---

### **JOUR 2: AUTHENTIFICATION OAUTH 2.1**

#### **📦 Dépendances sécurité**
```bash
# backend/requirements.txt - Ajouter
cat >> backend/requirements.txt << 'EOF'
# Security & Authentication
fastapi-users[oauth]==12.1.2
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
slowapi==0.1.9
python-multipart==0.0.6
EOF

cd backend && pip install -r requirements.txt
```

#### **🔐 Module authentification**
```bash
mkdir -p backend/auth
```

```python
# backend/auth/__init__.py
from .oauth import *
from .models import *
from .dependencies import *
```

```python
# backend/auth/models.py
from fastapi_users import schemas
from pydantic import BaseModel
from typing import Optional
import uuid

class UserRead(schemas.BaseUser[uuid.UUID]):
    username: str
    
class UserCreate(schemas.BaseUserCreate):
    username: str
    
class UserUpdate(schemas.BaseUserUpdate):
    username: Optional[str] = None
    
class LoginRequest(BaseModel):
    username: str
    password: str
```

```python
# backend/auth/oauth.py
import os
import uuid
from fastapi import Depends
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTAuthentication
)
from fastapi_users.db import SQLAlchemyUserDatabase
from .models import UserRead, UserCreate, UserUpdate

# JWT Configuration
SECRET = os.getenv("JARVIS_SECRET_KEY")
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")
jwt_authentication = JWTAuthentication(
    secret=SECRET,
    lifetime_seconds=3600,
    tokenUrl="auth/jwt/login"
)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=lambda: jwt_authentication
)

# FastAPI Users instance
fastapi_users = FastAPIUsers[UserRead, uuid.UUID](
    get_user_manager=get_user_manager,  # À implémenter
    auth_backends=[auth_backend]
)

current_active_user = fastapi_users.current_user(active=True)
```

#### **🛡️ Sécurisation API principale**
```python
# backend/main.py - Modifications sécurité
from fastapi.security import HTTPBearer
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from auth.oauth import current_active_user
from auth.models import UserRead

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Sécurisation endpoint chat
@app.post("/chat", response_model=ChatResponse)  
@limiter.limit("10/minute")
async def chat_endpoint(
    request: Request,
    chat_request: ChatMessage,
    current_user: UserRead = Depends(current_active_user)
):
    # Validation utilisateur authentifié
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Traitement sécurisé avec user_id validé
    response_text = await process_message_simple(
        chat_request.message, 
        str(current_user.id)  # User ID sécurisé
    )
    
    return ChatResponse(
        response=response_text,
        timestamp=datetime.now().isoformat(),
        user_id=str(current_user.id)
    )
```

---

### **JOUR 3: VALIDATION ET TESTS SÉCURITÉ**

#### **✅ Tests authentification**
```bash
# Test login/logout
curl -X POST http://localhost:8100/auth/jwt/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=enzo&password=secure_password"

# Test endpoint protégé  
curl -X POST http://localhost:8100/chat \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Test sécurisé"}'
```

#### **🔒 CORS sécurisé**
```python
# backend/main.py - CORS strict
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        os.getenv("FRONTEND_URL", "http://localhost:3000")
    ],  # ❌ Plus de ["*"]
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Méthodes spécifiques
    allow_headers=["Authorization", "Content-Type"],  # Headers spécifiques
)
```

#### **📊 Monitoring sécurité basique**
```python
# backend/security/monitoring.py
import logging
from functools import wraps
from fastapi import Request

security_logger = logging.getLogger("jarvis.security")

def log_security_event(event_type: str, details: dict):
    """Log événements sécurité"""
    security_logger.warning(f"[SECURITY] {event_type}: {details}")

def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Handler dépassement rate limit"""
    log_security_event("RATE_LIMIT_EXCEEDED", {
        "client_ip": request.client.host,
        "path": request.url.path,
        "limit": exc.detail
    })
    return {"error": "Rate limit exceeded", "retry_after": 60}
```

---

## ⚡ PHASE 2: MONITORING ET ROBUSTESSE (1 SEMAINE)

### **JOUR 4-5: MONITORING AVANCÉ**

#### **📊 Stack Prometheus + Grafana**
```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus:latest
    container_name: jarvis_prometheus
    networks: [jarvis_network]  
    ports: ["9090:9090"]
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'

  grafana:
    image: grafana/grafana:latest
    container_name: jarvis_grafana
    networks: [jarvis_network]
    ports: ["3001:3000"]  
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      
volumes:
  prometheus_data:
  grafana_data:
```

#### **📈 Métriques backend**
```python
# backend/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time

# Métriques applicatives
REQUEST_COUNT = Counter('jarvis_requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('jarvis_request_duration_seconds', 'Request latency')
ACTIVE_USERS = Gauge('jarvis_active_users', 'Active users')
MEMORY_OPERATIONS = Counter('jarvis_memory_operations_total', 'Memory operations', ['operation'])

def track_request(endpoint: str, method: str = "POST"):
    """Décorateur métriques requêtes"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            REQUEST_COUNT.labels(method=method, endpoint=endpoint).inc()
            
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                REQUEST_LATENCY.observe(time.time() - start_time)
        return wrapper
    return decorator

# backend/main.py - Intégration métriques
from monitoring.metrics import track_request, ACTIVE_USERS

@app.post("/chat")
@track_request("chat")
@limiter.limit("10/minute")
async def chat_endpoint(...):
    ACTIVE_USERS.inc()
    try:
        # Traitement chat
        pass
    finally:
        ACTIVE_USERS.dec()
```

### **JOUR 6-7: LOGGING ET ALERTING**

#### **📝 Logging centralisé**
```python
# backend/logging_config.py - Amélioration
import structlog
import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
            'level': 'INFO'
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': '/app/logs/jarvis.log',
            'formatter': 'json',
            'level': 'DEBUG'
        },
        'security': {
            'class': 'logging.FileHandler', 
            'filename': '/app/logs/security.log',
            'formatter': 'json',
            'level': 'WARNING'
        }
    },
    'loggers': {
        'jarvis.security': {
            'handlers': ['security', 'console'],
            'level': 'WARNING',
            'propagate': False
        }
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO'
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
```

#### **🚨 Alerting automatique**
```python
# backend/alerting/alerts.py
import smtplib
import os
from email.mime.text import MIMEText

class AlertManager:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_user = os.getenv("SMTP_USER") 
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.alert_email = os.getenv("ALERT_EMAIL", "enzo@example.com")
    
    async def send_security_alert(self, event_type: str, details: dict):
        """Envoi alerte sécurité critique"""
        if event_type in ["RATE_LIMIT_EXCEEDED", "UNAUTHORIZED_ACCESS", "SYSTEM_ERROR"]:
            subject = f"🚨 [JARVIS] Alerte sécurité: {event_type}"
            body = f"""
            Événement sécurité détecté:
            Type: {event_type}
            Détails: {details}
            Timestamp: {datetime.now().isoformat()}
            
            Action requise: Vérifier les logs de sécurité
            """
            
            await self._send_email(subject, body)
    
    async def _send_email(self, subject: str, body: str):
        """Envoi email alerte"""
        try:
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = self.smtp_user
            msg['To'] = self.alert_email
            
            with smtplib.SMTP(self.smtp_server, 587) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
        except Exception as e:
            logging.error(f"Erreur envoi alerte: {e}")
```

---

## 🚀 PHASE 3: SCALABILITÉ ET CI/CD (1 MOIS)

### **SEMAINE 1-2: KUBERNETES PRODUCTION**

#### **☸️ Manifests K8s améliorés**
```yaml
# k8s/02-configmap-secrets.yaml - Remplacer hardcoded
apiVersion: v1
kind: ConfigMap
metadata:
  name: jarvis-config
  namespace: jarvis
data:
  DOCKER_SUBNET: "172.20.0.0/16"
  DOCKER_GATEWAY: "172.20.0.1"
  STT_API_IP: "172.20.0.10"
  # ... toutes les variables dynamiques
---
apiVersion: v1
kind: Secret
metadata:
  name: jarvis-secrets
  namespace: jarvis
type: Opaque
data:
  POSTGRES_PASSWORD: <base64-encoded>
  JARVIS_SECRET_KEY: <base64-encoded>
  BROWSERBASE_API_KEY: <base64-encoded>
```

#### **🔄 Auto-scaling HPA**
```yaml
# k8s/14-autoscaling.yaml - Nouveau
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: jarvis-backend-hpa
  namespace: jarvis
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: jarvis-backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource  
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### **SEMAINE 3-4: CI/CD SÉCURISÉ**

#### **🔄 Pipeline GitHub Actions**
```yaml
# .github/workflows/security-deploy.yml
name: Jarvis Security & Deploy
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Security Scan - Trivy
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        format: 'sarif'
        output: 'trivy-results.sarif'
        
    - name: Security Scan - Bandit  
      run: |
        pip install bandit
        bandit -r backend/ -f json -o bandit-report.json
        
    - name: Dependency Check
      uses: dependency-check/Dependency-Check_Action@main
      with:
        project: 'jarvis'
        path: '.'
        format: 'JSON'
        
  tests:
    needs: security-scan
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
        
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install pytest pytest-cov
        
    - name: Run tests
      run: |
        cd backend
        pytest --cov=. --cov-report=xml --cov-report=html
        
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      
  build-deploy:
    needs: [security-scan, tests]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker images
      run: |
        docker-compose build
        docker-compose push  # Si registry configuré
        
    - name: Deploy to staging
      run: |
        # Déploiement automatisé staging
        kubectl apply -f k8s/ --namespace=jarvis-staging
        
    - name: Integration tests  
      run: |
        # Tests E2E sur staging
        ./tests/e2e/run_integration_tests.sh
        
    - name: Deploy to production
      if: success()
      run: |
        kubectl apply -f k8s/ --namespace=jarvis-production
```

---

## 📊 MÉTRIQUES DE SUCCÈS

### **🎯 Objectifs Phase 1 (3 jours)**
- ✅ **0 valeur hardcodée** dans docker-compose.yml
- ✅ **Authentification OAuth** sur tous endpoints sensibles  
- ✅ **Rate limiting** 10 req/min configuré
- ✅ **Tests déploiement** sur 2 environnements différents

### **📈 Objectifs Phase 2 (1 semaine)**
- ✅ **Monitoring** Prometheus + Grafana opérationnel
- ✅ **Alerting** automatique sur événements critiques
- ✅ **Logs centralisés** avec rotation automatique
- ✅ **Tests** coverage > 85% backend

### **🚀 Objectifs Phase 3 (1 mois)**  
- ✅ **K8s production** avec auto-scaling
- ✅ **Pipeline CI/CD** avec security scans
- ✅ **Zéro-downtime** déploiements
- ✅ **Monitoring business** métriques utilisateur

---

## 🚨 CHECKLIST VALIDATION

### **✅ Sécurité Critique Résolue**
- [ ] Toutes IPs configurables via variables env
- [ ] Tous ports configurables via variables env  
- [ ] OAuth 2.1 + JWT sur endpoints sensibles
- [ ] Rate limiting Redis 10 req/min par IP
- [ ] CORS stricte origins spécifiques
- [ ] Secrets management avec rotation
- [ ] Monitoring sécurité + alerting

### **✅ Déploiement Multi-Environnement**
- [ ] Test déploiement dev (192.168.x.x)
- [ ] Test déploiement staging (10.x.x.x)  
- [ ] Test déploiement production (différent)
- [ ] Rollback automatique si échec
- [ ] Health checks optimisés (60s intervals)

### **✅ Qualité et Robustesse**
- [ ] Tests unitaires coverage > 90%
- [ ] Tests intégration E2E automatisés
- [ ] Monitoring Prometheus opérationnel
- [ ] Alerting automatique configuré
- [ ] Documentation API à jour
- [ ] Logs centralisés avec retention

---

## 🎯 RÉSULTAT ATTENDU

### **AVANT (État Actuel)**
```yaml
❌ 350+ valeurs hardcodées
❌ API publique non sécurisée  
❌ Déploiement sur 1 seul environnement
❌ Aucun monitoring/alerting
❌ Configuration manuelle complète
```

### **APRÈS (Objectif 1 Mois)**
```yaml
✅ 0 valeur hardcodée - Configuration 100% dynamique
✅ API sécurisée OAuth 2.1 + rate limiting
✅ Déploiement multi-environnement automatisé  
✅ Monitoring complet + alerting temps réel
✅ CI/CD sécurisé avec tests automatisés
✅ Auto-scaling K8s production-ready
✅ Jarvis prêt pour production industrielle
```

---

**Date de création** : 2025-08-20 16:45  
**Priorité** : **CRITIQUE - COMMENCER IMMÉDIATEMENT**  
**Estimation** : 3 jours Phase 1, 1 semaine Phase 2, 1 mois Phase 3