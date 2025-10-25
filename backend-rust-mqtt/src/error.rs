/// Error types pour MQTT
use thiserror::Error;

#[derive(Error, Debug)]
pub enum MqttError {
    #[error("MQTT connection error: {0}")]
    Connection(String),

    #[error("MQTT publish error: {0}")]
    Publish(String),

    #[error("MQTT subscribe error: {0}")]
    Subscribe(String),

    #[error("Home Assistant error: {0}")]
    HomeAssistant(String),

    #[error("Automation error: {0}")]
    Automation(String),

    #[error("Invalid payload: {0}")]
    InvalidPayload(String),

    #[error("Serialization error: {0}")]
    SerializationError(#[from] serde_json::Error),

    #[error("Internal error: {0}")]
    Internal(String),
}

pub type MqttResult<T> = Result<T, MqttError>;

impl From<rumqttc::ClientError> for MqttError {
    fn from(err: rumqttc::ClientError) -> Self {
        MqttError::Connection(err.to_string())
    }
}
