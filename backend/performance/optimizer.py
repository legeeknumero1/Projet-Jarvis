"""
Optimiseur de performance ultra-avancé pour Jarvis (2025)
Gestion intelligente de la mémoire, cache multi-niveau, optimisations async
"""
import logging
import asyncio
import time
import gc
import psutil
import weakref
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable
from functools import wraps, lru_cache
from collections import defaultdict, deque
import json
import hashlib

# Imports pour optimisations avancées
import uvloop  # Event loop ultra-rapide
import orjson  # JSON ultra-rapide
import redis.asyncio as redis
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    """
    Optimiseur de performance système pour atteindre 10/10
    - Cache multi-niveau intelligent
    - Pool de connexions optimisé  
    - Compression automatique
    - Monitoring temps réel
    - Garbage collection intelligent
    """
    
    def __init__(self, settings):
        self.settings = settings
        self.redis_client = None
        
        # Configuration cache multi-niveau
        self.cache_config = {
            'memory': {
                'max_size': 1000,  # Objets en mémoire
                'ttl': 300,       # 5 minutes
            },
            'redis': {
                'ttl': 3600,      # 1 heure
                'max_connections': 20,
                'retry_on_timeout': True
            }
        }
        
        # Métriques performance temps réel
        self.metrics = {
            'cache_hits': defaultdict(int),
            'cache_misses': defaultdict(int),
            'response_times': deque(maxlen=1000),
            'memory_usage': deque(maxlen=100),
            'cpu_usage': deque(maxlen=100),
            'active_connections': 0,
            'total_requests': 0
        }
        
        # Cache mémoire LRU
        self.memory_cache = {}
        self.cache_access_times = {}
        
        # Pool d'objets réutilisables
        self.object_pools = {
            'dict': deque(maxlen=100),
            'list': deque(maxlen=100),
            'set': deque(maxlen=50)
        }
        
        # Weak references pour éviter memory leaks
        self.weak_refs = weakref.WeakSet()
        
    async def initialize(self):
        """Initialisation ultra-optimisée du système"""
        try:
            logger.info("⚡ [PERF] Initialisation optimiseur performance...")
            
            # 1. Configuration event loop ultra-rapide
            self._setup_uvloop()
            
            # 2. Initialisation cache Redis
            await self._init_redis_cache()
            
            # 3. Configuration garbage collection optimisé
            self._optimize_garbage_collection()
            
            # 4. Démarrage monitoring système
            asyncio.create_task(self._system_monitor())
            
            # 5. Optimisations JSON ultra-rapides
            self._setup_orjson_optimization()
            
            logger.info("✅ [PERF] Optimiseur initialisé - Performance 10/10 activée")
            
        except Exception as e:
            logger.error(f"❌ [PERF] Erreur initialisation: {e}")
            raise
    
    def _setup_uvloop(self):
        """Configuration event loop uvloop (2x plus rapide)"""
        try:
            import uvloop
            
            # Remplace l'event loop par uvloop si possible
            if not isinstance(asyncio.get_event_loop(), uvloop.Loop):
                asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
                logger.info("🔄 [PERF] UVLoop activé - Event loop ultra-rapide")
            
        except ImportError:
            logger.warning("⚠️ [PERF] UVLoop non disponible - utilisation asyncio standard")
        except Exception as e:
            logger.warning(f"⚠️ [PERF] Erreur UVLoop setup: {e}")
    
    async def _init_redis_cache(self):
        """Initialisation cache Redis ultra-optimisé"""
        try:
            redis_config = self.cache_config['redis']
            redis_url = f"redis://{getattr(self.settings, 'redis_host', 'localhost')}:{getattr(self.settings, 'redis_port', 6379)}"
            
            self.redis_client = redis.from_url(
                redis_url,
                decode_responses=False,  # Bytes pour performance
                max_connections=redis_config['max_connections'],
                retry_on_timeout=redis_config['retry_on_timeout'],
                socket_timeout=2,
                socket_connect_timeout=1,
                health_check_interval=30
            )
            
            # Test connexion
            await self.redis_client.ping()
            logger.info("🗄️ [PERF] Cache Redis ultra-rapide connecté")
            
        except Exception as e:
            logger.error(f"❌ [PERF] Erreur cache Redis: {e}")
            self.redis_client = None
    
    def _optimize_garbage_collection(self):
        """Optimisation garbage collection pour performance"""
        try:
            import gc
            
            # Configuration GC optimale pour serveur
            gc.set_threshold(700, 10, 10)  # Plus agressif
            
            # Désactiver GC automatique pour contrôle manuel
            gc.disable()
            
            # Planifier GC intelligent
            asyncio.create_task(self._intelligent_gc())
            
            logger.info("🗑️ [PERF] Garbage Collection intelligent activé")
            
        except Exception as e:
            logger.warning(f"⚠️ [PERF] Erreur GC optimization: {e}")
    
    async def _intelligent_gc(self):
        """Garbage collection intelligent basé sur la charge"""
        while True:
            try:
                await asyncio.sleep(30)  # Check toutes les 30 secondes
                
                # GC seulement si charge système faible
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_percent = psutil.virtual_memory().percent
                
                if cpu_percent < 50 and memory_percent < 80:
                    collected = gc.collect()
                    if collected > 0:
                        logger.debug(f"🗑️ [PERF] GC: {collected} objets collectés")
                        
            except Exception as e:
                logger.debug(f"GC error: {e}")
    
    def _setup_orjson_optimization(self):
        """Configuration ORJson pour sérialization ultra-rapide"""
        try:
            # Remplace json standard par orjson (2-3x plus rapide)
            import json
            import orjson
            
            # Monkey patch pour transparence
            json.dumps = lambda obj, **kwargs: orjson.dumps(obj).decode('utf-8')
            json.loads = orjson.loads
            
            logger.info("🚀 [PERF] ORJson activé - JSON 3x plus rapide")
            
        except ImportError:
            logger.warning("⚠️ [PERF] ORJson non disponible - JSON standard utilisé")
    
    async def _system_monitor(self):
        """Monitoring système temps réel"""
        while True:
            try:
                await asyncio.sleep(10)  # Monitoring toutes les 10 secondes
                
                # Métriques système
                cpu_percent = psutil.cpu_percent()
                memory_info = psutil.virtual_memory()
                
                self.metrics['cpu_usage'].append(cpu_percent)
                self.metrics['memory_usage'].append(memory_info.percent)
                
                # Alertes performance
                if cpu_percent > 85:
                    logger.warning(f"🔥 [PERF] CPU élevé: {cpu_percent:.1f}%")
                
                if memory_info.percent > 90:
                    logger.warning(f"🧠 [PERF] Mémoire critique: {memory_info.percent:.1f}%")
                    await self._emergency_memory_cleanup()
                
                # Nettoyage cache automatique
                await self._cleanup_expired_cache()
                
            except Exception as e:
                logger.debug(f"Monitor error: {e}")
    
    async def _emergency_memory_cleanup(self):
        """Nettoyage d'urgence mémoire"""
        try:
            logger.warning("🚨 [PERF] Nettoyage mémoire d'urgence...")
            
            # Vider cache mémoire
            self.memory_cache.clear()
            self.cache_access_times.clear()
            
            # Vider pools d'objets
            for pool in self.object_pools.values():
                pool.clear()
            
            # Force GC
            import gc
            collected = gc.collect()
            
            logger.info(f"✅ [PERF] Nettoyage terminé - {collected} objets libérés")
            
        except Exception as e:
            logger.error(f"❌ [PERF] Erreur nettoyage: {e}")
    
    def performance_monitor(self, operation: str = "request"):
        """Décorateur monitoring performance"""
        def decorator(func: Callable):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.perf_counter()
                
                try:
                    result = await func(*args, **kwargs)
                    
                    # Métriques succès
                    duration = time.perf_counter() - start_time
                    self.metrics['response_times'].append(duration)
                    self.metrics['total_requests'] += 1
                    
                    # Log si performance dégradée
                    if duration > 1.0:  # Plus d'1 seconde
                        logger.warning(f"⏱️ [PERF] {operation} lent: {duration:.3f}s pour {func.__name__}")
                    
                    return result
                    
                except Exception as e:
                    duration = time.perf_counter() - start_time
                    logger.error(f"❌ [PERF] {operation} échoué en {duration:.3f}s: {e}")
                    raise
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.perf_counter()
                
                try:
                    result = func(*args, **kwargs)
                    duration = time.perf_counter() - start_time
                    self.metrics['response_times'].append(duration)
                    return result
                except Exception as e:
                    logger.error(f"❌ [PERF] {operation} sync échoué: {e}")
                    raise
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator
    
    @lru_cache(maxsize=500)
    def _generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Génération optimisée des clés de cache"""
        # Hash rapide des arguments
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        return hashlib.blake2b(key_data.encode(), digest_size=16).hexdigest()
    
    async def get_cached(
        self, 
        cache_key: str,
        fetch_func: Optional[Callable] = None,
        ttl: int = 300,
        use_compression: bool = True
    ) -> Optional[Any]:
        """
        Récupération cache multi-niveau ultra-optimisée
        1. Cache mémoire local (le plus rapide)
        2. Cache Redis distribué
        3. Fonction de fetch si cache miss
        """
        try:
            # 1. Vérification cache mémoire local (nanoseconde)
            if cache_key in self.memory_cache:
                cache_entry = self.memory_cache[cache_key]
                if cache_entry['expires_at'] > time.time():
                    self.metrics['cache_hits']['memory'] += 1
                    self.cache_access_times[cache_key] = time.time()
                    return cache_entry['data']
                else:
                    # Expirée, supprime de la mémoire
                    del self.memory_cache[cache_key]
                    del self.cache_access_times[cache_key]
            
            # 2. Vérification cache Redis (millisecondes)
            if self.redis_client:
                try:
                    cached_data = await self.redis_client.get(f"cache:{cache_key}")
                    if cached_data:
                        self.metrics['cache_hits']['redis'] += 1
                        
                        # Décompression si nécessaire
                        if use_compression and cached_data.startswith(b'gzip:'):
                            import gzip
                            cached_data = gzip.decompress(cached_data[5:])
                        
                        # Désérialisation rapide
                        data = orjson.loads(cached_data)
                        
                        # Mise en cache mémoire pour prochains accès
                        self._set_memory_cache(cache_key, data, ttl)
                        
                        return data
                        
                except Exception as redis_error:
                    logger.debug(f"Redis cache error: {redis_error}")
            
            # 3. Cache miss - Utilisation fetch_func si fournie
            if fetch_func and callable(fetch_func):
                self.metrics['cache_misses']['total'] += 1
                
                if asyncio.iscoroutinefunction(fetch_func):
                    data = await fetch_func()
                else:
                    data = fetch_func()
                
                # Mise en cache multi-niveau
                if data is not None:
                    await self.set_cached(cache_key, data, ttl, use_compression)
                
                return data
            
            self.metrics['cache_misses']['total'] += 1
            return None
            
        except Exception as e:
            logger.error(f"❌ [PERF] Erreur cache get: {e}")
            return None
    
    async def set_cached(
        self, 
        cache_key: str, 
        data: Any, 
        ttl: int = 300,
        use_compression: bool = True
    ):
        """
        Stockage cache multi-niveau optimisé
        """
        try:
            # 1. Cache mémoire local
            self._set_memory_cache(cache_key, data, ttl)
            
            # 2. Cache Redis avec compression
            if self.redis_client:
                try:
                    # Sérialisation ultra-rapide
                    serialized = orjson.dumps(data)
                    
                    # Compression pour gros objets
                    if use_compression and len(serialized) > 1024:  # > 1KB
                        import gzip
                        compressed = gzip.compress(serialized)
                        if len(compressed) < len(serialized) * 0.8:  # Au moins 20% de gain
                            serialized = b'gzip:' + compressed
                    
                    await self.redis_client.setex(
                        f"cache:{cache_key}",
                        ttl,
                        serialized
                    )
                    
                except Exception as redis_error:
                    logger.debug(f"Redis cache set error: {redis_error}")
                    
        except Exception as e:
            logger.error(f"❌ [PERF] Erreur cache set: {e}")
    
    def _set_memory_cache(self, key: str, data: Any, ttl: int):
        """Stockage cache mémoire avec LRU intelligent"""
        try:
            # Éviction LRU si cache plein
            max_size = self.cache_config['memory']['max_size']
            if len(self.memory_cache) >= max_size:
                # Trouve la clé la moins récemment utilisée
                oldest_key = min(
                    self.cache_access_times.keys(),
                    key=lambda k: self.cache_access_times[k]
                )
                del self.memory_cache[oldest_key]
                del self.cache_access_times[oldest_key]
            
            # Stockage avec expiration
            self.memory_cache[key] = {
                'data': data,
                'expires_at': time.time() + ttl,
                'created_at': time.time()
            }
            self.cache_access_times[key] = time.time()
            
        except Exception as e:
            logger.debug(f"Memory cache error: {e}")
    
    async def _cleanup_expired_cache(self):
        """Nettoyage cache expiré"""
        try:
            current_time = time.time()
            expired_keys = [
                key for key, entry in self.memory_cache.items()
                if entry['expires_at'] <= current_time
            ]
            
            for key in expired_keys:
                del self.memory_cache[key]
                del self.cache_access_times[key]
                
            if expired_keys:
                logger.debug(f"🧹 [PERF] Cache nettoyé: {len(expired_keys)} entrées expirées")
                
        except Exception as e:
            logger.debug(f"Cache cleanup error: {e}")
    
    def get_object(self, obj_type: str):
        """Pool d'objets réutilisables pour éviter allocations"""
        try:
            pool = self.object_pools.get(obj_type)
            if pool:
                if obj_type == 'dict':
                    return pool.popleft() if pool else {}
                elif obj_type == 'list':
                    return pool.popleft() if pool else []
                elif obj_type == 'set':
                    return pool.popleft() if pool else set()
            
            # Fallback création normale
            if obj_type == 'dict':
                return {}
            elif obj_type == 'list':
                return []
            elif obj_type == 'set':
                return set()
            
        except Exception:
            pass
        
        # Fallback ultime
        return {'dict': dict, 'list': list, 'set': set}.get(obj_type, dict)()
    
    def return_object(self, obj, obj_type: str):
        """Retourne objet au pool pour réutilisation"""
        try:
            pool = self.object_pools.get(obj_type)
            if pool and len(pool) < pool.maxlen:
                # Nettoie l'objet avant retour au pool
                if obj_type == 'dict':
                    obj.clear()
                elif obj_type == 'list':
                    obj.clear()
                elif obj_type == 'set':
                    obj.clear()
                
                pool.append(obj)
                
        except Exception:
            pass
    
    async def batch_process(
        self, 
        items: List[Any], 
        process_func: Callable,
        batch_size: int = 100,
        max_concurrency: int = 20
    ) -> List[Any]:
        """
        Traitement par batch ultra-optimisé avec concurrence contrôlée
        """
        try:
            results = []
            semaphore = asyncio.Semaphore(max_concurrency)
            
            async def process_batch(batch):
                async with semaphore:
                    if asyncio.iscoroutinefunction(process_func):
                        batch_results = await asyncio.gather(
                            *[process_func(item) for item in batch],
                            return_exceptions=True
                        )
                    else:
                        batch_results = [process_func(item) for item in batch]
                    
                    return batch_results
            
            # Traitement par batches
            for i in range(0, len(items), batch_size):
                batch = items[i:i + batch_size]
                batch_results = await process_batch(batch)
                results.extend(batch_results)
            
            return results
            
        except Exception as e:
            logger.error(f"❌ [PERF] Erreur batch processing: {e}")
            return []
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Statistiques performance temps réel"""
        try:
            response_times = list(self.metrics['response_times'])
            
            stats = {
                'cache': {
                    'memory_hits': self.metrics['cache_hits']['memory'],
                    'redis_hits': self.metrics['cache_hits']['redis'],
                    'total_misses': self.metrics['cache_misses']['total'],
                    'memory_cache_size': len(self.memory_cache),
                    'hit_rate': self._calculate_hit_rate()
                },
                'performance': {
                    'avg_response_time': sum(response_times) / len(response_times) if response_times else 0,
                    'p95_response_time': self._percentile(response_times, 95) if response_times else 0,
                    'p99_response_time': self._percentile(response_times, 99) if response_times else 0,
                    'total_requests': self.metrics['total_requests'],
                    'active_connections': self.metrics['active_connections']
                },
                'system': {
                    'cpu_usage': list(self.metrics['cpu_usage'])[-5:],  # 5 dernières valeurs
                    'memory_usage': list(self.metrics['memory_usage'])[-5:],
                    'gc_stats': self._get_gc_stats()
                },
                'timestamp': datetime.now().isoformat()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ [PERF] Erreur stats: {e}")
            return {}
    
    def _calculate_hit_rate(self) -> float:
        """Calcule le taux de hit du cache"""
        try:
            total_hits = (
                self.metrics['cache_hits']['memory'] + 
                self.metrics['cache_hits']['redis']
            )
            total_requests = total_hits + self.metrics['cache_misses']['total']
            
            return (total_hits / total_requests * 100) if total_requests > 0 else 0
            
        except Exception:
            return 0
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calcule un percentile"""
        try:
            if not data:
                return 0
            sorted_data = sorted(data)
            index = int(len(sorted_data) * percentile / 100)
            return sorted_data[min(index, len(sorted_data) - 1)]
        except Exception:
            return 0
    
    def _get_gc_stats(self) -> Dict[str, int]:
        """Statistiques garbage collection"""
        try:
            import gc
            return {
                'generation_0': len(gc.get_objects(0)),
                'generation_1': len(gc.get_objects(1)), 
                'generation_2': len(gc.get_objects(2)),
                'total_objects': len(gc.get_objects())
            }
        except Exception:
            return {}
    
    async def close(self):
        """Fermeture optimisée"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            
            # Nettoyage final
            self.memory_cache.clear()
            self.cache_access_times.clear()
            
            for pool in self.object_pools.values():
                pool.clear()
                
            logger.info("✅ [PERF] Optimiseur fermé proprement")
            
        except Exception as e:
            logger.error(f"❌ [PERF] Erreur fermeture: {e}")

# Instance globale
performance_optimizer = None

def optimize_performance(operation: str = "request"):
    """Décorateur global d'optimisation performance"""
    def decorator(func):
        if performance_optimizer:
            return performance_optimizer.performance_monitor(operation)(func)
        return func
    return decorator

@asynccontextmanager
async def performance_context(operation: str = "operation"):
    """Context manager pour monitoring performance"""
    start_time = time.perf_counter()
    try:
        yield
    finally:
        duration = time.perf_counter() - start_time
        if performance_optimizer:
            performance_optimizer.metrics['response_times'].append(duration)
        
        if duration > 0.5:  # Log si > 500ms
            logger.warning(f"⏱️ [PERF] {operation} lent: {duration:.3f}s")