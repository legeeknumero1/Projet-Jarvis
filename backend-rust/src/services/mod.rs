//! Services Layer pour Jarvis Rust Backend
//! 
//! Couche de services métier avec injection de dépendances
//! Remplace les services Python avec gains de performance

use std::sync::Arc;

use crate::config::AppConfig;

pub mod chat;
pub mod llm;
pub mod memory;
pub mod voice;
pub mod health;
pub mod database;

pub use chat::ChatService;
pub use llm::LLMService;
pub use memory::MemoryService;
pub use voice::VoiceService;
pub use health::HealthService;
pub use database::DatabaseService;

/// Container de tous les services de l'application
#[derive(Clone)]
pub struct AppServices {
    pub chat: Arc<ChatService>,
    pub llm: Arc<LLMService>,
    pub memory: Arc<MemoryService>,
    pub voice: Arc<VoiceService>,
    pub health: Arc<HealthService>,
    pub database: Arc<DatabaseService>,
}

impl AppServices {
    /// Initialise tous les services avec injection de dépendances
    pub async fn new(config: &AppConfig) -> anyhow::Result<Self> {
        tracing::info!("🔧 Initialisation des services...");

        // Service base de données (doit être initialisé en premier)
        let database = Arc::new(DatabaseService::new(config).await?);
        tracing::info!("✅ DatabaseService initialisé");

        // Service mémoire (dépend de database)
        let memory = Arc::new(MemoryService::new(config, &database).await?);
        tracing::info!("✅ MemoryService initialisé");

        // Service LLM
        let llm = Arc::new(LLMService::new(config).await?);
        tracing::info!("✅ LLMService initialisé");

        // Service vocal
        let voice = Arc::new(VoiceService::new(config).await?);
        tracing::info!("✅ VoiceService initialisé");

        // Service chat (dépend de llm, memory, voice)
        let chat = Arc::new(ChatService::new(
            config,
            &llm,
            &memory,
            &voice,
        ).await?);
        tracing::info!("✅ ChatService initialisé");

        // Service de santé (dépend de tous les autres)
        let health = Arc::new(HealthService::new(
            config,
            &database,
            &llm,
            &memory,
            &voice,
        ).await?);
        tracing::info!("✅ HealthService initialisé");

        tracing::info!("🚀 Tous les services initialisés avec succès");

        Ok(Self {
            chat,
            llm,
            memory,
            voice,
            health,
            database,
        })
    }
}