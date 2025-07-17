#!/usr/bin/env python3
"""
TTS API Service for Jarvis
Handles text-to-speech conversion using Piper TTS
"""

import asyncio
import logging
import os
import tempfile
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import torch
import torchaudio
from TTS.api import TTS
import httpx
import io
import wave
import numpy as np
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Jarvis TTS API", version="1.0.0")

class TTSRequest(BaseModel):
    text: str
    session_id: Optional[str] = None
    voice: Optional[str] = "default"
    speed: Optional[float] = 1.0
    pitch: Optional[float] = 1.0

class TTSService:
    def __init__(self):
        self.tts = None
        self.model_path = os.getenv("TTS_MODEL_PATH", "/app/models/tts")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"TTS Service initialized on device: {self.device}")
        
    async def initialize_model(self):
        """Initialize TTS model"""
        try:
            # Use Coqui TTS as mentioned in French.txt
            self.tts = TTS(
                model_name="tts_models/fr/css10/vits",  # French model
                device=self.device
            )
            logger.info("TTS model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load TTS model: {e}")
            # Fallback to English model
            try:
                self.tts = TTS(
                    model_name="tts_models/en/ljspeech/tacotron2-DDC",
                    device=self.device
                )
                logger.info("Fallback TTS model loaded successfully")
            except Exception as e2:
                logger.error(f"Failed to load fallback TTS model: {e2}")
                raise
    
    async def synthesize_chunk(self, text: str, session_id: str = None) -> bytes:
        """Synthesize text to speech in chunks for streaming"""
        try:
            if not self.tts:
                await self.initialize_model()
            
            # Create temporary file for audio output
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Generate speech
            self.tts.tts_to_file(
                text=text,
                file_path=temp_path
            )
            
            # Read generated audio
            with open(temp_path, 'rb') as f:
                audio_data = f.read()
            
            # Clean up temporary file
            os.unlink(temp_path)
            
            return audio_data
            
        except Exception as e:
            logger.error(f"TTS synthesis error: {e}")
            raise HTTPException(status_code=500, detail=f"TTS synthesis failed: {str(e)}")
    
    def split_text_into_sentences(self, text: str) -> list:
        """Split text into sentences for chunk processing"""
        import re
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]

# Global TTS service instance
tts_service = TTSService()

@app.on_event("startup")
async def startup_event():
    """Initialize TTS service on startup"""
    await tts_service.initialize_model()

@app.post("/synthesize")
async def synthesize_text(request: TTSRequest):
    """Synthesize text to speech"""
    try:
        # Split text into sentences for better quality (as mentioned in French.txt)
        sentences = tts_service.split_text_into_sentences(request.text)
        
        if not sentences:
            raise HTTPException(status_code=400, detail="No valid text to synthesize")
        
        # For streaming, we'll process sentence by sentence
        # For now, we'll concatenate all sentences
        all_audio_data = bytearray()
        
        for sentence in sentences:
            if sentence.strip():
                audio_chunk = await tts_service.synthesize_chunk(
                    sentence, 
                    request.session_id
                )
                all_audio_data.extend(audio_chunk)
        
        return {
            "status": "success",
            "audio_length": len(all_audio_data),
            "session_id": request.session_id
        }
        
    except Exception as e:
        logger.error(f"TTS synthesis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/synthesize_stream")
async def synthesize_stream(request: TTSRequest):
    """Synthesize text to speech with streaming support"""
    try:
        sentences = tts_service.split_text_into_sentences(request.text)
        
        chunks = []
        for sentence in sentences:
            if sentence.strip():
                audio_chunk = await tts_service.synthesize_chunk(
                    sentence, 
                    request.session_id
                )
                chunks.append({
                    "text": sentence,
                    "audio_data": audio_chunk,
                    "sequence": len(chunks)
                })
        
        return {
            "status": "success",
            "chunks": len(chunks),
            "session_id": request.session_id,
            "streaming_ready": True
        }
        
    except Exception as e:
        logger.error(f"TTS stream synthesis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "tts-api",
        "model_loaded": tts_service.tts is not None,
        "device": tts_service.device
    }

@app.get("/models")
async def list_models():
    """List available TTS models"""
    return {
        "available_models": [
            "tts_models/fr/css10/vits",
            "tts_models/en/ljspeech/tacotron2-DDC"
        ],
        "current_model": "tts_models/fr/css10/vits"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)