"""Service Home Assistant - wrapper pour home_assistant integration"""
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class HomeAssistantService:
    """Service centralisé pour l'intégration Home Assistant"""
    
    def __init__(self, settings):
        self.settings = settings
        self.home_assistant = None
        
    async def initialize(self):
        """Initialise l'intégration Home Assistant"""
        try:
            # Import dynamique pour éviter dépendance au démarrage
            from integration.home_assistant import HomeAssistantIntegration
            
            self.home_assistant = HomeAssistantIntegration(self.settings)
            
            if hasattr(self.home_assistant, 'connect'):
                logger.info("🏠 [HA] Connexion Home Assistant...")
                await self.home_assistant.connect()
                logger.info("✅ [HA] Home Assistant connecté")
            else:
                logger.info("ℹ️ [HA] Home Assistant initialisé (pas de méthode connect)")
                
        except Exception as e:
            logger.error(f"❌ [HA] Erreur initialisation: {e}")
    
    async def close(self):
        """Ferme proprement la connexion Home Assistant"""
        if self.home_assistant and hasattr(self.home_assistant, 'disconnect'):
            try:
                await self.home_assistant.disconnect()
                logger.info("✅ [HA] Home Assistant déconnecté")
            except Exception as e:
                logger.error(f"❌ [HA] Erreur déconnexion: {e}")
        else:
            logger.info("ℹ️ [HA] Pas de déconnexion nécessaire")
    
    def is_available(self) -> bool:
        """Vérifie si le service Home Assistant est disponible"""
        return self.home_assistant is not None
    
    async def call_service(
        self, 
        domain: str, 
        service: str, 
        entity_id: Optional[str] = None,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        Appelle un service Home Assistant
        """
        try:
            if not self.is_available():
                logger.warning("⚠️ [HA] Service Home Assistant non disponible")
                return None
            
            # Cette méthode devra être implémentée selon l'API HomeAssistantIntegration
            logger.info(f"🏠 [HA] Appel service {domain}.{service}")
            
            # Placeholder - à adapter selon l'API réelle de HomeAssistantIntegration
            result = await self.home_assistant.call_service(domain, service, entity_id, **kwargs)
            
            if result:
                logger.info(f"✅ [HA] Service {domain}.{service} appelé avec succès")
                return result
            else:
                logger.warning(f"⚠️ [HA] Échec appel service {domain}.{service}")
                return None
                
        except Exception as e:
            logger.error(f"❌ [HA] Erreur appel service {domain}.{service}: {e}")
            return None
    
    async def get_state(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère l'état d'une entité Home Assistant
        """
        try:
            if not self.is_available():
                logger.warning("⚠️ [HA] Service Home Assistant non disponible")
                return None
            
            # Cette méthode devra être implémentée selon l'API HomeAssistantIntegration
            logger.debug(f"🏠 [HA] Récupération état {entity_id}")
            
            # Placeholder - à adapter selon l'API réelle
            state = await self.home_assistant.get_state(entity_id)
            
            if state:
                logger.debug(f"✅ [HA] État {entity_id} récupéré")
                return state
            else:
                logger.warning(f"⚠️ [HA] État {entity_id} introuvable")
                return None
                
        except Exception as e:
            logger.error(f"❌ [HA] Erreur récupération état {entity_id}: {e}")
            return None