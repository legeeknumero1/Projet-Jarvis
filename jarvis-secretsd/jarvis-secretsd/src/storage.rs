use crate::crypto::{aead_decrypt, aead_encrypt, generate_secret};
use crate::types::{SecretError, SecretMeta, SecretRecord, Vault};
use anyhow::{Context, Result};
use chrono::Utc;
use parking_lot::RwLock;
use std::fs;
use std::path::PathBuf;
use std::sync::Arc;
use tracing::{info, warn};

/// Thread-safe vault storage with encryption
pub struct VaultStore {
    vault: Arc<RwLock<Vault>>,
    master: [u8; 32],
    path: PathBuf,
}

impl VaultStore {
    /// Load existing vault or create new one
    pub fn load_or_init(path: &str, master: [u8; 32], rotation_days: u32, grace_days: u32) -> Result<Self> {
        let path_buf = PathBuf::from(path);

        let vault = if path_buf.exists() {
            info!(" Loading existing vault from {}", path);
            let content = fs::read_to_string(&path_buf)
                .context("failed to read vault file")?;

            let v: Vault = serde_json::from_str(&content)
                .context("failed to parse vault JSON")?;

            info!(" Loaded vault with {} secrets", v.secrets.len());
            v
        } else {
            info!(" Creating new vault at {}", path);

            // Ensure directory exists
            if let Some(parent) = path_buf.parent() {
                fs::create_dir_all(parent)
                    .context("failed to create vault directory")?;
            }

            Vault::new(rotation_days, grace_days)
        };

        Ok(Self {
            vault: Arc::new(RwLock::new(vault)),
            master,
            path: path_buf,
        })
    }

    /// Set a secret (encrypt and store)
    pub fn set_secret(&self, name: &str, plaintext: &str, meta: Option<SecretMeta>) -> Result<(), SecretError> {
        let encrypted = aead_encrypt(&self.master, plaintext.as_bytes())
            .map_err(|e| SecretError::Crypto(e.to_string()))?;

        let mut vault = self.vault.write();

        let meta = meta.unwrap_or_else(|| {
            let kid = format!("{}-{}", name, Utc::now().format("%Y%m%d-%H%M%S"));
            SecretMeta::new("aes-gcm-256".to_string(), kid, Some(vault.rotation_days))
        });

        let record = SecretRecord {
            enc: encrypted,
            meta,
        };

        vault.secrets.insert(name.to_string(), record);
        vault.touch();

        drop(vault); // Release lock before saving
        self.save()?;

        Ok(())
    }

    /// Get a secret (decrypt)
    pub fn get_secret(&self, name: &str) -> Result<(String, SecretMeta), SecretError> {
        let vault = self.vault.read();

        let record = vault.secrets.get(name)
            .ok_or_else(|| SecretError::NotFound(name.to_string()))?;

        let decrypted_bytes = aead_decrypt(&self.master, &record.enc)
            .map_err(|e| SecretError::Crypto(e.to_string()))?;

        let value = String::from_utf8(decrypted_bytes)
            .map_err(|e| SecretError::Crypto(format!("invalid UTF-8: {}", e)))?;

        Ok((value, record.meta.clone()))
    }

    /// Check if secret exists
    pub fn exists(&self, name: &str) -> bool {
        self.vault.read().secrets.contains_key(name)
    }

    /// Delete a secret
    pub fn delete_secret(&self, name: &str) -> Result<(), SecretError> {
        let mut vault = self.vault.write();

        if vault.secrets.remove(name).is_none() {
            return Err(SecretError::NotFound(name.to_string()));
        }

        vault.touch();
        drop(vault);
        self.save()?;

        Ok(())
    }

    /// List all secret names with metadata
    pub fn list_secrets(&self) -> Vec<(String, SecretMeta)> {
        let vault = self.vault.read();
        vault
            .secrets
            .iter()
            .map(|(name, record)| (name.clone(), record.meta.clone()))
            .collect()
    }

    /// Get vault statistics
    pub fn stats(&self) -> VaultStats {
        let vault = self.vault.read();

        let expired_count = vault
            .secrets
            .values()
            .filter(|r| r.meta.is_expired())
            .count();

        VaultStats {
            total_secrets: vault.secrets.len(),
            expired_secrets: expired_count,
            rotation_days: vault.rotation_days,
            grace_days: vault.grace_days,
            created_at: vault.created_at,
            updated_at: vault.updated_at,
        }
    }

    /// Generate and store a new secret
    pub fn generate_and_store(&self, name: &str, secret_type: &str) -> Result<(), SecretError> {
        let value = generate_secret(secret_type)
            .map_err(|e| SecretError::Crypto(e.to_string()))?;

        self.set_secret(name, &value, None)?;

        info!(" Generated new secret: {}", name);
        Ok(())
    }

