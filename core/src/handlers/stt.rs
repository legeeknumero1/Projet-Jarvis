use axum::{extract::State, http::StatusCode, Json};
use std::sync::Arc;
use tracing::info;

use crate::middleware::{InputValidator, STTValidator, ValidatedJwt};
use crate::models::{AppState, LanguageInfo, TranscribeRequest, TranscribeResponse};

/// Transcribe audio
#[utoipa::path(
    post,
    path = "/stt",
    request_body = TranscribeRequest,
    responses(
        (status = 200, description = "Transcription result", body = TranscribeResponse),
        (status = 400, description = "Invalid request")
    ),
    security(
        ("bearer_auth" = [])
    )
)]
pub async fn transcribe(
    ValidatedJwt(claims): ValidatedJwt,
    State(state): State<Arc<AppState>>,
    Json(req): Json<TranscribeRequest>,
) -> Result<(StatusCode, Json<TranscribeResponse>), (StatusCode, String)> {
    // ============================================================================
    // SECURITY FIX C7-C11: Validate audio data and language
    // ============================================================================
    let validator = STTValidator::new(req.audio_data.clone(), req.language.clone());
    if let Err(e) = validator.validate() {
        tracing::warn!(
            " STT VALIDATION FAILED: {} from user {}",
            e,
            claims.user_id
        );
        return Err((
            StatusCode::BAD_REQUEST,
            format!("Invalid audio data: {}", e),
        ));
    }

    info!(" Transcription request from user: {}", claims.user_id);
    let language = req.language.unwrap_or_else(|| "fr".to_string());

    // 1. Decode Base64
    use base64::{Engine as _, engine::general_purpose::STANDARD as BASE64};
    let audio_bytes = BASE64.decode(&req.audio_data)
        .map_err(|e| (StatusCode::BAD_REQUEST, format!("Invalid Base64 audio: {}", e)))?;

    // 2. Convert PCM 16-bit LE to f32
    // We assume the input is Raw PCM 16-bit Mono 16kHz (common for STT APIs)
    // If it's a WAV file, we should technically skip the 44-byte header.
    // Simple heuristic: if it starts with "RIFF", skip 44 bytes.
    let start_offset = if audio_bytes.len() > 44 && &audio_bytes[0..4] == b"RIFF" {
        44
    } else {
        0
    };

    let mut samples: Vec<f32> = Vec::with_capacity((audio_bytes.len() - start_offset) / 2);
    for chunk in audio_bytes[start_offset..].chunks_exact(2) {
        let sample_i16 = i16::from_le_bytes([chunk[0], chunk[1]]);
        let sample_f32 = sample_i16 as f32 / 32768.0;
        samples.push(sample_f32);
    }

    // 3. Perform Transcription
    let start_time = std::time::Instant::now();
    let text = state.stt.transcribe(&samples)
        .map_err(|e| {
            tracing::error!("STT Transcription failed: {}", e);
            (StatusCode::INTERNAL_SERVER_ERROR, "Transcription failed".to_string())
        })?;
    let duration = start_time.elapsed();

    info!(" Transcription success: '{}' ({}ms)", text, duration.as_millis());

    let response = TranscribeResponse {
        text,
        language,
        confidence: 0.95, // Whisper C++ wrapper might not expose confidence easily per segment in this simplified binding
        duration_ms: duration.as_millis() as u32,
    };

    Ok((StatusCode::OK, Json(response)))
}

pub async fn list_languages() -> (StatusCode, Json<Vec<LanguageInfo>>) {
    let languages = vec![
        LanguageInfo {
            code: "fr".to_string(),
            name: "Français".to_string(),
        },
        LanguageInfo {
            code: "en".to_string(),
            name: "English".to_string(),
        },
        LanguageInfo {
            code: "es".to_string(),
            name: "Español".to_string(),
        },
    ];

    (StatusCode::OK, Json(languages))
}
