#!/bin/bash

#  Script de démarrage ArgoCD sur K3s pour Jarvis

set -e

echo " Démarrage ArgoCD GitOps pour Jarvis"
echo "===================================="

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')]   $1${NC}"
}

# Vérifier k3s
if ! systemctl is-active --quiet k3s; then
    log " Démarrage k3s..."
    sudo systemctl start k3s
    sleep 5
fi

log " K3s cluster actif"

# Attendre que les pods ArgoCD soient prêts
log " Attente des pods ArgoCD..."
sudo kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=argocd-server -n argocd --timeout=300s

log " ArgoCD pods prêts"

# Utiliser admin/admin comme credentials
log " Configuration credentials admin/admin..."
ARGOCD_PASSWORD="admin"

# Démarrer port-forward en arrière-plan
log " Configuration port-forward ArgoCD..."
sudo kubectl port-forward svc/argocd-server -n argocd 8081:443 --address=0.0.0.0 > /dev/null 2>&1 &
PORT_FORWARD_PID=$!

# Attendre que le port-forward soit actif
sleep 3

log " ArgoCD démarré avec succès!"
echo ""
echo " Service ArgoCD disponible:"
echo "============================="
echo " ArgoCD GitOps:       https://localhost:8081"
echo ""
echo " Connexion:"
echo "=============="
echo "Username: admin"
echo "Password: $ARGOCD_PASSWORD"
echo ""
echo " Commandes utiles:"
echo "==================="
echo "Logs ArgoCD: sudo kubectl logs -f deployment/argocd-server -n argocd"
echo "Stop ArgoCD: kill $PORT_FORWARD_PID"
echo "Restart:     ./start-argocd.sh"
echo ""

# Sauvegarder le PID pour pouvoir l'arrêter
echo $PORT_FORWARD_PID > .argocd-port-forward.pid

log " ArgoCD prêt ! PID port-forward: $PORT_FORWARD_PID"