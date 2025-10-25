#!/usr/bin/env python3
"""
Ollama Load Balancer - Jarvis v1.3.2
Load balancer intelligent pour instances Ollama multiples
Optimisé pour performance et haute disponibilité selon standards 2025
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import httpx
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import StreamingResponse
import uvicorn
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import PlainTextResponse

# Configuration logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Métriques Prometheus
REQUEST_COUNT = Counter('ollama_lb_requests_total', 'Total requests to load balancer', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('ollama_lb_request_duration_seconds', 'Request duration', ['upstream'])
UPSTREAM_STATUS = Gauge('ollama_lb_upstream_status', 'Upstream server status (1=healthy, 0=unhealthy)', ['upstream'])
ACTIVE_CONNECTIONS = Gauge('ollama_lb_active_connections', 'Active connections per upstream', ['upstream'])
QUEUE_SIZE = Gauge('ollama_lb_queue_size', 'Queue size per upstream', ['upstream'])

class LoadBalancingStrategy(Enum):
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_RESPONSE_TIME = "weighted_response_time"
    QUEUE_LENGTH = "queue_length"

@dataclass
class UpstreamServer:
    """Représente un serveur Ollama upstream"""
    name: str
    url: str
    weight: float = 1.0
    is_healthy: bool = True
    last_health_check: datetime = field(default_factory=datetime.now)
    response_times: List[float] = field(default_factory=list)
    active_connections: int = 0
    queue_size: int = 0
    total_requests: int = 0
    failed_requests: int = 0
    
    @property
    def avg_response_time(self) -> float:
        """Temps de réponse moyen sur les 10 dernières requêtes"""
        if not self.response_times:
            return 0.0
        return sum(self.response_times[-10:]) / min(len(self.response_times), 10)
    
    @property
    def health_score(self) -> float:
        """Score de santé combiné (0-1)"""
        if not self.is_healthy:
            return 0.0
        
        # Facteurs: temps de réponse, connexions actives, taux d'erreur
        time_score = max(0, 1 - (self.avg_response_time / 10.0))  # Pénalité après 10s
        conn_score = max(0, 1 - (self.active_connections / 50.0))  # Pénalité après 50 connexions
        
        error_rate = self.failed_requests / max(self.total_requests, 1)
        error_score = max(0, 1 - error_rate)
        
        return (time_score + conn_score + error_score) / 3
    
    def add_response_time(self, duration: float):
        """Ajouter un temps de réponse"""
        self.response_times.append(duration)
        if len(self.response_times) > 50:  # Garder seulement les 50 derniers
            self.response_times = self.response_times[-50:]

class OllamaLoadBalancer:
    """Load Balancer intelligent pour Ollama"""
    
    def __init__(self):
        # Configuration depuis variables d'environnement
        self.strategy = LoadBalancingStrategy(
            os.getenv('LOAD_BALANCING_STRATEGY', 'least_connections')
        )
        self.health_check_interval = int(os.getenv('HEALTH_CHECK_INTERVAL', '10'))
        
        # Initialiser les serveurs upstream
        self.upstreams = self._init_upstreams()
        self.round_robin_index = 0
        
        # Client HTTP réutilisable
        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, read=300.0),  # Timeout long pour génération
            limits=httpx.Limits(max_keepalive_connections=20)
        )
        
        # Statistiques
        self.start_time = time.time()
        
        logger.info(f"🎯 [LB] Ollama Load Balancer initialisé")
        logger.info(f"📊 [LB] Stratégie: {self.strategy.value}")
        logger.info(f"🖥️ [LB] Upstreams: {[u.name for u in self.upstreams]}")
    
    def _init_upstreams(self) -> List[UpstreamServer]:
        """Initialiser les serveurs upstream depuis l'environnement"""
        upstreams = []
        
        # Lire les upstreams depuis les variables d'environnement
        for i in range(1, 10):  # Support jusqu'à 9 upstreams
            url_env = f'OLLAMA_UPSTREAM_{i}'
            weight_env = f'OLLAMA_UPSTREAM_{i}_WEIGHT'
            
            if url_env in os.environ:
                url = f"http://{os.environ[url_env]}"
                weight = float(os.environ.get(weight_env, '1.0'))
                name = f"ollama-{i}"
                
                upstreams.append(UpstreamServer(
                    name=name,
                    url=url,
                    weight=weight
                ))
                logger.info(f"✅ [LB] Upstream ajouté: {name} -> {url} (weight: {weight})")
        
        if not upstreams:
            # Configuration par défaut
            upstreams = [
                UpstreamServer("ollama-1", "http://ollama-1:11434", 1.0),
                UpstreamServer("ollama-2", "http://ollama-2:11434", 1.0)
            ]
            logger.warning("⚠️ [LB] Aucun upstream configuré, utilisation configuration par défaut")
        
        return upstreams
    
    async def health_check_loop(self):
        """Boucle de health check des upstreams"""
        while True:
            try:
                await self._check_all_upstreams_health()
                await asyncio.sleep(self.health_check_interval)
            except Exception as e:
                logger.error(f"❌ [HEALTH] Erreur health check loop: {e}")
                await asyncio.sleep(5)
    
    async def _check_all_upstreams_health(self):
        """Vérifier la santé de tous les upstreams"""
        tasks = [self._check_upstream_health(upstream) for upstream in self.upstreams]
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _check_upstream_health(self, upstream: UpstreamServer):
        """Vérifier la santé d'un upstream spécifique"""
        try:
            start_time = time.time()
            
            # Test simple avec /api/tags
            response = await self.http_client.get(
                f"{upstream.url}/api/tags",
                timeout=10.0
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                upstream.is_healthy = True
                upstream.add_response_time(duration)
                UPSTREAM_STATUS.labels(upstream=upstream.name).set(1)
                
                logger.debug(f"✅ [HEALTH] {upstream.name} healthy ({duration:.2f}s)")
            else:
                upstream.is_healthy = False
                UPSTREAM_STATUS.labels(upstream=upstream.name).set(0)
                logger.warning(f"⚠️ [HEALTH] {upstream.name} unhealthy: HTTP {response.status_code}")
                
        except Exception as e:
            upstream.is_healthy = False
            UPSTREAM_STATUS.labels(upstream=upstream.name).set(0)
            logger.warning(f"❌ [HEALTH] {upstream.name} check failed: {e}")
        
        upstream.last_health_check = datetime.now()
    
    def select_upstream(self) -> Optional[UpstreamServer]:
        """Sélectionner le meilleur upstream selon la stratégie"""
        healthy_upstreams = [u for u in self.upstreams if u.is_healthy]
        
        if not healthy_upstreams:
            logger.error("❌ [LB] Aucun upstream sain disponible")
            return None
        
        if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return self._round_robin_select(healthy_upstreams)
        elif self.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return min(healthy_upstreams, key=lambda u: u.active_connections)
        elif self.strategy == LoadBalancingStrategy.WEIGHTED_RESPONSE_TIME:
            return self._weighted_response_time_select(healthy_upstreams)
        elif self.strategy == LoadBalancingStrategy.QUEUE_LENGTH:
            return min(healthy_upstreams, key=lambda u: u.queue_size)
        else:
            return healthy_upstreams[0]  # Fallback
    
    def _round_robin_select(self, upstreams: List[UpstreamServer]) -> UpstreamServer:
        """Sélection round-robin"""
        upstream = upstreams[self.round_robin_index % len(upstreams)]
        self.round_robin_index += 1
        return upstream
    
    def _weighted_response_time_select(self, upstreams: List[UpstreamServer]) -> UpstreamServer:
        """Sélection pondérée par temps de réponse et score de santé"""
        # Utiliser le score de santé combiné
        return max(upstreams, key=lambda u: u.health_score * u.weight)
    
    async def proxy_request(self, method: str, path: str, request: Request) -> Response:
        """Proxier une requête vers un upstream"""
        upstream = self.select_upstream()
        if not upstream:
            raise HTTPException(status_code=503, detail="Aucun upstream disponible")
        
        upstream.active_connections += 1
        upstream.total_requests += 1
        
        ACTIVE_CONNECTIONS.labels(upstream=upstream.name).set(upstream.active_connections)
        REQUEST_COUNT.labels(method=method, endpoint=path).inc()
        
        start_time = time.time()
        
        try:
            # Construire l'URL complète
            url = f"{upstream.url}{path}"
            
            # Copier headers (filtrer les headers sensibles)
            headers = dict(request.headers)
            headers.pop('host', None)
            headers.pop('content-length', None)
            
            # Lire le body si présent
            body = None
            if method in ['POST', 'PUT', 'PATCH']:
                body = await request.body()
            
            # Faire la requête
            response = await self.http_client.request(
                method=method,
                url=url,
                headers=headers,
                content=body,
                params=dict(request.query_params)
            )
            
            duration = time.time() - start_time
            upstream.add_response_time(duration)
            REQUEST_DURATION.labels(upstream=upstream.name).observe(duration)
            
            logger.info(f"🎯 [PROXY] {method} {path} -> {upstream.name} ({duration:.2f}s, {response.status_code})")
            
            # Retourner la réponse
            response_headers = dict(response.headers)
            response_headers.pop('content-length', None)  # FastAPI le recalculera
            
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=response_headers
            )
            
        except Exception as e:
            duration = time.time() - start_time
            upstream.failed_requests += 1
            
            logger.error(f"❌ [PROXY] Erreur {method} {path} -> {upstream.name}: {e}")
            raise HTTPException(status_code=502, detail=f"Erreur upstream: {str(e)}")
            
        finally:
            upstream.active_connections -= 1
            ACTIVE_CONNECTIONS.labels(upstream=upstream.name).set(upstream.active_connections)
    
    async def proxy_streaming_request(self, method: str, path: str, request: Request):
        """Proxier une requête streaming vers un upstream"""
        upstream = self.select_upstream()
        if not upstream:
            raise HTTPException(status_code=503, detail="Aucun upstream disponible")
        
        upstream.active_connections += 1
        upstream.total_requests += 1
        upstream.queue_size += 1
        
        ACTIVE_CONNECTIONS.labels(upstream=upstream.name).set(upstream.active_connections)
        QUEUE_SIZE.labels(upstream=upstream.name).set(upstream.queue_size)
        
        start_time = time.time()
        
        try:
            url = f"{upstream.url}{path}"
            
            headers = dict(request.headers)
            headers.pop('host', None)
            headers.pop('content-length', None)
            
            body = await request.body() if method in ['POST', 'PUT', 'PATCH'] else None
            
            async def stream_response():
                try:
                    async with self.http_client.stream(
                        method=method,
                        url=url,
                        headers=headers,
                        content=body,
                        params=dict(request.query_params)
                    ) as response:
                        async for chunk in response.aiter_bytes():
                            yield chunk
                except Exception as e:
                    logger.error(f"❌ [STREAM] Erreur streaming {upstream.name}: {e}")
                    yield b""
            
            duration = time.time() - start_time
            upstream.add_response_time(duration)
            REQUEST_DURATION.labels(upstream=upstream.name).observe(duration)
            
            logger.info(f"🌊 [STREAM] {method} {path} -> {upstream.name}")
            
            return StreamingResponse(
                stream_response(),
                media_type="application/x-ndjson"
            )
            
        except Exception as e:
            upstream.failed_requests += 1
            logger.error(f"❌ [STREAM] Erreur {method} {path} -> {upstream.name}: {e}")
            raise HTTPException(status_code=502, detail=f"Erreur upstream streaming: {str(e)}")
            
        finally:
            upstream.active_connections -= 1
            upstream.queue_size -= 1
            ACTIVE_CONNECTIONS.labels(upstream=upstream.name).set(upstream.active_connections)
            QUEUE_SIZE.labels(upstream=upstream.name).set(upstream.queue_size)

