//! Service de santé pour Jarvis Rust Backend
//! 
//! Monitoring et vérification de l'état de tous les services
//! Centralise les health checks pour l'observabilité

use serde_json::Value;
use std::collections::HashMap;
use std::sync::Arc;
use std::time::Instant;

use crate::{
    config::AppConfig,
    models::{HealthStatus, MemoryUsage, ServiceHealth, ServiceHealthMap, ServiceStatus},
    services::{DatabaseService, LLMService, MemoryService, VoiceService},
};

/// Service de monitoring de santé
#[derive(Clone)]
pub struct HealthService {
    config: Arc<AppConfig>,
    database: Arc<DatabaseService>,
    llm: Arc<LLMService>,
    memory: Arc<MemoryService>,
    voice: Arc<VoiceService>,
    start_time: Instant,
}

impl HealthService {
    /// Initialise le service de santé
    pub async fn new(
        config: &AppConfig,
        database: &Arc<DatabaseService>,
        llm: &Arc<LLMService>,
        memory: &Arc<MemoryService>,
        voice: &Arc<VoiceService>,
    ) -> anyhow::Result<Self> {
        Ok(Self {
            config: Arc::new(config.clone()),
            database: database.clone(),
            llm: llm.clone(),
            memory: memory.clone(),
            voice: voice.clone(),
            start_time: Instant::now(),
        })
    }

    /// Vérifie la santé de tous les services
    pub async fn check_all_services(&self) -> anyhow::Result<HealthStatus> {
        let start_time = Instant::now();
        let mut services = ServiceHealthMap::new();

        // Vérifier chaque service en parallèle
        let (db_health, llm_health, memory_health, voice_health) = tokio::join!(
            self.check_database_health(),
            self.check_llm_health(),
            self.check_memory_health(),
            self.check_voice_health()
        );

        // Ajouter les résultats
        services.insert("database".to_string(), db_health);
        services.insert("llm".to_string(), llm_health);
        services.insert("memory".to_string(), memory_health);
        services.insert("voice".to_string(), voice_health);

        // Déterminer le statut global
        let global_status = self.calculate_global_status(&services);

        // Obtenir l'utilisation mémoire
        let memory_usage = self.get_memory_usage().await;

        let health_status = HealthStatus {
            status: global_status,
            version: env!("CARGO_PKG_VERSION").to_string(),
            uptime_secs: self.start_time.elapsed().as_secs(),
            services,
            memory_usage,
            timestamp: chrono::Utc::now(),
        };

        let check_time = start_time.elapsed().as_millis();
        tracing::debug!("🏥 Health check complet en {}ms", check_time);

        Ok(health_status)
    }

    /// Vérifie la santé de la base de données
    async fn check_database_health(&self) -> ServiceHealth {
        let start = Instant::now();
        
        match self.database.health_check().await {
            Ok(_) => ServiceHealth {
                status: ServiceStatus::Healthy,
                response_time_ms: Some(start.elapsed().as_millis() as u64),
                last_check: chrono::Utc::now(),
                error: None,
            },
            Err(e) => ServiceHealth {
                status: ServiceStatus::Unhealthy,
                response_time_ms: Some(start.elapsed().as_millis() as u64),
                last_check: chrono::Utc::now(),
                error: Some(e.to_string()),
            },
        }
    }

    /// Vérifie la santé du service LLM
    async fn check_llm_health(&self) -> ServiceHealth {
        let start = Instant::now();
        
        match self.llm.health_check().await {
            Ok(health_data) => {
                let status = match health_data.get("status").and_then(|s| s.as_str()) {
                    Some("healthy") => ServiceStatus::Healthy,
                    Some("unhealthy") => ServiceStatus::Unhealthy,
                    _ => ServiceStatus::Degraded,
                };
                
                ServiceHealth {
                    status,
                    response_time_ms: Some(start.elapsed().as_millis() as u64),
                    last_check: chrono::Utc::now(),
                    error: health_data.get("error").and_then(|e| e.as_str()).map(|s| s.to_string()),
                }
            }
            Err(e) => ServiceHealth {
                status: ServiceStatus::Unhealthy,
                response_time_ms: Some(start.elapsed().as_millis() as u64),
                last_check: chrono::Utc::now(),
                error: Some(e.to_string()),
            },
        }
    }

