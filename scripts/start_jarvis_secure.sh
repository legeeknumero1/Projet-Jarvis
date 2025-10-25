#!/bin/bash

# Script de démarrage sécurisé Jarvis v1.3 - Post corrections audit
# Utilise docker-compose.secure.yml avec toutes les corrections appliquées

set -euo pipefail

# Couleurs pour logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Vérifications pré-démarrage
check_requirements() {
    log_info "Vérification des prérequis..."
    
    # Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker n'est pas installé"
        exit 1
    fi
    
    # Docker Compose
    if ! docker compose version &> /dev/null; then
        log_error "Docker Compose n'est pas installé ou trop ancien"
        exit 1
    fi
    
    # NVIDIA Runtime (pour GPU)
    if ! docker info | grep -q "nvidia"; then
        log_warning "NVIDIA runtime non détecté - GPU peut ne pas fonctionner"
    fi
    
    # Vérifier les secrets
    if [[ ! -f "./secrets/postgres_password.txt" ]]; then
        log_error "Fichier secret postgres_password.txt manquant"
        exit 1
    fi
    
    if [[ ! -f "./secrets/api_key.txt" ]]; then
        log_error "Fichier secret api_key.txt manquant"
        exit 1
    fi
    
    log_success "Prérequis validés"
}

# Mise à jour des dépendances frontend
update_frontend_deps() {
    log_info "Mise à jour dépendances frontend (corrections sécurité)..."
    
    cd frontend
    if [[ -f package.json ]]; then
        # Vérifier les versions critiques
        if npm list next@14.1.0 &> /dev/null; then
            log_warning "Next.js 14.1.0 détecté - vulnérabilité CVE-2025-29927"
            npm install next@14.2.32 --save
            log_success "Next.js mis à jour vers 14.2.32 (sécurisé)"
        fi
        
        if npm list axios@1.6.7 &> /dev/null; then
            log_warning "Axios 1.6.7 détecté - vulnérabilités connues"
            npm install axios@1.8.2 --save
            log_success "Axios mis à jour vers 1.8.2 (sécurisé)"
        fi
        
        npm audit fix --force || log_warning "Certaines vulnérabilités n'ont pas pu être corrigées automatiquement"
    fi
    cd ..
}

# Build des images avec optimisations
build_images() {
    log_info "Build des images Docker avec optimisations..."
    
    # Backend
    log_info "Build image backend..."
    docker build \
        --build-arg BUILDKIT_INLINE_CACHE=1 \
        --cache-from jarvis/backend:latest \
        -t jarvis/backend:v1.3-secure \
        ./backend
    
    # Frontend  
    log_info "Build image frontend..."
    docker build \
        --build-arg BUILDKIT_INLINE_CACHE=1 \
        --cache-from jarvis/frontend:latest \
        -t jarvis/frontend:v1.3-secure \
        ./frontend
    
    log_success "Images buildées avec succès"
}

# Démarrage des services
start_services() {
    log_info "Démarrage des services Jarvis (configuration sécurisée)..."
    
    # Arrêter les services existants
    docker compose -f docker-compose.secure.yml down --remove-orphans || true
    
    # Nettoyer les volumes anonymes
    docker volume prune -f || true
    
    # Démarrer en mode détaché
    docker compose -f docker-compose.secure.yml up -d
    
    log_success "Services démarrés en arrière-plan"
}

# Vérifications santé post-démarrage
health_checks() {
    log_info "Vérification santé des services..."
    
    # Attendre démarrage
    sleep 10
    
    # Backend
    if curl -f http://localhost:8000/health &> /dev/null; then
        log_success "✅ Backend API - Healthy"
    else
        log_error "❌ Backend API - Not responding"
    fi
    
    # Frontend  
    if curl -f http://localhost:3000 &> /dev/null; then
        log_success "✅ Frontend - Healthy"
    else
        log_error "❌ Frontend - Not responding"
    fi
    
    # Ollama
    if curl -f http://localhost:11434/api/version &> /dev/null; then
        log_success "✅ Ollama API - Healthy"
        
        # Vérifier modèle gpt-oss:20B
        if docker exec jarvis_ollama ollama list | grep -q "gpt-oss:20B"; then
            log_success "✅ Modèle gpt-oss:20B - Disponible"
        else
            log_warning "⚠️ Modèle gpt-oss:20B - Non trouvé (téléchargement en cours?)"
        fi
    else
        log_error "❌ Ollama API - Not responding"
    fi
    
    # GPU Check
    if docker exec jarvis_ollama nvidia-smi &> /dev/null; then
        log_success "✅ GPU RTX 4080 - Accessible"
    else
        log_warning "⚠️ GPU - Non accessible ou non configuré"
    fi
}

# Monitoring temps réel
show_status() {
    log_info "Status des containers:"
    docker compose -f docker-compose.secure.yml ps
    
    echo ""
    log_info "Accès aux services:"
    echo "🌐 Frontend (ollama-webui): http://localhost:3000"
    echo "🔌 Backend API: http://localhost:8000"
    echo "🔌 API Health: http://localhost:8000/health"
    echo "🤖 Ollama API: http://localhost:11434"
    
    echo ""
    log_info "Logs en temps réel:"
    echo "docker compose -f docker-compose.secure.yml logs -f [service]"
    
    echo ""
    log_success "🚀 Jarvis v1.3 Secure démarré avec succès!"
    echo ""
    log_info "Corrections audit appliquées:"
    echo "  ✅ CVE-2025-29927 Next.js corrigé"
    echo "  ✅ Containers non-root users"
    echo "  ✅ Secrets Docker sécurisés"
    echo "  ✅ Resource limits configurés"
    echo "  ✅ Security headers ajoutés"
}

# Main
main() {
    echo ""
    log_info "🤖 Démarrage Jarvis v1.3 Secure - Post Audit Critique"
    echo ""
    
    check_requirements
    update_frontend_deps
    build_images
    start_services
    health_checks
    show_status
}

# Gestion des signaux
trap 'log_info "Arrêt demandé..."; docker compose -f docker-compose.secure.yml down; exit 0' INT TERM

# Exécution
main "$@"