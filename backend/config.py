"""Configuration centralisée avec Pydantic Settings"""
from pydantic import BaseSettings, Field
from typing import List, Optional
import os

class Settings(BaseSettings):
    """Configuration principale de Jarvis"""
    
    # API Configuration
    api_key: str = Field(default="jarvis-dev-key", env="JARVIS_API_KEY")
    
    allowed_origins: List[str] = Field(default=[
        "http://localhost:3000",
        "http://localhost:8001", 
        "http://172.20.0.50:3000"
    ], env="ALLOWED_ORIGINS")
    
    # Database
    database_url: str = Field(
        default="postgresql://jarvis:jarvis@172.20.0.100:5432/jarvis_db",
        env="DATABASE_URL"
    )
    
    # Services URLs
    ollama_base_url: str = Field(default="http://172.20.0.30:11434", env="OLLAMA_URL")
    stt_api_url: str = Field(default="http://172.20.0.10:8003", env="STT_API_URL")
    tts_api_url: str = Field(default="http://172.20.0.20:8002", env="TTS_API_URL")
    
    # Home Assistant
    ha_url: Optional[str] = Field(default=None, env="HOME_ASSISTANT_URL")
    ha_token: Optional[str] = Field(default=None, env="HOME_ASSISTANT_TOKEN")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="/app/logs/jarvis.log", env="LOG_FILE")
    
    # Features
    use_local_audio: bool = Field(default=False, env="USE_LOCAL_AUDIO")
    fallback_rest: bool = Field(default=True, env="FALLBACK_REST")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Support Docker secrets en production
        self._load_from_secrets()
    
    def _load_from_secrets(self):
        """Charge les secrets depuis /run/secrets/ (Docker swarm/compose)"""
        secrets_dir = "/run/secrets"
        if not os.path.exists(secrets_dir):
            return
        
        # API Key depuis Docker secret
        api_key_file = os.path.join(secrets_dir, "api_key")
        if os.path.exists(api_key_file):
            with open(api_key_file, "r") as f:
                self.api_key = f.read().strip()
        
        # Password DB depuis secret
        db_password_file = os.path.join(secrets_dir, "db_password")
        if os.path.exists(db_password_file):
            with open(db_password_file, "r") as f:
                db_password = f.read().strip()
                # Reconstruire database_url avec nouveau password
                if "jarvis:jarvis@" in self.database_url:
                    self.database_url = self.database_url.replace(
                        "jarvis:jarvis@", 
                        f"jarvis:{db_password}@"
                    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"