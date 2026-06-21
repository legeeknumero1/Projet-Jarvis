# Multi-stage build for jarvis-secretsd
FROM rust:slim AS builder

WORKDIR /build

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy source
COPY Cargo.toml Cargo.lock ./
COPY src ./src

# Build release binary
RUN cargo build --release

# Runtime stage
FROM debian:bookworm-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

# Create directories
RUN mkdir -p /etc/jarvis-secretsd /opt/jarvis/secrets /opt/jarvis/audit

# Copy binary
COPY --from=builder /build/target/release/jarvis-secretsd /usr/local/bin/

# Copy config
COPY config.toml /etc/jarvis-secretsd/
COPY policy.yaml /etc/jarvis-secretsd/

# Create non-root user
RUN useradd -r -u 1000 -m jarvis

# Set permissions
RUN chown -R jarvis:jarvis /opt/jarvis && \
    chown -R jarvis:jarvis /etc/jarvis-secretsd

USER jarvis

EXPOSE 8081

ENTRYPOINT ["/usr/local/bin/jarvis-secretsd"]
CMD ["--config", "/etc/jarvis-secretsd/config.toml"]
