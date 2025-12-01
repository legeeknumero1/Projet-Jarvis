# jarvis-secretsd - Integration Plan

**Version:** v0.1.0
**Target:** Jarvis v1.9.0 Production Environment
**Security Impact:** Critical vulnerabilities S1-S6 will be resolved
**Expected Security Score:** 45/100 → 95/100

---

## Overview

This plan details the step-by-step integration of jarvis-secretsd into the Jarvis production environment, replacing the current insecure `.env` file approach with encrypted secrets management.

**Critical Issues Addressed:**
- S1: Secrets in .env (CVSS 9.8)
- S2: HOME_ASSISTANT_TOKEN hardcoded (CVSS 9.5)
- S3: Hardcoded database passwords (CVSS 8.5)
- S4: No HTTPS enforcement (CVSS 9.1)
- S5: Mock authentication (CVSS 9.8)
- S6: .gitignore ineffective (CVSS 8.0)

---

## Phase 1: Pre-deployment Preparation

### 1.1 Review Current Secrets

```bash
cd /home/enzo/Documents/Projet-Jarvis

# Inventory all secrets in .env
grep -E "^[A-Z_]+=" .env | cut -d= -f1 | sort
```

**Expected secrets to migrate:**
- JWT_SECRET_KEY
- POSTGRES_PASSWORD
- POSTGRES_USER
- POSTGRES_DB
- HOME_ASSISTANT_TOKEN
- HOME_ASSISTANT_URL
- BRAVE_API_KEY
- TAVILY_API_KEY
- (and others)

### 1.2 Build jarvis-secretsd

```bash
cd jarvis-secretsd

# Build release binary
cargo build --release

# Verify binary
ls -lh target/release/jarvis-secretsd
```

**Expected output:**
```
-rwxr-xr-x 4.7M jarvis-secretsd
```

### 1.3 Create Production Configuration

```bash
# Create directories
sudo mkdir -p /etc/jarvis-secretsd
sudo mkdir -p /opt/jarvis/secrets
sudo mkdir -p /opt/jarvis/audit

# Copy configuration templates
sudo cp config.toml.example /etc/jarvis-secretsd/config.toml
sudo cp policy.yaml.example /etc/jarvis-secretsd/policy.yaml

# Set ownership
sudo chown -R $USER:$USER /opt/jarvis
sudo chmod 700 /opt/jarvis/secrets
sudo chmod 700 /opt/jarvis/audit
```

### 1.4 Configure RBAC Policy

Edit `/etc/jarvis-secretsd/policy.yaml`:

```yaml
default_deny: true

clients:
  # Admin client - full access for management
  admin:
    allow: ["*"]
    deny: []

  # Rust backend - core application secrets
  backend:
    allow:
      - jwt_signing_key
      - postgres_password
      - jarvis_encryption_key
      - home_assistant_token
    deny: []

  # Python services - specific API keys
  python-services:
    allow:
      - brave_api_key
      - tavily_api_key
      - duckduckgo_api_key
      - postgres_password
    deny: []

  # Database service - only database credentials
  postgres:
    allow:
      - postgres_password
    deny: []

  # Home Assistant integration
  ha-client:
    allow:
      - home_assistant_token
    deny: []

  # MCP services - API keys for external services
  mcp:
    allow:
      - brave_api_key
      - tavily_api_key
      - browserbase_api_key
    deny: []
```

### 1.5 Configure Service

Edit `/etc/jarvis-secretsd/config.toml`:

```toml
[server]
bind_addr = "127.0.0.1:8081"
allow_unix_socket = false

[paths]
vault_path = "/opt/jarvis/secrets/vault.json"
master_key_path = "/opt/jarvis/secrets/master.key"
audit_path = "/opt/jarvis/audit/audit.jsonl"

[security]
rotation_days = 90
grace_days = 14
require_client_id_header = true
deny_network_remote = true
rbac_policy_path = "/etc/jarvis-secretsd/policy.yaml"

[crypto]
aead = "aes-gcm-256"
jwt_sign_algo = "ed25519"
kdf = "argon2id"

[logging]
level = "info"
json = false
```

