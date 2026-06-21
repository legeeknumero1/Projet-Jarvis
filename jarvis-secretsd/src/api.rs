use crate::audit::AuditLog;
use crate::ids::IntrusionDetector;
use crate::policy::{Permission, Policy};
use crate::rotation::rotate_if_due;
use crate::storage::VaultStore;
use crate::types::*;
use axum::{
    extract::{Path, State},
    http::{HeaderMap, StatusCode},
    response::IntoResponse,
    routing::{get, post},
    Json, Router,
};
use std::sync::Arc;
use std::time::Instant;
use tracing::info;

#[derive(Clone)]
pub struct AppState {
    pub store: Arc<VaultStore>,
    pub policy: Arc<Policy>,
    pub ids: Arc<IntrusionDetector>,
    pub audit: Arc<AuditLog>,
    pub start_time: Instant,
}

/// Build Axum router
pub fn router(state: AppState) -> Router {
    Router::new()
        .route("/healthz", get(health_handler))
        .route("/secret/:name", get(get_secret_handler))
        .route("/secret", post(create_secret_handler))
        .route("/secrets", get(list_secrets_handler))
        .route("/rotate", post(rotate_handler))
        .with_state(state)
}

use subtle::ConstantTimeEq;

/// Constant-time string comparison to prevent timing attacks
fn secure_eq(a: &str, b: &str) -> bool {
    if a.len() != b.len() { return false; }
    a.as_bytes().ct_eq(b.as_bytes()).into()
}

/// Extract client ID from header
fn extract_client(headers: &HeaderMap) -> Option<String> {
    // 1. Check for SECRETSD_TOKENS mapping: "admin:tok1,backend:tok2"
    let tokens_env = std::env::var("SECRETSD_TOKENS").unwrap_or_default();
    if !tokens_env.is_empty() {
        if let Some(auth) = headers.get("authorization").and_then(|h| h.to_str().ok()) {
            for mapping in tokens_env.split(',') {
                let mut parts = mapping.split(':');
                if let (Some(role), Some(token)) = (parts.next(), parts.next()) {
                    let expected = format!("Bearer {}", token.trim());
                    if secure_eq(auth, &expected) {
                        return Some(role.trim().to_string());
                    }
                }
            }
        }
        tracing::error!("SECRETSD: Invalid Bearer token or mapping not found");
        return None;
    }

    // 2. Fallback to monolithic token (with X-Jarvis-Client trust)
    let expected_token = std::env::var("SECRETSD_TOKEN").unwrap_or_default();
    if expected_token.is_empty() {
        tracing::error!("SECRETSD: Tokens not configured");
        return None;
    }
    
    let expected_auth = format!("Bearer {}", expected_token);
    if let Some(auth) = headers.get("authorization").and_then(|h| h.to_str().ok()) {
        if !secure_eq(auth, &expected_auth) {
            tracing::error!("SECRETSD: Invalid Bearer token");
            return None;
        }
    } else {
        tracing::error!("SECRETSD: Missing Authorization header");
        return None;
    }

    headers.get("X-Jarvis-Client").and_then(|v| v.to_str().ok()).map(|s| s.to_string())
}

/// Health check
async fn health_handler(State(state): State<AppState>) -> impl IntoResponse {
    let stats = state.store.stats();

    let response = HealthResponse {
        status: "ok".to_string(),
        version: env!("CARGO_PKG_VERSION").to_string(),
        uptime_secs: state.start_time.elapsed().as_secs(),
        secrets_count: stats.total_secrets,
    };

    (StatusCode::OK, Json(response))
}