# Initialiser le load balancer
lb = OllamaLoadBalancer()

# Application FastAPI
app = FastAPI(
    title="Ollama Load Balancer",
    description="Load balancer intelligent pour instances Ollama multiples",
    version="1.3.2"
)

@app.on_event("startup")
async def startup_event():
    """Démarrer les tâches de background"""
    # Lancer le health check loop
    asyncio.create_task(lb.health_check_loop())
    logger.info("🚀 [LB] Load balancer démarré")

@app.on_event("shutdown")
async def shutdown_event():
    """Nettoyer à l'arrêt"""
    await lb.http_client.aclose()
    logger.info("🛑 [LB] Load balancer arrêté")

@app.get("/health")
async def health_check():
    """Health check du load balancer"""
    healthy_upstreams = [u for u in lb.upstreams if u.is_healthy]
    
    return {
        "status": "healthy" if healthy_upstreams else "unhealthy",
        "upstreams": {
            u.name: {
                "healthy": u.is_healthy,
                "url": u.url,
                "active_connections": u.active_connections,
                "avg_response_time": u.avg_response_time,
                "health_score": u.health_score
            }
            for u in lb.upstreams
        },
        "strategy": lb.strategy.value,
        "total_upstreams": len(lb.upstreams),
        "healthy_upstreams": len(healthy_upstreams)
    }