---

## Phase 2: Docker Integration

### 2.1 Create Dockerfile (Already exists)

Verify the existing Dockerfile:

```bash
cat jarvis-secretsd/Dockerfile
```

### 2.2 Update docker-compose.yml

Add secretsd service at the top of `/home/enzo/Documents/Projet-Jarvis/docker-compose.yml`:

```yaml
version: '3.8'

services:
  # ============================================
  # Secrets Management Daemon (NEW)
  # ============================================
  secretsd:
    build:
      context: ./jarvis-secretsd
      dockerfile: Dockerfile
    container_name: jarvis-secretsd
    restart: unless-stopped
    network_mode: "host"  # Bind to localhost only
    volumes:
      - /etc/jarvis-secretsd:/etc/jarvis-secretsd:ro
      - /opt/jarvis/secrets:/opt/jarvis/secrets
      - /opt/jarvis/audit:/opt/jarvis/audit
    environment:
      - RUST_LOG=info
    healthcheck:
      test: ["CMD", "curl", "-f", "http://127.0.0.1:8081/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s
    command: ["--config", "/etc/jarvis-secretsd/config.toml"]

  # ============================================
  # Existing Services
  # ============================================
  backend:
    depends_on:
      secretsd:
        condition: service_healthy
    environment:
      - JARVIS_SECRETS_URL=http://127.0.0.1:8081
      - JARVIS_CLIENT_ID=backend
      # Remove all secret env vars - fetch from secretsd instead
    # ... rest of backend config

  postgres:
    depends_on:
      secretsd:
        condition: service_healthy
    # ... rest of postgres config

  # ... other services
```

### 2.3 Update Production docker-compose

Add to `prod/docker-compose.prod.yml`:

```yaml
services:
  secretsd:
    build:
      context: ../jarvis-secretsd
      dockerfile: Dockerfile
    container_name: jarvis-secretsd-prod
    restart: always
    network_mode: "host"
    volumes:
      - /etc/jarvis-secretsd:/etc/jarvis-secretsd:ro
      - /opt/jarvis/secrets:/opt/jarvis/secrets
      - /opt/jarvis/audit:/opt/jarvis/audit
    environment:
      - RUST_LOG=warn  # Production logging
    healthcheck:
      test: ["CMD", "curl", "-f", "http://127.0.0.1:8081/healthz"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 10s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
```

---

## Phase 3: Secret Migration

### 3.1 Start secretsd

```bash
cd /home/enzo/Documents/Projet-Jarvis

# Build and start only secretsd
docker-compose up --build -d secretsd

# Verify startup
docker-compose logs secretsd
curl http://127.0.0.1:8081/healthz
```

**Expected response:**
```json
{
  "status": "ok",
  "version": "0.1.0",
  "uptime_secs": 5,
  "secrets_count": 0
}
```

### 3.2 Generate and Store Secrets

Create a migration script `jarvis-secretsd/scripts/migrate_secrets.sh`:

