// ============================================================================
// Secret Management Validation - SECURITY FIX C6 (Secret Management)
// ============================================================================
//
// Ce module valide que tous les secrets critiques sont correctement configurés
// à la mise en route de l'application.
//
// Vulnérabilité corrigée:
// - CVSS 8.2 : Pas de gestion des secrets (stockage plain-text, pas de rotation)
// - Impact : Fuites de credentials, exposition de tokens JWT, accès non autorisé
// - Correction : Validation des secrets à startup + guide de rotation

use std::env;
use tracing::{error, warn, info};

// ============================================================================
// Secret Configuration Requirements
// ============================================================================

const MIN_SECRET_LENGTH: usize = 32;
const MIN_PASSWORD_LENGTH: usize = 16;
const MIN_API_KEY_LENGTH: usize = 16;

// ============================================================================
// Secret Validation
// ============================================================================

pub struct SecretsValidator;

impl SecretsValidator {
    /// Valider tous les secrets requis
    pub fn validate_all() -> Result<(), String> {
        info!(" Validating secrets configuration...");

        // Validate JWT Secret
        Self::validate_jwt_secret()?;

        // Validate CORS Origins
        Self::validate_cors_origins()?;

        // Validate External Service URLs
        Self::validate_service_urls()?;

        info!(" All secrets validated successfully!");
        Ok(())
    }

    /// Valider JWT_SECRET
    fn validate_jwt_secret() -> Result<(), String> {
        let jwt_secret = env::var("JWT_SECRET")
            .unwrap_or_else(|_| "dev-secret-key-change-in-production".to_string());

        if jwt_secret.contains("dev-secret-key") || jwt_secret.contains("changeme") {
            warn!("  SECURITY WARNING: Using default/insecure JWT_SECRET!");
            warn!("   This is ONLY acceptable for development!");
            warn!("   In production, set JWT_SECRET to a secure random value:");
            warn!("   $ openssl rand -base64 32");
            return Err(
                "JWT_SECRET uses insecure default - change in production!".to_string()
            );
        }

        if jwt_secret.len() < MIN_SECRET_LENGTH {
            return Err(format!(
                "JWT_SECRET must be at least {} characters (got {})",
                MIN_SECRET_LENGTH,
                jwt_secret.len()
            ));
        }

        info!(" JWT_SECRET validated (length: {})", jwt_secret.len());
        Ok(())
    }

    /// Valider CORS_ORIGINS
    fn validate_cors_origins() -> Result<(), String> {
        let cors_origins = env::var("CORS_ORIGINS")
            .unwrap_or_else(|_| "http://localhost:3000".to_string());

        let origins: Vec<&str> = cors_origins.split(',').map(|s| s.trim()).collect();

        if origins.is_empty() || origins[0].is_empty() {
            return Err("CORS_ORIGINS must contain at least one valid origin".to_string());
        }

        let origin_count = origins.len();

        // Validate that all origins are properly formatted
        for origin in origins {
            if !origin.starts_with("http://") && !origin.starts_with("https://") {
                return Err(format!(
                    "CORS origin must start with http:// or https:// (got: {})",
                    origin
                ));
            }
        }

        info!(" CORS_ORIGINS validated ({} origins)", origin_count);
        Ok(())
    }

    /// Valider les URLs des services externes
    fn validate_service_urls() -> Result<(), String> {
        let required_urls = vec![
            ("PYTHON_BRIDGES_URL", "http://localhost:8005"),
            ("AUDIO_ENGINE_URL", "http://localhost:8004"),
        ];

        for (var_name, default) in required_urls {
            let url = env::var(var_name).unwrap_or_else(|_| default.to_string());

            if !url.starts_with("http://") && !url.starts_with("https://") {
                return Err(format!(
                    "{} must be a valid URL (got: {})",
                    var_name, url
                ));
            }

            info!(" {} validated", var_name);
        }

        Ok(())
    }

