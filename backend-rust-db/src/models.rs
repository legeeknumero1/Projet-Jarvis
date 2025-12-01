/// Modèles de données pour DB Layer
use serde::{Deserialize, Serialize};
use sqlx::FromRow;
use uuid::Uuid;
use chrono::{DateTime, Utc};

/// Conversation avec métadonnées complètes
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct Conversation {
    pub id: String,
    pub user_id: String,
    pub title: String,
    pub summary: Option<String>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
    pub message_count: i32,
    pub is_archived: bool,
    pub metadata: Option<serde_json::Value>,
}

impl Conversation {
    pub fn new(user_id: String, title: String) -> Self {
        let id = Uuid::new_v4().to_string();
        let now = Utc::now();

        Self {
            id,
            user_id,
            title,
            summary: None,
            created_at: now,
            updated_at: now,
            message_count: 0,
            is_archived: false,
            metadata: None,
        }
    }
}

/// Message dans une conversation
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct Message {
    pub id: String,
    pub conversation_id: String,
    pub role: String,  // "user" ou "assistant"
    pub content: String,
    pub embedding_vector: Option<Vec<f32>>,  // Pour recherche sémantique
    pub created_at: DateTime<Utc>,
    pub tokens: Option<i32>,
    pub metadata: Option<serde_json::Value>,
}

impl Message {
    pub fn new(conversation_id: String, role: String, content: String) -> Self {
        Self {
            id: Uuid::new_v4().to_string(),
            conversation_id,
            role,
            content,
            embedding_vector: None,
            created_at: Utc::now(),
            tokens: None,
            metadata: None,
        }
    }
}

/// Entrée de mémoire sémantique (pour Qdrant)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MemoryEntry {
    pub id: String,
    pub user_id: String,
    pub content: String,
    pub vector: Vec<f32>,  // Embedding (384D par défaut)
    pub category: String,  // "conversation", "preference", "context"
    pub importance: f32,   // 0.0 à 1.0
    pub created_at: DateTime<Utc>,
    pub last_accessed: DateTime<Utc>,
    pub metadata: Option<serde_json::Value>,
}

impl MemoryEntry {
    pub fn new(
        user_id: String,
        content: String,
        vector: Vec<f32>,
        category: String,
    ) -> Self {
        let now = Utc::now();

        Self {
            id: Uuid::new_v4().to_string(),
            user_id,
            content,
            vector,
            category,
            importance: 0.5,
            created_at: now,
            last_accessed: now,
            metadata: None,
        }
    }
}

/// Résultat de recherche
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SearchResult {
    pub id: String,
    pub content: String,
    pub score: f32,
    pub source: String,  // "conversation", "memory", etc.
    pub created_at: DateTime<Utc>,
    pub metadata: Option<serde_json::Value>,
}

/// Statistiques utilisateur
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct UserStats {
    pub user_id: String,
    pub total_conversations: i64,
    pub total_messages: i64,
    pub total_tokens_used: i64,
    pub first_seen: DateTime<Utc>,
    pub last_seen: DateTime<Utc>,
    pub preferences: Option<serde_json::Value>,
}

/// Chunk de texte pour indexation tantivy
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TextChunk {
    pub id: String,
    pub content: String,
    pub source: String,      // "conversation", "memory", etc.
    pub source_id: String,   // ID de la source
    pub created_at: DateTime<Utc>,
}

impl TextChunk {
    pub fn new(content: String, source: String, source_id: String) -> Self {
        Self {
            id: Uuid::new_v4().to_string(),
            content,
            source,
            source_id,
            created_at: Utc::now(),
        }
    }
}

/// Options de recherche
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SearchOptions {
    pub query: String,
    pub limit: i32,
    pub offset: i32,
    pub filters: Option<SearchFilters>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SearchFilters {
    pub user_id: Option<String>,
    pub source: Option<String>,
    pub date_from: Option<DateTime<Utc>>,
    pub date_to: Option<DateTime<Utc>>,
}
