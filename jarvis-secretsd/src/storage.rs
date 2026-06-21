use crate::crypto::{aead_decrypt, aead_encrypt, generate_secret};
use crate::types::{SecretError, SecretMeta, SecretRecord, Vault, VaultStats};
use anyhow::{Context, Result};
use chrono::Utc;
use parking_lot::RwLock;
use std::fs;
use std::path::PathBuf;
use std::sync::Arc;
use tracing::{info, warn};
use zeroize::Zeroizing;

/// Thread-safe vault storage with encryption
pub struct VaultStore {
    vault: Arc<RwLock<Vault>>,
    master: Zeroizing<[u8; 32]>,
    path: PathBuf,
}

impl VaultStore {
    /// Load existing vault or create new one
    pub fn load_or_init(path: &str, master: Zeroizing<[u8; 32]>, rotation_days: u32, grace_days: u32) -> Result<Self> {
        let path_buf = PathBuf::from(path);

        let vault = if path_buf.exists() {
            let content = fs::read_to_string(&path_buf)
                .context("failed to read vault file")?;

            if content.trim().is_empty() {
                warn!("Vault file at {} is empty, initializing new vault.", path);
                Vault::new(rotation_days, grace_days)
            } else {
                info!("Loading existing vault from {}", path);
                let v: Vault = serde_json::from_str(&content)
                    .context("failed to parse vault JSON")?;
                info!("Loaded vault with {} secrets", v.secrets.len());
                v
            }
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

        drop(vault); 
        self.save()?;

        Ok(())
    }

    /// Get a secret (decrypt) - Returns Zeroizing to ensure cleanup
    pub fn get_secret(&self, name: &str) -> Result<(Zeroizing<String>, SecretMeta), SecretError> {
        let vault = self.vault.read();

        let record = vault.secrets.get(name)
            .ok_or_else(|| SecretError::NotFound(name.to_string()))?;

        // MLOCK: Prevent swapping during decryption
        #[cfg(all(unix, not(target_os = "macos")))]
        unsafe {
            // Linux requires CAP_IPC_LOCK capability for non-root users.
            // This is provided via systemd AmbientCapabilities=CAP_IPC_LOCK
            // or docker cap_add: - IPC_LOCK.
            if libc::mlock(self.master.as_ptr() as *const libc::c_void, 32) != 0 {
                let err = std::io::Error::last_os_error();
                tracing::error!("SECOPS ALERT: Failed to mlock master key in memory (missing CAP_IPC_LOCK?): {}", err);
            }
        }
        #[cfg(target_os = "macos")]
        {
            // macOS mlock requires root privileges, breaking rootless isolation.
            // Skipping mlock on macOS.
        }

        let decrypted_bytes = aead_decrypt(&self.master, &record.enc)
            .map_err(|e| SecretError::Crypto(e.to_string()))?;

        let value_str = std::str::from_utf8(decrypted_bytes.as_ref())
            .map_err(|e| SecretError::Crypto(format!("invalid UTF-8: {}", e)))?;

        Ok((Zeroizing::new(value_str.to_string()), record.meta.clone()))
    }

    /// Generate and store a new secret
    pub fn generate_and_store(&self, name: &str, secret_type: &str) -> Result<(), SecretError> {
        let value = if secret_type == "deterministic_password" {
            // Derive a stable 32-char password from master key + name using HKDF
            // This prevents mismatch with DBs if the tmpfs vault is wiped on restart.
            use hkdf::Hkdf;
            use sha2::Sha256;
            let hk = Hkdf::<Sha256>::new(None, &*self.master);
            let mut derived = [0u8; 32];
            hk.expand(name.as_bytes(), &mut derived)
                .map_err(|_| SecretError::Crypto("HKDF expansion failed".to_string()))?;
            
            const CHARSET: &[u8] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
            let pwd: String = derived.iter().map(|&b| CHARSET[(b as usize) % CHARSET.len()] as char).collect();
            
            zeroize::Zeroizing::new(pwd)
        } else {
            generate_secret(secret_type)
                .map_err(|e| SecretError::Crypto(e.to_string()))?
        };

        self.set_secret(name, &*value, None)?;

        info!(" Generated new secret: {}", name);
        Ok(())
    }

    /// Rotate a secret (keep old in prev)
    pub fn rotate_secret(&self, name: &str, secret_type: &str) -> Result<(), SecretError> {
        let (_, old_meta) = self.get_secret(name)?;

        if secret_type == "deterministic_password" {
            return Err(SecretError::Storage("Deterministic passwords cannot be automatically rotated without external sync".into()));
        }

        let new_value = generate_secret(secret_type)
            .map_err(|e| SecretError::Crypto(e.to_string()))?;

        let mut new_meta = {
            let vault = self.vault.read();
            let kid = format!("{}-{}", name, Utc::now().format("%Y%m%d-%H%M%S"));
            SecretMeta::new("aes-gcm-256".to_string(), kid, Some(vault.rotation_days))
        };
        new_meta.prev = vec![old_meta.kid.clone()];

        self.set_secret(name, &*new_value, Some(new_meta))?;

        info!(" Rotated secret: {} (old kid: {})", name, old_meta.kid);
        Ok(())
    }

    /// Save vault to disk (RAM-FS assumed)
    pub fn save(&self) -> Result<(), SecretError> {
        let vault = self.vault.read();
        let json = serde_json::to_string(&*vault)
            .map_err(|e| SecretError::Storage(format!("JSON serialization failed: {}", e)))?;

        let temp_path = self.path.with_extension(format!("tmp.{}", rand::random::<u64>()));
        
        #[cfg(unix)]
        {
            use std::os::unix::fs::OpenOptionsExt;
            let mut file = std::fs::OpenOptions::new()
                .write(true)
                .create_new(true)
                .mode(0o600)
                .open(&temp_path)
                .map_err(|e| SecretError::Storage(format!("failed to create vault: {}", e)))?;
            use std::io::Write;
            file.write_all(json.as_bytes())
                .map_err(|e| SecretError::Storage(format!("failed to write vault: {}", e)))?;
        }
        #[cfg(not(unix))]
        {
            fs::write(&temp_path, json)
                .map_err(|e| SecretError::Storage(format!("failed to write vault: {}", e)))?;
        }

        fs::rename(&temp_path, &self.path)
            .map_err(|e| SecretError::Storage(format!("failed to rename vault: {}", e)))?;

        Ok(())
    }

    pub fn stats(&self) -> VaultStats {
        let vault = self.vault.read();
        let expired_count = vault.secrets.values().filter(|r| r.meta.is_expired()).count();
        VaultStats {
            total_secrets: vault.secrets.len(),
            expired_secrets: expired_count,
            rotation_days: vault.rotation_days,
            grace_days: vault.grace_days,
            created_at: vault.created_at,
            updated_at: vault.updated_at,
        }
    }

    pub fn list_secrets(&self) -> Vec<(String, SecretMeta)> {
        let vault = self.vault.read();
        vault.secrets.iter().map(|(n, r)| (n.clone(), r.meta.clone())).collect()
    }

    pub fn rotation_days(&self) -> u32 {
        self.vault.read().rotation_days
    }

    pub fn grace_days(&self) -> u32 {
        self.vault.read().grace_days
    }
}

impl Drop for VaultStore {
    fn drop(&mut self) {
        #[cfg(all(unix, not(target_os = "macos")))]
        unsafe {
            let _ = libc::munlock(self.master.as_ptr() as *const libc::c_void, 32);
        }
    }
}