    /// Vérifie la santé du service mémoire
    async fn check_memory_health(&self) -> ServiceHealth {
        let start = Instant::now();
        
        match self.memory.get_memory_stats().await {
            Ok(stats) => {
                let status = match stats.get("status").and_then(|s| s.as_str()) {
                    Some("healthy") => ServiceStatus::Healthy,
                    Some("unhealthy") => ServiceStatus::Unhealthy,
                    _ => ServiceStatus::Degraded,
                };
                
                ServiceHealth {
                    status,
                    response_time_ms: Some(start.elapsed().as_millis() as u64),
                    last_check: chrono::Utc::now(),
                    error: None,
                }
            }
            Err(e) => ServiceHealth {
                status: ServiceStatus::Unhealthy,
                response_time_ms: Some(start.elapsed().as_millis() as u64),
                last_check: chrono::Utc::now(),
                error: Some(e.to_string()),
            },
        }
    }

    /// Vérifie la santé du service vocal
    async fn check_voice_health(&self) -> ServiceHealth {
        let start = Instant::now();
        
        match self.voice.health_check().await {
            Ok(voice_stats) => {
                // Analyser les statuts STT et TTS
                let stt_healthy = voice_stats.get("stt")
                    .and_then(|s| s.get("status"))
                    .and_then(|s| s.as_str()) == Some("healthy");
                    
                let tts_healthy = voice_stats.get("tts")
                    .and_then(|s| s.get("status"))
                    .and_then(|s| s.as_str()) == Some("healthy");

                let status = match (stt_healthy, tts_healthy) {
                    (true, true) => ServiceStatus::Healthy,
                    (true, false) | (false, true) => ServiceStatus::Degraded,
                    (false, false) => ServiceStatus::Unhealthy,
                };

                ServiceHealth {
                    status,
                    response_time_ms: Some(start.elapsed().as_millis() as u64),
                    last_check: chrono::Utc::now(),
                    error: if status == ServiceStatus::Unhealthy { 
                        Some("Services STT et TTS indisponibles".to_string()) 
                    } else { 
                        None 
                    },
                }
            }
            Err(e) => ServiceHealth {
                status: ServiceStatus::Unhealthy,
                response_time_ms: Some(start.elapsed().as_millis() as u64),
                last_check: chrono::Utc::now(),
                error: Some(e.to_string()),
            },
        }
    }

    /// Calcule le statut global basé sur les services individuels
    fn calculate_global_status(&self, services: &ServiceHealthMap) -> ServiceStatus {
        let mut healthy_count = 0;
        let mut degraded_count = 0;
        let mut unhealthy_count = 0;

        for service in services.values() {
            match service.status {
                ServiceStatus::Healthy => healthy_count += 1,
                ServiceStatus::Degraded => degraded_count += 1,
                ServiceStatus::Unhealthy => unhealthy_count += 1,
            }
        }

        let total_services = services.len();

        // Logique de statut global
        if unhealthy_count > 0 {
            if unhealthy_count >= total_services / 2 {
                ServiceStatus::Unhealthy // Plus de la moitié des services sont down
            } else {
                ServiceStatus::Degraded // Quelques services sont down
            }
        } else if degraded_count > 0 {
            ServiceStatus::Degraded // Quelques services sont dégradés
        } else {
            ServiceStatus::Healthy // Tous les services sont healthy
        }
    }

