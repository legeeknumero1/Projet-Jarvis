use axum::{
    extract::{Path, State},
    http::StatusCode,
    Json,
};
use chrono::Utc;
use std::sync::Arc;
use tracing::info;
use uuid::Uuid;

use crate::middleware::{
    ChatMessageValidator, ConversationIdValidator, InputValidator, ValidatedJwt,
};
use crate::models::{AppState, ChatRequest, ChatResponse, Conversation};

/// Chat endpoint
#[utoipa::path(
    post,
    path = "/chat",
    request_body = ChatRequest,
    responses(
        (status = 200, description = "Chat response", body = ChatResponse),
        (status = 400, description = "Invalid request")
    ),
    security(
        ("bearer_auth" = [])
    )
)]
pub async fn chat_endpoint(
    ValidatedJwt(claims): ValidatedJwt,
    State(_state): State<Arc<AppState>>,
    Json(req): Json<ChatRequest>,
) -> Result<(StatusCode, Json<ChatResponse>), (StatusCode, String)> {
    // ============================================================================
    // SECURITY FIX C7-C11: Validate chat message and conversation ID
    // ============================================================================

    // Validate chat message content
    let message_validator = ChatMessageValidator::new(req.content.clone());
    if let Err(e) = message_validator.validate() {
        tracing::warn!(
            " CHAT VALIDATION FAILED: {} from user {}",
            e,
            claims.user_id
        );
        return Err((StatusCode::BAD_REQUEST, format!("Invalid message: {}", e)));
    }

    // Validate conversation ID if provided
    if let Some(ref conv_id) = req.conversation_id {
        let id_validator = ConversationIdValidator::new(conv_id.clone());
        if let Err(e) = id_validator.validate() {
            tracing::warn!(
                " CONVERSATION ID VALIDATION FAILED: {} from user {}",
                e,
                claims.user_id
            );
            return Err((
                StatusCode::BAD_REQUEST,
                format!("Invalid conversation ID: {}", e),
            ));
        }
    }

    info!(" Chat message from user: {}", claims.user_id);
    let conversation_id = req
        .conversation_id
        .unwrap_or_else(|| Uuid::new_v4().to_string());
    let message_id = Uuid::new_v4().to_string();

    // Sanitize message content for any XSS attempts
    let sanitized_content = message_validator.sanitize();

    let response = ChatResponse {
        id: message_id,
        conversation_id: conversation_id.clone(),
        role: "assistant".to_string(),
        content: format!("Réponse mock: {}", sanitized_content),
        timestamp: Utc::now(),
        tokens: Some(50),
    };

    Ok((StatusCode::OK, Json(response)))
}

/// Get conversations list
#[utoipa::path(
    get,
    path = "/chat/conversations",
    responses(
        (status = 200, description = "List of conversations", body = Vec<Conversation>)
    ),
    security(
        ("bearer_auth" = [])
    )
)]
pub async fn get_conversations(
    ValidatedJwt(claims): ValidatedJwt,
    State(_state): State<Arc<AppState>>,
) -> (StatusCode, Json<Vec<Conversation>>) {
    info!(" Listing conversations for user: {}", claims.user_id);
    let conversations = vec![Conversation {
        id: Uuid::new_v4().to_string(),
        title: "Conversation 1".to_string(),
        summary: Some("Résumé de la conversation 1".to_string()),
        created_at: Utc::now(),
        updated_at: Utc::now(),
        message_count: 5,
    }];

    (StatusCode::OK, Json(conversations))
}

/// Get conversation history
#[utoipa::path(
    get,
    path = "/chat/history/{id}",
    params(
        ("id" = String, Path, description = "Conversation ID")
    ),
    responses(
        (status = 200, description = "Conversation history", body = Vec<ChatResponse>),
        (status = 400, description = "Invalid conversation ID")
    ),
    security(
        ("bearer_auth" = [])
    )
)]
pub async fn get_history(
    ValidatedJwt(claims): ValidatedJwt,
    State(_state): State<Arc<AppState>>,
    Path(id): Path<String>,
) -> Result<(StatusCode, Json<Vec<ChatResponse>>), (StatusCode, String)> {
    // ============================================================================
    // SECURITY FIX C7-C11: Validate conversation ID
    // ============================================================================
    let id_validator = ConversationIdValidator::new(id.clone());
    if let Err(e) = id_validator.validate() {
        tracing::warn!(
            " HISTORY VALIDATION FAILED: {} from user {}",
            e,
            claims.user_id
        );
        return Err((
            StatusCode::BAD_REQUEST,
            format!("Invalid conversation ID: {}", e),
        ));
    }

    info!(" Getting history for user: {}", claims.user_id);
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

    Ok((StatusCode::OK, Json(history)))
}

pub async fn delete_conversation(
    ValidatedJwt(claims): ValidatedJwt,
    State(_state): State<Arc<AppState>>,
    Path(id): Path<String>,
) -> Result<StatusCode, (StatusCode, String)> {
    // ============================================================================
    // SECURITY FIX C7-C11: Validate conversation ID
    // ============================================================================
    let id_validator = ConversationIdValidator::new(id.clone());
    if let Err(e) = id_validator.validate() {
        tracing::warn!(
            " DELETE VALIDATION FAILED: {} from user {}",
            e,
            claims.user_id
        );
        return Err((
            StatusCode::BAD_REQUEST,
            format!("Invalid conversation ID: {}", e),
        ));
    }

    info!(" Deleting conversation for user: {}", claims.user_id);
    Ok(StatusCode::OK)
}

pub async fn websocket_handler() -> &'static str {
    "WebSocket handler - pour WebSocket temps réel"
}
