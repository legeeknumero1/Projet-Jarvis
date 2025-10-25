use axum::{
    extract::State,
    http::StatusCode,
    Json,
};
use chrono::Utc;
use std::sync::Arc;
use uuid::Uuid;
use tracing::info;

use crate::models::{
    AppState, MemoryEntry, AddMemoryRequest, SearchMemoryRequest, SearchMemoryResponse,
};
use crate::middleware::{ValidatedJwt, MemoryContentValidator, SearchQueryValidator, InputValidator};

pub async fn add_memory(
    ValidatedJwt(claims): ValidatedJwt,
    State(_state): State<Arc<AppState>>,
    Json(req): Json<AddMemoryRequest>,
) -> Result<(StatusCode, Json<MemoryEntry>), (StatusCode, String)> {
    // ============================================================================
    // SECURITY FIX C7-C11: Validate memory content and importance
    // ============================================================================
    let validator = MemoryContentValidator::new(req.content.clone(), req.importance);
    if let Err(e) = validator.validate() {
        tracing::warn!("🚨 MEMORY VALIDATION FAILED: {} from user {}", e, claims.user_id);
        return Err((
            StatusCode::BAD_REQUEST,
            format!("Invalid memory: {}", e),
        ));
    }

    info!("💾 Adding memory for user: {}", claims.user_id);
    let memory = MemoryEntry {
        id: Uuid::new_v4().to_string(),
        content: req.content,
        embedding: None,
        importance: req.importance.unwrap_or(0.5),
        created_at: Utc::now(),
    };

    Ok((StatusCode::OK, Json(memory)))
}

pub async fn search_memory(
    ValidatedJwt(claims): ValidatedJwt,
    State(_state): State<Arc<AppState>>,
    Json(req): Json<SearchMemoryRequest>,
) -> Result<(StatusCode, Json<SearchMemoryResponse>), (StatusCode, String)> {
    // ============================================================================
    // SECURITY FIX C7-C11: Validate search query and limit
    // ============================================================================
    let validator = SearchQueryValidator::new(req.query.clone(), req.limit);
    if let Err(e) = validator.validate() {
        tracing::warn!("🚨 SEARCH VALIDATION FAILED: {} from user {}", e, claims.user_id);
        return Err((
            StatusCode::BAD_REQUEST,
            format!("Invalid search: {}", e),
        ));
    }

    info!("🔍 Searching memory for user: {}", claims.user_id);
    let results = vec![
        MemoryEntry {
            id: Uuid::new_v4().to_string(),
            content: format!("Résultat de recherche pour: {}", req.query),
            embedding: None,
            importance: 0.8,
            created_at: Utc::now(),
        },
    ];

    let response = SearchMemoryResponse {
        results,
        total: 1,
    };

    Ok((StatusCode::OK, Json(response)))
}

pub async fn list_memories(
    ValidatedJwt(claims): ValidatedJwt,
    State(_state): State<Arc<AppState>>,
) -> (StatusCode, Json<Vec<MemoryEntry>>) {
    info!("📚 Listing memories for user: {}", claims.user_id);
    let memories = vec![
        MemoryEntry {
            id: Uuid::new_v4().to_string(),
            content: "Mémoire 1: Information importante".to_string(),
            embedding: None,
            importance: 0.9,
            created_at: Utc::now(),
        },
        MemoryEntry {
            id: Uuid::new_v4().to_string(),
            content: "Mémoire 2: Contexte utilisateur".to_string(),
            embedding: None,
            importance: 0.7,
            created_at: Utc::now(),
        },
    ];

    (StatusCode::OK, Json(memories))
}
