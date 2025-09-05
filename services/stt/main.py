#!/usr/bin/env python3
"""
STT API Service for Jarvis - Simplified Version
Provides basic speech-to-text endpoints
"""

import asyncio
import logging
import time
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Jarvis STT API", version="1.0.0")

# Métriques Prometheus pour STT
class STTMetrics:
    def __init__(self):
        self.transcribe_requests = 0
        self.transcribe_errors = 0
        self.total_processing_time = 0.0
        self.active_transcriptions = 0
        self.start_time = time.time()
    
    def record_transcription(self, duration: float, success: bool = True):
        self.transcribe_requests += 1
        self.total_processing_time += duration
        if not success:
            self.transcribe_errors += 1
    
    def get_avg_processing_time(self):
        if self.transcribe_requests == 0:
            return 0.0
        return self.total_processing_time / self.transcribe_requests

# Instance globale des métriques
stt_metrics = STTMetrics()

class STTResponse(BaseModel):
    text: str
    confidence: float
    duration: float

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="jarvis-stt-api",
        version="1.0.0"
    )

@app.post("/transcribe", response_model=STTResponse)
async def transcribe_audio(file: UploadFile = File(...)):
    """Transcribe audio file to text using Whisper"""
    start_time = time.time()
    stt_metrics.active_transcriptions += 1
    
    try:
        logger.info(f"Processing audio file: {file.filename}")
        
        # Lire les données audio
        audio_data = await file.read()
        
        # Sauvegarder temporairement le fichier
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(audio_data)
        
        try:
            # Importer whisper seulement quand nécessaire
            import whisper
            
            # Charger le modèle Whisper (base pour rapidité)
            model = whisper.load_model("base")
            
            # Transcrire l'audio
            result = model.transcribe(temp_path, language="fr")
            
            # Nettoyer le fichier temporaire
            os.unlink(temp_path)
            
            processing_duration = time.time() - start_time
            stt_metrics.record_transcription(processing_duration, True)
            
            return STTResponse(
                text=result["text"].strip(),
                confidence=0.95,  # Whisper ne donne pas de score de confiance
                duration=result.get("duration", 0.0)
            )
            
        except ImportError:
            logger.warning("Whisper not available - using demo mode")
            processing_duration = time.time() - start_time
            stt_metrics.record_transcription(processing_duration, True)
            
            # Fallback vers mode demo si whisper n'est pas installé
            return STTResponse(
                text="[DEMO] Bonjour, transcription automatique en cours...",
                confidence=0.85,
                duration=2.0
            )
        
    except Exception as e:
        logger.error(f"STT processing error: {e}")
        processing_duration = time.time() - start_time
        stt_metrics.record_transcription(processing_duration, False)
        raise HTTPException(status_code=500, detail="STT processing failed")
    
    finally:
        stt_metrics.active_transcriptions -= 1

@app.get("/metrics")
async def get_metrics():
    """Métriques Prometheus pour le service STT"""
    uptime = time.time() - stt_metrics.start_time
    
    metrics_output = f"""# HELP stt_transcribe_requests_total Total number of transcription requests
# TYPE stt_transcribe_requests_total counter
stt_transcribe_requests_total {stt_metrics.transcribe_requests}

# HELP stt_transcribe_errors_total Total number of transcription errors
# TYPE stt_transcribe_errors_total counter
stt_transcribe_errors_total {stt_metrics.transcribe_errors}

# HELP stt_processing_time_seconds Average transcription processing time
# TYPE stt_processing_time_seconds gauge
stt_processing_time_seconds {stt_metrics.get_avg_processing_time():.3f}

# HELP stt_active_transcriptions Current active transcriptions
# TYPE stt_active_transcriptions gauge
stt_active_transcriptions {stt_metrics.active_transcriptions}

# HELP stt_uptime_seconds Uptime in seconds
# TYPE stt_uptime_seconds gauge
stt_uptime_seconds {uptime:.1f}

# HELP stt_service_status Service status (1=up, 0=down)
# TYPE stt_service_status gauge
stt_service_status 1
"""
    return PlainTextResponse(metrics_output)

@app.get("/status")
async def get_status():
    """Get STT service status"""
    return {
        "service": "jarvis-stt-api",
        "status": "running",
        "model": "demo-mode",
        "ip": "172.20.0.10",
        "port": 8003,
        "metrics": {
            "transcribe_requests": stt_metrics.transcribe_requests,
            "transcribe_errors": stt_metrics.transcribe_errors,
            "uptime": time.time() - stt_metrics.start_time
        }
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Jarvis STT API service...")
    uvicorn.run(app, host="0.0.0.0", port=8003)