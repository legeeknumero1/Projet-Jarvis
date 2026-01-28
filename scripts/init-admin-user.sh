#!/bin/bash
set -e

# ============================================================================
# Admin User Initialization Script
# ============================================================================
# This script creates the initial admin user with a secure random password
# Password is hashed with bcrypt and stored in PostgreSQL
# Plaintext password is stored in jarvis-secretsd for secure retrieval
# ============================================================================

echo "🔐 Jarvis Admin User Initialization"
echo "===================================="
echo ""

# Configuration
SECRETSD_URL="${SECRETSD_URL:-http://localhost:8081}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-jarvis_db}"
DB_USER="${DB_USER:-jarvis}"
ADMIN_USERNAME="${ADMIN_USERNAME:-admin}"

# Check if PostgreSQL password is available
if [ -z "$POSTGRES_PASSWORD" ]; then
    echo "❌ ERROR: POSTGRES_PASSWORD environment variable is not set"
    echo "   Please load secrets from jarvis-secretsd first"
    exit 1
fi

# Generate secure random password (32 characters, alphanumeric + special chars)
echo "📝 Generating secure random password..."
ADMIN_PASSWORD=$(openssl rand -base64 24 | tr -d "=+/" | cut -c1-32)

if [ -z "$ADMIN_PASSWORD" ]; then
    echo "❌ ERROR: Failed to generate password"
    exit 1
fi

echo "✅ Password generated: ${ADMIN_PASSWORD:0:4}****************************"
echo ""

# Hash password with bcrypt (using Python with bcrypt library)
echo "🔒 Hashing password with bcrypt..."
PASSWORD_HASH=$(python3 -c "
import bcrypt
import sys
password = sys.argv[1].encode('utf-8')
salt = bcrypt.gensalt(rounds=12)
hashed = bcrypt.hashpw(password, salt)
print(hashed.decode('utf-8'))
" "$ADMIN_PASSWORD")

if [ -z "$PASSWORD_HASH" ]; then
    echo "❌ ERROR: Failed to hash password"
    echo "   Make sure Python 3 and bcrypt are installed: pip3 install bcrypt"
    exit 1
fi

echo "✅ Password hashed successfully"
echo ""

# Check if admin user already exists
echo "🔍 Checking if admin user already exists..."
USER_EXISTS=$(PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -tAc \
    "SELECT COUNT(*) FROM users WHERE username = '$ADMIN_USERNAME';")

if [ "$USER_EXISTS" -gt 0 ]; then
    echo "⚠️  WARNING: Admin user '$ADMIN_USERNAME' already exists!"
    echo ""
    read -p "Do you want to reset the password? (yes/no): " RESET_CONFIRM

    if [ "$RESET_CONFIRM" != "yes" ]; then
        echo "❌ Aborted by user"
        exit 1
    fi

    echo ""
    echo "🔄 Resetting password for admin user..."
    PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<EOF
UPDATE users
SET password_hash = '$PASSWORD_HASH',
    updated_at = CURRENT_TIMESTAMP,
    is_active = true,
    is_admin = true
WHERE username = '$ADMIN_USERNAME';
EOF

    echo "✅ Admin password reset successfully"
else
    echo "📝 Creating admin user in database..."
    PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<EOF
INSERT INTO users (username, password_hash, email, full_name, is_active, is_admin)
VALUES (
    '$ADMIN_USERNAME',
    '$PASSWORD_HASH',
    'admin@jarvis.local',
    'Jarvis Administrator',
    true,
    true
);
EOF

    echo "✅ Admin user created successfully"
fi

echo ""

# Store password in jarvis-secretsd
echo "🔐 Storing admin password in jarvis-secretsd..."
RESPONSE=$(curl -s -X POST "$SECRETSD_URL/secret" \
    -H "X-Jarvis-Client: admin" \
    -H "Content-Type: application/json" \
    -d "{\"name\":\"admin_password\",\"value\":\"$ADMIN_PASSWORD\"}")

if echo "$RESPONSE" | grep -q '"success":true'; then
    echo "✅ Admin password stored in jarvis-secretsd"
else
    echo "⚠️  WARNING: Failed to store password in jarvis-secretsd"
    echo "   Response: $RESPONSE"
    echo "   You will need to store it manually"
fi

echo ""
echo "============================================"
echo "✅ Admin User Initialization Complete!"
echo "============================================"
echo ""
echo "Username: $ADMIN_USERNAME"
echo "Password: $ADMIN_PASSWORD"
echo ""
echo "⚠️  IMPORTANT: Save this password securely!"
echo "   This is the only time it will be displayed in plaintext."
echo "   The password is also stored in jarvis-secretsd under 'admin_password'"
echo ""
echo "You can retrieve it later with:"
echo "  curl -H \"X-Jarvis-Client: admin\" $SECRETSD_URL/secret/admin_password"
echo ""