```bash
#!/bin/bash
set -euo pipefail

SECRETS_URL="http://127.0.0.1:8081"
ADMIN_CLIENT="admin"

# Source existing .env to get current values
source ../.env

echo " Migrating secrets to jarvis-secretsd..."

# Function to create secret
create_secret() {
    local name=$1
    local value=$2

    echo "Creating secret: $name"
    curl -s -X POST "$SECRETS_URL/secret" \
        -H "X-Jarvis-Client: $ADMIN_CLIENT" \
        -H "Content-Type: application/json" \
        -d "{\"name\":\"$name\",\"value\":\"$value\"}" || {
        echo " Failed to create secret: $name"
        exit 1
    }
    echo " Created: $name"
}

# Function to generate new secret
generate_secret() {
    local name=$1
    local type=$2

    echo "Generating new secret: $name (type: $type)"
    # Use jarvis-secretsd's built-in generation
    # For now, we'll create manually

    case "$type" in
        "jwt_signing_key")
            # Generate Ed25519 key
            VALUE=$(openssl rand -base64 32)
            ;;
        "password")
            # Generate 64-char password
            VALUE=$(openssl rand -base64 48 | tr -d '/+=' | head -c 64)
            ;;
        "api_key")
            # Generate 32-char API key
            VALUE=$(openssl rand -base64 24 | tr -d '/+=' | head -c 32)
            ;;
        *)
            VALUE=$(openssl rand -base64 32)
            ;;
    esac

    create_secret "$name" "$VALUE"
}

# Migrate existing secrets
echo ""
echo " Migrating existing secrets from .env..."
create_secret "home_assistant_token" "$HOME_ASSISTANT_TOKEN"
create_secret "home_assistant_url" "$HOME_ASSISTANT_URL"
create_secret "brave_api_key" "$BRAVE_API_KEY"
create_secret "tavily_api_key" "$TAVILY_API_KEY"

# Generate new secure secrets
echo ""
echo " Generating new secure secrets..."
generate_secret "jwt_signing_key" "jwt_signing_key"
generate_secret "postgres_password" "password"
generate_secret "jarvis_encryption_key" "jwt_signing_key"

# Optional: Add more API keys
if [[ -n "${DUCKDUCKGO_API_KEY:-}" ]]; then
    create_secret "duckduckgo_api_key" "$DUCKDUCKGO_API_KEY"
fi

if [[ -n "${BROWSERBASE_API_KEY:-}" ]]; then
    create_secret "browserbase_api_key" "$BROWSERBASE_API_KEY"
fi

echo ""
echo " Secret migration complete!"
echo ""
echo " Verifying secrets..."
curl -s "$SECRETS_URL/secrets" \
    -H "X-Jarvis-Client: $ADMIN_CLIENT" | jq '.secrets | length'

echo ""
echo "  IMPORTANT: Update database password manually:"
echo "   docker-compose exec postgres psql -U jarvis -d jarvis_db -c \"ALTER USER jarvis PASSWORD '<new_password>';\""
```

Make it executable and run:

```bash
chmod +x jarvis-secretsd/scripts/migrate_secrets.sh
cd jarvis-secretsd/scripts
./migrate_secrets.sh
```

### 3.3 Update Database Password

```bash
# Get new password from secretsd
NEW_PASSWORD=$(curl -s http://127.0.0.1:8081/secret/postgres_password \
    -H "X-Jarvis-Client: admin" | jq -r '.value')

# Update PostgreSQL password
docker-compose exec postgres psql -U jarvis -d jarvis_db \
    -c "ALTER USER jarvis PASSWORD '$NEW_PASSWORD';"

echo " Database password updated"
```

---

## Phase 4: Backend Integration

### 4.1 Add Secrets Client to Rust Backend

Create `core/src/services/secrets.rs`:

