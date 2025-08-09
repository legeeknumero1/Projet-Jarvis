"""Middleware production avec contextvars pour correlation logs"""
import time
import uuid
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from ..utils.logging import set_context, reset_context

class RequestIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware production pour:
    1. Générer/récupérer request-id unique
    2. Définir contexte de correlation (contextvars)
    3. Logger automatiquement les requêtes servies
    4. Injecter X-Request-ID dans la réponse
    """
    
    async def dispatch(self, request, call_next):
        # Générer ou récupérer request-id
        rid = request.headers.get("x-request-id") or uuid.uuid4().hex[:12]
        start_time = time.perf_counter()
        
        # Définir contexte pour toute la requête
        tokens = set_context(
            request_id=rid,
            path=request.url.path,
            method=request.method,
            client_ip=self._get_client_ip(request),
            component="api",
        )
        
        try:
            # Traiter la requête
            response = await call_next(request)
            
            # Enrichir le contexte avec la réponse
            latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            set_context(status_code=response.status_code, latency_ms=latency_ms)
            
            # Injecter request-id dans les headers
            response.headers["x-request-id"] = rid
            
            # Log automatique de la requête servie
            logger = logging.getLogger("backend.http")
            logger.info("request served")
            
            return response
            
        finally:
            # Cleanup contexte
            reset_context(tokens)
    
    def _get_client_ip(self, request) -> str:
        """Récupère IP client avec support proxy/load balancer"""
        # Headers de proxy en priorité
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fallback IP directe
        return request.client.host if request.client else "-"