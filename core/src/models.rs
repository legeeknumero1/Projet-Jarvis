use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};

pub mod entities;

#[derive(Clone)]
pub struct AppState {
    pub python_bridges_url: String,
    pub audio_engine_url: String,
}

// ============= Chat Models =============

#[derive(Debug, Serialize, Deserialize)]
pub struct ChatRequest {
    pub content: String,
    pub conversation_id: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ChatResponse {
    pub id: String,
    pub conversation_id: String,
    pub role: String,
    pub content: String,
    pub timestamp: DateTime<Utc>,
    pub tokens: Option<i32>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Conversation {
    pub id: String,
    pub title: String,
    pub summary: Option<String>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
    pub message_count: i32,
}

// ============= STT/TTS Models =============

#[derive(Debug, Serialize, Deserialize)]
pub struct TranscribeRequest {
    pub audio_data: String,
    pub language: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct TranscribeResponse {
    pub text: String,
    pub language: String,
    pub confidence: f32,
    pub duration_ms: u32,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SynthesizeRequest {
    pub text: String,
    pub voice: Option<String>,
    pub speed: Option<f32>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SynthesizeResponse {
    pub audio_data: String,
    pub sample_rate: u32,
    pub duration_ms: u32,
    pub voice: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct VoiceInfo {
    pub id: String,
    pub name: String,
    pub language: String,
    pub gender: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct LanguageInfo {
    pub code: String,
    pub name: String,
}

// ============= Memory Models =============

#[derive(Debug, Serialize, Deserialize)]
pub struct MemoryEntry {
    pub id: String,
    pub content: String,
    pub embedding: Option<Vec<f32>>,
    pub importance: f32,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct AddMemoryRequest {
    pub content: String,
    pub importance: Option<f32>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SearchMemoryRequest {
    pub query: String,
    pub limit: Option<i32>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SearchMemoryResponse {
    pub results: Vec<MemoryEntry>,
    pub total: i32,
}

// ============= Health Models =============

#[derive(Debug, Serialize, Deserialize)]
pub struct HealthStatus {
    pub status: String,
    pub version: String,
    pub uptime_secs: u64,
    pub services: ServiceStatus,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ServiceStatus {
    pub database: String,
    pub python_bridges: String,
    pub audio_engine: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Metrics {
    pub requests_total: u64,
    pub chat_requests: u64,
    pub stt_requests: u64,
    pub tts_requests: u64,
    pub memory_searches: u64,
    pub avg_latency_ms: f32,
}

// ============= Authentication Models =============

#[derive(Debug, Serialize, Deserialize)]
pub struct LoginRequest {
    pub username: String,
    pub password: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct LoginResponse {
    pub access_token: String,
    pub token_type: String,
    pub expires_in: i64,
    pub user_id: String,
    pub username: String,
}

// ============= Error Models =============

#[derive(Debug, Serialize, Deserialize)]
pub struct ErrorResponse {
    pub error: String,
    pub details: Option<String>,
    pub request_id: String,
}
