# jarvis-secretsd

A lightweight, offline Rust daemon that auto-generates, encrypts, rotates, and serves Jarvis secrets via a local API with signed audits.

## Features

- ✅ **Auto-bootstrap**: Creates master key and vault on first run
- ✅ **Strong crypto**: AES-GCM-256, Ed25519, CSPRNG (OsRng)
- ✅ **Zero-downtime rotation**: Old secrets kept during grace period
- ✅ **RBAC-lite**: Per-service access control via policy.yaml
- ✅ **Signed audit log**: Append-only JSONL with Ed25519 signatures
- ✅ **Local-only**: No network exposure beyond localhost
- ✅ **Observability**: Structured logs, metrics, health endpoint

## Quick Start

### 1. Build

```bash
cargo build --release
```

### 2. Configuration

```bash
# Copy config examples
sudo mkdir -p /etc/jarvis-secretsd
sudo cp config.toml.example /etc/jarvis-secretsd/config.toml
sudo cp policy.yaml.example /etc/jarvis-secretsd/policy.yaml

# Edit as needed
sudo nano /etc/jarvis-secretsd/config.toml
```

### 3. Run

```bash
# Create directories
sudo mkdir -p /opt/jarvis/secrets /opt/jarvis/audit

# Run daemon
sudo ./target/release/jarvis-secretsd --config /etc/jarvis-secretsd/config.toml
```

## API Usage

### Health Check

```bash
curl http://127.0.0.1:8081/healthz
```

### Get Secret

```bash
curl -H "X-Jarvis-Client: backend" \
  http://127.0.0.1:8081/secret/jwt_signing_key
```

### Create Secret (Admin only)

```bash
curl -X POST \
  -H "X-Jarvis-Client: admin" \
  -H "Content-Type: application/json" \
  -d '{"name":"my_secret","value":"my_value"}' \
  http://127.0.0.1:8081/secret
```

### List Secrets

```bash
curl -H "X-Jarvis-Client: backend" \
  http://127.0.0.1:8081/secrets
```

### Rotate Secrets

```bash
# Rotate specific secrets
curl -X POST \
  -H "X-Jarvis-Client: admin" \
  -H "Content-Type: application/json" \
  -d '{"names":["jwt_signing_key","postgres_password"]}' \
  http://127.0.0.1:8081/rotate

# Rotate all due secrets
curl -X POST \
  -H "X-Jarvis-Client: admin" \
  -H "Content-Type: application/json" \
  -d '{"names":[]}' \
  http://127.0.0.1:8081/rotate
```

## Integration with Jarvis Services

### Rust Backend

```rust
use reqwest::Client;

let client = Client::new();
let res = client
    .get("http://127.0.0.1:8081/secret/jwt_signing_key")
    .header("X-Jarvis-Client", "backend")
    .send()
    .await?
    .json::<serde_json::Value>()
    .await?;

let key = res["value"].as_str().unwrap();
```

### Python Service

```python
import requests

response = requests.get(
    "http://127.0.0.1:8081/secret/postgres_password",
    headers={"X-Jarvis-Client": "db"}
)
secret = response.json()["value"]
```

## Deployment

### Docker

```bash
docker build -t jarvis-secretsd .
docker run -d \
  -v /etc/jarvis-secretsd:/etc/jarvis-secretsd:ro \
  -v /opt/jarvis:/opt/jarvis \
  --network host \
  jarvis-secretsd
```

### Systemd

```bash
sudo cp jarvis-secretsd.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable jarvis-secretsd
sudo systemctl start jarvis-secretsd
```

## Security

- Master key stored at `/opt/jarvis/master.key` (permissions 0600)
- Vault encrypted with AES-GCM-256
- Audit log signed with Ed25519
- Local-only by default (localhost or Unix socket)
- RBAC enforced via policy.yaml

## Configuration

See `config.toml.example` and `policy.yaml.example` for full configuration options.

## License

MIT
