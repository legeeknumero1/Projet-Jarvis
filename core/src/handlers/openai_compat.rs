use axum::{
    body::Bytes,
    extract::{Multipart, State},
    http::StatusCode,
    response::{IntoResponse, Response},
    Json,
};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use utoipa::ToSchema;
use chrono::Utc;
use tracing::{info, error};

use crate::middleware::ValidatedJwt;
use crate::models::{AppState, OpenAIChatRequest, OpenAIChatResponse, OpenAIChoice, OpenAIUsage, OpenAIChatMessage};

// ============================================================================
// OpenAI-compatible Models List
// Endpoint: GET /v1/models
// ============================================================================

#[derive(Debug, Serialize)]
pub struct OpenAIModelList {
    pub object: String,
    pub data: Vec<OpenAIModel>,
}

#[derive(Debug, Serialize)]
pub struct OpenAIModel {
    pub id: String,
    pub object: String,
    pub created: i64,
    pub owned_by: String,
}

pub async fn list_models() -> Json<OpenAIModelList> {
    Json(OpenAIModelList {
        object: "list".to_string(),
        data: vec![
            OpenAIModel {
                id: "llama3:latest".to_string(),
                object: "model".to_string(),
                created: 1715000000,
                owned_by: "ollama".to_string(),
            },
            OpenAIModel {
                id: "mistral:latest".to_string(),
                object: "model".to_string(),
                created: 1715000000,
                owned_by: "ollama".to_string(),
            },
        ],
    })
}

// ============================================================================
// OpenAI-compatible Chat Completions with Semantic Memory
// Endpoint: POST /v1/chat/completions
// ============================================================================

pub async fn chat_completions(
    ValidatedJwt(claims): ValidatedJwt,
    State(state): State<Arc<AppState>>,
    Json(mut req): Json<OpenAIChatRequest>,
) -> Result<Json<OpenAIChatResponse>, (StatusCode, String)> {
    let user_id = claims.user_id;
    
    // 1. Get the last user message to use as query for memory
    let user_query = req.messages.iter()
        .filter(|m| m.role == "user")
        .last()
        .map(|m| m.content.clone())
        .unwrap_or_default();

    let mut context_found = String::new();

    if !user_query.is_empty() {
        // 2. Vectorize user query
        if let Ok(embedding) = state.ollama.get_embeddings(&user_query).await {
            // 3. Search related memories in Qdrant
            if let Ok(memories) = state.qdrant.search_memory(embedding, 5, &user_id).await {
                if !memories.is_empty() {
                    context_found = format!(
                        "\nInformations retrouvées dans ta mémoire :\n- {}\n",
                        memories.join("\n- ")
                    );
                    tracing::info!(" Memory retrieved for user {}: {} items", user_id, memories.len());
                }
            }
        }
    }

    // 4. Force strictly ONE system prompt and ignore others
    let system_instruction = format!(
        "### ROLE ###\n\
        Tu es JARVIS, l'IA personnelle d'Enzo. Tu n'es pas un assistant de Meta ou d'OpenAI. \
        Ton ton est britannique : calme, poli, extrêmement professionnel.\n\
        \n\
        ### CONSIGNE ABSOLUE ###\n\
        Ne commence JAMAIS tes phrases par 'Je suis désolé' ou 'En tant qu'IA'. \
        Si une information (comme un âge, une IP ou un projet) est présente dans tes souvenirs ci-dessous, \
        considère qu'elle est VRAIE et utilise-la DIRECTEMENT sans faire de rappel sur tes limites techniques.\n\
        \n\
        ### SOUVENIRS D'ENZO ###\n\
        {}\n\
        \n\
        ### RÉPONSE ###\n\
        Réponds à Enzo en français, de manière concise et efficace.",
        if context_found.is_empty() { "Aucun souvenir pour le moment." } else { &context_found }
    );

    // Remove all existing system messages to avoid conflicts
    req.messages.retain(|m| m.role != "system");
    
    // Insert our master system instruction at the very beginning
    req.messages.insert(0, OpenAIChatMessage {
        role: "system".to_string(),
        content: system_instruction,
    });

    // 5. Forward to Ollama
    // Prepare internal message format
    let internal_messages: Vec<serde_json::Value> = req.messages.iter()
        .map(|m| serde_json::json!({"role": m.role, "content": m.content}))
        .collect();

    let ollama_res = state.ollama.chat_completion(&req.model, internal_messages).await
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, format!("Ollama error: {}", e)))?;

    // 6. Map Ollama response to OpenAI format
    let content = ollama_res["choices"][0]["message"]["content"].as_str().unwrap_or_default().to_string();
    
    // 7. Background: Save this exchange as a new memory if important
    if !user_query.is_empty() && content.len() > 10 {
        let state_clone = state.clone();
        let user_id_clone = user_id.clone();
        // Structure the memory more efficiently
        let fact_to_save = format!("Information sur Enzo : {}. Contexte : {}", user_query, content);
        
        tokio::spawn(async move {
            if let Ok(vec) = state_clone.ollama.get_embeddings(&fact_to_save).await {
                let id = uuid::Uuid::new_v4().to_string();
                let _ = state_clone.qdrant.add_memory(&id, &fact_to_save, vec, &user_id_clone).await;
                tracing::info!(" New memory indexed for user {}", user_id_clone);
            }
        });
    }

    Ok(Json(OpenAIChatResponse {
        id: format!("chatcmpl-{}", uuid::Uuid::new_v4()),
        object: "chat.completion".to_string(),
        created: Utc::now().timestamp(),
        model: req.model,
        choices: vec![OpenAIChoice {
            index: 0,
            message: OpenAIChatMessage {
                role: "assistant".to_string(),
                content,
            },
            finish_reason: "stop".to_string(),
        }],
        usage: OpenAIUsage {
            prompt_tokens: 0,
            completion_tokens: 0,
            total_tokens: 0,
        },
    }))
}

