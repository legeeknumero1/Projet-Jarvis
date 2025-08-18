# Multi-stage build: Stage 1 - Build dependencies
FROM python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libsndfile1-dev \
    libespeak-ng-dev \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install with optimizations
COPY requirements.txt /tmp/requirements.txt

# Install PyTorch CPU-only (smaller size) and Coqui TTS
RUN pip install --no-cache-dir \
    torch==2.1.0+cpu \
    torchaudio==2.1.0+cpu \
    --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r /tmp/requirements.txt

# Stage 2 - Production runtime
FROM python:3.11-slim AS production

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    curl \
    libsndfile1 \
    espeak-ng \
    espeak-ng-data \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY main.py .
COPY . .

# Create models directory with proper permissions
RUN mkdir -p /app/models/tts && \
    chmod 755 /app/models/tts

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash --uid 1000 tts-user && \
    chown -R tts-user:tts-user /app
USER tts-user

# Environment variables for optimization
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TTS_MODEL_CACHE=/app/models/tts \
    TORCH_NUM_THREADS=2

# Health check with longer timeout for TTS models
HEALTHCHECK --interval=60s --timeout=30s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

# Expose port
EXPOSE 8002

# Run the application
CMD ["python", "main.py"]