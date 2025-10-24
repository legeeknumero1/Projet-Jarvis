"""
Middleware de sécurité ultra-avancé pour toutes les requêtes
Intégration complète avec le système de sécurité OWASP 2025
"""
import logging
import time
from typing import Callable
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Middleware de sécurité qui applique toutes les protections
    sur chaque requête entrante
    """
    
    def __init__(self, app, security_manager=None):
        super().__init__(app)
        self.security_manager = security_manager
        
        # Endpoints exemptés de certaines vérifications
        self.exempt_endpoints = {
            '/health',
            '/metrics', 
            '/docs',
            '/openapi.json'
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Traitement sécurisé de chaque requête"""
        start_time = time.perf_counter()
        
        try:
            # 1. Vérification disponibilité du système de sécurité
            if not self.security_manager:
                logger.error("❌ [SECURITY_MW] Système de sécurité non disponible")
                return Response(
                    content="Service sécurisé temporairement indisponible",
                    status_code=503,
                    media_type="text/plain"
                )
            
            # 2. Exemption pour certains endpoints
            if request.url.path in self.exempt_endpoints:
                response = await call_next(request)
                response = self._add_security_headers(response)
                return response
            
            # 3. Validation ultra-sécurisée de la requête
            try:
                validation_result = await self.security_manager.validate_request(request)
            except Exception as validation_error:
                logger.error(f"❌ [SECURITY_MW] Erreur validation: {validation_error}")
                return Response(
                    content="Erreur de validation sécurité",
                    status_code=500,
                    media_type="text/plain"
                )
            
            # 4. Blocage si requête malveillante
            if not validation_result.get('allowed', False):
                blocked_reasons = validation_result.get('blocked_reasons', [])
                threat_score = validation_result.get('threat_score', 0)
                
                logger.warning(
                    f"🚫 [SECURITY_MW] Requête bloquée de {request.client.host} "
                    f"- Score: {threat_score:.2f} - Raisons: {', '.join(blocked_reasons)}"
                )
                
                # Réponse générique pour éviter l'information leakage
                return Response(
                    content="Accès refusé",
                    status_code=403,
                    media_type="text/plain"
                )
            
            # 5. Log des requêtes suspectes (score élevé mais non bloquées)
            threat_score = validation_result.get('threat_score', 0)
            if threat_score > 5.0:
                security_flags = validation_result.get('security_flags', [])
                logger.warning(
                    f"⚠️ [SECURITY_MW] Requête suspecte de {request.client.host} "
                    f"- Score: {threat_score:.2f} - Flags: {', '.join(security_flags)}"
                )
            
            # 6. Ajout du contexte de sécurité à la requête
            request.state.security_validation = validation_result
            request.state.security_processed = True
            
            # 7. Traitement de la requête
            response = await call_next(request)
            
            # 8. Ajout des headers de sécurité OWASP 2025
            response = self._add_security_headers(response)
            
            # 9. Log de performance sécurisée
            duration = time.perf_counter() - start_time
            if duration > 1.0:  # Plus d'1 seconde
                logger.warning(
                    f"⏱️ [SECURITY_MW] Requête lente ({duration:.3f}s) de {request.client.host} "
                    f"vers {request.url.path}"
                )
            
            return response
            
        except HTTPException as http_exc:
            # Re-raise des HTTPException (normal flow)
            raise http_exc
            
        except Exception as e:
            # Erreur inattendue - log et réponse sécurisée
            logger.error(
                f"❌ [SECURITY_MW] Erreur critique dans middleware: {e} "
                f"- IP: {request.client.host} - Path: {request.url.path}"
            )
            
            # Réponse générique sans révéler d'informations
            return Response(
                content="Erreur interne du serveur",
                status_code=500,
                media_type="text/plain"
            )
    
    def _add_security_headers(self, response: Response) -> Response:
        """Ajout des headers de sécurité OWASP 2025"""
        try:
            if self.security_manager:
                security_headers = self.security_manager.get_security_headers()
                
                for header_name, header_value in security_headers.items():
                    response.headers[header_name] = header_value
            
            # Headers additionnels spécifiques à Jarvis
            response.headers['X-Jarvis-Security'] = 'Ultra-Secured-2025'
            response.headers['X-Request-ID'] = getattr(response, 'request_id', 'unknown')
            
        except Exception as e:
            logger.error(f"❌ [SECURITY_MW] Erreur ajout headers: {e}")
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware de rate limiting spécialisé avec fenêtre glissante
    """
    
    def __init__(self, app, redis_client=None):
        super().__init__(app)
        self.redis_client = redis_client
        
        # Configuration rate limiting
        self.rate_config = {
            'default_limit': 60,      # 60 req/min par défaut
            'burst_limit': 20,        # 20 req/10s max
            'auth_limit': 5,          # 5 tentatives auth/min
            'sensitive_limit': 10     # 10 req/min pour endpoints sensibles
        }
        
        # Endpoints sensibles avec limites strictes
        self.sensitive_endpoints = {
            '/chat': self.rate_config['sensitive_limit'],
            '/voice': self.rate_config['sensitive_limit'],
            '/auth': self.rate_config['auth_limit']
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Application du rate limiting par IP et endpoint"""
        try:
            client_ip = request.client.host
            endpoint = request.url.path
            current_time = time.time()
            
            # Détermination de la limite selon l'endpoint
            rate_limit = self._get_rate_limit_for_endpoint(endpoint)
            
            # Vérification rate limiting
            if await self._is_rate_limited(client_ip, endpoint, rate_limit):
                logger.warning(
                    f"🚫 [RATE_LIMIT] Limite dépassée pour {client_ip} "
                    f"sur {endpoint} (limite: {rate_limit}/min)"
                )
                
                return Response(
                    content="Limite de requêtes dépassée. Veuillez patienter.",
                    status_code=429,
                    media_type="text/plain",
                    headers={
                        'Retry-After': '60',
                        'X-RateLimit-Limit': str(rate_limit),
                        'X-RateLimit-Remaining': '0',
                        'X-RateLimit-Reset': str(int(current_time + 60))
                    }
                )
            
            # Traitement de la requête
            response = await call_next(request)
            
            # Ajout headers rate limiting
            remaining = await self._get_remaining_requests(client_ip, endpoint, rate_limit)
            response.headers['X-RateLimit-Limit'] = str(rate_limit)
            response.headers['X-RateLimit-Remaining'] = str(remaining)
            response.headers['X-RateLimit-Reset'] = str(int(current_time + 60))
            
            return response
            
        except Exception as e:
            logger.error(f"❌ [RATE_LIMIT] Erreur middleware: {e}")
            # En cas d'erreur, laisser passer la requête
            return await call_next(request)
    
    def _get_rate_limit_for_endpoint(self, endpoint: str) -> int:
        """Détermine la limite de rate pour un endpoint"""
        # Vérification endpoints sensibles
        for sensitive_path, limit in self.sensitive_endpoints.items():
            if endpoint.startswith(sensitive_path):
                return limit
        
        return self.rate_config['default_limit']
    
    async def _is_rate_limited(self, ip: str, endpoint: str, limit: int) -> bool:
        """Vérification si l'IP est rate limitée"""
        try:
            if not self.redis_client:
                return False
            
            current_minute = int(time.time() // 60)
            rate_key = f"rate:{ip}:{endpoint}:{current_minute}"
            
            # Incrémenter et vérifier compteur
            current_count = await self.redis_client.incr(rate_key)
            await self.redis_client.expire(rate_key, 60)
            
            return current_count > limit
            
        except Exception as e:
            logger.error(f"❌ [RATE_LIMIT] Erreur vérification: {e}")
            return False
    
    async def _get_remaining_requests(self, ip: str, endpoint: str, limit: int) -> int:
        """Calcule les requêtes restantes"""
        try:
            if not self.redis_client:
                return limit
            
            current_minute = int(time.time() // 60)
            rate_key = f"rate:{ip}:{endpoint}:{current_minute}"
            
            current_count = await self.redis_client.get(rate_key) or "0"
            remaining = max(0, limit - int(current_count))
            
            return remaining
            
        except Exception as e:
            logger.error(f"❌ [RATE_LIMIT] Erreur calcul remaining: {e}")
            return 0

class CORSSecurityMiddleware(BaseHTTPMiddleware):
    """
    Middleware CORS ultra-sécurisé avec validation stricte des origins
    """
    
    def __init__(self, app, allowed_origins=None):
        super().__init__(app)
        self.allowed_origins = set(allowed_origins or ['http://localhost:3000'])
        
        # Headers CORS sécurisés
        self.cors_headers = {
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Max-Age': '86400',  # 24h cache
            'Access-Control-Allow-Headers': (
                'Accept, Accept-Language, Content-Language, Content-Type, '
                'Authorization, X-Requested-With, X-Request-ID'
            ),
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Vary': 'Origin'
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Traitement CORS ultra-sécurisé"""
        try:
            origin = request.headers.get('origin', '')
            
            # Validation stricte de l'origin
            if origin and not self._is_origin_allowed(origin):
                logger.warning(f"🚫 [CORS] Origin non autorisé: {origin}")
                return Response(
                    content="Origin non autorisé",
                    status_code=403,
                    media_type="text/plain"
                )
            
            # Traitement requête OPTIONS (preflight)
            if request.method == 'OPTIONS':
                return self._handle_preflight(origin)
            
            # Traitement requête normale
            response = await call_next(request)
            
            # Ajout headers CORS si origin valide
            if origin and self._is_origin_allowed(origin):
                response.headers['Access-Control-Allow-Origin'] = origin
                for header_name, header_value in self.cors_headers.items():
                    response.headers[header_name] = header_value
            
            return response
            
        except Exception as e:
            logger.error(f"❌ [CORS] Erreur middleware: {e}")
            return await call_next(request)
    
    def _is_origin_allowed(self, origin: str) -> bool:
        """Validation stricte de l'origin"""
        if not origin:
            return False
        
        # Vérification exacte des origins autorisés
        if origin in self.allowed_origins:
            return True
        
        # Pattern pour développement local
        if origin.startswith('http://localhost:') or origin.startswith('http://127.0.0.1:'):
            port = origin.split(':')[-1]
            if port.isdigit() and 3000 <= int(port) <= 3010:
                return True
        
        return False
    
    def _handle_preflight(self, origin: str) -> Response:
        """Gestion des requêtes preflight OPTIONS"""
        if origin and self._is_origin_allowed(origin):
            headers = {
                'Access-Control-Allow-Origin': origin,
                **self.cors_headers
            }
            
            return Response(
                content="",
                status_code=200,
                headers=headers
            )
        else:
            return Response(
                content="Origin non autorisé pour preflight",
                status_code=403,
                media_type="text/plain"
            )