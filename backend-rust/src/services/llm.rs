//! Service LLM pour Jarvis Rust Backend
//! 
//! Client Rust pour Ollama avec streaming et gestion d'erreurs
//! Remplace les appels HTTP Python par des appels Rust natifs

use reqwest::Client;
use serde::{Deserialize, Serialize};
use std::time::{Duration, Instant};
use tokio_stream::{Stream, StreamExt};

use crate::config::AppConfig;

/// Service de communication avec Ollama LLM
#[derive(Clone)]
pub struct LLMService {
    client: Client,
    base_url: String,
    model: String,
    default_timeout: Duration,
    default_temperature: f32,
    default_max_tokens: u32,
}

/// Requête vers Ollama
#[derive(Debug, Serialize)]
struct OllamaRequest {
    model: String,
    prompt: String,
    stream: bool,
    options: OllamaOptions,
}

/// Options pour Ollama
#[derive(Debug, Serialize)]
struct OllamaOptions {
    temperature: f32,
    num_predict: u32,
    top_p: f32,
    top_k: u32,
}

/// Réponse d'Ollama (non-streaming)
#[derive(Debug, Deserialize)]
struct OllamaResponse {
    response: String,
    done: bool,
    context: Option<Vec<i32>>,
    total_duration: Option<u64>,
    load_duration: Option<u64>,
    prompt_eval_count: Option<u32>,
    prompt_eval_duration: Option<u64>,
    eval_count: Option<u32>,
    eval_duration: Option<u64>,
}

/// Chunk de réponse streaming d'Ollama
#[derive(Debug, Deserialize)]
struct OllamaStreamChunk {
    response: String,
    done: bool,
    context: Option<Vec<i32>>,
}

/// Réponse formatée pour l'API Jarvis
#[derive(Debug, Clone)]
pub struct LLMResponse {
    pub content: String,
    pub usage: TokenUsage,
    pub model: String,
    pub response_time_ms: u64,
    pub context: Option<Vec<i32>>,
}

/// Utilisation de tokens
#[derive(Debug, Clone)]
pub struct TokenUsage {
    pub prompt_tokens: u32,
    pub completion_tokens: u32,
    pub total_tokens: u32,
}

/// Erreurs spécifiques au service LLM
#[derive(Debug, thiserror::Error)]
pub enum LLMError {
    #[error("Timeout lors de la génération: {0}s")]
    Timeout(u64),
    
    #[error("Modèle non disponible: {0}")]
    ModelNotAvailable(String),
    
    #[error("Erreur réseau Ollama: {0}")]
    NetworkError(String),
    
    #[error("Réponse invalide d'Ollama: {0}")]
    InvalidResponse(String),
    
    #[error("Service Ollama indisponible")]
    ServiceUnavailable,
}

impl LLMService {
    /// Initialise le service LLM
    pub async fn new(config: &AppConfig) -> anyhow::Result<Self> {
        let client = Client::builder()
            .timeout(Duration::from_secs(config.ollama.timeout_secs))
            .build()?;

        let service = Self {
            client,
            base_url: config.ollama.url.clone(),
            model: config.ollama.model.clone(),
            default_timeout: Duration::from_secs(config.ollama.timeout_secs),
            default_temperature: config.ollama.temperature,
            default_max_tokens: config.ollama.max_tokens,
        };

        // Test de connexion
        service.test_connection().await?;
        tracing::info!("✅ Connexion Ollama établie: {}", config.ollama.url);

        Ok(service)
    }

    /// Teste la connexion à Ollama
    async fn test_connection(&self) -> anyhow::Result<()> {
        let url = format!("{}/api/version", self.base_url);
        
        match self.client.get(&url).send().await {
            Ok(response) => {
                if response.status().is_success() {
                    tracing::debug!("✅ Ollama accessible");
                    Ok(())
                } else {
                    Err(LLMError::ServiceUnavailable.into())
                }
            }
            Err(e) => {
                tracing::error!("❌ Impossible de joindre Ollama: {}", e);
                Err(LLMError::NetworkError(e.to_string()).into())
            }
        }
    }

    /// Vérifie si le service est prêt
    pub async fn is_ready(&self) -> anyhow::Result<()> {
        self.test_connection().await
    }

