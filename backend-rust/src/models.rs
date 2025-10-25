//! Modèles de données pour Jarvis Rust Backend
//! 
//! Structures Rust équivalentes aux modèles Pydantic Python
//! avec sérialisation JSON et validation stricte

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use sqlx::FromRow;
use uuid::Uuid;

// ============================================================================
// MODÈLES CHAT & CONVERSATIONS
// ============================================================================

/// Message de chat individuel
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct Message {
    pub id: Uuid,
    pub conversation_id: Uuid,
    pub role: MessageRole,
    pub content: String,
    pub metadata: Option<MessageMetadata>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

/// Rôle du message dans la conversation
#[derive(Debug, Clone, Serialize, Deserialize, sqlx::Type)]
#[sqlx(type_name = "message_role", rename_all = "lowercase")]
pub enum MessageRole {
    User,
    Assistant,
    System,
}

/// Métadonnées additionnelles du message
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MessageMetadata {
    pub tokens_used: Option<u32>,
    pub response_time_ms: Option<u64>,
    pub model_name: Option<String>,
    pub temperature: Option<f32>,
    pub audio_file: Option<String>,
    pub source: Option<String>,
}

/// Conversation complète avec messages
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct Conversation {
    pub id: Uuid,
    pub title: Option<String>,
    pub user_id: Option<Uuid>,
    pub status: ConversationStatus,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
    pub last_message_at: Option<DateTime<Utc>>,
}

/// Statut de la conversation
#[derive(Debug, Clone, Serialize, Deserialize, sqlx::Type)]
#[sqlx(type_name = "conversation_status", rename_all = "lowercase")]
pub enum ConversationStatus {
    Active,
    Archived,
    Deleted,
}

// ============================================================================
// REQUÊTES & RÉPONSES API
// ============================================================================

/// Requête d'envoi de message
#[derive(Debug, Deserialize)]
pub struct SendMessageRequest {
    pub message: String,
    pub conversation_id: Option<Uuid>,
    pub stream: Option<bool>,
    pub model: Option<String>,
    pub temperature: Option<f32>,
    pub max_tokens: Option<u32>,
}

/// Réponse de message IA
#[derive(Debug, Serialize)]
pub struct SendMessageResponse {
    pub message: Message,
    pub conversation_id: Uuid,
    pub usage: TokenUsage,
    pub response_time_ms: u64,
}

/// Utilisation de tokens
#[derive(Debug, Serialize, Deserialize)]
pub struct TokenUsage {
    pub prompt_tokens: u32,
    pub completion_tokens: u32,
    pub total_tokens: u32,
}

/// Requête d'historique de conversation
#[derive(Debug, Deserialize)]
pub struct GetHistoryRequest {
    pub conversation_id: Option<Uuid>,
    pub limit: Option<u32>,
    pub offset: Option<u32>,
    pub since: Option<DateTime<Utc>>,
}

/// Réponse d'historique avec pagination
#[derive(Debug, Serialize)]
pub struct GetHistoryResponse {
    pub messages: Vec<Message>,
    pub conversation: Option<Conversation>,
    pub total_count: u64,
    pub has_more: bool,
}

// ============================================================================
// MODÈLES AUDIO/VOICE
// ============================================================================

/// Requête de transcription STT
#[derive(Debug, Deserialize)]
pub struct TranscribeRequest {
    pub audio_data: String, // Base64 encoded
    pub language: Option<String>,
    pub prompt: Option<String>,
}

/// Réponse de transcription
#[derive(Debug, Serialize)]
pub struct TranscribeResponse {
    pub text: String,
    pub language: String,
    pub confidence: f32,
    pub duration_secs: f32,
    pub words: Option<Vec<WordTimestamp>>,
}

/// Timing des mots pour la transcription
#[derive(Debug, Serialize, Deserialize)]
pub struct WordTimestamp {
    pub word: String,
    pub start_time: f32,
    pub end_time: f32,
    pub confidence: f32,
}

/// Requête de synthèse TTS
#[derive(Debug, Deserialize)]
pub struct SynthesizeRequest {
    pub text: String,
    pub voice: Option<String>,
    pub speed: Option<f32>,
    pub format: Option<AudioFormat>,
}

/// Réponse de synthèse
#[derive(Debug, Serialize)]
pub struct SynthesizeResponse {
    pub audio_data: String, // Base64 encoded
    pub format: AudioFormat,
    pub duration_secs: f32,
    pub sample_rate: u32,
}

/// Format audio supporté
#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum AudioFormat {
    Wav,
    Mp3,
    Ogg,
    Flac,
}