    /// Rotate a secret (keep old in prev)
    pub fn rotate_secret(&self, name: &str, secret_type: &str) -> Result<(), SecretError> {
        // Get current secret to preserve in prev
        let (_, old_meta) = self.get_secret(name)?;

        // Generate new secret
        let new_value = generate_secret(secret_type)
            .map_err(|e| SecretError::Crypto(e.to_string()))?;

        // Create new metadata with old kid in prev
        let mut new_meta = {
            let vault = self.vault.read();
            let kid = format!("{}-{}", name, Utc::now().format("%Y%m%d-%H%M%S"));
            SecretMeta::new("aes-gcm-256".to_string(), kid, Some(vault.rotation_days))
        };
        new_meta.prev = vec![old_meta.kid.clone()];

        self.set_secret(name, &new_value, Some(new_meta))?;

        info!(" Rotated secret: {} (old kid: {})", name, old_meta.kid);
        Ok(())
    }

    /// Save vault to disk (atomic write)
    pub fn save(&self) -> Result<(), SecretError> {
        let vault = self.vault.read();
        let json = serde_json::to_string_pretty(&*vault)
            .map_err(|e| SecretError::Storage(format!("JSON serialization failed: {}", e)))?;

        // Atomic write: write to temp file, then rename
        let temp_path = self.path.with_extension("tmp");
        fs::write(&temp_path, json)
            .map_err(|e| SecretError::Storage(format!("failed to write vault: {}", e)))?;

        fs::rename(&temp_path, &self.path)
            .map_err(|e| SecretError::Storage(format!("failed to rename vault: {}", e)))?;

        // Set file permissions to 600 (owner read/write only)
        #[cfg(unix)]
        {
            use std::os::unix::fs::PermissionsExt;
            let mut perms = fs::metadata(&self.path)
                .map_err(|e| SecretError::Storage(format!("failed to get metadata: {}", e)))?
                .permissions();
            perms.set_mode(0o600);
            fs::set_permissions(&self.path, perms)
                .map_err(|e| SecretError::Storage(format!("failed to set permissions: {}", e)))?;
        }

        Ok(())
    }

    /// Get rotation days from vault
    pub fn rotation_days(&self) -> u32 {
        self.vault.read().rotation_days
    }

    /// Get grace days from vault
    pub fn grace_days(&self) -> u32 {
        self.vault.read().grace_days
    }
}

#[derive(Debug, Clone)]
pub struct VaultStats {
    pub total_secrets: usize,
    pub expired_secrets: usize,
    pub rotation_days: u32,
    pub grace_days: u32,
    pub created_at: chrono::DateTime<Utc>,
    pub updated_at: chrono::DateTime<Utc>,
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::NamedTempFile;

    #[test]
    fn test_vault_create_and_load() {
        let temp = NamedTempFile::new().unwrap();
        let path = temp.path().to_str().unwrap();
        let master = crate::crypto::gen_bytes_32();

        // Create new vault
        let store = VaultStore::load_or_init(path, master, 90, 14).unwrap();
        assert_eq!(store.stats().total_secrets, 0);

        // Load existing vault
        let store2 = VaultStore::load_or_init(path, master, 90, 14).unwrap();
        assert_eq!(store2.stats().total_secrets, 0);
    }

    #[test]
    fn test_set_and_get_secret() {
        let temp = NamedTempFile::new().unwrap();
        let path = temp.path().to_str().unwrap();
        let master = crate::crypto::gen_bytes_32();

        let store = VaultStore::load_or_init(path, master, 90, 14).unwrap();

        store.set_secret("test_key", "secret_value", None).unwrap();

        let (value, meta) = store.get_secret("test_key").unwrap();
        assert_eq!(value, "secret_value");
        assert_eq!(meta.alg, "aes-gcm-256");
    }

    #[test]
    fn test_generate_and_rotate() {
        let temp = NamedTempFile::new().unwrap();
        let path = temp.path().to_str().unwrap();
        let master = crate::crypto::gen_bytes_32();

        let store = VaultStore::load_or_init(path, master, 90, 14).unwrap();

        // Generate
        store.generate_and_store("jwt_key", "jwt_signing_key").unwrap();
        let (value1, meta1) = store.get_secret("jwt_key").unwrap();

        // Rotate
        store.rotate_secret("jwt_key", "jwt_signing_key").unwrap();
        let (value2, meta2) = store.get_secret("jwt_key").unwrap();

        assert_ne!(value1, value2); // Values should be different
        assert_ne!(meta1.kid, meta2.kid); // Kids should be different
        assert_eq!(meta2.prev, vec![meta1.kid]); // Old kid in prev
    }
}
