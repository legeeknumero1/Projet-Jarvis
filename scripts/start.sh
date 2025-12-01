#!/bin/bash
set -e

# Configuration
SECRETSD_URL="http://127.0.0.1:8081"
CLIENT_ID="admin"

echo " Starting Jarvis Secrets Daemon (Docker)..."
docker-compose up -d jarvis-secretsd

echo " Waiting for secretsd to be healthy..."
# Wait loop
for i in {1..30}; do
    if curl -sf "$SECRETSD_URL/healthz" >/dev/null; then
        echo " jarvis-secretsd is healthy!"
        break
    fi
    echo "   Waiting... ($i/30)"
    sleep 1
done

if ! curl -sf "$SECRETSD_URL/healthz" >/dev/null; then
    echo " Failed to start jarvis-secretsd!"
    docker-compose logs jarvis-secretsd
    exit 1
fi

echo " Fetching secrets from jarvis-secretsd..."

# Function to fetch a secret
fetch_secret() {
    local name=$1
    local var_name=$2
    
    val=$(curl -s -H "X-Jarvis-Client: $CLIENT_ID" "$SECRETSD_URL/secret/$name" | grep -o '"value":"[^"]*"' | cut -d'"' -f4)
    
    if [ -n "$val" ]; then
        export "$var_name"="$val"
        echo " Loaded $name"
    else
        echo "  Warning: Could not fetch $name"
    fi
}

# Fetch critical infrastructure secrets
fetch_secret "postgres_password" "POSTGRES_PASSWORD"
fetch_secret "timescale_password" "TIMESCALE_PASSWORD"
fetch_secret "jwt_secret_key" "JWT_SECRET"
fetch_secret "home_assistant_token" "HOME_ASSISTANT_TOKEN"
fetch_secret "brave_api_key" "BRAVE_API_KEY"
fetch_secret "openweather_api_key" "OPENWEATHER_API_KEY"
fetch_secret "jarvis_api_key" "JARVIS_API_KEY"

# Fetch other secrets as needed by docker-compose
fetch_secret "postgres_user" "POSTGRES_USER"
fetch_secret "postgres_db" "POSTGRES_DB"
fetch_secret "timescale_user" "TIMESCALE_USER"
fetch_secret "timescale_db" "TIMESCALE_DB"

echo " Starting remaining services..."
docker-compose up -d

echo " Project started securely (100% Docker)!"
