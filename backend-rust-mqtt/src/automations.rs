/// Automation Engine - Règles et décisions pour domotique
use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};
use std::collections::HashMap;
use tracing::{info, debug};

use crate::error::MqttResult;

/// Définition d'une automation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Automation {
    pub id: String,
    pub name: String,
    pub description: Option<String>,
    pub enabled: bool,
    pub triggers: Vec<Trigger>,
    pub conditions: Vec<Condition>,
    pub actions: Vec<Action>,
    pub created_at: DateTime<Utc>,
}

/// Trigger pour une automation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum Trigger {
    TimeOfDay { hour: u8, minute: u8 },
    StateChange { entity_id: String, from: String, to: String },
    MotionDetected { entity_id: String },
    DoorOpened { entity_id: String },
    Webhook { webhook_id: String },
    Template { condition: String },
}

/// Condition pour valider une automation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum Condition {
    TimeRange { start: String, end: String },
    StateEquals { entity_id: String, state: String },
    TemperatureAbove { sensor_id: String, threshold: f32 },
    TemperatureBelow { sensor_id: String, threshold: f32 },
    BrightnessAbove { sensor_id: String, threshold: u8 },
    DayOfWeek { days: Vec<String> },
}

/// Action à exécuter
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum Action {
    TurnOnLight { entity_id: String, brightness: Option<u8> },
    TurnOffLight { entity_id: String },
    SetTemperature { entity_id: String, temperature: f32 },
    SendNotification { title: String, message: String },
    PublishMqtt { topic: String, payload: String },
    CallService { domain: String, service: String },
    Delay { seconds: u32 },
}

/// Engine automation pour gérer les règles
pub struct AutomationEngine {
    automations: std::sync::Arc<tokio::sync::Mutex<HashMap<String, Automation>>>,
}

impl AutomationEngine {
    /// Créer nouveau engine
    pub fn new() -> Self {
        info!("⚙️ Automation Engine initialized");

        Self {
            automations: std::sync::Arc::new(tokio::sync::Mutex::new(HashMap::new())),
        }
    }

    /// Ajouter une automation
    pub async fn add_automation(&self, automation: Automation) -> MqttResult<()> {
        debug!("Adding automation: {}", automation.name);

        let mut automations = self.automations.lock().await;
        automations.insert(automation.id.clone(), automation.clone());

        info!("✅ Automation added: {}", automation.name);
        Ok(())
    }

    /// Récupérer une automation
    pub async fn get_automation(&self, id: &str) -> MqttResult<Option<Automation>> {
        let automations = self.automations.lock().await;
        Ok(automations.get(id).cloned())
    }

    /// Lister toutes les automations
    pub async fn list_automations(&self) -> MqttResult<Vec<Automation>> {
        let automations = self.automations.lock().await;
        Ok(automations.values().cloned().collect())
    }

    /// Supprimer une automation
    pub async fn delete_automation(&self, id: &str) -> MqttResult<()> {
        let mut automations = self.automations.lock().await;
        automations.remove(id);

        info!("✅ Automation deleted: {}", id);
        Ok(())
    }

    /// Évaluer si une condition est vraie
    pub fn evaluate_condition(&self, condition: &Condition, states: &HashMap<String, String>) -> bool {
        match condition {
            Condition::StateEquals { entity_id, state } => {
                states.get(entity_id).map_or(false, |s| s == state)
            }
            Condition::TimeRange { start, end } => {
                let now = chrono::Local::now();
                let now_str = now.format("%H:%M").to_string();
                &now_str >= start && &now_str <= end
            }
            _ => true,  // Conditions complexes implémentées plus tard
        }
    }

    /// Évaluer si un trigger s'est activé
    pub fn evaluate_trigger(&self, trigger: &Trigger, event: &TriggerEvent) -> bool {
        match (trigger, event) {
            (
                Trigger::StateChange { entity_id, from, to },
                TriggerEvent::StateChanged { entity, old_state, new_state },
            ) => {
                entity == entity_id && old_state == from && new_state == to
            }
            (
                Trigger::TimeOfDay { hour, minute },
                TriggerEvent::Time { h, m },
            ) => {
                h == *hour && m == *minute
            }
            _ => false,
        }
    }
}

/// Événement qui peut déclencher une automation
#[derive(Debug, Clone)]
pub enum TriggerEvent {
    StateChanged { entity: String, old_state: String, new_state: String },
    Time { h: u8, m: u8 },
    MotionDetected { entity: String },
    DoorOpened { entity: String },
}

/// Exemples d'automations pré-configurées
impl Automation {
    /// Automation: Allumer lumière au coucher du soleil
    pub fn sunset_lights() -> Self {
        Self {
            id: "sunset_lights".to_string(),
            name: "Sunset Lights".to_string(),
            description: Some("Allume les lumières au coucher du soleil".to_string()),
            enabled: true,
            triggers: vec![
                Trigger::TimeOfDay { hour: 18, minute: 30 },
            ],
            conditions: vec![
                Condition::DayOfWeek {
                    days: vec!["Mon".to_string(), "Tue".to_string(), "Wed".to_string(),
                               "Thu".to_string(), "Fri".to_string(), "Sat".to_string(), "Sun".to_string()],
                },
            ],
            actions: vec![
                Action::TurnOnLight {
                    entity_id: "light.salon".to_string(),
                    brightness: Some(200),
                },
                Action::TurnOnLight {
                    entity_id: "light.bedroom".to_string(),
                    brightness: Some(150),
                },
            ],
            created_at: Utc::now(),
        }
    }

    /// Automation: Mode nuit à 23h
    pub fn night_mode() -> Self {
        Self {
            id: "night_mode".to_string(),
            name: "Night Mode".to_string(),
            description: Some("Mode nuit avec diminution chauffage".to_string()),
            enabled: true,
            triggers: vec![
                Trigger::TimeOfDay { hour: 23, minute: 0 },
            ],
            conditions: vec![],
            actions: vec![
                Action::TurnOffLight {
                    entity_id: "light.salon".to_string(),
                },
                Action::SetTemperature {
                    entity_id: "climate.thermostat".to_string(),
                    temperature: 18.0,
                },
                Action::SendNotification {
                    title: "Jarvis".to_string(),
                    message: "Mode nuit activé".to_string(),
                },
            ],
            created_at: Utc::now(),
        }
    }

    /// Automation: Alarme motion détectée
    pub fn motion_alarm() -> Self {
        Self {
            id: "motion_alarm".to_string(),
            name: "Motion Alarm".to_string(),
            description: Some("Alerte si motion détectée la nuit".to_string()),
            enabled: true,
            triggers: vec![
                Trigger::MotionDetected {
                    entity_id: "binary_sensor.motion_kitchen".to_string(),
                },
            ],
            conditions: vec![
                Condition::TimeRange {
                    start: "22:00".to_string(),
                    end: "06:00".to_string(),
                },
            ],
            actions: vec![
                Action::TurnOnLight {
                    entity_id: "light.kitchen".to_string(),
                    brightness: Some(255),
                },
                Action::SendNotification {
                    title: "Alerte".to_string(),
                    message: "Mouvement détecté en cuisine".to_string(),
                },
            ],
            created_at: Utc::now(),
        }
    }
}

impl Default for Automation {
    fn default() -> Self {
        Self {
            id: uuid::Uuid::new_v4().to_string(),
            name: "New Automation".to_string(),
            description: None,
            enabled: true,
            triggers: vec![],
            conditions: vec![],
            actions: vec![],
            created_at: Utc::now(),
        }
    }
}
