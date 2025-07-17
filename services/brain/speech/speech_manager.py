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
# from pydub import AudioSegment
import numpy as np
# from piper import PiperVoice

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
            # Temporairement désactivé
            self.piper_voice = None
            self.logger.info("Piper TTS temporairement désactivé")
                
        except Exception as e:
            self.logger.warning(f"Failed to initialize Piper: {e}")
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
                self.logger.warning("Piper voice not loaded")
                return None
            
            # Temporairement désactivé
            self.logger.info(f"TTS demandé pour: {text[:50]}... (désactivé)")
            return None
                
        except Exception as e:
            self.logger.error(f"Text to speech failed: {e}")
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