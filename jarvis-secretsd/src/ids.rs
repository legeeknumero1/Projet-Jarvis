use std::collections::HashMap;
use std::sync::Arc;
use parking_lot::RwLock;
use chrono::{DateTime, Utc, Duration};
use tracing::{error, warn};

#[derive(Debug, Clone)]
pub struct SuspiciousEvent {
    pub client_id: String,
    pub reason: String,
    pub timestamp: DateTime<Utc>,
    pub severity: u8, // 1: Low, 2: Medium, 3: Critical (Intrusion)
}

pub struct IntrusionDetector {
    // Scores de suspicion par Client ID (ou IP si on l'ajoutait)
    scores: Arc<RwLock<HashMap<String, u32>>>,
    // Liste des clients bannis temporairement
    banned: Arc<RwLock<HashMap<String, DateTime<Utc>>>>,
    // Secret "Canari" : si accédé, alerte critique immédiate
    canary_secrets: Vec<String>,
}

impl IntrusionDetector {
    pub fn new() -> Self {
        Self {
            scores: Arc::new(RwLock::new(HashMap::new())),
            banned: Arc::new(RwLock::new(HashMap::new())),
            canary_secrets: vec!["root_master_password".to_string(), "admin_backdoor".to_string()],
        }
    }

    pub fn report_failure(&self, client_id: &str, reason: &str) {
        let mut scores = self.scores.write();
        let entry = scores.entry(client_id.to_string()).or_insert(0);
        *entry += 1;

        warn!("[IDS] Suspicious activity from {}: {} (Score: {})", client_id, reason, *entry);

        if *entry >= 5 {
            let mut banned = self.banned.write();
            let expiry = Utc::now() + Duration::minutes(15);
            banned.insert(client_id.to_string(), expiry);
            error!("[IDS] Banning client {} until {}", client_id, expiry);
        }
    }

    pub fn is_banned(&self, client_id: &str) -> bool {
        let banned = self.banned.read();
        if let Some(expiry) = banned.get(client_id) {
            if Utc::now() < *expiry {
                return true;
            }
        }
        false
    }

    pub fn check_canary(&self, secret_name: &str, client_id: &str) -> bool {
        if self.canary_secrets.contains(&secret_name.to_string()) {
            error!("[IDS] INTRUSION DETECTED! Client {} accessed CANARY SECRET {}", client_id, secret_name);
            self.report_failure(client_id, "canary_access");
            return true;
        }
        false
    }
}
