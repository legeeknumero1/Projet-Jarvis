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

# Fetch other configuration
fetch_secret "ollama_base_url" "OLLAMA_BASE_URL"
fetch_secret "qdrant_url" "QDRANT_URL"

echo "[fetch-secrets] All secrets loaded successfully"

# Execute the main command
exec "$@"
