use axum::{
    routing::{get, post},
    Router,
};
use std::sync::Arc;
use tower_http::cors::CorsLayer;
use tracing::info;

mod handlers;
mod models;
mod services;

use handlers::{chat, health, memory, stt, tts};
use models::AppState;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize tracing
    tracing_subscriber::fmt::init();

    info!("🦀 Jarvis Rust Backend v1.9.0 starting...");

    // Create application state
    let state = Arc::new(AppState {
        python_bridges_url: "http://localhost:8005".to_string(),
        audio_engine_url: "http://localhost:8004".to_string(),
    });

    // Build router
    let app = Router::new()
        // Health endpoints
        .route("/health", get(health::health_check))
        .route("/ready", get(health::readiness_check))
        .route("/metrics", get(health::metrics))

        // Chat endpoints
        .route("/api/chat", post(chat::send_message))
        .route("/api/chat/conversations", get(chat::list_conversations))
        .route("/api/chat/history/:id", get(chat::get_history))
        .route("/api/chat/conversation/:id", axum::routing::delete(chat::delete_conversation))

        // STT/TTS endpoints
        .route("/api/voice/transcribe", post(stt::transcribe))
        .route("/api/voice/synthesize", post(tts::synthesize))
        .route("/api/voice/voices", get(tts::list_voices))
        .route("/api/voice/languages", get(stt::list_languages))

        // Memory endpoints
        .route("/api/memory/add", post(memory::add_memory))
        .route("/api/memory/search", post(memory::search_memory))
        .route("/api/memory/list", get(memory::list_memories))

        // WebSocket
        .route("/ws", axum::routing::get(chat::websocket_handler))

        .layer(CorsLayer::permissive())
        .with_state(state);

    let listener = tokio::net::TcpListener::bind("0.0.0.0:8100").await?;
    info!("✅ Server listening on http://0.0.0.0:8100");
    info!("📊 Health check: http://localhost:8100/health");
    info!("💬 Chat API: POST http://localhost:8100/api/chat");
    info!("🎤 STT API: POST http://localhost:8100/api/voice/transcribe");
    info!("🔊 TTS API: POST http://localhost:8100/api/voice/synthesize");

    axum::serve(listener, app).await?;

    Ok(())
}
