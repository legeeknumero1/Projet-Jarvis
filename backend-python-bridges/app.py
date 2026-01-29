from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import base64
import numpy as np
import jwt
from datetime import datetime, timedelta
from loguru import logger
import traceback

# Clients IA (à adapter pour l'async si nécessaire)
from ollama_client import get_ollama_client
# Whisper et Piper restent sync car ils sont gourmands en CPU/GPU et tournent en local
from whisper_client import get_whisper_client
from piper_client import get_piper_client

import asyncio

# Limiter la concurrence pour les tâches lourdes (LLM, STT, TTS)
# Ajustez cette valeur selon votre GPU/CPU (ex: 1 pour un petit GPU, 4 pour un gros serveur)
AI_CONCURRENCY_LIMIT = int(os.environ.get("AI_CONCURRENCY_LIMIT", "2"))
ai_semaphore = asyncio.Semaphore(AI_CONCURRENCY_LIMIT)

app = FastAPI(title="Jarvis Python Bridges", version="1.4.0")

# CORS
cors_origins = os.environ.get("CORS_ORIGINS", "http://localhost:3000,http://localhost:8100").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in cors_origins if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"

# Models
class ChatRequest(BaseModel):
    prompt: str
    system_prompt: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 512

class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = "fr_FR-upmc-medium"
    speed: Optional[float] = 1.0

# Auth dependency
async def verify_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@app.get("/health")
async def health():
    ollama_ok = await get_ollama_client().health_check()
    return {"status": "healthy" if ollama_ok else "degraded", "services": {"ollama": ollama_ok}}

@app.post("/api/llm/generate")
async def llm_generate(req: ChatRequest, user=Depends(verify_token)):
    async with ai_semaphore:
        try:
            client = get_ollama_client()
            result = await client.generate(
                prompt=req.prompt,
                system_prompt=req.system_prompt,
                temperature=req.temperature,
                max_tokens=req.max_tokens
            )
            return {
                "text": result.text,
                "model": result.model,
                "duration_ms": result.duration_ms
            }
        except Exception as e:
            logger.error(f"LLM Error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tts/synthesize")
async def tts_synthesize(req: TTSRequest, user=Depends(verify_token)):
    # Whisper et Piper sont CPU-bound, on les laisse en sync dans le thread pool de FastAPI
    try:
        client = get_piper_client()
        result = client.synthesize(text=req.text, voice=req.voice, speed=req.speed)
        audio_b64 = base64.b64encode(result.audio_samples.astype(np.float32).tobytes()).decode()
        return {"audio_data": audio_b64, "sample_rate": result.sample_rate, "voice": result.voice}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)