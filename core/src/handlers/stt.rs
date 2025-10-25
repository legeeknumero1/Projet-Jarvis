use axum::{
    extract::State,
    http::StatusCode,
    Json,
};
use std::sync::Arc;

use crate::models::{AppState, TranscribeRequest, TranscribeResponse, LanguageInfo};

pub async fn transcribe(
    State(_state): State<Arc<AppState>>,
    Json(req): Json<TranscribeRequest>,
) -> (StatusCode, Json<TranscribeResponse>) {
    let language = req.language.unwrap_or_else(|| "fr".to_string());

    let response = TranscribeResponse {
        text: "Texte transcrire depuis le fichier audio".to_string(),
        language,
        confidence: 0.95,
        duration_ms: 2500,
    };

    (StatusCode::OK, Json(response))
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
