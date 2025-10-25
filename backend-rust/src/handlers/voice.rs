//! Handlers vocaux pour Jarvis Rust Backend
//! 
//! Endpoints équivalents aux routes voice.py Python
//! pour STT et TTS

use axum::{extract::State, http::StatusCode, response::IntoResponse, Json};
use std::time::Instant;

use crate::{
    models::{SynthesizeRequest, TranscribeRequest},
    ApiResponse, AppState,
};

/// POST /api/voice/transcribe - Transcription Speech-to-Text
/// 
/// Endpoint pour la transcription audio via Whisper.
/// Accepte de l'audio en base64 et retourne le texte transcrit.
pub async fn transcribe(
    State(state): State<AppState>,
    Json(request): Json<TranscribeRequest>,
) -> impl IntoResponse {
    let start_time = Instant::now();

    // Validation des données audio
    if request.audio_data.is_empty() {
        return (
            StatusCode::BAD_REQUEST,
            Json(ApiResponse::<()>::error("Les données audio ne peuvent pas être vides")),
        );
    }

    // Validation de la taille (limite à 25MB en base64)
    if request.audio_data.len() > 25 * 1024 * 1024 {
        return (
            StatusCode::BAD_REQUEST,
            Json(ApiResponse::<()>::error(
                "Fichier audio trop volumineux (max 25MB)",
            )),
        );
    }

    tracing::info!(
        "🎤 Transcription demandée: {} caractères base64, langue: {:?}",
        request.audio_data.len(),
        request.language
    );

    match state.services.voice.transcribe_audio(request).await {
        Ok(response) => {
            let response_time = start_time.elapsed().as_millis() as u64;
            
            tracing::info!(
                "✅ Transcription terminée en {}ms: '{}' (confiance: {:.2})",
                response_time,
                response.text.chars().take(50).collect::<String>(),
                response.confidence
            );

            (StatusCode::OK, Json(ApiResponse::ok(response)))
        }
        Err(e) => {
            tracing::error!("❌ Erreur lors de la transcription: {}", e);

            let error_message = if e.to_string().contains("timeout") {
                "Timeout lors de la transcription - fichier audio trop long"
            } else if e.to_string().contains("format") {
                "Format audio non supporté - utilisez WAV, MP3, OGG ou FLAC"
            } else {
                "Erreur lors de la transcription audio"
            };

            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(ApiResponse::<()>::error(error_message)),
            )
        }
    }
}

/// POST /api/voice/synthesize - Synthèse Text-to-Speech
/// 
/// Endpoint pour la synthèse vocale via Piper TTS.
/// Accepte du texte et retourne de l'audio en base64.
pub async fn synthesize(
    State(state): State<AppState>,
    Json(request): Json<SynthesizeRequest>,
) -> impl IntoResponse {
    let start_time = Instant::now();

    // Validation du texte
    if request.text.trim().is_empty() {
        return (
            StatusCode::BAD_REQUEST,
            Json(ApiResponse::<()>::error("Le texte ne peut pas être vide")),
        );
    }

    // Limitation de taille du texte (5000 caractères max)
    if request.text.len() > 5000 {
        return (
            StatusCode::BAD_REQUEST,
            Json(ApiResponse::<()>::error(
                "Le texte ne peut pas dépasser 5000 caractères",
            )),
        );
    }

    tracing::info!(
        "🔊 Synthèse demandée: '{}' ({} caractères), voix: {:?}",
        request.text.chars().take(50).collect::<String>(),
        request.text.len(),
        request.voice
    );

    match state.services.voice.synthesize_speech(request).await {
        Ok(response) => {
            let response_time = start_time.elapsed().as_millis() as u64;
            
            tracing::info!(
                "✅ Synthèse terminée en {}ms: {:.1}s audio généré, format: {:?}",
                response_time,
                response.duration_secs,
                response.format
            );

            (StatusCode::OK, Json(ApiResponse::ok(response)))
        }
        Err(e) => {
            tracing::error!("❌ Erreur lors de la synthèse: {}", e);

            let error_message = if e.to_string().contains("timeout") {
                "Timeout lors de la synthèse - texte trop long"
            } else if e.to_string().contains("voice") {
                "Voix demandée non disponible"
            } else {
                "Erreur lors de la synthèse vocale"
            };

            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(ApiResponse::<()>::error(error_message)),
            )
        }
    }
}

/// GET /api/voice/voices - Liste des voix disponibles
/// 
/// Endpoint pour récupérer la liste des voix TTS disponibles.
pub async fn list_voices(State(state): State<AppState>) -> impl IntoResponse {
    tracing::info!("🎭 Récupération liste des voix disponibles");

    match state.services.voice.get_available_voices().await {
        Ok(voices) => {
            tracing::info!("✅ {} voix disponibles", voices.len());

            (
                StatusCode::OK,
                Json(ApiResponse::ok(serde_json::json!({
                    "voices": voices,
                    "count": voices.len()
                }))),
            )
        }
        Err(e) => {
            tracing::error!("❌ Erreur lors de la récupération des voix: {}", e);

            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(ApiResponse::<()>::error(
                    "Erreur récupération des voix disponibles",
                )),
            )
        }
    }
}

/// GET /api/voice/languages - Langues supportées pour STT
/// 
/// Endpoint pour récupérer les langues supportées par Whisper.
pub async fn list_languages(State(_state): State<AppState>) -> impl IntoResponse {
    tracing::info!("🌍 Récupération langues supportées");

    let languages = vec![
        serde_json::json!({"code": "fr", "name": "Français", "native": "Français"}),
        serde_json::json!({"code": "en", "name": "English", "native": "English"}),
        serde_json::json!({"code": "es", "name": "Spanish", "native": "Español"}),
        serde_json::json!({"code": "de", "name": "German", "native": "Deutsch"}),
        serde_json::json!({"code": "it", "name": "Italian", "native": "Italiano"}),
        serde_json::json!({"code": "pt", "name": "Portuguese", "native": "Português"}),
        serde_json::json!({"code": "auto", "name": "Auto-detect", "native": "Détection automatique"}),
    ];

    tracing::info!("✅ {} langues supportées", languages.len());

    (
        StatusCode::OK,
        Json(ApiResponse::ok(serde_json::json!({
            "languages": languages,
            "count": languages.len(),
            "default": "auto"
        }))),
    )
}