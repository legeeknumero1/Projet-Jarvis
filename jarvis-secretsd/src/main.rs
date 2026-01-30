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
use tracing::{info, error};
use tracing_subscriber::{fmt, prelude::*, EnvFilter};
use rustls::pki_types::{CertificateDer, PrivateKeyDer};

#[tokio::main]
async fn main() -> Result<()> {
    // Audit Version Marker
    println!("--- JARVIS SECRETSD AUDIT MODE ACTIVE ---");
    
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

    // 7. Start server with mTLS
    let bind_addr = config.server.bind_addr.parse::<std::net::SocketAddr>()
        .with_context(|| format!("failed to parse bind address: {}", config.server.bind_addr))?;
    
    info!(" Starting mTLS server on {}", bind_addr);

    // Load TLS certificates
    let cert_path = "/etc/jarvis/certs/pki/issued/secretsd.crt";
    let key_path = "/etc/jarvis/certs/pki/private/secretsd.key";
    let ca_path = "/etc/jarvis/certs/pki/ca/ca.crt";

    if Path::new(cert_path).exists() && Path::new(key_path).exists() && Path::new(ca_path).exists() {
        info!(" TLS certificates found, enabling mTLS enforcement");
        
        // Custom acceptor to require client certificates
        let rustls_config = rustls::ServerConfig::builder()
            .with_client_cert_verifier(
                rustls::server::WebPkiClientVerifier::builder(
                    Arc::new(load_ca_cert(ca_path)?)
                ).build()?
            )
            .with_single_cert(
                load_certs(cert_path)?,
                load_private_key(key_path)?
            )?;
        
        let mut rustls_config = rustls_config;
        rustls_config.alpn_protocols = vec![b"h2".to_vec(), b"http/1.1".to_vec()];

        axum_server::from_tcp_rustls(std::net::TcpListener::bind(bind_addr)?, axum_server::tls_rustls::RustlsConfig::from_config(Arc::new(rustls_config)))
            .serve(app.into_make_service())
            .await
            .context("mTLS server error")?;
    } else {
        info!(" TLS certificates missing, falling back to insecure HTTP");
        let listener = tokio::net::TcpListener::bind(&bind_addr).await?;
        axum::serve(listener, app).await.context("insecure server error")?;
    }

    Ok(())
}

fn load_certs(path: &str) -> Result<Vec<CertificateDer<'static>>> {
    let file = fs::File::open(path)?;
    let mut reader = std::io::BufReader::new(file);
    let certs = rustls_pemfile::certs(&mut reader)
        .collect::<Result<Vec<_>, _>>()?;
    Ok(certs)
}

fn load_private_key(path: &str) -> Result<PrivateKeyDer<'static>> {
    let file = fs::File::open(path)?;
    let mut reader = std::io::BufReader::new(file);
    let key = rustls_pemfile::private_key(&mut reader)?
        .ok_or_else(|| anyhow::anyhow!("no private key found"))?;
    Ok(key)
}

fn load_ca_cert(path: &str) -> Result<rustls::RootCertStore> {
    let file = fs::File::open(path)?;
    let mut reader = std::io::BufReader::new(file);
    let mut root_store = rustls::RootCertStore::empty();
    for cert in rustls_pemfile::certs(&mut reader) {
        root_store.add(cert?)?;
    }
    Ok(root_store)
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
