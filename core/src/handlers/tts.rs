use axum::{extract::State, http::StatusCode, Json};
use std::sync::Arc;
use tracing::info;

use crate::middleware::{InputValidator, TTSValidator, ValidatedJwt};
use crate::models::{AppState, SynthesizeRequest, SynthesizeResponse, VoiceInfo};

/// Synthesize speech
#[utoipa::path(
    post,
    path = "/tts",
    request_body = SynthesizeRequest,
    responses(
        (status = 200, description = "Synthesis result", body = SynthesizeResponse),
        (status = 400, description = "Invalid request")
    ),
    security(
        ("bearer_auth" = [])
    )
)]
pub async fn synthesize(
    ValidatedJwt(claims): ValidatedJwt,
    State(state): State<Arc<AppState>>,
    Json(req): Json<SynthesizeRequest>,
) -> Result<(StatusCode, Json<SynthesizeResponse>), (StatusCode, String)> {
    // ============================================================================
    // SECURITY FIX C7-C11: Validate TTS text, voice, and speed
    // ============================================================================
    let validator = TTSValidator::new(req.text.clone(), req.voice.clone(), req.speed);
    if let Err(e) = validator.validate() {
        tracing::warn!(
            " TTS VALIDATION FAILED: {} from user {}",
            e,
            claims.user_id
        );
        return Err((
            StatusCode::BAD_REQUEST,
            format!("Invalid TTS request: {}", e),
        ));
    }

    info!(" Synthesis request from user: {}", claims.user_id);
    let voice = req.voice.unwrap_or_else(|| "fr_FR-upmc-medium".to_string());
    
    // Warning if requested voice differs from loaded model (Multi-voice not fully supported yet)
    // We proceed with the default model anyway.
    
    let start_time = std::time::Instant::now();
    
    // 1. Synthesize Audio (Raw PCM)
    let audio_bytes = state.tts.synthesize(&req.text)
        .map_err(|e| {
            tracing::error!("TTS Synthesis failed: {}", e);
            (StatusCode::INTERNAL_SERVER_ERROR, "Synthesis failed".to_string())
        })?;

    let duration = start_time.elapsed();
    
    // 2. Encode to Base64
    use base64::{Engine as _, engine::general_purpose::STANDARD as BASE64};
    let audio_base64 = BASE64.encode(&audio_bytes);

    info!(" Synthesis success: {} bytes ({}ms)", audio_bytes.len(), duration.as_millis());

    let response = SynthesizeResponse {
        audio_data: audio_base64,
        sample_rate: 22050, // Piper defaults to 22050Hz usually
        duration_ms: duration.as_millis() as u32, // Approximate processing time, not audio duration
        voice,
    };

    Ok((StatusCode::OK, Json(response)))
}

pub async fn list_voices() -> (StatusCode, Json<Vec<VoiceInfo>>) {
    let voices = vec![
        VoiceInfo {
            id: "fr_FR-upmc-medium".to_string(),
            name: "UPMC Français (Femme)".to_string(),
            language: "fr".to_string(),
            gender: "female".to_string(),
        },
        VoiceInfo {
            id: "fr_FR-siwis-medium".to_string(),
            name: "Siwis Français (Femme)".to_string(),
            language: "fr".to_string(),
            gender: "female".to_string(),
        },
        VoiceInfo {
            id: "fr_FR-tom-medium".to_string(),
            name: "Tom Français (Homme)".to_string(),
            language: "fr".to_string(),
            gender: "male".to_string(),
        },
    ];

    (StatusCode::OK, Json(voices))
}
