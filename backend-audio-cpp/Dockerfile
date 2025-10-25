# Phase 2: C++ Audio Engine (8004)
# DSP / FFmpeg / PortAudio + SPSC Lock-free Queues
#
# Purpose: Sub-millisecond audio processing
# - Noise suppression (Spectral Subtraction)
# - Echo cancellation (NLMS)
# - Gain normalization
# - Sample rate conversion

# ============================================================================
# Build Stage
# ============================================================================

FROM ubuntu:22.04 AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y \
    cmake \
    build-essential \
    g++ \
    git \
    libportaudio2 \
    libportaudio-dev \
    libfftw3-dev \
    libsndfile1-dev \
    && rm -rf /var/lib/apt/lists/*

# Optional: Install FFmpeg for advanced audio processing
# RUN apt-get install -y libavformat-dev libavcodec-dev libavutil-dev

# Copy source code
COPY . /build

# Build C++ library
RUN mkdir -p build && \
    cd build && \
    cmake -DCMAKE_BUILD_TYPE=Release .. && \
    cmake --build . --config Release -j$(nproc) && \
    ctest --output-on-failure

# ============================================================================
# Runtime Stage
# ============================================================================

FROM ubuntu:22.04 AS runtime

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libportaudio2 \
    libfftw3-3 \
    libsndfile1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy compiled library from builder
COPY --from=builder /build/build/lib/libaudio_engine_shared.so* /app/lib/
COPY --from=builder /build/include/audio_engine.h /app/include/

# Expose health check port (when integrated with Phase 1)
EXPOSE 8004

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8004/health || exit 1

# Set LD_LIBRARY_PATH
ENV LD_LIBRARY_PATH=/app/lib:$LD_LIBRARY_PATH

# Run audio engine (in production, this would be wrapped by Phase 1 Rust API)
CMD ["echo", "Audio Engine C++ Library Ready. Awaiting connections from Phase 1 (Rust Core)."]

# ============================================================================
# Build & Run
# ============================================================================
#
# Build:
#   docker build -t jarvis-audio-engine:1.9.0 .
#
# Run:
#   docker run -d --name audio-engine jarvis-audio-engine:1.9.0
#
# Verify:
#   docker logs audio-engine
#   docker exec audio-engine curl -f http://localhost:8004/health
