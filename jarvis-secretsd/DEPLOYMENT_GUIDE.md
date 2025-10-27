# Jarvis-Secretsd Deployment Guide

Complete guide for deploying jarvis-secretsd in production.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Docker Deployment](#docker-deployment)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [Migration from .env](#migration-from-env)
5. [CLI Tool Usage](#cli-tool-usage)
6. [Backup and Restore](#backup-and-restore)
7. [Monitoring](#monitoring)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- Docker 20+ or Kubernetes 1.24+
- curl
- bash 4+
- (Optional) GPG for encrypted backups
- (Optional) Rust 1.70+ for building from source

---

## Docker Deployment

### Quick Start

The easiest way to deploy is using the existing `docker-compose.yml`:

```bash
# jarvis-secretsd is already included in docker-compose.yml
cd /home/enzo/Documents/Projet-Jarvis
docker-compose up -d jarvis-secretsd
```

### Manual Docker Run

```bash
# Create volumes
docker volume create secretsd_vault
docker volume create secretsd_audit

# Run container
docker run -d \
  --name jarvis-secretsd \
  --network jarvis_network \
  -p 127.0.0.1:8081:8081 \
  -v secretsd_vault:/opt/jarvis/secrets \
  -v secretsd_audit:/opt/jarvis/audit \
  -v ./jarvis-secretsd/config.toml:/etc/jarvis-secretsd/config.toml:ro \
  -v ./jarvis-secretsd/policy.yaml:/etc/jarvis-secretsd/policy.yaml:ro \
  --security-opt no-new-privileges:true \
  jarvis-secretsd:latest
```

### Verification

```bash
# Check health
curl http://127.0.0.1:8081/healthz

# Expected output:
# {"status":"ok","version":"0.1.0","uptime_secs":10,"secrets_count":0}
```

---

## Kubernetes Deployment

### Deploy to Kubernetes

```bash
# Apply manifests
kubectl apply -f jarvis-secretsd/k8s/deployment.yaml

# Check status
kubectl -n jarvis-secrets get pods
kubectl -n jarvis-secrets get svc

# View logs
kubectl -n jarvis-secrets logs -f deployment/jarvis-secretsd
```

### Access from other namespaces

```bash
# From other pods in the cluster
SECRETSD_URL="http://jarvis-secretsd.jarvis-secrets.svc.cluster.local:8081"

# Get a secret
curl -H "X-Jarvis-Client: backend" \
  $SECRETSD_URL/secret/jwt_signing_key
```

### Scaling Considerations

**Important**: jarvis-secretsd is currently designed for single-instance deployment due to:
- File-based vault storage
- Local master key
- No distributed locking

For high availability, use:
- ReadWriteOnce PVC with node affinity
- Automated backups
- Fast failover with StatefulSet

---

## Migration from .env

### Automatic Migration

Use the provided migration script:

```bash
# Migrate from .env file
cd jarvis-secretsd
chmod +x scripts/migrate-env-secrets.sh
./scripts/migrate-env-secrets.sh /path/to/.env
```

The script will:
1. Read all KEY=value pairs from .env
2. Convert keys to lowercase
3. Create secrets via API
4. Report success/failure for each

### Manual Migration

```bash
# Create secrets one by one
curl -X POST -H "X-Jarvis-Client: admin" \
  -H "Content-Type: application/json" \
  -d '{"name":"postgres_password","value":"your-secret-value"}' \
  http://127.0.0.1:8081/secret
```

### Update Services

After migration, update your services to fetch secrets:

**Example: Docker Compose**
```yaml
services:
  backend:
    environment:
      # Old:
      # POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}

      # New: Set at runtime using init script
      POSTGRES_PASSWORD: ""
    entrypoint: /app/fetch-secrets.sh
```

**fetch-secrets.sh**:
```bash
#!/bin/bash
export POSTGRES_PASSWORD=$(curl -s -H "X-Jarvis-Client: backend" \
  http://jarvis-secretsd:8081/secret/postgres_password | jq -r '.value')

exec "$@"
```

---

## CLI Tool Usage

### Build the CLI

```bash
cd jarvis-secretsd/jarvis-secrets-cli
cargo build --release
sudo cp target/release/jarvis-secrets /usr/local/bin/
```

### Commands

```bash
# List all secrets
jarvis-secrets list

# Get a specific secret
jarvis-secrets get jwt_signing_key

# Create/update a secret
jarvis-secrets set my_secret --value "secret-value"

# Create from stdin (useful for pipes)
echo "secret-value" | jarvis-secrets set my_secret

# Rotate secrets
jarvis-secrets rotate jwt_signing_key postgres_password

# Check health
jarvis-secrets health

# View Prometheus metrics
jarvis-secrets metrics
```

### Advanced Usage

```bash
# Use custom URL
jarvis-secrets --url http://prod-secrets:8081 list

# Use different client ID
jarvis-secrets --client backend get jwt_signing_key

# Pipe secret to file
jarvis-secrets get db_password | jq -r '.value' > /tmp/db_pass
```

---

## Backup and Restore

### Automated Backups

```bash
# Run backup script
chmod +x scripts/backup-vault.sh
./scripts/backup-vault.sh

# Schedule with cron (daily at 2 AM)
0 2 * * * /opt/jarvis-secretsd/scripts/backup-vault.sh
```

Backups are:
- Encrypted with AES256 (GPG)
- Include vault + audit log + metadata
- Stored in `/opt/jarvis/backups/`

### Restore from Backup

```bash
# Decrypt and extract
gpg -d /opt/jarvis/backups/vault-backup-20251027-120000.tar.gz.gpg | \
  tar xzf - -C /tmp/restore

# Stop secretsd
docker-compose stop jarvis-secretsd

# Restore files
cp /tmp/restore/vault.json /opt/jarvis/secrets/
cp /tmp/restore/audit.jsonl /opt/jarvis/audit/

# Restart
docker-compose start jarvis-secretsd
```

### Disaster Recovery

1. **Restore from backup** (as above)
2. **Verify master key** is accessible
3. **Test decryption** with a known secret
4. **Rotate all secrets** after restore

```bash
# Rotate all secrets
jarvis-secrets list | tail -n +2 | awk '{print $1}' | \
  xargs jarvis-secrets rotate
```

---

## Monitoring

### Prometheus Integration

**Add to Prometheus config**:
```yaml
scrape_configs:
  - job_name: 'jarvis-secretsd'
    static_configs:
      - targets: ['jarvis-secretsd:8081']
    metrics_path: /metrics
```

**Key Metrics**:
- `http_requests_total` - Total HTTP requests
- `http_requests_success` - Successful requests
- `http_request_duration_seconds` - Request latency
- `secrets_total` - Current number of secrets
- `secrets_created_total` - Total secrets created
- `secrets_retrieved_total` - Total retrievals
- `secrets_rotated_total` - Total rotations
- `rbac_allowed_total` - RBAC allow decisions
- `rbac_denied_total` - RBAC deny decisions
- `encryption_ops_total` - Total encryptions
- `decryption_ops_total` - Total decryptions
- `audit_events_total` - Total audit events

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "Jarvis Secrets Management",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Secrets Count",
        "targets": [
          {
            "expr": "secrets_total"
          }
        ]
      },
      {
        "title": "RBAC Denials",
        "targets": [
          {
            "expr": "rate(rbac_denied_total[5m])"
          }
        ]
      }
    ]
  }
}
```

### Alerts

**Critical Alerts**:
```yaml
groups:
  - name: secretsd
    rules:
      - alert: SecretsServiceDown
        expr: up{job="jarvis-secretsd"} == 0
        for: 1m
        annotations:
          summary: "Secrets service is down"

      - alert: HighRBACDenials
        expr: rate(rbac_denied_total[5m]) > 10
        for: 5m
        annotations:
          summary: "High rate of RBAC denials"

      - alert: DecryptionErrors
        expr: rate(decryption_errors_total[5m]) > 0
        for: 1m
        annotations:
          summary: "Decryption errors detected"
