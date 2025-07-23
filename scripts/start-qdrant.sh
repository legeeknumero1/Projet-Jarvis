#!/bin/bash
# Démarrer Qdrant avec volumes persistants

echo "🗄️ Démarrage Qdrant Vector Database..."

# Créer le volume si nécessaire
docker volume create qdrant_data || true

# Démarrer Qdrant
docker run -d \
  --name jarvis_qdrant \
  --network jarvis_network \
  --ip 172.20.0.120 \
  -p 6333:6333 \
  -p 6334:6334 \
  -v qdrant_data:/qdrant/storage \
  --restart unless-stopped \
  -e QDRANT__SERVICE__HTTP_PORT=6333 \
  -e QDRANT__SERVICE__GRPC_PORT=6334 \
  -e QDRANT__STORAGE__PERFORMANCE__MAX_SEARCH_THREADS=4 \
  -e QDRANT__SERVICE__ENABLE_CORS=true \
  qdrant/qdrant:latest

echo "✅ Qdrant démarré sur http://localhost:6333"