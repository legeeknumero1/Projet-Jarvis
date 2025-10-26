mod api;
mod audit;
mod config;
mod crypto;
mod policy;
mod rotation;
mod storage;
mod types;

use crate::api::{router, AppState};
use crate::audit::AuditLog;
use crate::config::Config;
use crate::crypto::gen_bytes_32;
use crate::policy::Policy;
use crate::storage::VaultStore;
use anyhow::{Context, Result};
use std::fs;
use std::path::Path;
use std::sync::Arc;
use std::time::Instant;
use tracing::{error, info, warn};
use tracing_subscriber::{fmt, prelude::*, EnvFilter};

#[tokio::main]
async fn main() -> Result<()> {
    // Parse CLI args
    let args: Vec<String> = std::env::args().collect();
    let config_path = if args.len() > 2 && args[1] == "--config" {
        &args[2]
    } else {
        "/etc/jarvis-secretsd/config.toml"
    };

    // Load config
    let config = Config::load(config_path)
        .with_context(|| format!("failed to load config from {}", config_path))?
        .with_env_overrides();

    config.validate()?;

    // Initialize logging
    init_logging(&config)?;

    info!("🚀 Starting jarvis-secretsd v{}", env!("CARGO_PKG_VERSION"));
    info!("📁 Config loaded from: {}", config_path);

    // 1. Ensure master key exists or generate
    let master = ensure_master_key(&config.paths.master_key_path)?;

    // 2. Load/init vault
    let store = VaultStore::load_or_init(
        &config.paths.vault_path,
        master,
        config.security.rotation_days,
        config.security.grace_days,
    )?;
    let store = Arc::new(store);

    info!("✅ Vault loaded: {}", config.paths.vault_path);

    // 3. Load policy
    let policy = Policy::load(&config.security.rbac_policy_path)?;
    let policy = Arc::new(policy);

    // 4. Initialize audit log
    let audit = AuditLog::init(&config.paths.audit_path)?;
    let audit = Arc::new(audit);

    // 5. Start rotation scheduler
    let store_clone = store.clone();
    tokio::spawn(async move {
        rotation::start_rotation_scheduler(store_clone).await;
    });

    // 6. Build Axum app
    let app_state = AppState {
        store,
        policy,
        audit: audit.clone(),
        start_time: Instant::now(),
    };

    let app = router(app_state);

    // 7. Start server
    let bind_addr = config.server.bind_addr.clone();
    info!("🌐 Starting server on {}", bind_addr);

    let listener = tokio::net::TcpListener::bind(&bind_addr)
        .await
        .with_context(|| format!("failed to bind to {}", bind_addr))?;

    info!("✅ Server started successfully");
    audit.log_success("server_start", None, None);

    axum::serve(listener, app)
        .await
        .context("server error")?;

    Ok(())
}

/// Initialize logging (tracing)
fn init_logging(config: &Config) -> Result<()> {
    let filter = EnvFilter::try_from_default_env()
        .or_else(|_| EnvFilter::try_new(&config.logging.level))?;

    if config.logging.json {
        tracing_subscriber::registry()
            .with(filter)
            .with(fmt::layer().json())
            .init();
    } else {
        tracing_subscriber::registry()
            .with(filter)
            .with(fmt::layer())
            .init();
    }

    Ok(())
}

/// Ensure master key exists, generate if missing
fn ensure_master_key(path: &str) -> Result<[u8; 32]> {
    let path_obj = Path::new(path);

    if path_obj.exists() {
        info!("🔑 Loading existing master key from {}", path);

        let bytes = fs::read(path)
            .with_context(|| format!("failed to read master key: {}", path))?;

        if bytes.len() != 32 {
            anyhow::bail!("invalid master key length: expected 32, got {}", bytes.len());
        }

        let mut key = [0u8; 32];
        key.copy_from_slice(&bytes);

        Ok(key)
    } else {
        info!("🆕 Generating new master key at {}", path);

        // Ensure directory exists
        if let Some(parent) = path_obj.parent() {
            fs::create_dir_all(parent)
                .context("failed to create master key directory")?;
        }

        let key = gen_bytes_32();

        fs::write(path, &key)
            .with_context(|| format!("failed to write master key: {}", path))?;

        // Set permissions 600
        #[cfg(unix)]
        {
            use std::os::unix::fs::PermissionsExt;
            let mut perms = fs::metadata(path)?.permissions();
            perms.set_mode(0o600);
            fs::set_permissions(path, perms)?;
        }

        info!("✅ Generated new master key (32 bytes)");

        Ok(key)
    }
}
