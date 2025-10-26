use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};
use std::collections::HashMap;
use thiserror::Error;

/// Secret metadata
#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct SecretMeta {
    pub alg: String,
    pub kid: String,
    pub created_at: DateTime<Utc>,
    pub expires_at: Option<DateTime<Utc>>,
    #[serde(default)]
    pub prev: Vec<String>,
}

impl SecretMeta {
    pub fn new(alg: String, kid: String, rotation_days: Option<u32>) -> Self {
        let created_at = Utc::now();
        let expires_at = rotation_days.map(|days| {
            created_at + chrono::Duration::days(days as i64)
        });

        Self {
            alg,
            kid,
            created_at,
            expires_at,
            prev: Vec::new(),
        }
    }

    pub fn is_expired(&self) -> bool {
        if let Some(expires_at) = self.expires_at {
            Utc::now() > expires_at
        } else {
            false
        }
    }
}

/// Secret record with encrypted value
#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct SecretRecord {
    /// Encrypted value: "b64(nonce):b64(ciphertext)"
    pub enc: String,
    #[serde(flatten)]
    pub meta: SecretMeta,
}

/// Vault structure (on-disk JSON format)
#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct Vault {
    pub version: u8,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
    pub rotation_days: u32,
    pub grace_days: u32,
    pub secrets: HashMap<String, SecretRecord>,
}

impl Vault {
    pub fn new(rotation_days: u32, grace_days: u32) -> Self {
        let now = Utc::now();
        Self {
            version: 1,
            created_at: now,
            updated_at: now,
            rotation_days,
            grace_days,
            secrets: HashMap::new(),
        }
    }

    pub fn touch(&mut self) {
        self.updated_at = Utc::now();
    }
}

/// API request/response types
#[derive(Deserialize)]
pub struct CreateSecretRequest {
    pub name: String,
    pub value: String,
    #[serde(default)]
    pub metadata: HashMap<String, String>,
}

#[derive(Serialize)]
pub struct GetSecretResponse {
    pub name: String,
    pub value: String,
    pub kid: String,
    pub expires_at: Option<DateTime<Utc>>,
}

#[derive(Deserialize)]
pub struct RotateRequest {
    #[serde(default)]
    pub names: Vec<String>,
}

#[derive(Serialize)]
pub struct RotateResponse {
    pub rotated_count: usize,
    pub rotated: Vec<String>,
}

#[derive(Serialize)]
pub struct ListSecretsResponse {
    pub secrets: Vec<SecretMetadata>,
}

#[derive(Serialize)]
pub struct SecretMetadata {
    pub name: String,
    pub kid: String,
    pub created_at: DateTime<Utc>,
    pub expires_at: Option<DateTime<Utc>>,
    pub is_expired: bool,
}

#[derive(Serialize)]
pub struct HealthResponse {
    pub status: String,
    pub version: String,
    pub uptime_secs: u64,
    pub secrets_count: usize,
}

/// Error types
#[derive(Error, Debug)]
pub enum SecretError {
    #[error("secret not found: {0}")]
    NotFound(String),

    #[error("client not authorized: {0}")]
    NotAuthorized(String),

    #[error("bad request: {0}")]
    BadRequest(String),

    #[error("secret already exists: {0}")]
    Conflict(String),

    #[error("crypto error: {0}")]
    Crypto(String),

    #[error("storage error: {0}")]
    Storage(String),

    #[error("policy error: {0}")]
    Policy(String),

    #[error("internal error: {0}")]
    Internal(String),
}

/// Error response JSON
#[derive(Serialize)]
pub struct ErrorResponse {
    pub error: String,
    pub message: String,
}

impl ErrorResponse {
    pub fn new(error: &str, message: impl Into<String>) -> Self {
        Self {
            error: error.to_string(),
            message: message.into(),
        }
    }

    pub fn from_secret_error(err: &SecretError) -> Self {
        let (code, msg) = match err {
            SecretError::NotFound(s) => ("not_found", s.clone()),
            SecretError::NotAuthorized(s) => ("not_authorized", s.clone()),
            SecretError::BadRequest(s) => ("bad_request", s.clone()),
            SecretError::Conflict(s) => ("conflict", s.clone()),
            SecretError::Crypto(s) => ("internal", format!("crypto error: {}", s)),
            SecretError::Storage(s) => ("internal", format!("storage error: {}", s)),
            SecretError::Policy(s) => ("internal", format!("policy error: {}", s)),
            SecretError::Internal(s) => ("internal", s.clone()),
        };
        Self::new(&code, msg)
    }

    pub fn to_status_code(&self) -> axum::http::StatusCode {
        use axum::http::StatusCode;
        match self.error.as_str() {
            "not_found" => StatusCode::NOT_FOUND,
            "not_authorized" => StatusCode::FORBIDDEN,
            "bad_request" => StatusCode::BAD_REQUEST,
            "conflict" => StatusCode::CONFLICT,
            _ => StatusCode::INTERNAL_SERVER_ERROR,
        }
    }
}

/// Convert SecretError to HTTP response
impl axum::response::IntoResponse for SecretError {
    fn into_response(self) -> axum::response::Response {
        let err_resp = ErrorResponse::from_secret_error(&self);
        let status = err_resp.to_status_code();
        (status, axum::Json(err_resp)).into_response()
    }
}
