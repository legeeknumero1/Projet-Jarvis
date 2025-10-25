"""Service Voice pour STT/TTS avec timeouts et retries"""
import logging
import httpx
import asyncio
import random
from typing import Optional
from schemas.voice import TTSRequest, TranscriptionResponse

logger = logging.getLogger(__name__)

class VoiceService:
    """Service centralisé pour reconnaissance et synthèse vocale"""
    
    def __init__(self, settings):
        self.settings = settings
        self.speech_manager = None
        # Clients HTTP pour STT/TTS avec timeouts
        self.stt_client = httpx.AsyncClient(
            timeout=httpx.Timeout(15.0, connect=5.0),
            base_url=settings.stt_api_url
        )
        self.tts_client = httpx.AsyncClient(
            timeout=httpx.Timeout(10.0, connect=5.0),
            base_url=settings.tts_api_url
        )
        
    async def initialize(self):
        """Initialise le gestionnaire vocal"""
        try:
            # Import dynamique pour éviter dépendance au démarrage
            from speech.speech_manager import SpeechManager
            
            self.speech_manager = SpeechManager(self.settings)
            
            if hasattr(self.speech_manager, 'initialize'):
                logger.info("🎤 [VOICE] Initialisation gestionnaire vocal...")
                await self.speech_manager.initialize()
                logger.info("✅ [VOICE] Gestionnaire vocal initialisé")
            else:
                logger.info("ℹ️ [VOICE] Speech manager initialisé (pas de méthode initialize)")
                
        except Exception as e:
            logger.error(f"❌ [VOICE] Erreur initialisation: {e}")
    
    async def close(self):
        """Ferme les clients HTTP"""
        await self.stt_client.aclose()
        await self.tts_client.aclose()
        
    async def _retry_with_backoff(self, func, max_retries=3, base_delay=1.0):
        """Retry avec backoff exponentiel"""
        for attempt in range(max_retries):
            try:
                return await func()
            except (httpx.TimeoutException, httpx.ConnectError, asyncio.TimeoutError) as e:
                if attempt == max_retries - 1:
                    raise e
                
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                logger.warning(f"⚠️ [VOICE] Tentative {attempt + 1}/{max_retries} échouée, retry dans {delay:.1f}s: {e}")
                await asyncio.sleep(delay)
    
    async def ping(self) -> bool:
        """Health check pour STT/TTS services"""
        try:
            async def _ping_stt():
                resp = await self.stt_client.get("/health")
                return resp.status_code == 200
            
            return await self._retry_with_backoff(_ping_stt, max_retries=2, base_delay=0.5)
        except Exception:
            return False
    
    def is_available(self) -> bool:
        """Vérifie si le service Voice est disponible"""
        return self.speech_manager is not None
    
    async def speech_to_text(self, audio_data: bytes) -> TranscriptionResponse:
        """
        Transcrit audio vers texte via Whisper
        Wrapper pour speech_manager.speech_to_text()
        """
        try:
            if not self.is_available():
                logger.error("❌ [VOICE] Speech manager non disponible pour STT")
                return TranscriptionResponse(
                    transcript="", 
                    confidence=0.0
                )
            
            logger.info(f"🎤 [VOICE] Transcription audio ({len(audio_data)} bytes)")
            
            # Appel au speech manager existant
            transcript = await self.speech_manager.speech_to_text(audio_data)
            
            if transcript:
                logger.info(f"✅ [VOICE] Transcription réussie: {transcript}")
                return TranscriptionResponse(
                    transcript=transcript,
                    confidence=0.95,  # Confidence fixe pour l'instant
                    duration=None  # Durée non calculée pour l'instant
                )
            else:
                logger.warning("⚠️ [VOICE] Transcription vide")
                return TranscriptionResponse(
                    transcript="",
                    confidence=0.0
                )
                
        except Exception as e:
            logger.error(f"❌ [VOICE] Erreur transcription: {e}")
            return TranscriptionResponse(
                transcript="",
                confidence=0.0
            )
    
    async def text_to_speech(self, request: TTSRequest) -> Optional[bytes]:
        """
        Synthétise texte vers audio via Piper
        Wrapper pour speech_manager.text_to_speech()
        """
        try:
            if not self.is_available():
                logger.error("❌ [VOICE] Speech manager non disponible pour TTS")
                return None
            
            logger.info(f"🔊 [VOICE] Synthèse texte: {request.text[:50]}...")
            logger.debug(f"🎵 [VOICE] Voix demandée: {request.voice}")
            
            # Appel au speech manager existant
            audio_data = await self.speech_manager.text_to_speech(request.text)
            
            if audio_data is None:
                logger.error("❌ [VOICE] Service TTS indisponible")
                return None
            
            logger.info(f"✅ [VOICE] Audio généré: {len(audio_data)} bytes")
            return audio_data
                
        except Exception as e:
            logger.error(f"❌ [VOICE] Erreur synthèse: {e}")
            return None
