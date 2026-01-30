#!/bin/bash
set -e

SECRETSD_URL="${SECRETSD_URL:-https://jarvis_secretsd:8081}"
CLIENT_ID="${CLIENT_ID:-backend}"

echo "[fetch-secrets] Fetching secrets from $SECRETSD_URL..."

# Fetch a secret from jarvis-secretsd using mTLS and export it
fetch_and_export() {
    local secret_name=$1
    local env_var=$2
    local client_cert="/etc/jarvis/certs/pki/issued/backend.crt"
    local client_key="/etc/jarvis/certs/pki/private/backend.key"
    local ca_cert="/etc/jarvis/certs/pki/ca/ca.crt"

    # Use curl with mTLS certificates
    local val=$(curl -s --cacert "$ca_cert" --cert "$client_cert" --key "$client_key" \
        -H "X-Jarvis-Client: $CLIENT_ID" \
        "$SECRETSD_URL/secret/$secret_name" | jq -r '.value // empty')
    
    if [ -n "$val" ]; then
        export "$env_var"="$val"
        echo "[fetch-secrets] Loaded $env_var"
    else
        echo "[fetch-secrets] WARNING: Failed to fetch $secret_name"
    fi
}

# Fetch JWT secrets
fetch_and_export "jwt_secret_key" "JWT_SECRET"
fetch_and_export "jwt_algorithm" "JWT_ALGORITHM"
fetch_and_export "jwt_expiration_hours" "JWT_EXPIRATION_HOURS"

# Fetch database secrets
fetch_and_export "postgres_password" "POSTGRES_PASSWORD"
fetch_and_export "redis_password" "REDIS_PASSWORD"
fetch_and_export "database_url" "DATABASE_URL"

# Fetch API keys
fetch_and_export "brave_api_key" "BRAVE_API_KEY"
fetch_and_export "openweather_api_key" "OPENWEATHER_API_KEY"
fetch_and_export "jarvis_encryption_key" "JARVIS_ENCRYPTION_KEY"
fetch_and_export "jarvis_internal_key" "JARVIS_INTERNAL_KEY"

# Fetch other configuration
fetch_and_export "ollama_base_url" "OLLAMA_BASE_URL"
fetch_and_export "qdrant_url" "QDRANT_URL"

echo "[fetch-secrets] All secrets loaded successfully"

# Execute the main command
exec "$@"