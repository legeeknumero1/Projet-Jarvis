FROM python:3.11-slim

WORKDIR /app

ENV MALLOC_ARENA_MAX=2

# Install system dependencies (ffmpeg and PyAV build deps)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    pkg-config \
    libavformat-dev \
    libavcodec-dev \
    libavdevice-dev \
    libavutil-dev \
    libswscale-dev \
    libswresample-dev \
    libavfilter-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app.py .
COPY transcribe*.py ./
# (Optional) if there are models or other scripts, copy them
COPY models/ ./models/

RUN useradd -m -u 1000 jarvis && chown -R jarvis:jarvis /app
USER jarvis

EXPOSE 8005

CMD ["python", "app.py"]
