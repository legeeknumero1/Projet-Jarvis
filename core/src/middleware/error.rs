// ============================================================================
// Comprehensive Error Handling & Structured Logging
// ============================================================================
//
// Ce module gère les erreurs de manière structurée et sécurisée avec:
// - Messages d'erreur contextuel sans fuites d'info
// - Logging structuré pour audit/debugging
// - HTTP status codes appropriés
// - Recovery strategies

use axum::{
    http::StatusCode,
    response::{IntoResponse, Response},
    Json,
};
use serde_json::json;
use std::fmt;

// ============================================================================
// Error Types
// ============================================================================

#[derive(Debug)]
pub enum AppError {
    // Authentication errors (401/403)
    Unauthorized(String),
    Forbidden(String),
    InvalidToken(String),

    // Validation errors (400)
    ValidationFailed(String),
    InvalidInput(String),

    // Business logic errors (400/409)
    NotFound(String),
    Conflict(String),
    RateLimitExceeded(String),

    // Server errors (500)
    InternalError(String),
    DatabaseError(String),
    ServiceUnavailable(String),

    // Integration errors (502/503)
    ExternalServiceError(String),
}

impl fmt::Display for AppError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            AppError::Unauthorized(msg) => write!(f, "Unauthorized: {}", msg),
            AppError::Forbidden(msg) => write!(f, "Forbidden: {}", msg),
            AppError::InvalidToken(msg) => write!(f, "Invalid token: {}", msg),
            AppError::ValidationFailed(msg) => write!(f, "Validation failed: {}", msg),
            AppError::InvalidInput(msg) => write!(f, "Invalid input: {}", msg),
            AppError::NotFound(msg) => write!(f, "Not found: {}", msg),
            AppError::Conflict(msg) => write!(f, "Conflict: {}", msg),
            AppError::RateLimitExceeded(msg) => write!(f, "Rate limit exceeded: {}", msg),
            AppError::InternalError(msg) => write!(f, "Internal error: {}", msg),
            AppError::DatabaseError(msg) => write!(f, "Database error: {}", msg),
            AppError::ServiceUnavailable(msg) => write!(f, "Service unavailable: {}", msg),
            AppError::ExternalServiceError(msg) => write!(f, "External service error: {}", msg),
        }
    }
}

impl AppError {
    // Get HTTP status code
    pub fn status_code(&self) -> StatusCode {
        match self {
            AppError::Unauthorized(_) => StatusCode::UNAUTHORIZED,
            AppError::Forbidden(_) => StatusCode::FORBIDDEN,
            AppError::InvalidToken(_) => StatusCode::UNAUTHORIZED,
            AppError::ValidationFailed(_) => StatusCode::BAD_REQUEST,
            AppError::InvalidInput(_) => StatusCode::BAD_REQUEST,
            AppError::NotFound(_) => StatusCode::NOT_FOUND,
            AppError::Conflict(_) => StatusCode::CONFLICT,
            AppError::RateLimitExceeded(_) => StatusCode::TOO_MANY_REQUESTS,
            AppError::InternalError(_) => StatusCode::INTERNAL_SERVER_ERROR,
            AppError::DatabaseError(_) => StatusCode::INTERNAL_SERVER_ERROR,
            AppError::ServiceUnavailable(_) => StatusCode::SERVICE_UNAVAILABLE,
            AppError::ExternalServiceError(_) => StatusCode::BAD_GATEWAY,
        }
    }

    // Get user-facing message (safe, no internal details)
    pub fn user_message(&self) -> String {
        match self {
            AppError::Unauthorized(_) => "Authentication required".to_string(),
            AppError::Forbidden(_) => "Access denied".to_string(),
            AppError::InvalidToken(_) => "Invalid or expired token".to_string(),
            AppError::ValidationFailed(msg) => format!("Invalid input: {}", msg),
            AppError::InvalidInput(msg) => format!("Invalid input: {}", msg),
            AppError::NotFound(_) => "Resource not found".to_string(),
            AppError::Conflict(_) => "Resource conflict".to_string(),
            AppError::RateLimitExceeded(_) => "Too many requests. Please try again later.".to_string(),
            AppError::InternalError(_) => "Internal server error. Please try again later.".to_string(),
            AppError::DatabaseError(_) => "Database error. Please try again later.".to_string(),
            AppError::ServiceUnavailable(_) => "Service temporarily unavailable. Please try again later.".to_string(),
            AppError::ExternalServiceError(_) => "External service error. Please try again later.".to_string(),
        }
    }

