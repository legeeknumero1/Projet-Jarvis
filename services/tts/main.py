#!/usr/bin/env python3
"""
TTS API Service for Jarvis - Simplified Version  
Provides basic text-to-speech endpoints
"""

import asyncio
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Jarvis TTS API", version="1.0.0")

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
    try:
        logger.info(f"Synthesizing: {request.text[:50]}...")
        
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
            
            return TTSResponse(
                audio_url=output_path,
                duration=duration,
                voice_used=request.voice
            )
            
        except ImportError:
            logger.warning("Coqui TTS not available - using demo mode")
            # Fallback vers mode demo si TTS n'est pas installé
            return TTSResponse(
                audio_url="/audio/demo_response.wav",
                duration=len(request.text) * 0.1,  # Estimation basique
                voice_used=request.voice + "_demo"
            )
        
    except Exception as e:
        logger.error(f"TTS synthesis error: {e}")
        raise HTTPException(status_code=500, detail="TTS synthesis failed")

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

@app.get("/status")
async def get_status():
    """Get TTS service status"""
    return {
        "service": "jarvis-tts-api",
        "status": "running",
        "model": "demo-mode",
        "ip": "172.20.0.20",
        "port": 8002
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Jarvis TTS API service...")
    uvicorn.run(app, host="0.0.0.0", port=8002)