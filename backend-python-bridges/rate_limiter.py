"""
Flask Rate Limiting Module - Security Fix C14
Per-endpoint and per-user rate limiting using Flask-Limiter
Prevents DoS attacks and brute-force attempts
"""

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import request
from functools import wraps
from typing import Optional, Tuple, Callable
from loguru import logger
import time


# ============================================================================
# Rate Limit Configuration
# ============================================================================

class RateLimitConfig:
    """Configuration for rate limiting"""

    # Auth endpoints - most restrictive
    AUTH_LOGIN_LIMIT = "5/minute"           # 5 attempts per minute
    AUTH_VERIFY_LIMIT = "30/minute"         # 30 verifications per minute

    # LLM endpoints - moderate
    LLM_GENERATE_LIMIT = "10/minute"        # 10 requests per minute
    LLM_MODELS_LIMIT = "30/minute"          # 30 model list requests per minute

    # STT endpoints - moderate
    STT_TRANSCRIBE_LIMIT = "20/minute"      # 20 transcriptions per minute

    # TTS endpoints - moderate
    TTS_SYNTHESIZE_LIMIT = "20/minute"      # 20 syntheses per minute
    TTS_VOICES_LIMIT = "30/minute"          # 30 voice list requests per minute

    # Embeddings endpoints - moderate
    EMBEDDINGS_EMBED_LIMIT = "30/minute"    # 30 embeddings per minute
    EMBEDDINGS_BATCH_LIMIT = "20/minute"    # 20 batch operations per minute

    # Health checks - no limits
    HEALTH_LIMIT = None                     # Unlimited health checks


# ============================================================================
# Flask-Limiter Integration
# ============================================================================

def create_limiter(app) -> Limiter:
    """
    Create and configure Flask-Limiter instance

    Args:
        app: Flask application instance

    Returns:
        Configured Limiter instance
    """
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,  # Use client IP as key
        default_limits=["200/day", "50/hour"],  # Default fallback
        storage_uri="memory://",  # Use in-memory storage (can upgrade to Redis)
        strategy="fixed-window",  # Fixed window algorithm
        in_memory_fallback_enabled=True  # Fallback if storage fails
    )

    logger.info(" Flask-Limiter initialized")
    return limiter


# ============================================================================
# Custom Rate Limit Key Functions
# ============================================================================

def get_user_id_key() -> str:
    """
    Get rate limit key based on user ID from JWT token
    Falls back to IP address if no valid token

    Returns:
        Rate limit key (user_id or IP address)
    """
    try:
        # Try to get user_id from request context
        if hasattr(request, 'user') and request.user:
            user_id = request.user.get('user_id')
            if user_id:
                return f"user:{user_id}"
    except Exception:
        pass

    # Fallback to IP address
    return f"ip:{get_remote_address()}"


def get_username_key() -> str:
    """
    Get rate limit key based on username from JWT token
    Falls back to IP address if no valid token

    Returns:
        Rate limit key (username or IP address)
    """
    try:
        if hasattr(request, 'user') and request.user:
            username = request.user.get('username')
            if username:
                return f"user:{username}"
    except Exception:
        pass

    return f"ip:{get_remote_address()}"


# ============================================================================
# Rate Limit Decorators
# ============================================================================

def rate_limit_auth_login(limiter: Limiter) -> Callable:
    """
    Decorator for login endpoint - strictest limits to prevent brute-force

    Args:
        limiter: Limiter instance

    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        f = limiter.limit(
            RateLimitConfig.AUTH_LOGIN_LIMIT,
            key_func=get_remote_address,
            error_message="Too many login attempts. Please try again in a minute."
        )(f)
        return f
    return decorator


def rate_limit_auth_verify(limiter: Limiter) -> Callable:
    """
    Decorator for token verify endpoint

    Args:
        limiter: Limiter instance

    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        f = limiter.limit(
            RateLimitConfig.AUTH_VERIFY_LIMIT,
            key_func=get_user_id_key,
            error_message="Too many verification requests. Please try again later."
        )(f)
        return f
    return decorator


def rate_limit_llm_generate(limiter: Limiter) -> Callable:
    """
    Decorator for LLM generation endpoint - per-user limit

    Args:
        limiter: Limiter instance

    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        f = limiter.limit(
            RateLimitConfig.LLM_GENERATE_LIMIT,
            key_func=get_user_id_key,
            error_message="Too many LLM requests. Please try again in a minute."
        )(f)
        return f
    return decorator


def rate_limit_stt_transcribe(limiter: Limiter) -> Callable:
    """
    Decorator for STT transcription endpoint

    Args:
        limiter: Limiter instance

    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        f = limiter.limit(
            RateLimitConfig.STT_TRANSCRIBE_LIMIT,
            key_func=get_user_id_key,
            error_message="Too many transcription requests. Please try again in a minute."
        )(f)
        return f
    return decorator