    // Get internal log message (detailed for debugging)
    pub fn internal_message(&self) -> &str {
        match self {
            AppError::Unauthorized(msg) => msg,
            AppError::Forbidden(msg) => msg,
            AppError::InvalidToken(msg) => msg,
            AppError::ValidationFailed(msg) => msg,
            AppError::InvalidInput(msg) => msg,
            AppError::NotFound(msg) => msg,
            AppError::Conflict(msg) => msg,
            AppError::RateLimitExceeded(msg) => msg,
            AppError::InternalError(msg) => msg,
            AppError::DatabaseError(msg) => msg,
            AppError::ServiceUnavailable(msg) => msg,
            AppError::ExternalServiceError(msg) => msg,
        }
    }

    // Log the error appropriately
    pub fn log(&self, user_id: Option<&str>, context: &str) {
        let log_msg = format!(
            "[{}] {} | User: {} | Internal: {}",
            context,
            self,
            user_id.unwrap_or("anonymous"),
            self.internal_message()
        );

        match self {
            AppError::Unauthorized(_) | AppError::Forbidden(_) | AppError::InvalidToken(_) => {
                tracing::warn!("🔐 SECURITY: {}", log_msg);
            }
            AppError::ValidationFailed(_) | AppError::InvalidInput(_) => {
                tracing::warn!("⚠️  VALIDATION: {}", log_msg);
            }
            AppError::RateLimitExceeded(_) => {
                tracing::warn!("🚨 RATE LIMIT: {}", log_msg);
            }
            AppError::NotFound(_) | AppError::Conflict(_) => {
                tracing::info!("ℹ️  BUSINESS: {}", log_msg);
            }
            AppError::InternalError(_) | AppError::DatabaseError(_) => {
                tracing::error!("❌ ERROR: {}", log_msg);
            }
            AppError::ServiceUnavailable(_) | AppError::ExternalServiceError(_) => {
                tracing::error!("⚠️  SERVICE: {}", log_msg);
            }
        }
    }
}

// ============================================================================
// Axum Response Implementation
// ============================================================================

impl IntoResponse for AppError {
    fn into_response(self) -> Response {
        let status = self.status_code();
        let message = self.user_message();

        // Log the error (without exposing internal details to client)
        tracing::warn!(
            "HTTP {} - {} - Internal: {}",
            status.as_u16(),
            message,
            self.internal_message()
        );

        let body = Json(json!({
            "error": {
                "status": status.as_u16(),
                "message": message,
                "timestamp": chrono::Utc::now().to_rfc3339(),
            }
        }));

        (status, body).into_response()
    }
}

// ============================================================================
// Safe Error Converters
// ============================================================================

impl From<std::string::String> for AppError {
    fn from(err: std::string::String) -> Self {
        AppError::InternalError(err)
    }
}

impl From<&str> for AppError {
    fn from(err: &str) -> Self {
        AppError::InternalError(err.to_string())
    }
}

// ============================================================================
// Contextual Error Logging
// ============================================================================

pub struct ErrorContext {
    pub user_id: Option<String>,
    pub endpoint: String,
    pub request_id: String,
}

impl ErrorContext {
    pub fn new(endpoint: String, request_id: String) -> Self {
        Self {
            user_id: None,
            endpoint,
            request_id,
        }
    }

    pub fn with_user(mut self, user_id: String) -> Self {
        self.user_id = Some(user_id);
        self
    }

    pub fn log_error(&self, error: &AppError) {
        let context = format!(
            "[{}] {} (Request: {})",
            self.endpoint, self.user_id.as_deref().unwrap_or("anon"), self.request_id
        );
        error.log(self.user_id.as_deref(), &context);
    }
}

// ============================================================================
// Recovery Strategies
// ============================================================================

/// Retry strategy for transient failures
pub struct RetryStrategy {
    pub max_attempts: u32,
    pub delay_ms: u64,
    pub backoff_multiplier: f64,
}

impl RetryStrategy {
    pub fn new() -> Self {
        Self {
            max_attempts: 3,
            delay_ms: 100,
            backoff_multiplier: 2.0,
        }
    }

    pub fn with_max_attempts(mut self, attempts: u32) -> Self {
        self.max_attempts = attempts;
        self
    }

