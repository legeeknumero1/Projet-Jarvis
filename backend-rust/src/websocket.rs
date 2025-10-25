//! WebSocket handler pour Jarvis Rust Backend
//! 
//! Gestion des connexions WebSocket temps réel pour:
//! - Chat en streaming
//! - Audio en temps réel
//! - Notifications système
//! - Statut des services

use axum::extract::ws::{Message, WebSocket};
use futures_util::{sink::SinkExt, stream::StreamExt};
use serde_json;
use std::sync::Arc;
use tokio::sync::broadcast;
use tracing::{info, warn, error};
use uuid::Uuid;

use crate::{
    models::{WSIncomingMessage, WSOutgoingMessage},
    AppState,
};

/// Type de broadcast channel pour les messages WebSocket
pub type WSBroadcaster = broadcast::Sender<WSOutgoingMessage>;

/// État d'une connexion WebSocket
#[derive(Debug)]
pub struct WSConnection {
    pub id: Uuid,
    pub created_at: chrono::DateTime<chrono::Utc>,
    pub subscribed_channels: Vec<String>,
}

/// Gestionnaire principal des connexions WebSocket
pub async fn handle_socket(socket: WebSocket, state: AppState) {
    let connection_id = Uuid::new_v4();
    let connection = WSConnection {
        id: connection_id,
        created_at: chrono::Utc::now(),
        subscribed_channels: Vec::new(),
    };

    info!("🔌 Nouvelle connexion WebSocket: {}", connection_id);

    let (mut sender, mut receiver) = socket.split();

    // Channel pour la communication bidirectionnelle
    let (tx, mut rx) = tokio::sync::mpsc::channel::<WSOutgoingMessage>(100);

    // Task pour envoyer les messages sortants
    let send_task = tokio::spawn(async move {
        while let Some(msg) = rx.recv().await {
            match serde_json::to_string(&msg) {
                Ok(json_str) => {
                    if let Err(e) = sender.send(Message::Text(json_str)).await {
                        warn!("Erreur envoi message WebSocket: {}", e);
                        break;
                    }
                }
                Err(e) => {
                    error!("Erreur sérialisation message WebSocket: {}", e);
                }
            }
        }
    });

    // Task pour recevoir et traiter les messages entrants
    let state_clone = state.clone();
    let tx_clone = tx.clone();
    let receive_task = tokio::spawn(async move {
        while let Some(msg) = receiver.next().await {
            match msg {
                Ok(Message::Text(text)) => {
                    if let Err(e) = handle_incoming_message(
                        &text,
                        &state_clone,
                        &tx_clone,
                        &connection,
                    ).await {
                        error!("Erreur traitement message: {}", e);
                        
                        let error_msg = WSOutgoingMessage::Error {
                            message: e.to_string(),
                            code: 500,
                        };
                        
                        if let Err(send_err) = tx_clone.send(error_msg).await {
                            error!("Erreur envoi message d'erreur: {}", send_err);
                        }
                    }
                }
                Ok(Message::Binary(_)) => {
                    warn!("Messages binaires non supportés pour le moment");
                }
                Ok(Message::Ping(data)) => {
                    if let Err(e) = tx_clone.send(WSOutgoingMessage::Pong).await {
                        error!("Erreur envoi pong: {}", e);
                    }
                }
                Ok(Message::Pong(_)) => {
                    // Ignore les pongs
                }
                Ok(Message::Close(_)) => {
                    info!("Connexion fermée côté client: {}", connection_id);
                    break;
                }
                Err(e) => {
                    error!("Erreur WebSocket: {}", e);
                    break;
                }
            }
        }
    });

    // Attendre que l'une des tâches se termine
    tokio::select! {
        _ = send_task => {
            info!("Task d'envoi terminée pour {}", connection_id);
        }
        _ = receive_task => {
            info!("Task de réception terminée pour {}", connection_id);
        }
    }

    info!("🔌 Connexion WebSocket fermée: {}", connection_id);
}

