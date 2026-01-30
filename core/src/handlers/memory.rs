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
    State(state): State<Arc<AppState>>,
    Json(req): Json<AddMemoryRequest>,
) -> Result<(StatusCode, Json<MemoryEntry>), (StatusCode, String)> {
    // ============================================================================
    // SECURITY FIX C7-C11: Validate memory content and importance
    // ============================================================================
    let validator = MemoryContentValidator::new(req.content.clone(), req.importance);
    if let Err(e) = validator.validate() {
        tracing::warn!(" MEMORY VALIDATION FAILED: {} from user {}", e, claims.user_id);
        return Err((
            StatusCode::BAD_REQUEST,
            format!("Invalid memory: {}", e),
        ));
    }

    info!(" Adding memory for user: {}", claims.user_id);
    
    // 1. Generate Embedding via Ollama
    let embedding = state.ollama.get_embeddings(&req.content).await
        .map_err(|e| {
            tracing::error!("Failed to generate embedding: {}", e);
            (StatusCode::INTERNAL_SERVER_ERROR, format!("Embedding error: {}", e))
        })?;

    // 2. Store in Qdrant
    let memory_id = Uuid::new_v4().to_string();
    state.qdrant.add_memory(&memory_id, &req.content, embedding, &claims.user_id).await
        .map_err(|e| {
            tracing::error!("Failed to save to Qdrant: {}", e);
            (StatusCode::INTERNAL_SERVER_ERROR, format!("Storage error: {}", e))
        })?;

    let memory = MemoryEntry {
        id: memory_id,
        content: req.content,
        embedding: None, // We don't return the vector to client to save bandwidth
        importance: req.importance.unwrap_or(0.5),
        created_at: Utc::now(),
    };

    Ok((StatusCode::OK, Json(memory)))
}

pub async fn search_memory(
    ValidatedJwt(claims): ValidatedJwt,
    State(state): State<Arc<AppState>>,
    Json(req): Json<SearchMemoryRequest>,
) -> Result<(StatusCode, Json<SearchMemoryResponse>), (StatusCode, String)> {
    // ============================================================================
    // SECURITY FIX C7-C11: Validate search query and limit
    // ============================================================================
    let validator = SearchQueryValidator::new(req.query.clone(), req.limit);
    if let Err(e) = validator.validate() {
        tracing::warn!(" SEARCH VALIDATION FAILED: {} from user {}", e, claims.user_id);
        return Err((
            StatusCode::BAD_REQUEST,
            format!("Invalid search: {}", e),
        ));
    }

    info!(" Searching memory for user: {}", claims.user_id);
    
    // 1. Generate Embedding for query
    let embedding = state.ollama.get_embeddings(&req.query).await
        .map_err(|e| {
            tracing::error!("Failed to generate query embedding: {}", e);
            (StatusCode::INTERNAL_SERVER_ERROR, format!("Embedding error: {}", e))
        })?;

    // 2. Search in Qdrant
    let limit = req.limit.unwrap_or(5) as usize;
    let results_text = state.qdrant.search_memory(embedding, limit, &claims.user_id).await
        .map_err(|e| {
            tracing::error!("Failed to search Qdrant: {}", e);
            (StatusCode::INTERNAL_SERVER_ERROR, format!("Search error: {}", e))
        })?;

    // 3. Convert results
    let results: Vec<MemoryEntry> = results_text.into_iter().map(|text| {
        MemoryEntry {
            id: Uuid::new_v4().to_string(), // Qdrant currently only returns payload text, not ID. Should be improved later.
            content: text,
            embedding: None,
            importance: 1.0, // Default relevance
            created_at: Utc::now(),
        }
    }).collect();

    let total = results.len();

    let response = SearchMemoryResponse {
        results,
        total: total as i32,
    };

    Ok((StatusCode::OK, Json(response)))
}

pub async fn list_memories(
    ValidatedJwt(claims): ValidatedJwt,
    State(_state): State<Arc<AppState>>,
) -> (StatusCode, Json<Vec<MemoryEntry>>) {
    info!(" Listing memories for user: {}", claims.user_id);
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
