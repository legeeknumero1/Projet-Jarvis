#!/usr/bin/env python3
"""
STT API Service for Jarvis
Handles speech-to-text conversion using Whisper
"""

import asyncio
import logging
import os
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import torch
import whisper
import numpy as np
import librosa
import re
from typing import Optional, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Jarvis STT API", version="1.0.0")

class STTResponse(BaseModel):
    text: str
    confidence: float
    language: str
    segments: Optional[List[dict]] = None

class STTService:
    def __init__(self):
        self.model = None
        self.model_path = os.getenv("STT_MODEL_PATH", "/app/models/stt")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.hallucination_patterns = [
            "thank you", "thanks", "ok", "okay", "um", "uh", "ah", "eh", "mmm",
            "vous", "bien", "mais", "oui", "non", "voilà", "donc", "alors",
            "merci", "salut", "bonjour", "bonsoir", "au revoir"
        ]
        logger.info(f"STT Service initialized on device: {self.device}")
        
    async def initialize_model(self):
        """Initialize Whisper model"""
        try:
            # Use medium model for better accuracy
            self.model = whisper.load_model("medium", device=self.device)
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            # Fallback to smaller model
            try:
                self.model = whisper.load_model("small", device=self.device)
                logger.info("Fallback Whisper model loaded successfully")
            except Exception as e2:
                logger.error(f"Failed to load fallback model: {e2}")
                raise
    
    def is_hallucination(self, text: str) -> bool:
        """
        Detect hallucinations based on patterns from French.txt
        Implements the pre-filtering mentioned in the video
        """
        if not text or len(text.strip()) < 2:
            return True
            
        text_lower = text.lower().strip()
        
        # Check for common hallucination patterns
        for pattern in self.hallucination_patterns:
            if text_lower == pattern or text_lower.startswith(pattern + " "):
                return True
        
        # Check if text contains only non-latin characters
        if not re.search(r'[a-zA-Z]', text):
            return True
        
        # Check for very short meaningless text
        if len(text_lower) < 3 and text_lower in ["ok", "uh", "ah", "eh", "mm"]:
            return True
            
        return False
    
    def filter_transcription(self, text: str) -> str:
        """Apply additional filtering to transcription"""
        # Remove common filler words at the beginning
        filler_prefixes = ["euh", "um", "uh", "ah", "eh"]
        for prefix in filler_prefixes:
            if text.lower().startswith(prefix + " "):
                text = text[len(prefix):].strip()
        
        # Clean up punctuation
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single space
        text = text.strip()
        
        return text
    
    async def transcribe_audio(self, audio_file: UploadFile) -> STTResponse:
        """Transcribe audio file to text"""
        try:
            if not self.model:
                await self.initialize_model()
            
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                content = await audio_file.read()
                temp_file.write(content)
                temp_path = temp_file.name
            
            # Transcribe using Whisper
            result = self.model.transcribe(
                temp_path,
                language="fr",  # French as primary language
                task="transcribe",
                fp16=torch.cuda.is_available()
            )
            
            # Clean up temporary file
            os.unlink(temp_path)
            
            text = result["text"].strip()
            
            # Apply hallucination filtering
            if self.is_hallucination(text):
                return STTResponse(
                    text="",
                    confidence=0.0,
                    language=result.get("language", "fr"),
                    segments=[]
                )
            
            # Filter and clean transcription
            filtered_text = self.filter_transcription(text)
            
            # Calculate confidence (average of segment confidences)
            segments = result.get("segments", [])
            if segments:
                confidence = sum(seg.get("no_speech_prob", 0.0) for seg in segments) / len(segments)
                confidence = 1.0 - confidence  # Invert no_speech_prob
            else:
                confidence = 0.5  # Default confidence
            
            return STTResponse(
                text=filtered_text,
                confidence=confidence,
                language=result.get("language", "fr"),
                segments=segments
            )
            
        except Exception as e:
            logger.error(f"STT transcription error: {e}")
            raise HTTPException(status_code=500, detail=f"STT transcription failed: {str(e)}")

# Global STT service instance
stt_service = STTService()

@app.on_event("startup")
async def startup_event():
    """Initialize STT service on startup"""
    await stt_service.initialize_model()

@app.post("/transcribe", response_model=STTResponse)
async def transcribe_audio(audio: UploadFile = File(...)):
    """Transcribe audio to text"""
    try:
        if not audio.filename.endswith(('.wav', '.mp3', '.flac', '.m4a')):
            raise HTTPException(
                status_code=400, 
                detail="Unsupported audio format. Use WAV, MP3, FLAC, or M4A"
            )
        
        result = await stt_service.transcribe_audio(audio)
        
        logger.info(f"Transcription result: '{result.text}' (confidence: {result.confidence:.2f})")
        
        return result
        
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transcribe_stream")
async def transcribe_stream(audio: UploadFile = File(...)):
    """Transcribe audio with streaming support"""
    try:
        result = await stt_service.transcribe_audio(audio)
        
        return {
            "status": "success",
            "transcription": result,
            "streaming_ready": True
        }
        
    except Exception as e:
        logger.error(f"Stream transcription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "stt-api",
        "model_loaded": stt_service.model is not None,
        "device": stt_service.device
    }

@app.get("/models")
async def list_models():
    """List available STT models"""
    return {
        "available_models": [
            "tiny", "base", "small", "medium", "large"
        ],
        "current_model": "medium",
        "supported_languages": ["fr", "en"]
    }

@app.post("/test_hallucination")
async def test_hallucination(text: str):
    """Test hallucination detection"""
    is_hallucination = stt_service.is_hallucination(text)
    filtered_text = stt_service.filter_transcription(text)
    
    return {
        "original_text": text,
        "is_hallucination": is_hallucination,
        "filtered_text": filtered_text
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)