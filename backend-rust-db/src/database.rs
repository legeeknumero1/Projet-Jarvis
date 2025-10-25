/// Database Service - PostgreSQL avec sqlx
/// Type-safe SQL queries at compile time
use sqlx::postgres::{PgPool, PgPoolOptions};
use tracing::{info, debug};

use crate::models::*;
use crate::error::{DbError, DbResult};

pub struct DatabaseService {
    pool: PgPool,
}

impl DatabaseService {
    /// Créer nouvelle connexion PostgreSQL
    pub async fn new(database_url: &str) -> DbResult<Self> {
        info!("🗄️ Connecting to PostgreSQL: {}", database_url);

        let pool = PgPoolOptions::new()
            .max_connections(20)
            .connect(database_url)
            .await
            .map_err(|e| DbError::ConnectionError(e.to_string()))?;

        // Créer les tables si nécessaire
        Self::init_schema(&pool).await?;

        info!("✅ PostgreSQL connected");

        Ok(Self { pool })
    }

    /// Initialiser le schema
    async fn init_schema(pool: &PgPool) -> DbResult<()> {
        sqlx::query(
            r#"
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                summary TEXT,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
                message_count INTEGER DEFAULT 0,
                is_archived BOOLEAN DEFAULT FALSE,
                metadata JSONB,
                INDEX idx_user_id (user_id),
                INDEX idx_created_at (created_at)
            );

            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                embedding_vector FLOAT8[],
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                tokens INTEGER,
                metadata JSONB,
                INDEX idx_conversation_id (conversation_id),
                INDEX idx_role (role)
            );

