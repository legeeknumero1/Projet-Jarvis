/// Jarvis MQTT Automations - Phase 5
/// Automation engine pour domotique avec MQTT + Home Assistant

pub mod mqtt_client;
pub mod automations;
pub mod ha_client;
pub mod error;
pub mod event_bus;

pub use mqtt_client::MqttService;
pub use automations::AutomationEngine;
pub use ha_client::HomeAssistantClient;
pub use error::{MqttError, MqttResult};
pub use event_bus::{EventBus, JarvisEvent, EventHandler};

use std::sync::Arc;

/// Service container for MQTT layer
pub struct MqttServices {
    pub mqtt: Arc<MqttService>,
    pub automations: Arc<AutomationEngine>,
    pub ha_client: Arc<HomeAssistantClient>,
    pub event_bus: Arc<EventBus>,
}

impl MqttServices {
    pub async fn new(
        mqtt_broker: &str,
        ha_url: &str,
        ha_token: &str,
    ) -> MqttResult<Self> {
        let mqtt = Arc::new(MqttService::new(mqtt_broker).await?);
        let ha_client = Arc::new(HomeAssistantClient::new(ha_url.to_string(), ha_token.to_string()));
        let automations = Arc::new(AutomationEngine::new());
        let event_bus = Arc::new(EventBus::new(1000)); // 1000 event capacity

        Ok(MqttServices {
            mqtt,
            automations,
            ha_client,
            event_bus,
        })
    }

    pub async fn health_check(&self) -> MqttResult<bool> {
        Ok(self.mqtt.is_connected())
    }
}