    /// Obtient l'utilisation mémoire du processus
    async fn get_memory_usage(&self) -> MemoryUsage {
        // Pour le moment, utilisation factice
        // TODO: Implémenter la lecture réelle de la mémoire avec sysinfo
        
        #[cfg(target_os = "linux")]
        {
            self.get_linux_memory_usage().await
        }
        
        #[cfg(not(target_os = "linux"))]
        {
            MemoryUsage {
                used_mb: 64,
                total_mb: 2048,
                percentage: 3.1,
            }
        }
    }

    #[cfg(target_os = "linux")]
    async fn get_linux_memory_usage(&self) -> MemoryUsage {
        // Lire /proc/self/status pour obtenir la mémoire utilisée
        match tokio::fs::read_to_string("/proc/self/status").await {
            Ok(content) => {
                let mut vm_rss_kb = 0;
                for line in content.lines() {
                    if line.starts_with("VmRSS:") {
                        if let Some(value_str) = line.split_whitespace().nth(1) {
                            vm_rss_kb = value_str.parse::<u64>().unwrap_or(0);
                            break;
                        }
                    }
                }
                
                let used_mb = vm_rss_kb / 1024;
                let total_mb = 2048; // Approximation, TODO: lire la mémoire totale du système
                let percentage = (used_mb as f32 / total_mb as f32) * 100.0;

                MemoryUsage {
                    used_mb,
                    total_mb,
                    percentage,
                }
            }
            Err(_) => MemoryUsage {
                used_mb: 64,
                total_mb: 2048,
                percentage: 3.1,
            }
        }
    }

    /// Obtient des métriques détaillées du système
    pub async fn get_detailed_metrics(&self) -> anyhow::Result<Value> {
        let health_status = self.check_all_services().await?;
        
        // Métriques additionnelles
        let mut metrics = serde_json::to_value(&health_status)?;
        
        // Ajouter des métriques custom
        metrics["custom_metrics"] = serde_json::json!({
            "rust_version": env!("CARGO_PKG_VERSION"),
            "build_timestamp": env!("VERGEN_BUILD_TIMESTAMP").unwrap_or("unknown"),
            "git_sha": env!("VERGEN_GIT_SHA").unwrap_or("unknown"),
            "uptime_human": self.format_uptime(),
            "config": {
                "environment": if self.config.is_production() { "production" } else { "development" },
                "log_level": "info", // TODO: récupérer le niveau de log actuel
            }
        });

        Ok(metrics)
    }

    /// Formate l'uptime de manière lisible
    fn format_uptime(&self) -> String {
        let uptime_secs = self.start_time.elapsed().as_secs();
        let days = uptime_secs / 86400;
        let hours = (uptime_secs % 86400) / 3600;
        let minutes = (uptime_secs % 3600) / 60;
        let seconds = uptime_secs % 60;

        if days > 0 {
            format!("{}j {}h {}m {}s", days, hours, minutes, seconds)
        } else if hours > 0 {
            format!("{}h {}m {}s", hours, minutes, seconds)
        } else if minutes > 0 {
            format!("{}m {}s", minutes, seconds)
        } else {
            format!("{}s", seconds)
        }
    }

    /// Vérifie si tous les services critiques sont opérationnels
    pub async fn are_critical_services_ready(&self) -> bool {
        let health = self.check_all_services().await.unwrap_or_else(|_| {
            HealthStatus {
                status: ServiceStatus::Unhealthy,
                version: "unknown".to_string(),
                uptime_secs: 0,
                services: HashMap::new(),
                memory_usage: MemoryUsage { used_mb: 0, total_mb: 0, percentage: 0.0 },
                timestamp: chrono::Utc::now(),
            }
        });

        // Services critiques : database et llm
        let critical_services = ["database", "llm"];
        
        for service_name in critical_services.iter() {
            if let Some(service) = health.services.get(*service_name) {
                if service.status == ServiceStatus::Unhealthy {
                    return false;
                }
            } else {
                return false;
            }
        }

        true
    }
}