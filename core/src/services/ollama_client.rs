use reqwest::Client;
use serde_json::{json, Value};
use std::error::Error;

/// Async client for the local Ollama instance operating in zero-VRAM-standby mode.
///
/// Architecture rationale: the local LLM (e.g. `deepseek-r1:14b`) stays completely
/// unloaded from the RTX 4080 VRAM during normal operation. It is only materialized
/// in GPU memory when the Gemini cloud API is unreachable (network drop, HTTP 429,
/// server timeout). Once inference completes, `keep_alive: 0` forces Ollama to evict
/// the model weights from VRAM immediately — restoring full GPU headroom for gaming
/// workloads (Apex Legends @ 240Hz, CS2, LoL).
///
/// The embedding model (`nomic-embed-text`, ~300 Mo) is lightweight enough to run
/// on-demand without measurable impact on GPU-bound workloads.
pub struct OllamaClient {
    client: Client,
    base_url: String,
    llm_model: String,
    embed_model: String,
}

impl OllamaClient {
    pub fn new(llm_model: String, embed_model: String) -> Self {
        let base_url = std::env::var("OLLAMA_URL").unwrap_or_else(|_| "http://jarvis_ollama:11434".to_string());
        Self {
            client: Client::new(),
            base_url,
            llm_model,
            embed_model,
        }
    }

    /// Computes dense vector embeddings locally for Tantivy RAG archiving.
    ///
    /// Uses a lightweight embedding model (~300 Mo) that loads/unloads fast
    /// and has negligible VRAM footprint. Safe to call during gaming sessions.
    pub async fn generate_embedding(&self, text: &str) -> Result<Vec<f32>, Box<dyn Error + Send + Sync>> {
        let url = format!("{}/api/embeddings", self.base_url);
        let payload = json!({
            "model": self.embed_model,
            "prompt": text,
        });

        let res = self.client
            .post(&url)
            .json(&payload)
            .send()
            .await?
            .json::<Value>()
            .await?;

        if let Some(embedding) = res["embedding"].as_array() {
            let vec: Vec<f32> = embedding
                .iter()
                .filter_map(|v| v.as_f64().map(|f| f as f32))
                .collect();

            if vec.is_empty() {
                return Err("Ollama returned an empty embedding vector".into());
            }
            return Ok(vec);
        }

        Err("Invalid embedding format returned from Ollama".into())
    }

    /// Executes fallback inference on the local LLM and immediately evicts
    /// the model from GPU VRAM after generation completes.
    ///
    /// # VRAM lifecycle
    /// 1. Ollama loads model weights into RTX 4080 VRAM (~10-13 Go for 14B)
    /// 2. Inference runs with `format: "json"` for structured HUD output
    /// 3. `keep_alive: 0` triggers immediate VRAM deallocation post-inference
    /// 4. GPU memory returns to 0 bytes occupied by the LLM
    ///
    /// This function should ONLY be called when `GeminiClient::analyze_intent`
    /// has already failed. It is the last line of defense before returning an error.
    pub async fn fallback_chat(
        &self,
        system_instruction: &str,
        user_prompt: &str,
    ) -> Result<Value, Box<dyn Error + Send + Sync>> {
        let url = format!("{}/api/generate", self.base_url);

        // CRITICAL: keep_alive: 0 forces Ollama to drop the model from VRAM
        // the instant the last token is generated. Zero residual GPU footprint.
        let payload = json!({
            "model": self.llm_model,
            "prompt": user_prompt,
            "system": system_instruction,
            "stream": false,
            "format": "json",
            "keep_alive": 0
        });

        let res = self.client
            .post(&url)
            .json(&payload)
            .send()
            .await?
            .json::<Value>()
            .await?;

        if let Some(raw_response) = res["response"].as_str() {
            // Robust extraction: find '{' and '}'
            let mut clean_json = raw_response.trim();
            if let Some(start) = clean_json.find('{') {
                if let Some(end) = clean_json.rfind('}') {
                    clean_json = &clean_json[start..=end];
                }
            }
            if let Ok(parsed_json) = serde_json::from_str::<Value>(clean_json) {
                return Ok(parsed_json);
            } else {
                return Err(format!("Failed to parse JSON from Ollama. Raw: {}", raw_response).into());
            }
        }

        Err("Ollama fallback failed to return structured JSON response".into())
    }

    /// Triage sémantique ultra-rapide (Cerveau Frontal)
    /// Renvoie 'L' (Local), 'S' (Short/API), ou 'C' (Complex/API)
    pub async fn classify_intent(&self, user_prompt: &str) -> Result<String, Box<dyn Error + Send + Sync>> {
        let url = format!("{}/api/generate", self.base_url);
        
        let system_instruction = "Tu es le routeur sémantique d'un système domotique. 
Analyse la requête de l'utilisateur.
- Si c'est une commande pour allumer/éteindre, ouvrir une app, ou contrôler le système local : réponds 'L'.
- Si c'est une question simple, courte ou factuelle (ex: météo, heure, définition) : réponds 'S'.
- Si c'est une requête complexe nécessitant de la réflexion, de l'analyse, ou du code : réponds 'C'.
Tu ne dois répondre qu'avec une seule lettre : L, S, ou C. Rien d'autre.";

        let payload = json!({
            "model": self.llm_model,
            "prompt": user_prompt,
            "system": system_instruction,
            "stream": false,
            "options": {
                "num_predict": 2, // Hard limit to ensure only 1 or 2 tokens max are generated
                "temperature": 0.0
            },
            "keep_alive": "10m" // Keep the 1.5B model in RAM for consecutive routing
        });

        match self.client.post(&url).json(&payload).send().await {
            Ok(res) => {
                if let Ok(json_res) = res.json::<Value>().await {
                    if let Some(raw) = json_res["response"].as_str() {
                        let clean = raw.trim().to_uppercase();
                        if clean.contains('L') { return Ok("L".to_string()); }
                        if clean.contains('S') { return Ok("S".to_string()); }
                        if clean.contains('C') { return Ok("C".to_string()); }
                        // Si l'IA a bavardé, on extrait la première lettre L, S ou C
                        for c in clean.chars() {
                            if c == 'L' || c == 'S' || c == 'C' {
                                return Ok(c.to_string());
                            }
                        }
                    }
                }
            }
            Err(e) => {
                tracing::warn!("Failed to contact Ollama for triage: {}", e);
            }
        }
        
        // Failsafe: Si Ollama crash ou ne répond pas, on route de façon sécurisée (Short)
        Ok("S".to_string())
    }
}
