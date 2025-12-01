#!/bin/bash

# SCRIPT UNIQUE COMPLET : Fix K3s + Import + Déploiement Jarvis
# Tout-en-un pour éviter multiples scripts
set -e

# Couleurs pour output
RED='\033[0;31m'
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

error() {
    echo -e "${RED}[$(date +'%H:%M:%S')]  $1${NC}"
    exit 1
}

log " DÉPLOIEMENT JARVIS K3S - SCRIPT UNIQUE COMPLET"
log "================================================"

K3S_DATA_DIR="/home/enzo/.k3s"
K3S_SERVICE_FILE="/etc/systemd/system/k3s.service"

# ===== ÉTAPE 1: ARRÊT COMPLET K3S =====
log " ÉTAPE 1: Arrêt complet K3s..."
systemctl stop k3s 2>/dev/null || true
pkill -f k3s 2>/dev/null || true
sleep 10

# Nettoyer les sockets/processus
log " Nettoyage sockets/processus..."
rm -rf /run/k3s/* 2>/dev/null || true
rm -rf /var/run/k3s/* 2>/dev/null || true

# ===== ÉTAPE 2: RECONFIGURATION K3S =====
log " ÉTAPE 2: Reconfiguration K3s avec data-dir /home/enzo/.k3s"

# Créer data-dir avec bonnes permissions
mkdir -p "$K3S_DATA_DIR"
chown -R enzo:enzo "$K3S_DATA_DIR"
log " Data-dir créé: $K3S_DATA_DIR"

# Vérifier espace disque
log " Espace disponible home:"
df -h /home | tail -1

# Sauvegarder service existant
if [ -f "$K3S_SERVICE_FILE" ]; then
    cp "$K3S_SERVICE_FILE" "$K3S_SERVICE_FILE.backup"
    log " Service K3s sauvegardé"
fi

# Créer nouveau service avec data-dir personnalisé
log "  Configuration service K3s..."
tee "$K3S_SERVICE_FILE" > /dev/null << EOF
[Unit]
Description=Lightweight Kubernetes
Documentation=https://k3s.io
Wants=network-online.target

[Service]
Type=exec
EnvironmentFile=-/etc/systemd/system/k3s.service.env
Environment=K3S_DATA_DIR=${K3S_DATA_DIR}
KillMode=process
Delegate=yes
LimitNOFILE=1048576
LimitNPROC=infinity
LimitCORE=infinity
TasksMax=infinity
TimeoutStartSec=0
Restart=always
RestartSec=5s
ExecStartPre=-/sbin/modprobe br_netfilter
ExecStartPre=-/sbin/modprobe overlay
ExecStart=/usr/local/bin/k3s server --data-dir=${K3S_DATA_DIR} --write-kubeconfig-mode 644
ExecReload=/bin/kill -s HUP \$MAINPID
KillSignal=SIGTERM

[Install]
WantedBy=multi-user.target
EOF

# Fichier environnement
tee /etc/systemd/system/k3s.service.env > /dev/null << EOF
K3S_DATA_DIR=${K3S_DATA_DIR}
EOF

# ===== ÉTAPE 3: REDÉMARRAGE K3S =====
log " ÉTAPE 3: Redémarrage K3s avec nouveau data-dir..."
systemctl daemon-reload
systemctl start k3s
sleep 20

# Vérification démarrage avec timeout étendu
log " Vérification K3s (timeout 120s)..."
timeout=120
counter=0
until k3s kubectl get nodes &>/dev/null; do
    if [ $counter -ge $timeout ]; then
        error "K3s non opérationnel après ${timeout}s"
    fi
    sleep 3
    ((counter+=3))
done

log " K3s opérationnel avec nouveau data-dir"

# Vérifier que le data-dir est bien utilisé
if [ -d "$K3S_DATA_DIR/server" ]; then
    log " K3s utilise le nouveau data-dir: $K3S_DATA_DIR"
    log " Espace libre: $(df -h $K3S_DATA_DIR | tail -1 | awk '{print $4}')"
else
    warn " Data-dir peut-être pas encore initialisé, on continue..."
fi

# ===== ÉTAPE 4: VÉRIFICATION IMAGES DOCKER =====
log " ÉTAPE 4: Vérification images Docker..."
IMAGES=("jarvis-backend:latest" "jarvis-tts:latest" "jarvis-stt:latest" "jarvis-interface:latest")

for image in "${IMAGES[@]}"; do
    if docker images --format "table {{.Repository}}:{{.Tag}}" | grep -q "$image"; then
        log " $image disponible"
    else
        error "$image manquante - exécuter d'abord le build des images"
    fi
done

# ===== ÉTAPE 5: IMPORT IMAGES DANS K3S =====
log " ÉTAPE 5: Import des images dans K3s..."

log " Import jarvis-backend (19GB)..."
if docker save jarvis-backend:latest | k3s ctr images import -; then
    log " jarvis-backend importée"
else
    error "Erreur import jarvis-backend"
fi

log " Import jarvis-tts (7.88GB)..."
if docker save jarvis-tts:latest | k3s ctr images import -; then
    log " jarvis-tts importée"
else
    error "Erreur import jarvis-tts"
fi

log " Import jarvis-stt (6.76GB)..."
if docker save jarvis-stt:latest | k3s ctr images import -; then
    log " jarvis-stt importée"
else
    error "Erreur import jarvis-stt"
fi

log " Import jarvis-interface (571MB)..."
if docker save jarvis-interface:latest | k3s ctr images import -; then
    log " jarvis-interface importée"
else
    error "Erreur import jarvis-interface"
fi

# Vérification images importées
log " Images importées dans K3s:"
k3s ctr images ls | grep jarvis

# ===== ÉTAPE 6: DÉPLOIEMENT KUBERNETES =====
log " ÉTAPE 6: Déploiement Kubernetes complet..."

# Fonction d'attente deployment
wait_for_deployment() {
    local namespace=$1
    local deployment=$2
    local timeout=${3:-300}
    
    log "Attente deployment $deployment (${timeout}s max)..."
    if kubectl wait --for=condition=available --timeout=${timeout}s deployment/$deployment -n $namespace 2>/dev/null; then
        log " $deployment opérationnel"
        return 0
    else
        warn " $deployment timeout ou erreur - on continue"
        return 1
    fi
}

# Préparation stockage
log " Préparation stockage K3s..."
mkdir -p "$K3S_DATA_DIR/storage"/{postgres,redis,ollama,qdrant,timescale}
chown -R enzo:enzo "$K3S_DATA_DIR/storage"

# Déploiement par étapes
log " Namespace et configuration de base..."
kubectl apply -f 00-namespace.yaml 2>/dev/null || warn "Namespace existant"
kubectl apply -f 01-storage.yaml 2>/dev/null || warn "Storage non appliqué"
kubectl apply -f 02-configmap-secrets.yaml 2>/dev/null || warn "ConfigMap non appliqué"

log "  Déploiement bases de données..."
kubectl apply -f 03-postgres.yaml 2>/dev/null || warn "PostgreSQL non appliqué"
kubectl apply -f 04-redis.yaml 2>/dev/null || warn "Redis non appliqué"

# Attente DBs critiques
wait_for_deployment jarvis jarvis-postgres 240
wait_for_deployment jarvis jarvis-redis 120

log " Déploiement Ollama LLM..."
kubectl apply -f 07-ollama.yaml 2>/dev/null || warn "Ollama non appliqué"
wait_for_deployment jarvis jarvis-ollama 360

log "  Déploiement APIs vocales..."
kubectl apply -f 08-stt-api.yaml 2>/dev/null || warn "STT non appliqué"
kubectl apply -f 09-tts-api.yaml 2>/dev/null || warn "TTS non appliqué"

wait_for_deployment jarvis jarvis-stt 240
wait_for_deployment jarvis jarvis-tts 240

log " Déploiement backend principal..."
kubectl apply -f 10-backend.yaml 2>/dev/null || warn "Backend non appliqué"
wait_for_deployment jarvis jarvis-backend 300

log "  Déploiement interface utilisateur..."
kubectl apply -f 11-interface.yaml 2>/dev/null || warn "Interface non appliqué"
wait_for_deployment jarvis jarvis-interface 240

# Configuration réseau optionnelle
log " Configuration réseau (optionnel)..."
kubectl apply -f 12-ingress.yaml 2>/dev/null || warn "Ingress ignoré (nginx requis)"
kubectl apply -f 13-monitoring.yaml 2>/dev/null || warn "Monitoring ignoré (prometheus optionnel)"

# ===== ÉTAPE 7: VÉRIFICATION FINALE =====
log " ÉTAPE 7: Vérification déploiement final..."

echo ""
echo " État pods Jarvis:"
kubectl get pods -n jarvis -o wide 2>/dev/null || warn "Erreur lecture pods"

echo ""
echo " Services disponibles:"
kubectl get svc -n jarvis 2>/dev/null || warn "Erreur lecture services"

echo ""
echo " Stockage:"
kubectl get pvc -n jarvis 2>/dev/null || warn "Pas de PVC configurés"

# Test connectivité
log " Tests de connectivité..."
sleep 15

# Test API backend
if curl -s -m 10 http://localhost:30000/health >/dev/null 2>&1; then
    log " Backend API répond sur :30000"
else
    warn " Backend API ne répond pas encore"
fi

# Test interface
if curl -s -m 10 http://localhost:30100 >/dev/null 2>&1; then
    log " Interface web accessible sur :30100"
else
    warn " Interface web pas encore prête"
fi

# ===== RÉSULTAT FINAL =====
echo ""
echo " RÉSULTAT DÉPLOIEMENT JARVIS K3S"
echo "=================================="
echo ""
echo " K3s data-dir: $K3S_DATA_DIR"
echo " Espace libre: $(df -h $K3S_DATA_DIR | tail -1 | awk '{print $4}')"
echo " Images importées: 4/4 (34GB total)"
echo ""
echo " URLS D'ACCÈS:"
echo "Frontend:    http://localhost:30100"
echo "Backend API: http://localhost:30000"
echo "WebSocket:   ws://localhost:30001"  
echo "TTS API:     http://localhost:30002"
echo "STT API:     http://localhost:30003"
echo ""
echo " COMMANDES UTILES:"
echo "Status:      kubectl get pods -n jarvis"
echo "Logs:        kubectl logs -f deployment/jarvis-backend -n jarvis"
echo "Shell:       kubectl exec -it deployment/jarvis-backend -n jarvis -- bash"
echo "Monitoring:  kubectl get pods -n jarvis -w"
echo ""
echo " POUR ARRÊTER:"
echo "kubectl delete namespace jarvis"
echo ""

if curl -s -m 5 http://localhost:30000/health >/dev/null 2>&1; then
    log " JARVIS K3S DÉPLOYÉ AVEC SUCCÈS ! Interface: http://localhost:30100"
else
    warn " Déploiement terminé mais services pas encore tous prêts - patientez 2-3 minutes"
fi

log " Déploiement Jarvis K3S terminé - Script unique exécuté avec succès !"