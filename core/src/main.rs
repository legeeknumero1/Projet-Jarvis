use axum::{
    routing::{get, post},
    Router,
    http::HeaderValue,
};
use std::sync::Arc;
use std::time::Duration;
use tower_http::cors::{CorsLayer, AllowOrigin};
use tracing::{info, error};

mod handlers;
mod models;
mod services;

use handlers::{chat, health, memory, stt, tts};
use models::AppState;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize tracing
    tracing_subscriber::fmt::init();

    // Load environment variables from .env file
    dotenv::dotenv().ok();

    info!("🦀 Jarvis Rust Backend v1.9.0 starting...");

    // Configuration depuis les variables d'environnement
    let host = std::env::var("HOST").unwrap_or_else(|_| "0.0.0.0".to_string());
    let port = std::env::var("PORT").unwrap_or_else(|_| "8100".to_string());
    let python_bridges_url = std::env::var("PYTHON_BRIDGES_URL")
        .unwrap_or_else(|_| "http://localhost:8005".to_string());
    let audio_engine_url = std::env::var("AUDIO_ENGINE_URL")
        .unwrap_or_else(|_| "http://localhost:8004".to_string());
    let cors_origins = std::env::var("CORS_ORIGINS")
        .unwrap_or_else(|_| "http://localhost:3000".to_string());
    info!("📋 Configuration:");
    info!("  - Server: {}:{}", host, port);
    info!("  - Python Bridges: {}", python_bridges_url);
    info!("  - Audio Engine: {}", audio_engine_url);
    info!("  - CORS Origins: {}", cors_origins);

    // Create application state
    let state = Arc::new(AppState {
        python_bridges_url,
        audio_engine_url,
    });

    // Build CORS layer with restricted origins (NOT PERMISSIVE)
    let allowed_origins: Vec<HeaderValue> = cors_origins
        .split(',')
        .filter_map(|origin| {
            origin.trim().parse::<HeaderValue>().ok()
        })
        .collect();

    let cors = CorsLayer::new()
        .allow_origin(if allowed_origins.is_empty() {
            AllowOrigin::any()
        } else {
            AllowOrigin::list(allowed_origins)
        })
        .allow_methods([
            axum::http::Method::GET,
            axum::http::Method::POST,
            axum::http::Method::DELETE,
            axum::http::Method::OPTIONS,
        ])
        .allow_headers([
            axum::http::header::CONTENT_TYPE,
            axum::http::header::AUTHORIZATION,
        ])
        .allow_credentials(true)
        .max_age(Duration::from_secs(3600));

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

        // Security layers
        .layer(cors)
        .with_state(state);

    let addr = format!("{}:{}", host, port);
    match tokio::net::TcpListener::bind(&addr).await {
        Ok(listener) => {
            info!("✅ Server listening on http://{}", addr);
            info!("📊 Health check: http://{}/health", addr);
            info!("💬 Chat API: POST http://{}/api/chat", addr);
            info!("🎤 STT API: POST http://{}/api/voice/transcribe", addr);
            info!("🔊 TTS API: POST http://{}/api/voice/synthesize", addr);

            axum::serve(listener, app).await?;
        }
        Err(e) => {
            error!("❌ Erreur liaison au serveur {}: {}", addr, e);
            return Err(e.into());
        }
    }

    Ok(())
}
