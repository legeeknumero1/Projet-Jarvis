# Stage 1: Build
FROM rust:1.90-bookworm AS builder

# Dépendances système pour compiler l'audio (ALSA)
RUN apt-get update && apt-get install -y --no-install-recommends \
    pkg-config \
    libasound2-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Copier tous les répertoires nécessaires pour la compilation (contexte racine)
COPY core /build/core
COPY backend-rust-audio /build/backend-rust-audio

WORKDIR /build/core

# Build the app
ENV CARGO_BUILD_JOBS=1
RUN cargo build --release

# Stage 2: Runtime
FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    jq \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Create a non-privileged user and group
RUN groupadd -r jarvis && useradd -r -g jarvis -d /app -s /sbin/nologin jarvis

WORKDIR /app

# Copy binary from builder
COPY --from=builder /build/core/target/release/jarvis-core /app/jarvis-core

# Copy secrets fetching script (ajusté pour le nouveau contexte)
COPY core/fetch-secrets.sh /app/fetch-secrets.sh
RUN chmod +x /app/fetch-secrets.sh && chown -R jarvis:jarvis /app

# Copy certs
COPY certs /etc/jarvis/certs
RUN chown -R jarvis:jarvis /etc/jarvis/certs

USER jarvis

# Expose port
EXPOSE 8100

# Health check (ajusté pour HTTPS)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8100/health || curl -fk https://localhost:8100/health || exit 1

# Use fetch-secrets.sh as entrypoint to load secrets before running the app
ENTRYPOINT ["/app/fetch-secrets.sh"]
CMD ["./jarvis-core"]