    pub fn exponential_backoff_delay(&self, attempt: u32) -> u64 {
        (self.delay_ms as f64 * self.backoff_multiplier.powi(attempt as i32)) as u64
    }
}

// ============================================================================
// Structured Logging Helpers
// ============================================================================

pub struct AuditLog;

impl AuditLog {
    /// Log security-relevant events
    pub fn security(event: &str, user_id: &str, details: &str) {
        tracing::warn!(
            event = event,
            user_id = user_id,
            details = details,
            "🔐 SECURITY EVENT"
        );
    }

    /// Log authentication attempts
    pub fn auth_attempt(username: &str, success: bool, ip: &str) {
        tracing::info!(
            username = username,
            success = success,
            ip = ip,
            "🔑 AUTH ATTEMPT"
        );
    }

    /// Log access to sensitive data
    pub fn data_access(user_id: &str, resource: &str, action: &str) {
        tracing::info!(
            user_id = user_id,
            resource = resource,
            action = action,
            "📊 DATA ACCESS"
        );
    }

    /// Log rate limit violations
    pub fn rate_limit_violation(ip: &str, endpoint: &str, limit: u32) {
        tracing::warn!(
            ip = ip,
            endpoint = endpoint,
            limit = limit,
            "🚨 RATE LIMIT VIOLATION"
        );
    }

    /// Log validation failures
    pub fn validation_failure(endpoint: &str, field: &str, reason: &str) {
        tracing::warn!(
            endpoint = endpoint,
            field = field,
            reason = reason,
            "⚠️  VALIDATION FAILURE"
        );
    }
}

// ============================================================================
// Error Recovery Helpers
// ============================================================================

pub struct Recovery;

impl Recovery {
    /// Suggest retry for transient errors
    pub fn should_retry(error: &AppError) -> bool {
        matches!(
            error,
            AppError::ServiceUnavailable(_)
                | AppError::ExternalServiceError(_)
                | AppError::DatabaseError(_)
        )
    }

    /// Get user-friendly recovery message
    pub fn recovery_message(error: &AppError) -> Option<String> {
        match error {
            AppError::RateLimitExceeded(_) => {
                Some("Please wait a moment before trying again.".to_string())
            }
            AppError::ServiceUnavailable(_) => {
                Some("Our service is temporarily down. Please try again in a few minutes.".to_string())
            }
            AppError::ExternalServiceError(_) => {
                Some("An external service is unavailable. Please try again later.".to_string())
            }
            _ => None,
        }
    }
}

// ============================================================================
// Tests
// ============================================================================

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_app_error_status_codes() {
        assert_eq!(
            AppError::Unauthorized("test".to_string()).status_code(),
            StatusCode::UNAUTHORIZED
        );
        assert_eq!(
            AppError::ValidationFailed("test".to_string()).status_code(),
            StatusCode::BAD_REQUEST
        );
        assert_eq!(
            AppError::NotFound("test".to_string()).status_code(),
            StatusCode::NOT_FOUND
        );
        assert_eq!(
            AppError::RateLimitExceeded("test".to_string()).status_code(),
            StatusCode::TOO_MANY_REQUESTS
        );
        assert_eq!(
            AppError::InternalError("test".to_string()).status_code(),
            StatusCode::INTERNAL_SERVER_ERROR
        );
    }

    #[test]
    fn test_error_user_messages_safe() {
        let error = AppError::DatabaseError("SELECT * FROM users dropped table".to_string());
        let user_msg = error.user_message();
        // Should not leak SQL details
        assert!(!user_msg.contains("SELECT"));
        assert!(!user_msg.contains("users"));
    }

    #[test]
    fn test_retry_strategy() {
        let strategy = RetryStrategy::new().with_max_attempts(3);
        assert_eq!(strategy.max_attempts, 3);
        assert_eq!(strategy.exponential_backoff_delay(0), 100);
        assert_eq!(strategy.exponential_backoff_delay(1), 200);
        assert_eq!(strategy.exponential_backoff_delay(2), 400);
    }

    #[test]
    fn test_recovery_should_retry() {
        assert!(Recovery::should_retry(&AppError::ServiceUnavailable(
            "test".to_string()
        )));
        assert!(Recovery::should_retry(&AppError::DatabaseError(
            "test".to_string()
        )));
        assert!(!Recovery::should_retry(&AppError::ValidationFailed(
            "test".to_string()
        )));
    }
}
