use tokio::sync::broadcast;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::Arc;
use parking_lot::RwLock;
use tracing::{info, warn, error};

/// Event types for the internal event bus
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type")]
pub enum JarvisEvent {
    /// MQTT message received
    MqttMessage {
        topic: String,
        payload: String,
        qos: u8,
    },
    /// Home Assistant state change
    HomeAssistantStateChange {
        entity_id: String,
        old_state: String,
        new_state: String,
    },
    /// Automation triggered
    AutomationTriggered {
        automation_id: String,
        trigger: String,
    },
    /// Plugin event
    PluginEvent {
        plugin_id: String,
        event_data: String,
    },
    /// System event
    SystemEvent {
        event_type: String,
        data: String,
    },
}

/// Event bus for pub/sub pattern
/// Allows MQTT → Internal Event Stream routing
pub struct EventBus {
    /// Broadcast channel for events
    sender: broadcast::Sender<JarvisEvent>,
    /// Event listeners by topic pattern
    listeners: Arc<RwLock<HashMap<String, Vec<String>>>>,
}

impl EventBus {
    /// Create new event bus with capacity
    pub fn new(capacity: usize) -> Self {
        let (sender, _) = broadcast::channel(capacity);
        Self {
            sender,
            listeners: Arc::new(RwLock::new(HashMap::new())),
        }
    }

    /// Publish event to all subscribers
    pub fn publish(&self, event: JarvisEvent) -> Result<(), String> {
        let topic = match &event {
            JarvisEvent::MqttMessage { topic, .. } => topic.clone(),
            JarvisEvent::HomeAssistantStateChange { entity_id, .. } => {
                format!("ha/{}", entity_id)
            }
            JarvisEvent::AutomationTriggered { automation_id, .. } => {
                format!("automation/{}", automation_id)
            }
            JarvisEvent::PluginEvent { plugin_id, .. } => {
                format!("plugin/{}", plugin_id)
            }
            JarvisEvent::SystemEvent { event_type, .. } => {
                format!("system/{}", event_type)
            }
        };

        info!("Publishing event to topic: {}", topic);

        match self.sender.send(event) {
            Ok(receiver_count) => {
                info!("Event delivered to {} subscribers", receiver_count);
                Ok(())
            }
            Err(_) => {
                warn!("No active subscribers for event");
                Ok(())
            }
        }
    }

    /// Subscribe to events
    pub fn subscribe(&self) -> broadcast::Receiver<JarvisEvent> {
        self.sender.subscribe()
    }

    /// Register a listener for a specific topic pattern
    pub fn register_listener(&self, pattern: String, listener_id: String) {
        let mut listeners = self.listeners.write();
        listeners
            .entry(pattern.clone())
            .or_insert_with(Vec::new)
            .push(listener_id.clone());
        info!("Registered listener {} for pattern {}", listener_id, pattern);
    }

    /// Unregister a listener
    pub fn unregister_listener(&self, pattern: &str, listener_id: &str) {
        let mut listeners = self.listeners.write();
        if let Some(listener_list) = listeners.get_mut(pattern) {
            listener_list.retain(|id| id != listener_id);
            info!("Unregistered listener {} from pattern {}", listener_id, pattern);
        }
    }

    /// Get number of active subscribers
    pub fn subscriber_count(&self) -> usize {
        self.sender.receiver_count()
    }

    /// Convert MQTT topic to event bus topic
    pub fn mqtt_to_event_topic(mqtt_topic: &str) -> String {
        format!("mqtt/{}", mqtt_topic)
    }
}

/// Event handler trait for plugins and automations
#[async_trait::async_trait]
pub trait EventHandler: Send + Sync {
    /// Handle incoming event
    async fn handle_event(&self, event: &JarvisEvent) -> Result<(), String>;

    /// Get handler ID
    fn handler_id(&self) -> String;

    /// Get subscribed topics/patterns
    fn subscribed_topics(&self) -> Vec<String>;
}

/// Example automation event handler
pub struct AutomationHandler {
    id: String,
    topics: Vec<String>,
}

impl AutomationHandler {
    pub fn new(id: String, topics: Vec<String>) -> Self {
        Self { id, topics }
    }
}

#[async_trait::async_trait]
impl EventHandler for AutomationHandler {
    async fn handle_event(&self, event: &JarvisEvent) -> Result<(), String> {
        match event {
            JarvisEvent::MqttMessage { topic, payload, .. } => {
                info!("Automation {} handling MQTT: {} = {}", self.id, topic, payload);
                // Execute automation logic here
                Ok(())
            }
            JarvisEvent::HomeAssistantStateChange { entity_id, new_state, .. } => {
                info!("Automation {} handling HA state change: {} → {}", self.id, entity_id, new_state);
                Ok(())
            }
            _ => Ok(()),
        }
    }

    fn handler_id(&self) -> String {
        self.id.clone()
    }

    fn subscribed_topics(&self) -> Vec<String> {
        self.topics.clone()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_event_bus_publish_subscribe() {
        let bus = EventBus::new(100);
        let mut receiver = bus.subscribe();

        let event = JarvisEvent::MqttMessage {
            topic: "test/topic".to_string(),
            payload: "test payload".to_string(),
            qos: 0,
        };

        bus.publish(event.clone()).unwrap();

        let received = receiver.recv().await.unwrap();
        match received {
            JarvisEvent::MqttMessage { topic, payload, .. } => {
                assert_eq!(topic, "test/topic");
                assert_eq!(payload, "test payload");
            }
            _ => panic!("Wrong event type"),
        }
    }

    #[tokio::test]
    async fn test_multiple_subscribers() {
        let bus = EventBus::new(100);
        let mut receiver1 = bus.subscribe();
        let mut receiver2 = bus.subscribe();

        let event = JarvisEvent::SystemEvent {
            event_type: "startup".to_string(),
            data: "{}".to_string(),
        };

        bus.publish(event).unwrap();

        assert!(receiver1.recv().await.is_ok());
        assert!(receiver2.recv().await.is_ok());
    }
}
