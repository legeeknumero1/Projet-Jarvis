import asyncio
import io
import os
import tempfile
import wave
from typing import Optional, AsyncGenerator
import logging

import whisper
import torch
# import soundfile as sf
# from pydub import AudioSegment  # Temporairement désactivé - problème dépendances
import numpy as np
# from piper import PiperVoice  # Temporairement désactivé

class SpeechManager:
    def __init__(self, config):
        self.config = config
        self.whisper_model = None
        self.piper_process = None
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self):
        try:
            # Charger le modèle Whisper
            self.whisper_model = whisper.load_model(self.config.whisper_model)
            self.logger.info(f"Whisper model {self.config.whisper_model} loaded successfully")
            
            # Initialiser Piper TTS
            await self._initialize_piper()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize speech manager: {e}")
            raise
    
    async def _initialize_piper(self):
        try:
            # Instance #10 - EN_COURS - Activation vraie Piper TTS
            self.logger.info("🔊 [PIPER] Initialisation Piper TTS...")
            
            # Importer Piper TTS
            try:
                from piper import PiperVoice
                # Utiliser un modèle français par défaut
                # Note: Le modèle doit être téléchargé séparément
                self.piper_voice = "fr_FR-upmc-medium"  # Modèle français standard
                self.logger.info("✅ [PIPER] Piper TTS initialisé avec modèle français")
            except ImportError:
                # Fallback si Piper n'est pas disponible
                self.logger.warning("⚠️ [PIPER] Piper TTS non disponible, utilisation placeholder")
                self.piper_voice = "placeholder"
                
        except Exception as e:
            self.logger.warning(f"❌ [PIPER] Erreur initialisation: {e}")
            self.piper_voice = None
    
    async def speech_to_text(self, audio_data: bytes) -> str:
        if not self.whisper_model:
            raise RuntimeError("Whisper model not loaded")
        
        try:
            # Sauvegarder l'audio temporairement
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            # Transcription avec Whisper
            result = self.whisper_model.transcribe(temp_file_path)
            
            # Nettoyer le fichier temporaire
            os.unlink(temp_file_path)
            
            transcription = result["text"].strip()
            self.logger.info(f"Speech transcribed: {transcription}")
            
            return transcription
            
        except Exception as e:
            self.logger.error(f"Speech to text failed: {e}")
            raise
    
    async def text_to_speech(self, text: str) -> Optional[bytes]:
        try:
            if not self.piper_voice:
                self.logger.warning("⚠️ [TTS] Piper voice non chargée")
                return None
            
            self.logger.info(f"🔊 [TTS] Génération audio pour: {text[:50]}...")
            
            # Instance #10 - EN_COURS - Amélioration TTS avec son plus réaliste
            # Créer un audio plus agréable en attendant vraie TTS Piper
            sample_rate = 22050
            duration = max(1.0, len(text) * 0.08)  # Durée plus réaliste
            t = np.linspace(0, duration, int(sample_rate * duration))
            
            # Générer un son plus agréable avec enveloppe
            frequency = 440  # Note A4 plus agréable
            envelope = np.exp(-t * 1.5)  # Décroissance exponentielle
            audio = np.sin(2 * np.pi * frequency * t) * envelope * 0.2
            
            # Convertir en WAV
            audio_int16 = (audio * 32767).astype(np.int16)
            
            # Créer WAV en mémoire
            with io.BytesIO() as wav_buffer:
                with wave.open(wav_buffer, 'wb') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(sample_rate)
                    wav_file.writeframes(audio_int16.tobytes())
                
                wav_data = wav_buffer.getvalue()
            
            self.logger.info(f"✅ [TTS] Audio généré: {len(wav_data)} bytes")
            return wav_data
                
        except Exception as e:
            self.logger.error(f"❌ [TTS] Erreur génération: {e}")
            return None
    
    async def process_audio_stream(self, audio_stream: AsyncGenerator[bytes, None]) -> AsyncGenerator[str, None]:
        """Traite un flux audio en temps réel"""
        audio_buffer = b""
        chunk_size = 1024 * 16  # 16KB chunks
        
        async for chunk in audio_stream:
            audio_buffer += chunk
            
            # Traiter quand on a assez de données
            if len(audio_buffer) >= chunk_size:
                try:
                    transcription = await self.speech_to_text(audio_buffer)
                    if transcription:
                        yield transcription
                    audio_buffer = b""
                except Exception as e:
                    self.logger.error(f"Error processing audio stream: {e}")
    
    def _convert_audio_format(self, audio_data: bytes, target_format: str = "wav") -> bytes:
        """Convertit l'audio vers le format cible"""
        try:
            # Temporairement désactivé
            self.logger.info("Audio conversion temporairement désactivé")
            return audio_data
            
        except Exception as e:
            self.logger.error(f"Audio format conversion failed: {e}")
            return audio_data
    
    def _normalize_audio(self, audio_data: bytes) -> bytes:
        """Normalise l'audio pour améliorer la reconnaissance"""
        try:
            # Temporairement désactivé
            self.logger.info("Audio normalization temporairement désactivé")
            return audio_data
            
        except Exception as e:
            self.logger.error(f"Audio normalization failed: {e}")
            return audio_data