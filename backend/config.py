"""Configuration centralisée avec Pydantic Settings"""
import json
import os
from typing import List, Optional

from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    """Configuration principale de Jarvis"""
    
    # API Configuration
    api_key: str = Field(default="jarvis-dev-key", env="JARVIS_API_KEY")
    brave_api_key: Optional[str] = Field(default=None, env="BRAVE_API_KEY")
    brave_api_key_backup: Optional[str] = Field(default=None, env="BRAVE_API_KEY_BACKUP")
    google_cse_key: Optional[str] = Field(default=None, env="GOOGLE_CSE_KEY")
    google_cse_id: Optional[str] = Field(default=None, env="GOOGLE_CSE_ID")
    openweather_api_key: Optional[str] = Field(default=None, env="OPENWEATHER_API_KEY")
    
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
    db_host: str = Field(default="172.20.0.100", env="POSTGRES_HOST")
    db_port: int = Field(default=5432, env="POSTGRES_PORT")
    db_user: str = Field(default="jarvis", env="POSTGRES_USER")
    db_password: str = Field(default="jarvis", env="POSTGRES_PASSWORD")
    db_name: str = Field(default="jarvis_db", env="POSTGRES_DB")
    
    # Redis
    redis_host: str = Field(default="172.20.0.110", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    
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
    
    # Security
    jwt_secret_key: Optional[str] = Field(default=None, env="JWT_SECRET_KEY")
    encryption_key: Optional[str] = Field(default=None, env="JARVIS_ENCRYPTION_KEY")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Support Docker secrets en production
        self._load_from_secrets()
        self._normalize_allowed_origins()
        self._fallback_brave_api_key()
    
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
                self.db_password = db_password

    def _normalize_allowed_origins(self) -> None:
        """Convertit ALLOWED_ORIGINS en liste si fourni en chaîne"""
        if isinstance(self.allowed_origins, str):
            try:
                self.allowed_origins = json.loads(self.allowed_origins)
            except json.JSONDecodeError:
                self.allowed_origins = [
                    origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()
                ]

    def _fallback_brave_api_key(self) -> None:
        """Permet d'utiliser une clé Brave secondaire si la primaire est absente"""
        if not self.brave_api_key and self.brave_api_key_backup:
            self.brave_api_key = self.brave_api_key_backup

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
