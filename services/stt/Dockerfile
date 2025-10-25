FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libsndfile1 \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY services/stt/requirements.txt ./requirements.txt
COPY requirements-unified.txt ./requirements-unified.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY services/stt/ .

# Create models directory
RUN mkdir -p /app/models/stt

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8003/health || exit 1

# Expose port
EXPOSE 8003

# Run the application
CMD ["python", "main.py"]
