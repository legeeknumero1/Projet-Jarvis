#!/usr/bin/env python3
"""
STT API Service for Jarvis - Simplified Version
Provides basic speech-to-text endpoints
"""

import asyncio
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Jarvis STT API", version="1.0.0")

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
            
            return STTResponse(
                text=result["text"].strip(),
                confidence=0.95,  # Whisper ne donne pas de score de confiance
                duration=result.get("duration", 0.0)
            )
            
        except ImportError:
            logger.warning("Whisper not available - using demo mode")
            # Fallback vers mode demo si whisper n'est pas installé
            return STTResponse(
                text="[DEMO] Bonjour, transcription automatique en cours...",
                confidence=0.85,
                duration=2.0
            )
        
    except Exception as e:
        logger.error(f"STT processing error: {e}")
        raise HTTPException(status_code=500, detail="STT processing failed")

@app.get("/status")
async def get_status():
    """Get STT service status"""
    return {
        "service": "jarvis-stt-api",
        "status": "running",
        "model": "demo-mode",
        "ip": "172.20.0.10",
        "port": 8003
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Jarvis STT API service...")
    uvicorn.run(app, host="0.0.0.0", port=8003)