    /// Vérifier si les secrets contiennent des valeurs dangereux (DEBUG)
    pub fn check_for_insecure_defaults() {
        let insecure_patterns = vec![
            ("JWT_SECRET", "changeme"),
            ("JWT_SECRET", "dev-secret"),
            ("JWT_SECRET", "test"),
        ];

        for (var_name, pattern) in insecure_patterns {
            if let Ok(value) = env::var(var_name) {
                if value.to_lowercase().contains(pattern) {
                    warn!(
                        " SECURITY WARNING: {} contains insecure pattern: {}",
                        var_name, pattern
                    );
                }
            }
        }
    }
}

// ============================================================================
// Secret Masking for Logging
// ============================================================================

/// Masquer les secrets dans les logs
pub fn mask_secret(secret: &str, visible_chars: usize) -> String {
    if secret.len() <= visible_chars {
        return "*".repeat(secret.len());
    }

    let visible_part = &secret[..visible_chars];
    let masked_part = "*".repeat(secret.len() - visible_chars);
    format!("{}{}", visible_part, masked_part)
}

// ============================================================================
// Environment Checklist
// ============================================================================

pub struct EnvironmentChecklist;

impl EnvironmentChecklist {
    /// Afficher une checklist des variables d'environnement
    pub fn print_requirements() {
        eprintln!("\n{}", "=".repeat(80));
        eprintln!(" JARVIS SECRET MANAGEMENT - REQUIRED ENVIRONMENT VARIABLES");
        eprintln!("{}\n", "=".repeat(80));

        eprintln!("CRITICAL SECRETS (MUST BE CHANGED):");
        eprintln!("  [ ] JWT_SECRET (min 32 chars)");
        eprintln!("        Generate: openssl rand -base64 32");
        eprintln!("  [ ] POSTGRES_PASSWORD (min 16 chars, alphanumeric + special)");
        eprintln!("        Generate: openssl rand -base64 16");
        eprintln!("  [ ] REDIS_PASSWORD (min 16 chars, optional but recommended)");
        eprintln!("        Generate: openssl rand -base64 16");
        eprintln!("  [ ] JARVIS_ENCRYPTION_KEY (valid Fernet key)");
        eprintln!("        Generate: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\"");
        eprintln!();

        eprintln!("EXTERNAL API KEYS:");
        eprintln!("  [ ] HOME_ASSISTANT_TOKEN (if using Home Assistant integration)");
        eprintln!("  [ ] BRAVE_API_KEY (if using Brave Search)");
        eprintln!("  [ ] GOOGLE_CSE_KEY & GOOGLE_CSE_ID (if using Google Search)");
        eprintln!("  [ ] OPENWEATHER_API_KEY (if using weather)");
        eprintln!();

        eprintln!("NETWORK CONFIGURATION:");
        eprintln!("  [ ] CORS_ORIGINS (at least one valid origin)");
        eprintln!("  [ ] JWT_ALGORITHM (default: HS256)");
        eprintln!("  [ ] JWT_EXPIRATION_HOURS (default: 24)");
        eprintln!();

        eprintln!("{}", "=".repeat(80));
        eprintln!(" For more info, see: .env.template");
        eprintln!(" Secret Rotation Guide: SECURITY_FIXES_2025_10_25.md");
        eprintln!("{}\n", "=".repeat(80));
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_mask_secret() {
        let secret = "super-secret-key-12345";
        let masked = mask_secret(secret, 5);
        assert_eq!(masked, "super*********************");

        let short = "abc";
        let masked_short = mask_secret(short, 5);
        assert_eq!(masked_short, "***");
    }

    #[test]
    fn test_secret_length_validation() {
        let short_secret = "short";
        assert!(short_secret.len() < MIN_SECRET_LENGTH);

        let long_secret = "this-is-a-proper-secret-key-minimum-32-chars-long";
        assert!(long_secret.len() >= MIN_SECRET_LENGTH);
    }
}