/// Traite un message entrant du WebSocket
async fn handle_incoming_message(
    text: &str,
    state: &AppState,
    tx: &tokio::sync::mpsc::Sender<WSOutgoingMessage>,
    connection: &WSConnection,
) -> anyhow::Result<()> {
    let incoming: WSIncomingMessage = serde_json::from_str(text)?;

    match incoming {
        WSIncomingMessage::ChatMessage { content, conversation_id } => {
            handle_chat_message(content, conversation_id, state, tx).await?;
        }
        
        WSIncomingMessage::AudioData { data, format } => {
            handle_audio_data(data, format, state, tx).await?;
        }
        
        WSIncomingMessage::Ping => {
            tx.send(WSOutgoingMessage::Pong).await?;
        }
        
        WSIncomingMessage::Subscribe { channels } => {
            handle_subscription(channels, connection, tx).await?;
        }
    }

    Ok(())
}

/// Traite un message de chat via WebSocket
async fn handle_chat_message(
    content: String,
    conversation_id: Option<Uuid>,
    state: &AppState,
    tx: &tokio::sync::mpsc::Sender<WSOutgoingMessage>,
) -> anyhow::Result<()> {
    info!("💬 Message chat WebSocket: {} caractères", content.len());

    // Créer une requête de message
    let request = crate::models::SendMessageRequest {
        message: content,
        conversation_id,
        stream: Some(true), // Toujours en streaming via WebSocket
        model: None,
        temperature: None,
        max_tokens: None,
    };

    // Traiter le message via le service de chat
    match state.services.chat.process_message(request).await {
        Ok(response) => {
            let ws_response = WSOutgoingMessage::ChatResponse {
                message: response.message,
                conversation_id: response.conversation_id,
            };
            
            tx.send(ws_response).await?;
            info!("✅ Réponse chat envoyée via WebSocket");
        }
        Err(e) => {
            error!("❌ Erreur traitement message chat: {}", e);
            
            let error_msg = WSOutgoingMessage::Error {
                message: format!("Erreur traitement message: {}", e),
                code: 500,
            };
            
            tx.send(error_msg).await?;
        }
    }

    Ok(())
}

/// Traite des données audio via WebSocket
async fn handle_audio_data(
    data: String,
    format: crate::models::AudioFormat,
    state: &AppState,
    tx: &tokio::sync::mpsc::Sender<WSOutgoingMessage>,
) -> anyhow::Result<()> {
    info!("🎤 Données audio WebSocket: {} caractères, format: {:?}", 
          data.len(), format);

    // Créer une requête de transcription
    let transcribe_request = crate::models::TranscribeRequest {
        audio_data: data,
        language: Some("auto".to_string()),
        prompt: None,
    };

    // Transcrire l'audio
    match state.services.voice.transcribe_audio(transcribe_request).await {
        Ok(transcription) => {
            info!("✅ Transcription: '{}'", transcription.text);

            // Si transcription réussie, traiter comme message de chat
            if !transcription.text.trim().is_empty() {
                handle_chat_message(transcription.text, None, state, tx).await?;
            }
        }
        Err(e) => {
            error!("❌ Erreur transcription audio: {}", e);
            
            let error_msg = WSOutgoingMessage::Error {
                message: format!("Erreur transcription: {}", e),
                code: 500,
            };
            
            tx.send(error_msg).await?;
        }
    }

    Ok(())
}

/// Traite une demande d'abonnement à des channels
async fn handle_subscription(
    channels: Vec<String>,
    connection: &WSConnection,
    tx: &tokio::sync::mpsc::Sender<WSOutgoingMessage>,
) -> anyhow::Result<()> {
    info!("📺 Abonnement aux channels: {:?} pour connexion {}", 
          channels, connection.id);

    // Pour le moment, on accepte tous les abonnements
    // TODO: Implémenter la logique de channels/room

    let confirmation = WSOutgoingMessage::SystemStatus {
        status: crate::models::HealthStatus {
            status: crate::models::ServiceStatus::Healthy,
            version: env!("CARGO_PKG_VERSION").to_string(),
            uptime_secs: 0, // TODO: Calculer l'uptime réel
            services: std::collections::HashMap::new(),
            memory_usage: crate::models::MemoryUsage {
                used_mb: 0,
                total_mb: 0,
                percentage: 0.0,
            },
            timestamp: chrono::Utc::now(),
        },
    };

    tx.send(confirmation).await?;
    info!("✅ Confirmation abonnement envoyée");

    Ok(())
}

/// Broadcaster global pour envoyer des messages à toutes les connexions
/// (sera utilisé pour les notifications système)
pub fn create_broadcaster() -> WSBroadcaster {
    let (tx, _) = broadcast::channel(1000);
    tx
}