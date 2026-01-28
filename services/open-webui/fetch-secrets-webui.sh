#!/bin/bash
set -e

SECRETSD_URL="${SECRETSD_URL:-http://jarvis-secretsd:8081}"
CLIENT_ID="${CLIENT_ID:-open-webui}"

echo "[fetch-secrets-webui] Fetching JWT secret from $SECRETSD_URL..."

# Fetch JWT secret
JWT_VALUE=$(curl -s -H "X-Jarvis-Client: $CLIENT_ID" \
    "$SECRETSD_URL/secret/jwt_secret_key" | jq -r '.value // empty')

if [ -n "$JWT_VALUE" ]; then
    export WEBUI_SECRET_KEY="$JWT_VALUE"
    export AUDIO_STT_OPENAI_API_KEY="$JWT_VALUE"
    export AUDIO_TTS_OPENAI_API_KEY="$JWT_VALUE"
    echo "[fetch-secrets-webui] JWT secret loaded successfully"
else
    echo "[fetch-secrets-webui] WARNING: Failed to fetch JWT secret" >&2
fi

echo "[fetch-secrets-webui] Starting Open-WebUI with authenticated secrets..."

# Execute the main command (exports are already done above)
exec "$@"
