use crate::storage::VaultStore;
use crate::types::{SecretError, SecretMeta};
use chrono::{DateTime, Utc};
use std::sync::Arc;
use tokio::time::{interval, Duration};
use tracing::{info, warn};

/// Check if secret is due for rotation
pub fn due_for_rotation(
    meta: &SecretMeta,
    now: DateTime<Utc>,
    rotation_days: u32,
) -> bool {
    if let Some(expires_at) = meta.expires_at {
        now >= expires_at
    } else {
        // No expiry set - check age
        let age = now.signed_duration_since(meta.created_at);
        age.num_days() >= rotation_days as i64
    }
}

/// Rotate secrets that are due
pub fn rotate_if_due(
    store: &VaultStore,
    names: Option<Vec<String>>,
) -> Result<Vec<String>, SecretError> {
    let rotation_days = store.rotation_days();
    let now = Utc::now();

    let secrets_to_rotate: Vec<String> = if let Some(names) = names {
        names
    } else {
        store
            .list_secrets()
            .into_iter()
            .filter(|(_name, meta)| due_for_rotation(meta, now, rotation_days))
            .map(|(name, _)| name)
            .collect()
    };

    let mut rotated = Vec::new();

    for name in secrets_to_rotate {
        let secret_type = infer_secret_type(&name);

        match store.rotate_secret(&name, secret_type) {
            Ok(_) => {
                info!(" Rotated: {}", name);
                rotated.push(name);
            }
            Err(e) => {
                warn!("  Failed to rotate {}: {}", name, e);
            }
        }
    }

    Ok(rotated)
}

/// Infer secret type from name (heuristic)
fn infer_secret_type(name: &str) -> &str {
    let lower = name.to_lowercase();

    if lower.contains("jwt") || lower.contains("signing") {
        "jwt_signing_key"
    } else if lower.contains("postgres") || lower.contains("password") {
        "postgres_password"
    } else if lower.contains("encryption") || lower.contains("backup") {
        "backup_encryption_key"
    } else if lower.contains("api") && lower.contains("key") {
        "api_key"
    } else {
        "api_key" // Default
    }
}

/// Start rotation scheduler (runs daily check)
pub async fn start_rotation_scheduler(store: Arc<VaultStore>) {
    let mut tick = interval(Duration::from_secs(86400)); // 24 hours

    info!(" Rotation scheduler started (checking daily)");

    loop {
        tick.tick().await;

        info!(" Checking for secrets due for rotation...");

        match rotate_if_due(&store, None) {
            Ok(rotated) => {
                if rotated.is_empty() {
                    info!(" No secrets due for rotation");
                } else {
                    info!(" Rotated {} secrets: {:?}", rotated.len(), rotated);
                }
            }
            Err(e) => {
                warn!("  Rotation check failed: {}", e);
            }
        }
    }
}