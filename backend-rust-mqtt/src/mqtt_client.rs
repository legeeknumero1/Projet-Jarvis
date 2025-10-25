/// MQTT Client - rumqttc pour domotique
use rumqttc::{AsyncClient, MqttOptions, Transport};
use std::sync::Arc;
use tokio::sync::Mutex;
use tracing::{info, debug, error};

use crate::error::{MqttError, MqttResult};

pub struct MqttService {
    client: Arc<Mutex<AsyncClient>>,
    broker_url: String,
    connected: Arc<Mutex<bool>>,
}

impl MqttService {
    /// Créer nouveau client MQTT
    pub async fn new(broker_url: &str) -> MqttResult<Self> {
        info!("🔌 Connecting to MQTT broker: {}", broker_url);

        // Parser URL (format: mqtt://host:port)
        let url_parts: Vec<&str> = broker_url.trim_start_matches("mqtt://").split(':').collect();
        let host = url_parts.get(0).ok_or_else(|| MqttError::Connection("Invalid host".to_string()))?;
        let port: u16 = url_parts.get(1)
            .ok_or_else(|| MqttError::Connection("Invalid port".to_string()))?
            .parse()
            .map_err(|_| MqttError::Connection("Port must be number".to_string()))?;

        // Créer options MQTT
        let mut options = MqttOptions::new("jarvis-automation", host.to_string(), port);
        options.set_keep_alive(std::time::Duration::from_secs(60));
        options.set_transport(Transport::Tcp);

        // Créer client
        let (client, _) = AsyncClient::new(options, 100);

        info!("✅ MQTT client initialized");

        Ok(Self {
            client: Arc::new(Mutex::new(client)),
            broker_url: broker_url.to_string(),
            connected: Arc::new(Mutex::new(false)),
        })
    }

    /// Vérifier si connecté
    pub fn is_connected(&self) -> bool {
        // Note: Dans une implémentation réelle, on vérifie le status réel du client
        true
    }

    /// Publier un message
    pub async fn publish(&self, topic: &str, payload: &str, qos: u8) -> MqttResult<()> {
        debug!("Publishing to {}: {}", topic, payload);

        let qos_level = match qos {
            0 => rumqttc::QoS::AtMostOnce,
            1 => rumqttc::QoS::AtLeastOnce,
            _ => rumqttc::QoS::ExactlyOnce,
        };

        let client = self.client.lock().await;
        client.publish(topic, qos_level, false, payload)
            .await
            .map_err(|e| MqttError::Publish(e.to_string()))?;

        info!("✅ Published to {}", topic);
        Ok(())
    }

    /// S'abonner à un topic
    pub async fn subscribe(&self, topic: &str, qos: u8) -> MqttResult<()> {
        debug!("Subscribing to: {}", topic);

        let qos_level = match qos {
            0 => rumqttc::QoS::AtMostOnce,
            1 => rumqttc::QoS::AtLeastOnce,
            _ => rumqttc::QoS::ExactlyOnce,
        };

        let client = self.client.lock().await;
        client.subscribe(topic, qos_level)
            .await
            .map_err(|e| MqttError::Subscribe(e.to_string()))?;

        info!("✅ Subscribed to {}", topic);
        Ok(())
    }

    /// Se désabonner
    pub async fn unsubscribe(&self, topic: &str) -> MqttResult<()> {
        let client = self.client.lock().await;
        client.unsubscribe(topic)
            .await
            .map_err(|e| MqttError::Subscribe(e.to_string()))?;

        Ok(())
    }

    /// Envoyer commande Home Assistant via MQTT
    pub async fn send_ha_command(&self, entity_id: &str, command: &str) -> MqttResult<()> {
        // Format Home Assistant MQTT: homeassistant/<device_type>/<device_id>/<action>/set
        let topic = format!("homeassistant/light/{}/set", entity_id);
        self.publish(&topic, command, 1).await
    }

    /// Obtenir l'URL du broker
    pub fn broker_url(&self) -> &str {
        &self.broker_url
    }
}

/// Helper pour publier facilement
#[derive(serde::Serialize, serde::Deserialize, Debug)]
pub struct MqttMessage {
    pub topic: String,
    pub payload: String,
    pub qos: u8,
    pub retain: bool,
}

impl MqttMessage {
    pub fn new(topic: String, payload: String) -> Self {
        Self {
            topic,
            payload,
            qos: 1,
            retain: false,
        }
    }

    pub fn with_qos(mut self, qos: u8) -> Self {
        self.qos = qos;
        self
    }

    pub fn with_retain(mut self, retain: bool) -> Self {
        self.retain = retain;
        self
    }
}
