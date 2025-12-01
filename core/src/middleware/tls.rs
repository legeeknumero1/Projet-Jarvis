// ============================================================================
// TLS/HTTPS Certificate Handling - SECURITY FIX C4 (Encryption in Transit)
// ============================================================================
//
// Ce module gère le chargement et la validation des certificats TLS pour
// l'activation de HTTPS.
//
// Vulnérabilité corrigée:
// - CVSS 9.1 : Pas de TLS/HTTPS (communication en clair, MITM possible)
// - Impact : Interception de données, vol de tokens JWT, eavesdropping
// - Correction : TLS 1.2+ obligatoire, certificats valides, HTTP redirect

use rustls_pemfile as pemfile;
use std::fs;
use std::io::BufReader;
use std::path::Path;
use std::sync::Arc;
use tracing::{info, warn};
use tokio_rustls::rustls;

// ============================================================================
// TLS Configuration
// ============================================================================

pub struct TlsConfig {
    pub cert_path: String,
    pub key_path: String,
    pub enable_https: bool,
}

impl TlsConfig {
    pub fn new(cert_path: String, key_path: String) -> Self {
        Self {
            cert_path,
            key_path,
            enable_https: true,
        }
    }

    pub fn from_env() -> Self {
        let cert_path = std::env::var("TLS_CERT_PATH")
            .unwrap_or_else(|_| "./certs/server.crt".to_string());
        let key_path = std::env::var("TLS_KEY_PATH")
            .unwrap_or_else(|_| "./certs/server.key".to_string());

        Self {
            cert_path,
            key_path,
            enable_https: true,
        }
    }
}

// ============================================================================
// Certificate Loader
// ============================================================================

pub struct CertificateLoader;

impl CertificateLoader {
    /// Load and validate TLS certificate chain from PEM file
    pub fn load_certs(path: &str) -> Result<Vec<rustls::pki_types::CertificateDer<'static>>, String> {
        let cert_file = fs::File::open(path)
            .map_err(|e| format!("Failed to open cert file {}: {}", path, e))?;

        let mut reader = BufReader::new(cert_file);
        let certs: Vec<_> = pemfile::certs(&mut reader)
            .collect::<Result<Vec<_>, _>>()
            .map_err(|e| format!("Failed to parse certificates: {}", e))?;

        if certs.is_empty() {
            return Err("No certificates found in file".to_string());
        }

        info!(" Loaded {} certificate(s) from {}", certs.len(), path);
        Ok(certs)
    }

    /// Load and validate private key from PEM file
    pub fn load_key(path: &str) -> Result<rustls::pki_types::PrivateKeyDer<'static>, String> {
        let key_file = fs::File::open(path)
            .map_err(|e| format!("Failed to open key file {}: {}", path, e))?;

        let mut reader = BufReader::new(key_file);

        // Try PKCS8 private key first (most common)
        for key_result in pemfile::pkcs8_private_keys(&mut reader) {
            match key_result {
                Ok(key) => {
                    info!(" Loaded PKCS8 private key from {}", path);
                    return Ok(rustls::pki_types::PrivateKeyDer::Pkcs8(key));
                }
                Err(e) => {
                    warn!("Failed to parse PKCS8 key: {}", e);
                }
            }
        }

        // Try RSA private key
        let key_file = fs::File::open(path)
            .map_err(|e| format!("Failed to reopen key file: {}", e))?;
        let mut reader = BufReader::new(key_file);

        for key_result in pemfile::rsa_private_keys(&mut reader) {
            match key_result {
                Ok(key) => {
                    info!(" Loaded RSA private key from {}", path);
                    return Ok(rustls::pki_types::PrivateKeyDer::Pkcs1(key));
                }
                Err(e) => {
                    warn!("Failed to parse RSA key: {}", e);
                }
            }
        }

        Err("No private keys found in file".to_string())
    }

    /// Create rustls ServerConfig from certificate and key files
    pub fn create_server_config(cert_path: &str, key_path: &str)
        -> Result<Arc<rustls::ServerConfig>, String>
    {
        let certs = Self::load_certs(cert_path)?;
        let key = Self::load_key(key_path)?;

        let mut config = rustls::ServerConfig::builder()
            .with_no_client_auth()
            .with_single_cert(certs, key)
            .map_err(|e| format!("Failed to create server config: {}", e))?;

        // Configure TLS versions and cipher suites
        config.alpn_protocols = vec![b"h2".to_vec(), b"http/1.1".to_vec()];

        info!(" TLS/HTTPS configured (TLS 1.2+)");
        Ok(Arc::new(config))
    }

    /// Validate certificate file existence and readability
    pub fn validate_certificates(config: &TlsConfig) -> Result<(), String> {
        if !config.enable_https {
            warn!("  HTTPS is disabled - communication will be unencrypted!");
            return Ok(());
        }

        // Check certificate file
        if !Path::new(&config.cert_path).exists() {
            return Err(format!(
                "Certificate file not found: {}. Generate with: openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes",
                config.cert_path
            ));
        }

        // Check key file
        if !Path::new(&config.key_path).exists() {
            return Err(format!(
                "Private key file not found: {}",
                config.key_path
            ));
        }

        // Try to load them
        Self::load_certs(&config.cert_path)?;
        Self::load_key(&config.key_path)?;

        info!(" TLS certificates validated");
        Ok(())
    }
}

