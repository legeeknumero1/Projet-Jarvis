# Stage 1: Build
FROM rust:1.90 AS builder

WORKDIR /app

# Copy manifests
COPY Cargo.toml Cargo.toml

# Copy source
COPY src src

# Copy migrations for sqlx macro
COPY migrations migrations

# Build the app
RUN cargo build --release

# Stage 2: Runtime
FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    jq \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy binary from builder
COPY --from=builder /app/target/release/jarvis-core /app/jarvis-core

# Copy secrets fetching script
COPY fetch-secrets.sh /app/fetch-secrets.sh
RUN chmod +x /app/fetch-secrets.sh

# Expose port
EXPOSE 8100

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8100/health || exit 1

# Use fetch-secrets.sh as entrypoint to load secrets before running the app
ENTRYPOINT ["/app/fetch-secrets.sh"]
CMD ["./jarvis-core"]
