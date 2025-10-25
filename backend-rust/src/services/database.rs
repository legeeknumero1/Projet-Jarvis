//! Service de base de données pour Jarvis Rust Backend
//! 
//! Wrapper Rust autour de PostgreSQL avec sqlx
//! Remplace SQLAlchemy Python avec gains de sécurité mémoire

use chrono::{DateTime, Utc};
use sqlx::{postgres::PgPoolOptions, PgPool, Row};
use std::time::Duration;
use uuid::Uuid;

use crate::{
    config::AppConfig,
    models::{Conversation, ConversationStatus, Message, MessageRole},
};

/// Service de gestion de base de données
#[derive(Clone)]
pub struct DatabaseService {
    pool: PgPool,
}

impl DatabaseService {
    /// Initialise le service avec une pool de connexions
    pub async fn new(config: &AppConfig) -> anyhow::Result<Self> {
        tracing::info!("🗄️ Connexion à PostgreSQL: {}", 
                      config.database.url.replace(&config.database.url.split('@').nth(1).unwrap_or(""), "@***"));

        let pool = PgPoolOptions::new()
            .max_connections(config.database.max_connections)
            .min_connections(config.database.min_connections)
            .acquire_timeout(Duration::from_secs(config.database.acquire_timeout_secs))
            .idle_timeout(Duration::from_secs(config.database.idle_timeout_secs))
            .connect(&config.database.url)
            .await?;

        // Test de connexion
        let version: String = sqlx::query_scalar("SELECT version()")
            .fetch_one(&pool)
            .await?;
        
        tracing::info!("✅ Connecté à PostgreSQL: {}", 
                      version.split_whitespace().take(2).collect::<Vec<_>>().join(" "));

        // Vérifier les migrations (sera implémenté plus tard)
        // sqlx::migrate!("./migrations").run(&pool).await?;

        Ok(Self { pool })
    }

    /// Vérifie si la base de données est prête
    pub async fn is_ready(&self) -> anyhow::Result<()> {
        sqlx::query("SELECT 1")
            .fetch_one(&self.pool)
            .await?;
        Ok(())
    }

    // ========================================================================
    // MÉTHODES CONVERSATIONS
    // ========================================================================

