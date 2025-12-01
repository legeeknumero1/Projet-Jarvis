# Multi-stage build for PyO3 Rust-Python bridge
FROM rust:1.90-slim AS builder

RUN apt-get update && apt-get install -y python3-pip patchelf pkg-config libssl-dev && rm -rf /var/lib/apt/lists/*
RUN pip3 install --break-system-packages maturin

WORKDIR /build
COPY Cargo.toml Cargo.lock ./
COPY src ./src

# Build the Python wheel with maturin
RUN maturin build --release --strip

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Install Python runtime dependencies
RUN pip3 install --no-cache-dir --break-system-packages numpy

# Copy built wheel from builder
COPY --from=builder /build/target/wheels/*.whl /tmp/

# Install the wheel
RUN pip3 install --break-system-packages /tmp/*.whl && rm /tmp/*.whl

# Copy test script
COPY tests/ ./tests/

# Expose port for gRPC or HTTP API (if needed)
EXPOSE 8005

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python3 -c "import jarvis_bridge; print('OK')" || exit 1

CMD ["python3", "-m", "http.server", "8005"]
