# Multi-stage build pour réduire la taille
FROM python:3.12-slim as builder

WORKDIR /app

# Installation dépendances build uniquement
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
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
    && rm -rf /var/lib/apt/lists/* \
    && apt-get autoremove -y \
    && apt-get clean

# Copie des dépendances installées
COPY --from=builder /root/.local /root/.local

# PATH pour les packages utilisateur
ENV PATH=/root/.local/bin:$PATH

# Créer utilisateur non-root
RUN groupadd -r jarvis && useradd -r -g jarvis jarvis

# Copie du code source et des dépendances vers home jarvis
COPY . .
COPY --from=builder /root/.local /home/jarvis/.local

# Création des dossiers nécessaires avec bonnes permissions
RUN mkdir -p models logs data && \
    chown -R jarvis:jarvis /app /home/jarvis/.local

# Changer vers utilisateur non-root et PATH
USER jarvis
ENV PATH=/home/jarvis/.local/bin:$PATH

# Exposition du port
EXPOSE 8000

# Commande de démarrage production (sans --reload)
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]