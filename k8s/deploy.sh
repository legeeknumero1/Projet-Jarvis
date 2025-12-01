#!/bin/bash

# Script de déploiement Kubernetes pour Jarvis
# Instance #11 - Migration complète Docker → K8s

set -e

echo " Déploiement Kubernetes Jarvis V1.4.0"
echo "========================================"

# Couleurs pour output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction logging
log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')]   $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%H:%M:%S')]  $1${NC}"
    exit 1
}

# Vérification prérequis
log "Vérification des prérequis..."

# Vérifier kubectl
if ! command -v kubectl &> /dev/null; then
    error "kubectl n'est pas installé"
fi

# Vérifier connexion cluster
if ! kubectl cluster-info &> /dev/null; then
    error "Impossible de se connecter au cluster Kubernetes"
fi

# Vérifier Docker (pour build images)
if ! command -v docker &> /dev/null; then
    error "Docker n'est pas installé"
fi

log " Prérequis validés"

# Fonction pour attendre qu'un deployment soit prêt
wait_for_deployment() {
    local namespace=$1
    local deployment=$2
    local timeout=${3:-300}
    
    log "Attente deployment $deployment..."
    if kubectl wait --for=condition=available --timeout=${timeout}s deployment/$deployment -n $namespace; then
        log " $deployment est prêt"
    else
        error " Timeout deployment $deployment"
    fi
}

# Build des images Docker locales
log "Construction des images Docker..."

# Image Backend
log " Build image jarvis-backend..."
cd /home/enzo/Documents/Projet\ Jarvis/backend
docker build -t jarvis-backend:latest . || error "Erreur build backend"

# Image TTS
log " Build image jarvis-tts..."
cd /home/enzo/Documents/Projet\ Jarvis/services/tts
docker build -t jarvis-tts:latest . || error "Erreur build TTS"

# Image STT
log " Build image jarvis-stt..."
cd /home/enzo/Documents/Projet\ Jarvis/services/stt
docker build -t jarvis-stt:latest . || error "Erreur build STT"

# Image Interface
log " Build image jarvis-interface..."
cd /home/enzo/Documents/Projet\ Jarvis/services/interface
docker build -t jarvis-interface:latest . || error "Erreur build interface"

log " Images construites"

# Import des images dans K3s
log " Import des images dans K3s..."
k3s ctr images import <(docker save jarvis-backend:latest) || warn "Erreur import backend"
k3s ctr images import <(docker save jarvis-tts:latest) || warn "Erreur import TTS"  
k3s ctr images import <(docker save jarvis-stt:latest) || warn "Erreur import STT"
k3s ctr images import <(docker save jarvis-interface:latest) || warn "Erreur import interface"
log " Images importées dans K3s"

# Retour au répertoire k8s
cd /home/enzo/Documents/Projet\ Jarvis/k8s

# Création des répertoires de stockage
log "Création des répertoires de stockage..."
sudo mkdir -p /var/lib/jarvis/{postgres,redis,ollama,qdrant,timescale}
sudo chown -R $USER:$USER /var/lib/jarvis

# Déploiement étape par étape
log "Déploiement namespace et configuration..."
kubectl apply -f 00-namespace.yaml
kubectl apply -f 01-storage.yaml
kubectl apply -f 02-configmap-secrets.yaml

log "Déploiement des bases de données..."
kubectl apply -f 03-postgres.yaml
kubectl apply -f 04-redis.yaml
kubectl apply -f 05-qdrant.yaml
kubectl apply -f 06-timescale.yaml

# Attendre que les DBs soient prêtes
wait_for_deployment jarvis jarvis-postgres 180
wait_for_deployment jarvis jarvis-redis 120
wait_for_deployment jarvis jarvis-qdrant 120
wait_for_deployment jarvis jarvis-timescale 180

log "Déploiement Ollama..."
kubectl apply -f 07-ollama.yaml
wait_for_deployment jarvis jarvis-ollama 300

log "Déploiement des APIs..."
kubectl apply -f 08-stt-api.yaml
kubectl apply -f 09-tts-api.yaml
kubectl apply -f 10-backend.yaml

# Attendre APIs
wait_for_deployment jarvis jarvis-stt 180
wait_for_deployment jarvis jarvis-tts 180
wait_for_deployment jarvis jarvis-backend 240

log "Déploiement interface..."
kubectl apply -f 11-interface.yaml
wait_for_deployment jarvis jarvis-interface 180

log "Configuration réseau et monitoring..."
kubectl apply -f 12-ingress.yaml || warn "Ingress non appliqué (nginx-ingress requis)"
kubectl apply -f 13-monitoring.yaml || warn "Monitoring non appliqué (prometheus optionnel)"

# Vérification finale
log "Vérification du déploiement..."
echo ""
echo " État des pods:"
kubectl get pods -n jarvis -o wide

echo ""
echo " Services disponibles:"
kubectl get svc -n jarvis

echo ""
echo " Stockage:"
kubectl get pvc -n jarvis

# URLs d'accès
echo ""
echo " URLs d'accès:"
echo "Frontend:    http://localhost:30100"
echo "Backend API: http://localhost:30000"
echo "WebSocket:   ws://localhost:30001"
echo "TTS API:     http://localhost:30002"
echo "STT API:     http://localhost:30003"
echo "Prometheus:  http://localhost:30090"
echo "Grafana:     http://localhost:30300 (admin/jarvis123)"

# Commandes utiles
echo ""
echo " Commandes utiles:"
echo "Logs backend:    kubectl logs -f deployment/jarvis-backend -n jarvis"
echo "Logs interface:  kubectl logs -f deployment/jarvis-interface -n jarvis"
echo "Shell backend:   kubectl exec -it deployment/jarvis-backend -n jarvis -- /bin/bash"
echo "Monitoring:      kubectl get pods -n jarvis -w"

# Test de connectivité
log "Test de connectivité..."
sleep 10

# Test health check backend
if curl -s http://localhost:30000/health > /dev/null; then
    log " Backend API répond"
else
    warn " Backend API ne répond pas encore"
fi

log " Déploiement Kubernetes Jarvis terminé !"
log "Accédez à l'interface: http://localhost:30100"

echo ""
echo " Pour arrêter complètement:"
echo "kubectl delete namespace jarvis"