"""
Système de monitoring des requêtes lentes PostgreSQL
Conforme aux standards de performance 2025
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json
import statistics
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine.events import event
from sqlalchemy.engine import Engine
from sqlalchemy import text
import asyncpg
from prometheus_client import Counter, Histogram, Gauge
import psutil

# Métriques Prometheus pour le monitoring
QUERY_DURATION = Histogram('jarvis_db_query_duration_seconds', 'Query execution time', ['query_type', 'table', 'operation'])
SLOW_QUERIES_TOTAL = Counter('jarvis_db_slow_queries_total', 'Total number of slow queries', ['query_type', 'table'])
ACTIVE_CONNECTIONS = Gauge('jarvis_db_active_connections', 'Number of active database connections')
DB_POOL_SIZE = Gauge('jarvis_db_pool_size', 'Current database pool size')
DB_POOL_CHECKED_OUT = Gauge('jarvis_db_pool_checked_out', 'Checked out connections from pool')

@dataclass
class QueryMetrics:
    """Métriques d'une requête"""
    query: str
    duration: float
    timestamp: datetime
    user_id: Optional[str] = None
    table: Optional[str] = None
    operation: Optional[str] = None
    rows_affected: Optional[int] = None
    explain_plan: Optional[Dict] = None
    stack_trace: Optional[str] = None
    
    def __post_init__(self):
        """Analyser automatiquement la requête après création"""
        if not self.table or not self.operation:
            parsed = QueryAnalyzer.parse_query(self.query)
            self.table = self.table or parsed.get('table', 'unknown')
            self.operation = self.operation or parsed.get('operation', 'unknown')

@dataclass
class QueryStats:
    """Statistiques agrégées pour un type de requête"""
    total_count: int = 0
    slow_count: int = 0
    total_duration: float = 0.0
    min_duration: float = float('inf')
    max_duration: float = 0.0
    durations: deque = field(default_factory=lambda: deque(maxlen=1000))
    
    def add_measurement(self, duration: float, is_slow: bool = False):
        """Ajouter une mesure"""
        self.total_count += 1
        self.total_duration += duration
        self.durations.append(duration)
        
        if is_slow:
            self.slow_count += 1
            
        self.min_duration = min(self.min_duration, duration)
        self.max_duration = max(self.max_duration, duration)
    
    @property
    def avg_duration(self) -> float:
        """Durée moyenne"""
        return self.total_duration / self.total_count if self.total_count > 0 else 0.0
    
    @property
    def p95_duration(self) -> float:
        """95e percentile"""
        if not self.durations:
            return 0.0
        return statistics.quantiles(list(self.durations), n=20)[18]  # 95e percentile
    
    @property
    def slow_query_rate(self) -> float:
        """Taux de requêtes lentes"""
        return (self.slow_count / self.total_count * 100) if self.total_count > 0 else 0.0

class QueryAnalyzer:
    """Analyseur de requêtes SQL"""
    
    @staticmethod
    def parse_query(query: str) -> Dict[str, str]:
        """Parser une requête pour extraire table et opération"""
        query_upper = query.upper().strip()
        
        # Déterminer l'opération
        if query_upper.startswith('SELECT'):
            operation = 'SELECT'
        elif query_upper.startswith('INSERT'):
            operation = 'INSERT'
        elif query_upper.startswith('UPDATE'):
            operation = 'UPDATE'
        elif query_upper.startswith('DELETE'):
            operation = 'DELETE'
        elif query_upper.startswith('CREATE'):
            operation = 'CREATE'
        elif query_upper.startswith('DROP'):
            operation = 'DROP'
        elif query_upper.startswith('ALTER'):
            operation = 'ALTER'
        else:
            operation = 'UNKNOWN'
        
        # Extraire le nom de table (simplifiée)
        table = 'unknown'
        try:
            if 'FROM' in query_upper:
                parts = query_upper.split('FROM')[1].strip().split()
                if parts:
                    table = parts[0].replace('"', '').replace('`', '')
            elif 'INTO' in query_upper:
                parts = query_upper.split('INTO')[1].strip().split()
                if parts:
                    table = parts[0].replace('"', '').replace('`', '')
            elif 'UPDATE' in query_upper:
                parts = query_upper.split('UPDATE')[1].strip().split()
                if parts:
                    table = parts[0].replace('"', '').replace('`', '')
        except Exception:
            pass
            
        return {'operation': operation, 'table': table}
    
    @staticmethod
    def is_query_problematic(query: str, duration: float) -> List[str]:
        """Détecter les problèmes potentiels dans une requête"""
        issues = []
        query_upper = query.upper()
        
        # Requête très lente
        if duration > 5.0:
            issues.append(f"VERY_SLOW ({duration:.2f}s)")
        elif duration > 1.0:
            issues.append(f"SLOW ({duration:.2f}s)")
        
        # Anti-patterns
        if 'SELECT *' in query_upper:
            issues.append("SELECT_ALL")
        
        if 'WITHOUT INDEX' in query_upper or ('WHERE' in query_upper and 'LIKE' in query_upper and query.count('%') >= 2):
            issues.append("POTENTIAL_FULL_SCAN")
            
        if 'ORDER BY' in query_upper and 'LIMIT' not in query_upper:
            issues.append("UNBOUNDED_ORDER_BY")
            
        if 'GROUP BY' in query_upper and 'HAVING' not in query_upper and 'LIMIT' not in query_upper:
            issues.append("UNBOUNDED_GROUP_BY")
        
        return issues

