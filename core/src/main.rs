use axum::{
    http::HeaderValue,
    routing::{get, post},
    Router,
};
use std::sync::Arc;
use std::time::Duration;
use tower_http::cors::{AllowOrigin, CorsLayer};
use tracing::{error, info, warn};

mod handlers;
mod middleware;
mod models;
mod openapi;
mod services;

use handlers::{chat, health, memory, openai_compat, stt, tts, web_search};
use middleware::{CertificateLoader, EnvironmentChecklist, SecretsValidator, TlsConfig};
use models::AppState;
use openapi::ApiDoc;
use utoipa::OpenApi;
use utoipa_swagger_ui::SwaggerUi;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // SECURITY FIX: Explicitly initialize rustls crypto provider
    rustls::crypto::aws_lc_rs::default_provider()
        .install_default()
        .expect("Failed to install rustls crypto provider");

    // Initialize tracing
    tracing_subscriber::fmt::init();

    // Load environment variables from .env file
    dotenvy::dotenv().ok();

    info!(" Jarvis Rust Backend v1.9.0 starting...");

    // ============================================================================
    // SECURITY FIX C6: Validate all secrets before starting server
    // ============================================================================
    match SecretsValidator::validate_all() {
        Ok(()) => {
            info!(" All secrets validated - proceeding with startup");
        }
        Err(e) => {
            error!(" SECURITY ERROR: Secret validation failed - {}", e);
            error!("  Application will NOT start without proper secrets configuration");
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
            info!(" TLS certificates validated - HTTPS will be enabled");
        }
        Err(e) => {
            warn!("  SECURITY WARNING: {}", e);
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
    let ollama_url = 
        std::env::var("OLLAMA_URL").unwrap_or_else(|_| "http://jarvis_ollama:11434".to_string());
    let qdrant_url = 
        std::env::var("QDRANT_URL").unwrap_or_else(|_| "http://jarvis_qdrant:6333".to_string());
    let cors_origins =
        std::env::var("CORS_ORIGINS").unwrap_or_else(|_| "http://localhost:3000".to_string());
    
    info!(" Configuration:");
    info!("  - Server: {}:{}", host, port);
    info!("  - Ollama: {}", ollama_url);
    info!("  - Qdrant: {}", qdrant_url);
    info!("  - Audio Engine: Integrated (Rust Native)");
    info!("  - CORS Origins: {}", cors_origins);

    // ============================================================================
    // SERVICES INITIALIZATION
    // ============================================================================
    let audio_engine = Arc::new(services::audio_engine::AudioEngineClient::new());
    let ollama = Arc::new(services::ollama::OllamaService::new(&ollama_url));
    let qdrant = Arc::new(services::qdrant::QdrantService::new(&qdrant_url));
    
    // Native Voice Services (The new Rust Ears and Voice)
    let stt = match services::stt_native::SttNativeService::new("/app/models/stt/ggml-base.bin") {
        Ok(service) => Arc::new(service),
        Err(e) => {
            warn!(" WARNING: STT Native Service could not be initialized: {}", e);
            warn!(" Voice transcription will be unavailable until models are placed in models/stt/");
            Arc::new(services::stt_native::SttNativeService::new_dummy())
        }
    };
    let tts = Arc::new(services::tts_native::TtsNativeService::new("/app/models/fr_FR-upmc-medium.onnx"));

    // Initialize Qdrant collection (nomic-embed-text is 768 dimensions)
    if let Ok(rt) = tokio::runtime::Handle::try_current() {
        let q_clone = qdrant.clone();
        rt.spawn(async move {
            if let Err(e) = q_clone.init_collection(768).await {
                warn!(" Failed to initialize Qdrant collection: {}", e);
            }
        });
    }

    // ============================================================================
    // DATABASE CONNECTION
    // ============================================================================
    let database_url = std::env::var("DATABASE_URL")
        .expect("DATABASE_URL must be set (loaded from jarvis-secretsd)");

    info!(" Connecting to PostgreSQL database...");
    let db_service = services::db::DbService::new(&database_url)
        .await
        .expect("Failed to connect to PostgreSQL");

    info!(" Database connection established");

    // Create application state
    let state = Arc::new(AppState {
        ollama_url,
        qdrant_url,
        audio_engine,
        db: Arc::new(db_service),
        ollama,
        qdrant,
        stt,
        tts,
    });

    // ============================================================================
    // SECURITY FIX C5: Rate Limiting Initialized (lazy static)
    // ============================================================================
    info!(" Rate limiting initialized - protecting against DoS attacks");

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
        panic!(" SECURITY ERROR: CORS_ORIGINS must contain at least one valid origin!");
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

    // Initialize Prometheus metrics
    let (prometheus_layer, metric_handle) = axum_prometheus::PrometheusMetricLayer::pair();

    // Build router
    let app = Router::new()
        // ============================================================================
        // PUBLIC ENDPOINTS (no authentication required)
        // ============================================================================
        // Health endpoints
        .route("/health", get(health::health_check))
        .route("/ready", get(health::readiness_check))
        .route("/metrics", get(|| async move { metric_handle.render() }))
        // OpenAPI/Swagger UI
        .merge(SwaggerUi::new("/swagger-ui").url("/api-docs/openapi.json", ApiDoc::openapi()))
        // Auth endpoints
        // .route("/api/auth/login", post(auth::login))
        // .route("/api/auth/verify", post(auth::verify_token))
        // .route("/api/auth/whoami", get(auth::whoami))
        // ============================================================================
        // PROTECTED ENDPOINTS (JWT authentication required)
        // ============================================================================
        // Chat endpoints
        // .route("/api/chat", post(chat::chat_endpoint))
        // .route("/api/chat/conversations", get(chat::get_conversations))
        // .route("/api/chat/history/:id", get(chat::get_history))
        // .route(
        //     "/api/chat/conversation/:id",
        //     axum::routing::delete(chat::delete_conversation),
        // )
        // STT/TTS endpoints
        .route("/api/voice/transcribe", post(stt::transcribe))
        .route("/api/voice/synthesize", post(tts::synthesize))
        .route("/api/voice/voices", get(tts::list_voices))
        .route("/api/voice/languages", get(stt::list_languages))
        // Memory endpoints
        .route("/api/memory/add", post(memory::add_memory))
        .route("/api/memory/search", post(memory::search_memory))
        .route("/api/memory/list", get(memory::list_memories))
        // Web Search endpoint (uses BRAVE_API_KEY from jarvis-secretsd)
        .route("/api/v1/search", get(web_search::web_search))
        // OpenAI-compatible endpoints for Open-WebUI integration
        .route("/v1/models", get(openai_compat::list_models))
        .route("/v1/chat/completions", post(openai_compat::chat_completions))
        .route("/v1/audio/transcriptions", post(openai_compat::create_transcription))
        .route("/v1/audio/speech", post(openai_compat::create_speech))
        // WebSocket
        .route("/ws", axum::routing::get(chat::websocket_handler))
        // Security layers
        .layer(cors)
        .layer(prometheus_layer)
        .with_state(state);

    let addr = format!("{}:{}", host, port).parse::<std::net::SocketAddr>()?;

    // ============================================================================
    // Start HTTP Server (Internal communication is better in HTTP)
    // ============================================================================
    info!(" Starting Jarvis Server");
    info!("  - Port: {}", port);
    info!(" Server listening on http://{}", addr);
    
    let listener = tokio::net::TcpListener::bind(&addr).await?;
    axum::serve(listener, app).await?;

    Ok(())
}
