#!/bin/bash

# Script de démarrage manuel pour l'architecture Jarvis "poupée russe"
# Compatible avec Docker sans docker-compose

echo "🚀 Démarrage de l'architecture Jarvis (poupée russe)"
echo "====================================================="

# Création du réseau jarvis_network
echo "🌐 Création du réseau jarvis_network..."
docker network create --driver bridge --subnet=172.20.0.0/16 jarvis_network

# Création des volumes
echo "💾 Création des volumes..."
docker volume create postgres_data
docker volume create redis_data  
docker volume create ollama_data

# Build des images personnalisées
echo "🔨 Build des images..."
docker build -t jarvis_backend ./backend
docker build -t jarvis_stt ./services/stt
docker build -t jarvis_tts ./services/tts
docker build -t jarvis_interface ./services/interface

# Démarrage des services de support
echo "🗄️ Démarrage PostgreSQL..."
docker run -d \
  --name jarvis_postgres \
  --network jarvis_network \
  --ip 172.20.0.100 \
  -e POSTGRES_DB=jarvis_db \
  -e POSTGRES_USER=jarvis \
  -e POSTGRES_PASSWORD=jarvis \
  -v postgres_data:/var/lib/postgresql/data \
  -v ./backend/db/init.sql:/docker-entrypoint-initdb.d/init.sql \
  --restart unless-stopped \
  postgres:15

echo "⚡ Démarrage Redis..."
docker run -d \
  --name jarvis_redis \
  --network jarvis_network \
  --ip 172.20.0.110 \
  -v redis_data:/data \
  --restart unless-stopped \
  redis:7-alpine

echo "🤖 Démarrage Ollama..."
docker run -d \
  --name jarvis_ollama \
  --network jarvis_network \
  --ip 172.20.0.30 \
  -p 11434:11434 \
  -v ollama_data:/root/.ollama \
  -e OLLAMA_ORIGINS=* \
  -e OLLAMA_HOST=0.0.0.0 \
  --restart unless-stopped \
  ollama/ollama:latest

# Attendre que les services de support soient prêts
echo "⏳ Attente des services de support..."
sleep 10

# Test de connectivité des services
echo "🔍 Test de connectivité..."
docker exec jarvis_postgres pg_isready -U jarvis
docker exec jarvis_redis redis-cli ping

# Démarrage des services principaux dans l'ordre du schéma
echo "🎤 Démarrage STT API (Container 1)..."
docker run -d \
  --name jarvis_stt_api \
  --network jarvis_network \
  --ip 172.20.0.10 \
  -p 8003:8003 \
  -e SERVICE_NAME=stt-api \
  -e STT_MODEL_PATH=/app/models/stt \
  -e BACKEND_API_URL=http://172.20.0.40:8000 \
  -v ./services/stt:/app \
  -v ./models/stt:/app/models/stt \
  -v ./logs:/app/logs \
  --restart unless-stopped \
  jarvis_stt

echo "🔊 Démarrage TTS API (Container 2)..."
docker run -d \
  --name jarvis_tts_api \
  --network jarvis_network \
  --ip 172.20.0.20 \
  -p 8002:8002 \
  -e SERVICE_NAME=tts-api \
  -e TTS_MODEL_PATH=/app/models/tts \
  -e BACKEND_API_URL=http://172.20.0.40:8000 \
  -v ./services/tts:/app \
  -v ./models/tts:/app/models/tts \
  -v ./logs:/app/logs \
  --restart unless-stopped \
  jarvis_tts

echo "🧠 Démarrage Backend API (Container 4)..."
docker run -d \
  --name jarvis_backend \
  --network jarvis_network \
  --ip 172.20.0.40 \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://jarvis:jarvis@172.20.0.100:5432/jarvis_db \
  -e REDIS_URL=redis://172.20.0.110:6379 \
  -e OLLAMA_BASE_URL=http://172.20.0.30:11434 \
  -e TTS_API_URL=http://172.20.0.20:8002 \
  -e STT_API_URL=http://172.20.0.10:8003 \
  -e INTERFACE_URL=http://172.20.0.50:8001 \
  -e MEMORY_UPDATE_INTERVAL=604800 \
  -e MEMORY_RETENTION_DAYS=365 \
  -v ./backend:/app \
  -v ./models:/app/models \
  -v ./logs:/app/logs \
  -v ./data:/app/data \
  -v ./memory:/app/memory \
  --restart unless-stopped \
  jarvis_backend

echo "🌐 Démarrage Interface (Container 5)..."
docker run -d \
  --name jarvis_interface \
  --network jarvis_network \
  --ip 172.20.0.50 \
  -p 3000:3000 \
  -p 8001:8001 \
  -e REACT_APP_API_URL=http://localhost:8000 \
  -e REACT_APP_WS_URL=ws://localhost:8001 \
  -e BACKEND_API_URL=http://172.20.0.40:8000 \
  -e TTS_API_URL=http://172.20.0.20:8002 \
  -e STT_API_URL=http://172.20.0.10:8003 \
  -v ./services/interface:/app \
  -v ./frontend:/app/frontend \
  --restart unless-stopped \
  jarvis_interface

# Setup des modèles Ollama
echo "📥 Installation des modèles Ollama..."
sleep 5
docker exec jarvis_ollama ollama pull llama3.1:latest
docker exec jarvis_ollama ollama pull llama3.2:1b

echo ""
echo "✅ Architecture Jarvis poupée russe démarrée !"
echo "================================================"
echo "🎤 STT API:       http://localhost:8003"
echo "🔊 TTS API:       http://localhost:8002"
echo "🤖 Ollama:        http://localhost:11434"
echo "🧠 Backend API:   http://localhost:8000"
echo "🌐 Interface:     http://localhost:3000"
echo "🔌 WebSocket:     ws://localhost:8001"
echo "================================================"
echo ""
echo "📊 Status des containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"