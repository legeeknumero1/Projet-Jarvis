use reqwest::Client;
use serde_json::Value;

pub struct PythonBridgesClient {
    base_url: String,
    client: Client,
}

impl PythonBridgesClient {
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

    pub async fn generate_llm(&self, prompt: &str) -> Result<Value, reqwest::Error> {
        let url = format!("{}/api/llm/generate", self.base_url);
        let payload = serde_json::json!({
            "prompt": prompt,
            "temperature": 0.7,
            "max_tokens": 512
        });
        self.client.post(&url).json(&payload).send().await?.json().await
    }

    pub async fn transcribe(&self, audio_data: &str, language: &str) -> Result<Value, reqwest::Error> {
        let url = format!("{}/api/stt/transcribe", self.base_url);
        let payload = serde_json::json!({
            "audio_data": audio_data,
            "language": language
        });
        self.client.post(&url).json(&payload).send().await?.json().await
    }

    pub async fn synthesize(&self, text: &str, voice: &str) -> Result<Value, reqwest::Error> {
        let url = format!("{}/api/tts/synthesize", self.base_url);
        let payload = serde_json::json!({
            "text": text,
            "voice": voice
        });
        self.client.post(&url).json(&payload).send().await?.json().await
    }

    pub async fn embed(&self, text: &str) -> Result<Value, reqwest::Error> {
        let url = format!("{}/api/embeddings/embed", self.base_url);
        let payload = serde_json::json!({
            "text": text
        });
        self.client.post(&url).json(&payload).send().await?.json().await
    }
}
