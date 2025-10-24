//! Handlers de chat pour Jarvis Rust Backend
//! 
//! Endpoints équivalents aux routes chat.py Python
//! avec streaming et gestion de conversation

use axum::{
    extract::{Query, State},
    http::StatusCode,
    response::IntoResponse,
    Json,
};
use std::time::Instant;
use uuid::Uuid;

use crate::{
    models::{GetHistoryRequest, SendMessageRequest, SendMessageResponse},
    ApiResponse, AppState,
};

/// POST /api/chat - Envoi d'un message à l'IA
/// 
/// Endpoint principal pour l'interaction avec l'IA.
/// Gère la conversation, la mémoire contextuelle et la génération de réponse.
pub async fn send_message(
    State(state): State<AppState>,
    Json(request): Json<SendMessageRequest>,
) -> impl IntoResponse {
    let start_time = Instant::now();

    // Validation du message
    if request.message.trim().is_empty() {
        return (
            StatusCode::BAD_REQUEST,
            Json(ApiResponse::<()>::error("Le message ne peut pas être vide")),
        );
    }

    // Limitation de taille du message
    if request.message.len() > 10000 {
        return (
            StatusCode::BAD_REQUEST,
            Json(ApiResponse::<()>::error(
                "Le message ne peut pas dépasser 10000 caractères",
            )),
        );
    }

    tracing::info!(
        "💬 Nouveau message reçu: {} caractères, conversation_id: {:?}",
        request.message.len(),
        request.conversation_id
    );

    match state.services.chat.process_message(request).await {
        Ok(response) => {
            let response_time = start_time.elapsed().as_millis() as u64;
            
            tracing::info!(
                "✅ Réponse générée en {}ms, tokens: {}",
                response_time,
                response.usage.total_tokens
            );

            (StatusCode::OK, Json(ApiResponse::ok(response)))
        }
        Err(e) => {
            tracing::error!("❌ Erreur lors du traitement du message: {}", e);
            
            let error_message = match e.downcast_ref::<crate::services::chat::ChatError>() {
                Some(chat_err) => match chat_err {
                    crate::services::chat::ChatError::LLMTimeout => {
                        "Timeout lors de la génération de la réponse IA"
                    }
                    crate::services::chat::ChatError::LLMError(msg) => {
                        &format!("Erreur IA: {}", msg)
                    }
                    crate::services::chat::ChatError::MemoryError(msg) => {
                        &format!("Erreur mémoire: {}", msg)
                    }
                    crate::services::chat::ChatError::DatabaseError(msg) => {
                        &format!("Erreur base de données: {}", msg)
                    }
                    crate::services::chat::ChatError::ValidationError(msg) => msg,
                },
                None => "Erreur interne du serveur",
            };

            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(ApiResponse::<()>::error(error_message)),
            )
        }
    }
}

/// GET /api/chat/history - Récupération de l'historique des conversations
/// 
/// Endpoint pour récupérer l'historique avec pagination et filtres.
pub async fn get_history(
    State(state): State<AppState>,
    Query(params): Query<GetHistoryRequest>,
) -> impl IntoResponse {
    tracing::info!(
        "📚 Récupération historique - conversation_id: {:?}, limit: {:?}",
        params.conversation_id,
        params.limit
    );

    // Validation des paramètres
    let limit = params.limit.unwrap_or(50).min(500); // Max 500 messages
    let offset = params.offset.unwrap_or(0);

    if limit == 0 {
        return (
            StatusCode::BAD_REQUEST,
            Json(ApiResponse::<()>::error("La limite doit être supérieure à 0")),
        );
    }

    match state
        .services
        .chat
        .get_conversation_history(params.conversation_id, limit, offset, params.since)
        .await
    {
        Ok(response) => {
            tracing::info!(
                "✅ Historique récupéré: {} messages, total: {}",
                response.messages.len(),
                response.total_count
            );

            (StatusCode::OK, Json(ApiResponse::ok(response)))
        }
        Err(e) => {
            tracing::error!("❌ Erreur lors de la récupération de l'historique: {}", e);

            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(ApiResponse::<()>::error(format!(
                    "Erreur récupération historique: {}",
                    e
                ))),
            )
        }
    }
}

/// DELETE /api/chat/conversation/{id} - Suppression d'une conversation
/// 
/// Endpoint pour supprimer une conversation et tous ses messages.
pub async fn delete_conversation(
    State(state): State<AppState>,
    axum::extract::Path(conversation_id): axum::extract::Path<Uuid>,
) -> impl IntoResponse {
    tracing::info!("🗑️ Suppression conversation: {}", conversation_id);

    match state
        .services
        .chat
        .delete_conversation(conversation_id)
        .await
    {
        Ok(deleted_count) => {
            tracing::info!(
                "✅ Conversation supprimée: {} messages supprimés",
                deleted_count
            );

            (
                StatusCode::OK,
                Json(ApiResponse::ok(serde_json::json!({
                    "conversation_id": conversation_id,
                    "deleted_messages": deleted_count
                }))),
            )
        }
        Err(e) => {
            tracing::error!("❌ Erreur lors de la suppression: {}", e);

            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(ApiResponse::<()>::error(format!(
                    "Erreur suppression conversation: {}",
                    e
                ))),
            )
        }
    }
}

/// GET /api/chat/conversations - Liste toutes les conversations
/// 
/// Endpoint pour récupérer la liste de toutes les conversations avec pagination.
pub async fn list_conversations(
    State(state): State<AppState>,
    Query(params): Query<serde_json::Value>,
) -> impl IntoResponse {
    let limit = params
        .get("limit")
        .and_then(|v| v.as_u64())
        .unwrap_or(20)
        .min(100) as u32;
    let offset = params
        .get("offset")
        .and_then(|v| v.as_u64())
        .unwrap_or(0) as u32;

    tracing::info!("📋 Liste conversations - limit: {}, offset: {}", limit, offset);

    match state
        .services
        .chat
        .list_conversations(limit, offset)
        .await
    {
        Ok(conversations) => {
            tracing::info!("✅ {} conversations trouvées", conversations.len());

            (
                StatusCode::OK,
                Json(ApiResponse::ok(serde_json::json!({
                    "conversations": conversations,
                    "count": conversations.len(),
                    "limit": limit,
                    "offset": offset
                }))),
            )
        }
        Err(e) => {
            tracing::error!("❌ Erreur lors de la récupération des conversations: {}", e);

            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(ApiResponse::<()>::error(format!(
                    "Erreur récupération conversations: {}",
                    e
                ))),
            )
        }
    }
}