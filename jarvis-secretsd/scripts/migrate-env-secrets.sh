#!/bin/bash
# Migrate secrets from .env file to jarvis-secretsd vault

set -e

SECRETSD_URL="${SECRETSD_URL:-http://127.0.0.1:8081}"
CLIENT_ID="${CLIENT_ID:-admin}"
ENV_FILE="${1:-.env}"

if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Error: $ENV_FILE not found"
    exit 1
fi

echo "🔐 Migrating secrets from $ENV_FILE to jarvis-secretsd"
echo "📍 Target: $SECRETSD_URL"
echo ""

# Check if secretsd is running
if ! curl -sf "$SECRETSD_URL/healthz" >/dev/null; then
    echo "❌ Error: jarvis-secretsd not reachable at $SECRETSD_URL"
    exit 1
fi

# Read .env and extract secrets
while IFS='=' read -r key value || [ -n "$key" ]; do
    # Skip comments and empty lines
    [[ "$key" =~ ^#.*$ ]] && continue
    [[ -z "$key" ]] && continue

    # Remove quotes from value
    value=$(echo "$value" | sed -e 's/^"//' -e 's/"$//' -e "s/^'//" -e "s/'$//")

    # Convert to lowercase for secret name
    secret_name=$(echo "$key" | tr '[:upper:]' '[:lower:]')

    echo "⏳ Migrating: $key -> $secret_name"

    # Create secret via API
    response=$(curl -s -w "\n%{http_code}" -X POST \
        -H "X-Jarvis-Client: $CLIENT_ID" \
        -H "Content-Type: application/json" \
        -d "{\"name\":\"$secret_name\",\"value\":\"$value\"}" \
        "$SECRETSD_URL/secret")

    http_code=$(echo "$response" | tail -n1)

    if [ "$http_code" = "201" ] || [ "$http_code" = "200" ]; then
        echo "✅ Migrated: $secret_name"
    else
        echo "❌ Failed: $secret_name (HTTP $http_code)"
    fi

done < "$ENV_FILE"

echo ""
echo "✅ Migration complete!"
echo ""
echo "Next steps:"
echo "1. Verify secrets: jarvis-secrets list"
echo "2. Update docker-compose.yml to remove .env references"
echo "3. Update services to fetch secrets from secretsd API"
echo "4. Backup .env file and remove from repository"
