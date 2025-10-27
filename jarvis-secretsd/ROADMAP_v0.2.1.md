# jarvis-secretsd v0.2.1 - Metrics Module Roadmap

**Branch:** feature/metrics-module
**Target Release:** v0.2.1
**Priority:** HIGH
**ETA:** 48 hours (2025-10-29)

---

## Objective

Integrate Prometheus metrics exporter into jarvis-secretsd to enable comprehensive monitoring and observability.

---

## Tasks Checklist

### 1. Code Integration ✅ (Already in codebase)

- [x] Add `prometheus-client = "0.22"` to Cargo.toml
- [x] Create `src/metrics.rs` module
- [x] Implement 15 metrics:
  - [x] HTTP request counters (total, success, error)
  - [x] HTTP request duration histogram
  - [x] Secrets gauge and operation counters
  - [x] RBAC decision counters
  - [x] Crypto operation counters
  - [x] Audit event counters
- [x] Update `src/main.rs` to initialize metrics
- [x] Update `src/api.rs` to add `/metrics` endpoint

**Status:** Code already written, needs rebuild

---

### 2. Build and Test ⏳

- [ ] Rebuild binary with metrics module
  ```bash
  cd jarvis-secretsd/jarvis-secretsd
  cargo build --release
  ```

- [ ] Verify binary size and metrics inclusion
  ```bash
  ls -lh target/release/jarvis-secretsd
  strings target/release/jarvis-secretsd | grep "prometheus"
  ```

- [ ] Test metrics endpoint locally
  ```bash
  ./target/release/jarvis-secretsd --config config.toml &
  curl http://127.0.0.1:8081/metrics
  ```

- [ ] Validate Prometheus format
  ```bash
  curl http://127.0.0.1:8081/metrics | promtool check metrics
  ```

---

### 3. Docker Integration ⏳

- [ ] Update Dockerfile.runtime to use new binary
  ```dockerfile
  # Copy new binary with metrics
  COPY target/release/jarvis-secretsd /usr/local/bin/jarvis-secretsd
  ```

- [ ] Rebuild Docker image
  ```bash
  docker-compose build jarvis-secretsd
  ```

- [ ] Restart container
  ```bash
  docker-compose down jarvis-secretsd
  docker-compose up -d jarvis-secretsd
  ```

- [ ] Test metrics endpoint through Docker
  ```bash
  curl http://127.0.0.1:8081/metrics
  ```

---

### 4. Validation ⏳

- [ ] Verify all 15 metrics are exposed
- [ ] Test metric updates during operations:
  - Create secret → `secrets_created_total` increments
  - Retrieve secret → `secrets_retrieved_total` increments
  - RBAC deny → `rbac_denied_total` increments
  - Rotation → `secrets_rotated_total` increments

- [ ] Load test to verify histogram buckets
  ```bash
  for i in {1..100}; do
    curl -s -H "X-Jarvis-Client: admin" \
      http://127.0.0.1:8081/secret/test_secret > /dev/null
  done
  ```

- [ ] Check Prometheus scraping compatibility
  ```bash
  curl http://127.0.0.1:8081/metrics | head -50
  ```

---

### 5. Documentation ⏳

- [ ] Update README.md with metrics section
- [ ] Document available metrics in DEPLOYMENT_GUIDE.md
- [ ] Update PRODUCTION_STATUS.md to reflect metrics availability
- [ ] Create example Prometheus scrape config
- [ ] Document Grafana dashboard import process

---

### 6. Grafana Dashboard ⏳

- [ ] Validate `docs/grafana-dashboard-secrets.json` compatibility
- [ ] Test dashboard with live metrics
- [ ] Create screenshots for documentation
- [ ] Document dashboard panels and queries

---

### 7. Git Workflow ⏳

- [ ] Commit metrics rebuild
  ```bash
  git add jarvis-secretsd/target/release/jarvis-secretsd
  git commit -m "feat: rebuild with Prometheus metrics module - v0.2.1"
  ```

- [ ] Update Docker configuration
  ```bash
  git add Dockerfile.runtime docker-compose.yml
  git commit -m "chore: update Docker config for metrics support"
  ```