    /// Génère une réponse complète (non-streaming)
    pub async fn generate(
        &self,
        prompt: String,
        model: Option<String>,
        temperature: Option<f32>,
        max_tokens: Option<u32>,
    ) -> anyhow::Result<LLMResponse> {
        let start_time = Instant::now();
        
        let request = OllamaRequest {
            model: model.unwrap_or_else(|| self.model.clone()),
            prompt,
            stream: false,
            options: OllamaOptions {
                temperature: temperature.unwrap_or(self.default_temperature),
                num_predict: max_tokens.unwrap_or(self.default_max_tokens),
                top_p: 0.9,
                top_k: 40,
            },
        };

        tracing::debug!("🧠 Génération LLM: modèle={}, temp={}, max_tokens={}", 
                       request.model, request.options.temperature, request.options.num_predict);

        let url = format!("{}/api/generate", self.base_url);
        
        let response = self
            .client
            .post(&url)
            .json(&request)
            .send()
            .await
            .map_err(|e| LLMError::NetworkError(e.to_string()))?;

        if !response.status().is_success() {
            let status = response.status();
            let error_text = response.text().await.unwrap_or_default();
            
            return Err(match status.as_u16() {
                404 => LLMError::ModelNotAvailable(request.model),
                _ => LLMError::ServiceUnavailable,
            }.into());
        }

        let ollama_response: OllamaResponse = response
            .json()
            .await
            .map_err(|e| LLMError::InvalidResponse(e.to_string()))?;

        let response_time_ms = start_time.elapsed().as_millis() as u64;

        // Calculer l'utilisation de tokens
        let usage = TokenUsage {
            prompt_tokens: ollama_response.prompt_eval_count.unwrap_or(0),
            completion_tokens: ollama_response.eval_count.unwrap_or(0),
            total_tokens: ollama_response.prompt_eval_count.unwrap_or(0) 
                         + ollama_response.eval_count.unwrap_or(0),
        };

        tracing::info!(
            "✅ Génération LLM terminée en {}ms - {} tokens total",
            response_time_ms,
            usage.total_tokens
        );

        Ok(LLMResponse {
            content: ollama_response.response,
            usage,
            model: request.model,
            response_time_ms,
            context: ollama_response.context,
        })
    }

    /// Génère une réponse en streaming
    pub async fn generate_stream(
        &self,
        prompt: String,
        model: Option<String>,
        temperature: Option<f32>,
        max_tokens: Option<u32>,
    ) -> anyhow::Result<impl Stream<Item = Result<String, LLMError>>> {
        let request = OllamaRequest {
            model: model.unwrap_or_else(|| self.model.clone()),
            prompt,
            stream: true,
            options: OllamaOptions {
                temperature: temperature.unwrap_or(self.default_temperature),
                num_predict: max_tokens.unwrap_or(self.default_max_tokens),
                top_p: 0.9,
                top_k: 40,
            },
        };

        tracing::debug!("🧠 Génération LLM streaming: modèle={}", request.model);

        let url = format!("{}/api/generate", self.base_url);
        
        let response = self
            .client
            .post(&url)
            .json(&request)
            .send()
            .await
            .map_err(|e| LLMError::NetworkError(e.to_string()))?;

        if !response.status().is_success() {
            return Err(LLMError::ServiceUnavailable.into());
        }

        let stream = response
            .bytes_stream()
            .map(|chunk_result| {
                match chunk_result {
                    Ok(chunk) => {
                        match serde_json::from_slice::<OllamaStreamChunk>(&chunk) {
                            Ok(stream_chunk) => Ok(stream_chunk.response),
                            Err(e) => Err(LLMError::InvalidResponse(e.to_string())),
                        }
                    }
                    Err(e) => Err(LLMError::NetworkError(e.to_string())),
                }
            });

        Ok(stream)
    }

    /// Liste les modèles disponibles
    pub async fn list_models(&self) -> anyhow::Result<Vec<String>> {
        let url = format!("{}/api/tags", self.base_url);
        
        let response = self
            .client
            .get(&url)
            .send()
            .await
            .map_err(|e| LLMError::NetworkError(e.to_string()))?;

        if !response.status().is_success() {
            return Err(LLMError::ServiceUnavailable.into());
        }

        #[derive(Deserialize)]
        struct ModelsResponse {
            models: Vec<ModelInfo>,
        }

        #[derive(Deserialize)]
        struct ModelInfo {
            name: String,
        }

        let models_response: ModelsResponse = response
            .json()
            .await
            .map_err(|e| LLMError::InvalidResponse(e.to_string()))?;

        let model_names = models_response
            .models
            .into_iter()
            .map(|m| m.name)
            .collect();

        Ok(model_names)
    }

    /// Vérifie la santé du service LLM
    pub async fn health_check(&self) -> anyhow::Result<serde_json::Value> {
        let start = Instant::now();
        
        // Test simple avec un prompt minimal
        let test_prompt = "Test";
        
        match self.generate(
            test_prompt.to_string(),
            None,
            Some(0.1), // Température faible pour cohérence
            Some(10),  // Très peu de tokens
        ).await {
            Ok(response) => {
                let response_time = start.elapsed().as_millis() as u64;
                
                Ok(serde_json::json!({
                    "status": "healthy",
                    "response_time_ms": response_time,
                    "model": response.model,
                    "test_tokens": response.usage.total_tokens
                }))
            }
            Err(e) => {
                Ok(serde_json::json!({
                    "status": "unhealthy",
                    "error": e.to_string(),
                    "model": self.model
                }))
            }
        }
    }
}