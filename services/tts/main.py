#!/usr/bin/env python3
"""
TTS API Service for Jarvis - Simplified Version  
Provides basic text-to-speech endpoints
"""

import asyncio
import logging
import time
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Jarvis TTS API", version="1.0.0")

# Métriques Prometheus pour TTS
class TTSMetrics:
    def __init__(self):
        self.synthesis_requests = 0
        self.synthesis_errors = 0
        self.total_synthesis_time = 0.0
        self.total_text_length = 0
        self.active_synthesis = 0
        self.start_time = time.time()
    
    def record_synthesis(self, text_length: int, duration: float, success: bool = True):
        self.synthesis_requests += 1
        self.total_synthesis_time += duration
        self.total_text_length += text_length
        if not success:
            self.synthesis_errors += 1
    
    def get_avg_synthesis_time(self):
        if self.synthesis_requests == 0:
            return 0.0
        return self.total_synthesis_time / self.synthesis_requests
    
    def get_avg_text_length(self):
        if self.synthesis_requests == 0:
            return 0.0
        return self.total_text_length / self.synthesis_requests

# Instance globale des métriques
tts_metrics = TTSMetrics()

class TTSRequest(BaseModel):
    text: str
    voice: str = "default"
    speed: float = 1.0

class TTSResponse(BaseModel):
    audio_url: str
    duration: float
    voice_used: str

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="jarvis-tts-api",
        version="1.0.0"
    )

@app.post("/synthesize", response_model=TTSResponse)
async def synthesize_speech(request: TTSRequest):
    """Synthesize text to speech using Coqui TTS"""
    start_time = time.time()
    tts_metrics.active_synthesis += 1
    
    try:
        logger.info(f"Synthesizing: {request.text[:50]}...")
        text_length = len(request.text)
        
        try:
            # Importer TTS seulement quand nécessaire
            from TTS.api import TTS
            import torch
            
            # Choisir le device (GPU si disponible)
            device = "cuda" if torch.cuda.is_available() else "cpu"
            
            # Initialiser TTS (modèle français)
            tts = TTS("tts_models/fr/mai/tacotron2-DDC")
            if device == "cuda":
                tts = tts.to(device)
            
            # Générer l'audio
            output_path = f"/tmp/tts_output_{hash(request.text)}.wav"
            tts.tts_to_file(text=request.text, file_path=output_path)
            
            # Calculer la durée approximative (mots par minute)
            word_count = len(request.text.split())
            duration = (word_count / 150) * 60  # ~150 mots/min
            
            synthesis_duration = time.time() - start_time
            tts_metrics.record_synthesis(text_length, synthesis_duration, True)
            
            return TTSResponse(
                audio_url=output_path,
                duration=duration,
                voice_used=request.voice
            )
            
        except ImportError:
            logger.warning("Coqui TTS not available - using demo mode")
            synthesis_duration = time.time() - start_time
            tts_metrics.record_synthesis(text_length, synthesis_duration, True)
            
            # Fallback vers mode demo si TTS n'est pas installé
            return TTSResponse(
                audio_url="/audio/demo_response.wav",
                duration=len(request.text) * 0.1,  # Estimation basique
                voice_used=request.voice + "_demo"
            )
        
    except Exception as e:
        logger.error(f"TTS synthesis error: {e}")
        synthesis_duration = time.time() - start_time
        tts_metrics.record_synthesis(len(request.text), synthesis_duration, False)
        raise HTTPException(status_code=500, detail="TTS synthesis failed")
    
    finally:
        tts_metrics.active_synthesis -= 1

@app.get("/voices")
async def get_available_voices():
    """Get list of available voices"""
    return {
        "voices": [
            {"name": "default", "language": "fr-FR", "gender": "neutral"},
            {"name": "jarvis", "language": "fr-FR", "gender": "male"},
            {"name": "nova", "language": "fr-FR", "gender": "female"}
        ]
    }

@app.get("/metrics")
async def get_metrics():
    """Métriques Prometheus pour le service TTS"""
    uptime = time.time() - tts_metrics.start_time
    
    metrics_output = f"""# HELP tts_synthesis_requests_total Total number of synthesis requests
# TYPE tts_synthesis_requests_total counter
tts_synthesis_requests_total {tts_metrics.synthesis_requests}

# HELP tts_synthesis_errors_total Total number of synthesis errors
# TYPE tts_synthesis_errors_total counter
tts_synthesis_errors_total {tts_metrics.synthesis_errors}

# HELP tts_synthesis_time_seconds Average synthesis time
# TYPE tts_synthesis_time_seconds gauge
tts_synthesis_time_seconds {tts_metrics.get_avg_synthesis_time():.3f}

# HELP tts_text_length_average Average text length processed
# TYPE tts_text_length_average gauge
tts_text_length_average {tts_metrics.get_avg_text_length():.1f}

# HELP tts_active_synthesis Current active synthesis
# TYPE tts_active_synthesis gauge
tts_active_synthesis {tts_metrics.active_synthesis}

# HELP tts_uptime_seconds Uptime in seconds
# TYPE tts_uptime_seconds gauge
tts_uptime_seconds {uptime:.1f}

# HELP tts_service_status Service status (1=up, 0=down)
# TYPE tts_service_status gauge
tts_service_status 1
"""
    return PlainTextResponse(metrics_output)

@app.get("/status")
async def get_status():
    """Get TTS service status"""
    return {
        "service": "jarvis-tts-api",
        "status": "running",
        "model": "demo-mode",
        "ip": "172.20.0.20",
        "port": 8002,
        "metrics": {
            "synthesis_requests": tts_metrics.synthesis_requests,
            "synthesis_errors": tts_metrics.synthesis_errors,
            "uptime": time.time() - tts_metrics.start_time,
            "avg_text_length": tts_metrics.get_avg_text_length()
        }
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Jarvis TTS API service...")
    uvicorn.run(app, host="0.0.0.0", port=8002)