- [ ] Update documentation
  ```bash
  git add README.md DEPLOYMENT_GUIDE.md PRODUCTION_STATUS.md
  git commit -m "docs: update for v0.2.1 metrics release"
  ```

- [ ] Merge to master
  ```bash
  git checkout master
  git merge feature/metrics-module
  ```

- [ ] Tag release
  ```bash
  git tag -a v0.2.1 -m "Release v0.2.1 - Prometheus metrics support"
  git push origin master --tags
  ```

---

## Metrics Specification

### Counter Metrics

| Metric Name | Type | Description |
|-------------|------|-------------|
| `http_requests_total` | Counter | Total HTTP requests received |
| `http_requests_success` | Counter | Successful HTTP responses (2xx) |
| `http_requests_error` | Counter | Error HTTP responses (4xx, 5xx) |
| `secrets_created_total` | Counter | Total secrets created |
| `secrets_retrieved_total` | Counter | Total secret retrievals |
| `secrets_rotated_total` | Counter | Total secret rotations |
| `rbac_allowed_total` | Counter | RBAC allow decisions |
| `rbac_denied_total` | Counter | RBAC deny decisions |
| `encryption_ops_total` | Counter | Total encryption operations |
| `decryption_ops_total` | Counter | Total decryption operations |
| `decryption_errors_total` | Counter | Failed decryption attempts |
| `audit_events_total` | Counter | Total audit events logged |
| `audit_errors_total` | Counter | Audit logging failures |

### Gauge Metrics

| Metric Name | Type | Description |
|-------------|------|-------------|
| `secrets_total` | Gauge | Current number of secrets in vault |

### Histogram Metrics

| Metric Name | Type | Description | Buckets |
|-------------|------|-------------|---------|
| `http_request_duration_seconds` | Histogram | Request latency distribution | 0.001, 0.005, 0.01, 0.025, 0.05, 0.1 |

---

## Testing Plan

### Unit Tests
```bash
cd jarvis-secretsd/jarvis-secretsd
cargo test metrics
```

### Integration Tests
```bash
# Start service
./target/release/jarvis-secretsd --config config.toml &
PID=$!

# Create secret and check metrics
curl -X POST -H "X-Jarvis-Client: admin" \
  -d '{"name":"test","value":"val"}' \
  http://127.0.0.1:8081/secret

curl http://127.0.0.1:8081/metrics | grep secrets_created_total

# Cleanup
kill $PID
```

### Load Tests
```bash
# 1000 requests in 10 seconds
ab -n 1000 -c 10 -H "X-Jarvis-Client: admin" \
  http://127.0.0.1:8081/healthz

# Check histogram data
curl http://127.0.0.1:8081/metrics | grep http_request_duration
```

---

## Acceptance Criteria

- [ ] `/metrics` endpoint returns HTTP 200
- [ ] All 15 metrics are present in output
- [ ] Metrics format is Prometheus-compatible
- [ ] Histogram has correct bucket structure
- [ ] Counters increment on operations
- [ ] Gauge reflects current state
- [ ] Docker health check still passes
- [ ] No performance regression (<1ms overhead)
- [ ] Documentation updated
- [ ] Grafana dashboard imports successfully

---

## Rollback Plan

If metrics cause issues:

1. Stop container
   ```bash
   docker-compose stop jarvis-secretsd
   ```

2. Revert to v0.2.0
   ```bash
   git checkout v0.2.0-prod
   docker-compose build jarvis-secretsd
   docker-compose up -d jarvis-secretsd
   ```

3. Binary is already v0.2.0 compatible (no breaking changes)

---

## Timeline

| Day | Tasks | Deliverables |
|-----|-------|--------------|
| **Day 1** (2025-10-28) | Build, test, Docker rebuild | Working metrics endpoint |
| **Day 2** (2025-10-29) | Validation, docs, release | v0.2.1 tagged and deployed |

---

## Success Metrics

- ✅ Metrics endpoint operational
- ✅ Prometheus scraping successful
- ✅ Grafana dashboard functional
- ✅ Zero downtime during upgrade
- ✅ Performance maintained (<15ms p99)

---

**Status:** 🚧 IN PROGRESS
**Current Phase:** Planning Complete, Ready for Build
**Next Action:** Rebuild binary with metrics module

---

Last Updated: 2025-10-27
Branch: feature/metrics-module
