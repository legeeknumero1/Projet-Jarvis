use anyhow::{Context, Result};
use serde::{Deserialize, Serialize};
use std::fs;
use std::path::Path;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Config {
    #[serde(default)]
    pub server: ServerConfig,

    #[serde(default)]
    pub paths: PathsConfig,

    #[serde(default)]
    pub security: SecurityConfig,

    #[serde(default)]
    pub crypto: CryptoConfig,

    #[serde(default)]
    pub logging: LoggingConfig,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ServerConfig {
    #[serde(default = "default_bind_addr")]
    pub bind_addr: String,

    #[serde(default)]
    pub allow_unix_socket: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PathsConfig {
    #[serde(default = "default_vault_path")]
    pub vault_path: String,

    #[serde(default = "default_audit_path")]
    pub audit_path: String,

    #[serde(default = "default_master_key_path")]
    pub master_key_path: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SecurityConfig {
    #[serde(default = "default_rotation_days")]
    pub rotation_days: u32,

    #[serde(default = "default_grace_days")]
    pub grace_days: u32,

    #[serde(default = "default_true")]
    pub require_client_id_header: bool,

    #[serde(default = "default_true")]
    pub deny_network_remote: bool,

    #[serde(default = "default_policy_path")]
    pub rbac_policy_path: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CryptoConfig {
    #[serde(default = "default_aead")]
    pub aead: String,

    #[serde(default = "default_jwt_algo")]
    pub jwt_sign_algo: String,

    #[serde(default = "default_kdf")]
    pub kdf: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LoggingConfig {
    #[serde(default = "default_log_level")]
    pub level: String,

    #[serde(default)]
    pub json: bool,
}

// Default values
fn default_bind_addr() -> String {
    "127.0.0.1:8081".to_string()
}

fn default_vault_path() -> String {
    "/opt/jarvis/secrets/vault.json".to_string()
}

fn default_audit_path() -> String {
    "/opt/jarvis/audit/audit.jsonl".to_string()
}

fn default_master_key_path() -> String {
    "/opt/jarvis/master.key".to_string()
}

fn default_rotation_days() -> u32 {
    90
}

fn default_grace_days() -> u32 {
    14
}

fn default_true() -> bool {
    true
}

fn default_policy_path() -> String {
    "/etc/jarvis-secretsd/policy.yaml".to_string()
}

fn default_aead() -> String {
    "aes-gcm-256".to_string()
}

fn default_jwt_algo() -> String {
    "ed25519".to_string()
}

fn default_kdf() -> String {
    "argon2id".to_string()
}

fn default_log_level() -> String {
    "info".to_string()
}

impl Default for ServerConfig {
    fn default() -> Self {
        Self {
            bind_addr: default_bind_addr(),
            allow_unix_socket: false,
        }
    }
}

impl Default for PathsConfig {
    fn default() -> Self {
        Self {
            vault_path: default_vault_path(),
            audit_path: default_audit_path(),
            master_key_path: default_master_key_path(),
        }
    }
}

impl Default for SecurityConfig {
    fn default() -> Self {
        Self {
            rotation_days: default_rotation_days(),
            grace_days: default_grace_days(),
            require_client_id_header: true,
            deny_network_remote: true,
            rbac_policy_path: default_policy_path(),
        }
    }
}

impl Default for CryptoConfig {
    fn default() -> Self {
        Self {
            aead: default_aead(),
            jwt_sign_algo: default_jwt_algo(),
            kdf: default_kdf(),
        }
    }
}

impl Default for LoggingConfig {
    fn default() -> Self {
        Self {
            level: default_log_level(),
            json: false,
        }
    }
}

impl Default for Config {
    fn default() -> Self {
        Self {
            server: ServerConfig::default(),
            paths: PathsConfig::default(),
            security: SecurityConfig::default(),
            crypto: CryptoConfig::default(),
            logging: LoggingConfig::default(),
        }
    }
}

impl Config {
    /// Load configuration from TOML file
    pub fn load(path: &str) -> Result<Self> {
        if !Path::new(path).exists() {
            tracing::warn!("  Config file not found: {}, using defaults", path);
            return Ok(Config::default());
        }

        let content = fs::read_to_string(path)
            .with_context(|| format!("failed to read config file: {}", path))?;

        let config: Config = toml::from_str(&content)
            .with_context(|| format!("failed to parse config file: {}", path))?;

        Ok(config)
    }

    /// Override config with environment variables
    pub fn with_env_overrides(mut self) -> Self {
        if let Ok(val) = std::env::var("JARVIS_SECRETSD_BIND_ADDR") {
            self.server.bind_addr = val;
        }
        if let Ok(val) = std::env::var("JARVIS_SECRETSD_VAULT_PATH") {
            self.paths.vault_path = val;
        }
        if let Ok(val) = std::env::var("JARVIS_SECRETSD_AUDIT_PATH") {
            self.paths.audit_path = val;
        }
        if let Ok(val) = std::env::var("JARVIS_SECRETSD_MASTER_KEY_PATH") {
            self.paths.master_key_path = val;
        }
        if let Ok(val) = std::env::var("JARVIS_SECRETSD_POLICY_PATH") {
            self.security.rbac_policy_path = val;
        }
        if let Ok(val) = std::env::var("JARVIS_SECRETSD_ROTATION_DAYS") {
            if let Ok(days) = val.parse() {
                self.security.rotation_days = days;
            }
        }
        if let Ok(val) = std::env::var("JARVIS_SECRETSD_LOG_LEVEL") {
            self.logging.level = val;
        }
        if let Ok(val) = std::env::var("JARVIS_SECRETSD_LOG_JSON") {
            self.logging.json = val.to_lowercase() == "true" || val == "1";
        }

        self
    }

    /// Validate configuration
    pub fn validate(&self) -> Result<()> {
        // Validate bind address format
        if !self.server.bind_addr.contains(':') && !self.server.bind_addr.starts_with("unix://") {
            anyhow::bail!("invalid bind_addr format: {}", self.server.bind_addr);
        }

        // Validate rotation and grace days
        if self.security.rotation_days == 0 {
            anyhow::bail!("rotation_days must be > 0");
        }
        if self.security.grace_days > self.security.rotation_days {
            anyhow::bail!("grace_days cannot be > rotation_days");
        }

        // Validate crypto algo
        if self.crypto.aead != "aes-gcm-256" && self.crypto.aead != "chacha20poly1305" {
            anyhow::bail!("unsupported AEAD: {}", self.crypto.aead);
        }

        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_default_config() {
        let config = Config::default();
        assert_eq!(config.server.bind_addr, "127.0.0.1:8081");
        assert_eq!(config.security.rotation_days, 90);
        assert_eq!(config.security.grace_days, 14);
    }

    #[test]
    fn test_config_validation() {
        let config = Config::default();
        assert!(config.validate().is_ok());

        let mut bad_config = Config::default();
        bad_config.security.rotation_days = 0;
        assert!(bad_config.validate().is_err());
    }

    #[test]
    fn test_env_overrides() {
        std::env::set_var("JARVIS_SECRETSD_BIND_ADDR", "127.0.0.1:9999");
        std::env::set_var("JARVIS_SECRETSD_ROTATION_DAYS", "120");

        let config = Config::default().with_env_overrides();

        assert_eq!(config.server.bind_addr, "127.0.0.1:9999");
        assert_eq!(config.security.rotation_days, 120);

        std::env::remove_var("JARVIS_SECRETSD_BIND_ADDR");
        std::env::remove_var("JARVIS_SECRETSD_ROTATION_DAYS");
    }
}
