#!/bin/bash

# Script de gestion optimisée des containers Jarvis
# Évite les doublons et optimise l'espace disque

set -e

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.yml"
PROJECT_NAME="jarvis"

echo -e "${BLUE}🐳 Script de gestion containers Jarvis${NC}"
echo "=================================================="

# Fonction de nettoyage
cleanup_containers() {
    echo -e "${YELLOW}🧹 Nettoyage des containers existants...${NC}"
    
    # Arrêter tous les containers Jarvis
    echo "📄 Arrêt des containers Jarvis..."
    docker ps -q --filter "name=jarvis_" | xargs -r docker stop
    
    # Supprimer tous les containers Jarvis
    echo "🗑️ Suppression des containers Jarvis..."
    docker ps -aq --filter "name=jarvis_" | xargs -r docker rm
    
    echo -e "${GREEN}✅ Containers nettoyés${NC}"
}

# Fonction de nettoyage des images
cleanup_images() {
    echo -e "${YELLOW}🖼️ Nettoyage des images orphelines...${NC}"
    
    # Supprimer les images dangereuses (non taguées)
    echo "🗑️ Suppression images <none>..."
    docker images --filter "dangling=true" -q | xargs -r docker rmi
    
    # Nettoyer le cache Docker
    echo "🧹 Nettoyage cache Docker..."
    docker system prune -f
    
    echo -e "${GREEN}✅ Images nettoyées${NC}"
}

# Fonction de build optimisé
build_services() {
    echo -e "${YELLOW}🔨 Build des services...${NC}"
    
    # Build avec cache et parallélisation
    docker-compose build --parallel --no-cache
    
    echo -e "${GREEN}✅ Build terminé${NC}"
}

# Fonction de démarrage
start_services() {
    echo -e "${YELLOW}🚀 Démarrage des services...${NC}"
    
    # Créer le réseau si nécessaire
    docker network create jarvis_network --driver bridge --subnet=172.20.0.0/16 2>/dev/null || true
    
    # Créer les volumes si nécessaire
    docker volume create postgres_data 2>/dev/null || true
    docker volume create redis_data 2>/dev/null || true
    docker volume create ollama_data 2>/dev/null || true
    
    # Démarrer en détaché
    docker-compose up -d
    
    echo -e "${GREEN}✅ Services démarrés${NC}"
}

# Fonction d'état
show_status() {
    echo -e "${BLUE}📊 État des containers:${NC}"
    docker ps --filter "name=jarvis_" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    echo -e "\n${BLUE}💾 Utilisation espace Docker:${NC}"
    docker system df
}

# Fonction complète (recommandée)
full_rebuild() {
    echo -e "${RED}🔄 REBUILD COMPLET (nettoyage + build + start)${NC}"
    cleanup_containers
    cleanup_images
    build_services
    start_services
    show_status
    echo -e "${GREEN}🎉 Rebuild complet terminé !${NC}"
}

# Menu principal
case "${1:-}" in
    "clean")
        cleanup_containers
        ;;
    "clean-all")
        cleanup_containers
        cleanup_images
        ;;
    "build")
        build_services
        ;;
    "start")
        start_services
        ;;
    "restart")
        cleanup_containers
        start_services
        ;;
    "status")
        show_status
        ;;
    "rebuild"|"")
        full_rebuild
        ;;
    "stop")
        echo -e "${YELLOW}🛑 Arrêt des services...${NC}"
        docker-compose down
        echo -e "${GREEN}✅ Services arrêtés${NC}"
        ;;
    *)
        echo "Usage: $0 [clean|clean-all|build|start|restart|status|rebuild|stop]"
        echo ""
        echo "Commandes:"
        echo "  clean     - Nettoyer les containers Jarvis"
        echo "  clean-all - Nettoyer containers + images orphelines"
        echo "  build     - Build des services"
        echo "  start     - Démarrer les services"
        echo "  restart   - Nettoyer + redémarrer"
        echo "  status    - Afficher l'état"
        echo "  rebuild   - Rebuild complet (recommandé)"
        echo "  stop      - Arrêter tous les services"
        echo ""
        echo "Usage recommandé: $0 rebuild"
        exit 1
        ;;
esac

echo -e "${GREEN}✨ Terminé !${NC}"