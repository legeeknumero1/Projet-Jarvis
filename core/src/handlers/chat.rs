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
    ChatMessageValidator, InputValidator, ValidatedJwt,
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
    State(state): State<Arc<AppState>>,
    Json(req): Json<ChatRequest>,
) -> Result<(StatusCode, Json<ChatResponse>), (StatusCode, String)> {
    // 1. Validation de l'entrée (Sécurité)
    let message_validator = ChatMessageValidator::new(req.content.clone());
    if let Err(e) = message_validator.validate() {
        return Err((StatusCode::BAD_REQUEST, format!("Invalid message: {}", e)));
    }

    let sanitized_content = message_validator.sanitize();
    let user_id = &claims.user_id;

    // 2. Gérer la conversation (Base de données)
    let conv_id = if let Some(id_str) = req.conversation_id {
        Uuid::parse_str(&id_str).map_err(|_| (StatusCode::BAD_REQUEST, "Invalid UUID".to_string()))?
    } else {
        let title = if sanitized_content.len() > 30 {
            format!("{}...", &sanitized_content[0..27])
        } else {
            sanitized_content.clone()
        };
        let conv = state.db.create_conversation(user_id, &title).await
            .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;
        conv.id
    };

    // 3. Sauvegarder le message utilisateur
    state.db.add_message(conv_id, "user", &sanitized_content).await
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    // 4. Appeler le Bridge Python (IA)
    let client = reqwest::Client::new();
    let bridge_url = format!("{}/api/llm/generate", state.python_bridges_url);
    
    // Note: Dans un environnement réel, on passerait le token JWT reçu ou un token de service
    let response = client.post(&bridge_url)
        .header("Authorization", format!("Bearer dev-token-placeholder")) // À ajuster selon auth inter-service
        .json(&serde_json::json!({
            "prompt": sanitized_content,
            "user_id": user_id
        }))
        .send()
        .await
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, format!("Bridge error: {}", e)))?;

    if !response.status().is_success() {
        return Err((StatusCode::BAD_GATEWAY, "Python Bridge returned an error".to_string()));
    }

    let ai_data: serde_json::Value = response.json().await
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, format!("Parsing error: {}", e)))?;
    
    let ai_content = ai_data["text"].as_str().unwrap_or("Désolé, je n'ai pas pu générer de réponse.");

    // 5. Sauvegarder la réponse de l'IA
    let ai_msg = state.db.add_message(conv_id, "assistant", ai_content).await
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    let response = ChatResponse {
        id: ai_msg.id.to_string(),
        conversation_id: conv_id.to_string(),
        role: "assistant".to_string(),
        content: ai_content.to_string(),
        timestamp: Utc::now(),
        tokens: ai_data["tokens_generated"].as_i64().map(|t| t as i32),
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
    State(state): State<Arc<AppState>>,
) -> Result<(StatusCode, Json<Vec<Conversation>>), (StatusCode, String)> {
    info!(" Listing conversations for user: {}", claims.user_id);
    
    let conversations = state.db.list_conversations(&claims.user_id).await
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    let result = conversations.into_iter().map(|c| Conversation {
        id: c.id.to_string(),
        title: c.title,
        summary: None,
        created_at: c.created_at.into(),
        updated_at: c.updated_at.into(),
        message_count: c.message_count,
    }).collect();

    Ok((StatusCode::OK, Json(result)))
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
    State(state): State<Arc<AppState>>,
    Path(id): Path<String>,
) -> Result<(StatusCode, Json<Vec<ChatResponse>>), (StatusCode, String)> {
    let conv_id = Uuid::parse_str(&id).map_err(|_| (StatusCode::BAD_REQUEST, "Invalid UUID".to_string()))?;

    info!(" Getting history for user: {}", claims.user_id);
    
    let messages = state.db.get_messages(conv_id).await
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    let history = messages.into_iter().map(|m| ChatResponse {
        id: m.id.to_string(),
        conversation_id: id.clone(),
        role: m.role,
        content: m.content,
        timestamp: m.created_at.into(),
        tokens: None,
    }).collect();

    Ok((StatusCode::OK, Json(history)))
}

pub async fn delete_conversation(
    ValidatedJwt(claims): ValidatedJwt,
    State(state): State<Arc<AppState>>,
    Path(id): Path<String>,
) -> Result<StatusCode, (StatusCode, String)> {
    let conv_id = Uuid::parse_str(&id).map_err(|_| (StatusCode::BAD_REQUEST, "Invalid UUID".to_string()))?;

    info!(" Deleting conversation for user: {}", claims.user_id);
    
    state.db.delete_conversation(conv_id).await
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    Ok(StatusCode::OK)
}


pub async fn websocket_handler() -> &'static str {
    "WebSocket handler - pour WebSocket temps réel"
}
