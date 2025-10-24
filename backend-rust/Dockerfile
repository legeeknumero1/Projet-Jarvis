# Dockerfile pour Jarvis Rust Backend
# Build multi-stage pour optimiser la taille finale

# Stage 1: Builder
FROM rust:1.75-slim as builder

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    pkg-config \
    libssl-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Créer le répertoire de travail
WORKDIR /app

# Copier les fichiers de configuration Rust
COPY Cargo.toml Cargo.lock build.rs ./

# Créer un projet dummy pour compiler les dépendances
RUN mkdir src && echo "fn main() {}" > src/main.rs
RUN cargo build --release && rm -rf src

# Copier le code source
COPY src/ ./src/
COPY migrations/ ./migrations/

# Compiler l'application
RUN cargo build --release

# Stage 2: Runtime
FROM debian:bookworm-slim

# Installer les dépendances runtime
RUN apt-get update && apt-get install -y \
    ca-certificates \
    libssl3 \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Créer un utilisateur non-root
RUN groupadd -r jarvis && useradd -r -g jarvis jarvis

# Créer les répertoires nécessaires
WORKDIR /app
RUN mkdir -p /app/logs && chown -R jarvis:jarvis /app

# Copier le binaire depuis le stage builder
COPY --from=builder /app/target/release/jarvis-core /app/jarvis-core
COPY --from=builder /app/migrations /app/migrations

# Changer les permissions
RUN chmod +x /app/jarvis-core

# Passer à l'utilisateur non-root
USER jarvis

# Variables d'environnement par défaut
ENV RUST_LOG=jarvis_core=info
ENV RUST_BACKTRACE=1

# Exposer le port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Commande de démarrage
CMD ["./jarvis-core"]