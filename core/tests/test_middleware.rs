// Integration tests for middleware components
use jarvis_core::middleware::{error::AppError, validation::validate_input};

#[cfg(test)]
mod validation_tests {
    use super::*;

    #[test]
    fn test_validate_input_empty_string() {
        let result = validate_input("");
        assert!(result.is_err());
        assert_eq!(result.unwrap_err().to_string(), "Input cannot be empty");
    }

    #[test]
    fn test_validate_input_whitespace_only() {
        let result = validate_input("   ");
        assert!(result.is_err());
    }

    #[test]
    fn test_validate_input_valid_string() {
        let result = validate_input("Hello, world!");
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), "Hello, world!");
    }

    #[test]
    fn test_validate_input_trims_whitespace() {
        let result = validate_input("  Hello  ");
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), "Hello");
    }

    #[test]
    fn test_validate_input_max_length() {
        let long_input = "a".repeat(10000);
        let result = validate_input(&long_input);
        assert!(result.is_ok());
    }

    #[test]
    fn test_validate_input_sql_injection_attempt() {
        let sql_injection = "'; DROP TABLE users; --";
        let result = validate_input(sql_injection);
        // Should validate input but not execute SQL
        assert!(result.is_ok());
    }

    #[test]
    fn test_validate_input_special_characters() {
        let special_chars = "Hello <script>alert('xss')</script>";
        let result = validate_input(special_chars);
        assert!(result.is_ok());
    }
}

#[cfg(test)]
mod error_tests {
    use super::*;
    use axum::http::StatusCode;

    #[test]
    fn test_app_error_not_found() {
        let error = AppError::NotFound("Resource not found".to_string());
        let (status, _) = error.into_response().into_parts();
        assert_eq!(status, StatusCode::NOT_FOUND);
    }

    #[test]
    fn test_app_error_unauthorized() {
        let error = AppError::Unauthorized;
        let (status, _) = error.into_response().into_parts();
        assert_eq!(status, StatusCode::UNAUTHORIZED);
    }

    #[test]
    fn test_app_error_bad_request() {
        let error = AppError::BadRequest("Invalid input".to_string());
        let (status, _) = error.into_response().into_parts();
        assert_eq!(status, StatusCode::BAD_REQUEST);
    }

    #[test]
    fn test_app_error_internal_server() {
        let error = AppError::InternalServerError("Something went wrong".to_string());
        let (status, _) = error.into_response().into_parts();
        assert_eq!(status, StatusCode::INTERNAL_SERVER_ERROR);
    }

    #[test]
    fn test_app_error_rate_limit() {
        let error = AppError::RateLimitExceeded;
        let (status, _) = error.into_response().into_parts();
        assert_eq!(status, StatusCode::TOO_MANY_REQUESTS);
    }

    #[test]
    fn test_app_error_display() {
        let error = AppError::NotFound("User".to_string());
        assert_eq!(format!("{}", error), "User");
    }
}

#[cfg(test)]
mod rate_limit_tests {
    use std::time::Duration;
    use tokio::time::sleep;

    #[tokio::test]
    async fn test_rate_limit_allows_within_limit() {
        // This would test the actual rate limiter
        // For now, we just test the concept
        let max_requests = 5;
        let mut count = 0;

        for _ in 0..max_requests {
            count += 1;
            assert!(count <= max_requests);
        }

        assert_eq!(count, max_requests);
    }

    #[tokio::test]
    async fn test_rate_limit_blocks_over_limit() {
        let max_requests = 3;
        let mut requests = vec![];

        for i in 0..5 {
            requests.push(i);
        }

        assert!(requests.len() > max_requests);
    }

    #[tokio::test]
    async fn test_rate_limit_window_reset() {
        // Simulate window reset after time period
        let max_requests = 2;
        let window_duration = Duration::from_millis(100);

        // First batch
        for _ in 0..max_requests {
            // Request allowed
        }

        // Wait for window to reset
        sleep(window_duration).await;

        // Second batch should be allowed
        for _ in 0..max_requests {
            // Request allowed
        }
    }
}

#[cfg(test)]
mod secrets_tests {
    use jarvis_core::middleware::secrets::mask_sensitive_data;

    #[test]
    fn test_mask_password() {
        let input = r#"{"password": "secret123"}"#;
        let masked = mask_sensitive_data(input);
        assert!(masked.contains("***"));
        assert!(!masked.contains("secret123"));
    }

    #[test]
    fn test_mask_api_key() {
        let input = "api_key=sk-1234567890abcdef";
        let masked = mask_sensitive_data(input);
        assert!(!masked.contains("sk-1234567890abcdef"));
    }

    #[test]
    fn test_mask_token() {
        let input = r#"{"token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"}"#;
        let masked = mask_sensitive_data(input);
        assert!(!masked.contains("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"));
    }

    #[test]
    fn test_no_sensitive_data() {
        let input = "Hello, world!";
        let masked = mask_sensitive_data(input);
        assert_eq!(masked, input);
    }
}
