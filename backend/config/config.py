import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import ConfigDict, Field

class Config(BaseSettings):
    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    # Base configuration
    app_name: str = "Jarvis AI Assistant"
    debug: bool = Field(default=False, alias="DEBUG")
    environment: str = Field(default="production", alias="ENVIRONMENT")
    
    # Database - TOUT via variables d'environnement
    database_url: str = Field(alias="DATABASE_URL")
    postgres_db: str = Field(alias="POSTGRES_DB")
    postgres_user: str = Field(alias="POSTGRES_USER")
    postgres_password: str = Field(alias="POSTGRES_PASSWORD")
    
    # Redis
    redis_url: str = Field(alias="REDIS_URL")
    
    # Ollama
    ollama_base_url: str = Field(alias="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="llama3.2:1b", alias="OLLAMA_MODEL")
    
    # Services API - TOUT via variables d'environnement
    tts_api_url: str = Field(alias="TTS_API_URL")
    stt_api_url: str = Field(alias="STT_API_URL")
    backend_api_url: str = Field(alias="BACKEND_API_URL")
    interface_url: str = Field(alias="INTERFACE_URL")
    
    # WebSocket
    websocket_url: str = Field(alias="WEBSOCKET_URL")
    
    # Speech
    whisper_model: str = Field(default="base", alias="WHISPER_MODEL")
    piper_model: str = Field(default="fr_FR-upmc-medium", alias="PIPER_MODEL")
    
    # Home Assistant
    home_assistant_url: str = Field(alias="HOME_ASSISTANT_URL")
    home_assistant_token: Optional[str] = Field(default=None, alias="HOME_ASSISTANT_TOKEN")
    
    # MQTT
    mqtt_broker: str = Field(alias="MQTT_BROKER")
    mqtt_port: int = Field(default=1883, alias="MQTT_PORT")
    mqtt_username: Optional[str] = Field(default=None, alias="MQTT_USERNAME")
    mqtt_password: Optional[str] = Field(default=None, alias="MQTT_PASSWORD")
    
    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_file: str = Field(default="logs/jarvis.log")
    
    # Memory
    memory_update_interval: str = Field(alias="MEMORY_UPDATE_INTERVAL")
    memory_retention_days: str = Field(alias="MEMORY_RETENTION_DAYS")
    
    # Security
    secret_key: str = Field(alias="JARVIS_SECRET_KEY")
    cors_origins: str = Field(alias="CORS_ORIGINS")
    
    # Paths - via variables d'environnement
    models_path: str = Field(default="./models")
    tts_model_path: str = Field(alias="TTS_MODEL_PATH")
    stt_model_path: str = Field(alias="STT_MODEL_PATH")
    logs_path: str = Field(alias="LOGS_PATH")
    data_path: str = Field(alias="DATA_PATH")