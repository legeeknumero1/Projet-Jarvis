#!/bin/bash
# Script démarrage production Jarvis avec graceful shutdown

set -euo pipefail

echo "🚀 Démarrage Jarvis Production v1.3"

# Vérifier prérequis
if [[ ! -f docker-compose.prod.yml ]]; then
    echo "❌ docker-compose.prod.yml manquant"
    exit 1
fi

if [[ ! -f secrets/api_key.txt ]]; then
    echo "❌ Secrets non configurés - exécuter setup-secrets.sh"
    exit 1
fi

# Build frontend optimisé
echo "📦 Build frontend production..."
cd ../frontend
npm ci --production
npm run build
cd ../prod

# Démarrer stack
echo "🐳 Démarrage containers Docker..."
docker-compose -f docker-compose.prod.yml up -d

# Attendre que les services soient prêts
echo "⏳ Attente readiness services..."
for i in {1..30}; do
    if curl -sf http://localhost/ready >/dev/null 2>&1; then
        echo "✅ Services prêts"
        break
    fi
    echo "⏳ Tentative $i/30..."
    sleep 2
done

# Vérifier status final
echo "🔍 Vérification status final..."
curl -s http://localhost/health | jq .

echo "
🎉 Jarvis Production démarré !

📊 URLs:
- Application: https://jarvis.example.com
- Health: https://jarvis.example.com/health  
- Ready: https://jarvis.example.com/ready
- Metrics: https://jarvis.example.com/metrics

🛑 Pour arrêter:
docker-compose -f docker-compose.prod.yml down
"

# Trap pour graceful shutdown
trap 'echo "🛑 Arrêt graceful..."; docker-compose -f docker-compose.prod.yml down; exit 0' SIGTERM SIGINT