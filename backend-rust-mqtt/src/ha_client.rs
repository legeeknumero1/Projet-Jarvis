/// Home Assistant Client - API REST pour contrôle domotique
use reqwest::Client;
use serde_json::json;
use tracing::{info, debug, error};

use crate::error::{MqttError, MqttResult};

pub struct HomeAssistantClient {
    base_url: String,
    token: String,
    http_client: Client,
}

impl HomeAssistantClient {
    /// Créer nouveau client Home Assistant
    pub fn new(base_url: String, token: String) -> Self {
        info!("🏠 Home Assistant client initialized: {}", base_url);

        Self {
            base_url: base_url.trim_end_matches('/').to_string(),
            token,
            http_client: Client::new(),
        }
    }

    /// Vérifier la connexion
    pub async fn health_check(&self) -> MqttResult<bool> {
        let url = format!("{}/api/", self.base_url);
        let response = self.http_client
            .get(&url)
            .bearer_auth(&self.token)
            .send()
            .await
            .map_err(|e| MqttError::HomeAssistant(e.to_string()))?;

        Ok(response.status().is_success())
    }

    /// Lister les entités
    pub async fn list_states(&self) -> MqttResult<Vec<serde_json::Value>> {
        let url = format!("{}/api/states", self.base_url);
        let response = self.http_client
            .get(&url)
            .bearer_auth(&self.token)
            .send()
            .await
            .map_err(|e| MqttError::HomeAssistant(e.to_string()))?;

        let states = response
            .json::<Vec<serde_json::Value>>()
            .await
            .map_err(|e| MqttError::HomeAssistant(e.to_string()))?;

        Ok(states)
    }

    /// Obtenir l'état d'une entité
    pub async fn get_state(&self, entity_id: &str) -> MqttResult<serde_json::Value> {
        let url = format!("{}/api/states/{}", self.base_url, entity_id);
        let response = self.http_client
            .get(&url)
            .bearer_auth(&self.token)
            .send()
            .await
            .map_err(|e| MqttError::HomeAssistant(e.to_string()))?;

        let state = response
            .json::<serde_json::Value>()
            .await
            .map_err(|e| MqttError::HomeAssistant(e.to_string()))?;

        Ok(state)
    }

    /// Appeler un service Home Assistant
    pub async fn call_service(&self, domain: &str, service: &str, data: serde_json::Value) -> MqttResult<()> {
        debug!("Calling service: {}.{}", domain, service);

        let url = format!("{}/api/services/{}/{}", self.base_url, domain, service);
        let response = self.http_client
            .post(&url)
            .bearer_auth(&self.token)
            .json(&data)
            .send()
            .await
            .map_err(|e| MqttError::HomeAssistant(e.to_string()))?;

        if !response.status().is_success() {
            return Err(MqttError::HomeAssistant(format!(
                "Service call failed: {}",
                response.status()
            )));
        }

        info!("✅ Service called: {}.{}", domain, service);
        Ok(())
    }

    /// Allumer une lumière
    pub async fn light_on(&self, entity_id: &str, brightness: Option<u8>) -> MqttResult<()> {
        let mut data = json!({
            "entity_id": entity_id
        });

        if let Some(b) = brightness {
            data["brightness"] = json!(b);
        }

        self.call_service("light", "turn_on", data).await
    }

    /// Éteindre une lumière
    pub async fn light_off(&self, entity_id: &str) -> MqttResult<()> {
        let data = json!({
            "entity_id": entity_id
        });

        self.call_service("light", "turn_off", data).await
    }

    /// Contrôler le chauffage
    pub async fn set_temperature(&self, entity_id: &str, temperature: f32) -> MqttResult<()> {
        let data = json!({
            "entity_id": entity_id,
            "temperature": temperature
        });

        self.call_service("climate", "set_temperature", data).await
    }

    /// Créer une notification
    pub async fn notify(&self, message: &str, title: Option<&str>) -> MqttResult<()> {
        let mut data = json!({
            "message": message
        });

        if let Some(t) = title {
            data["title"] = json!(t);
        }

        self.call_service("notify", "persistent_notification", data).await
    }

    /// Obtenir les accessoires Zigbee/Zwave
    pub async fn get_devices(&self) -> MqttResult<Vec<serde_json::Value>> {
        let url = format!("{}/api/config/device_registry/list", self.base_url);
        let response = self.http_client
            .get(&url)
            .bearer_auth(&self.token)
            .send()
            .await
            .map_err(|e| MqttError::HomeAssistant(e.to_string()))?;

        let devices = response
            .json::<Vec<serde_json::Value>>()
            .await
            .map_err(|e| MqttError::HomeAssistant(e.to_string()))?;

        Ok(devices)
    }
}
