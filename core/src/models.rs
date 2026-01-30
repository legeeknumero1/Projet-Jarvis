use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use utoipa::ToSchema;

pub mod entities;

use crate::services::db::DbService;
use crate::services::audio_engine::AudioEngineClient;
use crate::services::qdrant::QdrantService;
use crate::services::ollama::OllamaService;
use crate::services::stt_native::SttNativeService;
use crate::services::tts_native::TtsNativeService;
use std::sync::Arc;

#[derive(Clone)]
pub struct AppState {
    pub ollama_url: String,
    pub qdrant_url: String,
    pub audio_engine: Arc<AudioEngineClient>,
    pub db: Arc<DbService>,
    pub qdrant: Arc<QdrantService>,
    pub ollama: Arc<OllamaService>,
    pub stt: Arc<SttNativeService>,
    pub tts: Arc<TtsNativeService>,
}

impl AppState {
    pub fn ollama_url(&self) -> &String {
        &self.ollama_url
    }
}

// ============= Chat Models =============

#[derive(Debug, Serialize, Deserialize, ToSchema)]
pub struct ChatRequest {
    pub content: String,
    pub conversation_id: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, ToSchema)]
pub struct ChatResponse {
    pub id: String,
    pub conversation_id: String,
    pub role: String,
    pub content: String,
    pub timestamp: DateTime<Utc>,
    pub tokens: Option<i32>,
}

#[derive(Debug, Serialize, Deserialize, ToSchema)]
pub struct Conversation {
    pub id: String,
    pub title: String,
    pub summary: Option<String>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
    pub message_count: i32,
}

// ============= STT/TTS Models =============

#[derive(Debug, Serialize, Deserialize, ToSchema)]
pub struct TranscribeRequest {
    pub audio_data: String,
    pub language: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, ToSchema)]
pub struct TranscribeResponse {
    pub text: String,
    pub language: String,
    pub confidence: f32,
    pub duration_ms: u32,
}

#[derive(Debug, Serialize, Deserialize, ToSchema)]
pub struct SynthesizeRequest {
    pub text: String,
    pub voice: Option<String>,
    pub speed: Option<f32>,
}

#[derive(Debug, Serialize, Deserialize, ToSchema)]
pub struct SynthesizeResponse {
    pub audio_data: String,
    pub sample_rate: u32,
    pub duration_ms: u32,
    pub voice: String,
}

#[derive(Debug, Serialize, Deserialize, ToSchema)]
pub struct VoiceInfo {
    pub id: String,
    pub name: String,
    pub language: String,
    pub gender: String,
}

#[derive(Debug, Serialize, Deserialize, ToSchema)]
pub struct LanguageInfo {
    pub code: String,
    pub name: String,
}

// ============= Memory Models =============

#[derive(Debug, Serialize, Deserialize, ToSchema)]
pub struct MemoryEntry {
    pub id: String,
    pub content: String,
    pub embedding: Option<Vec<f32>>,
    pub importance: f32,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Serialize, Deserialize, ToSchema)]
pub struct AddMemoryRequest {
    pub content: String,
    pub importance: Option<f32>,
}

#[derive(Debug, Serialize, Deserialize, ToSchema)]
pub struct SearchMemoryRequest {
    pub query: String,
    pub limit: Option<i32>,
}

#[derive(Debug, Serialize, Deserialize, ToSchema)]
pub struct SearchMemoryResponse {
    pub results: Vec<MemoryEntry>,
    pub total: i32,
}

// ============= Health Models =============

#[derive(Debug, Serialize, Deserialize, ToSchema)]
pub struct HealthStatus {
    pub status: String,
    pub version: String,
    pub uptime_secs: u64,
    pub services: ServiceStatus,
}

#[derive(Debug, Serialize, Deserialize, ToSchema)]
pub struct ServiceStatus {
    pub database: String,
    pub python_bridges: String,
    pub audio_engine: String,
}

#[derive(Debug, Serialize, Deserialize, ToSchema)]
pub struct Metrics {
    pub requests_total: u64,
    pub chat_requests: u64,
    pub stt_requests: u64,
    pub tts_requests: u64,
    pub memory_searches: u64,
    pub avg_latency_ms: f32,
}

// ============= Authentication Models =============

#[derive(Debug, Serialize, Deserialize, ToSchema)]
pub struct LoginRequest {
    pub username: String,
    pub password: String,
}

#[derive(Debug, Serialize, Deserialize, ToSchema)]
pub struct LoginResponse {
    pub access_token: String,
    pub token_type: String,
    pub expires_in: i64,
    pub user_id: String,
    pub username: String,
}

// User model from database (for authentication)
#[derive(Debug, sqlx::FromRow)]
pub struct User {
    pub id: uuid::Uuid,
    pub username: String,
    pub password_hash: String,
    pub email: Option<String>,
    pub full_name: Option<String>,
    pub is_active: bool,
    pub is_admin: bool,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
    pub last_login: Option<DateTime<Utc>>,
}

/*
============= OpenAI Compatibility Models =============
*/

#[derive(Debug, Serialize, Deserialize)]
pub struct OpenAIChatRequest {
    pub model: String,
    pub messages: Vec<OpenAIChatMessage>,
    #[serde(default)]
    pub stream: bool,
    pub temperature: Option<f32>,
    pub max_tokens: Option<i32>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct OpenAIChatMessage {
    pub role: String,
    pub content: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct OpenAIChatResponse {
    pub id: String,
    pub object: String,
    pub created: i64,
    pub model: String,
    pub choices: Vec<OpenAIChoice>,
    pub usage: OpenAIUsage,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct OpenAIChoice {
    pub index: i32,
    pub message: OpenAIChatMessage,
    pub finish_reason: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct OpenAIUsage {
    pub prompt_tokens: i32,
    pub completion_tokens: i32,
    pub total_tokens: i32,
}

/*
============= Error Models =============
*/

#[derive(Debug, Serialize, Deserialize, ToSchema)]
pub struct ErrorResponse {
    pub error: String,
    pub details: Option<String>,
    pub request_id: String,
}
