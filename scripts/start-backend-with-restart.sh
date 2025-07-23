#!/bin/bash
# Script pour démarrer le backend avec restart policy

cd /home/enzo/Documents/Projet\ Jarvis/backend

# Construire l'image backend si nécessaire
docker build -t jarvis-backend .

# Démarrer le container avec restart policy
docker run -d \
  --name jarvis_backend_with_restart \
  --network jarvis_network \
  --ip 172.20.0.40 \
  -p 8000:8000 \
  --restart unless-stopped \
  -e DATABASE_URL=postgresql://jarvis:jarvis@172.20.0.100:5432/jarvis_db \
  -e REDIS_URL=redis://172.20.0.110:6379 \
  -e OLLAMA_BASE_URL=http://172.20.0.30:11434 \
  -v $(pwd):/app \
  -v $(pwd)/logs:/app/logs \
  jarvis-backend

echo "✅ Backend démarré avec restart policy: unless-stopped"