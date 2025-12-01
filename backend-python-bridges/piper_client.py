"""
Client Piper TTS - Phase 3 Python Bridges
Text-to-Speech avec Piper local (français haute qualité)
"""

import subprocess
import numpy as np
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from loguru import logger
import os
import json


@dataclass
class PiperResult:
    """Résultat de synthèse Piper"""
    audio_samples: np.ndarray  # Array float32
    sample_rate: int
    duration_ms: float
    voice: str


class PiperClient:
    """Client Piper TTS local"""

    # Voix disponibles (français)
    FRENCH_VOICES = {
        "fr_FR-upmc-medium": "Français UPMC (femme) - Recommandé",
        "fr_FR-siwis-medium": "Français Siwis (femme)",
        "fr_FR-tom-medium": "Français Tom (homme)"
    }

    def __init__(
        self,
        voice: str = "fr_FR-upmc-medium",
        piper_binary: str = "piper"
    ):
        """
        Initialiser le client Piper

        Args:
            voice: Voix à utiliser
            piper_binary: Chemin vers l'exécutable Piper
        """
        self.voice = voice
        self.piper_binary = os.getenv("PIPER_BINARY", piper_binary)
        self.sample_rate = 22050

        logger.info(f" Piper Client initialized: {voice}")
        self.check_available_voices()

    def check_available_voices(self) -> List[str]:
        """Vérifier les voix disponibles"""
        try:
            result = subprocess.run(
                [self.piper_binary, "--help"],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info(" Piper TTS available")
                return list(self.FRENCH_VOICES.keys())
            else:
                logger.error(" Piper TTS not found")
                return []
        except Exception as e:
            logger.error(f" Error checking Piper: {e}")
            return []

    def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        speed: float = 1.0
    ) -> PiperResult:
        """
        Synthétiser texte en audio

        Args:
            text: Texte à synthétiser
            voice: Voix (optionnel, utilise la voix par défaut)
            speed: Vitesse de parole (0.5-2.0)

        Returns:
            PiperResult avec samples audio et métadonnées
        """
        selected_voice = voice or self.voice

        # SECURITY FIX: Validate voice against whitelist (defense in depth)
        if selected_voice not in self.FRENCH_VOICES:
            raise ValueError(f"Invalid voice: {selected_voice}. Allowed voices: {list(self.FRENCH_VOICES.keys())}")

        # Validate input text length
        if not text or len(text) > 5000:
            raise ValueError("Text must be between 1 and 5000 characters")

        # Validate speed
        if not (0.5 <= speed <= 2.0):
            raise ValueError("Speed must be between 0.5 and 2.0")

        try:
            import time
            start_time = time.time()

            logger.debug(f" Synthesizing: {text[:50]}...")

            # Créer fichier temporaire pour sortie audio
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp_path = tmp.name

            try:
                # Exécuter Piper (subprocess.Popen with list prevents shell injection)
                cmd = [
                    self.piper_binary,
                    "--model", selected_voice,
                    "--output-file", tmp_path,
                    "--length-scale", str(1.0 / speed)  # Inverse pour vitesse
                ]

                process = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )

                stdout, stderr = process.communicate(input=text.encode())

                if process.returncode != 0:
                    logger.error(f" Piper error: {stderr.decode()}")
                    return PiperResult(
                        audio_samples=np.array([], dtype=np.float32),
                        sample_rate=22050,
                        duration_ms=0,
                        voice=selected_voice
                    )

                # Charger fichier audio généré
                try:
                    import soundfile as sf
                    audio, sr = sf.read(tmp_path, dtype='float32')
                except ImportError:
                    # Fallback sans soundfile
                    logger.warning(" soundfile not available, using placeholder")
                    audio = np.zeros(22050, dtype=np.float32)
                    sr = 22050

                duration_ms = (time.time() - start_time) * 1000

                logger.info(f" Synthesis done in {duration_ms:.0f}ms: {len(audio) / sr:.1f}s audio")

                return PiperResult(
                    audio_samples=audio,
                    sample_rate=sr,
                    duration_ms=duration_ms,
                    voice=selected_voice
                )

            finally:
                # Nettoyer fichier temporaire
                try:
                    os.unlink(tmp_path)
                except:
                    pass

        except subprocess.TimeoutExpired:
            logger.error(" Piper synthesis timeout")
            return PiperResult(
                audio_samples=np.array([], dtype=np.float32),
                sample_rate=22050,
                duration_ms=0,
                voice=selected_voice
            )
        except Exception as e:
            logger.error(f" Synthesis error: {e}")
            return PiperResult(
                audio_samples=np.array([], dtype=np.float32),
                sample_rate=22050,
                duration_ms=0,
                voice=selected_voice
            )

    def set_voice(self, voice: str):
        """Changer la voix"""
        if voice in self.FRENCH_VOICES:
            self.voice = voice
            logger.info(f" Piper voice changed to: {voice}")
        else:
            logger.warning(f" Unknown voice: {voice}")

    def list_voices(self) -> Dict[str, str]:
        """Lister les voix disponibles"""
        return self.FRENCH_VOICES


# Instance globale
_piper_client: Optional[PiperClient] = None


def get_piper_client(voice: str = "fr_FR-upmc-medium") -> PiperClient:
    """Obtenir instance singleton Piper"""
    global _piper_client
    if _piper_client is None:
        _piper_client = PiperClient(voice=voice)
    return _piper_client


def init_piper(voice: str = "fr_FR-upmc-medium"):
    """Initialiser Piper avec paramètres personnalisés"""
    global _piper_client
    _piper_client = PiperClient(voice=voice)
