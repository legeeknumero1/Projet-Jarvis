"""
Middleware pour monitoring automatique des requêtes de base de données
Intégration transparente avec SQLAlchemy et FastAPI
"""

import time
import logging
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
from sqlalchemy.engine.events import event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request
from sqlalchemy.pool import Pool

from monitoring.query_monitor import db_monitor, QueryMetrics

class DatabaseMonitoringMiddleware:
    """Middleware pour intercepter et monitorer les requêtes de base de données"""
    
    def __init__(self, engine: Engine):
        self.engine = engine
        self.logger = logging.getLogger(__name__)
        self._setup_sqlalchemy_events()
    
    def _setup_sqlalchemy_events(self):
        """Configurer les événements SQLAlchemy pour le monitoring"""
        
        @event.listens_for(self.engine, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            """Événement avant exécution de requête"""
            context._query_start_time = time.time()
            context._statement = statement
            context._parameters = parameters
        
        @event.listens_for(self.engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            """Événement après exécution de requête"""
            if hasattr(context, '_query_start_time'):
                duration = time.time() - context._query_start_time
                
                # Enregistrer la requête de manière asynchrone
                import asyncio
                asyncio.create_task(
                    db_monitor.record_query(
                        query=statement,
                        duration=duration,
                        rows_affected=cursor.rowcount if hasattr(cursor, 'rowcount') else None
                    )
                )
        
        @event.listens_for(self.engine, "handle_error")
        def handle_error(exception_context):
            """Événement en cas d'erreur de requête"""
            if hasattr(exception_context.execution_context, '_query_start_time'):
                duration = time.time() - exception_context.execution_context._query_start_time
                statement = getattr(exception_context.execution_context, '_statement', 'UNKNOWN')
                
                # Enregistrer la requête échouée
                import asyncio
                asyncio.create_task(
                    db_monitor.record_query(
                        query=f"FAILED: {statement}",
                        duration=duration,
                        operation="ERROR"
                    )
                )
                
                self.logger.error(
                    f"Database query failed after {duration:.2f}s: {statement[:100]}..."
                )

class MonitoredAsyncSession:
    """Wrapper pour AsyncSession avec monitoring intégré"""
    
    def __init__(self, session: AsyncSession, user_id: Optional[str] = None):
        self.session = session
        self.user_id = user_id
        self._query_count = 0
        self._total_duration = 0.0
    
    async def execute(self, statement, parameters=None, execution_options=None, bind_arguments=None, **kwargs):
        """Execute avec monitoring"""
        start_time = time.time()
        self._query_count += 1
        
        try:
            result = await self.session.execute(
                statement, parameters, execution_options, bind_arguments, **kwargs
            )
            
            duration = time.time() - start_time
            self._total_duration += duration
            
            # Enregistrer la métrique
            await db_monitor.record_query(
                query=str(statement),
                duration=duration,
                user_id=self.user_id,
                rows_affected=result.rowcount if hasattr(result, 'rowcount') else None
            )
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            await db_monitor.record_query(
                query=f"FAILED: {str(statement)}",
                duration=duration,
                user_id=self.user_id,
                operation="ERROR"
            )
            raise
    
    async def commit(self):
        """Commit avec timing"""
        start_time = time.time()
        await self.session.commit()
        duration = time.time() - start_time
        
        if duration > 0.5:  # Log des commits lents
            logging.warning(f"Slow commit detected: {duration:.2f}s")
    
    async def rollback(self):
        """Rollback avec logging"""
        await self.session.rollback()
        logging.info("Session rolled back")
    
    async def close(self):
        """Fermeture avec métriques de session"""
        await self.session.close()
        
        if self._query_count > 0:
            avg_duration = self._total_duration / self._query_count
            if avg_duration > 0.5:
                logging.info(
                    f"Session closed - {self._query_count} queries, "
                    f"avg duration: {avg_duration:.2f}s, "
                    f"total: {self._total_duration:.2f}s"
                )
    
    def __getattr__(self, name):
        """Déléguer les autres méthodes à la session originale"""
        return getattr(self.session, name)

class QueryAnalysisMiddleware:
    """Middleware d'analyse avancée des requêtes"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._request_queries = {}
    
    async def __call__(self, request: Request, call_next):
        """Middleware FastAPI pour analyser les requêtes par endpoint"""
        request_id = id(request)
        self._request_queries[request_id] = {
            'queries': [],
            'start_time': time.time(),
            'endpoint': request.url.path
        }
        
        # Callback pour capturer les requêtes de cette requête HTTP
        def query_callback(metrics: QueryMetrics):
            if request_id in self._request_queries:
                self._request_queries[request_id]['queries'].append(metrics)
        
        # Ajouter le callback temporairement
        db_monitor.add_slow_query_callback(query_callback)
        
        try:
            response = await call_next(request)
            
            # Analyser les requêtes de cette requête
            request_data = self._request_queries.get(request_id, {})
            queries = request_data.get('queries', [])
            total_duration = time.time() - request_data.get('start_time', time.time())
            
            if queries:
                query_duration = sum(q.duration for q in queries)
                query_ratio = (query_duration / total_duration) * 100
                
                # Alerter si les requêtes représentent plus de 70% du temps de traitement
                if query_ratio > 70 and total_duration > 0.5:
                    self.logger.warning(
                        f"Database-heavy endpoint detected: {request_data['endpoint']} - "
                        f"{len(queries)} queries took {query_duration:.2f}s "
                        f"({query_ratio:.1f}% of {total_duration:.2f}s total)"
                    )
                
                # Détecter les N+1 queries
                if len(queries) > 10:
                    similar_queries = self._detect_n_plus_one(queries)
                    if similar_queries:
                        self.logger.warning(
                            f"Potential N+1 query detected in {request_data['endpoint']}: "
                            f"{len(similar_queries)} similar queries"
                        )
            
            return response
            
        finally:
            # Nettoyer
            self._request_queries.pop(request_id, None)
            # Note: Dans une vraie implémentation, on devrait gérer la suppression des callbacks
    
    def _detect_n_plus_one(self, queries) -> list:
        """Détecter les patterns N+1"""
        # Grouper les requêtes similaires (même structure, paramètres différents)
        query_patterns = {}
        
        for query in queries:
            # Simplifier la requête pour détecter les patterns
            pattern = self._normalize_query(query.query)
            if pattern not in query_patterns:
                query_patterns[pattern] = []
            query_patterns[pattern].append(query)
        
        # Retourner les patterns avec plus de 5 occurrences
        n_plus_one_patterns = []
        for pattern, pattern_queries in query_patterns.items():
            if len(pattern_queries) >= 5:
                n_plus_one_patterns.extend(pattern_queries)
        
        return n_plus_one_patterns
    
    def _normalize_query(self, query: str) -> str:
        """Normaliser une requête pour détecter les patterns"""
        import re
        
        # Remplacer les valeurs par des placeholders
        normalized = re.sub(r"'[^']*'", "'?'", query)  # Strings
        normalized = re.sub(r'\b\d+\b', '?', normalized)  # Numbers
        normalized = re.sub(r'\$\d+', '?', normalized)  # PostgreSQL parameters
        
        return normalized.strip()

# Factory function pour créer une session monitorée
@asynccontextmanager
async def get_monitored_session(session_factory, user_id: Optional[str] = None):
    """Context manager pour obtenir une session monitorée"""
    session = session_factory()
    monitored_session = MonitoredAsyncSession(session, user_id=user_id)
    
    try:
        yield monitored_session
    except Exception as e:
        await monitored_session.rollback()
        raise
    finally:
        await monitored_session.close()

# Configuration pour pool monitoring
def setup_pool_monitoring(engine: Engine):
    """Configurer le monitoring du pool de connexions"""
    
    @event.listens_for(engine, "connect")
    def on_connect(dbapi_conn, connection_record):
        logging.info("New database connection established")
    
    @event.listens_for(engine, "checkout")
    def on_checkout(dbapi_conn, connection_record, connection_proxy):
        logging.debug("Connection checked out from pool")
    
    @event.listens_for(engine, "checkin")
    def on_checkin(dbapi_conn, connection_record):
        logging.debug("Connection returned to pool")
    
    # Monitoring périodique du pool
    async def monitor_pool():
        """Fonction de monitoring du pool à exécuter périodiquement"""
        pool = engine.pool
        logging.info(
            f"Pool status - Size: {pool.size()}, "
            f"Checked out: {pool.checkedout()}, "
            f"Overflow: {pool.overflow()}, "
            f"Invalid: {pool.invalidated()}"
        )
        
        # Métriques Prometheus
        from monitoring.query_monitor import DB_POOL_SIZE, DB_POOL_CHECKED_OUT
        DB_POOL_SIZE.set(pool.size())
        DB_POOL_CHECKED_OUT.set(pool.checkedout())
    
    return monitor_pool

# Alertes automatiques pour requêtes critiques
class QueryAlerter:
    """Système d'alertes pour requêtes problématiques"""
    
    def __init__(self, webhooks: list = None, email_config: dict = None):
        self.webhooks = webhooks or []
        self.email_config = email_config
        self.logger = logging.getLogger(__name__)
        
        # Seuils d'alerte
        self.critical_duration = 10.0  # 10 secondes
        self.high_duration = 5.0       # 5 secondes
        
        # Éviter le spam d'alertes
        self.last_alerts = {}
        self.alert_cooldown = 300      # 5 minutes
    
    async def handle_slow_query(self, metrics: QueryMetrics):
        """Gérer une requête lente avec alertes si nécessaire"""
        alert_key = f"{metrics.operation}:{metrics.table}"
        current_time = time.time()
        
        # Vérifier le cooldown
        if alert_key in self.last_alerts:
            if current_time - self.last_alerts[alert_key] < self.alert_cooldown:
                return
        
        severity = self._get_severity(metrics.duration)
        if severity:
            await self._send_alert(metrics, severity)
            self.last_alerts[alert_key] = current_time
    
    def _get_severity(self, duration: float) -> Optional[str]:
        """Déterminer la sévérité d'une requête lente"""
        if duration >= self.critical_duration:
            return "CRITICAL"
        elif duration >= self.high_duration:
            return "HIGH"
        return None
    
    async def _send_alert(self, metrics: QueryMetrics, severity: str):
        """Envoyer une alerte"""
        message = (
            f"[{severity}] Slow query detected\n"
            f"Duration: {metrics.duration:.2f}s\n"
            f"Operation: {metrics.operation} on {metrics.table}\n"
            f"Time: {metrics.timestamp}\n"
            f"Query: {metrics.query[:200]}..."
        )
        
        self.logger.critical(message)
        
        # Ici on pourrait intégrer avec des services d'alerting externes
        # comme Slack, Discord, email, PagerDuty, etc.

# Instance globale de l'alerter
query_alerter = QueryAlerter()

# Ajouter l'alerter comme callback
db_monitor.add_slow_query_callback(query_alerter.handle_slow_query)