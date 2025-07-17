import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
import httpx
import paho.mqtt.client as mqtt

class HomeAssistantIntegration:
    def __init__(self, config):
        self.config = config
        self.http_client = None
        self.mqtt_client = None
        self.logger = logging.getLogger(__name__)
    
    async def connect(self):
        try:
            # Temporairement désactivé pour éviter les erreurs de démarrage
            self.logger.info("Home Assistant integration temporairement désactivé")
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Home Assistant: {e}")
            # Ne pas faire planter l'app
            pass
    
    async def disconnect(self):
        if self.http_client:
            await self.http_client.aclose()
        
        if self.mqtt_client:
            self.mqtt_client.disconnect()
    
    async def _connect_mqtt(self):
        try:
            self.mqtt_client = mqtt.Client()
            
            if self.config.mqtt_username:
                self.mqtt_client.username_pw_set(
                    self.config.mqtt_username,
                    self.config.mqtt_password
                )
            
            # Callbacks
            self.mqtt_client.on_connect = self._on_mqtt_connect
            self.mqtt_client.on_message = self._on_mqtt_message
            self.mqtt_client.on_disconnect = self._on_mqtt_disconnect
            
            # Connexion
            await asyncio.get_event_loop().run_in_executor(
                None,
                self.mqtt_client.connect,
                self.config.mqtt_broker,
                self.config.mqtt_port,
                60
            )
            
            # Démarrer la boucle MQTT
            self.mqtt_client.loop_start()
            
        except Exception as e:
            self.logger.error(f"MQTT connection failed: {e}")
            raise
    
    def _on_mqtt_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.logger.info("MQTT connected successfully")
            # S'abonner aux topics importants
            client.subscribe("homeassistant/+/+/state")
            client.subscribe("jarvis/+/+")
        else:
            self.logger.error(f"MQTT connection failed with code {rc}")
    
    def _on_mqtt_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            payload = msg.payload.decode()
            self.logger.debug(f"MQTT message received: {topic} -> {payload}")
            
            # Traiter les messages selon le topic
            if topic.startswith("homeassistant/"):
                self._handle_homeassistant_message(topic, payload)
            elif topic.startswith("jarvis/"):
                self._handle_jarvis_message(topic, payload)
                
        except Exception as e:
            self.logger.error(f"Error processing MQTT message: {e}")
    
    def _on_mqtt_disconnect(self, client, userdata, rc):
        self.logger.warning(f"MQTT disconnected with code {rc}")
    
    async def _test_connection(self):
        try:
            if self.http_client:
                response = await self.http_client.get("/api/")
                if response.status_code == 200:
                    self.logger.info("Home Assistant HTTP API is accessible")
                else:
                    self.logger.warning(f"Home Assistant HTTP API returned {response.status_code}")
        except Exception as e:
            self.logger.warning(f"Home Assistant HTTP API test failed: {e}")
    
    async def get_states(self) -> List[Dict[str, Any]]:
        """Récupère tous les états des entités"""
        try:
            if not self.http_client:
                raise RuntimeError("HTTP client not initialized")
            
            response = await self.http_client.get("/api/states")
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            self.logger.error(f"Failed to get states: {e}")
            return []
    
    async def get_entity_state(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Récupère l'état d'une entité spécifique"""
        try:
            if not self.http_client:
                raise RuntimeError("HTTP client not initialized")
            
            response = await self.http_client.get(f"/api/states/{entity_id}")
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get entity state for {entity_id}: {e}")
            return None
    
    async def call_service(self, domain: str, service: str, entity_id: str = None, service_data: Dict[str, Any] = None) -> bool:
        """Appelle un service Home Assistant"""
        try:
            if not self.http_client:
                raise RuntimeError("HTTP client not initialized")
            
            data = service_data or {}
            if entity_id:
                data["entity_id"] = entity_id
            
            response = await self.http_client.post(
                f"/api/services/{domain}/{service}",
                json=data
            )
            
            if response.status_code == 200:
                self.logger.info(f"Service {domain}.{service} called successfully")
                return True
            else:
                self.logger.error(f"Service call failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to call service {domain}.{service}: {e}")
            return False
    
    async def turn_on(self, entity_id: str) -> bool:
        """Allume une entité"""
        domain = entity_id.split('.')[0]
        return await self.call_service(domain, "turn_on", entity_id)
    
    async def turn_off(self, entity_id: str) -> bool:
        """Éteint une entité"""
        domain = entity_id.split('.')[0]
        return await self.call_service(domain, "turn_off", entity_id)
    
    async def set_value(self, entity_id: str, value: Any) -> bool:
        """Définit une valeur pour une entité"""
        domain = entity_id.split('.')[0]
        
        if domain == "light":
            return await self.call_service("light", "turn_on", entity_id, {"brightness": value})
        elif domain == "climate":
            return await self.call_service("climate", "set_temperature", entity_id, {"temperature": value})
        elif domain == "input_number":
            return await self.call_service("input_number", "set_value", entity_id, {"value": value})
        else:
            self.logger.warning(f"Don't know how to set value for domain {domain}")
            return False
    
    def _handle_homeassistant_message(self, topic: str, payload: str):
        """Traite les messages de Home Assistant"""
        try:
            # Extraire l'entité du topic
            parts = topic.split('/')
            if len(parts) >= 3:
                entity_id = f"{parts[1]}.{parts[2]}"
                
                # Parser le payload
                data = json.loads(payload) if payload else {}
                
                self.logger.debug(f"Home Assistant state change: {entity_id} -> {data}")
                
        except Exception as e:
            self.logger.error(f"Error handling Home Assistant message: {e}")
    
    def _handle_jarvis_message(self, topic: str, payload: str):
        """Traite les messages destinés à Jarvis"""
        try:
            parts = topic.split('/')
            if len(parts) >= 3:
                command = parts[1]
                target = parts[2]
                
                self.logger.info(f"Jarvis command received: {command} -> {target}")
                
                # Traiter les commandes
                if command == "control":
                    asyncio.create_task(self._handle_control_command(target, payload))
                
        except Exception as e:
            self.logger.error(f"Error handling Jarvis message: {e}")
    
    async def _handle_control_command(self, target: str, payload: str):
        """Traite une commande de contrôle"""
        try:
            data = json.loads(payload) if payload else {}
            action = data.get("action", "")
            
            if action == "turn_on":
                await self.turn_on(target)
            elif action == "turn_off":
                await self.turn_off(target)
            elif action == "set_value":
                value = data.get("value")
                if value is not None:
                    await self.set_value(target, value)
            
        except Exception as e:
            self.logger.error(f"Error handling control command: {e}")
    
    async def publish_mqtt(self, topic: str, payload: str, retain: bool = False):
        """Publie un message MQTT"""
        if self.mqtt_client:
            self.mqtt_client.publish(topic, payload, retain=retain)
        else:
            self.logger.warning("MQTT client not available")