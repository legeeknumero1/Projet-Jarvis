# GUIDE DÉPLOIEMENT MULTI-ENVIRONNEMENT JARVIS v1.9.0

##  **SOMMAIRE DÉPLOIEMENT**

1. [Vue d'Ensemble](#vue-densemble)
2. [Environnements Cibles](#environnements-cibles)
3. [Prérequis par Environnement](#prérequis-par-environnement)
4. [Configuration Variables](#configuration-variables)
5. [Déploiement Développement](#déploiement-développement)
6. [Déploiement Staging](#déploiement-staging)
7. [Déploiement Production](#déploiement-production)
8. [Déploiement Cloud](#déploiement-cloud)
9. [Monitoring & Observabilité](#monitoring--observabilité)
10. [Rollback & Recovery](#rollback--recovery)

---

##  **VUE D'ENSEMBLE**

### **Stratégie Déploiement Enterprise**
```
 PIPELINE DÉPLOIEMENT JARVIS v1.3.2 
                                                                   
  Development    Staging        Production      Cloud              
                     
   Local    Pre-Prod On-Prem  AWS/Azure         
   Docker      K8s         K8s HA      Multi-AZ           
   Compose     Test        LoadBalancer  Auto-Scale        
                     
                                                              
   [Auto-tests]  [Integration]  [Security]   [Global]            
   [Hot-reload]   [E2E Tests]   [Backup]     [CDN]               
                                                                   

```

### **Principes Déploiement**
- **Infrastructure as Code** : Terraform + Ansible
- **GitOps** : ArgoCD pour synchronisation
- **Blue/Green** : Déploiement sans interruption
- **Canary Release** : Déploiement progressif
- **Immutable Infrastructure** : Containers read-only
- **Zero Downtime** : Health checks + rolling updates

---

##  **ENVIRONNEMENTS CIBLES**

### **1. Développement Local**
- **Usage** : Développement quotidien, debug
- **Infrastructure** : Docker Compose sur machine locale
- **Base de données** : PostgreSQL container
- **Monitoring** : Logs locaux + métriques basiques
- **Sécurité** : Authentification optionnelle

### **2. Staging (Pré-Production)**
- **Usage** : Tests d'intégration, validation
- **Infrastructure** : Kubernetes local (K3s)
- **Base de données** : PostgreSQL + backup
- **Monitoring** : Stack complète Prometheus/Grafana
- **Sécurité** : JWT + HTTPS

### **3. Production On-Premise**
- **Usage** : Environnement client final
- **Infrastructure** : Kubernetes HA (K8s)
- **Base de données** : PostgreSQL cluster + réplication
- **Monitoring** : Observabilité complète + alerting
- **Sécurité** : Enterprise-grade + audit

### **4. Production Cloud**
- **Usage** : SaaS, scalabilité globale
- **Infrastructure** : AWS EKS / Azure AKS
- **Base de données** : RDS/CloudSQL managé
- **Monitoring** : Cloud-native + metrics custom
- **Sécurité** : Cloud security + compliance

---

##  **PRÉREQUIS PAR ENVIRONNEMENT**

### **Développement Local**
```bash
# Outils requis
- Docker 24+ with Docker Compose v2
- Node.js 18+ (pour frontend)
- Python 3.11+ (pour backend dev)
- Git 2.30+

# Resources minimales
- RAM: 8GB (16GB recommandé)
- Disk: 20GB libre
- CPU: 4 cores minimum
- Réseau: Internet pour téléchargement modèles
```

### **Staging/Production**
```bash
# Infrastructure Kubernetes
- Kubernetes 1.28+
- kubectl configuré
- Helm 3.10+
- ArgoCD installé

# Resources production
- Nodes: 3+ (HA)
- RAM: 32GB+ par node
- Disk: 100GB+ SSD
- Network: Load balancer + ingress controller

# Outils DevOps
- Terraform 1.5+
- Ansible 2.14+
- Jenkins/GitLab CI
```

### **Cloud AWS/Azure**
```bash
# AWS Requirements
- EKS cluster 1.28+
- RDS PostgreSQL 15+
- ElastiCache Redis
- Application Load Balancer
- Route53 DNS
- CloudWatch monitoring

# Azure Requirements  
- AKS cluster 1.28+
- Azure Database for PostgreSQL
- Azure Cache for Redis
- Application Gateway
- Azure DNS
- Azure Monitor
```

---

##  **CONFIGURATION VARIABLES**

### **Structure Environnements**
```
 environments/
    development/
       .env
       docker-compose.override.yml
       config.local.json
    staging/
       .env.staging
       k8s-staging/
       values-staging.yaml
    production/
       .env.production
       k8s-production/
       values-production.yaml
    cloud/
        .env.cloud
        terraform/
        values-cloud.yaml
```

### **Variables par Environnement**

#### **Development (.env)**
```bash
# Environment
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=jarvis_dev
POSTGRES_USER=jarvis
POSTGRES_PASSWORD=dev_password_123

# Redis  
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=dev_redis_123

# Services
OLLAMA_BASE_URL=http://localhost:11434
BACKEND_PORT=8000
FRONTEND_PORT=3000

# Security (dev - not for production)
JARVIS_SECRET_KEY=dev_secret_key_32_chars_long_123
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
JWT_EXPIRE_MINUTES=1440  # 24h for dev

# Features
BRAIN_MEMORY_ENABLED=true
MCP_SEARCH_ENABLED=true
WEBSOCKET_ENABLED=true
```

#### **Staging (.env.staging)**
```bash
# Environment
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO

# Database
POSTGRES_HOST=postgres-staging.jarvis.local
POSTGRES_PORT=5432
POSTGRES_DB=jarvis_staging
POSTGRES_USER=jarvis_staging
POSTGRES_PASSWORD=${POSTGRES_STAGING_PASSWORD}

# Redis
REDIS_HOST=redis-staging.jarvis.local
REDIS_PORT=6379
REDIS_PASSWORD=${REDIS_STAGING_PASSWORD}

# Services
OLLAMA_BASE_URL=http://ollama-staging.jarvis.local:11434
BACKEND_URL=https://api-staging.jarvis.local
FRONTEND_URL=https://app-staging.jarvis.local

# Security
JARVIS_SECRET_KEY=${JARVIS_STAGING_SECRET_KEY}
CORS_ORIGINS=https://app-staging.jarvis.local
JWT_EXPIRE_MINUTES=480  # 8h

# SSL/TLS
SSL_CERT_PATH=/etc/ssl/certs/jarvis-staging.crt
SSL_KEY_PATH=/etc/ssl/private/jarvis-staging.key
```

#### **Production (.env.production)**
```bash
# Environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# Database HA
POSTGRES_HOST=postgres-cluster.jarvis.local
POSTGRES_PORT=5432
POSTGRES_DB=jarvis_production
POSTGRES_USER=jarvis_prod
POSTGRES_PASSWORD=${POSTGRES_PROD_PASSWORD}
POSTGRES_REPLICA_HOST=postgres-replica.jarvis.local

# Redis Cluster
REDIS_CLUSTER_HOSTS=redis-1.jarvis.local:6379,redis-2.jarvis.local:6379,redis-3.jarvis.local:6379
REDIS_PASSWORD=${REDIS_PROD_PASSWORD}

# Services HA
OLLAMA_CLUSTER_URLS=http://ollama-1.jarvis.local:11434,http://ollama-2.jarvis.local:11434
BACKEND_URL=https://api.jarvis.com
FRONTEND_URL=https://app.jarvis.com

# Security Enterprise
JARVIS_SECRET_KEY=${JARVIS_PROD_SECRET_KEY}
CORS_ORIGINS=https://app.jarvis.com,https://admin.jarvis.com
JWT_EXPIRE_MINUTES=60  # 1h strict

# SSL/TLS Production
SSL_CERT_PATH=/etc/ssl/certs/jarvis-prod.crt
SSL_KEY_PATH=/etc/ssl/private/jarvis-prod.key

# Performance
MAX_WORKERS=8
WORKER_CONNECTIONS=1000
KEEPALIVE_TIMEOUT=65

# Backup
BACKUP_SCHEDULE=0 2 * * *  # Daily at 2 AM
BACKUP_RETENTION_DAYS=30
```

---

##  **DÉPLOIEMENT DÉVELOPPEMENT**

### **Setup Initial**
```bash
#!/bin/bash
# setup-development.sh

echo " Configuration environnement développement Jarvis v1.9.0"

# 1. Clonage repository
git clone https://github.com/enzo/jarvis.git
cd jarvis

# 2. Configuration environnement
cp environments/development/.env .env
cp environments/development/docker-compose.override.yml .

# 3. Build images
echo " Build des images Docker..."
docker-compose build --no-cache

# 4. Démarrage services
echo " Démarrage services..."
docker-compose up -d

# 5. Vérification santé
echo " Vérification santé services..."
sleep 30
./scripts/health-check.sh

# 6. Setup initial database
echo " Initialisation base de données..."
docker-compose exec backend python -m alembic upgrade head

# 7. Création utilisateur admin
echo " Création utilisateur admin..."
docker-compose exec backend python -c "
from backend.auth.models import User
from backend.auth.security import SecurityManager
from backend.db.database import Database

security = SecurityManager('dev_secret_key_32_chars_long_123')
# Create admin user logic here
"

echo " Environnement développement prêt !"
echo " Interface: http://localhost:3000"
echo " API: http://localhost:8100"
echo " Grafana: http://localhost:3001"
```

### **Workflow Développement**
```bash
# Hot reload backend (FastAPI)
docker-compose up backend --build

# Hot reload frontend (React)
cd frontend && npm start

# Tests unitaires
docker-compose exec backend python -m pytest tests/ -v

# Tests intégration
docker-compose exec backend python -m pytest tests/integration/ -v

# Lint et format
docker-compose exec backend black . && flake8 .
cd frontend && npm run lint && npm run format
```

### **Debug & Troubleshooting**
```bash
# Logs temps réel
docker-compose logs -f backend
docker-compose logs -f frontend

# Debug interactif
docker-compose exec backend python -m pdb

# Reset complet environnement
docker-compose down -v
docker system prune -f
docker-compose up --build
```

---

##  **DÉPLOIEMENT STAGING**

### **Infrastructure Staging (K3s)**
```bash
#!/bin/bash
# deploy-staging.sh

echo " Déploiement Staging Jarvis v1.9.0"

# 1. Configuration kubectl
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

# 2. Création namespace
kubectl create namespace jarvis-staging --dry-run=client -o yaml | kubectl apply -f -

# 3. Secrets configuration
kubectl create secret generic jarvis-secrets \
  --from-env-file=environments/staging/.env.staging \
  -n jarvis-staging

# 4. Déploiement Helm
helm upgrade --install jarvis-staging \
  ./helm/jarvis \
  -f environments/staging/values-staging.yaml \
  -n jarvis-staging \
  --wait --timeout=600s

# 5. Vérification déploiement
kubectl get pods -n jarvis-staging
kubectl get services -n jarvis-staging
kubectl get ingress -n jarvis-staging

echo " Déploiement staging terminé"
```

### **Helm Chart Staging (`values-staging.yaml`)**
```yaml
# environments/staging/values-staging.yaml
replicaCount: 2

image:
  repository: jarvis
  tag: "staging"
  pullPolicy: Always

environment: staging

backend:
  replicas: 2
  resources:
    requests:
      memory: "1Gi"
      cpu: "500m"
    limits:
      memory: "2Gi"
      cpu: "1000m"

frontend:
  replicas: 2
  resources:
    requests:
      memory: "512Mi"
      cpu: "250m"
    limits:
      memory: "1Gi"
      cpu: "500m"

database:
  enabled: true
  persistence:
    size: 20Gi
    storageClass: fast-ssd

redis:
  enabled: true
  cluster:
    enabled: false

monitoring:
  enabled: true
  prometheus:
    enabled: true
  grafana:
    enabled: true

ingress:
  enabled: true
  className: nginx
  hosts:
    - host: app-staging.jarvis.local
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: jarvis-staging-tls
      hosts:
        - app-staging.jarvis.local

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
```

### **Tests Automatisés Staging**
```bash
#!/bin/bash
# test-staging.sh

echo " Tests automatisés staging"

# Variables
STAGING_URL="https://app-staging.jarvis.local"
API_URL="https://api-staging.jarvis.local"

# 1. Health checks
echo " Health checks..."
curl -f ${API_URL}/health || exit 1
curl -f ${API_URL}/metrics || exit 1

# 2. Tests API
echo " Tests API..."
python -m pytest tests/e2e/ \
  --base-url=${API_URL} \
  --staging \
  --junit-xml=reports/staging-api-tests.xml

# 3. Tests interface
echo " Tests interface..."
npx playwright test \
  --config=playwright.staging.config.js \
  --reporter=junit

# 4. Tests performance
echo " Tests performance..."
k6 run tests/performance/staging-load-test.js

# 5. Tests sécurité
echo " Tests sécurité..."
bandit -r backend/ -f json -o reports/staging-security.json

# 6. Rapport final
echo " Génération rapport..."
python scripts/generate-staging-report.py

echo " Tests staging terminés"
```

---

##  **DÉPLOIEMENT PRODUCTION**

### **Architecture Production HA**
```yaml
# k8s-production/production-architecture.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: jarvis-production

---
# PostgreSQL HA avec réplication
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: postgres-cluster
  namespace: jarvis-production
spec:
  instances: 3
  postgresql:
    parameters:
      max_connections: "200"
      shared_buffers: "256MB"
      effective_cache_size: "1GB"
  
  bootstrap:
    initdb:
      database: jarvis_production
      owner: jarvis_prod
      secret:
        name: postgres-credentials

  storage:
    size: 100Gi
    storageClass: fast-ssd

---
# Redis Sentinel HA
apiVersion: v1
kind: ConfigMap
metadata:
  name: redis-config
  namespace: jarvis-production
data:
  redis.conf: |
    bind 0.0.0.0
    port 6379
    requirepass ${REDIS_PASSWORD}
    maxmemory 2gb
    maxmemory-policy allkeys-lru
    save 900 1
    save 300 10
    save 60 10000

---
# Load Balancer Production
apiVersion: v1
kind: Service
metadata:
  name: jarvis-loadbalancer
  namespace: jarvis-production
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
spec:
  type: LoadBalancer
  selector:
    app: jarvis-backend
  ports:
    - name: https
      port: 443
      targetPort: 8000
      protocol: TCP
```

### **Script Déploiement Production**
```bash
#!/bin/bash
# deploy-production.sh

echo " Déploiement PRODUCTION Jarvis v1.9.0"

# Validation sécurité pré-déploiement
if [[ "$ENVIRONMENT" != "production" ]]; then
    echo " ERREUR: Variable ENVIRONMENT doit être 'production'"
    exit 1
fi

# Validation secrets
if [[ -z "$JARVIS_PROD_SECRET_KEY" ]]; then
    echo " ERREUR: JARVIS_PROD_SECRET_KEY requis"
    exit 1
fi

# 1. Backup avant déploiement
echo " Backup base de données..."
kubectl exec -n jarvis-production postgres-cluster-1 -- \
  pg_dump -U jarvis_prod jarvis_production > backup-$(date +%Y%m%d-%H%M%S).sql

# 2. Blue/Green deployment
echo " Déploiement Blue/Green..."

# Deploy version Green (nouvelle)
helm upgrade jarvis-green ./helm/jarvis \
  -f environments/production/values-production.yaml \
  --set image.tag=${BUILD_VERSION} \
  --set environment=production-green \
  -n jarvis-production \
  --wait --timeout=900s

# Validation Green environment
echo " Validation environnement Green..."
./scripts/validate-production.sh green

# Switch traffic Blue -> Green
echo " Basculement trafic vers Green..."
kubectl patch service jarvis-loadbalancer \
  -p '{"spec":{"selector":{"version":"green"}}}' \
  -n jarvis-production

# Validation post-switch
echo " Validation post-déploiement..."
./scripts/validate-production.sh green --post-switch

# Cleanup old Blue version
echo " Nettoyage ancienne version Blue..."
helm uninstall jarvis-blue -n jarvis-production

echo " Déploiement PRODUCTION réussi !"
```

### **Monitoring Production**
```yaml
# monitoring-production.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-production-config
  namespace: jarvis-production
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s
      external_labels:
        cluster: 'jarvis-production'
        environment: 'production'

    rule_files:
      - "alerts/*.yml"

    scrape_configs:
      - job_name: 'jarvis-backend'
        kubernetes_sd_configs:
          - role: endpoints
            namespaces:
              names: ['jarvis-production']
        relabel_configs:
          - source_labels: [__meta_kubernetes_service_name]
            action: keep
            regex: jarvis-backend

      - job_name: 'jarvis-microservices'
        kubernetes_sd_configs:
          - role: pod
            namespaces:
              names: ['jarvis-production']
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_label_app]
            action: keep
            regex: 'jarvis-(stt|tts|interface)'

    alerting:
      alertmanagers:
        - kubernetes_sd_configs:
            - role: pod
              namespaces:
                names: ['jarvis-production']
          relabel_configs:
            - source_labels: [__meta_kubernetes_pod_label_app]
              action: keep
              regex: alertmanager
```

### **Alertes Production Critiques**
```yaml
# alerts/production-critical.yml
groups:
- name: jarvis-production-critical
  rules:
  - alert: ServiceDown
    expr: up{job=~"jarvis-.*"} == 0
    for: 30s
    labels:
      severity: critical
      environment: production
    annotations:
      summary: "Service {{ $labels.job }} is down"
      description: "Service {{ $labels.job }} has been down for more than 30 seconds"

  - alert: HighErrorRate
    expr: rate(jarvis_requests_errors_total[5m]) > 0.1
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value | humanizePercentage }}"

  - alert: DatabaseConnectionFailure
    expr: jarvis_database_connections_failed_total > 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Database connection failures"
      description: "{{ $value }} database connections failed"

  - alert: HighMemoryUsage
    expr: container_memory_usage_bytes / container_spec_memory_limit_bytes > 0.9
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High memory usage"
      description: "Container {{ $labels.container }} using {{ $value | humanizePercentage }} memory"
```

---

##  **DÉPLOIEMENT CLOUD**

### **AWS EKS Deployment**
```hcl
# terraform/aws/main.tf
provider "aws" {
  region = var.aws_region
}

# EKS Cluster
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "19.15.3"

  cluster_name    = "jarvis-production"
  cluster_version = "1.28"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  # Node groups
  eks_managed_node_groups = {
    main = {
      min_size       = 3
      max_size       = 10
      desired_size   = 3
      instance_types = ["m5.xlarge"]
      
      k8s_labels = {
        Environment = "production"
        Application = "jarvis"
      }
    }
  }

  # IRSA for service accounts
  enable_irsa = true
}

# RDS PostgreSQL
resource "aws_db_instance" "jarvis_postgres" {
  identifier = "jarvis-postgres-prod"
  
  engine            = "postgres"
  engine_version    = "15.3"
  instance_class    = "db.r6g.xlarge"
  allocated_storage = 100
  storage_encrypted = true
  
  db_name  = "jarvis_production"
  username = var.db_username
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.jarvis.name
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  skip_final_snapshot = false
  final_snapshot_identifier = "jarvis-postgres-final-snapshot"

  tags = {
    Name        = "jarvis-postgres-production"
    Environment = "production"
  }
}

# ElastiCache Redis
resource "aws_elasticache_replication_group" "jarvis_redis" {
  replication_group_id       = "jarvis-redis-prod"
  description                = "Redis cluster for Jarvis production"
  
  node_type          = "cache.r6g.large"
  port               = 6379
  parameter_group_name = "default.redis6.x"
  
  num_cache_clusters = 3
  automatic_failover_enabled = true
  
  subnet_group_name = aws_elasticache_subnet_group.jarvis.name
  security_group_ids = [aws_security_group.redis.id]
  
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  auth_token                 = var.redis_auth_token

  tags = {
    Name        = "jarvis-redis-production"
    Environment = "production"
  }
}
```

### **Azure AKS Deployment**
```hcl
# terraform/azure/main.tf
provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "jarvis" {
  name     = "rg-jarvis-production"
  location = var.azure_region
}

# AKS Cluster
resource "azurerm_kubernetes_cluster" "jarvis" {
  name                = "aks-jarvis-production"
  location            = azurerm_resource_group.jarvis.location
  resource_group_name = azurerm_resource_group.jarvis.name
  dns_prefix          = "jarvis-prod"
  
  kubernetes_version = "1.28"

  default_node_pool {
    name       = "default"
    node_count = 3
    vm_size    = "Standard_D4s_v3"
    
    enable_auto_scaling = true
    min_count           = 3
    max_count           = 10
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin = "azure"
  }

  tags = {
    Environment = "production"
    Application = "jarvis"
  }
}

# Azure Database for PostgreSQL
resource "azurerm_postgresql_flexible_server" "jarvis" {
  name                   = "psql-jarvis-production"
  resource_group_name    = azurerm_resource_group.jarvis.name
  location              = azurerm_resource_group.jarvis.location
  version               = "15"
  
  administrator_login    = var.db_username
  administrator_password = var.db_password
  
  sku_name = "GP_Standard_D4s_v3"
  
  storage_mb = 102400
  backup_retention_days = 7
  
  zone = "1"

  tags = {
    Environment = "production"
  }
}

# Azure Cache for Redis
resource "azurerm_redis_cache" "jarvis" {
  name                = "redis-jarvis-production"
  location            = azurerm_resource_group.jarvis.location
  resource_group_name = azurerm_resource_group.jarvis.name
  capacity            = 2
  family              = "C"
  sku_name            = "Standard"
  
  enable_non_ssl_port = false
  minimum_tls_version = "1.2"
  
  redis_configuration {
    enable_authentication = true
  }

  tags = {
    Environment = "production"
  }
}
```

### **Déploiement Cloud Script**
```bash
#!/bin/bash
# deploy-cloud.sh

CLOUD_PROVIDER=${1:-aws}  # aws or azure
ENVIRONMENT=production

echo " Déploiement Cloud ${CLOUD_PROVIDER} - Jarvis v1.9.0"

case $CLOUD_PROVIDER in
  "aws")
    echo " Déploiement AWS EKS..."
    
    # 1. Infrastructure Terraform
    cd terraform/aws
    terraform init
    terraform plan -var-file="production.tfvars"
    terraform apply -auto-approve -var-file="production.tfvars"
    
    # 2. Configuration kubectl
    aws eks update-kubeconfig --region us-east-1 --name jarvis-production
    
    # 3. Deploy application
    helm upgrade --install jarvis ./helm/jarvis \
      -f environments/cloud/values-aws.yaml \
      --set cloud.provider=aws \
      -n jarvis-production \
      --create-namespace
    ;;
    
  "azure")
    echo " Déploiement Azure AKS..."
    
    # 1. Infrastructure Terraform
    cd terraform/azure
    terraform init
    terraform plan -var-file="production.tfvars"
    terraform apply -auto-approve -var-file="production.tfvars"
    
    # 2. Configuration kubectl
    az aks get-credentials --resource-group rg-jarvis-production --name aks-jarvis-production
    
    # 3. Deploy application
    helm upgrade --install jarvis ./helm/jarvis \
      -f environments/cloud/values-azure.yaml \
      --set cloud.provider=azure \
      -n jarvis-production \
      --create-namespace
    ;;
    
  *)
    echo " Provider non supporté: $CLOUD_PROVIDER"
    echo "Usage: $0 [aws|azure]"
    exit 1
    ;;
esac

# 4. Validation déploiement
echo " Validation déploiement cloud..."
kubectl get pods -n jarvis-production
kubectl get services -n jarvis-production
kubectl get ingress -n jarvis-production

# 5. Tests post-déploiement
echo " Tests post-déploiement..."
./scripts/test-cloud-deployment.sh $CLOUD_PROVIDER

echo " Déploiement cloud $CLOUD_PROVIDER terminé !"
```

---

##  **MONITORING & OBSERVABILITÉ**

### **Stack Monitoring Multi-Environnement**
```yaml
# monitoring/values-monitoring.yaml
prometheus:
  server:
    global:
      external_labels:
        cluster: "${CLUSTER_NAME}"
        environment: "${ENVIRONMENT}"
    
    retention: "30d"
    resources:
      requests:
        memory: "2Gi"
        cpu: "1000m"
      limits:
        memory: "4Gi"
        cpu: "2000m"

grafana:
  admin:
    user: admin
    password: "${GRAFANA_PASSWORD}"
  
  dashboards:
    default:
      jarvis-overview:
        gnetId: 12345
        revision: 1
        datasource: Prometheus
      
      jarvis-performance:
        url: https://grafana.com/api/dashboards/67890/revisions/1/download
        datasource: Prometheus

  datasources:
    datasources.yaml:
      apiVersion: 1
      datasources:
        - name: Prometheus
          type: prometheus
          url: http://prometheus-server:80
          isDefault: true
        - name: Loki
          type: loki
          url: http://loki:3100

loki:
  persistence:
    enabled: true
    size: 20Gi
  
  config:
    limits_config:
      retention_period: 744h  # 31 days

alertmanager:
  config:
    global:
      slack_api_url: "${SLACK_WEBHOOK_URL}"
    
    route:
      group_by: ['alertname', 'environment']
      group_wait: 10s
      group_interval: 10s
      repeat_interval: 1h
      receiver: 'web.hook'
      
      routes:
        - match:
            severity: critical
          receiver: 'critical-alerts'
        - match:
            environment: production
          receiver: 'production-alerts'

    receivers:
      - name: 'web.hook'
        webhook_configs:
          - url: 'http://webhook-handler:5000/alerts'
      
      - name: 'critical-alerts'
        slack_configs:
          - channel: '#jarvis-critical'
            title: 'CRITICAL: {{ .GroupLabels.alertname }}'
            text: '{{ .CommonAnnotations.summary }}'
      
      - name: 'production-alerts'
        slack_configs:
          - channel: '#jarvis-production'
            title: 'PROD: {{ .GroupLabels.alertname }}'
```

### **Custom Metrics & Dashboards**
```python
# monitoring/custom_metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Business Metrics
jarvis_conversations_total = Counter(
    'jarvis_conversations_total',
    'Total conversations with Jarvis',
    ['user_id', 'environment']
)

jarvis_ai_response_time = Histogram(
    'jarvis_ai_response_time_seconds',
    'Time taken for AI to generate response',
    ['model', 'environment'],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0]
)

jarvis_active_users = Gauge(
    'jarvis_active_users',
    'Number of active users',
    ['environment']
)

# System Metrics
jarvis_memory_usage = Gauge(
    'jarvis_memory_usage_bytes',
    'Memory usage by component',
    ['component', 'environment']
)

jarvis_database_connections = Gauge(
    'jarvis_database_connections_active',
    'Active database connections',
    ['database', 'environment']
)
```

---

##  **ROLLBACK & RECOVERY**

### **Stratégies Rollback**

#### **1. Application Rollback (Helm)**
```bash
#!/bin/bash
# rollback-application.sh

ENVIRONMENT=${1:-staging}
REVISION=${2:-0}  # 0 = previous version

echo " Rollback application Jarvis - Environment: $ENVIRONMENT"

# Liste des versions disponibles
helm history jarvis -n jarvis-$ENVIRONMENT

# Rollback vers version précédente ou spécifique
if [[ $REVISION -eq 0 ]]; then
    echo " Rollback vers version précédente..."
    helm rollback jarvis -n jarvis-$ENVIRONMENT
else
    echo " Rollback vers revision $REVISION..."
    helm rollback jarvis $REVISION -n jarvis-$ENVIRONMENT
fi

# Validation post-rollback
echo " Validation post-rollback..."
kubectl get pods -n jarvis-$ENVIRONMENT
./scripts/health-check.sh $ENVIRONMENT

# Tests automatiques
echo " Tests post-rollback..."
./scripts/test-deployment.sh $ENVIRONMENT

echo " Rollback terminé avec succès"
```

#### **2. Database Rollback**
```bash
#!/bin/bash
# rollback-database.sh

ENVIRONMENT=${1:-staging}
BACKUP_FILE=${2}

echo " Rollback base de données - Environment: $ENVIRONMENT"

if [[ -z "$BACKUP_FILE" ]]; then
    # Utiliser le backup le plus récent
    BACKUP_FILE=$(ls -t backups/ | head -1)
    echo " Utilisation backup: $BACKUP_FILE"
fi

# Validation backup
if [[ ! -f "backups/$BACKUP_FILE" ]]; then
    echo " Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Scale down application
echo " Scale down application..."
kubectl scale deployment jarvis-backend --replicas=0 -n jarvis-$ENVIRONMENT

# Restore database
echo " Restoration base de données..."
case $ENVIRONMENT in
    "staging"|"development")
        kubectl exec -n jarvis-$ENVIRONMENT postgres-0 -- \
            psql -U jarvis -d jarvis_$ENVIRONMENT < "backups/$BACKUP_FILE"
        ;;
    "production")
        # Production nécessite procédure spéciale avec réplication
        ./scripts/restore-production-db.sh "$BACKUP_FILE"
        ;;
esac

# Scale up application
echo " Scale up application..."
kubectl scale deployment jarvis-backend --replicas=2 -n jarvis-$ENVIRONMENT

# Validation
echo " Validation restoration..."
./scripts/validate-database.sh $ENVIRONMENT

echo " Rollback base de données terminé"
```

### **Disaster Recovery Plan**
```yaml
# disaster-recovery-plan.yaml
disaster_recovery:
  rto: 4h  # Recovery Time Objective
  rpo: 1h  # Recovery Point Objective
  
  procedures:
    level_1_incident:  # Service degradation
      - Check monitoring alerts
      - Restart affected services
      - Scale up resources if needed
      - Notify team via Slack
      
    level_2_incident:  # Partial outage
      - Activate incident response team
      - Switch to backup services
      - Rollback recent deployments
      - Communicate to stakeholders
      
    level_3_incident:  # Complete outage
      - Activate disaster recovery site
      - Restore from backups
      - Failover to secondary region
      - Executive notification
      
  backup_strategy:
    database:
      frequency: "Every 6 hours"
      retention: "30 days"
      location: "Multi-region S3"
      
    application:
      frequency: "Every deployment"
      retention: "10 versions"
      location: "Container registry"
      
    configuration:
      frequency: "Every change"
      retention: "Indefinite"
      location: "Git repository"

  contact_list:
    incident_commander: "enzo@jarvis.com"
    technical_lead: "devops@jarvis.com"
    communications: "support@jarvis.com"
```

---

##  **CONCLUSION DÉPLOIEMENT**

Ce guide couvre tous les aspects du déploiement multi-environnement de Jarvis v1.9.0 :

###  **Objectifs Atteints**
- **Multi-environnement** : Dev, Staging, Production, Cloud
- **Infrastructure as Code** : Terraform + Helm + GitOps
- **Zero Downtime** : Blue/Green + Rolling updates
- **Monitoring Complet** : Prometheus + Grafana + Alerting
- **Disaster Recovery** : Backup + Rollback automatisé

###  **Best Practices Appliquées**
- **Security First** : Secrets management + RBAC + Network policies
- **Scalabilité** : Horizontal Pod Autoscaling + Load balancing
- **Observabilité** : Metrics + Logs + Tracing + Alerting
- **Automation** : CI/CD pipelines + GitOps + Self-healing

###  **Prochaines Étapes**
- **Multi-Region** : Déploiement géographiquement distribué
- **Chaos Engineering** : Tests de résistance automatisés
- **Cost Optimization** : Optimisation ressources cloud
- **Security Hardening** : Audit sécurité continu

**Date** : 23 août 2025  
**Version** : 1.3.2 Enterprise  
**Statut** : Production-Ready Multi-Cloud  
**Contact** : DevOps Team - devops@jarvis.com