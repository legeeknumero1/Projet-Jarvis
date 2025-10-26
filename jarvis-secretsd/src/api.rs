use crate::audit::AuditLog;
use crate::policy::Policy;
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
use tracing::{info, warn};

#[derive(Clone)]
pub struct AppState {
    pub store: Arc<VaultStore>,
    pub policy: Arc<Policy>,
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

/// Extract client ID from header
fn extract_client(headers: &HeaderMap) -> Option<String> {
    headers
        .get("X-Jarvis-Client")
        .and_then(|v| v.to_str().ok())
        .map(|s| s.to_string())
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
    let client = extract_client(&headers)
        .ok_or_else(|| SecretError::NotAuthorized("missing X-Jarvis-Client header".to_string()))?;

    // Check policy
    if !state.policy.allowed(&client, &name) {
        state.audit.log_error("get_secret", Some(&client), "not_authorized");
        return Err(SecretError::NotAuthorized(format!(
            "client {} not allowed to access {}",
            client, name
        )));
    }

    // Retrieve secret
    let (value, meta) = state.store.get_secret(&name)?;

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

    // Only admin can create secrets
    if client != "admin" {
        state.audit.log_error("create_secret", Some(&client), "not_authorized");
        return Err(SecretError::NotAuthorized(format!(
            "only admin can create secrets, got client: {}",
            client
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
        .filter(|(name, _)| state.policy.allowed(&client, name))
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

    // Only admin can rotate
    if client != "admin" {
        state.audit.log_error("rotate", Some(&client), "not_authorized");
        return Err(SecretError::NotAuthorized(format!(
            "only admin can rotate secrets, got client: {}",
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

    info!("🔄 Rotated {} secrets via API", rotated.len());

    Ok(Json(RotateResponse {
        rotated_count: rotated.len(),
        rotated,
    }))
}
