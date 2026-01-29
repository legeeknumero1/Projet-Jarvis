mod api;
mod audit;
mod config;
mod crypto;
mod ids;
mod policy;
mod rotation;
mod storage;
mod types;

use crate::api::{router, AppState};
use crate::audit::AuditLog;
use crate::config::Config;
use crate::crypto::gen_bytes_32;
use crate::ids::IntrusionDetector;
use crate::policy::Policy;
use crate::storage::VaultStore;
use anyhow::{Context, Result};
use std::fs;
use std::path::Path;
use std::sync::Arc;
use std::time::Instant;
use tracing::info;
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

    info!(" Starting jarvis-secretsd v{}", env!("CARGO_PKG_VERSION"));
    info!(" Config loaded from: {}", config_path);

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

    info!(" Vault loaded: {}", config.paths.vault_path);

    // 3. Load policy
    let policy = Policy::load(&config.security.rbac_policy_path)?;
    let policy = Arc::new(policy);

    // 4. Initialize audit log
    let audit = AuditLog::init(&config.paths.audit_path)?;
    let audit = Arc::new(audit);

    // 5. Initialize Intrusion Detection System
    let ids = Arc::new(IntrusionDetector::new());

    // 6. Start rotation scheduler
    let store_clone = store.clone();
    tokio::spawn(async move {
        rotation::start_rotation_scheduler(store_clone).await;
    });

    // 7. Build Axum app
    let app_state = AppState {
        store,
        policy,
        ids,
        audit: audit.clone(),
        start_time: Instant::now(),
    };

    let app = router(app_state);

    // 7. Start server
    let bind_addr = config.server.bind_addr.clone();
    info!(" Starting server on {}", bind_addr);

    let listener = tokio::net::TcpListener::bind(&bind_addr)
        .await
        .with_context(|| format!("failed to bind to {}", bind_addr))?;

    info!(" Server started successfully");
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

use hkdf::Hkdf;
use sha2::Sha256;

/// Ensure master key exists, generate if missing, and bind it to the host machine-id via HKDF
fn ensure_master_key(path: &str) -> Result<[u8; 32]> {
    let path_obj = Path::new(path);
    
    // 1. Get host hardware signature
    let machine_id = fs::read_to_string("/etc/machine-id")
        .unwrap_or_else(|_| "generic-jarvis-host-id-fallback".to_string());
    let host_salt = machine_id.trim();

    if path_obj.exists() {
        info!(" Loading existing master key from {} (HKDF Bound to host)", path);

        let bytes = fs::read(path)
            .with_context(|| format!("failed to read master key: {}", path))?;

        if bytes.len() != 32 {
            anyhow::bail!("invalid master key length");
        }

        // Use HKDF to derive the final key from raw key + host salt
        let hk = Hkdf::<Sha256>::new(Some(host_salt.as_bytes()), &bytes);
        let mut final_key = [0u8; 32];
        hk.expand(b"jarvis-secretsd-host-binding", &mut final_key)
            .map_err(|_| anyhow::anyhow!("HKDF expansion failed"))?;

        Ok(final_key)
    } else {
        info!(" Generating new master key bound to this hardware via HKDF");

        if let Some(parent) = path_obj.parent() {
            fs::create_dir_all(parent)?;
        }

        let raw_key = gen_bytes_32();
        
        // Write raw key (worthless without HKDF + machine-id)
        fs::write(path, &*raw_key)
            .with_context(|| format!("failed to write master key: {}", path))?;

        #[cfg(unix)]
        {
            use std::os::unix::fs::PermissionsExt;
            let mut perms = fs::metadata(path)?.permissions();
            perms.set_mode(0o600);
            fs::set_permissions(path, perms)?;
        }

        let hk = Hkdf::<Sha256>::new(Some(host_salt.as_bytes()), &*raw_key);
        let mut final_key = [0u8; 32];
        hk.expand(b"jarvis-secretsd-host-binding", &mut final_key)
            .map_err(|_| anyhow::anyhow!("HKDF expansion failed"))?;

        info!(" Hardware-bound master key (HKDF) initialized");
        Ok(final_key)
    }
}