class SlowQueryLogger:
    """Logger spécialisé pour les requêtes lentes"""
    
    def __init__(self, log_file: str = "logs/slow_queries.log"):
        self.logger = logging.getLogger("jarvis.slow_queries")
        
        # Handler pour fichier dédié
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [SLOW_QUERY] %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.WARNING)
    
    def log_slow_query(self, metrics: QueryMetrics):
        """Logger une requête lente"""
        issues = QueryAnalyzer.is_query_problematic(metrics.query, metrics.duration)
        
        log_data = {
            "duration": metrics.duration,
            "timestamp": metrics.timestamp.isoformat(),
            "table": metrics.table,
            "operation": metrics.operation,
            "user_id": metrics.user_id,
            "issues": issues,
            "query": metrics.query[:500] + "..." if len(metrics.query) > 500 else metrics.query,
            "rows_affected": metrics.rows_affected
        }
        
        self.logger.warning(json.dumps(log_data, indent=2))

class DatabaseMonitor:
    """Monitor principal pour les performances de base de données"""
    
    def __init__(self, slow_query_threshold: float = 1.0, enable_explain: bool = True):
        self.slow_query_threshold = slow_query_threshold
        self.enable_explain = enable_explain
        self.query_stats: Dict[str, QueryStats] = defaultdict(QueryStats)
        self.recent_slow_queries: deque = deque(maxlen=100)
        self.slow_query_logger = SlowQueryLogger()
        self.logger = logging.getLogger(__name__)
        
        # Callbacks personnalisés
        self.slow_query_callbacks: List[Callable] = []
        
        # Pool de connexions pour les requêtes d'analyse
        self._analysis_pool: Optional[asyncpg.Pool] = None
    
    async def initialize_analysis_pool(self, database_url: str):
        """Initialiser un pool de connexions pour l'analyse"""
        try:
            self._analysis_pool = await asyncpg.create_pool(
                database_url,
                min_size=2,
                max_size=5,
                command_timeout=10
            )
            self.logger.info("Analysis connection pool initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize analysis pool: {e}")
    
    def add_slow_query_callback(self, callback: Callable[[QueryMetrics], None]):
        """Ajouter un callback pour les requêtes lentes"""
        self.slow_query_callbacks.append(callback)
    
    async def record_query(self, query: str, duration: float, session: Optional[AsyncSession] = None, **kwargs):
        """Enregistrer une requête exécutée"""
        metrics = QueryMetrics(
            query=query,
            duration=duration,
            timestamp=datetime.utcnow(),
            **kwargs
        )
        
        # Mettre à jour les statistiques
        key = f"{metrics.operation}:{metrics.table}"
        is_slow = duration >= self.slow_query_threshold
        
        self.query_stats[key].add_measurement(duration, is_slow)
        
        # Métriques Prometheus
        QUERY_DURATION.labels(
            query_type=metrics.operation,
            table=metrics.table,
            operation=metrics.operation
        ).observe(duration)
        
        if is_slow:
            SLOW_QUERIES_TOTAL.labels(
                query_type=metrics.operation,
                table=metrics.table
            ).inc()
            
            # Logger et analyser la requête lente
            await self._handle_slow_query(metrics, session)
    
    async def _handle_slow_query(self, metrics: QueryMetrics, session: Optional[AsyncSession] = None):
        """Gérer une requête lente détectée"""
        # Ajouter à la liste des requêtes lentes récentes
        self.recent_slow_queries.append(metrics)
        
        # Logger
        self.slow_query_logger.log_slow_query(metrics)
        
        # Obtenir le plan d'exécution si possible
        if self.enable_explain and self._analysis_pool:
            try:
                explain_plan = await self._get_explain_plan(metrics.query)
                metrics.explain_plan = explain_plan
            except Exception as e:
                self.logger.debug(f"Could not get explain plan: {e}")
        
        # Appeler les callbacks
        for callback in self.slow_query_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(metrics)
                else:
                    callback(metrics)
            except Exception as e:
                self.logger.error(f"Error in slow query callback: {e}")
        
        # Log console pour les requêtes très lentes
        if metrics.duration > 5.0:
            self.logger.error(
                f"🐌 VERY SLOW QUERY ({metrics.duration:.2f}s): "
                f"{metrics.operation} on {metrics.table} "
                f"- {metrics.query[:100]}..."
            )
        elif metrics.duration > self.slow_query_threshold:
            self.logger.warning(
                f"⚠️ Slow query ({metrics.duration:.2f}s): "
                f"{metrics.operation} on {metrics.table}"
            )
    
    async def _get_explain_plan(self, query: str) -> Optional[Dict]:
        """Obtenir le plan d'exécution d'une requête"""
        if not self._analysis_pool:
            return None
            
        try:
            async with self._analysis_pool.acquire() as conn:
                # Utiliser EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
                explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"
                result = await conn.fetchval(explain_query)
                return result[0] if result else None
        except Exception as e:
            self.logger.debug(f"Error getting explain plan: {e}")
            return None
    
    def get_query_statistics(self) -> Dict[str, Any]:
        """Obtenir les statistiques de requêtes"""
        stats = {}
        total_queries = 0
        total_slow_queries = 0
        
        for key, query_stats in self.query_stats.items():
            total_queries += query_stats.total_count
            total_slow_queries += query_stats.slow_count
            
            stats[key] = {
                "total_count": query_stats.total_count,
                "slow_count": query_stats.slow_count,
                "avg_duration": query_stats.avg_duration,
                "p95_duration": query_stats.p95_duration,
                "max_duration": query_stats.max_duration,
                "slow_rate": query_stats.slow_query_rate
            }
        
        return {
            "query_stats": stats,
            "summary": {
                "total_queries": total_queries,
                "total_slow_queries": total_slow_queries,
                "slow_query_rate": (total_slow_queries / total_queries * 100) if total_queries > 0 else 0,
                "monitored_query_types": len(stats)
            },
            "recent_slow_queries": [
                {
                    "duration": q.duration,
                    "table": q.table,
                    "operation": q.operation,
                    "timestamp": q.timestamp.isoformat(),
                    "query": q.query[:200] + "..." if len(q.query) > 200 else q.query
                }
                for q in list(self.recent_slow_queries)[-10:]  # 10 plus récentes
            ]
        }
    
    async def get_database_metrics(self) -> Dict[str, Any]:
        """Obtenir les métriques générales de la base de données"""
        if not self._analysis_pool:
            return {}
        
        try:
            async with self._analysis_pool.acquire() as conn:
                # Statistiques de connexions actives
                active_connections = await conn.fetchval(
                    "SELECT count(*) FROM pg_stat_activity WHERE state = 'active'"
                )
                
                # Taille de la base de données
                db_size = await conn.fetchval(
                    "SELECT pg_size_pretty(pg_database_size(current_database()))"
                )
                
                # Cache hit ratio
                cache_hit_ratio = await conn.fetchval(
                    """
                    SELECT 
                        round(
                            sum(blks_hit) * 100.0 / nullif(sum(blks_hit + blks_read), 0), 2
                        ) as cache_hit_ratio 
                    FROM pg_stat_database
                    """
                )
                
                # Top tables by activity
                table_stats = await conn.fetch(
                    """
                    SELECT 
                        schemaname,
                        tablename,
                        n_tup_ins + n_tup_upd + n_tup_del as total_activity,
                        seq_scan,
                        seq_tup_read,
                        idx_scan,
                        idx_tup_fetch
                    FROM pg_stat_user_tables 
                    ORDER BY total_activity DESC 
                    LIMIT 10
                    """
                )
                
                # Mettre à jour métriques Prometheus
                ACTIVE_CONNECTIONS.set(active_connections)
                
                return {
                    "active_connections": active_connections,
                    "database_size": db_size,
                    "cache_hit_ratio": cache_hit_ratio,
                    "table_activity": [dict(row) for row in table_stats]
                }
                
        except Exception as e:
            self.logger.error(f"Error getting database metrics: {e}")
            return {}
    
    async def cleanup(self):
        """Nettoyer les ressources"""
        if self._analysis_pool:
            await self._analysis_pool.close()

# Décorateur pour monitoring automatique
def monitor_query(monitor: DatabaseMonitor, query_type: str = None):
    """Décorateur pour monitorer automatiquement les requêtes"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Extraire des informations du contexte
                query = getattr(result, 'statement', str(result)) if hasattr(result, 'statement') else 'unknown'
                
                await monitor.record_query(
                    query=query,
                    duration=duration,
                    operation=query_type or func.__name__
                )
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                await monitor.record_query(
                    query=f"FAILED: {func.__name__}",
                    duration=duration,
                    operation=query_type or func.__name__
                )
                raise
        return wrapper
    return decorator

# Instance globale du monitor
db_monitor = DatabaseMonitor(
    slow_query_threshold=1.0,  # 1 seconde
    enable_explain=True
)