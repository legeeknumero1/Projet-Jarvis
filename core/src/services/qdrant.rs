use anyhow::{Result, Context};
use serde::{Deserialize, Serialize};
use serde_json::json;
use tracing::{info, warn, error};

pub struct QdrantService {
    client: reqwest::Client,
    url: String,
    collection: String,
}

impl QdrantService {
    pub fn new(url: &str) -> Self {
        Self {
            client: reqwest::Client::new(),
            url: url.trim_end_matches('/').to_string(),
            collection: "jarvis_memory".to_string(),
        }
    }

    /// Ensure collection exists
    pub async fn init_collection(&self, vector_size: usize) -> Result<()> {
        let check_url = format!("{}/collections/{}", self.url, self.collection);
        let res = self.client.get(&check_url).send().await?;

        if res.status() == 404 {
            info!(" Creating Qdrant collection: {}", self.collection);
            let create_url = format!("{}/collections/{}", self.url, self.collection);
            self.client.put(&create_url)
                .json(&json!({
                    "vectors": {
                        "size": vector_size,
                        "distance": "Cosine"
                    }
                }))
                .send()
                .await?
                .error_for_status()
                .context("Failed to create Qdrant collection")?;
        }

        Ok(())
    }

    /// Add a memory point
    pub async fn add_memory(&self, id: &str, text: &str, vector: Vec<f32>, user_id: &str) -> Result<()> {
        let url = format!("{}/collections/{}/points", self.url, self.collection);
        
        self.client.put(&url)
            .json(&json!({
                "points": [
                    {
                        "id": id,
                        "vector": vector,
                        "payload": {
                            "text": text,
                            "user_id": user_id,
                            "timestamp": chrono::Utc::now().to_rfc3339()
                        }
                    }
                ]
            }))
            .send()
            .await?
            .error_for_status()
            .context("Failed to add point to Qdrant")?;

        Ok(())
    }

    /// Search similar memories
    pub async fn search_memory(&self, vector: Vec<f32>, limit: usize, user_id: &str) -> Result<Vec<String>> {
        let url = format!("{}/collections/{}/points/search", self.url, self.collection);
        
        let res = self.client.post(&url)
            .json(&json!({
                "vector": vector,
                "limit": limit,
                "with_payload": true,
                "filter": {
                    "must": [
                        { "key": "user_id", "match": { "value": user_id } }
                    ]
                }
            }))
            .send()
            .await?
            .error_for_status()?;

        let body: serde_json::Value = res.json().await?;
        let mut memories = Vec::new();

        if let Some(hits) = body["result"].as_array() {
            for hit in hits {
                if let Some(text) = hit["payload"]["text"].as_str() {
                    memories.push(text.to_string());
                }
            }
        }

        Ok(memories)
    }
}
