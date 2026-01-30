#!/bin/bash
# Bootstrap Script to generate/fetch secrets from jarvis-secretsd

SECRETSD_URL="http://127.0.0.1:8081"
ENV_FILE=".env"

echo " Bootstrapping Jarvis Secrets..."

# Function to fetch or trigger generation of a secret
fetch_and_append() {
    local secret_name=$1
    local env_var=$2
    
    echo " Fetching/Generating $secret_name..."
    # The daemon automatically generates known patterns on GET if not found
    local response=$(curl -s -H "X-Jarvis-Client: admin" "$SECRETSD_URL/secret/$secret_name")
    local value=$(echo "$response" | jq -r '.value // empty')
    
    if [ -n "$value" ] && [ "$value" != "null" ]; then
        # Check if var already exists in .env
        if grep -q "^$env_var=" "$ENV_FILE" 2>/dev/null; then
            # Update existing
            sed -i "s|^$env_var=.*|$env_var=$value|" "$ENV_FILE"
        else
            # Append new
            echo "$env_var=$value" >> "$ENV_FILE"
        fi
        echo " Success: $secret_name"
    else
        echo " Failure: Could not fetch $secret_name"
        echo " Response: $response"
    fi
}

# Ensure .env exists
touch "$ENV_FILE"

# List of secrets to bootstrap
fetch_and_append "postgres_password" "POSTGRES_PASSWORD"
fetch_and_append "redis_password" "REDIS_PASSWORD"
fetch_and_append "database_url" "DATABASE_URL"
fetch_and_append "jwt_secret_key" "JWT_SECRET"
fetch_and_append "jarvis_encryption_key" "JARVIS_ENCRYPTION_KEY"

echo " .env file updated."
echo " You can now run: docker-compose up -d"