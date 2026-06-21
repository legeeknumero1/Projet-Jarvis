// ============================================================================
// Middleware pour authentification, traçage, CORS, rate limiting, etc.
// ============================================================================

pub mod auth;
pub mod secrets;

pub mod tls;
pub mod validation;
pub mod error;

pub use auth::{generate_token, verify_token, ValidatedJwt};
pub use secrets::{SecretsValidator, EnvironmentChecklist};

pub use tls::{TlsConfig, CertificateLoader, CertificateGenerator};
pub use validation::{
    InputValidator,
    MemoryContentValidator, SearchQueryValidator
};
pub use error::{AppError, ErrorContext, AuditLog, Recovery, RetryStrategy};

pub struct RequestContext {
    pub request_id: String,
    pub user_id: Option<String>,
    pub username: Option<String>,
    pub timestamp: chrono::DateTime<chrono::Utc>,
}

impl RequestContext {
    pub fn new() -> Self {
        Self {
            request_id: uuid::Uuid::new_v4().to_string(),
            user_id: None,
            username: None,
            timestamp: chrono::Utc::now(),
        }
    }

    pub fn with_user(user_id: String, username: String) -> Self {
        Self {
            request_id: uuid::Uuid::new_v4().to_string(),
            user_id: Some(user_id),
            username: Some(username),
            timestamp: chrono::Utc::now(),
        }
    }
}
