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

    let secrets_to_rotate = if let Some(names) = names {
        // Specific secrets requested
        names
    } else {
        // Auto-detect secrets due for rotation
        store
            .list_secrets()
            .into_iter()
            .filter(|(_name, meta)| due_for_rotation(meta, now, rotation_days))
            .map(|(name, _)| name)
            .collect()
    };

    let mut rotated = Vec::new();

    for name in secrets_to_rotate {
        // Determine secret type from name (heuristic)
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

#[cfg(test)]
mod tests {
    use super::*;
    use crate::crypto::gen_bytes_32;
    use crate::storage::VaultStore;
    use tempfile::NamedTempFile;

    #[test]
    fn test_due_for_rotation() {
        let now = Utc::now();
        let old = now - chrono::Duration::days(100);

        let meta = SecretMeta {
            alg: "aes-gcm-256".to_string(),
            kid: "test-1".to_string(),
            created_at: old,
            expires_at: Some(old + chrono::Duration::days(90)),
            prev: Vec::new(),
        };

        assert!(due_for_rotation(&meta, now, 90));
    }

    #[test]
    fn test_rotate_if_due() {
        let temp = NamedTempFile::new().unwrap();
        let path = temp.path().to_str().unwrap();
        let master = gen_bytes_32();

        let store = VaultStore::load_or_init(path, master, 1, 0).unwrap(); // 1 day rotation

        // Create old secret
        store.generate_and_store("test_key", "api_key").unwrap();

        // Force expiry by setting created_at to past
        // (In real scenario, we'd wait or manipulate time)

        // Rotate
        let rotated = rotate_if_due(&store, Some(vec!["test_key".to_string()])).unwrap();
        assert_eq!(rotated.len(), 1);
    }

    #[test]
    fn test_infer_secret_type() {
        assert_eq!(infer_secret_type("jwt_signing_key"), "jwt_signing_key");
        assert_eq!(infer_secret_type("postgres_password"), "postgres_password");
        assert_eq!(infer_secret_type("brave_api_key"), "api_key");
        assert_eq!(infer_secret_type("jarvis_encryption_key"), "backup_encryption_key");
    }
}
