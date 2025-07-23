#!/bin/bash
# Docker Compose V2 Wrapper Script
# Utilise les commandes docker natives pour gérer les services

COMPOSE_FILE=${1:-docker-compose.yml}
COMMAND=${2:-up}

case "$COMMAND" in
    "up")
        echo "🚀 Démarrage services Jarvis via Docker native..."
        docker network create jarvis_network --driver bridge --subnet 172.20.0.0/16 || true
        
        # PostgreSQL
        docker run -d --name jarvis_postgres --network jarvis_network --ip 172.20.0.100 \
            -e POSTGRES_DB=jarvis_db -e POSTGRES_USER=jarvis -e POSTGRES_PASSWORD=jarvis \
            -v postgres_data:/var/lib/postgresql/data \
            --restart unless-stopped postgres:15
        
        # Redis
        docker run -d --name jarvis_redis --network jarvis_network --ip 172.20.0.110 \
            -v redis_data:/data --restart unless-stopped redis:7-alpine
        
        # Ollama
        docker run -d --name jarvis_ollama --network jarvis_network --ip 172.20.0.30 \
            -p 11434:11434 -v ollama_data:/root/.ollama \
            --restart unless-stopped ollama/ollama:latest
        
        echo "✅ Services de base démarrés"
        ;;
    "down")
        echo "🛑 Arrêt services Jarvis..."
        docker stop jarvis_postgres jarvis_redis jarvis_ollama || true
        docker rm jarvis_postgres jarvis_redis jarvis_ollama || true
        ;;
    "ps")
        docker ps --filter "name=jarvis_"
        ;;
    *)
        echo "Usage: $0 [compose-file] [up|down|ps]"
        ;;
esac