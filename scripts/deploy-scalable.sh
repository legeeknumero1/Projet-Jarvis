#!/bin/bash
# Script de déploiement architecture scalable - Jarvis v1.3.2
# Automatise le déploiement complet de l'infrastructure microservices

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_FILE="${PROJECT_ROOT}/.env.scalable"

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonctions utilitaires
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifications préalables
check_prerequisites() {
    log_info "Vérification des prérequis..."
    
    # Docker et Docker Compose
    if ! command -v docker &> /dev/null; then
        log_error "Docker n'est pas installé"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose n'est pas installé"
        exit 1
    fi
    
    # Vérifier que Docker fonctionne
    if ! docker info &> /dev/null; then
        log_error "Docker daemon n'est pas accessible"
        exit 1
    fi
    
    # Espace disque suffisant (au moins 10GB)
    available_space=$(df -BG "$PROJECT_ROOT" | awk 'NR==2 {print $4}' | sed 's/G//')
    if [[ $available_space -lt 10 ]]; then
        log_warning "Espace disque faible: ${available_space}GB disponible (recommandé: 10GB+)"
    fi
    
    log_success "Prérequis validés"
}

# Génération/validation du fichier .env
setup_environment() {
    log_info "Configuration de l'environnement..."
    
    if [[ ! -f "$ENV_FILE" ]]; then
        log_info "Création du fichier .env.scalable..."
        cat > "$ENV_FILE" << EOF
# Configuration Jarvis Scalable Architecture v1.3.2
# Fichier généré automatiquement le $(date)

# === SERVICES SCALING ===
BACKEND_INSTANCES=2
FRONTEND_INSTANCES=2
OLLAMA_INSTANCES=2

# === NETWORK CONFIGURATION ===
DOCKER_FRONTEND_NETWORK=jarvis_frontend
DOCKER_BACKEND_NETWORK=jarvis_backend
DOCKER_DATA_NETWORK=jarvis_data
DOCKER_FRONTEND_SUBNET=172.21.0.0/16
DOCKER_BACKEND_SUBNET=172.22.0.0/16
DOCKER_DATA_SUBNET=172.23.0.0/16

# === LOAD BALANCER ===
NGINX_HTTP_PORT=80
NGINX_HTTPS_PORT=443
NGINX_ADMIN_PORT=8080
API_RATE_LIMIT=20r/s

# === DATABASE CLUSTER ===
POSTGRES_DB=jarvis_db
POSTGRES_USER=jarvis
POSTGRES_PASSWORD=$(openssl rand -base64 32)
POSTGRES_REPLICATION_USER=replicator
POSTGRES_REPLICATION_PASSWORD=$(openssl rand -base64 32)
POSTGRES_MASTER_PORT=5432
POSTGRES_REPLICA_PORT=5433

# === REDIS CLUSTER ===
REDIS_1_PORT=6379
REDIS_2_PORT=6380
REDIS_3_PORT=6381
REDIS_CLUSTER_NODES=redis-1:6379,redis-2:6380,redis-3:6381

# === OLLAMA CONFIGURATION ===
OLLAMA_LB_PORT=11434
OLLAMA_UPSTREAM_1=ollama-1:11434
OLLAMA_UPSTREAM_2=ollama-2:11434
OLLAMA_LB_STRATEGY=least_connections
OLLAMA_MEMORY_LIMIT=6G
OLLAMA_CPU_LIMIT=4.0

# === MONITORING ===
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001
GRAFANA_ADMIN_PASSWORD=$(openssl rand -base64 16)
JAEGER_UI_PORT=16686

# === SECURITY ===
JARVIS_SECRET_KEY=$(openssl rand -base64 32)

# === RESOURCES ===
BACKEND_MEMORY_LIMIT=2G
BACKEND_CPU_LIMIT=2.0
INTERFACE_MEMORY_LIMIT=1G
INTERFACE_CPU_LIMIT=1.0

# === LOGGING ===
LOGGING_DRIVER=json-file
LOG_MAX_SIZE=10m
LOG_MAX_FILE=3

# === HEALTHCHECKS ===
HEALTHCHECK_INTERVAL=30s
HEALTHCHECK_TIMEOUT=10s
HEALTHCHECK_RETRIES=3
HEALTHCHECK_START_PERIOD=30s

RESTART_POLICY=unless-stopped
EOF
        log_success "Fichier .env.scalable créé"
    else
        log_info "Utilisation du fichier .env.scalable existant"
    fi
}

# Création des répertoires nécessaires
create_directories() {
    log_info "Création des répertoires..."
    
    local dirs=(
        "config/nginx/conf.d"
        "config/postgres"
        "config/redis"
        "config/qdrant"
        "config/grafana/dashboards"
        "config/grafana/provisioning/dashboards"
        "config/grafana/provisioning/datasources"
        "logs/nginx"
        "logs/backend-1"
        "logs/backend-2"
        "logs/interface-1"
        "logs/interface-2"
        "ssl"
    )
    
    for dir in "${dirs[@]}"; do
        mkdir -p "$PROJECT_ROOT/$dir"
    done
    
    log_success "Répertoires créés"
}

