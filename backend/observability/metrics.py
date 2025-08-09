"""Métriques Prometheus personnalisées pour Jarvis"""
from prometheus_client import Counter, Gauge, Histogram, Info

# =============================================================================
# Métriques WebSocket
# =============================================================================

ws_connections = Gauge(
    'ws_active_connections', 
    'Nombre de connexions WebSocket actives'
)

ws_connections_total = Counter(
    'ws_connections_total',
    'Total des connexions WebSocket créées',
    ['status']  # success, refused_draining, error
)

ws_messages = Counter(
    'ws_messages_total',
    'Messages WebSocket traités',
    ['direction', 'status']  # direction: in/out, status: success/error/timeout
)

# =============================================================================
# Métriques Chat/LLM
# =============================================================================

chat_requests = Counter(
    'chat_requests_total',
    'Requêtes de chat totales',
    ['secure', 'status']  # secure: true/false, status: success/error/rate_limited
)

chat_errors = Counter(
    'chat_errors_total',
    'Erreurs de chat par étape',
    ['stage']  # recv, validation, memory, llm, send
)

llm_latency = Histogram(
    'llm_generate_seconds',
    'Latence de génération LLM (secondes)',
    buckets=(0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0)
)

memory_operations = Counter(
    'memory_operations_total',
    'Opérations de mémoire neuromorphique',
    ['operation', 'status']  # operation: get_context/store_interaction, status: success/error
)

# =============================================================================
# Métriques Services Externes  
# =============================================================================

service_health = Gauge(
    'service_health_status',
    'Status de santé des services externes (1=healthy, 0=unhealthy)',
    ['service']  # ollama, voice_stt, voice_tts, home_assistant, memory
)

service_response_time = Histogram(
    'service_response_seconds',
    'Temps de réponse des services externes',
    ['service'],
    buckets=(0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0)
)

# =============================================================================
# Métriques Rate Limiting
# =============================================================================

rate_limit_hits = Counter(
    'rate_limit_hits_total',
    'Nombre de fois où le rate limiting a été déclenché',
    ['endpoint', 'client_type']  # endpoint: chat/ws, client_type: api/browser
)

# =============================================================================
# Informations système
# =============================================================================

jarvis_info = Info(
    'jarvis_build_info',
    'Informations de build Jarvis'
)

# Initialiser les infos système
jarvis_info.info({
    'version': '1.3.0-hardened',
    'architecture': 'modular',
    'python_version': '3.11+',
    'environment': 'production'
})

# =============================================================================
# Helpers pour mise à jour des métriques
# =============================================================================

def update_service_health(service_name: str, is_healthy: bool):
    """Met à jour le status de santé d'un service"""
    service_health.labels(service=service_name).set(1 if is_healthy else 0)

def record_chat_request(is_secure: bool, status: str):
    """Enregistre une requête de chat"""
    chat_requests.labels(secure=str(is_secure).lower(), status=status).inc()

def record_ws_connection(status: str):
    """Enregistre une connexion WebSocket"""
    ws_connections_total.labels(status=status).inc()

def record_rate_limit_hit(endpoint: str, client_type: str = "api"):
    """Enregistre un hit de rate limiting"""
    rate_limit_hits.labels(endpoint=endpoint, client_type=client_type).inc()