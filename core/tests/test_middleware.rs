// Integration tests for middleware components
use axum::{http::StatusCode, response::IntoResponse};
use jarvis_core::middleware::{
    error::AppError,
    secrets::mask_secret,
    validation::{ChatMessageValidator, InputValidator, LoginValidator},
};

#[cfg(test)]
mod validation_tests {
    use super::*;

    #[test]
    fn test_chat_message_validation() {
        // Valid
        let validator = ChatMessageValidator::new("Hello, world!".to_string());
        assert!(validator.validate().is_ok());

        // Empty
        let validator = ChatMessageValidator::new("".to_string());
        assert!(validator.validate().is_err());
    }

    #[test]
    fn test_login_validation() {
        // Valid
        let validator = LoginValidator::new("valid_user".to_string(), "password123".to_string());
        assert!(validator.validate().is_ok());

        // Invalid username
        let validator = LoginValidator::new("invalid user".to_string(), "password123".to_string());
        assert!(validator.validate().is_err());
    }

    #[test]
    fn test_sanitization() {
        let msg = "Hello <script>alert('xss')</script>";
        let validator = ChatMessageValidator::new(msg.to_string());
        let sanitized = validator.sanitize();
        assert!(!sanitized.contains("<script>"));
    }
}

#[cfg(test)]
mod error_tests {
    use super::*;

    #[test]
    fn test_app_error_not_found() {
        let error = AppError::NotFound("Resource not found".to_string());
        let response = error.into_response();
        assert_eq!(response.status(), StatusCode::NOT_FOUND);
    }

    #[test]
    fn test_app_error_unauthorized() {
        let error = AppError::Unauthorized("Access denied".to_string());
        let response = error.into_response();
        assert_eq!(response.status(), StatusCode::UNAUTHORIZED);
    }

    #[test]
    fn test_app_error_validation_failed() {
        let error = AppError::ValidationFailed("Invalid input".to_string());
        let response = error.into_response();
        assert_eq!(response.status(), StatusCode::BAD_REQUEST);
    }

    #[test]
    fn test_app_error_internal_error() {
        let error = AppError::InternalError("Something went wrong".to_string());
        let response = error.into_response();
        assert_eq!(response.status(), StatusCode::INTERNAL_SERVER_ERROR);
    }

    #[test]
    fn test_app_error_rate_limit() {
        let error = AppError::RateLimitExceeded("Too many requests".to_string());
        let response = error.into_response();
        assert_eq!(response.status(), StatusCode::TOO_MANY_REQUESTS);
    }
}

#[cfg(test)]
mod secrets_tests {
    use super::*;

    #[test]
    fn test_mask_secret() {
        let secret = "very_secret_key_12345";
        let masked = mask_secret(secret, 5);
        assert_eq!(masked, "very_****************");
        assert!(!masked.contains("12345"));
    }

    #[test]
    fn test_mask_short_secret() {
        let secret = "abc";
        let masked = mask_secret(secret, 5);
        assert_eq!(masked, "***");
    }
}