```

---

## Troubleshooting

### Common Issues

#### 1. Connection Refused

**Symptom**: `curl: (7) Failed to connect to 127.0.0.1 port 8081`

**Solutions**:
```bash
# Check if service is running
docker ps | grep secretsd

# Check logs
docker logs jarvis_secretsd

# Verify port binding
netstat -tulpn | grep 8081
```

#### 2. Permission Denied

**Symptom**: `failed to write master key: /opt/jarvis/secrets/master.key`

**Solutions**:
```bash
# Fix permissions
sudo chown -R 1000:1000 /opt/jarvis/secrets
sudo chmod 700 /opt/jarvis/secrets
```

#### 3. Decryption Failed

**Symptom**: `{"error":"internal","message":"crypto error: decryption failed"}`

**Causes**:
- Master key changed
- Vault corrupted
- Wrong master key

**Solutions**:
```bash
# Restore from backup
./scripts/restore-backup.sh

# If no backup, secrets are irrecoverable
# Rotate all secrets manually
```

#### 4. RBAC Denial

**Symptom**: `{"error":"not_authorized","message":"client X not allowed to access Y"}`

**Solutions**:
```bash
# Check policy
cat /etc/jarvis-secretsd/policy.yaml

# Verify client ID header
curl -H "X-Jarvis-Client: admin" ...

