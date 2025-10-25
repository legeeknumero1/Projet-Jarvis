# Dockerfile pour Jarvis Audio Engine C++
# Build multi-stage pour taille minimale

# Stage 1: Builder
FROM ubuntu:22.04 as builder

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    libasound2-dev \
    libpipewire-0.3-dev \
    libspa-0.2-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Cloner et compiler whisper.cpp
RUN git clone https://github.com/ggerganov/whisper.cpp.git /tmp/whisper.cpp && \
    cd /tmp/whisper.cpp && \
    mkdir build && cd build && \
    cmake .. -DBUILD_SHARED_LIBS=ON && \
    make -j$(nproc) && \
    make install

# Cloner et compiler piper
RUN git clone https://github.com/rhasspy/piper.git /tmp/piper && \
    cd /tmp/piper/src/cpp && \
    mkdir build && cd build && \
    cmake .. -DBUILD_SHARED_LIBS=ON && \
    make -j$(nproc) && \
    make install

# Construire Jarvis Audio Engine
COPY . /app
WORKDIR /app

RUN mkdir -p build && cd build && \
    cmake .. -DCMAKE_BUILD_TYPE=Release && \
    make -j$(nproc)

# Stage 2: Runtime
FROM ubuntu:22.04

# Installer dépendances runtime
RUN apt-get update && apt-get install -y \
    libasound2 \
    libpipewire-0.3-0 \
    libstdc++6 \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copier les binaires compilés
COPY --from=builder /app/build/jarvis-audio-api /usr/local/bin/
COPY --from=builder /usr/local/lib/libwhisper* /usr/local/lib/
COPY --from=builder /usr/local/lib/libpiper* /usr/local/lib/

# Créer utilisateur non-root
RUN groupadd -r jarvis && useradd -r -g jarvis jarvis

WORKDIR /app
RUN mkdir -p /app/logs && chown -R jarvis:jarvis /app

USER jarvis

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8004/health || exit 1

# Configuration
ENV RUST_LOG=info
EXPOSE 8004

# Lancement
CMD ["jarvis-audio-api"]