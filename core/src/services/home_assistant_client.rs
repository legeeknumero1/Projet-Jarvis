use reqwest::Client;
use serde_json::Value;
use std::error::Error;
use tracing::{info, warn};

/// Client for communicating with the local Home Assistant (HAos) instance
pub struct HomeAssistantClient {
    client: Client,
    base_url: String,
    api_token: String,
}

impl HomeAssistantClient {
    /// Initializes a new Home Assistant client
    /// The API token is securely provided via the secretsd vault during startup
    pub fn new(api_token: String) -> Self {
        let base_url = std::env::var("HAOS_URL").unwrap_or_else(|_| "http://homeassistant.local:8123".to_string());
        Self {
            client: Client::new(),
            base_url,
            api_token,
        }
    }

    /// Generic method to call any Home Assistant service
    pub async fn call_service(
        &self,
        domain: &str,
        service: &str,
        entity_id: Option<&str>,
        extra_payload: Option<serde_json::Value>,
    ) -> Result<(), Box<dyn Error + Send + Sync>> {
        if self.api_token.is_empty() {
            warn!(" HAos token is empty, cannot execute {}/{}", domain, service);
            return Err("Missing HAos API token".into());
        }

        let url = format!("{}/api/services/{}/{}", self.base_url, domain, service);
        
        let mut payload = extra_payload.unwrap_or_else(|| serde_json::json!({}));
        if let Some(eid) = entity_id {
            if let Some(obj) = payload.as_object_mut() {
                if eid.contains(',') {
                    let entities: Vec<&str> = eid.split(',').map(|s| s.trim()).collect();
                    obj.insert("entity_id".to_string(), serde_json::json!(entities));
                } else {
                    obj.insert("entity_id".to_string(), serde_json::Value::String(eid.to_string()));
                }
            }
        }

        let res = self.client.post(&url)
            .header("Authorization", format!("Bearer {}", self.api_token))
            .header("Content-Type", "application/json")
            .json(&payload)
            .send()
            .await?;

        if res.status().is_success() {
            info!(" Successfully called HAos service: {}/{}", domain, service);
            Ok(())
        } else {
            let error_text = res.text().await.unwrap_or_default();
            Err(format!("Failed to call {}/{}: {}", domain, service, error_text).into())
        }
    }

    /// Retrieve states of all entities (or a specific one if implemented later)
    pub async fn get_states(&self) -> Result<Vec<Value>, Box<dyn Error + Send + Sync>> {
        if self.api_token.is_empty() {
            warn!(" HAos token is empty, cannot get states");
            return Err("Missing HAos API token".into());
        }

        let url = format!("{}/api/states", self.base_url);
        let res = self.client.get(&url)
            .header("Authorization", format!("Bearer {}", self.api_token))
            .header("Content-Type", "application/json")
            .send()
            .await?;

        if res.status().is_success() {
            let states: Vec<Value> = res.json().await?;
            Ok(states)
        } else {
            let error_text = res.text().await.unwrap_or_default();
            Err(format!("Failed to get states: {}", error_text).into())
        }
    }
}
