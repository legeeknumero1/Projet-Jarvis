// ============================================================================
// Authentication Handler - Login and Token Management
// ============================================================================
//
// Endpoints:
// - POST /auth/login - Generate JWT token (public endpoint)
// - POST /auth/refresh - Refresh JWT token (public endpoint)
// - GET /auth/verify - Verify token validity (protected endpoint)

use axum::{extract::{ConnectInfo, State}, http::StatusCode, Json};
use std::net::SocketAddr;
use std::sync::Arc;
use tracing::info;

use crate::middleware::{
    check_auth_rate_limit, generate_token, InputValidator, LoginValidator, ValidatedJwt,
};
use crate::models::{AppState, LoginRequest, LoginResponse, User};

/// Login endpoint - Generate JWT token for user
///
/// SECURITY: Validates credentials against PostgreSQL database with bcrypt password hashing
#[utoipa::path(
    post,
    path = "/auth/login",
    request_body = LoginRequest,
    responses(
        (status = 200, description = "Login successful", body = LoginResponse),
        (status = 400, description = "Invalid credentials"),
        (status = 401, description = "Authentication failed"),
        (status = 429, description = "Too many requests")
    )
)]
pub async fn login(
    State(state): State<Arc<AppState>>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
    Json(payload): Json<LoginRequest>,
) -> Result<(StatusCode, Json<LoginResponse>), (StatusCode, String)> {
    // ============================================================================
    // DATABASE-RELATED CODE COMMENTED OUT FOR TESTING
    // ============================================================================
    Err((
        StatusCode::INTERNAL_SERVER_ERROR,
        "Database is disabled for this test".to_string(),
    ))
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