# Update policy if needed
# Restart secretsd after policy changes
```

### Debug Mode

```bash
# Enable trace logging
export RUST_LOG=trace
docker-compose restart jarvis-secretsd

# View detailed logs
docker logs -f jarvis_secretsd
```

### Health Checks

```bash
# Basic health
curl http://127.0.0.1:8081/healthz

# List secrets (admin only)
curl -H "X-Jarvis-Client: admin" \
  http://127.0.0.1:8081/secrets

# Check metrics
curl http://127.0.0.1:8081/metrics
```

---

## Security Best Practices

1. **Network Isolation**
   - Bind to localhost only in production
   - Use network policies in Kubernetes
   - Never expose to public internet

2. **Access Control**
   - Use strong RBAC policies
   - Audit `rbac_denied_total` regularly
   - Rotate credentials quarterly

3. **Backup Strategy**
   - Daily automated backups
   - Encrypt backups with GPG
   - Store backups off-site
   - Test restore procedures monthly

4. **Monitoring**
   - Alert on service downtime
   - Monitor decryption errors
   - Track RBAC denials
   - Review audit logs weekly

5. **Master Key Protection**
   - Store master key on encrypted volume
   - Set file permissions to 600
   - Consider HSM for production
   - Never commit to git

6. **Rotation Policy**
   - Rotate secrets every 90 days
   - Use 14-day grace period
   - Test rotation in staging first
   - Document rotation procedures

---

## Performance Tuning

### Recommended Settings

**Production Environment**:
```toml
[server]
bind_addr = "0.0.0.0:8081"

[security]
rotation_days = 90
grace_days = 14

[logging]
level = "info"
json = true
```

**Expected Performance**:
- Latency: <10ms (p99)
- Throughput: >1000 req/s
- Memory: ~50MB
- CPU: <5% (idle), <20% (load)

### Optimization Tips

1. **Use connection pooling** in clients
2. **Cache secret values** (with TTL)
3. **Batch rotations** during maintenance windows
4. **Monitor vault size** (audit log growth)
5. **Use SSD storage** for vault

---

## Changelog

### v0.2.0 (2025-10-27)
- ✅ Added Prometheus metrics endpoint
- ✅ Created jarvis-secrets CLI tool
- ✅ Added migration scripts
- ✅ Kubernetes manifests
- ✅ Backup/restore scripts
- ✅ Comprehensive documentation

### v0.1.0 (2025-10-26)
- ✅ Initial implementation
- ✅ AES-GCM-256 encryption
- ✅ Ed25519 audit trail
- ✅ RBAC policy enforcement
- ✅ Secret rotation with grace period
- ✅ Docker integration

---

## Support

- **Documentation**: See INTEGRATION_REPORT.md
- **Issues**: https://github.com/legeeknumero1/Projet-Jarvis/issues
- **Security**: Report to security@jarvis.local

---

**Deployment Status**: ✅ Production Ready

Last updated: 2025-10-27
Version: 0.2.0
