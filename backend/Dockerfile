# Multi-stage build pour réduire la taille
FROM python:3.12-slim as builder

WORKDIR /app

# Installation dépendances build + PostgreSQL dev
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    libpq-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Installation dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage final - image légère
FROM python:3.12-slim

WORKDIR /app

# Installation dépendances runtime uniquement
RUN apt-get update && apt-get install -y \
    curl \
    ffmpeg \
    libsndfile1 \
    portaudio19-dev \
    libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get autoremove -y \
    && apt-get clean

# Copie des dépendances installées
COPY --from=builder /root/.local /root/.local

# PATH pour les packages utilisateur + Python modules
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app

# Copie du code source complet
COPY . .

# Création des dossiers nécessaires
RUN mkdir -p models logs data

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Exposition du port
EXPOSE 8000

# Commande de démarrage production
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]