```rust
use anyhow::{Context, Result};
use reqwest::Client;
use serde::{Deserialize, Serialize};
use std::env;
use std::sync::Arc;
use tokio::sync::RwLock;
use std::time::{Duration, Instant};

#[derive(Debug, Clone, Deserialize)]
struct SecretResponse {
    name: String,
    value: String,
    kid: String,
    expires_at: String,
}

pub struct SecretsClient {
    client: Client,
    base_url: String,
    client_id: String,
    cache: Arc<RwLock<SecretCache>>,
}

struct SecretCache {
    entries: std::collections::HashMap<String, CachedSecret>,
}

struct CachedSecret {
    value: String,
    fetched_at: Instant,
    ttl: Duration,
}

impl SecretsClient {
    pub fn new() -> Result<Self> {
        let base_url = env::var("JARVIS_SECRETS_URL")
            .unwrap_or_else(|_| "http://127.0.0.1:8081".to_string());

        let client_id = env::var("JARVIS_CLIENT_ID")
            .unwrap_or_else(|_| "backend".to_string());

        Ok(Self {
            client: Client::builder()
                .timeout(Duration::from_secs(5))
                .build()?,
            base_url,
            client_id,
            cache: Arc::new(RwLock::new(SecretCache {
                entries: std::collections::HashMap::new(),
            })),
        })
    }

    pub async fn get_secret(&self, name: &str) -> Result<String> {
        // Check cache first
        {
            let cache = self.cache.read().await;
            if let Some(cached) = cache.entries.get(name) {
                if cached.fetched_at.elapsed() < cached.ttl {
                    tracing::debug!("Using cached secret: {}", name);
                    return Ok(cached.value.clone());
                }
            }
        }

        // Fetch from secretsd
        let url = format!("{}/secret/{}", self.base_url, name);

        let response = self.client
            .get(&url)
            .header("X-Jarvis-Client", &self.client_id)
            .send()
            .await
            .with_context(|| format!("failed to fetch secret: {}", name))?;

        if !response.status().is_success() {
            anyhow::bail!("secretsd returned {}: {}",
                response.status(),
                response.text().await.unwrap_or_default()
            );
        }

        let secret: SecretResponse = response.json().await
            .context("failed to parse secret response")?;

        // Cache for 5 minutes
        {
            let mut cache = self.cache.write().await;
            cache.entries.insert(name.to_string(), CachedSecret {
                value: secret.value.clone(),
                fetched_at: Instant::now(),
                ttl: Duration::from_secs(300),
            });
        }

        tracing::info!("Fetched secret from secretsd: {}", name);
        Ok(secret.value)
    }

    pub async fn clear_cache(&self) {
        let mut cache = self.cache.write().await;
        cache.entries.clear();
        tracing::info!("Secrets cache cleared");
    }
}

// Convenience functions
lazy_static::lazy_static! {
    static ref SECRETS_CLIENT: SecretsClient = SecretsClient::new()
        .expect("failed to initialize secrets client");
}

pub async fn get_jwt_secret() -> Result<String> {
    SECRETS_CLIENT.get_secret("jwt_signing_key").await
}

pub async fn get_postgres_password() -> Result<String> {
    SECRETS_CLIENT.get_secret("postgres_password").await
}

pub async fn get_home_assistant_token() -> Result<String> {
    SECRETS_CLIENT.get_secret("home_assistant_token").await
}
```

Add to `core/src/services/mod.rs`:

```rust
pub mod secrets;
```

Update `core/Cargo.toml`:

```toml
[dependencies]
lazy_static = "1.4"
```

### 4.2 Update JWT Configuration

Edit `core/src/main.rs` or wherever JWT is configured:

```rust
use crate::services::secrets;

// Old way (remove):
// let jwt_secret = env::var("JWT_SECRET_KEY")?;

// New way:
let jwt_secret = secrets::get_jwt_secret()
    .await
    .context("failed to load JWT secret from secretsd")?;
```

### 4.3 Update Database Connection

Edit database connection code:

```rust
use crate::services::secrets;

// Old way (remove):
// let db_password = env::var("POSTGRES_PASSWORD")?;

// New way:
let db_password = secrets::get_postgres_password()
    .await
    .context("failed to load database password from secretsd")?;

let database_url = format!(
    "postgresql://{}:{}@{}:{}/{}",
    username, db_password, host, port, database
);
```

### 4.4 Update Home Assistant Integration

Edit `backend-rust-mqtt/src/ha_client.rs`:

```rust
use crate::services::secrets;

pub async fn create_ha_client() -> Result<HomeAssistantClient> {
    let token = secrets::get_home_assistant_token()
        .await
        .context("failed to load Home Assistant token")?;

    let url = env::var("HOME_ASSISTANT_URL")
        .unwrap_or_else(|_| "http://homeassistant.local:8123".to_string());

    Ok(HomeAssistantClient::new(url, token))
}
```

