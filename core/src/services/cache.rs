/// Distributed Cache using Redis
/// High-performance caching for conversation context, LLM responses, etc.
use anyhow::Result;
use redis::aio::ConnectionManager;
use redis::{AsyncCommands, Client};
use serde::{Deserialize, Serialize};
use std::time::Duration;
use tracing::{info, warn};

/// Redis cache client
pub struct CacheClient {
    manager: ConnectionManager,
}

impl CacheClient {
    /// Connect to Redis server
    pub async fn new(redis_url: &str) -> Result<Self> {
        info!("Connecting to Redis at {}", redis_url);

        let client = Client::open(redis_url)?;
        let manager = ConnectionManager::new(client).await?;

        info!("Redis connection established");

        Ok(Self { manager })
    }

    /// Set key-value with optional TTL
    pub async fn set<V: Serialize>(
        &mut self,
        key: &str,
        value: &V,
        ttl: Option<Duration>,
    ) -> Result<()> {
        let serialized = serde_json::to_string(value)?;

        match ttl {
            Some(duration) => {
                self.manager
                    .set_ex::<_, _, ()>(key, serialized, duration.as_secs())
                    .await?;
            }
            None => {
                self.manager.set::<_, _, ()>(key, serialized).await?;
            }
        }

        Ok(())
    }

    /// Get value by key
    pub async fn get<V: for<'de> Deserialize<'de>>(&mut self, key: &str) -> Result<Option<V>> {
        let value: Option<String> = self.manager.get(key).await?;

        match value {
            Some(serialized) => {
                let deserialized = serde_json::from_str(&serialized)?;
                Ok(Some(deserialized))
            }
            None => Ok(None),
        }
    }

    /// Delete key
    pub async fn delete(&mut self, key: &str) -> Result<()> {
        self.manager.del::<_, ()>(key).await?;
        Ok(())
    }

    /// Check if key exists
    pub async fn exists(&mut self, key: &str) -> Result<bool> {
        let exists: bool = self.manager.exists(key).await?;
        Ok(exists)
    }

    /// Set expiration on existing key
    pub async fn expire(&mut self, key: &str, ttl: Duration) -> Result<()> {
        self.manager.expire::<_, ()>(key, ttl.as_secs() as i64).await?;
        Ok(())
    }

    /// Increment counter
    pub async fn incr(&mut self, key: &str) -> Result<i64> {
        let value: i64 = self.manager.incr(key, 1).await?;
        Ok(value)
    }

    /// Get multiple keys
    pub async fn mget<V: for<'de> Deserialize<'de>>(
        &mut self,
        keys: &[&str],
    ) -> Result<Vec<Option<V>>> {
        let values: Vec<Option<String>> = self.manager.get(keys).await?;

        let mut results = Vec::new();
        for value in values {
            match value {
                Some(serialized) => {
                    let deserialized = serde_json::from_str(&serialized)?;
                    results.push(Some(deserialized));
                }
                None => results.push(None),
            }
        }

        Ok(results)
    }

    /// Flush all keys (use with caution!)
    pub async fn flush_all(&mut self) -> Result<()> {
        warn!("Flushing all Redis keys");
        redis::cmd("FLUSHALL").query_async::<_, ()>(&mut self.manager).await?;
        Ok(())
    }

    /// Health check
    pub async fn health_check(&mut self) -> Result<bool> {
        let pong: String = redis::cmd("PING").query_async(&mut self.manager).await?;
        Ok(pong == "PONG")
    }
}

/// Cache key builders for consistent naming
pub mod keys {
    use uuid::Uuid;

    pub fn conversation(id: &Uuid) -> String {
        format!("jarvis:conv:{}", id)
    }

    pub fn user_session(user_id: &str) -> String {
        format!("jarvis:session:{}", user_id)
    }

    pub fn llm_response(prompt_hash: &str) -> String {
        format!("jarvis:llm:{}", prompt_hash)
    }

    pub fn rate_limit(ip: &str) -> String {
        format!("jarvis:ratelimit:{}", ip)
    }

    pub fn search_cache(query_hash: &str) -> String {
        format!("jarvis:search:{}", query_hash)
    }
}

/// Cached conversation context
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConversationContext {
    pub conversation_id: String,
    pub user_id: String,
    pub messages: Vec<CachedMessage>,
    pub created_at: chrono::DateTime<chrono::Utc>,
    pub updated_at: chrono::DateTime<chrono::Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CachedMessage {
    pub role: String,
    pub content: String,
    pub timestamp: chrono::DateTime<chrono::Utc>,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    #[ignore] // Requires running Redis instance
    async fn test_cache_operations() {
        let mut cache = CacheClient::new("redis://127.0.0.1:6379").await.unwrap();

        // Set/Get
        cache.set("test:key", &"test_value", None).await.unwrap();
        let value: Option<String> = cache.get("test:key").await.unwrap();
        assert_eq!(value, Some("test_value".to_string()));

        // Exists
        assert!(cache.exists("test:key").await.unwrap());

        // Delete
        cache.delete("test:key").await.unwrap();
        assert!(!cache.exists("test:key").await.unwrap());

        // Health check
        assert!(cache.health_check().await.unwrap());
    }
}
