"""Service Weather - wrapper pour weather_service"""
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class WeatherService:
    """Service centralisé pour les informations météo"""
    
    def __init__(self, settings):
        self.settings = settings
        self.weather_service = None
        
    async def initialize(self):
        """Initialise le service météo"""
        try:
            # Import dynamique pour éviter dépendance au démarrage
            from services.weather_service import WeatherService as WeatherServiceCore
            
            self.weather_service = WeatherServiceCore(api_key=self.settings.openweather_api_key)
            
            if self.settings.openweather_api_key:
                logger.info("🌤️ [WEATHER] Service météo initialisé avec OpenWeatherMap")
            else:
                logger.info("🌤️ [WEATHER] Service météo initialisé (fallback public)")
            
        except Exception as e:
            logger.error(f"❌ [WEATHER] Erreur initialisation: {e}")
    
    def is_available(self) -> bool:
        """Vérifie si le service Weather est disponible"""
        return self.weather_service is not None
    
    async def get_weather(self, city: str = "Perpignan") -> Optional[Dict[str, Any]]:
        """
        Récupère les informations météo pour une ville
        Wrapper pour weather_service.get_weather()
        """
        try:
            if not self.is_available():
                logger.warning("⚠️ [WEATHER] Service météo non disponible")
                return None
            
            logger.debug(f"🌤️ [WEATHER] Récupération météo pour {city}")
            weather_data = await self.weather_service.get_weather(city)
            
            if weather_data:
                logger.info(f"✅ [WEATHER] Données météo récupérées pour {city}")
                return weather_data
            else:
                logger.warning(f"⚠️ [WEATHER] Aucune donnée météo pour {city}")
                return None
                
        except Exception as e:
            logger.error(f"❌ [WEATHER] Erreur récupération météo: {e}")
            return None
    
    def format_weather_info(
        self, 
        weather_data: Optional[Dict[str, Any]], 
        city: str = "Perpignan"
    ) -> str:
        """
        Formate les données météo pour inclusion dans le prompt LLM
        Extrait de main.py:581
        """
        if not weather_data or not self.is_available():
            return ""
        
        try:
            formatted_info = self.weather_service.format_weather_response(weather_data)
            return f"\\nMÉTÉO ACTUELLE POUR {city.upper()} :\\n{formatted_info}\\n"
        except Exception as e:
            logger.error(f"❌ [WEATHER] Erreur formatage météo: {e}")
            return ""
    
    def detect_weather_request(self, message: str) -> bool:
        """
        Détecte si un message contient une demande météo
        Extrait de main.py:567-568
        """
        weather_keywords = [
            "météo", "meteo", "temps qu'il fait", "température", 
            "pluie", "soleil", "climat", "temps", "°c", "degré"
        ]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in weather_keywords)
    
    def extract_city(self, message: str) -> str:
        """
        Extrait la ville mentionnée dans le message
        Extrait de main.py:573-578
        """
        message_lower = message.lower()
        
        if "rivesaltes" in message_lower or "rivesalte" in message_lower:
            return "Rivesaltes"
        elif "perpignan" in message_lower:
            return "Perpignan"
        else:
            return "Perpignan"  # Par défaut
