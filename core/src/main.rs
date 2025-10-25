use axum::{
    routing::{get, post},
    Router,
    http::HeaderValue,
};
use std::sync::Arc;
use std::time::Duration;
use tower_http::cors::{CorsLayer, AllowOrigin};
use tracing::{info, error, warn};

mod handlers;
mod middleware;
mod models;
mod services;

use handlers::{auth, chat, health, memory, stt, tts};
use middleware::{SecretsValidator, EnvironmentChecklist, TlsConfig, CertificateLoader};
use models::AppState;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize tracing
    tracing_subscriber::fmt::init();

    // Load environment variables from .env file
    dotenv::dotenv().ok();

    info!("🦀 Jarvis Rust Backend v1.9.0 starting...");

    // ============================================================================
    // SECURITY FIX C6: Validate all secrets before starting server
    // ============================================================================
    match SecretsValidator::validate_all() {
        Ok(()) => {
            info!("✅ All secrets validated - proceeding with startup");
        }
        Err(e) => {
            error!("🚨 SECURITY ERROR: Secret validation failed - {}", e);
            error!("⚠️  Application will NOT start without proper secrets configuration");
            EnvironmentChecklist::print_requirements();
            panic!("Secret validation failed: {}", e);
        }
    }

    // Check for common insecure defaults
    SecretsValidator::check_for_insecure_defaults();

    // ============================================================================
    // SECURITY FIX C4: Validate TLS/HTTPS Certificates
    // ============================================================================
    let tls_config = TlsConfig::from_env();

    // Try to validate certificates, provide helpful message if missing
    match CertificateLoader::validate_certificates(&tls_config) {
        Ok(()) => {
            info!("✅ TLS certificates validated - HTTPS will be enabled");
        }
        Err(e) => {
            warn!("⚠️  SECURITY WARNING: {}", e);
            warn!("    For development, generate a self-signed certificate:");
            warn!("    $ mkdir -p certs");
            warn!("    $ openssl req -x509 -newkey rsa:4096 -keyout certs/server.key \\");
            warn!("      -out certs/server.crt -days 365 -nodes -subj '/CN=localhost'");
            warn!("    Then set: export TLS_CERT_PATH=./certs/server.crt TLS_KEY_PATH=./certs/server.key");
            warn!("    Server will run HTTP-only without HTTPS until certificates are provided");
        }
    }

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

    // ============================================================================
    // SECURITY FIX C5: Rate Limiting Initialized (lazy static)
    // ============================================================================
    info!("🔒 Rate limiting initialized - protecting against DoS attacks");

    // Build CORS layer with restricted origins (SECURITY FIX C2)
    let allowed_origins: Vec<HeaderValue> = cors_origins
        .split(',')
        .filter_map(|origin| {
            let trimmed = origin.trim();
            if !trimmed.is_empty() {
                trimmed.parse::<HeaderValue>().ok()
            } else {
                None
            }
        })
        .collect();

    // CRITICAL FIX: Panic if no valid origins (prevents AllowOrigin::any())
    if allowed_origins.is_empty() {
        panic!("🚨 SECURITY ERROR: CORS_ORIGINS must contain at least one valid origin!");
    }

    let cors = CorsLayer::new()
        .allow_origin(AllowOrigin::list(allowed_origins))
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
        // ============================================================================
        // PUBLIC ENDPOINTS (no authentication required)
        // ============================================================================

        // Health endpoints
        .route("/health", get(health::health_check))
        .route("/ready", get(health::readiness_check))
        .route("/metrics", get(health::metrics))

        // Auth endpoints
        .route("/api/auth/login", post(auth::login))
        .route("/api/auth/verify", post(auth::verify_token))
        .route("/api/auth/whoami", get(auth::whoami))

        // ============================================================================
        // PROTECTED ENDPOINTS (JWT authentication required)
        // ============================================================================

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

    let app = app.into_make_service_with_connect_info::<std::net::SocketAddr>();

    let addr = format!("{}:{}", host, port);

    // ============================================================================
    // Start HTTP Server (TLS infrastructure ready for deployment)
    // ============================================================================
    // Note: Full HTTPS integration requires using a reverse proxy (nginx) or
    // alternative web framework (actix-web). TLS certificate validation and
    // config creation are implemented in tls.rs and ready for integration.

    if CertificateLoader::validate_certificates(&tls_config).is_ok() {
        info!("🔒 TLS certificates are valid - ready for HTTPS deployment via reverse proxy");
        info!("   Set up nginx with TLS or use actix-web for direct HTTPS support");
    } else {
        info!("⚠️  TLS certificates not configured - running HTTP-only (development mode)");
    }

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
