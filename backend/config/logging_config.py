"""
Configuration centralisée des logs pour Jarvis
"""

import logging
import logging.handlers
import os
from datetime import datetime
from typing import Dict, Any

class JarvisLogger:
    """Gestionnaire de logs centralisé pour Jarvis"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        self.ensure_log_directory()
        self.loggers: Dict[str, logging.Logger] = {}
        self.setup_formatters()
    
    def ensure_log_directory(self):
        """Crée le dossier de logs s'il n'existe pas"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def setup_formatters(self):
        """Configure les formateurs de logs"""
        # Formateur détaillé avec emojis
        self.detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Formateur JSON pour parsing automatique
        self.json_formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "logger": "%(name)s", '
            '"level": "%(levelname)s", "message": "%(message)s", '
            '"module": "%(module)s", "function": "%(funcName)s", "line": %(lineno)d}',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Formateur simple pour console
        self.console_formatter = logging.Formatter(
            '%(levelname)s - %(name)s - %(message)s'
        )
    
    def get_logger(self, name: str, level: str = "INFO") -> logging.Logger:
        """Récupère ou crée un logger configuré"""
        if name in self.loggers:
            return self.loggers[name]
        
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level.upper()))
        
        # Éviter les doublons de handlers
        if not logger.handlers:
            self.setup_handlers(logger, name)
        
        self.loggers[name] = logger
        return logger
    
    def setup_handlers(self, logger: logging.Logger, name: str):
        """Configure les handlers pour un logger"""
        # Handler fichier principal avec rotation
        main_handler = logging.handlers.RotatingFileHandler(
            filename=os.path.join(self.log_dir, f"{name}.log"),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        main_handler.setFormatter(self.detailed_formatter)
        logger.addHandler(main_handler)
        
        # Handler fichier JSON pour parsing
        json_handler = logging.handlers.RotatingFileHandler(
            filename=os.path.join(self.log_dir, f"{name}_json.log"),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=3,
            encoding='utf-8'
        )
        json_handler.setFormatter(self.json_formatter)
        logger.addHandler(json_handler)
        
        # Handler console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self.console_formatter)
        logger.addHandler(console_handler)
        
        # Handler erreurs séparé
        error_handler = logging.handlers.RotatingFileHandler(
            filename=os.path.join(self.log_dir, "errors.log"),
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(self.detailed_formatter)
        logger.addHandler(error_handler)
    
    def setup_jarvis_loggers(self) -> Dict[str, logging.Logger]:
        """Configure tous les loggers nécessaires pour Jarvis"""
        components = [
            "jarvis.main",
            "jarvis.speech",
            "jarvis.memory",
            "jarvis.profile",
            "jarvis.database",
            "jarvis.ollama",
            "jarvis.home_assistant",
            "jarvis.websocket",
            "jarvis.api"
        ]
        
        loggers = {}
        for component in components:
            loggers[component] = self.get_logger(component)
        
        return loggers
    
    def log_system_info(self, logger: logging.Logger):
        """Log des informations système au démarrage"""
        logger.info("🚀 [SYSTEM] Démarrage du système de logs Jarvis")
        logger.info(f"📁 [SYSTEM] Dossier logs: {os.path.abspath(self.log_dir)}")
        logger.info(f"🕐 [SYSTEM] Timestamp: {datetime.now().isoformat()}")
        logger.info("📋 [SYSTEM] Rotation activée: 10MB max par fichier")

# Instance globale
jarvis_logger = JarvisLogger()

# Fonctions utilitaires
def get_jarvis_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Récupère un logger Jarvis configuré"""
    return jarvis_logger.get_logger(name, level)

def setup_all_loggers() -> Dict[str, logging.Logger]:
    """Configure tous les loggers Jarvis"""
    loggers = jarvis_logger.setup_jarvis_loggers()
    
    # Log info système
    main_logger = loggers["jarvis.main"]
    jarvis_logger.log_system_info(main_logger)
    
    return loggers