def rate_limit_tts_synthesize(limiter: Limiter) -> Callable:
    """
    Decorator for TTS synthesis endpoint

    Args:
        limiter: Limiter instance

    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        f = limiter.limit(
            RateLimitConfig.TTS_SYNTHESIZE_LIMIT,
            key_func=get_user_id_key,
            error_message="Too many synthesis requests. Please try again in a minute."
        )(f)
        return f
    return decorator


def rate_limit_embeddings(limiter: Limiter) -> Callable:
    """
    Decorator for embeddings endpoint

    Args:
        limiter: Limiter instance

    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        f = limiter.limit(
            RateLimitConfig.EMBEDDINGS_EMBED_LIMIT,
            key_func=get_user_id_key,
            error_message="Too many embedding requests. Please try again in a minute."
        )(f)
        return f
    return decorator


# ============================================================================
# Rate Limit Monitoring & Logging
# ============================================================================

class RateLimitMonitor:
    """Monitor and log rate limit violations"""

    @staticmethod
    def log_violation(endpoint: str, key: str, limit: str, user_id: Optional[str] = None):
        """
        Log a rate limit violation

        Args:
            endpoint: Endpoint path
            key: Rate limit key (user_id or IP)
            limit: Rate limit config
            user_id: Optional user ID
        """
        logger.warning(
            f" RATE LIMIT VIOLATION: endpoint={endpoint}, key={key}, limit={limit}",
            extra={
                "endpoint": endpoint,
                "key": key,
                "limit": limit,
                "user_id": user_id,
                "timestamp": time.time()
            }
        )

    @staticmethod
    def log_rate_limit_success(endpoint: str, key: str, user_id: Optional[str] = None):
        """
        Log successful request under rate limit

        Args:
            endpoint: Endpoint path
            key: Rate limit key
            user_id: Optional user ID
        """
        # Only log at debug level to avoid log spam
        logger.debug(
            f" Rate limit check passed: endpoint={endpoint}, key={key}",
            extra={
                "endpoint": endpoint,
                "key": key,
                "user_id": user_id
            }
        )


# ============================================================================
# Rate Limit Error Handler
# ============================================================================

def handle_rate_limit_exceeded(limiter: Limiter, app):
    """
    Configure error handler for rate limit exceeded

    Args:
        limiter: Limiter instance
        app: Flask application instance
    """
    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        """Handle rate limit exceeded errors"""
        logger.warning(
            f" Rate limit exceeded: {e.description}",
            extra={
                "error": str(e),
                "remote_addr": get_remote_address(),
                "endpoint": request.endpoint
            }
        )

        from flask import jsonify
        return jsonify({
            "error": "Rate limit exceeded",
            "message": e.description or "Too many requests. Please try again later.",
            "status": 429
        }), 429


# ============================================================================
# Rate Limit Statistics
# ============================================================================

class RateLimitStats:
    """Collect statistics about rate limiting"""

    def __init__(self):
        self.violations = 0
        self.total_requests = 0
        self.by_endpoint = {}

    def record_request(self, endpoint: str):
        """Record a request"""
        self.total_requests += 1
        if endpoint not in self.by_endpoint:
            self.by_endpoint[endpoint] = 0
        self.by_endpoint[endpoint] += 1

    def record_violation(self, endpoint: str):
        """Record a rate limit violation"""
        self.violations += 1

    def get_stats(self) -> dict:
        """Get statistics summary"""
        return {
            "total_requests": self.total_requests,
            "violations": self.violations,
            "violation_rate": (
                (self.violations / self.total_requests * 100)
                if self.total_requests > 0 else 0
            ),
            "by_endpoint": self.by_endpoint
        }


# ============================================================================
# Tests
# ============================================================================

def test_rate_limit_config():
    """Test rate limit configuration"""
    assert RateLimitConfig.AUTH_LOGIN_LIMIT == "5/minute", "Auth login limit should be 5/minute"
    assert RateLimitConfig.LLM_GENERATE_LIMIT == "10/minute", "LLM generate limit should be 10/minute"
    assert RateLimitConfig.STT_TRANSCRIBE_LIMIT == "20/minute", "STT transcribe limit should be 20/minute"
    assert RateLimitConfig.TTS_SYNTHESIZE_LIMIT == "20/minute", "TTS synthesize limit should be 20/minute"
    print("[OK] All rate limit config tests passed!")


if __name__ == "__main__":
    test_rate_limit_config()
