use anyhow::{Result, Context};
use serde::{Deserialize, Serialize};
use serde_json::json;

pub struct OllamaService {
    client: reqwest::Client,
    url: String,
}

impl OllamaService {
    pub fn new(url: &str) -> Self {
        Self {
            client: reqwest::Client::new(),
            url: url.trim_end_matches('/').to_string(),
        }
    }

    /// Get embeddings for a text using nomic-embed-text
    pub async fn get_embeddings(&self, text: &str) -> Result<Vec<f32>> {
        let url = format!("{}/api/embeddings", self.url);
        
        let res = self.client.post(&url)
            .json(&json!({
                "model": "nomic-embed-text",
                "prompt": text
            }))
            .send()
            .await?
            .error_for_status()
            .context("Failed to get embeddings from Ollama")?;

        let body: serde_json::Value = res.json().await?;
        
        let embedding = body["embedding"].as_array()
            .context("Invalid embedding response from Ollama")?
            .iter()
            .map(|v| v.as_f64().unwrap_or(0.0) as f32)
            .collect();

        Ok(embedding)
    }

    /// Forward chat completion to Ollama (OpenAI compatible internally)
    pub async fn chat_completion(&self, model: &str, messages: Vec<serde_json::Value>) -> Result<serde_json::Value> {
        let url = format!("{}/v1/chat/completions", self.url);
        
        let res = self.client.post(&url)
            .json(&json!({
                "model": model,
                "messages": messages,
                "stream": false
            }))
            .send()
            .await?
            .error_for_status()
            .context("Failed to get chat completion from Ollama")?;

        let body: serde_json::Value = res.json().await?;
        Ok(body)
    }
}
