"""Router Voice - endpoints vocaux STT/TTS"""
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Request
from fastapi.responses import StreamingResponse
from schemas.voice import TTSRequest, TranscriptionResponse
from security.deps import api_key_required
from utils.logging import get_logger
import io

router = APIRouter()
logger = get_logger(__name__)

@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    request: Request,
    file: UploadFile = File(...), 
    api_key: str = Depends(api_key_required)
):
    """
    Transcrit un fichier audio en texte
    Extrait de main.py:474-500
    """
    try:
        logger.info(f"🎤 [VOICE] Transcription fichier: {file.filename} ({file.content_type})")
        
        # Lire le contenu du fichier audio
        audio_data = await file.read()
        logger.debug(f"📁 [VOICE] Fichier lu: {len(audio_data)} bytes")
        
        # Utiliser voice_service depuis app.state (vrais services)
        voice_service = request.app.state.voice
        result = await voice_service.speech_to_text(audio_data)
        
        logger.info(f"✅ [VOICE] Transcription réussie: {result.transcript}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ [VOICE] Erreur transcription: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur de transcription: {str(e)}")

@router.post("/synthesize")
async def synthesize_speech(
    tts_request: TTSRequest,
    fastapi_request: Request, 
    api_key: str = Depends(api_key_required)
):
    """
    Synthétise du texte en audio
    Extrait de main.py:502-528
    """
    try:
        logger.info(f"🔊 [TTS] Synthèse texte: {tts_request.text[:50]}...")
        logger.debug(f"🎵 [TTS] Voix demandée: {tts_request.voice}")
        
        # Utiliser voice_service depuis app.state (vrais services)
        voice_service = fastapi_request.app.state.voice
        audio_data = await voice_service.text_to_speech(tts_request)
        
        if not audio_data:
            logger.error("❌ [TTS] Service TTS indisponible")
            raise HTTPException(status_code=503, detail="Service TTS indisponible")
        
        logger.info(f"✅ [TTS] Audio généré: {len(audio_data)} bytes")
        
        # Retourner l'audio comme streaming response
        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=speech.wav"}
        )
        
    except Exception as e:
        logger.error(f"❌ [TTS] Erreur synthèse: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur de synthèse: {str(e)}")