"""Rate limiting middleware pour anti-abus"""
import time
from collections import defaultdict, deque
from typing import Dict, Deque
from fastapi import HTTPException, Request
from utils.logging import get_logger

logger = get_logger(__name__)

# Import métriques Prometheus
try:
    from ..observability.metrics import record_rate_limit_hit
except ImportError:
    def record_rate_limit_hit(*args, **kwargs):
        pass

class RateLimiter:
    """Rate limiter in-memory pour développement/test"""
    
    def __init__(self, max_requests: int = 30, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.clients: Dict[str, Deque[float]] = defaultdict(deque)
    
    def _get_client_ip(self, request: Request) -> str:
        """Récupère IP client (avec support proxy)"""
        # Essayer X-Forwarded-For en premier (reverse proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        # Fallback sur X-Real-IP
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
            
        # Fallback sur IP client direct
        return request.client.host if request.client else "unknown"
    
    def is_allowed(self, request: Request) -> bool:
        """Vérifie si la requête est autorisée"""
        client_ip = self._get_client_ip(request)
        now = time.time()
        window_start = now - self.window_seconds
        
        # Nettoyer les anciennes requêtes
        client_requests = self.clients[client_ip]
        while client_requests and client_requests[0] < window_start:
            client_requests.popleft()
        
        # Vérifier limite
        if len(client_requests) >= self.max_requests:
            logger.warning(f"🚫 [RATE_LIMIT] IP {client_ip} bloquée - {len(client_requests)} req/min")
            # Enregistrer métrique
            record_rate_limit_hit("chat", "browser")
            return False
        
        # Enregistrer cette requête
        client_requests.append(now)
        return True


# Instance globale (pour développement - utiliser Redis en prod)
chat_limiter = RateLimiter(max_requests=30, window_seconds=60)  # 30 req/min
ws_limiter = RateLimiter(max_requests=10, window_seconds=60)    # 10 connexions/min


def check_chat_rate_limit(request: Request):
    """Dependency pour rate limiting chat API"""
    if not chat_limiter.is_allowed(request):
        raise HTTPException(
            status_code=429,
            detail="Trop de requêtes - max 30/minute"
        )


def check_ws_rate_limit(request: Request):
    """Check rate limit pour WebSocket (à utiliser manuellement)"""
    if not ws_limiter.is_allowed(request):
        return False
    return True