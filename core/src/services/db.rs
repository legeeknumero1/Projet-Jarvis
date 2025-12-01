/// Database service using SeaORM
use anyhow::Result;
use sea_orm::{
    ConnectOptions, Database, DatabaseConnection, EntityTrait, QueryFilter, QueryOrder,
    ColumnTrait, Set, ActiveModelTrait,
};
use std::time::Duration;
use tracing::info;
use uuid::Uuid;

use crate::models::entities::{conversation, message};

pub struct DbService {
    conn: DatabaseConnection,
}

impl DbService {
    /// Connect to PostgreSQL database
    pub async fn new(database_url: &str) -> Result<Self> {
        info!("Connecting to database: {}", database_url);

        let mut opt = ConnectOptions::new(database_url);
        opt.max_connections(100)
            .min_connections(5)
            .connect_timeout(Duration::from_secs(8))
            .idle_timeout(Duration::from_secs(8))
            .max_lifetime(Duration::from_secs(8))
            .sqlx_logging(true);

        let conn = Database::connect(opt).await?;

        info!("Database connection established");

        Ok(Self { conn })
    }

    /// Create a new conversation
    pub async fn create_conversation(&self, user_id: &str, title: &str) -> Result<conversation::Model> {
        let now = chrono::Utc::now();

        let conversation = conversation::ActiveModel {
            id: Set(Uuid::new_v4()),
            user_id: Set(user_id.to_string()),
            title: Set(title.to_string()),
            created_at: Set(now.into()),
            updated_at: Set(now.into()),
            message_count: Set(0),
        };

        let result = conversation.insert(&self.conn).await?;
        Ok(result)
    }

    /// Get conversation by ID
    pub async fn get_conversation(&self, id: Uuid) -> Result<Option<conversation::Model>> {
        let result = conversation::Entity::find_by_id(id)
            .one(&self.conn)
            .await?;
        Ok(result)
    }

    /// List all conversations for a user
    pub async fn list_conversations(&self, user_id: &str) -> Result<Vec<conversation::Model>> {
        let results = conversation::Entity::find()
            .filter(conversation::Column::UserId.eq(user_id))
            .order_by_desc(conversation::Column::UpdatedAt)
            .all(&self.conn)
            .await?;
        Ok(results)
    }

    /// Add message to conversation
    pub async fn add_message(
        &self,
        conversation_id: Uuid,
        role: &str,
        content: &str,
    ) -> Result<message::Model> {
        let msg = message::ActiveModel {
            id: Set(Uuid::new_v4()),
            conversation_id: Set(conversation_id),
            role: Set(role.to_string()),
            content: Set(content.to_string()),
            created_at: Set(chrono::Utc::now().into()),
        };

        let result = msg.insert(&self.conn).await?;

        // Update conversation message count and timestamp
        if let Some(conv) = self.get_conversation(conversation_id).await? {
            let mut active_conv: conversation::ActiveModel = conv.into();
            active_conv.message_count = Set(active_conv.message_count.unwrap() + 1);
            active_conv.updated_at = Set(chrono::Utc::now().into());
            active_conv.update(&self.conn).await?;
        }

        Ok(result)
    }

    /// Get messages for a conversation
    pub async fn get_messages(&self, conversation_id: Uuid) -> Result<Vec<message::Model>> {
        let results = message::Entity::find()
            .filter(message::Column::ConversationId.eq(conversation_id))
            .order_by_asc(message::Column::CreatedAt)
            .all(&self.conn)
            .await?;
        Ok(results)
    }

    /// Delete conversation and all its messages
    pub async fn delete_conversation(&self, id: Uuid) -> Result<()> {
        // Delete all messages first
        message::Entity::delete_many()
            .filter(message::Column::ConversationId.eq(id))
            .exec(&self.conn)
            .await?;

        // Delete conversation
        conversation::Entity::delete_by_id(id)
            .exec(&self.conn)
            .await?;

        Ok(())
    }

    /// Health check
    pub async fn health_check(&self) -> Result<bool> {
        // Simple query to check connection
        use sea_orm::EntityTrait;
        let result = conversation::Entity::find()
            .one(&self.conn)
            .await;

        Ok(result.is_ok())
    }
}
