use utoipa::openapi::security::{HttpAuthScheme, HttpBuilder, SecurityScheme};
use utoipa::OpenApi;

#[derive(OpenApi)]
#[openapi(
    info(
        title = "Jarvis API",
        version = "1.9.0",
        description = "Polyglot AI Assistant - 9-Phase Distributed Architecture",
        contact(
            name = "Jarvis Project",
            url = "https://github.com/legeeknumero1/Projet-Jarvis"
        )
    ),
    servers(
        (url = "http://localhost:8100", description = "Development server"),
        (url = "https://api.jarvis.local", description = "Production server")
    ),
    paths(
        crate::handlers::health::health_check,
        crate::handlers::health::readiness_check,
        crate::handlers::chat::chat_endpoint,
        crate::handlers::chat::get_conversations,
        crate::handlers::chat::get_history,
        crate::handlers::stt::transcribe,
        crate::handlers::tts::synthesize,
        crate::handlers::auth::login,
        crate::handlers::auth::logout,
        crate::handlers::openai_compat::create_transcription,
        crate::handlers::openai_compat::create_speech,
        crate::handlers::web_search::web_search,
    ),
    components(
        schemas(
            crate::models::ChatRequest,
            crate::models::ChatResponse,
            crate::models::HealthStatus,
            crate::models::SynthesizeRequest,
            crate::models::SynthesizeResponse,
            crate::models::TranscribeRequest,
            crate::models::TranscribeResponse,
            crate::models::LoginRequest,
            crate::models::LoginResponse,
            crate::handlers::openai_compat::TranscriptionResponse,
            crate::handlers::openai_compat::SpeechRequest,
            crate::handlers::web_search::SearchResult,
            crate::handlers::web_search::SearchResponse,
        )
    ),
    modifiers(&SecurityAddon),
    tags(
        (name = "health", description = "Health check endpoints"),
        (name = "chat", description = "Chat and conversation endpoints"),
        (name = "voice", description = "TTS and STT voice endpoints"),
        (name = "auth", description = "Authentication endpoints"),
        (name = "OpenAI Compatible", description = "OpenAI-compatible endpoints for Open-WebUI integration"),
        (name = "Web Search", description = "Internet search via Brave Search API (secured by jarvis-secretsd)"),
    )
)]
pub struct ApiDoc;

struct SecurityAddon;

impl utoipa::Modify for SecurityAddon {
    fn modify(&self, openapi: &mut utoipa::openapi::OpenApi) {
        if let Some(components) = openapi.components.as_mut() {
            components.add_security_scheme(
                "bearer_auth",
                SecurityScheme::Http(
                    HttpBuilder::new()
                        .scheme(HttpAuthScheme::Bearer)
                        .bearer_format("JWT")
                        .build(),
                ),
            )
        }
    }
}
