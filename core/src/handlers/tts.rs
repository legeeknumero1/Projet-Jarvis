use axum::{
    extract::State,
    http::StatusCode,
    Json,
};
use std::sync::Arc;
use tracing::info;

use crate::models::{AppState, SynthesizeRequest, SynthesizeResponse, VoiceInfo};
use crate::middleware::{ValidatedJwt, TTSValidator, InputValidator};

pub async fn synthesize(
    ValidatedJwt(claims): ValidatedJwt,
    State(_state): State<Arc<AppState>>,
    Json(req): Json<SynthesizeRequest>,
) -> Result<(StatusCode, Json<SynthesizeResponse>), (StatusCode, String)> {
    // ============================================================================
    // SECURITY FIX C7-C11: Validate TTS text, voice, and speed
    // ============================================================================
    let validator = TTSValidator::new(req.text.clone(), req.voice.clone(), req.speed);
    if let Err(e) = validator.validate() {
        tracing::warn!("🚨 TTS VALIDATION FAILED: {} from user {}", e, claims.user_id);
        return Err((
            StatusCode::BAD_REQUEST,
            format!("Invalid TTS request: {}", e),
        ));
    }

    info!("🔊 Synthesis request from user: {}", claims.user_id);
    let voice = req.voice.unwrap_or_else(|| "fr_FR-upmc-medium".to_string());
    let _speed = req.speed.unwrap_or(1.0);

    let response = SynthesizeResponse {
        audio_data: "base64_encoded_audio_data".to_string(),
        sample_rate: 22050,
        duration_ms: 3000,
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