/// Get a secret
async fn get_secret_handler(
    State(state): State<AppState>,
    Path(name): Path<String>,
    headers: HeaderMap,
) -> Result<Json<GetSecretResponse>, SecretError> {
    let name = name.to_lowercase();
    let client = extract_client(&headers)
        .ok_or_else(|| SecretError::NotAuthorized("missing X-Jarvis-Client header".to_string()))?;

    // 1. Check IDS ban
    if state.ids.is_banned(&client) {
        state.audit.log_error("get_secret", Some(&client), "banned");
        return Err(SecretError::NotAuthorized("client is temporarily banned due to suspicious activity".to_string()));
    }

    // 2. Check Canary
    if state.ids.check_canary(&name, &client) {
        state.audit.log_error("get_secret", Some(&client), "canary_tripped");
        return Err(SecretError::NotFound(name)); // Hide existence if canary
    }

    // 3. Check policy with new Permission system
    if !state.policy.is_authorized(&client, &name, Permission::Read) {
        state.ids.report_failure(&client, "unauthorized_access_attempt");
        state.audit.log_error("get_secret", Some(&client), "not_authorized");
        
        // Artificial delay to mitigate timing attacks
        tokio::time::sleep(std::time::Duration::from_millis(10)).await;

        return Err(SecretError::NotAuthorized(format!(
            "client {} not allowed to Read {}",
            client, name
        )));
    }

    // Retrieve secret
    let (value, meta) = match state.store.get_secret(&name) {
        Ok(v) => v,
        Err(SecretError::NotFound(_)) => {
            // Auto-generate based on name patterns
            let secret_type = if name.starts_with("jwt_") || name == "JWT_SECRET" {
                Some("jwt_signing_key")
            } else if name.ends_with("_encryption_key") {
                Some("jarvis_encryption_key")
            } else if name.ends_with("_key") || name.ends_with("_token") {
                Some("api_key")
            } else if name.ends_with("_password") {
                Some("deterministic_password")
            } else {
                None
            };

            if let Some(stype) = secret_type {
                info!(" Auto-generating secret '{}' of type '{}' on demand", name, stype);
                state.store.generate_and_store(&name, stype)?;
                state.store.get_secret(&name)?
            } else {
                return Err(SecretError::NotFound(name));
            }
        }
        Err(e) => return Err(e),
    };

    state.audit.log_success("get_secret", Some(&client), Some(&name));

    Ok(Json(GetSecretResponse {
        name,
        value,
        kid: meta.kid,
        expires_at: meta.expires_at,
    }))
}

/// Create/update a secret
async fn create_secret_handler(
    State(state): State<AppState>,
    headers: HeaderMap,
    Json(req): Json<CreateSecretRequest>,
) -> Result<StatusCode, SecretError> {
    let client = extract_client(&headers)
        .ok_or_else(|| SecretError::NotAuthorized("missing X-Jarvis-Client header".to_string()))?;

    // Check IDS ban
    if state.ids.is_banned(&client) {
        return Err(SecretError::NotAuthorized("client is temporarily banned".to_string()));
    }

    // Check policy
    if !state.policy.is_authorized(&client, &req.name, Permission::Write) {
        state.ids.report_failure(&client, "unauthorized_write_attempt");
        state.audit.log_error("create_secret", Some(&client), "not_authorized");
        return Err(SecretError::NotAuthorized(format!(
            "client {} not allowed to Write {}",
            client, req.name
        )));
    }

    // Validate input
    if req.name.is_empty() || req.value.is_empty() {
        return Err(SecretError::BadRequest("name and value are required".to_string()));
    }

    // Store secret
    state.store.set_secret(&req.name, &req.value, None)?;

    state.audit.log_success("create_secret", Some(&client), Some(&req.name));

    Ok(StatusCode::CREATED)
}

/// List secrets metadata
async fn list_secrets_handler(
    State(state): State<AppState>,
    headers: HeaderMap,
) -> Result<Json<ListSecretsResponse>, SecretError> {
    let client = extract_client(&headers)
        .ok_or_else(|| SecretError::NotAuthorized("missing X-Jarvis-Client header".to_string()))?;

    let all_secrets = state.store.list_secrets();

    // Filter by policy
    let filtered: Vec<SecretMetadata> = all_secrets
        .into_iter()
        .filter(|(name, _)| state.policy.is_authorized(&client, name, Permission::List))
        .map(|(name, meta)| {
            let is_expired = meta.is_expired();
            SecretMetadata {
                name,
                kid: meta.kid,
                created_at: meta.created_at,
                expires_at: meta.expires_at,
                is_expired,
            }
        })
        .collect();

    state.audit.log_success("list_secrets", Some(&client), None);

    Ok(Json(ListSecretsResponse {
        secrets: filtered,
    }))
}

/// Rotate secrets
async fn rotate_handler(
    State(state): State<AppState>,
    headers: HeaderMap,
    Json(req): Json<RotateRequest>,
) -> Result<Json<RotateResponse>, SecretError> {
    let client = extract_client(&headers)
        .ok_or_else(|| SecretError::NotAuthorized("missing X-Jarvis-Client header".to_string()))?;

    // Check IDS ban
    if state.ids.is_banned(&client) {
        return Err(SecretError::NotAuthorized("client is temporarily banned".to_string()));
    }

    // Check policy
    if !state.policy.is_authorized(&client, "*", Permission::Rotate) {
        state.ids.report_failure(&client, "unauthorized_rotate_attempt");
        state.audit.log_error("rotate", Some(&client), "not_authorized");
        return Err(SecretError::NotAuthorized(format!(
            "client {} not allowed to Rotate",
            client
        )));
    }

    let names = if req.names.is_empty() {
        None
    } else {
        Some(req.names)
    };

    let rotated = rotate_if_due(&state.store, names)?;

    state.audit.log_success("rotate", Some(&client), None);

    info!(" Rotated {} secrets via API", rotated.len());

    Ok(Json(RotateResponse {
        rotated_count: rotated.len(),
        rotated,
    }))
}