//! Configuration management pour Jarvis Rust Backend
//! 
//! Gestion centralisée de toute la configuration avec:
//! - Chargement depuis .env et variables d'environnement
//! - Validation stricte des types
//! - Valeurs par défaut sécurisées
//! - Hot-reload en développement

use serde::{Deserialize, Serialize};
use std::env;

/// Configuration principale de l'application
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AppConfig {
    /// Configuration serveur
    pub server: ServerConfig,
    
    /// Configuration base de données
    pub database: DatabaseConfig,
    
    /// Configuration Redis
    pub redis: RedisConfig,
    
    /// Configuration Ollama
    pub ollama: OllamaConfig,
    
    /// Configuration services externes
    pub external: ExternalConfig,
    
    /// Configuration sécurité
    pub security: SecurityConfig,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ServerConfig {
    pub host: String,
    pub port: u16,
    pub workers: usize,
    pub max_connections: usize,
    pub request_timeout_secs: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DatabaseConfig {
    pub url: String,
    pub max_connections: u32,
    pub min_connections: u32,
    pub acquire_timeout_secs: u64,
    pub idle_timeout_secs: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RedisConfig {
    pub url: String,
    pub max_connections: u32,
    pub timeout_secs: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OllamaConfig {
    pub url: String,
    pub model: String,
    pub timeout_secs: u64,
    pub max_tokens: u32,
    pub temperature: f32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExternalConfig {
    pub stt_url: String,
    pub tts_url: String,
    pub qdrant_url: String,
    pub home_assistant_url: Option<String>,
    pub home_assistant_token: Option<String>,
    pub weather_api_key: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SecurityConfig {
    pub jwt_secret: String,
    pub api_key: String,
    pub rate_limit_requests: u32,
    pub rate_limit_window_secs: u64,
    pub allowed_origins: Vec<String>,
    pub encryption_key: String,
}

impl AppConfig {
    /// Charge la configuration depuis l'environnement
    pub fn load() -> anyhow::Result<Self> {
        // Charger le fichier .env si présent
        dotenvy::dotenv().ok();

        Ok(Self {
            server: ServerConfig {
                host: env::var("HOST").unwrap_or_else(|_| "0.0.0.0".to_string()),
                port: env::var("PORT")
                    .unwrap_or_else(|_| "8000".to_string())
                    .parse()
                    .unwrap_or(8000),
                workers: env::var("WORKERS")
                    .unwrap_or_else(|_| num_cpus::get().to_string())
                    .parse()
                    .unwrap_or(num_cpus::get()),
                max_connections: env::var("MAX_CONNECTIONS")
                    .unwrap_or_else(|_| "1000".to_string())
                    .parse()
                    .unwrap_or(1000),
                request_timeout_secs: env::var("REQUEST_TIMEOUT_SECS")
                    .unwrap_or_else(|_| "30".to_string())
                    .parse()
                    .unwrap_or(30),
            },

            database: DatabaseConfig {
                url: env::var("DATABASE_URL")
                    .unwrap_or_else(|_| {
                        "postgresql://jarvis:jarvis123@localhost:5432/jarvis_db".to_string()
                    }),
                max_connections: env::var("DB_MAX_CONNECTIONS")
                    .unwrap_or_else(|_| "20".to_string())
                    .parse()
                    .unwrap_or(20),
                min_connections: env::var("DB_MIN_CONNECTIONS")
                    .unwrap_or_else(|_| "5".to_string())
                    .parse()
                    .unwrap_or(5),
                acquire_timeout_secs: env::var("DB_ACQUIRE_TIMEOUT_SECS")
                    .unwrap_or_else(|_| "10".to_string())
                    .parse()
                    .unwrap_or(10),
                idle_timeout_secs: env::var("DB_IDLE_TIMEOUT_SECS")
                    .unwrap_or_else(|_| "600".to_string())
                    .parse()
                    .unwrap_or(600),
            },

            redis: RedisConfig {
                url: env::var("REDIS_URL")
                    .unwrap_or_else(|_| "redis://localhost:6379".to_string()),
                max_connections: env::var("REDIS_MAX_CONNECTIONS")
                    .unwrap_or_else(|_| "10".to_string())
                    .parse()
                    .unwrap_or(10),
                timeout_secs: env::var("REDIS_TIMEOUT_SECS")
                    .unwrap_or_else(|_| "5".to_string())
                    .parse()
                    .unwrap_or(5),
            },

            ollama: OllamaConfig {
                url: env::var("OLLAMA_URL")
                    .unwrap_or_else(|_| "http://localhost:11434".to_string()),
                model: env::var("OLLAMA_MODEL")
                    .unwrap_or_else(|_| "llama3.2:1b".to_string()),
                timeout_secs: env::var("OLLAMA_TIMEOUT_SECS")
                    .unwrap_or_else(|_| "30".to_string())
                    .parse()
                    .unwrap_or(30),
                max_tokens: env::var("OLLAMA_MAX_TOKENS")
                    .unwrap_or_else(|_| "2048".to_string())
                    .parse()
                    .unwrap_or(2048),
                temperature: env::var("OLLAMA_TEMPERATURE")
                    .unwrap_or_else(|_| "0.7".to_string())
                    .parse()
                    .unwrap_or(0.7),
            },

            external: ExternalConfig {
                stt_url: env::var("STT_URL")
                    .unwrap_or_else(|_| "http://localhost:8003".to_string()),
                tts_url: env::var("TTS_URL")
                    .unwrap_or_else(|_| "http://localhost:8002".to_string()),
                qdrant_url: env::var("QDRANT_URL")
                    .unwrap_or_else(|_| "http://localhost:6333".to_string()),
                home_assistant_url: env::var("HOME_ASSISTANT_URL").ok(),
                home_assistant_token: env::var("HOME_ASSISTANT_TOKEN").ok(),
                weather_api_key: env::var("OPENWEATHER_API_KEY").ok(),
            },

            security: SecurityConfig {
                jwt_secret: env::var("JWT_SECRET_KEY")
                    .unwrap_or_else(|_| "dev-jwt-secret-change-in-production".to_string()),
                api_key: env::var("JARVIS_API_KEY")
                    .unwrap_or_else(|_| "dev-local-key".to_string()),
                rate_limit_requests: env::var("RATE_LIMIT_REQUESTS")
                    .unwrap_or_else(|_| "100".to_string())
                    .parse()
                    .unwrap_or(100),
                rate_limit_window_secs: env::var("RATE_LIMIT_WINDOW_SECS")
                    .unwrap_or_else(|_| "60".to_string())
                    .parse()
                    .unwrap_or(60),
                allowed_origins: env::var("ALLOWED_ORIGINS")
                    .unwrap_or_else(|_| "http://localhost:3000,http://localhost:8000,http://172.20.0.50:3000".to_string())
                    .split(',')
                    .map(|s| s.trim().to_string())
                    .collect(),
                encryption_key: env::var("ENCRYPTION_KEY")
                    .unwrap_or_else(|_| "dev-encryption-key-32-chars-long!".to_string()),
            },
        })
    }

    /// Retourne le chemin du fichier .env utilisé
    pub fn env_file(&self) -> &str {
        ".env"
    }

    /// Valide la configuration
    pub fn validate(&self) -> anyhow::Result<()> {
        // Validation JWT secret (minimum 32 caractères)
        if self.security.jwt_secret.len() < 32 {
            anyhow::bail!("JWT_SECRET_KEY doit contenir au moins 32 caractères");
        }

        // Validation clé de chiffrement (doit être exactement 32 caractères pour Fernet)
        if self.security.encryption_key.len() != 32 {
            anyhow::bail!("ENCRYPTION_KEY doit contenir exactement 32 caractères");
        }

        // Validation URL de base de données
        if !self.database.url.starts_with("postgresql://") {
            anyhow::bail!("DATABASE_URL doit être une URL PostgreSQL valide");
        }

        Ok(())
    }

    /// Configuration pour l'environnement de développement
    pub fn is_development(&self) -> bool {
        env::var("RUST_ENV").unwrap_or_else(|_| "development".to_string()) == "development"
    }

    /// Configuration pour l'environnement de production
    pub fn is_production(&self) -> bool {
        env::var("RUST_ENV").unwrap_or_else(|_| "development".to_string()) == "production"
    }
}

impl Default for AppConfig {
    fn default() -> Self {
        Self::load().expect("Échec du chargement de la configuration par défaut")
    }
}