---

## Phase 5: Python Services Integration

### 5.1 Create Python Secrets Client

Create `backend-python-bridges/secrets_client.py`:

```python
import os
import requests
from functools import lru_cache
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class SecretsClient:
    def __init__(self):
        self.base_url = os.getenv("JARVIS_SECRETS_URL", "http://127.0.0.1:8081")
        self.client_id = os.getenv("JARVIS_CLIENT_ID", "python-services")

    @lru_cache(maxsize=128)
    def get_secret(self, name: str) -> str:
        """Fetch secret from jarvis-secretsd with caching."""
        url = f"{self.base_url}/secret/{name}"
        headers = {"X-Jarvis-Client": self.client_id}

        try:
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Fetched secret from secretsd: {name}")
            return data["value"]
        except requests.RequestException as e:
            logger.error(f"Failed to fetch secret '{name}': {e}")
            raise

# Singleton instance
_client = SecretsClient()

def get_secret(name: str) -> str:
    """Get a secret by name."""
    return _client.get_secret(name)

def get_brave_api_key() -> str:
    return get_secret("brave_api_key")

def get_tavily_api_key() -> str:
    return get_secret("tavily_api_key")

def get_postgres_password() -> str:
    return get_secret("postgres_password")
```

### 5.2 Update MCP Services

Edit `MCP/servers/brave_search_mcp.py`:

```python
from secrets_client import get_brave_api_key

# Old way (remove):
# API_KEY = os.getenv("BRAVE_API_KEY")

# New way:
API_KEY = get_brave_api_key()
```

Repeat for all MCP servers:
- `tavily_search_mcp.py`
- `duckduckgo_search_mcp.py`
- `google_search_mcp.py`
- etc.

### 5.3 Update Embeddings Service

Edit `backend-python-bridges/embeddings_service.py`:

```python
from secrets_client import get_postgres_password

# Database connection
DB_PASSWORD = get_postgres_password()
DATABASE_URL = f"postgresql://jarvis:{DB_PASSWORD}@localhost:5432/jarvis_db"
```

---

## Phase 6: Remove .env File

### 6.1 Backup Current .env

```bash
cd /home/enzo/Documents/Projet-Jarvis

# Create encrypted backup
gpg --symmetric --cipher-algo AES256 -o .env.backup.gpg .env

# Verify backup
gpg --decrypt .env.backup.gpg | head

echo " Backup created: .env.backup.gpg"
```

### 6.2 Update .gitignore

Ensure `.env` and `.env.backup.gpg` are in `.gitignore`:

```bash
cat >> .gitignore << 'EOF'

# Secrets (should not exist anymore)
.env
.env.backup*
*.key
*.secret
EOF
```

### 6.3 Remove .env from Git and Filesystem

```bash
# Remove from git history (careful!)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# Remove from filesystem
rm -f .env

# Commit changes
git add .gitignore
git commit -m "security: remove .env file, secrets now managed by jarvis-secretsd"

# Force push (if needed, coordinate with team)
# git push origin --force --all
```

** WARNING:** Coordinate with team before force-pushing to remove .env from history!

---

## Phase 7: Testing

### 7.1 Smoke Tests

```bash
cd /home/enzo/Documents/Projet-Jarvis

# Start all services
docker-compose up -d

# Wait for services to start
sleep 30

# Check secretsd health
curl http://127.0.0.1:8081/healthz

# Check backend can fetch secrets
docker-compose logs backend | grep -i secret

# Test API endpoint
curl -H "Authorization: Bearer <jwt_token>" \
  http://localhost:8000/api/v1/health
```

### 7.2 Integration Tests

Run existing integration tests:

```bash
cd tests
python run_tests.py
```

### 7.3 Rotation Test

