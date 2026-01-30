#!/bin/bash
set -e

# Use CLIENT_ID from env, default to postgres if not set
CLIENT=${CLIENT_ID:-postgres}
# DIRECT IP for maximum reliability during DNS bootstrap
SECRETSD_IP="172.20.0.5"

# mTLS Configuration
CA_CERT="/etc/jarvis/certs/pki/ca/ca.crt"
# Try to find a specific cert for the client, otherwise fallback or fail
CLIENT_CERT="/etc/jarvis/certs/pki/issued/${CLIENT}.crt"
CLIENT_KEY="/etc/jarvis/certs/pki/private/${CLIENT}.key"

# Fallback to backend cert if specific cert missing (for dev/testing only)
if [ ! -f "$CLIENT_CERT" ]; then
    echo "[db-secrets] WARNING: No specific cert for $CLIENT, trying backend cert..."
    CLIENT_CERT="/etc/jarvis/certs/pki/issued/backend.crt"
    CLIENT_KEY="/etc/jarvis/certs/pki/private/backend.key"
fi

# Wait for secretsd to be ready (HTTPS + mTLS)
echo "[db-secrets] Checking availability of https://$SECRETSD_IP:8081..."
until curl -s --cacert "$CA_CERT" --cert "$CLIENT_CERT" --key "$CLIENT_KEY" \
    "https://$SECRETSD_IP:8081/healthz" > /dev/null; do
  echo "[db-secrets] Waiting for jarvis-secretsd at $SECRETSD_IP (mTLS)..."
  sleep 2
done

echo "[db-secrets] Fetching database password for client '$CLIENT'..."
# Fetch the password from secretsd
URL="https://$SECRETSD_IP:8081/secret/${CLIENT}_password?client_id=$CLIENT"
if [ "$CLIENT" == "postgres" ]; then
    # Postgres needs 'postgres_password' specifically if mapped that way in secretsd
    URL="https://$SECRETSD_IP:8081/secret/postgres_password?client_id=$CLIENT"
fi

echo "[db-secrets] Requesting: $URL"

# We MUST include the X-Jarvis-Client header!
RESPONSE=$(curl -s --cacert "$CA_CERT" --cert "$CLIENT_CERT" --key "$CLIENT_KEY" \
    -H "X-Jarvis-Client: $CLIENT" "$URL")
DB_PASS=$(echo "$RESPONSE" | jq -r .value)

if [ "$DB_PASS" == "null" ] || [ -z "$DB_PASS" ]; then
  echo "[db-secrets] ERROR: Failed to fetch password from secretsd"
  echo "[db-secrets] DEBUG RESPONSE: $RESPONSE"
  exit 1
fi

echo "[db-secrets] Secret loaded into memory successfully"
export POSTGRES_PASSWORD="$DB_PASS"

# Execute the original entrypoint
exec docker-entrypoint.sh "$@"