// ============================================================================
// MODÈLES SYSTÈME & MONITORING
// ============================================================================

/// Statut de santé du système
#[derive(Debug, Serialize)]
pub struct HealthStatus {
    pub status: ServiceStatus,
    pub version: String,
    pub uptime_secs: u64,
    pub services: ServiceHealthMap,
    pub memory_usage: MemoryUsage,
    pub timestamp: DateTime<Utc>,
}

/// Statut d'un service
#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum ServiceStatus {
    Healthy,
    Degraded,
    Unhealthy,
}

/// Map des statuts de services
pub type ServiceHealthMap = std::collections::HashMap<String, ServiceHealth>;

/// Santé d'un service individuel
#[derive(Debug, Serialize)]
pub struct ServiceHealth {
    pub status: ServiceStatus,
    pub response_time_ms: Option<u64>,
    pub last_check: DateTime<Utc>,
    pub error: Option<String>,
}

/// Utilisation mémoire
#[derive(Debug, Serialize)]
pub struct MemoryUsage {
    pub used_mb: u64,
    pub total_mb: u64,
    pub percentage: f32,
}

// ============================================================================
// MODÈLES WEBSOCKET
// ============================================================================

/// Message WebSocket entrant
#[derive(Debug, Deserialize)]
#[serde(tag = "type", rename_all = "snake_case")]
pub enum WSIncomingMessage {
    ChatMessage { 
        content: String, 
        conversation_id: Option<Uuid>,
    },
    AudioData { 
        data: String, // Base64
        format: AudioFormat,
    },
    Ping,
    Subscribe { 
        channels: Vec<String>,
    },
}

/// Message WebSocket sortant
#[derive(Debug, Serialize)]
#[serde(tag = "type", rename_all = "snake_case")]
pub enum WSOutgoingMessage {
    ChatResponse { 
        message: Message,
        conversation_id: Uuid,
    },
    AudioResponse { 
        data: String, // Base64
        format: AudioFormat,
    },
    SystemStatus { 
        status: HealthStatus,
    },
    Error { 
        message: String,
        code: u16,
    },
    Pong,
}

// ============================================================================
// MODÈLES MÉMOIRE & CONTEXTE
// ============================================================================

/// Entrée de mémoire vectorielle
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct MemoryEntry {
    pub id: Uuid,
    pub content: String,
    pub embedding: Vec<f32>,
    pub metadata: MemoryMetadata,
    pub relevance_score: Option<f32>,
    pub created_at: DateTime<Utc>,
}

/// Métadonnées de mémoire
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MemoryMetadata {
    pub source: String,
    pub conversation_id: Option<Uuid>,
    pub tags: Vec<String>,
    pub importance: f32,
    pub context_type: ContextType,
}

/// Type de contexte
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ContextType {
    Conversation,
    Knowledge,
    Preference,
    Command,
    Automation,
}

// ============================================================================
// MODÈLES DOMOTIQUE & AUTOMATIONS
// ============================================================================

/// État d'un device domotique
#[derive(Debug, Serialize, Deserialize)]
pub struct DeviceState {
    pub entity_id: String,
    pub state: String,
    pub attributes: serde_json::Value,
    pub last_changed: DateTime<Utc>,
    pub last_updated: DateTime<Utc>,
}

/// Commande domotique
#[derive(Debug, Deserialize)]
pub struct DeviceCommand {
    pub entity_id: String,
    pub action: String,
    pub parameters: Option<serde_json::Value>,
}

// ============================================================================
// IMPLÉMENTATIONS UTILITAIRES
// ============================================================================

impl Default for MessageRole {
    fn default() -> Self {
        Self::User
    }
}

impl Default for ConversationStatus {
    fn default() -> Self {
        Self::Active
    }
}

impl Default for ServiceStatus {
    fn default() -> Self {
        Self::Healthy
    }
}

impl Default for AudioFormat {
    fn default() -> Self {
        Self::Wav
    }
}

impl std::fmt::Display for MessageRole {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::User => write!(f, "user"),
            Self::Assistant => write!(f, "assistant"),
            Self::System => write!(f, "system"),
        }
    }
}

impl std::fmt::Display for ServiceStatus {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Healthy => write!(f, "healthy"),
            Self::Degraded => write!(f, "degraded"),
            Self::Unhealthy => write!(f, "unhealthy"),
        }
    }
}