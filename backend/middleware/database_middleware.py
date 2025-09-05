"""
DB query monitoring middleware
SQLAlchemy + FastAPI
"""

from __future__ import annotations

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from typing import Any, Optional, Sequence

from fastapi import Request
from sqlalchemy import event
from sqlalchemy.engine import Engine, Connection
from sqlalchemy.engine.interfaces import ExceptionContext
from sqlalchemy.engine import ExecutionContext  # type: ignore[attr-defined]
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Protocol, runtime_checkable

from monitoring.query_monitor import db_monitor, QueryMetrics


# --- DB-API cursor typing (portable) -----------------------------------------
@runtime_checkable
class DBCursor(Protocol):
    rowcount: int
    def execute(self, *args: Any, **kwargs: Any) -> Any: ...
# ----------------------------------------------------------------------------


class DatabaseMonitoringMiddleware:
    """Intercept and monitor low-level SQL executions via SQLAlchemy events."""

    def __init__(self, engine: Engine) -> None:
        self.engine: Engine = engine
        self.logger = logging.getLogger(__name__)
        # Capture the main loop once; handlers may execute in worker threads.
        try:
            self._loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
        except RuntimeError:
            # If constructed at import time, defer loop lookup to first use
            self._loop = asyncio.new_event_loop()  # placeholder; will be replaced
        self._setup_sqlalchemy_events()

    # ---------- utilities ----------
    def _ensure_loop(self) -> asyncio.AbstractEventLoop:
        try:
            # If we're on the main thread with a running loop:
            self._loop = asyncio.get_running_loop()
        except RuntimeError:
            pass
        return self._loop

    def _fire_and_forget(self, coro: "asyncio.coroutines.CoroWrapper[Any] | asyncio.Future[Any] | Any") -> None:
        """Schedule an async task from *any* thread without crashing."""
        loop = self._ensure_loop()
        # we must hop to the loop thread
        loop.call_soon_threadsafe(asyncio.create_task, coro)

    # ---------- wiring ----------
    def _setup_sqlalchemy_events(self) -> None:
        """Wire SQLAlchemy core events with proper typing and safe scheduling."""

        @event.listens_for(self.engine, "before_cursor_execute")
        def before_cursor_execute(
            conn: Connection,
            cursor: DBCursor,
            statement: str,
            parameters: Sequence[Any] | dict[str, Any] | None,
            context: ExecutionContext,
            executemany: bool,
        ) -> None:
            context._query_start_time = time.time()
            context._statement = statement
            context._parameters = parameters

        @event.listens_for(self.engine, "after_cursor_execute")
        def after_cursor_execute(
            conn: Connection,
            cursor: DBCursor,
            statement: str,
            parameters: Sequence[Any] | dict[str, Any] | None,
            context: ExecutionContext,
            executemany: bool,
        ) -> None:
            if hasattr(context, "_query_start_time"):
                duration = time.time() - context._query_start_time  # type: ignore[attr-defined]
                rows = getattr(cursor, "rowcount", None)
                # schedule in the main event loop; handler is sync/threaded
                self._fire_and_forget(
                    db_monitor.record_query(
                        query=statement,
                        duration=duration,
                        rows_affected=rows if isinstance(rows, int) else None,
                    )
                )

        @event.listens_for(self.engine, "handle_error")
        def handle_error(exception_context: ExceptionContext) -> None:
            ctx = exception_context.execution_context
            if hasattr(ctx, "_query_start_time"):
                duration = time.time() - getattr(ctx, "_query_start_time")
                statement = getattr(ctx, "_statement", "UNKNOWN")
                self._fire_and_forget(
                    db_monitor.record_query(
                        query=f"FAILED: {statement}",
                        duration=duration,
                        operation="ERROR",
                    )
                )
                self.logger.error("DB query failed after %.2fs: %s...", duration, str(statement)[:100])


class MonitoredAsyncSession:
    """Thin AsyncSession wrapper that adds timing and metrics."""

    def __init__(self, session: AsyncSession, user_id: Optional[str] = None) -> None:
        self.session = session
        self.user_id = user_id
        self._query_count = 0
        self._total_duration = 0.0

    async def execute(
        self,
        statement: Any,
        parameters: Any | None = None,
        *,
        execution_options: dict[str, Any] | None = None,
        bind_arguments: dict[str, Any] | None = None,
        **kwargs: Any,
    ):
        start = time.time()
        self._query_count += 1
        try:
            result = await self.session.execute(
                statement,
                parameters=parameters,
                execution_options=execution_options,
                bind_arguments=bind_arguments,
                **kwargs,
            )
            dur = time.time() - start
            self._total_duration += dur
            rows = getattr(result, "rowcount", None)
            await db_monitor.record_query(
                query=str(statement),
                duration=dur,
                user_id=self.user_id,
                rows_affected=rows if isinstance(rows, int) else None,
            )
            return result
        except Exception:
            dur = time.time() - start
            await db_monitor.record_query(
                query=f"FAILED: {statement}",
                duration=dur,
                user_id=self.user_id,
                operation="ERROR",
            )
            raise

    async def commit(self) -> None:
        start = time.time()
        await self.session.commit()
        dur = time.time() - start
        if dur > 0.5:
            logging.warning("Slow commit detected: %.2fs", dur)

    async def rollback(self) -> None:
        await self.session.rollback()
        logging.info("Session rolled back")

    async def close(self) -> None:
        await self.session.close()
        if self._query_count:
            avg = self._total_duration / self._query_count
            if avg > 0.5:
                logging.info(
                    "Session closed - %d queries, avg %.2fs, total %.2fs",
                    self._query_count, avg, self._total_duration
                )

    def __getattr__(self, name: str) -> Any:  # delegate
        return getattr(self.session, name)