# Génération des configurations
generate_configs() {
    log_info "Génération des fichiers de configuration..."
    
    # Configuration Redis Cluster
    cat > "$PROJECT_ROOT/config/redis/redis-cluster.conf" << 'EOF'
port 6379
cluster-enabled yes
cluster-node-timeout 5000
appendonly yes
appendfsync everysec
maxmemory-policy allkeys-lru
EOF
    
    # Configuration PostgreSQL Master
    cat > "$PROJECT_ROOT/config/postgres/master.conf" << 'EOF'
# PostgreSQL Master Configuration
listen_addresses = '*'
port = 5432
max_connections = 200
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB

# Replication
wal_level = replica
max_wal_senders = 3
max_replication_slots = 3
archive_mode = on
archive_command = 'test ! -f /var/lib/postgresql/archive/%f && cp %p /var/lib/postgresql/archive/%f'
hot_standby = on
EOF
    
    # Configuration PostgreSQL Replica
    cat > "$PROJECT_ROOT/config/postgres/replica.conf" << 'EOF'
# PostgreSQL Replica Configuration
listen_addresses = '*'
port = 5432
max_connections = 100
shared_buffers = 256MB
effective_cache_size = 1GB
hot_standby = on
hot_standby_feedback = on
max_standby_streaming_delay = 30s
wal_receiver_timeout = 60s
EOF
    
    # pg_hba.conf pour réplication
    cat > "$PROJECT_ROOT/config/postgres/pg_hba.conf" << 'EOF'
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             postgres                                trust
local   all             all                                     md5
host    all             all             172.23.0.0/16           md5
host    replication     replicator      172.23.0.0/16           md5
EOF
    
    # Script de configuration réplication
    cat > "$PROJECT_ROOT/config/postgres/replication.sql" << 'EOF'
-- Configuration utilisateur réplication
CREATE USER replicator REPLICATION LOGIN CONNECTION LIMIT 3 ENCRYPTED PASSWORD 'REPLICATION_PASSWORD_PLACEHOLDER';
EOF
    
    # Datasource Grafana
    cat > "$PROJECT_ROOT/config/grafana/provisioning/datasources/prometheus.yml" << 'EOF'
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false
EOF
    
    log_success "Configurations générées"
}

# Build des images
build_images() {
    log_info "Build des images Docker..."
    
    cd "$PROJECT_ROOT"
    
    # Build backend scalable
    log_info "Build backend scalable..."
    docker build -f backend/Dockerfile.scalable -t jarvis/backend:scalable backend/
    
    # Build interface scalable
    log_info "Build interface scalable..."
    docker build -f services/interface/Dockerfile.scalable -t jarvis/interface:scalable services/interface/
    
    # Build Ollama Load Balancer
    log_info "Build Ollama Load Balancer..."
    docker build -t jarvis/ollama-lb:latest services/ollama-lb/
    
    log_success "Images buildées"
}

# Déploiement des services
deploy_services() {
    log_info "Déploiement des services..."
    
    cd "$PROJECT_ROOT"
    
    # Charger l'environnement
    set -a
    source "$ENV_FILE"
    set +a
    
    # Arrêter les services existants
    log_info "Arrêt des services existants..."
    docker-compose -f docker-compose.scalable.yml down --remove-orphans 2>/dev/null || true
    
    # Nettoyer les réseaux existants
    docker network prune -f
    
    # Déployer avec les nouvelles configurations
    log_info "Démarrage des services..."
    docker-compose -f docker-compose.scalable.yml up -d
    
    log_success "Services déployés"
}

# Vérification de la santé des services
check_services_health() {
    log_info "Vérification de la santé des services..."
    
    local services=(
        "nginx-lb:80:/health"
        "prometheus:9090/-/healthy"
        "grafana:3000/api/health"
    )
    
    local max_attempts=30
    local attempt=1
    
    for service in "${services[@]}"; do
        IFS=':' read -r service_name port path <<< "$service"
        
        log_info "Vérification de $service_name..."
        
        while [[ $attempt -le $max_attempts ]]; do
            if curl -sf "http://localhost:$port$path" > /dev/null 2>&1; then
                log_success "$service_name est sain"
                break
            fi
            
            if [[ $attempt -eq $max_attempts ]]; then
                log_warning "$service_name ne répond pas après $max_attempts tentatives"
            fi
            
            sleep 5
            ((attempt++))
        done
        
        attempt=1
    done
}

# Affichage des informations de déploiement
show_deployment_info() {
    log_info "Informations de déploiement"
    echo
    echo "🎯 Architecture Scalable Jarvis v1.3.2 déployée !"
    echo
    echo "📊 Services principaux:"
    echo "  - Load Balancer:     http://localhost:80"
    echo "  - Admin Nginx:       http://localhost:8080/health"
    echo "  - Prometheus:        http://localhost:9090"
    echo "  - Grafana:           http://localhost:3001 (admin/$(grep GRAFANA_ADMIN_PASSWORD "$ENV_FILE" | cut -d'=' -f2))"
    echo "  - Jaeger:            http://localhost:16686"
    echo
    echo "🔧 Commandes utiles:"
    echo "  - Status services:   docker-compose -f docker-compose.scalable.yml ps"
    echo "  - Logs:              docker-compose -f docker-compose.scalable.yml logs -f [service]"
    echo "  - Scale backend:     docker-compose -f docker-compose.scalable.yml up -d --scale backend-1=3"
    echo "  - Arrêt:             docker-compose -f docker-compose.scalable.yml down"
    echo
    echo "📁 Configuration:     $ENV_FILE"
    echo "📋 Logs:              $PROJECT_ROOT/logs/"
    echo
}

# Fonction principale
main() {
    log_info "🚀 Déploiement Architecture Scalable Jarvis v1.3.2"
    echo
    
    check_prerequisites
    setup_environment
    create_directories
    generate_configs
    build_images
    deploy_services
    check_services_health
    show_deployment_info
    
    log_success "Déploiement terminé avec succès !"
}

# Gestion des signaux
cleanup() {
    log_info "Nettoyage en cours..."
    # Arrêter les services si nécessaire
    exit 0
}

trap cleanup INT TERM

# Exécution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi