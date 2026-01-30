# Stage 1: Build
FROM rust:1.90-bookworm AS builder

# Dépendances système pour compiler l'audio et Whisper (C++)
RUN apt-get update && apt-get install -y \
    pkg-config \
    libasound2-dev \
    clang \
    llvm-dev \
    libclang-dev \
    build-essential \
    cmake \
    && rustup component add rustfmt \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Copier tous les répertoires nécessaires pour la compilation (contexte racine)
COPY core /build/core
COPY backend-rust-audio /build/backend-rust-audio

WORKDIR /build/core

# Build the app
RUN cargo build --release

# Stage 2: Runtime
FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    jq \
    libasound2 \
    libstdc++6 \
    espeak-ng \
    ffmpeg \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install Piper TTS binary (Download and extract)
RUN curl -L https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz | tar -xzC /usr/local/bin --strip-components=1

WORKDIR /app

# Copy binary from builder
COPY --from=builder /build/core/target/release/jarvis-core /app/jarvis-core

# Copy secrets fetching script (ajusté pour le nouveau contexte)
COPY core/fetch-secrets.sh /app/fetch-secrets.sh
RUN chmod +x /app/fetch-secrets.sh

# Expose port
EXPOSE 8100

# Health check (ajusté pour HTTPS)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -fk https://localhost:8100/health || exit 1

# Use fetch-secrets.sh as entrypoint to load secrets before running the app
ENTRYPOINT ["/app/fetch-secrets.sh"]
CMD ["./jarvis-core"]
