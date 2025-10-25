use axum::{
    extract::State,
    http::StatusCode,
    Json,
};
use chrono::Utc;
use std::sync::Arc;
use uuid::Uuid;

use crate::models::{
    AppState, MemoryEntry, AddMemoryRequest, SearchMemoryRequest, SearchMemoryResponse,
};

pub async fn add_memory(
    State(_state): State<Arc<AppState>>,
    Json(req): Json<AddMemoryRequest>,
) -> (StatusCode, Json<MemoryEntry>) {
    let memory = MemoryEntry {
        id: Uuid::new_v4().to_string(),
        content: req.content,
        embedding: None,
        importance: req.importance.unwrap_or(0.5),
        created_at: Utc::now(),
    };

    (StatusCode::OK, Json(memory))
}

pub async fn search_memory(
    State(_state): State<Arc<AppState>>,
    Json(req): Json<SearchMemoryRequest>,
) -> (StatusCode, Json<SearchMemoryResponse>) {
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

    (StatusCode::OK, Json(response))
}

pub async fn list_memories(
    State(_state): State<Arc<AppState>>,
) -> (StatusCode, Json<Vec<MemoryEntry>>) {
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