@app.get("/metrics")
async def metrics():
    """Métriques Prometheus"""
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/stats")
async def stats():
    """Statistiques détaillées"""
    return {
        "load_balancer": {
            "strategy": lb.strategy.value,
            "uptime": time.time() - lb.start_time,
            "total_upstreams": len(lb.upstreams)
        },
        "upstreams": [
            {
                "name": u.name,
                "url": u.url,
                "healthy": u.is_healthy,
                "weight": u.weight,
                "active_connections": u.active_connections,
                "queue_size": u.queue_size,
                "total_requests": u.total_requests,
                "failed_requests": u.failed_requests,
                "avg_response_time": u.avg_response_time,
                "health_score": u.health_score,
                "last_health_check": u.last_health_check.isoformat()
            }
            for u in lb.upstreams
        ]
    }

# Proxier toutes les requêtes API Ollama
@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_api(path: str, request: Request):
    """Proxier les requêtes API Ollama"""
    full_path = f"/api/{path}"
    
    # Détecter les requêtes streaming
    if path in ["generate", "chat"] and request.method == "POST":
        try:
            body = await request.json()
            if body.get("stream", False):
                return await lb.proxy_streaming_request(request.method, full_path, request)
        except:
            pass  # Fallback vers requête normale
    
    return await lb.proxy_request(request.method, full_path, request)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=11434,
        log_level="info",
        access_log=True
    )