from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn
import asyncio
import json
import logging
import io
from typing import List, Dict, Any
import os
from datetime import datetime

from config.config import Config
from db.database import Database
from memory.memory_manager import MemoryManager
from profile.profile_manager import ProfileManager
from speech.speech_manager import SpeechManager
from integration.home_assistant import HomeAssistantIntegration
from integration.ollama_client import OllamaClient

app = FastAPI(title="Jarvis AI Assistant", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8001"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

config = Config()
db = Database(config)
memory_manager = MemoryManager(db)
profile_manager = ProfileManager(db)
speech_manager = SpeechManager(config)
home_assistant = HomeAssistantIntegration(config)
ollama_client = OllamaClient(base_url="http://localhost:11434")

class MessageRequest(BaseModel):
    message: str
    user_id: str = "default"

class MessageResponse(BaseModel):
    response: str
    timestamp: datetime

class TranscriptionResponse(BaseModel):
    transcript: str
    confidence: float

class TTSRequest(BaseModel):
    text: str
    voice: str = "default"

@app.on_event("startup")
async def startup_event():
    await db.connect()
    await memory_manager.initialize()
    await profile_manager.initialize()
    await speech_manager.initialize()
    await home_assistant.connect()
    
    # Vérifier et préparer Ollama
    try:
        if await ollama_client.is_available():
            await ollama_client.ensure_model_available("llama3.1:latest")
            print("✅ Ollama est prêt avec LLaMA 3.1")
        else:
            print("⚠️ Ollama non disponible")
    except Exception as e:
        print(f"⚠️ Erreur Ollama: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    await db.disconnect()
    await home_assistant.disconnect()
    if hasattr(ollama_client, 'client'):
        await ollama_client.client.aclose()

@app.get("/")
async def root():
    return {"message": "Jarvis AI Assistant is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

@app.post("/chat", response_model=MessageResponse)
async def chat(request: MessageRequest):
    try:
        # Récupération du contexte utilisateur
        user_context = await memory_manager.get_user_context(request.user_id)
        
        # Traitement du message avec l'IA
        response = await process_message(request.message, user_context)
        
        # Sauvegarde de la conversation
        await memory_manager.save_conversation(
            request.user_id, 
            request.message, 
            response
        )
        
        return MessageResponse(
            response=response,
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Traitement du message en temps réel
            response = await process_message(
                message_data["message"],
                await memory_manager.get_user_context(message_data.get("user_id", "default"))
            )
            
            await websocket.send_text(json.dumps({
                "response": response,
                "timestamp": datetime.now().isoformat()
            }))
    except WebSocketDisconnect:
        pass

@app.post("/voice/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(file: UploadFile = File(...)):
    """Transcrit un fichier audio en texte"""
    try:
        # Lire le contenu du fichier audio
        audio_data = await file.read()
        
        # Utiliser le speech manager pour la transcription
        transcript = await speech_manager.speech_to_text(audio_data)
        
        return TranscriptionResponse(
            transcript=transcript,
            confidence=0.95  # Pour l'instant, confidence fixe
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de transcription: {str(e)}")

@app.post("/voice/synthesize")
async def synthesize_speech(request: TTSRequest):
    """Synthétise du texte en audio"""
    try:
        # Générer l'audio avec le speech manager
        audio_data = await speech_manager.text_to_speech(request.text)
        
        if audio_data is None:
            raise HTTPException(status_code=503, detail="Service TTS indisponible")
        
        # Retourner l'audio comme streaming response
        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=speech.wav"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de synthèse: {str(e)}")

async def process_message(message: str, context: Dict[str, Any]) -> str:
    """Traite un message et retourne une réponse"""
    try:
        # Préparer le contexte pour l'IA
        system_prompt = """Tu es Jarvis, l'assistant IA personnel d'Enzo. Tu dois répondre en français de manière naturelle et utile. 
        Tu peux contrôler la domotique, répondre aux questions et aider avec diverses tâches.
        Sois concis mais informatif."""
        
        # Utiliser Ollama pour générer la réponse
        if await ollama_client.is_available():
            response = await ollama_client.chat(
                model="llama3.1:latest",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                max_tokens=512
            )
            
            if response:
                return response.strip()
            else:
                return "Désolé, je n'ai pas pu traiter votre demande."
        else:
            return "Jarvis est temporairement indisponible. Ollama n'est pas connecté."
            
    except Exception as e:
        logging.error(f"Erreur lors du traitement du message: {e}")
        return "Une erreur s'est produite lors du traitement de votre message."

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)