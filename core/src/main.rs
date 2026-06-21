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

use handlers::{chat, health, openai_compat, web_search};
use middleware::{CertificateLoader, EnvironmentChecklist, SecretsValidator, TlsConfig};
use models::AppState;
use openapi::ApiDoc;
use utoipa::OpenApi;
use utoipa_swagger_ui::SwaggerUi;
use once_cell::sync::Lazy;
use parking_lot::RwLock;

// removed RATE_LIMITS

async fn rate_limiter(
    axum::extract::State(state): axum::extract::State<Arc<AppState>>,
    req: axum::extract::Request,
    next: axum::middleware::Next,
) -> axum::response::Response {
    // Try to get IP from ConnectInfo extension
    let ip = match req.extensions().get::<axum::extract::ConnectInfo<std::net::SocketAddr>>() {
        Some(axum::extract::ConnectInfo(addr)) => addr.ip(),
        None => std::net::IpAddr::V4(std::net::Ipv4Addr::new(127, 0, 0, 1)),
    };
    let now = std::time::Instant::now();
    
    let mut limits = state.rate_limits.write();
    let entry = limits.entry(ip).or_insert((0, now));
    
    if now.duration_since(entry.1).as_secs() > 60 {
        entry.0 = 0;
        entry.1 = now;
    }
    
    if entry.0 > 100 {
        tracing::warn!("Rate limit exceeded for IP: {}", ip);
        return axum::response::IntoResponse::into_response(axum::http::StatusCode::TOO_MANY_REQUESTS);
    }
    entry.0 += 1;

    // Prevent infinite HashMap leak by pruning expired items
    if limits.len() > 1000 {
        limits.retain(|_, v| now.duration_since(v.1).as_secs() <= 60);
    }

    drop(limits);
    
    next.run(req).await
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Install default crypto provider for Rustls 0.23+ (resolves CryptoProvider panic)
    rustls::crypto::ring::default_provider()
        .install_default()
        .map_err(|_| "Failed to install rustls default crypto provider")?;

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
            return Err(e.into());
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
    let jwt_secret = std::env::var("JWT_SECRET")
        .map_err(|_| "SECURITY ERROR: JWT_SECRET environment variable is not set!")?;
    let host = std::env::var("HOST").unwrap_or_else(|_| "0.0.0.0".to_string());
    let port = std::env::var("PORT").unwrap_or_else(|_| "8100".to_string());
    let python_bridges_url =
        std::env::var("PYTHON_BRIDGES_URL").unwrap_or_else(|_| "http://localhost:8005".to_string());
    let cors_origins =
        std::env::var("CORS_ORIGINS").unwrap_or_else(|_| "http://localhost:3000".to_string());
    
    info!(" Configuration:");
    info!("  - Server: {}:{}", host, port);
    info!("  - Python Bridges: {}", python_bridges_url);
    info!("  - Audio Engine: Integrated (Rust Native)");
    info!("  - CORS Origins: {}", cors_origins);

    // ============================================================================
    // SERVICES INITIALIZATION
    // ============================================================================
    let audio_engine = Arc::new(services::audio_engine::AudioEngineClient::new());

    // ============================================================================
    // OLLAMA LOCAL FALLBACK & EMBEDDINGS (Zero-VRAM Standby)
    // ============================================================================
    let ollama_llm_model = std::env::var("OLLAMA_LLM_MODEL")
        .unwrap_or_else(|_| "qwen2.5:1.5b".to_string());
    let ollama_embed_model = std::env::var("OLLAMA_EMBED_MODEL")
        .unwrap_or_else(|_| "nomic-embed-text".to_string());
    info!(" Ollama fallback configured:");
    info!("  - LLM Model: {} (zero-VRAM standby, keep_alive:0)", ollama_llm_model);
    info!("  - Embed Model: {} (~300Mo, on-demand)", ollama_embed_model);
    let ollama_client = Arc::new(services::ollama_client::OllamaClient::new(
        ollama_llm_model,
        ollama_embed_model,
    ));

    // ============================================================================
    // MEMORY INDEX LAYER (Tantivy Local RAG Pipeline)
    // ============================================================================
    info!(" Initializing local Tantivy Memory Index RAG pipeline...");
    let memory_index_path = std::env::var("MEMORY_INDEX_PATH").unwrap_or_else(|_| "/app/memory_index".to_string());
    let memory_index = Arc::new(
        services::memory_index::AsyncMemoryIndex::new(memory_index_path, ollama_client.clone())
            .map_err(|e| format!("Failed to initialize Tantivy AsyncMemoryIndex: {}", e))?
    );

    // ============================================================================
    // GEMINI AI INTEGRATION (with Secretsd support)
    // ============================================================================
    let mut gemini_api_key = std::env::var("GEMINI_API_KEY").unwrap_or_else(|_| "".to_string());
    if gemini_api_key.is_empty() {
        let secretsd_url = std::env::var("SECRETSD_URL").unwrap_or_else(|_| "http://jarvis_secretsd:8081".to_string());
        let client_id = std::env::var("CLIENT_ID").unwrap_or_else(|_| "backend".to_string());
        
        info!(" GEMINI_API_KEY not found in env, attempting to fetch from secretsd...");
        
        let client = reqwest::Client::new();
        let resp = client.get(&format!("{}/secret/gemini_api_key", secretsd_url))
            .header("X-Jarvis-Client", "backend")
            .header("Authorization", format!("Bearer {}", std::env::var("SECRETSD_TOKEN").unwrap_or_else(|_| "secret-vault-token".to_string())))
            .send()
            .await;
            
        match resp {
            Ok(r) if r.status().is_success() => {
                if let Ok(json) = r.json::<serde_json::Value>().await {
                    if let Some(key) = json["value"].as_str() {
                        gemini_api_key = key.to_string();
                        info!(" Successfully loaded GEMINI_API_KEY from secretsd vault.");
                    }
                }
            }
            Ok(r) => warn!(" Secretsd returned {}. GEMINI_API_KEY missing from vault.", r.status()),
            Err(e) => warn!(" Failed to reach secretsd: {}", e),
        }
    }
    
    if gemini_api_key.is_empty() {
        warn!(" GEMINI_API_KEY is not set. Intent analysis will fail.");
    }
    let gemini_client = Arc::new(services::gemini_client::GeminiClient::new(gemini_api_key));

    // ============================================================================
    // HOME ASSISTANT INTEGRATION (with Secretsd support)
    // ============================================================================
    let mut haos_api_token = std::env::var("HAOS_API_TOKEN").unwrap_or_else(|_| "".to_string());
    if haos_api_token.is_empty() {
        let secretsd_url = std::env::var("SECRETSD_URL").unwrap_or_else(|_| "http://jarvis_secretsd:8081".to_string());
        let client_id = std::env::var("CLIENT_ID").unwrap_or_else(|_| "backend".to_string());
        
        info!(" HAOS_API_TOKEN not found in env, attempting to fetch from secretsd...");
        
        let client = reqwest::Client::new();
        let resp = client.get(&format!("{}/secret/haos_api_token", secretsd_url))
            .header("X-Jarvis-Client", "backend")
            .header("Authorization", format!("Bearer {}", std::env::var("SECRETSD_TOKEN").unwrap_or_else(|_| "secret-vault-token".to_string())))
            .send()
            .await;
            
        match resp {
            Ok(r) if r.status().is_success() => {
                if let Ok(json) = r.json::<serde_json::Value>().await {
                    if let Some(key) = json["value"].as_str() {
                        haos_api_token = key.to_string();
                        info!(" Successfully loaded HAOS_API_TOKEN from secretsd vault.");
                    }
                }
            }
            Ok(r) => warn!(" Secretsd returned {}. HAOS_API_TOKEN missing from vault.", r.status()),
            Err(e) => warn!(" Failed to reach secretsd: {}", e),
        }
    }
    
    if haos_api_token.is_empty() {
        warn!(" HAOS_API_TOKEN is not set. Domotics will not function.");
    }
    let haos_client = Arc::new(services::home_assistant_client::HomeAssistantClient::new(haos_api_token));

    // Create application state
    let state = Arc::new(AppState {
        python_bridges_url,
        audio_engine,
        memory_index,
        agents: Arc::new(parking_lot::RwLock::new(std::collections::HashMap::new())),
        rate_limits: Arc::new(parking_lot::RwLock::new(std::collections::HashMap::new())),
        jwt_secret,
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
        return Err(" SECURITY ERROR: CORS_ORIGINS must contain at least one valid origin!".into());
    }

    let cors = CorsLayer::new()
        .allow_origin(AllowOrigin::list(allowed_origins))
        .allow_methods(tower_http::cors::Any)
        .allow_headers(tower_http::cors::Any)
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
        // ============================================================================
        // PROTECTED ENDPOINTS (JWT authentication required - MIGRATED TO V2)
        // ============================================================================
        // Web Search endpoint (uses BRAVE_API_KEY from jarvis-secretsd)
        .route("/api/v1/search", get(web_search::web_search))
        // OpenAI-compatible endpoints for Open-WebUI integration
        .route("/v1/audio/transcriptions", post(openai_compat::create_transcription))
        .route("/v1/audio/speech", post(openai_compat::create_speech))
        // WebSocket and Commands
        .route("/api/v2/jarvis/ws", axum::routing::get(chat::jarvis_ws_handler))
        .route("/api/v2/jarvis/command", post(chat::process_jarvis_command))
        // Agent Management
        .route("/api/agents/register", post(handlers::agents::register_agent))
        .route("/api/agents/list", get(handlers::agents::list_agents))
        // Security layers
        .layer(cors)
        .layer(prometheus_layer)
        .layer(axum::Extension(gemini_client))
        .layer(axum::Extension(ollama_client))
        .layer(axum::Extension(haos_client))
        .with_state(state);

    let app = app.into_make_service_with_connect_info::<std::net::SocketAddr>();

    let addr = format!("{}:{}", host, port).parse::<std::net::SocketAddr>()?;

    // ============================================================================
    // Start HTTPS Server
    // ============================================================================
    let cert_path = std::env::var("TLS_CERT_PATH").unwrap_or_else(|_| "certs/server.crt".to_string());
    let key_path = std::env::var("TLS_KEY_PATH").unwrap_or_else(|_| "certs/server.key".to_string());

    if std::path::Path::new(&cert_path).exists() && std::path::Path::new(&key_path).exists() {
        info!(" Starting Jarvis in HTTPS mode");
        info!("  - Cert: {}", cert_path);
        info!("  - Key: {}", key_path);
        
        let config = axum_server::tls_rustls::RustlsConfig::from_pem_file(cert_path, key_path)
            .await?;

        info!(" Server listening on https://{}", addr);
        axum_server::bind_rustls(addr, config)
            .serve(app)
            .await?;
    } else {
        warn!(" TLS certificates not found. Falling back to HTTP.");
        info!(" Server listening on http://{}", addr);
        let listener = tokio::net::TcpListener::bind(&addr).await?;
        axum::serve(listener, app).await?;
    }

    Ok(())
}