            CREATE TABLE IF NOT EXISTS user_stats (
                user_id TEXT PRIMARY KEY,
                total_conversations BIGINT DEFAULT 0,
                total_messages BIGINT DEFAULT 0,
                total_tokens_used BIGINT DEFAULT 0,
                first_seen TIMESTAMP NOT NULL DEFAULT NOW(),
                last_seen TIMESTAMP NOT NULL DEFAULT NOW(),
                preferences JSONB
            );
            "#
        )
        .execute(pool)
        .await
        .map_err(|e| DbError::Database(e.to_string()))?;

        info!("✅ Database schema initialized");
        Ok(())
    }

    /// Vérifier la santé de la connexion
    pub async fn health_check(&self) -> DbResult<bool> {
        sqlx::query("SELECT 1")
            .fetch_one(&self.pool)
            .await
            .map(|_| true)
            .map_err(|e| DbError::Database(e.to_string()))
    }

    // ========== CONVERSATIONS ==========

    /// Créer une nouvelle conversation
    pub async fn create_conversation(&self, conversation: Conversation) -> DbResult<Conversation> {
        debug!("Creating conversation: {}", conversation.id);

        sqlx::query(
            r#"
            INSERT INTO conversations (id, user_id, title, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5)
            "#
        )
        .bind(&conversation.id)
        .bind(&conversation.user_id)
        .bind(&conversation.title)
        .bind(conversation.created_at)
        .bind(conversation.updated_at)
        .execute(&self.pool)
        .await?;

        info!("✅ Conversation created: {}", conversation.id);
        Ok(conversation)
    }

    /// Récupérer une conversation
    pub async fn get_conversation(&self, id: &str) -> DbResult<Conversation> {
        sqlx::query_as::<_, Conversation>(
            "SELECT id, user_id, title, summary, created_at, updated_at, message_count, is_archived, metadata FROM conversations WHERE id = $1"
        )
        .bind(id)
        .fetch_one(&self.pool)
        .await
        .map_err(|_| DbError::NotFound(format!("Conversation {} not found", id)))
    }

    /// Lister conversations d'un utilisateur
    pub async fn list_conversations(&self, user_id: &str, limit: i32, offset: i32) -> DbResult<Vec<Conversation>> {
        sqlx::query_as::<_, Conversation>(
            r#"
            SELECT id, user_id, title, summary, created_at, updated_at, message_count, is_archived, metadata
            FROM conversations
            WHERE user_id = $1 AND NOT is_archived
            ORDER BY updated_at DESC
            LIMIT $2 OFFSET $3
            "#
        )
        .bind(user_id)
        .bind(limit)
        .bind(offset)
        .fetch_all(&self.pool)
        .await
        .map_err(|e| DbError::Database(e.to_string()))
    }

    /// Supprimer une conversation (soft delete)
    pub async fn archive_conversation(&self, id: &str) -> DbResult<()> {
        sqlx::query("UPDATE conversations SET is_archived = TRUE, updated_at = NOW() WHERE id = $1")
            .bind(id)
            .execute(&self.pool)
            .await?;

        info!("✅ Conversation archived: {}", id);
        Ok(())
    }

    // ========== MESSAGES ==========

    /// Créer un message
    pub async fn create_message(&self, message: Message) -> DbResult<Message> {
        debug!("Creating message: {}", message.id);

        sqlx::query(
            r#"
            INSERT INTO messages (id, conversation_id, role, content, created_at, tokens, metadata)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            "#
        )
        .bind(&message.id)
        .bind(&message.conversation_id)
        .bind(&message.role)
        .bind(&message.content)
        .bind(message.created_at)
        .bind(message.tokens)
        .bind(&message.metadata)
        .execute(&self.pool)
        .await?;

        // Incrémenter message_count
        sqlx::query(
            "UPDATE conversations SET message_count = message_count + 1, updated_at = NOW() WHERE id = $1"
        )
        .bind(&message.conversation_id)
        .execute(&self.pool)
        .await?;

        info!("✅ Message created: {}", message.id);
        Ok(message)
    }

    /// Récupérer les messages d'une conversation
    pub async fn get_messages(&self, conversation_id: &str, limit: i32) -> DbResult<Vec<Message>> {
        sqlx::query_as::<_, Message>(
            r#"
            SELECT id, conversation_id, role, content, embedding_vector, created_at, tokens, metadata
            FROM messages
            WHERE conversation_id = $1
            ORDER BY created_at ASC
            LIMIT $2
            "#
        )
        .bind(conversation_id)
        .bind(limit)
        .fetch_all(&self.pool)
        .await
        .map_err(|e| DbError::Database(e.to_string()))
    }

    // ========== STATS ==========

    /// Mettre à jour stats utilisateur
    pub async fn update_user_stats(&self, user_id: &str, tokens_used: i32) -> DbResult<()> {
        sqlx::query(
            r#"
            INSERT INTO user_stats (user_id, total_messages, total_tokens_used, last_seen)
            VALUES ($1, 1, $2, NOW())
            ON CONFLICT (user_id) DO UPDATE SET
                total_messages = user_stats.total_messages + 1,
                total_tokens_used = user_stats.total_tokens_used + $2,
                last_seen = NOW()
            "#
        )
        .bind(user_id)
        .bind(tokens_used)
        .execute(&self.pool)
        .await?;

        Ok(())
    }

    /// Récupérer stats utilisateur
    pub async fn get_user_stats(&self, user_id: &str) -> DbResult<UserStats> {
        sqlx::query_as::<_, UserStats>(
            "SELECT user_id, total_conversations, total_messages, total_tokens_used, first_seen, last_seen, preferences FROM user_stats WHERE user_id = $1"
        )
        .bind(user_id)
        .fetch_optional(&self.pool)
        .await?
        .ok_or_else(|| DbError::NotFound(format!("Stats for user {} not found", user_id)))
    }

    /// Exécuter une raw query (pour cas spéciaux)
    pub async fn execute_raw(&self, query: &str) -> DbResult<u64> {
        sqlx::query(query)
            .execute(&self.pool)
            .await
            .map(|r| r.rows_affected())
            .map_err(|e| DbError::Database(e.to_string()))
    }
}
