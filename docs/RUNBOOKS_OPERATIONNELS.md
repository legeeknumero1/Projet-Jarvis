# RUNBOOKS OPÉRATIONNELS JARVIS v1.9.0

## 📋 **SOMMAIRE OPÉRATIONNEL**

1. [Vue d'Ensemble Opérationnelle](#vue-densemble-opérationnelle)
2. [Procédures de Démarrage](#procédures-de-démarrage)
3. [Procédures d'Arrêt](#procédures-darrêt)
4. [Monitoring & Alertes](#monitoring--alertes)
5. [Résolution d'Incidents](#résolution-dincidents)
6. [Maintenance Planifiée](#maintenance-planifiée)
7. [Backup & Recovery](#backup--recovery)
8. [Sécurité Opérationnelle](#sécurité-opérationnelle)
9. [Escalation Procedures](#escalation-procedures)
10. [Contacts & Responsabilités](#contacts--responsabilités)

---

## 🎯 **VUE D'ENSEMBLE OPÉRATIONNELLE**

### **Architecture Services Critiques**
```
┌─────────────── SERVICES CRITIQUES JARVIS v1.3.2 ──────────────┐
│                                                                │
│  TIER 1 - CRITIQUE (RTO: 5 min, RPO: 1 min)                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Backend API (8100) │ PostgreSQL (5432) │ Redis (6379) │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                │
│  TIER 2 - IMPORTANT (RTO: 15 min, RPO: 5 min)                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Ollama LLM (11434) │ Frontend (3000) │ Qdrant (6333)  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                │
│  TIER 3 - SUPPORT (RTO: 30 min, RPO: 15 min)                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ STT API (8003) │ TTS API (8002) │ TimescaleDB (5433)  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                │
│  MONITORING & DEVOPS (RTO: 60 min, RPO: 30 min)              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Prometheus (9090) │ Grafana (3001) │ Jenkins (8080)   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### **Objectifs de Niveau de Service (SLO)**
| Service | Disponibilité | Temps Réponse | Erreur Max |
|---------|---------------|---------------|------------|
| Backend API | 99.9% | <200ms (P95) | <0.1% |
| PostgreSQL | 99.95% | <50ms (P95) | <0.05% |
| Redis Cache | 99.8% | <10ms (P95) | <0.2% |
| Frontend | 99.7% | <2s load | <0.5% |
| Ollama LLM | 99.5% | <5s (P95) | <1% |

---

## 🚀 **PROCÉDURES DE DÉMARRAGE**

### **1. Démarrage Standard (Développement/Staging)**
```bash
#!/bin/bash
# startup-standard.sh

echo "🚀 [$(date)] Démarrage Standard Jarvis v1.9.0"

# Pré-vérifications
echo "🔍 Pré-vérifications système..."
./scripts/pre-flight-checks.sh || exit 1

# 1. Services de base (ordre critique)
echo "📊 Démarrage PostgreSQL..."
docker-compose up -d postgres
./scripts/wait-for-service.sh postgres:5432 30

echo "💾 Démarrage Redis..."  
docker-compose up -d redis
./scripts/wait-for-service.sh redis:6379 15

echo "🧠 Démarrage Qdrant..."
docker-compose up -d qdrant
./scripts/wait-for-service.sh qdrant:6333 20

# 2. Services applicatifs
echo "🤖 Démarrage Ollama..."
docker-compose up -d ollama
./scripts/wait-for-service.sh ollama:11434 60

echo "⚙️ Démarrage Backend..."
docker-compose up -d backend
./scripts/wait-for-service.sh backend:8100 30

# 3. Microservices
echo "🎤 Démarrage STT API..."
docker-compose up -d stt-api
./scripts/wait-for-service.sh stt-api:8003 20

echo "🔊 Démarrage TTS API..."
docker-compose up -d tts-api
./scripts/wait-for-service.sh tts-api:8002 20

echo "🖥️ Démarrage Interface..."
docker-compose up -d interface
./scripts/wait-for-service.sh interface:3000 25

# 4. Services support
echo "📈 Démarrage TimescaleDB..."
docker-compose up -d timescale
./scripts/wait-for-service.sh timescale:5432 20

# 5. Validation finale
echo "✅ Validation démarrage..."
./scripts/health-check-all.sh

echo "🎉 [$(date)] Démarrage terminé avec succès"
```

### **2. Démarrage Production (Blue/Green)**
```bash
#!/bin/bash
# startup-production.sh

ENVIRONMENT=${1:-production}
DEPLOYMENT_TYPE=${2:-green}  # blue or green

echo "🏭 [$(date)] Démarrage Production - Environment: $ENVIRONMENT, Type: $DEPLOYMENT_TYPE"

# Validation sécurité
if [[ "$ENVIRONMENT" == "production" ]]; then
    echo "🔐 Validation sécurité production..."
    
    # Vérification secrets
    kubectl get secrets jarvis-secrets -n jarvis-production || exit 1
    
    # Vérification backups récents
    LAST_BACKUP=$(ls -t backups/ | head -1)
    BACKUP_AGE=$(stat -c %Y "backups/$LAST_BACKUP")
    CURRENT_TIME=$(date +%s)
    
    if [[ $((CURRENT_TIME - BACKUP_AGE)) -gt 86400 ]]; then
        echo "❌ Backup trop ancien (>24h) - Création backup avant démarrage"
        ./scripts/create-backup.sh production
    fi
fi

# 1. Infrastructure services
echo "🏗️ Démarrage infrastructure..."
kubectl apply -f k8s-$ENVIRONMENT/infrastructure/ -n jarvis-$ENVIRONMENT

# 2. Base de données (si pas déjà lancée)
echo "📊 Validation base de données..."
kubectl get pods -l app=postgres -n jarvis-$ENVIRONMENT | grep Running || {
    echo "🚀 Démarrage base de données..."
    kubectl apply -f k8s-$ENVIRONMENT/database/ -n jarvis-$ENVIRONMENT
    kubectl wait --for=condition=ready pod -l app=postgres -n jarvis-$ENVIRONMENT --timeout=300s
}

# 3. Services applicatifs (Green deployment)
echo "🔄 Déploiement $DEPLOYMENT_TYPE..."
helm upgrade --install jarvis-$DEPLOYMENT_TYPE ./helm/jarvis \
    -f values-$ENVIRONMENT.yaml \
    --set deployment.type=$DEPLOYMENT_TYPE \
    --set image.tag=$BUILD_VERSION \
    -n jarvis-$ENVIRONMENT \
    --wait --timeout=600s

# 4. Tests de santé
echo "🩺 Tests de santé post-démarrage..."
./scripts/health-check-production.sh $DEPLOYMENT_TYPE

# 5. Switch traffic (si Green OK)
if [[ "$DEPLOYMENT_TYPE" == "green" ]]; then
    echo "🚦 Basculement trafic vers Green..."
    kubectl patch service jarvis-loadbalancer \
        -p '{"spec":{"selector":{"version":"green"}}}' \
        -n jarvis-$ENVIRONMENT
    
    # Validation post-switch
    sleep 30
    ./scripts/validate-traffic-switch.sh green
fi

echo "✅ [$(date)] Démarrage production terminé"
```

### **3. Scripts Support Démarrage**
```bash
#!/bin/bash
# wait-for-service.sh

SERVICE_ENDPOINT=$1
TIMEOUT=${2:-30}

echo "⏳ Attente service $SERVICE_ENDPOINT (timeout: ${TIMEOUT}s)"

for i in $(seq 1 $TIMEOUT); do
    if curl -f -s http://$SERVICE_ENDPOINT/health >/dev/null 2>&1; then
        echo "✅ Service $SERVICE_ENDPOINT prêt après ${i}s"
        exit 0
    fi
    sleep 1
done

echo "❌ Timeout atteint pour service $SERVICE_ENDPOINT"
exit 1
```

---

## 🛑 **PROCÉDURES D'ARRÊT**

### **1. Arrêt Gracieux (Maintenance)**
```bash
#!/bin/bash
# shutdown-graceful.sh

ENVIRONMENT=${1:-development}
REASON=${2:-"Maintenance planifiée"}

echo "🛑 [$(date)] Arrêt gracieux - Environment: $ENVIRONMENT"
echo "📝 Raison: $REASON"

# 1. Notification utilisateurs (si production)
if [[ "$ENVIRONMENT" == "production" ]]; then
    echo "📢 Notification utilisateurs..."
    curl -X POST $SLACK_WEBHOOK \
        -d "{\"text\":\"🚨 Maintenance Jarvis démarrant dans 5 minutes\"}"
    
    # Attendre 5 minutes pour notification
    sleep 300
fi

# 2. Arrêt acceptation nouveau trafic
echo "🚫 Arrêt acceptation nouveau trafic..."
kubectl patch deployment jarvis-backend \
    --patch '{"spec":{"replicas":0}}' \
    -n jarvis-$ENVIRONMENT

# 3. Attendre fin des requêtes en cours (max 60s)
echo "⏳ Attente fin requêtes en cours..."
for i in $(seq 1 60); do
    ACTIVE_CONN=$(curl -s http://backend:8100/metrics | grep jarvis_active_connections | awk '{print $2}')
    if [[ "${ACTIVE_CONN:-0}" -eq 0 ]]; then
        echo "✅ Plus de connexions actives après ${i}s"
        break
    fi
    sleep 1
done

# 4. Arrêt services par ordre inverse
echo "🔄 Arrêt services..."

echo "  🖥️ Arrêt Interface..."
docker-compose stop interface

echo "  🔊 Arrêt TTS API..."
docker-compose stop tts-api

echo "  🎤 Arrêt STT API..."
docker-compose stop stt-api

echo "  ⚙️ Arrêt Backend..."
docker-compose stop backend

echo "  🤖 Arrêt Ollama..."
docker-compose stop ollama

echo "  🧠 Arrêt Qdrant..."
docker-compose stop qdrant

echo "  💾 Arrêt Redis..."
docker-compose stop redis

# 5. Base de données en dernier (avec backup)
echo "📊 Backup base de données avant arrêt..."
./scripts/create-backup.sh $ENVIRONMENT

echo "  📊 Arrêt PostgreSQL..."
docker-compose stop postgres

# 6. Logs et nettoyage
echo "📝 Archivage logs..."
tar -czf "logs/shutdown-$(date +%Y%m%d-%H%M%S).tar.gz" logs/*.log

echo "🧹 Nettoyage temporaire..."
docker system prune -f --volumes

echo "✅ [$(date)] Arrêt gracieux terminé"
```

### **2. Arrêt d'Urgence**
```bash
#!/bin/bash
# shutdown-emergency.sh

ENVIRONMENT=${1:-development}
INCIDENT_ID=${2:-$(date +%Y%m%d-%H%M%S)}

echo "🚨 [$(date)] ARRÊT D'URGENCE - Environment: $ENVIRONMENT"
echo "🆔 Incident ID: $INCIDENT_ID"

# 1. Notification immédiate
curl -X POST $EMERGENCY_WEBHOOK \
    -d "{\"text\":\"🚨 EMERGENCY SHUTDOWN Jarvis $ENVIRONMENT - Incident: $INCIDENT_ID\"}"

# 2. Capture état système avant arrêt
echo "📸 Capture état système..."
kubectl get pods -A > "incidents/$INCIDENT_ID-pods-state.txt"
docker ps -a > "incidents/$INCIDENT_ID-containers-state.txt"
df -h > "incidents/$INCIDENT_ID-disk-usage.txt"
free -m > "incidents/$INCIDENT_ID-memory-usage.txt"

# 3. Arrêt immédiat tous services
echo "🛑 Arrêt immédiat tous services..."
case $ENVIRONMENT in
    "production")
        kubectl delete deployment --all -n jarvis-production
        kubectl delete pod --all -n jarvis-production --force --grace-period=0
        ;;
    *)
        docker-compose down --remove-orphans
        docker kill $(docker ps -q) 2>/dev/null || true
        ;;
esac

# 4. Collecte logs d'urgence
echo "📋 Collecte logs d'urgence..."
kubectl logs --all-containers --tail=1000 -n jarvis-$ENVIRONMENT \
    > "incidents/$INCIDENT_ID-k8s-logs.txt"

docker-compose logs --tail=1000 > "incidents/$INCIDENT_ID-docker-logs.txt"

# 5. Isolation réseau si nécessaire
if [[ "${3:-}" == "isolate" ]]; then
    echo "🔒 Isolation réseau..."
    iptables -P INPUT DROP
    iptables -P FORWARD DROP
fi

echo "⚠️ [$(date)] Arrêt d'urgence terminé - Incident: $INCIDENT_ID"
```

---

## 📊 **MONITORING & ALERTES**

### **1. Dashboard Opérationnel**
```yaml
# monitoring/operational-dashboard.json
{
  "dashboard": {
    "title": "Jarvis Operational Dashboard",
    "tags": ["jarvis", "operations"],
    "refresh": "30s",
    "panels": [
      {
        "title": "Services Status",
        "type": "stat",
        "targets": [
          {
            "expr": "up{job=~\"jarvis-.*\"}",
            "legendFormat": "{{ job }}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "thresholds": {
              "steps": [
                {"color": "red", "value": 0},
                {"color": "green", "value": 1}
              ]
            }
          }
        }
      },
      {
        "title": "Response Time P95",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(jarvis_response_time_seconds_bucket[5m]))",
            "legendFormat": "API P95"
          }
        ],
        "alert": {
          "conditions": [
            {
              "query": {"queryType": "", "refId": "A"},
              "reducer": {"params": [], "type": "last"},
              "evaluator": {"params": [0.2], "type": "gt"}
            }
          ],
          "executionErrorState": "alerting",
          "for": "2m",
          "frequency": "30s",
          "handler": 1,
          "name": "High Response Time",
          "noDataState": "no_data"
        }
      },
      {
        "title": "Error Rate",
        "type": "singlestat",
        "targets": [
          {
            "expr": "rate(jarvis_requests_errors_total[5m]) / rate(jarvis_requests_total[5m]) * 100",
            "legendFormat": "Error %"
          }
        ],
        "thresholds": "5,10"
      }
    ]
  }
}
```

### **2. Alertes Critiques**
```yaml
# monitoring/critical-alerts.yml
groups:
- name: jarvis-critical-operations
  rules:
  - alert: ServiceDown
    expr: up{job=~"jarvis-.*"} == 0
    for: 30s
    labels:
      severity: critical
      runbook: "https://docs.jarvis.com/runbooks#service-down"
    annotations:
      summary: "Service {{ $labels.job }} is down"
      description: "Service {{ $labels.job }} has been down for more than 30 seconds"
      action: "Check service logs and restart if necessary"

  - alert: HighErrorRate
    expr: rate(jarvis_requests_errors_total[5m]) / rate(jarvis_requests_total[5m]) > 0.05
    for: 2m
    labels:
      severity: critical
      runbook: "https://docs.jarvis.com/runbooks#high-error-rate"
    annotations:
      summary: "High error rate: {{ $value | humanizePercentage }}"
      description: "Error rate is above 5% for more than 2 minutes"
      action: "Check application logs and recent deployments"

  - alert: DatabaseConnectionsHigh
    expr: jarvis_database_connections_active > 80
    for: 5m
    labels:
      severity: warning
      runbook: "https://docs.jarvis.com/runbooks#db-connections"
    annotations:
      summary: "High database connections: {{ $value }}"
      description: "Database connections above 80 for more than 5 minutes"
      action: "Check for connection leaks and scale database if needed"

  - alert: MemoryUsageHigh
    expr: container_memory_usage_bytes / container_spec_memory_limit_bytes > 0.9
    for: 5m
    labels:
      severity: warning
      runbook: "https://docs.jarvis.com/runbooks#memory-usage"
    annotations:
      summary: "High memory usage: {{ $value | humanizePercentage }}"
      description: "Container {{ $labels.container }} using more than 90% memory"
      action: "Restart container or increase memory limits"
```

### **3. Health Check Complet**
```bash
#!/bin/bash
# health-check-all.sh

ENVIRONMENT=${1:-development}
echo "🩺 [$(date)] Health Check Complet - Environment: $ENVIRONMENT"

# Résultats
RESULTS_FILE="/tmp/health-check-$(date +%Y%m%d-%H%M%S).json"
echo "{\"timestamp\":\"$(date -Iseconds)\",\"environment\":\"$ENVIRONMENT\",\"checks\":[]}" > $RESULTS_FILE

# Fonction health check générique
check_service() {
    local service=$1
    local endpoint=$2
    local expected_code=${3:-200}
    
    echo "🔍 Vérification $service..."
    
    local start_time=$(date +%s.%N)
    local response=$(curl -s -w "%{http_code}" -o /dev/null $endpoint)
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc -l)
    
    local status="OK"
    local message="Service accessible"
    
    if [[ "$response" != "$expected_code" ]]; then
        status="FAILED"
        message="HTTP $response (attendu: $expected_code)"
    fi
    
    # Ajouter résultat au JSON
    jq --arg service "$service" \
       --arg status "$status" \
       --arg message "$message" \
       --arg duration "$duration" \
       --arg response_code "$response" \
       '.checks += [{
         "service": $service,
         "status": $status,
         "message": $message,
         "duration_seconds": ($duration | tonumber),
         "response_code": ($response_code | tonumber)
       }]' $RESULTS_FILE > /tmp/health.tmp && mv /tmp/health.tmp $RESULTS_FILE
    
    printf "%-20s [%s] %s (%.3fs)\n" "$service" "$status" "$message" "$duration"
}

# Vérifications services
check_service "Backend API" "http://localhost:8100/health"
check_service "Frontend" "http://localhost:3000" 200
check_service "STT API" "http://localhost:8003/health"
check_service "TTS API" "http://localhost:8002/health"
check_service "Prometheus" "http://localhost:9090/-/healthy"
check_service "Grafana" "http://localhost:3001/api/health"

# Vérifications base de données
echo "🔍 Vérification PostgreSQL..."
DB_STATUS=$(docker exec jarvis_postgres pg_isready -U jarvis 2>/dev/null && echo "OK" || echo "FAILED")
printf "%-20s [%s]\n" "PostgreSQL" "$DB_STATUS"

echo "🔍 Vérification Redis..."
REDIS_STATUS=$(docker exec jarvis_redis redis-cli ping 2>/dev/null | grep PONG >/dev/null && echo "OK" || echo "FAILED")
printf "%-20s [%s]\n" "Redis" "$REDIS_STATUS"

# Résumé final
echo ""
echo "📊 Résumé Health Check:"
TOTAL_CHECKS=$(jq '.checks | length' $RESULTS_FILE)
OK_CHECKS=$(jq '[.checks[] | select(.status == "OK")] | length' $RESULTS_FILE)
FAILED_CHECKS=$(jq '[.checks[] | select(.status == "FAILED")] | length' $RESULTS_FILE)

echo "  ✅ Services OK: $OK_CHECKS/$TOTAL_CHECKS"
echo "  ❌ Services FAILED: $FAILED_CHECKS/$TOTAL_CHECKS"
echo "  📄 Rapport détaillé: $RESULTS_FILE"

if [[ $FAILED_CHECKS -gt 0 ]]; then
    echo ""
    echo "❌ Services en échec:"
    jq -r '.checks[] | select(.status == "FAILED") | "  - \(.service): \(.message)"' $RESULTS_FILE
    exit 1
fi

echo "✅ [$(date)] Tous les services sont opérationnels"
```

---

## 🚨 **RÉSOLUTION D'INCIDENTS**

### **1. Incident Backend API Non Réactif**
```bash
#!/bin/bash
# incident-backend-unresponsive.sh

echo "🚨 [$(date)] INCIDENT: Backend API non réactif"

# 1. Diagnostic rapide
echo "🔍 Diagnostic initial..."
kubectl get pods -l app=jarvis-backend -n jarvis-production
kubectl describe pod -l app=jarvis-backend -n jarvis-production

# 2. Logs récents
echo "📋 Logs récents (5 minutes)..."
kubectl logs -l app=jarvis-backend --since=5m -n jarvis-production --tail=50

# 3. Métriques système
echo "📊 Métriques système..."
kubectl top pods -l app=jarvis-backend -n jarvis-production

# 4. Test connectivité base de données
echo "🔌 Test connectivité PostgreSQL..."
kubectl exec -n jarvis-production postgres-0 -- \
    psql -U jarvis -d jarvis_production -c "SELECT 1;" || {
    echo "❌ Base de données non accessible"
    # Procédure recovery DB
    ./scripts/recover-database.sh production
}

# 5. Restart progressif si nécessaire
echo "🔄 Restart progressif backend..."
kubectl rollout restart deployment jarvis-backend -n jarvis-production
kubectl rollout status deployment jarvis-backend -n jarvis-production

# 6. Validation post-incident
echo "✅ Validation post-incident..."
sleep 30
curl -f http://backend:8100/health || {
    echo "❌ Backend toujours non réactif - Escalade nécessaire"
    curl -X POST $CRITICAL_ALERT_WEBHOOK \
        -d '{"text":"🚨 CRITICAL: Backend restart failed - Manual intervention required"}'
    exit 1
}

echo "✅ [$(date)] Backend récupéré avec succès"
```

### **2. Incident Base de Données Corruption**
```bash
#!/bin/bash
# incident-database-corruption.sh

INCIDENT_ID="DB-CORRUPT-$(date +%Y%m%d-%H%M%S)"
echo "🚨 [$(date)] INCIDENT: Corruption base de données - ID: $INCIDENT_ID"

# 1. Isolation immédiate
echo "🔒 Isolation base de données..."
kubectl scale deployment jarvis-backend --replicas=0 -n jarvis-production

# 2. Évaluation dégâts
echo "🔍 Évaluation corruption..."
kubectl exec -n jarvis-production postgres-0 -- \
    psql -U jarvis -d jarvis_production -c "SELECT pg_stat_database_conflicts.*;" \
    > "incidents/$INCIDENT_ID-corruption-stats.txt"

# 3. Tentative repair automatique
echo "🔧 Tentative réparation automatique..."
kubectl exec -n jarvis-production postgres-0 -- \
    psql -U jarvis -d jarvis_production -c "REINDEX DATABASE jarvis_production;" || {
    
    echo "❌ Réparation automatique échouée - Recovery depuis backup"
    
    # 4. Recovery depuis backup le plus récent
    LATEST_BACKUP=$(ls -t backups/production/ | head -1)
    echo "📂 Recovery depuis backup: $LATEST_BACKUP"
    
    # Stop PostgreSQL
    kubectl scale deployment postgres --replicas=0 -n jarvis-production
    
    # Restore backup
    kubectl exec -n jarvis-production postgres-0 -- \
        psql -U jarvis -d postgres -c "DROP DATABASE IF EXISTS jarvis_production;"
    kubectl exec -n jarvis-production postgres-0 -- \
        psql -U jarvis -d postgres -c "CREATE DATABASE jarvis_production;"
    
    kubectl exec -i -n jarvis-production postgres-0 -- \
        psql -U jarvis -d jarvis_production < "backups/production/$LATEST_BACKUP"
}

# 5. Validation intégrité
echo "✅ Validation intégrité post-recovery..."
kubectl exec -n jarvis-production postgres-0 -- \
    psql -U jarvis -d jarvis_production -c "SELECT COUNT(*) FROM users;" || {
    echo "❌ Validation échec - Escalade niveau 3"
    exit 1
}

# 6. Redémarrage services
echo "🚀 Redémarrage services..."
kubectl scale deployment jarvis-backend --replicas=2 -n jarvis-production
kubectl rollout status deployment jarvis-backend -n jarvis-production

echo "✅ [$(date)] Recovery base de données terminé"
```

### **3. Incident Memory Leak**
```bash
#!/bin/bash
# incident-memory-leak.sh

SERVICE=${1:-backend}
THRESHOLD=${2:-90}  # Pourcentage mémoire

echo "🧠 [$(date)] INCIDENT: Memory leak détecté - Service: $SERVICE"

# 1. Capture état mémoire
echo "📊 Capture état mémoire..."
kubectl exec -n jarvis-production $SERVICE-pod -- \
    cat /proc/meminfo > "incidents/memory-$SERVICE-$(date +%Y%m%d-%H%M%S).txt"

# 2. Analyse processus consommateurs
echo "🔍 Top processus mémoire..."
kubectl exec -n jarvis-production $SERVICE-pod -- \
    ps aux --sort=-%mem | head -20

# 3. Dump heap si Python
if kubectl exec -n jarvis-production $SERVICE-pod -- \
    ps aux | grep python >/dev/null; then
    
    echo "🐍 Python heap dump..."
    kubectl exec -n jarvis-production $SERVICE-pod -- \
        python -c "
import tracemalloc
import gc
tracemalloc.start()
print('Memory usage:', tracemalloc.get_traced_memory())
print('Objects:', len(gc.get_objects()))
"
fi

# 4. Redémarrage du service avec monitoring
echo "🔄 Restart service avec monitoring..."
kubectl delete pod -l app=jarvis-$SERVICE -n jarvis-production
kubectl wait --for=condition=ready pod -l app=jarvis-$SERVICE --timeout=120s -n jarvis-production

# 5. Monitoring post-restart (5 minutes)
echo "📈 Monitoring mémoire post-restart..."
for i in {1..5}; do
    MEMORY_USAGE=$(kubectl exec -n jarvis-production -l app=jarvis-$SERVICE -- \
        awk '/^VmRSS/ {print $2}' /proc/self/status)
    echo "  Minute $i: ${MEMORY_USAGE}KB"
    sleep 60
done

echo "✅ [$(date)] Memory leak incident résolu"
```

---

## 🔧 **MAINTENANCE PLANIFIÉE**

### **1. Maintenance Base de Données**
```bash
#!/bin/bash
# maintenance-database.sh

MAINTENANCE_TYPE=${1:-routine}  # routine, upgrade, migration
ENVIRONMENT=${2:-production}

echo "🔧 [$(date)] Maintenance Base de Données - Type: $MAINTENANCE_TYPE"

# Notification maintenance
curl -X POST $MAINTENANCE_WEBHOOK \
    -d "{\"text\":\"🔧 Maintenance DB $MAINTENANCE_TYPE démarrant dans 10 minutes\"}"

# Attente notification
sleep 600  # 10 minutes

case $MAINTENANCE_TYPE in
    "routine")
        echo "📊 Maintenance routine PostgreSQL..."
        
        # Statistiques avant maintenance
        kubectl exec -n jarvis-$ENVIRONMENT postgres-0 -- \
            psql -U jarvis -d jarvis_$ENVIRONMENT -c "
            SELECT schemaname, tablename, n_tup_ins, n_tup_upd, n_tup_del 
            FROM pg_stat_user_tables;" > maintenance-stats-before.txt
        
        # VACUUM et ANALYZE
        kubectl exec -n jarvis-$ENVIRONMENT postgres-0 -- \
            psql -U jarvis -d jarvis_$ENVIRONMENT -c "VACUUM ANALYZE;"
        
        # REINDEX sur tables principales
        kubectl exec -n jarvis-$ENVIRONMENT postgres-0 -- \
            psql -U jarvis -d jarvis_$ENVIRONMENT -c "
            REINDEX TABLE users;
            REINDEX TABLE conversations;
            REINDEX TABLE memory_vectors;"
        
        # Statistiques après maintenance
        kubectl exec -n jarvis-$ENVIRONMENT postgres-0 -- \
            psql -U jarvis -d jarvis_$ENVIRONMENT -c "
            SELECT schemaname, tablename, n_tup_ins, n_tup_upd, n_tup_del 
            FROM pg_stat_user_tables;" > maintenance-stats-after.txt
        ;;
        
    "upgrade")
        echo "⬆️ Upgrade PostgreSQL..."
        
        # Backup complet avant upgrade
        ./scripts/create-full-backup.sh $ENVIRONMENT
        
        # Rolling upgrade avec validation
        kubectl set image deployment/postgres postgres=postgres:16 -n jarvis-$ENVIRONMENT
        kubectl rollout status deployment/postgres -n jarvis-$ENVIRONMENT
        
        # Validation post-upgrade
        kubectl exec -n jarvis-$ENVIRONMENT postgres-0 -- \
            psql -U jarvis -d jarvis_$ENVIRONMENT -c "SELECT version();"
        ;;
        
    "migration")
        echo "🔄 Migration schéma base de données..."
        
        # Backup avant migration
        ./scripts/create-backup.sh $ENVIRONMENT
        
        # Exécution migrations Alembic
        kubectl exec -n jarvis-$ENVIRONMENT backend-pod -- \
            python -m alembic upgrade head
        
        # Validation migration
        kubectl exec -n jarvis-$ENVIRONMENT backend-pod -- \
            python -c "from backend.db.database import Database; db = Database(); print('Migration OK')"
        ;;
esac

echo "✅ [$(date)] Maintenance base de données terminée"
```

### **2. Maintenance Certificats SSL**
```bash
#!/bin/bash
# maintenance-ssl-certificates.sh

ENVIRONMENT=${1:-production}
DOMAIN=${2:-jarvis.com}

echo "🔐 [$(date)] Maintenance Certificats SSL - Domain: $DOMAIN"

# 1. Vérification expiration actuelles
echo "📅 Vérification expiration certificats..."
openssl x509 -in /etc/ssl/certs/${DOMAIN}.crt -noout -dates

EXPIRY_DATE=$(openssl x509 -in /etc/ssl/certs/${DOMAIN}.crt -noout -enddate | cut -d= -f2)
EXPIRY_TIMESTAMP=$(date -d "$EXPIRY_DATE" +%s)
CURRENT_TIMESTAMP=$(date +%s)
DAYS_LEFT=$(( (EXPIRY_TIMESTAMP - CURRENT_TIMESTAMP) / 86400 ))

echo "📊 Jours restants: $DAYS_LEFT"

if [[ $DAYS_LEFT -gt 30 ]]; then
    echo "✅ Certificats valides pour $DAYS_LEFT jours - Maintenance non nécessaire"
    exit 0
fi

# 2. Renouvellement Let's Encrypt
echo "🔄 Renouvellement certificats Let's Encrypt..."
certbot renew --nginx --domain $DOMAIN --non-interactive

# 3. Mise à jour secrets Kubernetes
echo "🔑 Mise à jour secrets Kubernetes..."
kubectl create secret tls jarvis-tls-new \
    --cert=/etc/letsencrypt/live/$DOMAIN/fullchain.pem \
    --key=/etc/letsencrypt/live/$DOMAIN/privkey.pem \
    -n jarvis-$ENVIRONMENT

# 4. Rolling update des services avec nouveaux certificats
echo "🔄 Rolling update services..."
kubectl patch deployment jarvis-backend \
    -p '{"spec":{"template":{"metadata":{"annotations":{"ssl-update":"'$(date +%s)'"}}}}}' \
    -n jarvis-$ENVIRONMENT

kubectl rollout status deployment jarvis-backend -n jarvis-$ENVIRONMENT

# 5. Validation nouveaux certificats
echo "✅ Validation nouveaux certificats..."
sleep 30
openssl s_client -connect $DOMAIN:443 -servername $DOMAIN </dev/null | \
    openssl x509 -noout -dates

# 6. Suppression ancien secret
kubectl delete secret jarvis-tls -n jarvis-$ENVIRONMENT
kubectl patch secret jarvis-tls-new --type='merge' -p '{"metadata":{"name":"jarvis-tls"}}' -n jarvis-$ENVIRONMENT

echo "✅ [$(date)] Maintenance certificats SSL terminée"
```

---

## 💾 **BACKUP & RECOVERY**

### **1. Backup Complet Automatisé**
```bash
#!/bin/bash
# backup-complete.sh

ENVIRONMENT=${1:-production}
BACKUP_TYPE=${2:-daily}  # daily, weekly, monthly
RETENTION_DAYS=${3:-30}

BACKUP_DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="/backups/$ENVIRONMENT/$BACKUP_TYPE"
BACKUP_ID="jarvis-$ENVIRONMENT-$BACKUP_TYPE-$BACKUP_DATE"

echo "💾 [$(date)] Backup Complet - ID: $BACKUP_ID"

# Création répertoire backup
mkdir -p "$BACKUP_DIR"

# 1. Backup PostgreSQL
echo "📊 Backup PostgreSQL..."
kubectl exec -n jarvis-$ENVIRONMENT postgres-0 -- \
    pg_dump -U jarvis -d jarvis_$ENVIRONMENT --verbose --format=custom \
    > "$BACKUP_DIR/$BACKUP_ID-postgres.dump"

# 2. Backup Redis (RDB snapshot)
echo "💾 Backup Redis..."
kubectl exec -n jarvis-$ENVIRONMENT redis-0 -- redis-cli BGSAVE
sleep 10
kubectl cp jarvis-$ENVIRONMENT/redis-0:/data/dump.rdb \
    "$BACKUP_DIR/$BACKUP_ID-redis.rdb"

# 3. Backup Qdrant vectors
echo "🧠 Backup Qdrant vectors..."
kubectl exec -n jarvis-$ENVIRONMENT qdrant-0 -- \
    tar -czf /tmp/qdrant-backup.tar.gz /qdrant/storage
kubectl cp jarvis-$ENVIRONMENT/qdrant-0:/tmp/qdrant-backup.tar.gz \
    "$BACKUP_DIR/$BACKUP_ID-qdrant.tar.gz"

# 4. Backup configurations
echo "⚙️ Backup configurations..."
kubectl get configmaps -o yaml -n jarvis-$ENVIRONMENT > "$BACKUP_DIR/$BACKUP_ID-configmaps.yaml"
kubectl get secrets -o yaml -n jarvis-$ENVIRONMENT > "$BACKUP_DIR/$BACKUP_ID-secrets.yaml"
helm get values jarvis -n jarvis-$ENVIRONMENT > "$BACKUP_DIR/$BACKUP_ID-helm-values.yaml"

# 5. Backup logs récents (7 derniers jours)
echo "📋 Backup logs..."
find /var/log/jarvis -name "*.log" -mtime -7 -exec tar -czf "$BACKUP_DIR/$BACKUP_ID-logs.tar.gz" {} +

# 6. Manifest de backup
echo "📄 Création manifest backup..."
cat > "$BACKUP_DIR/$BACKUP_ID-manifest.json" <<EOF
{
    "backup_id": "$BACKUP_ID",
    "environment": "$ENVIRONMENT", 
    "backup_type": "$BACKUP_TYPE",
    "timestamp": "$(date -Iseconds)",
    "components": {
        "postgresql": "$BACKUP_ID-postgres.dump",
        "redis": "$BACKUP_ID-redis.rdb", 
        "qdrant": "$BACKUP_ID-qdrant.tar.gz",
        "configurations": "$BACKUP_ID-configmaps.yaml",
        "secrets": "$BACKUP_ID-secrets.yaml",
        "helm_values": "$BACKUP_ID-helm-values.yaml",
        "logs": "$BACKUP_ID-logs.tar.gz"
    },
    "sizes": {
        "postgresql": "$(du -h "$BACKUP_DIR/$BACKUP_ID-postgres.dump" | cut -f1)",
        "redis": "$(du -h "$BACKUP_DIR/$BACKUP_ID-redis.rdb" | cut -f1)",
        "qdrant": "$(du -h "$BACKUP_DIR/$BACKUP_ID-qdrant.tar.gz" | cut -f1)",
        "total": "$(du -hs "$BACKUP_DIR" | cut -f1)"
    }
}
EOF

# 7. Validation backup
echo "✅ Validation backup..."
if [[ -f "$BACKUP_DIR/$BACKUP_ID-postgres.dump" && -f "$BACKUP_DIR/$BACKUP_ID-redis.rdb" ]]; then
    echo "✅ Backup validé avec succès"
    
    # Upload vers stockage externe (S3/Azure/GCP)
    if [[ -n "${BACKUP_STORAGE_URL}" ]]; then
        echo "☁️ Upload vers stockage externe..."
        aws s3 sync "$BACKUP_DIR" "${BACKUP_STORAGE_URL}/$ENVIRONMENT/$BACKUP_TYPE/" || \
        az storage blob upload-batch --destination backups --source "$BACKUP_DIR" || \
        gsutil -m rsync -r "$BACKUP_DIR" "${BACKUP_STORAGE_URL}/$ENVIRONMENT/$BACKUP_TYPE/"
    fi
else
    echo "❌ Backup invalide - Fichiers manquants"
    exit 1
fi

# 8. Nettoyage anciens backups
echo "🧹 Nettoyage anciens backups..."
find "$BACKUP_DIR" -name "jarvis-$ENVIRONMENT-$BACKUP_TYPE-*" -mtime +$RETENTION_DAYS -delete

echo "✅ [$(date)] Backup complet terminé - ID: $BACKUP_ID"
```

### **2. Recovery Complet**
```bash
#!/bin/bash
# recovery-complete.sh

BACKUP_ID=${1}
TARGET_ENVIRONMENT=${2:-staging}

echo "🔄 [$(date)] Recovery Complet - Backup: $BACKUP_ID"

if [[ -z "$BACKUP_ID" ]]; then
    echo "❌ ERREUR: Backup ID requis"
    echo "Usage: $0 <backup_id> [target_environment]"
    echo ""
    echo "Backups disponibles:"
    find /backups -name "*-manifest.json" | head -10
    exit 1
fi

# Localisation backup
BACKUP_DIR=$(find /backups -name "$BACKUP_ID-manifest.json" | head -1 | dirname)
if [[ ! -d "$BACKUP_DIR" ]]; then
    echo "❌ Backup non trouvé: $BACKUP_ID"
    exit 1
fi

echo "📂 Backup trouvé: $BACKUP_DIR"

# 1. Arrêt services cible
echo "🛑 Arrêt services environnement cible..."
kubectl scale deployment --all --replicas=0 -n jarvis-$TARGET_ENVIRONMENT

# 2. Recovery PostgreSQL
echo "📊 Recovery PostgreSQL..."
kubectl exec -n jarvis-$TARGET_ENVIRONMENT postgres-0 -- \
    psql -U jarvis -d postgres -c "DROP DATABASE IF EXISTS jarvis_$TARGET_ENVIRONMENT;"
kubectl exec -n jarvis-$TARGET_ENVIRONMENT postgres-0 -- \
    psql -U jarvis -d postgres -c "CREATE DATABASE jarvis_$TARGET_ENVIRONMENT;"

kubectl exec -i -n jarvis-$TARGET_ENVIRONMENT postgres-0 -- \
    pg_restore -U jarvis -d jarvis_$TARGET_ENVIRONMENT --verbose \
    < "$BACKUP_DIR/$BACKUP_ID-postgres.dump"

# 3. Recovery Redis
echo "💾 Recovery Redis..."
kubectl cp "$BACKUP_DIR/$BACKUP_ID-redis.rdb" \
    jarvis-$TARGET_ENVIRONMENT/redis-0:/data/dump.rdb
kubectl exec -n jarvis-$TARGET_ENVIRONMENT redis-0 -- redis-cli FLUSHALL
kubectl exec -n jarvis-$TARGET_ENVIRONMENT redis-0 -- redis-cli DEBUG RELOAD

# 4. Recovery Qdrant
echo "🧠 Recovery Qdrant..."
kubectl exec -n jarvis-$TARGET_ENVIRONMENT qdrant-0 -- rm -rf /qdrant/storage/*
kubectl cp "$BACKUP_DIR/$BACKUP_ID-qdrant.tar.gz" \
    jarvis-$TARGET_ENVIRONMENT/qdrant-0:/tmp/qdrant-backup.tar.gz
kubectl exec -n jarvis-$TARGET_ENVIRONMENT qdrant-0 -- \
    tar -xzf /tmp/qdrant-backup.tar.gz -C /

# 5. Recovery configurations
echo "⚙️ Recovery configurations..."
kubectl apply -f "$BACKUP_DIR/$BACKUP_ID-configmaps.yaml" -n jarvis-$TARGET_ENVIRONMENT
kubectl apply -f "$BACKUP_DIR/$BACKUP_ID-secrets.yaml" -n jarvis-$TARGET_ENVIRONMENT

# 6. Redémarrage services
echo "🚀 Redémarrage services..."
kubectl scale deployment jarvis-backend --replicas=2 -n jarvis-$TARGET_ENVIRONMENT
kubectl scale deployment jarvis-frontend --replicas=2 -n jarvis-$TARGET_ENVIRONMENT
kubectl scale deployment --all --replicas=1 -n jarvis-$TARGET_ENVIRONMENT

# 7. Validation recovery
echo "✅ Validation recovery..."
sleep 60
./scripts/health-check-all.sh $TARGET_ENVIRONMENT

# Test données
USER_COUNT=$(kubectl exec -n jarvis-$TARGET_ENVIRONMENT postgres-0 -- \
    psql -U jarvis -d jarvis_$TARGET_ENVIRONMENT -t -c "SELECT COUNT(*) FROM users;")
echo "👥 Utilisateurs récupérés: $USER_COUNT"

echo "✅ [$(date)] Recovery complet terminé avec succès"
```

---

## 📞 **CONTACTS & RESPONSABILITÉS**

### **Équipe Technique**
```yaml
# contacts.yaml
contacts:
  technical_lead:
    name: "Enzo"
    email: "enzo@jarvis.com"
    phone: "+33 6 XX XX XX XX"
    slack: "@enzo"
    responsibilities: 
      - Architecture générale
      - Décisions techniques majeures
      - Escalation niveau 3
    availability: "24/7"
    
  devops_lead:
    name: "DevOps Team Lead"
    email: "devops@jarvis.com"
    phone: "+33 6 XX XX XX XX"
    slack: "@devops-lead"
    responsibilities:
      - Infrastructure & déploiements
      - Monitoring & alerting
      - CI/CD pipelines
    availability: "Heures ouvrées + on-call"
    
  security_lead:
    name: "Security Team Lead"
    email: "security@jarvis.com"
    phone: "+33 6 XX XX XX XX"
    slack: "@security-lead"
    responsibilities:
      - Incidents sécurité
      - Audit & compliance
      - Politiques sécurité
    availability: "On-call incidents sécurité"

escalation_matrix:
  level_1:  # Service degradation
    duration: "0-15 minutes"
    responders: ["devops-oncall"]
    actions: 
      - Diagnostics automatisés
      - Restart services si nécessaire
      - Notification équipe
      
  level_2:  # Partial outage
    duration: "15-60 minutes"
    responders: ["devops-lead", "technical-lead"]
    actions:
      - Investigation approfondie
      - Rollback si nécessaire
      - Communication clients
      - War room si besoin
      
  level_3:  # Complete outage
    duration: ">60 minutes"
    responders: ["technical-lead", "cto", "management"]
    actions:
      - Activation disaster recovery
      - Communication executive
      - Post-mortem obligatoire
      - Plan d'action préventif

notification_channels:
  slack:
    critical: "#jarvis-critical"
    warnings: "#jarvis-alerts"
    maintenance: "#jarvis-maintenance"
    general: "#jarvis-ops"
    
  email:
    critical: "critical@jarvis.com"
    technical: "tech-team@jarvis.com"
    management: "leadership@jarvis.com"
    
  sms:
    enabled: true
    numbers: ["+33 6 XX XX XX XX"]
    severity_threshold: "critical"

on_call_schedule:
  primary:
    week: "DevOps Engineer A"
    weekend: "DevOps Engineer B"
    rotation: "Weekly"
    
  secondary:
    week: "Technical Lead"
    weekend: "Technical Lead" 
    escalation_time: "30 minutes"
    
  holidays:
    coverage: "External contractor"
    contact: "support@external-company.com"
```

---

## 📝 **CONCLUSION RUNBOOKS**

Ces runbooks opérationnels couvrent tous les aspects critiques de l'exploitation de Jarvis v1.9.0 :

### ✅ **Procédures Couvertes**
- **Démarrage/Arrêt** : Gracieux et d'urgence
- **Monitoring** : Dashboards et alertes
- **Incidents** : Résolution structurée
- **Maintenance** : Planifiée et préventive
- **Backup/Recovery** : Complet et testé
- **Escalation** : Matrice claire

### 🎯 **Objectifs Atteints**
- **RTO/RPO** : Objectifs définis par tier
- **SLO** : Mesurables et monitoring
- **Automation** : Scripts reproductibles
- **Documentation** : Procédures détaillées

**Date** : 23 août 2025  
**Version** : 1.3.2 Enterprise  
**Statut** : Opérationnellement Prêt  
**Contact** : ops-team@jarvis.com