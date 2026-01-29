use crate::crypto::{ed25519_generate, sign_audit};
use anyhow::{Context, Result};
use chrono::Utc;
use serde::{Deserialize, Serialize};
use std::fs::{File, OpenOptions};
use std::io::{BufWriter, Write};
use std::path::{Path, PathBuf};
use std::sync::Mutex;
use tracing::{error, info};
use zeroize::Zeroizing;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AuditEntry {
    pub timestamp: String,
    pub event: String,
    pub client: Option<String>,
    pub secret_name: Option<String>,
    pub result: String,
    pub signature: String,
}

pub struct AuditLog {
    path: PathBuf,
    signing_key: Zeroizing<String>,
    writer: Mutex<BufWriter<File>>,
}

impl AuditLog {
    /// Initialize audit log (create if not exists)
    pub fn init(path: &str) -> Result<Self> {
        let path_buf = PathBuf::from(path);

        // Ensure directory exists
        if let Some(parent) = path_buf.parent() {
            std::fs::create_dir_all(parent)
                .context("failed to create audit directory")?;
        }

        // Load or generate signing key
        let signing_key = Self::load_or_generate_signing_key(&path_buf)?;

        // Open file in append mode
        let file = OpenOptions::new()
            .create(true)
            .append(true)
            .open(&path_buf)
            .with_context(|| format!("failed to open audit log: {}", path))?;

        let writer = BufWriter::new(file);

        info!(" Audit log initialized: {}", path);

        Ok(Self {
            path: path_buf,
            signing_key,
            writer: Mutex::new(writer),
        })
    }

    /// Load or generate Ed25519 signing key for audit
    fn load_or_generate_signing_key(audit_path: &Path) -> Result<Zeroizing<String>> {
        let key_path = audit_path.with_extension("sign.key");

        if key_path.exists() {
            let key = std::fs::read_to_string(&key_path)
                .context("failed to read signing key")?;
            Ok(Zeroizing::new(key.trim().to_string()))
        } else {
            let (sk, pk) = ed25519_generate();

            std::fs::write(&key_path, &*sk)
                .context("failed to write signing key")?;

            let pk_path = audit_path.with_extension("sign.pub");
            std::fs::write(&pk_path, &pk)
                .context("failed to write public key")?;

            // Set permissions 600 on signing key
            #[cfg(unix)]
            {
                use std::os::unix::fs::PermissionsExt;
                let mut perms = std::fs::metadata(&key_path)?.permissions();
                perms.set_mode(0o600);
                std::fs::set_permissions(&key_path, perms)?;
            }

            info!(" Generated new audit signing key");
            Ok(sk)
        }
    }

    /// Log an event with signature
    pub fn log(
        &self,
        event: &str,
        client: Option<&str>,
        secret_name: Option<&str>,
        result: &str,
    ) -> Result<()> {
        let timestamp = Utc::now().to_rfc3339();

        // Create audit entry
        let entry_data = format!(
            "{}|{}|{}|{}|{}",
            timestamp,
            event,
            client.unwrap_or(""),
            secret_name.unwrap_or(""),
            result
        );

        // Sign the entry
        let signature = sign_audit(&self.signing_key, &entry_data)
            .context("failed to sign audit entry")?;

        let entry = AuditEntry {
            timestamp,
            event: event.to_string(),
            client: client.map(|s| s.to_string()),
            secret_name: secret_name.map(|s| s.to_string()),
            result: result.to_string(),
            signature,
        };

        // Write JSONL (JSON lines)
        let json = serde_json::to_string(&entry)?;

        let mut writer = self.writer.lock().unwrap();
        writeln!(writer, "{}", json)?;
        writer.flush()?;

        Ok(())
    }

    /// Log error (convenience)
    pub fn log_error(&self, event: &str, client: Option<&str>, error: &str) {
        if let Err(e) = self.log(event, client, None, &format!("error: {}", error)) {
            error!(" Failed to write audit log: {}", e);
        }
    }

    /// Log success (convenience)
    pub fn log_success(&self, event: &str, client: Option<&str>, secret: Option<&str>) {
        if let Err(e) = self.log(event, client, secret, "success") {
            error!(" Failed to write audit log: {}", e);
        }
    }
}