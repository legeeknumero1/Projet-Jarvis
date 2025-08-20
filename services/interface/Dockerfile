# Multi-stage build: Stage 1 - Build React frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./
COPY frontend/bun.lock* ./

# Install dependencies with bun (faster than npm)
RUN npm install -g bun
RUN bun install

# Copy frontend source and build
COPY frontend/ ./
RUN bun run build

# Stage 2 - Python backend + serve React build
FROM python:3.12-slim AS production

WORKDIR /app

# Install system dependencies including Node.js for hybrid server
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install setuptools
RUN pip install --upgrade pip setuptools wheel

# Install Python dependencies
COPY ./services/interface/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python application code
COPY ./services/interface/ .

# Copy built React frontend from stage 1
COPY --from=frontend-builder /app/frontend/build ./static/

# Create environment file with proper configuration
RUN echo "NODE_ENV=production" > .env && \
    echo "REACT_APP_API_URL=http://localhost:8000" >> .env && \
    echo "REACT_APP_WS_URL=ws://localhost:8000/ws" >> .env

# Health check on correct port
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose correct ports
EXPOSE 8000 3000 8001

# Run the hybrid server
CMD ["python", "hybrid_server.py"]
