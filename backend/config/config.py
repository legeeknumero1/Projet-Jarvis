import os
import secrets
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import ConfigDict, Field

class Config(BaseSettings):
    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    # Base configuration
    app_name: str = "Jarvis AI Assistant"
    debug: bool = False
    environment: str = "development"
    
    # Database - utilise variables d'environnement pour sécurité
    database_url: str = Field(alias="DATABASE_URL", default="postgresql+asyncpg://jarvis:jarvis@172.20.0.100:5432/jarvis_db")
    postgres_db: str = Field(alias="POSTGRES_DB", default="jarvis_db")
    postgres_user: str = Field(alias="POSTGRES_USER", default="jarvis")
    postgres_password: str = Field(alias="POSTGRES_PASSWORD", default="jarvis")
    
    # Redis
    redis_url: str = "redis://172.20.0.110:6379"
    
    # Ollama
    ollama_base_url: str = "http://172.20.0.30:11434"
    ollama_model: str = "llama3.2:1b"
    
    # Services API
    tts_api_url: str = "http://172.20.0.20:8002"
    stt_api_url: str = "http://172.20.0.10:8003"
    brain_api_url: str = "http://172.20.0.40:8000"
    interface_url: str = "http://172.20.0.50:3000"
    
    # WebSocket
    websocket_url: str = "ws://172.20.0.50:8001/ws"
    
    # Speech
    whisper_model: str = "base"
    piper_model: str = "fr_FR-upmc-medium"
    
    # Home Assistant
    home_assistant_url: str = "http://localhost:8123"
    home_assistant_token: Optional[str] = None
    
    # MQTT
    mqtt_broker: str = "localhost"
    mqtt_port: int = 1883
    mqtt_username: Optional[str] = None
    mqtt_password: Optional[str] = None
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/jarvis.log"
    
    # Memory
    memory_update_interval: str = "604800"
    memory_retention_days: str = "365"
    
    # Security
    secret_key: str = Field(default_factory=lambda: os.getenv("SECRET_KEY") or secrets.token_urlsafe(32))
    cors_origins: str = "http://localhost:3000,http://localhost:8000"
    
    # Paths
    models_path: str = "./models"
    tts_model_path: str = "./models/tts"
    stt_model_path: str = "./models/stt"
    logs_path: str = "./logs"
    data_path: str = "./data"