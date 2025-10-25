use axum::{
    extract::{State, Path},
    http::StatusCode,
    Json,
};
use chrono::Utc;
use std::sync::Arc;
use uuid::Uuid;

use crate::models::{AppState, ChatRequest, ChatResponse, Conversation};

pub async fn send_message(
    State(_state): State<Arc<AppState>>,
    Json(req): Json<ChatRequest>,
) -> (StatusCode, Json<ChatResponse>) {
    let conversation_id = req.conversation_id.unwrap_or_else(|| Uuid::new_v4().to_string());
    let message_id = Uuid::new_v4().to_string();

    let response = ChatResponse {
        id: message_id,
        conversation_id: conversation_id.clone(),
        role: "assistant".to_string(),
        content: format!("Réponse mock: {}", req.content),
        timestamp: Utc::now(),
        tokens: Some(50),
    };

    (StatusCode::OK, Json(response))
}

pub async fn list_conversations(
    State(_state): State<Arc<AppState>>,
) -> (StatusCode, Json<Vec<Conversation>>) {
    let conversations = vec![
        Conversation {
            id: Uuid::new_v4().to_string(),
            title: "Conversation 1".to_string(),
            summary: Some("Résumé de la conversation 1".to_string()),
            created_at: Utc::now(),
            updated_at: Utc::now(),
            message_count: 5,
        },
    ];

    (StatusCode::OK, Json(conversations))
}

pub async fn get_history(
    State(_state): State<Arc<AppState>>,
    Path(_id): Path<String>,
) -> (StatusCode, Json<Vec<ChatResponse>>) {
    let history = vec![
        ChatResponse {
            id: Uuid::new_v4().to_string(),
            conversation_id: "conv_1".to_string(),
            role: "user".to_string(),
            content: "Bonjour Jarvis".to_string(),
            timestamp: Utc::now(),
            tokens: Some(10),
        },
        ChatResponse {
            id: Uuid::new_v4().to_string(),
            conversation_id: "conv_1".to_string(),
            role: "assistant".to_string(),
            content: "Bonjour! Comment puis-je t'aider?".to_string(),
            timestamp: Utc::now(),
            tokens: Some(20),
        },
    ];

    (StatusCode::OK, Json(history))
}

pub async fn delete_conversation(
    State(_state): State<Arc<AppState>>,
    Path(_id): Path<String>,
) -> StatusCode {
    StatusCode::OK
}

pub async fn websocket_handler() -> &'static str {
    "WebSocket handler - pour WebSocket temps réel"
}
