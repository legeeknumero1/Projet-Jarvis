"""Manager centralisé pour connexions WebSocket avec métriques"""
from typing import Set
from fastapi import WebSocket
import logging

logger = logging.getLogger(__name__)

# Import métriques Prometheus
try:
    from ..observability.metrics import ws_connections, record_ws_connection
    PROMETHEUS_AVAILABLE = True
except ImportError:
    # Fallback si prometheus_client pas installé
    ws_connections = None
    PROMETHEUS_AVAILABLE = False
    def record_ws_connection(*args, **kwargs):
        pass

class WSManager:
    """
    Gestionnaire centralisé des connexions WebSocket
    - Registre des connexions actives
    - Fermeture graceful en batch
    - Métriques intégrées
    """
    
    def __init__(self):
        self._connections: Set[WebSocket] = set()
        self._total_connections = 0
        self._closed_connections = 0
    
    def __len__(self) -> int:
        """Nombre de connexions actives"""
        return len(self._connections)
    
    @property
    def active_count(self) -> int:
        """Alias pour compatibilité métriques"""
        return len(self._connections)
    
    @property
    def total_connections(self) -> int:
        """Total connexions depuis démarrage"""
        return self._total_connections
    
    @property
    def closed_connections(self) -> int:
        """Total connexions fermées"""
        return self._closed_connections
    
    async def register(self, websocket: WebSocket) -> None:
        """Enregistre une nouvelle connexion"""
        self._connections.add(websocket)
        self._total_connections += 1
        
        # Mise à jour métriques Prometheus - INC gauge
        if PROMETHEUS_AVAILABLE and ws_connections:
            ws_connections.inc()
        record_ws_connection("success")
        
        logger.info(f"📊 [WS_MGR] Connexion enregistrée - Actives: {len(self._connections)}")
    
    async def unregister(self, websocket: WebSocket) -> None:
        """Désenregistre une connexion"""
        if websocket in self._connections:
            self._connections.discard(websocket)
            self._closed_connections += 1
            
            # Mise à jour métriques Prometheus - DEC gauge
            if PROMETHEUS_AVAILABLE and ws_connections:
                ws_connections.dec()
            
            logger.info(f"📊 [WS_MGR] Connexion désenregistrée - Actives: {len(self._connections)}")
    
    async def close_all(self, code: int = 1001, reason: str = "Server shutdown") -> None:
        """
        Ferme toutes les connexions WebSocket de manière graceful
        
        Args:
            code: Code de fermeture WebSocket (1001 = Going Away)
            reason: Raison lisible de la fermeture
        """
        if not self._connections:
            logger.info("🔌 [WS_MGR] Aucune connexion à fermer")
            return
        
        logger.info(f"🔌 [WS_MGR] Fermeture de {len(self._connections)} connexions...")
        
        # Copie pour éviter modification pendant itération
        connections_to_close = list(self._connections)
        success_count = 0
        error_count = 0
        
        for websocket in connections_to_close:
            try:
                # Vérifier état avant fermeture
                if websocket.client_state != 3:  # 3 = DISCONNECTED
                    await websocket.close(code=code, reason=reason)
                    success_count += 1
            except Exception as e:
                error_count += 1
                logger.warning(f"⚠️ [WS_MGR] Erreur fermeture connexion: {e}")
        
        # Nettoyer le registre
        self._connections.clear()
        
        logger.info(f"✅ [WS_MGR] Fermeture terminée - Succès: {success_count}, Erreurs: {error_count}")
    
    def get_stats(self) -> dict:
        """Statistiques pour monitoring"""
        return {
            "active_connections": len(self._connections),
            "total_connections": self._total_connections,
            "closed_connections": self._closed_connections,
            "success_rate": (
                (self._total_connections - self._closed_connections) / max(self._total_connections, 1)
            ) * 100 if self._total_connections > 0 else 0
        }