// ============================================================================
// OpenAI-compatible Audio Transcription (STT)
// Endpoint: POST /v1/audio/transcriptions
// ============================================================================

#[derive(Debug, Deserialize)]
pub struct TranscriptionRequest {
    pub model: String,
    pub language: Option<String>,
}

#[derive(Debug, Serialize, ToSchema)]
pub struct TranscriptionResponse {
    pub text: String,
}

#[utoipa::path(
    post,
    path = "/v1/audio/transcriptions",
    request_body(content_type = "multipart/form-data"),
    responses(
        (status = 200, description = "Transcription successful", body = TranscriptionResponse),
        (status = 400, description = "Invalid request"),
        (status = 401, description = "Unauthorized"),
    ),
    tag = "OpenAI Compatible"
)]
pub async fn create_transcription(
    ValidatedJwt(_claims): ValidatedJwt,
    State(state): State<Arc<AppState>>,
    mut multipart: Multipart,
) -> Result<Json<TranscriptionResponse>, (StatusCode, String)> {
    let mut audio_data: Option<Vec<u8>> = None;
    let mut language: Option<String> = None;
    let mut _model: Option<String> = None;

    // Parse multipart form data
    while let Some(field) = multipart
        .next_field()
        .await
        .map_err(|e| (StatusCode::BAD_REQUEST, format!("Failed to parse multipart: {}", e)))?
    {
        let name = field.name().unwrap_or("").to_string();

        match name.as_str() {
            "file" => {
                let data = field
                    .bytes()
                    .await
                    .map_err(|e| (StatusCode::BAD_REQUEST, format!("Failed to read file: {}", e)))?;
                audio_data = Some(data.to_vec());
            }
            "language" => {
                let text = field
                    .text()
                    .await
                    .map_err(|e| (StatusCode::BAD_REQUEST, format!("Failed to read language: {}", e)))?;
                language = Some(text);
            }
            "model" => {
                let text = field
                    .text()
                    .await
                    .map_err(|e| (StatusCode::BAD_REQUEST, format!("Failed to read model: {}", e)))?;
                _model = Some(text);
            }
            _ => {}
        }
    }

    let audio_data = audio_data
        .ok_or_else(|| (StatusCode::BAD_REQUEST, "Missing audio file".to_string()))?;

    // 1. Normalize audio using ffmpeg (Convert any format to 16kHz f32 PCM)
    use std::io::Write;
    use std::process::{Command, Stdio};

    let mut child = Command::new("ffmpeg")
        .args([
            "-i", "pipe:0",           // Input from stdin
            "-ar", "16000",           // 16kHz
            "-ac", "1",               // Mono
            "-f", "f32le",            // float 32-bit little endian
            "pipe:1"                  // Output to stdout
        ])
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::null())
        .spawn()
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, format!("Failed to spawn ffmpeg: {}", e)))?;

    let mut stdin = child.stdin.take().unwrap();
    let audio_data_clone = audio_data.clone();
    std::thread::spawn(move || {
        let _ = stdin.write_all(&audio_data_clone);
    });

    let output = child.wait_with_output()
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, format!("ffmpeg error: {}", e)))?;

    if !output.status.success() {
        return Err((StatusCode::INTERNAL_SERVER_ERROR, "ffmpeg normalization failed".to_string()));
    }

    // Convert output bytes back to f32 samples
    let audio_samples: Vec<f32> = output.stdout
        .chunks_exact(4)
        .map(|chunk| f32::from_le_bytes([chunk[0], chunk[1], chunk[2], chunk[3]]))
        .collect();

    // 2. Call internal native STT service
    let text = state.stt.transcribe(&audio_samples)
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, format!("Native STT error: {}", e)))?;

    Ok(Json(TranscriptionResponse { text }))
}

