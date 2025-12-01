// ============================================================================
// Authentication Handler - Login and Token Management
// ============================================================================
//
// Endpoints:
// - POST /auth/login - Generate JWT token (public endpoint)
// - POST /auth/refresh - Refresh JWT token (public endpoint)
// - GET /auth/verify - Verify token validity (protected endpoint)

use axum::{extract::ConnectInfo, http::StatusCode, Json};
use std::net::SocketAddr;
use tracing::info;

use crate::middleware::{
    check_auth_rate_limit, generate_token, InputValidator, LoginValidator, ValidatedJwt,
};
use crate::models::{LoginRequest, LoginResponse};

/// Login endpoint - Generate JWT token for user
///
/// SECURITY: This is intentionally permissive for testing/development
/// In production, this should validate against a real user database
#[utoipa::path(
    post,
    path = "/auth/login",
    request_body = LoginRequest,
    responses(
        (status = 200, description = "Login successful", body = LoginResponse),
        (status = 400, description = "Invalid credentials"),
        (status = 429, description = "Too many requests")
    )
)]
pub async fn login(
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
    Json(payload): Json<LoginRequest>,
) -> Result<(StatusCode, Json<LoginResponse>), (StatusCode, String)> {
    // ============================================================================
    // SECURITY FIX C5: Check rate limit before processing login
    // ============================================================================
    let client_ip = addr.ip().to_string();
    if let Err(e) = check_auth_rate_limit(&client_ip) {
        tracing::warn!(" RATE LIMIT: Login attempt from {} - {}", client_ip, e);
        return Err((
            StatusCode::TOO_MANY_REQUESTS,
            "Too many login attempts. Please try again later.".to_string(),
        ));
    }

    // ============================================================================
    // SECURITY FIX C7-C11: Validate username and password input
    // ============================================================================
    let validator = LoginValidator::new(payload.username.clone(), payload.password.clone());
    if let Err(e) = validator.validate() {
        tracing::warn!(" LOGIN VALIDATION FAILED: {} from {}", e, client_ip);
        return Err((
            StatusCode::BAD_REQUEST,
            format!("Invalid credentials: {}", e),
        ));
    }

    // TODO: In production, validate username/password against database
    // For now, accept any username (testing only)

    // SECURITY NOTE: In production, validate credentials!
    // This is for testing/development only
    let user_id = format!("user-{}", uuid::Uuid::new_v4());

    match generate_token(&user_id, &payload.username) {
        Ok(token) => {
            info!(" Login successful for user: {}", payload.username);

            Ok((
                StatusCode::OK,
                Json(LoginResponse {
                    access_token: token,
                    token_type: "Bearer".to_string(),
                    expires_in: 24 * 3600, // 24 hours
                    user_id,
                    username: payload.username,
                }),
            ))
        }
        Err(e) => {
            tracing::error!(" Token generation failed: {}", e);
            Err((
                StatusCode::INTERNAL_SERVER_ERROR,
                "Failed to generate token".to_string(),
            ))
        }
    }
}

/// Logout endpoint
#[utoipa::path(
    post,
    path = "/auth/logout",
    responses(
        (status = 200, description = "Logout successful")
    ),
    security(
        ("bearer_auth" = [])
    )
)]
pub async fn logout() -> StatusCode {
    StatusCode::OK
}

/// Verify token endpoint - Check if token is valid
pub async fn verify_token(
    ValidatedJwt(claims): ValidatedJwt,
) -> (StatusCode, Json<serde_json::Value>) {
    info!(" Token verified for user: {}", claims.user_id);

    (
        StatusCode::OK,
        Json(serde_json::json!({
            "valid": true,
            "user_id": claims.user_id,
            "username": claims.username,
            "permissions": claims.permissions,
        })),
    )
}

/// Get current user info endpoint
pub async fn whoami(ValidatedJwt(claims): ValidatedJwt) -> (StatusCode, Json<serde_json::Value>) {
    (
        StatusCode::OK,
        Json(serde_json::json!({
            "user_id": claims.user_id,
            "username": claims.username,
            "permissions": claims.permissions,
        })),
    )
}
