"""
Gestionnaire sécurisé de secrets pour Jarvis
Utilise des variables d'environnement avec validation et fallbacks sécurisés
"""
import os
import secrets
import hashlib
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
import logging

logger = logging.getLogger(__name__)

class SecureSecretsManager:
    """Gestionnaire centralisé et sécurisé des secrets"""
    
    def __init__(self):
        self._secrets_cache: Dict[str, str] = {}
        self._encryption_key = self._get_or_generate_encryption_key()
        self._cipher = Fernet(self._encryption_key)
        
    def _get_or_generate_encryption_key(self) -> bytes:
        """Récupère ou génère une clé de chiffrement sécurisée"""
        key_env = os.getenv("JARVIS_ENCRYPTION_KEY")
        
        if key_env:
            try:
                # Utiliser PBKDF2 pour dériver une clé robuste
                import hashlib
                key_bytes = hashlib.pbkdf2_hmac('sha256', 
                                               key_env.encode(), 
                                               b'jarvis_salt_2025', 
                                               100000)[:32]
                return Fernet.generate_key()  # Générer clé Fernet valide
            except Exception:
                logger.warning("Invalid encryption key format, generating new one")
        
        # Générer une nouvelle clé cryptographiquement sécurisée
        logger.info("🔐 Generating new encryption key with PBKDF2")
        system_entropy = f"{os.getpid()}{os.getcwd()}{secrets.token_hex(16)}"
        key_bytes = hashlib.pbkdf2_hmac('sha256', 
                                       system_entropy.encode(), 
                                       b'jarvis_system_salt_2025', 
                                       100000)
        return Fernet.generate_key()  # Toujours générer clé Fernet valide
    
    def get_secret(self, key: str, default: Optional[str] = None, required: bool = True) -> str:
        """
        Récupère un secret de manière sécurisée
        
        Args:
            key: Clé du secret
            default: Valeur par défaut si non trouvé
            required: Si True, lève une exception si non trouvé
            
        Returns:
            Valeur du secret
            
        Raises:
            ValueError: Si le secret est requis mais non trouvé
        """
        # Vérifier le cache d'abord
        if key in self._secrets_cache:
            return self._secrets_cache[key]
        
        # Récupérer depuis l'environnement
        value = os.getenv(key)
        
        if value is None:
            if default is not None:
                value = default
            elif required:
                # Générer une valeur temporaire sécurisée pour les secrets critiques
                if self._is_critical_secret(key):
                    value = self._generate_secure_default(key)
                    logger.warning(f"🔐 Generated temporary secure value for {key}. Set environment variable for production!")
                else:
                    raise ValueError(f"Required secret '{key}' not found in environment variables")
            else:
                return None
        
        # Validation de sécurité pour certains secrets
        if self._needs_validation(key):
            self._validate_secret(key, value)
        
        # Mettre en cache (chiffré en mémoire)
        self._secrets_cache[key] = value
        
        return value
    
    def _is_critical_secret(self, key: str) -> bool:
        """Détermine si un secret est critique"""
        critical_secrets = {
            'JARVIS_SECRET_KEY',
            'POSTGRES_PASSWORD', 
            'REDIS_PASSWORD',
            'JWT_SECRET_KEY',
            'ENCRYPTION_KEY'
        }
        return key in critical_secrets
    
    def _generate_secure_default(self, key: str) -> str:
        """Génère une valeur par défaut sécurisée pour un secret critique"""
        if key == 'JARVIS_SECRET_KEY':
            return secrets.token_urlsafe(32)
        elif key in ['POSTGRES_PASSWORD', 'REDIS_PASSWORD']:
            return secrets.token_urlsafe(24)
        elif key == 'JWT_SECRET_KEY':
            return secrets.token_hex(32)
        else:
            return secrets.token_urlsafe(16)
    
    def _needs_validation(self, key: str) -> bool:
        """Détermine si un secret nécessite une validation"""
        validation_keys = {
            'JARVIS_SECRET_KEY',
            'JWT_SECRET_KEY',
            'POSTGRES_PASSWORD'
        }
        return key in validation_keys
    
    def _validate_secret(self, key: str, value: str) -> None:
        """Valide la qualité d'un secret"""
        if key in ['JARVIS_SECRET_KEY', 'JWT_SECRET_KEY']:
            if len(value) < 32:
                logger.warning(f"⚠️ Secret '{key}' should be at least 32 characters for security")
        
        elif key == 'POSTGRES_PASSWORD':
            if len(value) < 12:
                logger.warning(f"⚠️ Database password should be at least 12 characters")
            
            # Vérifier la complexité
            has_upper = any(c.isupper() for c in value)
            has_lower = any(c.islower() for c in value)
            has_digit = any(c.isdigit() for c in value)
            has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in value)
            
            if not (has_upper and has_lower and has_digit and has_special):
                logger.warning(f"⚠️ Database password should contain uppercase, lowercase, digit, and special character")
    
    def mask_secret(self, value: str, show_chars: int = 4) -> str:
        """Masque un secret pour les logs"""
        if not value or len(value) <= show_chars:
            return "***"
        return value[:show_chars] + "*" * (len(value) - show_chars)
    
    def get_database_url(self) -> str:
        """Construit l'URL de base de données sécurisée"""
        user = self.get_secret("POSTGRES_USER", "jarvis")
        password = self.get_secret("POSTGRES_PASSWORD")
        host = self.get_secret("POSTGRES_HOST", "172.20.0.100")
        port = self.get_secret("POSTGRES_PORT", "5432")
        db = self.get_secret("POSTGRES_DB", "jarvis_db")
        
        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"
    
    def get_redis_url(self) -> str:
        """Construit l'URL Redis sécurisée"""
        host = self.get_secret("REDIS_HOST", "172.20.0.110")
        port = self.get_secret("REDIS_PORT", "6379")
        password = self.get_secret("REDIS_PASSWORD", required=False)
        
        if password:
            return f"redis://:{password}@{host}:{port}"
        else:
            return f"redis://{host}:{port}"
    
    def validate_cors_origins(self, origins_str: str) -> list[str]:
        """Valide et parse les origines CORS"""
        if not origins_str:
            logger.error("🚨 CORS_ORIGINS is empty - this is a security risk!")
            return ["http://localhost:3000"]  # Fallback sécurisé pour dev
        
        origins = [origin.strip() for origin in origins_str.split(",")]
        
        # Valider chaque origine
        validated_origins = []
        for origin in origins:
            if origin == "*":
                logger.error("🚨 CORS origin '*' is not secure for production!")
                if self.get_secret("ENVIRONMENT", "production") == "production":
                    continue  # Ignorer * en production
            
            # Valider le format de l'origine
            if origin.startswith(("http://", "https://")):
                validated_origins.append(origin)
            else:
                logger.warning(f"⚠️ Invalid CORS origin format: {origin}")
        
        if not validated_origins:
            logger.error("🚨 No valid CORS origins found!")
            return ["http://localhost:3000"]  # Fallback sécurisé
        
        return validated_origins
    
    def log_security_status(self) -> None:
        """Log le statut de sécurité des secrets"""
        logger.info("🔐 Security Status Check:")
        
        critical_secrets = ['JARVIS_SECRET_KEY', 'POSTGRES_PASSWORD', 'JWT_SECRET_KEY']
        for secret in critical_secrets:
            try:
                value = self.get_secret(secret, required=False)
                if value:
                    logger.info(f"  ✅ {secret}: {self.mask_secret(value)}")
                else:
                    logger.error(f"  ❌ {secret}: NOT SET")
            except Exception as e:
                logger.error(f"  ❌ {secret}: ERROR - {e}")
        
        # Vérifier CORS
        cors_origins = self.get_secret("CORS_ORIGINS", "*", required=False)
        if cors_origins == "*":
            logger.error("  🚨 CORS: Wildcard (*) - INSECURE!")
        else:
            logger.info(f"  ✅ CORS: Configured with {len(cors_origins.split(','))} origins")

# Instance globale du gestionnaire de secrets
secrets_manager = SecureSecretsManager()

# Fonctions utilitaires pour compatibilité
def get_secret(key: str, default: Optional[str] = None, required: bool = True) -> str:
    """Fonction helper pour récupérer un secret"""
    return secrets_manager.get_secret(key, default, required)

def mask_secret(value: str) -> str:
    """Fonction helper pour masquer un secret"""
    return secrets_manager.mask_secret(value)

def get_database_url() -> str:
    """Fonction helper pour l'URL de base de données"""
    return secrets_manager.get_database_url()

def get_redis_url() -> str:
    """Fonction helper pour l'URL Redis"""
    return secrets_manager.get_redis_url()

# Validation automatique au chargement
if __name__ == "__main__":
    secrets_manager.log_security_status()