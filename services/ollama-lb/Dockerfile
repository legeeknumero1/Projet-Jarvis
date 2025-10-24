# Ollama Load Balancer - Jarvis v1.3.2
# Smart load balancing pour instances Ollama multiples

FROM python:3.11-slim

WORKDIR /app

# Installer dépendances système
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Installer dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier code source
COPY . .

# Configuration
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Ports
EXPOSE 11434

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:11434/health || exit 1

# Démarrage
CMD ["python", "ollama_lb.py"]