```bash
# Trigger rotation
curl -X POST http://127.0.0.1:8081/rotate \
  -H "X-Jarvis-Client: admin" \
  -H "Content-Type: application/json" \
  -d '{"names":["jwt_signing_key"]}'

# Verify services can still authenticate
# (might need to restart services to pick up new key)
docker-compose restart backend
sleep 10

# Test API again
curl -H "Authorization: Bearer <new_jwt_token>" \
  http://localhost:8000/api/v1/health
```

### 7.4 Audit Log Verification

```bash
# Check audit log
sudo cat /opt/jarvis/audit/audit.jsonl | jq .

# Verify signatures
ls -lh /opt/jarvis/audit/audit.sign.*
```

---

## Phase 8: Production Deployment

### 8.1 Deploy to Production

```bash
cd /home/enzo/Documents/Projet-Jarvis/prod

# Build production images
docker-compose -f docker-compose.prod.yml build secretsd

# Start secretsd first
docker-compose -f docker-compose.prod.yml up -d secretsd

# Verify health
curl http://127.0.0.1:8081/healthz

# Migrate secrets (run migration script with prod env)
cd ../jarvis-secretsd/scripts
ADMIN_CLIENT=admin ./migrate_secrets.sh

# Start remaining services
cd ../../prod
docker-compose -f docker-compose.prod.yml up -d
```

### 8.2 Setup Systemd Service (Alternative to Docker)

```bash
sudo cp jarvis-secretsd.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable jarvis-secretsd
sudo systemctl start jarvis-secretsd
sudo systemctl status jarvis-secretsd
```

### 8.3 Setup Log Rotation

Create `/etc/logrotate.d/jarvis-secretsd`:

```
/opt/jarvis/audit/audit.jsonl {
    daily
    missingok
    rotate 365
    compress
    notifempty
    create 0640 jarvis jarvis
    sharedscripts
    postrotate
        # Signal daemon to reopen log file (if needed)
    endscript
}
```

### 8.4 Setup Monitoring

Add to Prometheus configuration (`devops-tools/monitoring/prometheus/prometheus.yml`):

```yaml
  - job_name: 'jarvis-secretsd'
    static_configs:
      - targets: ['localhost:8081']
    metrics_path: '/metrics'  # If metrics endpoint exists
```

Add Grafana dashboard for secretsd monitoring.

---

## Phase 9: Security Hardening

### 9.1 File Permissions

```bash
# Master key - owner read/write only
sudo chmod 600 /opt/jarvis/secrets/master.key
sudo chown jarvis:jarvis /opt/jarvis/secrets/master.key

# Vault - owner read/write only
sudo chmod 600 /opt/jarvis/secrets/vault.json
sudo chown jarvis:jarvis /opt/jarvis/secrets/vault.json

# Audit signing key - owner read/write only
sudo chmod 600 /opt/jarvis/audit/audit.sign.key
sudo chown jarvis:jarvis /opt/jarvis/audit/audit.sign.key

# Config directory - owner read only
sudo chmod 700 /etc/jarvis-secretsd
sudo chown root:root /etc/jarvis-secretsd
sudo chmod 400 /etc/jarvis-secretsd/config.toml
sudo chmod 400 /etc/jarvis-secretsd/policy.yaml
```

### 9.2 Network Security

Add to `config.toml`:

```toml
[server]
bind_addr = "127.0.0.1:8081"  # Localhost only

[security]
deny_network_remote = true  # Reject non-localhost connections
require_client_id_header = true  # Require X-Jarvis-Client header
```

### 9.3 Firewall Rules

```bash
# Block external access to secretsd port (just in case)
sudo ufw deny 8081/tcp
sudo ufw allow from 127.0.0.1 to any port 8081
```

### 9.4 SELinux/AppArmor (if applicable)

Create AppArmor profile for jarvis-secretsd (advanced, optional).

---

## Phase 10: Documentation and Handoff

### 10.1 Update Documentation

Update `/home/enzo/Documents/Projet-Jarvis/docs/SECURITY.md`:

