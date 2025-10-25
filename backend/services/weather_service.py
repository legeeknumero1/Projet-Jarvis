import asyncio
import logging
import httpx
from typing import Dict, Any, Optional
from datetime import datetime

class WeatherService:
    def __init__(self, api_key: Optional[str] = None):
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)
        
    async def get_weather(self, city: str = "Perpignan", country: str = "FR") -> Dict[str, Any]:
        """Récupère la météo pour une ville via internet"""
        try:
            # Essayer d'abord avec API gratuite wttr.in
            async with httpx.AsyncClient() as client:
                url = f"https://wttr.in/{city}?format=j1"
                headers = {"User-Agent": "Jarvis/1.0"}
                
                try:
                    response = await client.get(url, headers=headers, timeout=10.0)
                    
                    if response.status_code == 200:
                        data = response.json()
                        current_condition = data["current_condition"][0]
                        
                        weather_data = {
                            "city": city,
                            "country": country,
                            "temperature": int(current_condition["temp_C"]),
                            "description": current_condition["weatherDesc"][0]["value"],
                            "humidity": int(current_condition["humidity"]),
                            "wind_speed": int(float(current_condition["windspeedKmph"])),
                            "wind_direction": current_condition["winddir16Point"],
                            "pressure": int(current_condition["pressure"]),
                            "timestamp": datetime.now().isoformat(),
                            "source": "wttr.in"
                        }
                        
                        self.logger.info(f"🌤️ [WEATHER] Météo récupérée via internet pour {city}: {weather_data['temperature']}°C")
                        return weather_data
                        
                except Exception as e:
                    self.logger.warning(f"⚠️ [WEATHER] Erreur API wttr.in: {e}")
            
            # Si API OpenWeatherMap disponible, tenter fallback
            if self.api_key:
                api_result = await self.get_weather_with_api(city, self.api_key)
                if api_result:
                    return api_result
            
            # Fallback : retourner erreur au lieu de données hardcodées
            return {
                "error": f"Impossible de récupérer la météo pour {city}",
                "city": city,
                "timestamp": datetime.now().isoformat(),
                "source": "error"
            }
            
        except Exception as e:
            self.logger.error(f"❌ [WEATHER] Erreur récupération météo: {e}")
            return {
                "error": "Impossible de récupérer la météo",
                "city": city,
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_weather_with_api(self, city: str, api_key: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Récupère la météo via API OpenWeatherMap (si clé disponible)"""
        if api_key is None:
            api_key = self.api_key
        if not api_key:
            return None
            
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}/weather"
                params = {
                    "q": f"{city},FR",
                    "appid": api_key,
                    "units": "metric",
                    "lang": "fr"
                }
                
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "city": data["name"],
                        "country": "France",
                        "temperature": round(data["main"]["temp"]),
                        "description": data["weather"][0]["description"],
                        "humidity": data["main"]["humidity"],
                        "wind_speed": round(data["wind"]["speed"] * 3.6),  # m/s vers km/h
                        "pressure": data["main"]["pressure"],
                        "timestamp": datetime.now().isoformat(),
                        "source": "openweathermap"
                    }
                else:
                    self.logger.error(f"❌ [WEATHER] API error: {response.status_code}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"❌ [WEATHER] Erreur API: {e}")
            return None
    
    def format_weather_response(self, weather_data: Dict[str, Any]) -> str:
        """Formate la réponse météo en français naturel"""
        if "error" in weather_data:
            return f"Désolé, je n'ai pas pu récupérer la météo pour {weather_data['city']}."
        
        city = weather_data.get("city", "votre ville")
        temp = weather_data.get("temperature", "N/A")
        desc = weather_data.get("description", "conditions inconnues")
        humidity = weather_data.get("humidity", "N/A")
        wind = weather_data.get("wind_speed", "N/A")
        
        response = f"🌤️ Météo à {city} :\n"
        response += f"• Température : {temp}°C\n"
        response += f"• Conditions : {desc}\n"
        response += f"• Humidité : {humidity}%\n"
        response += f"• Vent : {wind} km/h"
        
        return response