class QueryAnalysisMiddleware:
    """FastAPI middleware analyzing queries per-request (endpoint)."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self._request_queries: dict[int, dict[str, Any]] = {}

    async def __call__(self, request: Request, call_next):
        rid = id(request)
        self._request_queries[rid] = {"queries": [], "start_time": time.time(), "endpoint": request.url.path}

        def _cb(metrics: QueryMetrics) -> None:
            bucket = self._request_queries.get(rid)
            if bucket is not None:
                bucket["queries"].append(metrics)

        db_monitor.add_slow_query_callback(_cb)
        try:
            response = await call_next(request)
            bucket = self._request_queries.get(rid, {})
            queries: list[QueryMetrics] = bucket.get("queries", [])
            total = time.time() - bucket.get("start_time", time.time())
            if queries:
                qtime = sum(q.duration for q in queries)
                ratio = (qtime / total) * 100 if total > 0 else 0.0
                if ratio > 70 and total > 0.5:
                    self.logger.warning(
                        "DB-heavy endpoint %s: %d queries took %.2fs (%.1f%% of %.2fs)",
                        bucket.get("endpoint"), len(queries), qtime, ratio, total
                    )
                if len(queries) > 10:
                    similars = self._detect_n_plus_one(queries)
                    if similars:
                        self.logger.warning(
                            "Potential N+1 in %s: %d similar queries",
                            bucket.get("endpoint"), len(similars)
                        )
            return response
        finally:
            self._request_queries.pop(rid, None)
            # (If you registered per-request callbacks globally in db_monitor,
            # make sure db_monitor can deregister them, or filter by request id.)

    def _detect_n_plus_one(self, queries: list[QueryMetrics]) -> list[QueryMetrics]:
        groups: dict[str, list[QueryMetrics]] = {}
        for q in queries:
            pat = self._normalize_query(q.query)
            groups.setdefault(pat, []).append(q)
        flagged: list[QueryMetrics] = []
        for pat, qs in groups.items():
            if len(qs) >= 5:
                flagged.extend(qs)
        return flagged

    def _normalize_query(self, query: str) -> str:
        import re
        s = re.sub(r"'[^']*'", "'?'", query)        # strings
        s = re.sub(r"\b\d+\b", "?", s)              # numbers
        s = re.sub(r"\$\d+", "?", s)                # PG parameters
        return s.strip()


@asynccontextmanager
async def get_monitored_session(session_factory, user_id: Optional[str] = None):
    session = session_factory()
    monitored = MonitoredAsyncSession(session, user_id=user_id)
    try:
        yield monitored
    except Exception:
        await monitored.rollback()
        raise
    finally:
        await monitored.close()


def setup_pool_monitoring(engine: Engine):
    """Return an async callable you can schedule to scrape pool metrics."""
    @event.listens_for(engine, "connect")
    def on_connect(dbapi_conn, connection_record) -> None:  # types: DB-API specific
        logging.info("New DB connection established")

    @event.listens_for(engine, "checkout")
    def on_checkout(dbapi_conn, connection_record, connection_proxy) -> None:
        logging.debug("Connection checked out from pool")

    @event.listens_for(engine, "checkin")
    def on_checkin(dbapi_conn, connection_record) -> None:
        logging.debug("Connection returned to pool")

    async def monitor_pool() -> None:
        pool = engine.pool
        logging.info(
            "Pool status - Size: %s, Checked out: %s, Overflow: %s, Invalid: %s",
            pool.size(), pool.checkedout(), pool.overflow(), pool.invalidated()
        )
        from monitoring.query_monitor import DB_POOL_SIZE, DB_POOL_CHECKED_OUT
        DB_POOL_SIZE.set(pool.size())
        DB_POOL_CHECKED_OUT.set(pool.checkedout())

    return monitor_pool


class QueryAlerter:
    """Alerting for slow/critical queries."""

    def __init__(self, webhooks: list[str] | None = None, email_config: dict[str, Any] | None = None) -> None:
        self.webhooks = webhooks or []
        self.email_config = email_config
        self.logger = logging.getLogger(__name__)
        self.critical_duration = 10.0
        self.high_duration = 5.0
        self.last_alerts: dict[str, float] = {}
        self.alert_cooldown = 300.0

    async def handle_slow_query(self, metrics: QueryMetrics) -> None:
        key = f"{metrics.operation}:{metrics.table}"
        now = time.time()
        if now - self.last_alerts.get(key, 0.0) < self.alert_cooldown:
            return
        severity = self._severity(metrics.duration)
        if severity:
            await self._send_alert(metrics, severity)
            self.last_alerts[key] = now

    def _severity(self, duration: float) -> Optional[str]:
        if duration >= self.critical_duration:
            return "CRITICAL"
        if duration >= self.high_duration:
            return "HIGH"
        return None

    async def _send_alert(self, metrics: QueryMetrics, severity: str) -> None:
        msg = (
            f"[{severity}] Slow query\n"
            f"Duration: {metrics.duration:.2f}s\n"
            f"Operation: {metrics.operation} on {metrics.table}\n"
            f"Time: {metrics.timestamp}\n"
            f"Query: {metrics.query[:200]}..."
        )
        self.logger.critical(msg)


query_alerter = QueryAlerter()
db_monitor.add_slow_query_callback(query_alerter.handle_slow_query)
