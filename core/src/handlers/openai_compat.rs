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

use crate::middleware::ValidatedJwt;
use crate::models::AppState;

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

    // Convert to base64 for internal API
    let audio_base64 = base64::Engine::encode(&base64::engine::general_purpose::STANDARD, &audio_data);

    // Call internal STT service
    let client = reqwest::Client::new();
    let response = client
        .post(format!("{}/transcribe", state.python_bridges_url))
        .json(&serde_json::json!({
            "audio_data": audio_base64,
            "language": language.unwrap_or_else(|| "fr".to_string()),
        }))
        .send()
        .await
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, format!("STT service error: {}", e)))?;

    if !response.status().is_success() {
        return Err((
            StatusCode::INTERNAL_SERVER_ERROR,
            "STT service failed".to_string(),
        ));
    }

    let stt_result: serde_json::Value = response
        .json()
        .await
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, format!("Failed to parse STT response: {}", e)))?;

    let text = stt_result["text"]
        .as_str()
        .unwrap_or("Transcription non disponible")
        .to_string();

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
    // Map OpenAI voices to Piper voices
    let voice = match req.voice.as_str() {
        "alloy" | "echo" | "fable" => "fr_FR-upmc-medium",
        "onyx" | "nova" | "shimmer" => "fr_FR-siwis-medium",
        custom => custom,
    };

    // Call internal TTS service
    let client = reqwest::Client::new();
    let response = client
        .post(format!("{}/synthesize", state.python_bridges_url))
        .json(&serde_json::json!({
            "text": req.input,
            "voice": voice,
            "speed": req.speed,
        }))
        .send()
        .await
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, format!("TTS service error: {}", e)))?;

    if !response.status().is_success() {
        return Err((
            StatusCode::INTERNAL_SERVER_ERROR,
            "TTS service failed".to_string(),
        ));
    }

    let tts_result: serde_json::Value = response
        .json()
        .await
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, format!("Failed to parse TTS response: {}", e)))?;

    let audio_base64 = tts_result["audio_data"]
        .as_str()
        .unwrap_or("")
        .to_string();

    // Decode base64 to bytes
    let audio_bytes = base64::Engine::decode(&base64::engine::general_purpose::STANDARD, audio_base64)
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, format!("Failed to decode audio: {}", e)))?;

    // Return raw audio bytes with appropriate content type
    let content_type = match req.response_format.as_str() {
        "mp3" => "audio/mpeg",
        "opus" => "audio/opus",
        "aac" => "audio/aac",
        "flac" => "audio/flac",
        "wav" => "audio/wav",
        "pcm" => "audio/pcm",
        _ => "audio/mpeg",
    };

    Ok((
        StatusCode::OK,
        [(axum::http::header::CONTENT_TYPE, content_type)],
        Bytes::from(audio_bytes),
    )
        .into_response())
}
