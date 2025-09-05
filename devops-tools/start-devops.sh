#!/bin/bash

# 🛠️ Script de démarrage stack DevOps complète Jarvis
# Jenkins + ArgoCD + Prometheus + Grafana + Loki

set -e

echo "🚀 Démarrage stack DevOps Jarvis v1.4.0"
echo "=============================================="

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')] ⚠️  $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] ❌ $1${NC}"
    exit 1
}

# Vérifier Docker
if ! command -v docker &> /dev/null; then
    error "Docker n'est pas installé"
fi

if ! docker info &> /dev/null; then
    error "Docker daemon n'est pas démarré"
fi

log "✅ Docker validé"

# Créer le réseau DevOps s'il n'existe pas
if ! docker network ls | grep -q jarvis_devops; then
    log "🌐 Création réseau jarvis_devops..."
    docker network create jarvis_devops --subnet=172.21.0.0/16 --gateway=172.21.0.1
else
    log "🌐 Réseau jarvis_devops déjà existant"
fi

# Arrêter les services existants
log "🛑 Arrêt des services DevOps existants..."
docker-compose -f docker-compose-devops.yml down 2>/dev/null || true

# Nettoyer les volumes orphelins si demandé
if [[ "$1" == "--clean" ]]; then
    warn "🧹 Nettoyage des volumes DevOps..."
    docker volume prune -f
fi

# Démarrer la stack DevOps
log "🚀 Démarrage stack DevOps complète..."
docker-compose -f docker-compose-devops.yml up -d

# Attendre que les services soient prêts
log "⏳ Attente démarrage des services..."

services=(
    "jenkins:8080:/health"
    "argocd-server:8080:/healthz"
    "grafana:3000:/api/health"
    "prometheus:9090/-/healthy"
    "loki:3100/ready"
    "alertmanager:9093/-/healthy"
)

for service in "${services[@]}"; do
    IFS=':' read -r name port path <<< "$service"
    log "🔍 Vérification $name..."
    
    for i in {1..30}; do
        if docker exec -it jarvis_$name curl -f http://localhost:$port$path &>/dev/null; then
            log "✅ $name est prêt"
            break
        fi
        
        if [ $i -eq 30 ]; then
            warn "⚠️ Timeout pour $name"
        fi
        
        sleep 2
    done
done

log "🎉 Stack DevOps démarrée avec succès!"

# Démarrer ArgoCD sur k3s
log "🚀 Démarrage ArgoCD sur cluster k3s..."
./start-argocd.sh > /dev/null 2>&1 &
ARGOCD_PID=$!

echo ""
echo "📊 Services disponibles:"
echo "========================"
echo "🔧 Jenkins CI/CD:       http://localhost:8080"
echo "🚀 ArgoCD GitOps:       https://localhost:8081 (sur k3s)"
echo "📈 Grafana Monitoring:  http://localhost:3001"
echo "📊 Prometheus Metrics:  http://localhost:9090"
echo "📝 Loki Logs:           http://localhost:3100"
echo "🚨 AlertManager:        http://localhost:9093"
echo "🌐 DevOps Dashboard:    http://localhost:80"
echo ""
echo "🔑 Accès par défaut:"
echo "==================="
echo "Jenkins:  admin / (voir docker logs jarvis_jenkins)"
echo "ArgoCD:   admin / (voir ./start-argocd.sh pour mot de passe)"
echo "Grafana:  admin / admin"
echo ""
echo "🔧 Commandes utiles:"
echo "==================="
echo "Logs:     docker-compose -f docker-compose-devops.yml logs -f [service]"
echo "Stop:     docker-compose -f docker-compose-devops.yml down"
echo "Restart:  ./start-devops.sh"
echo "Clean:    ./start-devops.sh --clean"
echo ""

# Afficher les conteneurs en cours
log "📦 État des conteneurs DevOps:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep jarvis

echo ""
log "🎯 Stack DevOps prête ! Bon développement avec Jarvis 🤖"