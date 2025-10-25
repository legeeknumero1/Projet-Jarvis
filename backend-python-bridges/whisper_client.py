"""
Client Whisper STT - Phase 3 Python Bridges
Speech-to-Text avec OpenAI Whisper local
"""

import whisper
import numpy as np
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
from loguru import logger
import os


@dataclass
class WhisperResult:
    """Résultat de transcription Whisper"""
    text: str
    language: str
    confidence: float  # 0.0 à 1.0
    duration_ms: float
    segments: list[Dict[str, Any]]


class WhisperClient:
    """Client Whisper STT local"""

    # Modèles disponibles
    MODELS = {
        "tiny": "tiny (39M, ~1s latence)",
        "base": "base (74M, ~5s latence)",
        "small": "small (244M, ~15s latence)",
        "medium": "medium (769M, ~40s latence)",
        "large": "large (1.5B, ~80s latence)"
    }

    def __init__(
        self,
        model_size: str = "base",
        language: Optional[str] = None,
        device: str = "cpu"
    ):
        """
        Initialiser le client Whisper

        Args:
            model_size: Taille du modèle (tiny, base, small, medium, large)
            language: Code langue (ex: 'fr', 'en'). None = auto-detect
            device: 'cpu' ou 'cuda' (si disponible)
        """
        self.model_size = model_size
        self.language = language
        self.device = device

        logger.info(f"🎤 Whisper Client initializing: {model_size}")
        try:
            self.model = whisper.load_model(model_size, device=device)
            logger.info(f"✅ Whisper model loaded: {model_size}")
        except Exception as e:
            logger.error(f"❌ Error loading Whisper model: {e}")
            raise

    def transcribe(
        self,
        audio: np.ndarray,
        sample_rate: int = 16000,
        language: Optional[str] = None,
        temperature: float = 0.0
    ) -> WhisperResult:
        """
        Transcrire audio en texte

        Args:
            audio: Array numpy avec échantillons audio (float32)
            sample_rate: Fréquence d'échantillonnage (Hz)
            language: Code langue (optionnel, sinon auto-detect)
            temperature: Température du modèle (0.0-1.0)

        Returns:
            WhisperResult avec texte transcrit et métadonnées
        """
        try:
            import time
            start_time = time.time()

            logger.debug(f"🎤 Transcribing {len(audio) / sample_rate:.1f}s of audio")

            # Normaliser audio si nécessaire
            if audio.max() > 1.0:
                audio = audio / 32768.0
            elif audio.min() < -1.0:
                audio = np.clip(audio, -1.0, 1.0)

            # Transcrire
            result = self.model.transcribe(
                audio,
                language=language or self.language,
                temperature=temperature,
                verbose=False
            )

            duration_ms = (time.time() - start_time) * 1000

            # Extraire segments
            segments = []
            for segment in result.get("segments", []):
                segments.append({
                    "id": segment.get("id"),
                    "start": segment.get("start"),
                    "end": segment.get("end"),
                    "text": segment.get("text", "").strip(),
                    "confidence": segment.get("confidence", 0.0)
                })

            logger.info(f"✅ Transcription done in {duration_ms:.0f}ms: {result.get('text', '')[:50]}")

            return WhisperResult(
                text=result.get("text", "").strip(),
                language=result.get("language", "unknown"),
                confidence=0.95,  # Whisper ne donne pas de confiance globale
                duration_ms=duration_ms,
                segments=segments
            )

        except Exception as e:
            logger.error(f"❌ Transcription error: {e}")
            return WhisperResult(
                text=f"Error: {str(e)}",
                language="unknown",
                confidence=0.0,
                duration_ms=0,
                segments=[]
            )

    def transcribe_file(
        self,
        file_path: str,
        language: Optional[str] = None
    ) -> WhisperResult:
        """Transcrire un fichier audio"""
        try:
            logger.info(f"🎤 Transcribing file: {file_path}")
            result = self.model.transcribe(
                file_path,
                language=language or self.language,
                verbose=False
            )
            return WhisperResult(
                text=result.get("text", "").strip(),
                language=result.get("language", "unknown"),
                confidence=0.95,
                duration_ms=0,
                segments=result.get("segments", [])
            )
        except Exception as e:
            logger.error(f"❌ File transcription error: {e}")
            return WhisperResult(
                text=f"Error: {str(e)}",
                language="unknown",
                confidence=0.0,
                duration_ms=0,
                segments=[]
            )

    def set_language(self, language: str):
        """Définir la langue pour les transcriptions futures"""
        self.language = language
        logger.info(f"🌍 Whisper language set to: {language}")


# Instance globale
_whisper_client: Optional[WhisperClient] = None


def get_whisper_client(model_size: str = "base") -> WhisperClient:
    """Obtenir instance singleton Whisper"""
    global _whisper_client
    if _whisper_client is None:
        _whisper_client = WhisperClient(model_size=model_size)
    return _whisper_client


def init_whisper(model_size: str = "base", language: Optional[str] = None):
    """Initialiser Whisper avec paramètres personnalisés"""
    global _whisper_client
    _whisper_client = WhisperClient(model_size=model_size, language=language)