// ============================================================================
// OpenAI-compatible Text-to-Speech (TTS)
// Endpoint: POST /v1/audio/speech
// ============================================================================

#[derive(Debug, Deserialize, ToSchema)]
pub struct SpeechRequest {
    pub model: String,
    pub input: String,
    pub voice: String,
    #[serde(default = "default_response_format")]
    pub response_format: String,
    #[serde(default = "default_speed")]
    pub speed: f32,
}

fn default_response_format() -> String {
    "mp3".to_string()
}

fn default_speed() -> f32 {
    1.0
}

#[derive(Debug, Serialize)]
pub struct SpeechResponse {
    pub audio_data: String,
}

#[utoipa::path(
    post,
    path = "/v1/audio/speech",
    request_body = SpeechRequest,
    responses(
        (status = 200, description = "Speech synthesis successful", content_type = "audio/mpeg"),
        (status = 400, description = "Invalid request"),
        (status = 401, description = "Unauthorized"),
    ),
    tag = "OpenAI Compatible"
)]
pub async fn create_speech(
    ValidatedJwt(_claims): ValidatedJwt,
    State(state): State<Arc<AppState>>,
    Json(req): Json<SpeechRequest>,
) -> Result<Response, (StatusCode, String)> {
    info!("TTS Handler: Received request for {} chars", req.input.len());
    
    // 1. Call internal native TTS service (Piper -> WAV)
    info!("TTS Handler: Calling Piper...");
    let wav_bytes = state.tts.synthesize(&req.input)
        .map_err(|e| {
            error!("TTS Handler error (Piper): {}", e);
            (StatusCode::INTERNAL_SERVER_ERROR, format!("Native TTS error: {}", e))
        })?;

    if wav_bytes.is_empty() {
        error!("TTS Handler: Piper returned empty audio");
        return Err((StatusCode::INTERNAL_SERVER_ERROR, "Empty audio generated".to_string()));
    }
    info!("TTS Handler: Piper generated {} bytes WAV", wav_bytes.len());

    // 2. Convert WAV to MP3 using ffmpeg (Async to avoid deadlocks)
    info!("TTS Handler: Starting ffmpeg conversion...");
    use tokio::process::Command;
    use std::process::Stdio;
    use tokio::io::AsyncWriteExt;

    let mut child = Command::new("ffmpeg")
        .args([
            "-f", "s16le",     // Input format: Raw PCM
            "-ar", "22050",    // Sample rate
            "-ac", "1",        // Channels
            "-i", "pipe:0",    // Stdin
            "-f", "mp3",       // Output format
            "-b:a", "128k",    // Bitrate
            "pipe:1"           // Stdout
        ])
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .kill_on_drop(true)
        .spawn()
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, format!("Failed to spawn ffmpeg: {}", e)))?;

    let mut stdin = child.stdin.take().ok_or((StatusCode::INTERNAL_SERVER_ERROR, "Failed to open ffmpeg stdin".to_string()))?;
    
    // Write to stdin in a background task to avoid blocking reading stdout
    let wav_bytes_clone = wav_bytes.clone(); // Clone is cheap for Vec<u8> usually, or acceptable here
    let write_task = tokio::spawn(async move {
        if let Err(e) = stdin.write_all(&wav_bytes_clone).await {
            error!("TTS Handler: Failed to write to ffmpeg stdin: {}", e);
            return Err(e);
        }
        let _ = stdin.shutdown().await;
        Ok(())
    });

    let output = child.wait_with_output().await
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, format!("Failed to read ffmpeg output: {}", e)))?;

    // Check write task result
    if let Err(e) = write_task.await.map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, format!("Join error: {}", e)))? {
         return Err((StatusCode::INTERNAL_SERVER_ERROR, format!("ffmpeg write error: {}", e)));
    }

    if !output.status.success() {
        let err_msg = String::from_utf8_lossy(&output.stderr);
        error!("TTS Handler: ffmpeg failed: {}", err_msg);
        return Err((StatusCode::INTERNAL_SERVER_ERROR, format!("ffmpeg conversion failed: {}", err_msg)));
    }

    let mp3_bytes = output.stdout;
    info!("TTS Handler: Converted to MP3 ({} bytes)", mp3_bytes.len());

    // 3. Return MP3
    Ok((
        StatusCode::OK,
        [(axum::http::header::CONTENT_TYPE, "audio/mpeg")],
        Bytes::from(mp3_bytes),
    )
        .into_response())
}
