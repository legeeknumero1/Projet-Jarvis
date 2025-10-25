FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install setuptools
RUN pip install --upgrade pip setuptools wheel

# Install Python dependencies
COPY services/interface/requirements.txt ./requirements.txt
COPY requirements-unified.txt ./requirements-unified.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY services/interface/ .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Expose ports
EXPOSE 8001

# Run the hybrid server
CMD ["python", "hybrid_server.py"]
