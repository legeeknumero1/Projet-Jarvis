"""Configuration logging structuré avec emojis"""
import logging
import sys
from pathlib import Path
from typing import Optional

def configure_logging(settings) -> None:
    """Configure le système de logging"""
    
    # Format avec emojis (comme dans l'actuel)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Handler console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Handler fichier (si spécifié)
    handlers = [console_handler]
    if settings.log_file:
        try:
            log_path = Path(settings.log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_path)
            file_handler.setFormatter(formatter)
            handlers.append(file_handler)
        except Exception as e:
            logging.warning(f"⚠️ [LOG] Cannot create log file {settings.log_file}: {e}")
    
    # Configuration root logger
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        handlers=handlers,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    
    # Réduire verbosité des libs externes
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING) 
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    logging.info("🔧 [LOG] Logging configuré")

def get_logger(name: str) -> logging.Logger:
    """Helper pour créer des loggers nommés"""
    return logging.getLogger(name)