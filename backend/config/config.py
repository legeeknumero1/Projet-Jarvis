import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import ConfigDict, Field, validator
from .secrets import secrets_manager

class Config(BaseSettings):
    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    # Base configuration
    app_name: str = "Jarvis AI Assistant"
    debug: bool = Field(default=False, alias="DEBUG")
    environment: str = Field(default="production", alias="ENVIRONMENT")
    
    # Database - Sécurisé via gestionnaire de secrets
    database_url: Optional[str] = Field(default=None, alias="DATABASE_URL")
    postgres_db: str = Field(default="jarvis_db", alias="POSTGRES_DB")
    postgres_user: str = Field(default="jarvis", alias="POSTGRES_USER")
    postgres_password: Optional[str] = Field(default=None, alias="POSTGRES_PASSWORD")
    
    # Redis - Sécurisé via gestionnaire de secrets
    redis_url: Optional[str] = Field(default=None, alias="REDIS_URL")
    
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
    
    # Security - Sécurisé via gestionnaire de secrets
    secret_key: Optional[str] = Field(default=None, alias="JARVIS_SECRET_KEY") 
    cors_origins: str = Field(default="http://localhost:3000", alias="CORS_ORIGINS")
    
    # Configuration sécurisée
    @property
    def secure_database_url(self) -> str:
        """URL de base de données sécurisée"""
        if self.database_url:
            return self.database_url
        return secrets_manager.get_database_url()
    
    @property 
    def secure_redis_url(self) -> str:
        """URL Redis sécurisée"""
        if self.redis_url:
            return self.redis_url
        return secrets_manager.get_redis_url()
    
    @property
    def secure_secret_key(self) -> str:
        """Clé secrète sécurisée"""
        if self.secret_key:
            return self.secret_key
        return secrets_manager.get_secret("JARVIS_SECRET_KEY")
    
    @property
    def secure_cors_origins(self) -> List[str]:
        """Origines CORS sécurisées"""
        return secrets_manager.validate_cors_origins(self.cors_origins)
    
    # Paths - via variables d'environnement
    models_path: str = Field(default="./models")
    tts_model_path: str = Field(alias="TTS_MODEL_PATH")
    stt_model_path: str = Field(alias="STT_MODEL_PATH")
    logs_path: str = Field(alias="LOGS_PATH")
    data_path: str = Field(alias="DATA_PATH")