// ============================================================================
// Certificate Generation Helper (for development/testing)
// ============================================================================

pub struct CertificateGenerator;

impl CertificateGenerator {
    /// Print certificate generation instructions
    pub fn print_instructions() {
        eprintln!("\n{}", "=".repeat(80));
        eprintln!(" JARVIS TLS/HTTPS - CERTIFICATE SETUP REQUIRED");
        eprintln!("{}\n", "=".repeat(80));

        eprintln!("SELF-SIGNED CERTIFICATE (Development/Testing):");
        eprintln!("  Generate with OpenSSL:");
        eprintln!("  $ mkdir -p certs");
        eprintln!("  $ openssl req -x509 -newkey rsa:4096 -keyout certs/server.key \\");
        eprintln!("    -out certs/server.crt -days 365 -nodes \\");
        eprintln!("    -subj '/CN=localhost'");
        eprintln!();

        eprintln!("PRODUCTION CERTIFICATE (Let's Encrypt/Certbot):");
        eprintln!("  1. Install Certbot:");
        eprintln!("     $ sudo apt-get install certbot");
        eprintln!();
        eprintln!("  2. Generate certificate:");
        eprintln!("     $ sudo certbot certonly --standalone -d yourdomain.com");
        eprintln!();
        eprintln!("  3. Set environment variables:");
        eprintln!("     export TLS_CERT_PATH=/etc/letsencrypt/live/yourdomain.com/fullchain.pem");
        eprintln!("     export TLS_KEY_PATH=/etc/letsencrypt/live/yourdomain.com/privkey.pem");
        eprintln!();

        eprintln!("CERTIFICATE VALIDATION:");
        eprintln!("  $ openssl x509 -in certs/server.crt -text -noout");
        eprintln!();

        eprintln!("{}\n", "=".repeat(80));
    }
}

// ============================================================================
// Tests
// ============================================================================

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_tls_config_creation() {
        let config = TlsConfig::new(
            "certs/server.crt".to_string(),
            "certs/server.key".to_string(),
        );

        assert_eq!(config.cert_path, "certs/server.crt");
        assert_eq!(config.key_path, "certs/server.key");
        assert!(config.enable_https);
    }

    #[test]
    fn test_certificate_validation() {
        let config = TlsConfig::new(
            "nonexistent.crt".to_string(),
            "nonexistent.key".to_string(),
        );

        let result = CertificateLoader::validate_certificates(&config);
        assert!(result.is_err(), "Should fail for nonexistent files");
    }
}
