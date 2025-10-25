# Dockerfile pour Python Bridges IA - Phase 3
# Services : Ollama, Whisper, Piper, Embeddings
# Port : 8005

FROM python:3.11-slim as builder

# Dépendances système pour audio et modèles ML
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    libasound2-dev \
    libsndfile1-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copier requirements
COPY requirements.txt .

# Installer dépendances Python avec cache
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Dépendances runtime
RUN apt-get update && apt-get install -y \
    libasound2 \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copier venv depuis builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Créer utilisateur non-root
RUN groupadd -r jarvis && useradd -r -g jarvis jarvis

WORKDIR /app
RUN mkdir -p /app/logs && chown -R jarvis:jarvis /app

# Copier code application
COPY --chown=jarvis:jarvis . .

USER jarvis

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8005/health || exit 1

# Configuration
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
EXPOSE 8005

# Lancement
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=8005"]
