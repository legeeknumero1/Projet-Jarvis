#!/bin/bash

# Script de test avec Docker - Évite les doublons
# Instance #22 - Script intelligent de gestion containers

set -e

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'  
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE} Tests Docker Jarvis - Gestion Optimisée${NC}"
echo "============================================="

cd /home/enzo/Documents/Projet\ Jarvis

# 1. Vérification état actuel
echo -e "${YELLOW} État actuel des containers:${NC}"
docker ps -a --filter "name=jarvis_" --format "table {{.Names}}\t{{.Status}}\t{{.Size}}" || echo "Aucun container Jarvis"

# 2. Nettoyage préventif pour éviter doublons
echo -e "${YELLOW} Nettoyage préventif (éviter doublons)...${NC}"
docker ps -q --filter "name=jarvis_" | xargs -r docker stop
docker ps -aq --filter "name=jarvis_" | xargs -r docker rm
echo -e "${GREEN} Containers nettoyés${NC}"

# 3. Vérification docker-compose
echo -e "${YELLOW} Vérification Docker Compose...${NC}"
if command -v docker-compose &> /dev/null; then
    echo -e "${GREEN} docker-compose disponible: $(docker-compose --version)${NC}"
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    echo -e "${GREEN} docker compose (intégré) disponible${NC}"
    COMPOSE_CMD="docker compose"
else
    echo -e "${RED} Docker Compose non disponible${NC}"
    exit 1
fi

# 4. Test build ARCHITECTURE COMPLÈTE (7/7 services)
echo -e "${YELLOW} Test build architecture complète Jarvis...${NC}"

# Créer le réseau Jarvis si nécessaire
echo " Création réseau jarvis_network..."
docker network create jarvis_network --driver bridge --subnet=172.20.0.0/16 2>/dev/null || echo "Réseau existe déjà"

# Créer les volumes nécessaires
echo " Création volumes..."
docker volume create postgres_data 2>/dev/null || echo "Volume postgres_data existe"
docker volume create redis_data 2>/dev/null || echo "Volume redis_data existe"
docker volume create ollama_data 2>/dev/null || echo "Volume ollama_data existe"

# Build et démarrage avec docker-compose (architecture complète)
echo -e "${YELLOW} Build architecture 7/7 avec docker-compose...${NC}"
$COMPOSE_CMD build --parallel

echo -e "${GREEN} Build architecture complète réussi${NC}"

# 5. Démarrage architecture complète 7/7
echo -e "${YELLOW} Démarrage architecture complète (7 services)...${NC}"
$COMPOSE_CMD up -d

echo -e "${GREEN} Architecture 7/7 démarrée${NC}"

# 6. Tests de santé TOUS les services
echo -e "${YELLOW} Tests de santé architecture complète (attente 30s)...${NC}"
sleep 30

echo -e "${BLUE} État des 7 services:${NC}"
docker ps --filter "name=jarvis_" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Test des endpoints principaux
echo -e "${YELLOW} Tests endpoints architecture...${NC}"

# 1. PostgreSQL (172.20.0.100:5432)
echo -n " PostgreSQL: "
if docker exec jarvis_postgres pg_isready -U jarvis &>/dev/null; then
    echo -e "${GREEN} OK${NC}"
else
    echo -e "${RED} ERREUR${NC}"
fi

# 2. Redis (172.20.0.110:6379)
echo -n " Redis: "
if docker exec jarvis_redis redis-cli ping &>/dev/null; then
    echo -e "${GREEN} OK${NC}"
else
    echo -e "${RED} ERREUR${NC}"
fi

# 3. Ollama (172.20.0.30:11434)
echo -n " Ollama: "
if curl -f http://localhost:11434/api/tags &>/dev/null; then
    echo -e "${GREEN} OK${NC}"
else
    echo -e "${RED} ERREUR${NC}"
fi

# 4. STT API (172.20.0.10:8003)
echo -n " STT API: "
if curl -f http://localhost:8003/health &>/dev/null; then
    echo -e "${GREEN} OK${NC}"
else
    echo -e "${RED} ERREUR${NC}"
fi

# 5. TTS API (172.20.0.20:8002)
echo -n " TTS API: "
if curl -f http://localhost:8002/health &>/dev/null; then
    echo -e "${GREEN} OK${NC}"
else
    echo -e "${RED} ERREUR${NC}"
fi

# 6. Backend API (172.20.0.40:8000)
echo -n " Backend API: "
if curl -f http://localhost:8000/health &>/dev/null; then
    echo -e "${GREEN} OK${NC}"
else
    echo -e "${RED} ERREUR${NC}"
    echo "Logs Backend:"
    docker logs jarvis_backend --tail 10
fi

# 7. Interface (172.20.0.50:3000/8001)
echo -n " Interface: "
if curl -f http://localhost:3000 &>/dev/null || curl -f http://localhost:8001 &>/dev/null; then
    echo -e "${GREEN} OK${NC}"
else
    echo -e "${RED} ERREUR${NC}"
fi

# Test intégration WebSocket
echo -n " WebSocket Backend: "
if curl -f http://localhost:8000/ws &>/dev/null; then
    echo -e "${GREEN} OK${NC}"
else
    echo -e "${RED} ERREUR${NC}"
fi

# 7. Résumé final et logs en cas d'erreur
echo -e "${BLUE} RÉSUMÉ TEST ARCHITECTURE 7/7:${NC}"
RUNNING_CONTAINERS=$(docker ps --filter "name=jarvis_" --format "{{.Names}}" | wc -l)
echo "Containers actifs: $RUNNING_CONTAINERS/7"

if [ "$RUNNING_CONTAINERS" -eq 7 ]; then
    echo -e "${GREEN} ARCHITECTURE COMPLÈTE 7/7 OPÉRATIONNELLE !${NC}"
else
    echo -e "${RED} Architecture incomplète ($RUNNING_CONTAINERS/7)${NC}"
    echo -e "${YELLOW}Containers manquants ou en erreur:${NC}"
    
    # Vérifier quels containers manquent
    for service in "jarvis_postgres" "jarvis_redis" "jarvis_ollama" "jarvis_stt_api" "jarvis_tts_api" "jarvis_backend" "jarvis_interface"; do
        if ! docker ps --format "{{.Names}}" | grep -q "$service"; then
            echo -e "${RED} $service${NC}"
            if docker ps -a --format "{{.Names}}" | grep -q "$service"; then
                echo "   Logs $service:"
                docker logs "$service" --tail 5 2>/dev/null || echo "   Pas de logs disponibles"
            fi
        fi
    done
fi

# 8. Option nettoyage après test (demande à l'utilisateur)
echo ""
echo -e "${YELLOW} Nettoyage après test ?${NC}"
echo "Les 7 services restent actifs pour utilisation."
echo "Pour les arrêter: $COMPOSE_CMD down"
echo "Pour rebuild propre: ./scripts/manage-containers.sh rebuild"

# 9. Statistiques espace
echo -e "${BLUE} Utilisation espace Docker après test complet:${NC}"
docker system df

echo -e "${GREEN} Test architecture complète 7/7 terminé !${NC}"
echo ""
echo -e "${BLUE} Conseils:${NC}"
echo "- Architecture 7/7 testée : PostgreSQL + Redis + Ollama + STT + TTS + Backend + Interface"
echo "- Services actifs sur : 5432, 6379, 11434, 8003, 8002, 8000, 3000/8001"
echo "- Pour arrêter: $COMPOSE_CMD down"
echo "- Pour rebuild complet: ./scripts/manage-containers.sh rebuild"
echo "- Monitoring continu: docker stats"