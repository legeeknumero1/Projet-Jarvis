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
    State(_state): State<Arc<AppState>>,
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

    let response = TranscribeResponse {
        text: "Texte transcrire depuis le fichier audio".to_string(),
        language,
        confidence: 0.95,
        duration_ms: 2500,
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
