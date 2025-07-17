import os
from typing import Optional
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    # Base configuration
    app_name: str = "Jarvis AI Assistant"
    debug: bool = False
    
    # Database
    database_url: str = "postgresql+asyncpg://jarvis:jarvis@localhost/jarvis_db"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3:70b"
    
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
    
    # Security
    secret_key: str = "your-secret-key-here"
    
    # Paths
    models_path: str = "./models"
    logs_path: str = "./logs"
    data_path: str = "./data"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"