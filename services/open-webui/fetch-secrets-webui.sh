#!/bin/bash
set -e

SECRETSD_URL="${SECRETSD_URL:-https://jarvis_secretsd:8081}"
CLIENT_ID="${CLIENT_ID:-open-webui}"

# Internal mTLS certificates (mounted via docker-compose)
CLIENT_CERT="/etc/jarvis/certs/pki/issued/backend.crt"
CLIENT_KEY="/etc/jarvis/certs/pki/private/backend.key"
CA_CERT="/etc/jarvis/certs/pki/ca/ca.crt"

echo "[fetch-secrets-webui] Fetching JWT secret from $SECRETSD_URL..."
JWT_SECRET=$(curl -s --cacert "$CA_CERT" --cert "$CLIENT_CERT" --key "$CLIENT_KEY" \
    -H "X-Jarvis-Client: $CLIENT_ID" \
    "$SECRETSD_URL/secret/jwt_secret_key" | jq -r '.value // empty')

if [ -n "$JWT_SECRET" ]; then
    export OPENAI_API_KEYS="$JWT_SECRET"
    export AUDIO_STT_OPENAI_API_KEY="$JWT_SECRET"
    export AUDIO_TTS_OPENAI_API_KEY="$JWT_SECRET"
    echo "[fetch-secrets-webui] JWT Secret loaded and keys exported"
else
    echo "[fetch-secrets-webui] ERROR: Failed to fetch JWT secret"
    # Fallback to the internal trust key for emergency access
    export OPENAI_API_KEYS="sk-jarvis-internal-trust-key"
    export AUDIO_STT_OPENAI_API_KEY="sk-jarvis-internal-trust-key"
    export AUDIO_TTS_OPENAI_API_KEY="sk-jarvis-internal-trust-key"
fi

# Execute the original start script
exec bash start.sh