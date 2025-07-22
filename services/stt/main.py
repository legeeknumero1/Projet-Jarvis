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
    """Transcribe audio file to text"""
    try:
        # Simulate STT processing
        logger.info(f"Processing audio file: {file.filename}")
        
        # For demo purposes, return a fixed response
        return STTResponse(
            text="Bonjour, ceci est un test de transcription audio.",
            confidence=0.95,
            duration=2.5
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