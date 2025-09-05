"""
Gestionnaire Redis sécurisé avec expiration automatique et gestion d'erreurs
"""
import asyncio
import json
import logging
import time
from typing import Any, Optional, Dict, List
import redis.asyncio as redis
from datetime import timedelta

from config.config import Config
from config.secrets import secrets_manager

logger = logging.getLogger(__name__)

class RedisManager:
    """Gestionnaire Redis avec expiration automatique et nettoyage mémoire"""
    
    def __init__(self, config: Config):
        self.config = config
        self.redis_client: Optional[redis.Redis] = None
        self.default_expiry = 3600  # 1 heure par défaut
        self.max_retries = 3
        self.retry_delay = 1.0
        
        # Configuration des expirations par type de données
        self.expiry_config = {
            'session': 1800,        # 30 minutes
            'cache': 3600,          # 1 heure  
            'temp': 300,            # 5 minutes
            'user_data': 86400,     # 24 heures
            'metrics': 604800,      # 7 jours
            'conversation': 86400,  # 24 heures
        }
    
    async def connect(self) -> None:
        """Connexion sécurisée à Redis"""
        try:
            redis_url = self.config.secure_redis_url
            
            # Configuration du client Redis
            self.redis_client = redis.from_url(
                redis_url,
                decode_responses=True,
                health_check_interval=30,
                socket_keepalive=True,
                socket_keepalive_options={},
                retry_on_timeout=True,
                max_connections=20
            )
            
            # Test de connexion
            await self.redis_client.ping()
            logger.info("✅ Redis connected successfully")
            
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Fermer proprement la connexion Redis"""
        if self.redis_client:
            try:
                await self.redis_client.close()
                logger.info("✅ Redis disconnected")
            except Exception as e:
                logger.error(f"Error disconnecting Redis: {e}")
    
    async def _execute_with_retry(self, operation_name: str, operation_func, *args, **kwargs):
        """Exécuter une opération Redis avec retry automatique"""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                if not self.redis_client:
                    raise ConnectionError("Redis client not connected")
                
                return await operation_func(*args, **kwargs)
                
            except (redis.ConnectionError, redis.TimeoutError) as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(f"Redis {operation_name} failed (attempt {attempt + 1}), retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    
                    # Reconnecter si nécessaire
                    try:
                        await self.connect()
                    except Exception as reconnect_error:
                        logger.error(f"Failed to reconnect to Redis: {reconnect_error}")
                else:
                    logger.error(f"Redis {operation_name} failed after {self.max_retries} attempts")
                    
            except Exception as e:
                logger.error(f"Redis {operation_name} error: {e}")
                last_error = e
                break
        
        raise last_error if last_error else Exception(f"Redis {operation_name} failed")
    
    def _get_expiry_time(self, data_type: str = 'cache') -> int:
        """Obtenir le temps d'expiration selon le type de données"""
        return self.expiry_config.get(data_type, self.default_expiry)
    
    def _generate_key(self, key: str, namespace: str = None) -> str:
        """Générer une clé Redis avec namespace"""
        if namespace:
            return f"jarvis:{namespace}:{key}"
        return f"jarvis:{key}"
    
    async def set(self, key: str, value: Any, data_type: str = 'cache', 
                  namespace: str = None, custom_expiry: Optional[int] = None) -> bool:
        """Stocker une valeur avec expiration automatique"""
        try:
            redis_key = self._generate_key(key, namespace)
            expiry = custom_expiry or self._get_expiry_time(data_type)
            
            # Sérialiser la valeur
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value, default=str)
            else:
                serialized_value = str(value)
            
            # Stocker avec expiration
            await self._execute_with_retry(
                "set", 
                self.redis_client.setex,
                redis_key, expiry, serialized_value
            )
            
            logger.debug(f"Redis SET: {redis_key} (expires in {expiry}s)")
            return True
            
        except Exception as e:
            logger.error(f"Redis SET failed for key {key}: {e}")
            return False
    
    async def get(self, key: str, namespace: str = None, default: Any = None) -> Any:
        """Récupérer une valeur"""
        try:
            redis_key = self._generate_key(key, namespace)
            
            value = await self._execute_with_retry(
                "get",
                self.redis_client.get,
                redis_key
            )
            
            if value is None:
                return default
            
            # Tentative de désérialisation JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
                
        except Exception as e:
            logger.error(f"Redis GET failed for key {key}: {e}")
            return default
    
    async def delete(self, key: str, namespace: str = None) -> bool:
        """Supprimer une clé"""
        try:
            redis_key = self._generate_key(key, namespace)
            
            result = await self._execute_with_retry(
                "delete",
                self.redis_client.delete,
                redis_key
            )
            
            logger.debug(f"Redis DELETE: {redis_key}")
            return result > 0
            
        except Exception as e:
            logger.error(f"Redis DELETE failed for key {key}: {e}")
            return False
    
    async def exists(self, key: str, namespace: str = None) -> bool:
        """Vérifier si une clé existe"""
        try:
            redis_key = self._generate_key(key, namespace)
            
            result = await self._execute_with_retry(
                "exists",
                self.redis_client.exists,
                redis_key
            )
            
            return result > 0
            
        except Exception as e:
            logger.error(f"Redis EXISTS failed for key {key}: {e}")
            return False
    
    async def extend_expiry(self, key: str, additional_time: int, namespace: str = None) -> bool:
        """Étendre la durée de vie d'une clé"""
        try:
            redis_key = self._generate_key(key, namespace)
            
            result = await self._execute_with_retry(
                "expire",
                self.redis_client.expire,
                redis_key, additional_time
            )
            
            logger.debug(f"Redis EXPIRE: {redis_key} extended by {additional_time}s")
            return result
            
        except Exception as e:
            logger.error(f"Redis EXPIRE failed for key {key}: {e}")
            return False
    
    async def get_ttl(self, key: str, namespace: str = None) -> int:
        """Obtenir le TTL d'une clé"""
        try:
            redis_key = self._generate_key(key, namespace)
            
            ttl = await self._execute_with_retry(
                "ttl",
                self.redis_client.ttl,
                redis_key
            )
            
            return ttl
            
        except Exception as e:
            logger.error(f"Redis TTL failed for key {key}: {e}")
            return -2  # Clé n'existe pas
    
    async def clear_namespace(self, namespace: str) -> int:
        """Supprimer toutes les clés d'un namespace"""
        try:
            pattern = f"jarvis:{namespace}:*"
            
            # Scanner les clés par batch pour éviter de bloquer Redis
            keys_deleted = 0
            async for key in self.redis_client.scan_iter(match=pattern, count=100):
                await self._execute_with_retry(
                    "delete",
                    self.redis_client.delete,
                    key
                )
                keys_deleted += 1
            
            logger.info(f"Redis cleared {keys_deleted} keys from namespace '{namespace}'")
            return keys_deleted
            
        except Exception as e:
            logger.error(f"Redis CLEAR_NAMESPACE failed for {namespace}: {e}")
            return 0
    
    async def health_check(self) -> Dict[str, Any]:
        """Vérifier la santé de Redis"""
        try:
            # Test ping
            start_time = time.time()
            pong = await self.redis_client.ping()
            ping_time = (time.time() - start_time) * 1000
            
            # Informations du serveur
            info = await self.redis_client.info()
            
            return {
                'status': 'healthy' if pong else 'error',
                'ping_ms': round(ping_time, 2),
                'connected_clients': info.get('connected_clients', 0),
                'used_memory_human': info.get('used_memory_human', 'unknown'),
                'redis_version': info.get('redis_version', 'unknown'),
                'uptime_in_seconds': info.get('uptime_in_seconds', 0)
            }
            
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'ping_ms': -1
            }
    
    async def cleanup_expired_keys(self) -> int:
        """Nettoyage manuel des clés expirées (optionnel)"""
        try:
            # Cette fonction est principalement pour le monitoring
            # Redis gère automatiquement l'expiration des clés
            info = await self.redis_client.info('keyspace')
            
            total_keys = 0
            for db_info in info.values():
                if isinstance(db_info, dict) and 'keys' in db_info:
                    total_keys += db_info['keys']
            
            logger.debug(f"Redis contains {total_keys} total keys")
            return total_keys
            
        except Exception as e:
            logger.error(f"Redis cleanup check failed: {e}")
            return 0

# Instance globale (sera initialisée par l'application)
redis_manager: Optional[RedisManager] = None

def get_redis_manager() -> RedisManager:
    """Obtenir l'instance du gestionnaire Redis"""
    global redis_manager
    if not redis_manager:
        from config.config import Config
        redis_manager = RedisManager(Config())
    return redis_manager