    /// Crée une nouvelle conversation
    pub async fn create_conversation(
        &self,
        title: Option<String>,
        user_id: Option<Uuid>,
    ) -> anyhow::Result<Conversation> {
        let id = Uuid::new_v4();
        let now = Utc::now();

        let conversation = sqlx::query_as!(
            Conversation,
            r#"
            INSERT INTO conversations (id, title, user_id, status, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING 
                id, title, user_id, 
                status as "status: ConversationStatus", 
                created_at, updated_at, last_message_at
            "#,
            id,
            title,
            user_id,
            ConversationStatus::Active as ConversationStatus,
            now,
            now
        )
        .fetch_one(&self.pool)
        .await?;

        tracing::debug!("✅ Conversation créée: {}", id);
        Ok(conversation)
    }

    /// Récupère une conversation par ID
    pub async fn get_conversation(&self, id: Uuid) -> anyhow::Result<Option<Conversation>> {
        let conversation = sqlx::query_as!(
            Conversation,
            r#"
            SELECT 
                id, title, user_id, 
                status as "status: ConversationStatus", 
                created_at, updated_at, last_message_at
            FROM conversations 
            WHERE id = $1 AND status != $2
            "#,
            id,
            ConversationStatus::Deleted as ConversationStatus
        )
        .fetch_optional(&self.pool)
        .await?;

        Ok(conversation)
    }

    /// Liste les conversations avec pagination
    pub async fn list_conversations(
        &self,
        limit: u32,
        offset: u32,
    ) -> anyhow::Result<Vec<Conversation>> {
        let conversations = sqlx::query_as!(
            Conversation,
            r#"
            SELECT 
                id, title, user_id, 
                status as "status: ConversationStatus", 
                created_at, updated_at, last_message_at
            FROM conversations 
            WHERE status != $1
            ORDER BY COALESCE(last_message_at, updated_at) DESC
            LIMIT $2 OFFSET $3
            "#,
            ConversationStatus::Deleted as ConversationStatus,
            limit as i64,
            offset as i64
        )
        .fetch_all(&self.pool)
        .await?;

        Ok(conversations)
    }

    /// Supprime une conversation (soft delete)
    pub async fn delete_conversation(&self, id: Uuid) -> anyhow::Result<u64> {
        let now = Utc::now();
        
        let result = sqlx::query!(
            "UPDATE conversations SET status = $1, updated_at = $2 WHERE id = $3",
            ConversationStatus::Deleted as ConversationStatus,
            now,
            id
        )
        .execute(&self.pool)
        .await?;

        // Compter les messages associés (pour retourner le nombre)
        let message_count = sqlx::query_scalar!(
            "SELECT COUNT(*) FROM messages WHERE conversation_id = $1",
            id
        )
        .fetch_one(&self.pool)
        .await?
        .unwrap_or(0) as u64;

        Ok(message_count)
    }

    // ========================================================================
    // MÉTHODES MESSAGES
    // ========================================================================

    /// Ajoute un message à une conversation
    pub async fn create_message(
        &self,
        conversation_id: Uuid,
        role: MessageRole,
        content: String,
        metadata: Option<serde_json::Value>,
    ) -> anyhow::Result<Message> {
        let id = Uuid::new_v4();
        let now = Utc::now();

        // Convertir les métadonnées en JSON
        let metadata_json = metadata.map(|m| serde_json::to_value(m).unwrap_or_default());

        let message = sqlx::query_as!(
            Message,
            r#"
            INSERT INTO messages (id, conversation_id, role, content, metadata, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING 
                id, conversation_id, 
                role as "role: MessageRole",
                content, 
                metadata as "metadata: Option<serde_json::Value>",
                created_at, updated_at
            "#,
            id,
            conversation_id,
            role as MessageRole,
            content,
            metadata_json,
            now,
            now
        )
        .fetch_one(&self.pool)
        .await?;

        // Mettre à jour last_message_at de la conversation
        sqlx::query!(
            "UPDATE conversations SET last_message_at = $1, updated_at = $2 WHERE id = $3",
            now,
            now,
            conversation_id
        )
        .execute(&self.pool)
        .await?;

        tracing::debug!("✅ Message créé: {} pour conversation {}", id, conversation_id);
        Ok(message)
    }

    /// Récupère les messages d'une conversation
    pub async fn get_messages(
        &self,
        conversation_id: Uuid,
        limit: u32,
        offset: u32,
        since: Option<DateTime<Utc>>,
    ) -> anyhow::Result<Vec<Message>> {
        let messages = if let Some(since_time) = since {
            sqlx::query_as!(
                Message,
                r#"
                SELECT 
                    id, conversation_id, 
                    role as "role: MessageRole",
                    content, 
                    metadata as "metadata: Option<serde_json::Value>",
                    created_at, updated_at
                FROM messages 
                WHERE conversation_id = $1 AND created_at >= $2
                ORDER BY created_at ASC
                LIMIT $3 OFFSET $4
                "#,
                conversation_id,
                since_time,
                limit as i64,
                offset as i64
            )
            .fetch_all(&self.pool)
            .await?
        } else {
            sqlx::query_as!(
                Message,
                r#"
                SELECT 
                    id, conversation_id, 
                    role as "role: MessageRole",
                    content, 
                    metadata as "metadata: Option<serde_json::Value>",
                    created_at, updated_at
                FROM messages 
                WHERE conversation_id = $1
                ORDER BY created_at ASC
                LIMIT $2 OFFSET $3
                "#,
                conversation_id,
                limit as i64,
                offset as i64
            )
            .fetch_all(&self.pool)
            .await?
        };

        Ok(messages)
    }

    /// Compte le nombre total de messages dans une conversation
    pub async fn count_messages(&self, conversation_id: Uuid) -> anyhow::Result<u64> {
        let count = sqlx::query_scalar!(
            "SELECT COUNT(*) FROM messages WHERE conversation_id = $1",
            conversation_id
        )
        .fetch_one(&self.pool)
        .await?
        .unwrap_or(0) as u64;

        Ok(count)
    }

    // ========================================================================
    // MÉTHODES SYSTÈME
    // ========================================================================

    /// Vérifie la santé de la base de données
    pub async fn health_check(&self) -> anyhow::Result<serde_json::Value> {
        let start = std::time::Instant::now();
        
        // Test de connexion simple
        let version: String = sqlx::query_scalar("SELECT version()")
            .fetch_one(&self.pool)
            .await?;

        let response_time = start.elapsed().as_millis() as u64;

        // Statistiques de la pool
        let pool_size = self.pool.size();
        let idle_connections = self.pool.num_idle();

        Ok(serde_json::json!({
            "status": "healthy",
            "response_time_ms": response_time,
            "version": version.split_whitespace().take(2).collect::<Vec<_>>().join(" "),
            "pool": {
                "size": pool_size,
                "idle": idle_connections,
                "active": pool_size - idle_connections
            }
        }))
    }

    /// Nettoie les anciennes données (maintenance)
    pub async fn cleanup_old_data(&self, days: i32) -> anyhow::Result<u64> {
        let cutoff_date = Utc::now() - chrono::Duration::days(days as i64);
        
        // Supprimer les conversations marquées comme supprimées depuis plus de X jours
        let result = sqlx::query!(
            r#"
            DELETE FROM conversations 
            WHERE status = $1 AND updated_at < $2
            "#,
            ConversationStatus::Deleted as ConversationStatus,
            cutoff_date
        )
        .execute(&self.pool)
        .await?;

        Ok(result.rows_affected())
    }
}