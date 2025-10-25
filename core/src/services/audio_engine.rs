use reqwest::Client;
use serde_json::Value;

pub struct AudioEngineClient {
    base_url: String,
    client: Client,
}

impl AudioEngineClient {
    pub fn new(base_url: String) -> Self {
        Self {
            base_url,
            client: Client::new(),
        }
    }

    pub async fn health_check(&self) -> Result<Value, reqwest::Error> {
        let url = format!("{}/health", self.base_url);
        self.client.get(&url).send().await?.json().await
    }

    pub async fn get_stats(&self) -> Result<Value, reqwest::Error> {
        let url = format!("{}/stats", self.base_url);
        self.client.get(&url).send().await?.json().await
    }

    pub async fn process_audio(&self, audio_data: &str) -> Result<Value, reqwest::Error> {
        let url = format!("{}/process", self.base_url);
        let payload = serde_json::json!({
            "audio_data": audio_data
        });
        self.client.post(&url).json(&payload).send().await?.json().await
    }

    pub async fn dsp_pipeline(&self, buffer: Vec<f32>) -> Result<Vec<f32>, reqwest::Error> {
        let url = format!("{}/dsp", self.base_url);
        let payload = serde_json::json!({
            "samples": buffer
        });

        let response = self.client.post(&url).json(&payload).send().await?.json::<Value>().await?;

        // Extraire les samples du résultat
        if let Some(samples) = response.get("samples").and_then(|s| s.as_array()) {
            Ok(samples.iter()
                .filter_map(|v| v.as_f64().map(|f| f as f32))
                .collect())
        } else {
            Ok(vec![])
        }
    }
}
