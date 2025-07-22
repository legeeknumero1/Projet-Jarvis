import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Config(BaseSettings):
    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    # Base configuration
    app_name: str = "Jarvis AI Assistant"
    debug: bool = False
    environment: str = "development"
    
    # Database
    database_url: str = "postgresql+asyncpg://jarvis:jarvis@localhost/jarvis_db"
    postgres_db: str = "jarvis_db"
    postgres_user: str = "jarvis"
    postgres_password: str = "jarvis"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Ollama
    ollama_base_url: str = "http://172.20.0.30:11434"
    ollama_model: str = "llama3.2:1b"
    
    # Services API
    tts_api_url: str = "http://localhost:8002"
    stt_api_url: str = "http://localhost:8003"
    brain_api_url: str = "http://localhost:8000"
    interface_url: str = "http://localhost:3000"
    
    # WebSocket
    websocket_url: str = "ws://localhost:8001/ws"
    
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
    secret_key: str = "your-secret-key-here"
    cors_origins: str = "http://localhost:3000,http://localhost:8000"
    
    # Paths
    models_path: str = "./models"
    tts_model_path: str = "./models/tts"
    stt_model_path: str = "./models/stt"
    logs_path: str = "./logs"
    data_path: str = "./data"