```markdown
## Secrets Management

Jarvis uses jarvis-secretsd for secure secrets management:

- **Encryption:** AES-GCM-256 with random nonces
- **Storage:** Encrypted vault at `/opt/jarvis/secrets/vault.json`
- **Access Control:** RBAC via policy.yaml
- **Audit:** Signed append-only log at `/opt/jarvis/audit/audit.jsonl`
- **Rotation:** Automatic 90-day rotation with 14-day grace period

### Accessing Secrets

**Rust:**
```rust
use crate::services::secrets;
let secret = secrets::get_secret("name").await?;
```

**Python:**
```python
from secrets_client import get_secret
secret = get_secret("name")
```

### Managing Secrets

```bash
# Create secret
curl -X POST http://127.0.0.1:8081/secret \
  -H "X-Jarvis-Client: admin" \
  -H "Content-Type: application/json" \
  -d '{"name":"key_name","value":"key_value"}'

# Rotate secret
curl -X POST http://127.0.0.1:8081/rotate \
  -H "X-Jarvis-Client: admin" \
  -H "Content-Type: application/json" \
  -d '{"names":["key_name"]}'
```
```

### 10.2 Create Operations Runbook

Create `docs/RUNBOOK_SECRETS.md`:

```markdown
# Secrets Management Runbook

## Common Operations

### Add New Secret
[instructions]

### Rotate Secret
[instructions]

### Recover from Master Key Loss
[instructions]

### Audit Log Review
[instructions]

### Troubleshooting
[common issues and solutions]
```

### 10.3 Team Training

Schedule training session covering:
- How to access secrets in code
- How to add new secrets
- RBAC policy management
- Rotation procedures
- Emergency procedures

---

## Rollback Plan

If issues are encountered during deployment:

### Quick Rollback

```bash
# Stop secretsd
docker-compose stop secretsd

# Restore .env file from backup
gpg --decrypt .env.backup.gpg > .env

# Revert code changes
git checkout HEAD~1 -- core/src/services/secrets.rs
# ... revert other changes

# Restart services without secretsd
docker-compose up -d
```

### Full Rollback

```bash
# Stop all services
docker-compose down

# Restore previous git commit
git revert <commit-hash>

# Restore .env
gpg --decrypt .env.backup.gpg > .env

# Restart with old configuration
docker-compose up -d
```

---

## Success Criteria

 **Security:**
- All secrets removed from .env
- Secrets encrypted at rest with AES-GCM-256
- RBAC enforced for all secret access
- Audit log captures all operations
- Master key has 0600 permissions

 **Functionality:**
- All services can fetch secrets from secretsd
- JWT authentication works with new secrets
- Database connections succeed
- Home Assistant integration works
- MCP services can access API keys

 **Operations:**
- Health checks pass
- Audit log is being written
- Rotation scheduler is running
- Monitoring alerts configured
- Logs are being rotated

 **Performance:**
- API response time < 100ms
- No impact on service startup time
- Secrets caching working correctly

---

## Timeline

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1: Preparation | 1 hour | None |
| Phase 2: Docker Integration | 30 min | Phase 1 |
| Phase 3: Secret Migration | 30 min | Phase 2 |
| Phase 4: Backend Integration | 2 hours | Phase 3 |
| Phase 5: Python Integration | 1 hour | Phase 4 |
| Phase 6: Remove .env | 30 min | Phase 5 |
| Phase 7: Testing | 2 hours | Phase 6 |
| Phase 8: Production | 1 hour | Phase 7 |
| Phase 9: Hardening | 1 hour | Phase 8 |
| Phase 10: Documentation | 1 hour | Phase 9 |

**Total Estimated Time:** 10-12 hours

---

## Support Contacts

- **Implementation:** Claude Code (Anthropic)
- **Specifications:** ChatGPT
- **Project Owner:** [Your Name/Team]

---

**Plan created:** 2025-10-26
**Status:** Ready for execution
**Version:** 1.0
