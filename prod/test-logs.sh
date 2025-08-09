#!/bin/bash
# Script de validation observabilité Jarvis v1.3

set -e

echo "🧪 Tests observabilité Jarvis v1.3"
echo "================================"

# 1) Validation config JSON
echo "1) Validation config logs..."
if command -v jq >/dev/null 2>&1; then
    jq . prod/logs-config.json >/dev/null && echo "✅ JSON config valide"
else
    python -c "import json; json.load(open('prod/logs-config.json'))" && echo "✅ JSON config valide"
fi

# 2) Test démarrage avec config
echo "2) Test démarrage backend avec config logs..."
export JARVIS_LOG_CONFIG="$(pwd)/prod/logs-config.json"
echo "   JARVIS_LOG_CONFIG=$JARVIS_LOG_CONFIG"

# Créer dossier logs si nécessaire
mkdir -p /tmp/jarvis-test-logs

# Remplacer le chemin pour test local
sed 's|/var/log/jarvis/app.jsonl|/tmp/jarvis-test-logs/app.jsonl|g' prod/logs-config.json > /tmp/logs-config-test.json
export JARVIS_LOG_CONFIG="/tmp/logs-config-test.json"

echo "   Démarrage backend (5s)..."
timeout 5s uvicorn backend.app:app --host 127.0.0.1 --port 8001 --workers 1 &
BACKEND_PID=$!
sleep 2

# 3) Tests API avec correlation
echo "3) Tests requêtes avec request-id..."

# Test health
echo "   GET /health"
RESP=$(curl -s -w "%{http_code}" -H "X-Request-ID: test-health-001" http://127.0.0.1:8001/health)
echo "   Status: $RESP"

# Test chat (si disponible)
echo "   POST /chat"
curl -s -H "Content-Type: application/json" -H "X-Request-ID: test-chat-001" \
     -d '{"message":"ping test","user_id":"test"}' \
     http://127.0.0.1:8001/chat > /dev/null || echo "   (endpoint chat non disponible)"

# Test metrics
echo "   GET /metrics"
curl -s -H "X-Request-ID: test-metrics-001" http://127.0.0.1:8001/metrics | head -5
echo "   ..."

# 4) Arrêt propre
echo "4) Arrêt backend..."
kill $BACKEND_PID 2>/dev/null || true
wait $BACKEND_PID 2>/dev/null || true

# 5) Vérification logs
echo "5) Vérification logs générés..."
if [ -f "/tmp/jarvis-test-logs/app.jsonl" ]; then
    echo "✅ Fichier logs JSON créé"
    echo "   Nombre de lignes: $(wc -l < /tmp/jarvis-test-logs/app.jsonl)"
    
    echo "   Exemples logs (3 premiers):"
    head -3 /tmp/jarvis-test-logs/app.jsonl | while read line; do
        if command -v jq >/dev/null 2>&1; then
            echo "   $(echo "$line" | jq -c '{ts,lvl,logger,request_id,path,msg}')"
        else
            echo "   $line" | cut -c1-80
        fi
    done
    
    # Vérifier présence champs obligatoires
    if grep -q '"request_id"' /tmp/jarvis-test-logs/app.jsonl; then
        echo "✅ request_id présent dans les logs"
    else
        echo "❌ request_id manquant dans les logs"
    fi
    
    if grep -q '"component":"api"' /tmp/jarvis-test-logs/app.jsonl; then
        echo "✅ component api détecté"
    fi
    
else
    echo "❌ Aucun fichier log JSON généré"
fi

# 6) Cleanup
rm -f /tmp/logs-config-test.json
rm -rf /tmp/jarvis-test-logs

echo ""
echo "🎯 Tests terminés"
echo "Pour tests WebSocket:"
echo "   websocat ws://127.0.0.1:8000/ws <<< '{\"message\":\"test\",\"user_id\":\"enzo\"}'"
echo ""
echo "Pour logs temps réel:"
echo "   tail -f /var/log/jarvis/app.jsonl | jq"