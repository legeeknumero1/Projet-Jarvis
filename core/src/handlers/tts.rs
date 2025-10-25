use axum::{
    extract::State,
    http::StatusCode,
    Json,
};
use std::sync::Arc;

use crate::models::{AppState, SynthesizeRequest, SynthesizeResponse, VoiceInfo};

pub async fn synthesize(
    State(_state): State<Arc<AppState>>,
    Json(req): Json<SynthesizeRequest>,
) -> (StatusCode, Json<SynthesizeResponse>) {
    let voice = req.voice.unwrap_or_else(|| "fr_FR-upmc-medium".to_string());
    let speed = req.speed.unwrap_or(1.0);

    let response = SynthesizeResponse {
        audio_data: "base64_encoded_audio_data".to_string(),
        sample_rate: 22050,
        duration_ms: 3000,
        voice,
    };

    (StatusCode::OK, Json(response))
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
