#!/bin/bash
set -e

SECRETSD_URL="${SECRETSD_URL:-http://jarvis-secretsd:8081}"
CLIENT_ID="${CLIENT_ID:-backend}"

echo "[fetch-secrets] Fetching secrets from $SECRETSD_URL..."

# Function to fetch a secret and export it
fetch_secret() {
    local secret_name=$1
    local env_var_name=${2:-$(echo $secret_name | tr '[:lower:]' '[:upper:]')}

    local value=$(curl -s -H "X-Jarvis-Client: $CLIENT_ID" \
        "$SECRETSD_URL/secret/$secret_name" | jq -r '.value // empty')

    if [ -n "$value" ]; then
        export "$env_var_name=$value"
        echo "[fetch-secrets] Loaded $env_var_name from $secret_name"
    else
        echo "[fetch-secrets] WARNING: Failed to fetch $secret_name" >&2
    fi
}

# Fetch JWT secrets
fetch_secret "jwt_secret_key" "JWT_SECRET"
fetch_secret "jwt_algorithm" "JWT_ALGORITHM"
fetch_secret "jwt_expiration_hours" "JWT_EXPIRATION_HOURS"

# Fetch database secrets
fetch_secret "postgres_password" "POSTGRES_PASSWORD"
fetch_secret "redis_password" "REDIS_PASSWORD"
fetch_secret "database_url" "DATABASE_URL"

# Fetch API keys
fetch_secret "brave_api_key" "BRAVE_API_KEY"
fetch_secret "openweather_api_key" "OPENWEATHER_API_KEY"
fetch_secret "jarvis_encryption_key" "JARVIS_ENCRYPTION_KEY"
fetch_secret "gemini_api_key" "GEMINI_API_KEY"

# Fetch other configuration
fetch_secret "ollama_base_url" "OLLAMA_BASE_URL"
fetch_secret "qdrant_url" "QDRANT_URL"

# ============================================================================
# AUTOMATED IN-MEMORY TLS LOAD - TRANSPARENT, AUTOMATIC & SECURE
# ============================================================================
# Récupération automatique et écriture sécurisée en RAM vive (tmpfs) des certificats
# TLS depuis le Secrets Daemon, sans jamais toucher au stockage persistant physique.
# ============================================================================
mkdir -p /tmp/secrets
chmod 700 /tmp/secrets

echo "[fetch-secrets] Fetching TLS certificates from secrets daemon..."
cert_val=$(curl -s -H "X-Jarvis-Client: $CLIENT_ID" "$SECRETSD_URL/secret/ssl_server_crt" | jq -r '.value // empty')
if [ -n "$cert_val" ] && [[ "$cert_val" == *"-----BEGIN"* ]]; then
    echo "$cert_val" > /tmp/secrets/server.crt
    chmod 600 /tmp/secrets/server.crt
    export TLS_CERT_PATH=/tmp/secrets/server.crt
    echo "[fetch-secrets]  [SUCCESS] SSL certificate loaded to in-memory RAM"
else
    echo "[fetch-secrets]  [WARNING] ssl_server_crt not found or invalid format, falling back to disk certs"
fi

key_val=$(curl -s -H "X-Jarvis-Client: $CLIENT_ID" "$SECRETSD_URL/secret/ssl_server_key" | jq -r '.value // empty')
if [ -n "$key_val" ] && [[ "$key_val" == *"-----BEGIN"* ]]; then
    echo "$key_val" > /tmp/secrets/server.key
    chmod 600 /tmp/secrets/server.key
    export TLS_KEY_PATH=/tmp/secrets/server.key
    echo "[fetch-secrets]  [SUCCESS] SSL private key loaded to in-memory RAM"
else
    echo "[fetch-secrets]  [WARNING] ssl_server_key not found or invalid format, falling back to disk keys"
fi

echo "[fetch-secrets] All secrets and RAM certificates loaded successfully"

# Execute the main command
exec "$@"
