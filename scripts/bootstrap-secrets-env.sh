#!/bin/bash
# bootstrap-secrets-env.sh
# Automates secret generation via jarvis-secretsd and prepares .env for Docker Compose

set -e

SECRETSD_URL="http://127.0.0.1:8081"
ENV_FILE=".env"

echo "🚀 Bootstrapping Jarvis Secrets..."

# Check if jarvis-secretsd is running, if not, try to start it locally
if ! curl -s "$SECRETSD_URL/healthz" > /dev/null; then
    echo "⚠️ jarvis-secretsd is not running at $SECRETSD_URL"
    echo "💡 Please start it with: cd jarvis-secretsd && ./target/release/jarvis-secretsd --config config.toml &"
    echo "   Wait a few seconds and try again."
    exit 1
fi

fetch_and_append() {
    local secret_name=$1
    local env_var=$2
    
    echo "🔑 Fetching/Generating $secret_name..."
    local value=$(curl -s -H "X-Jarvis-Client: admin" "$SECRETSD_URL/secret/$secret_name" | jq -r '.value')
    
    if [ -n "$value" ] && [ "$value" != "null" ]; then
        # Check if already exists in .env, if so replace, else append
        if grep -q "^$env_var=" "$ENV_FILE" 2>/dev/null; then
            sed -i "s|^$env_var=.*|$env_var=$value|" "$ENV_FILE"
        else
            echo "$env_var=$value" >> "$ENV_FILE"
        fi
    else
        echo "❌ Failed to fetch $secret_name"
    fi
}

# Ensure .env exists
touch "$ENV_FILE"

# Core Secrets
fetch_and_append "postgres_password" "POSTGRES_PASSWORD"
fetch_and_append "redis_password" "REDIS_PASSWORD"
fetch_and_append "database_url" "DATABASE_URL"
fetch_and_append "jwt_secret_key" "JWT_SECRET"
fetch_and_append "jarvis_encryption_key" "JARVIS_ENCRYPTION_KEY"

# Database Configuration (Fixed defaults)
grep -q "^POSTGRES_USER=" "$ENV_FILE" || echo "POSTGRES_USER=jarvis" >> "$ENV_FILE"
grep -q "^POSTGRES_DB=" "$ENV_FILE" || echo "POSTGRES_DB=jarvis_db" >> "$ENV_FILE"

# Sync Timescale with Postgres password for simplicity
grep -q "^TIMESCALE_PASSWORD=" "$ENV_FILE" || echo "TIMESCALE_PASSWORD=\${POSTGRES_PASSWORD}" >> "$ENV_FILE"
grep -q "^TIMESCALE_USER=" "$ENV_FILE" || echo "TIMESCALE_USER=jarvis" >> "$ENV_FILE"
grep -q "^TIMESCALE_DB=" "$ENV_FILE" || echo "TIMESCALE_DB=jarvis_timeseries" >> "$ENV_FILE"

echo "✅ .env file updated with secrets from jarvis-secretsd."
echo "🐳 You can now run: docker-compose up -d"
