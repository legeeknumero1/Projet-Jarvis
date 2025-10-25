/// Cache Service - Redis caching layer
use redis::aio::ConnectionManager;
use redis::AsyncCommands;
use tracing::{info, debug};
use std::time::Duration;

use crate::error::{DbError, DbResult};

pub struct CacheService {
    client: ConnectionManager,
}

impl CacheService {
    /// Créer nouvelle connexion Redis
    pub async fn new(redis_url: &str) -> DbResult<Self> {
        info!("🔴 Connecting to Redis: {}", redis_url);

        let client = redis::Client::open(redis_url)
            .map_err(|e| DbError::Cache(e.to_string()))?;

        let connection_manager = ConnectionManager::new(client)
            .await
            .map_err(|e| DbError::Cache(e.to_string()))?;

        info!("✅ Redis connected");

        Ok(Self {
            client: connection_manager,
        })
    }

    /// Vérifier la santé de la connexion
    pub async fn health_check(&self) -> DbResult<bool> {
        let mut conn = self.client.clone();
        redis::cmd("PING")
            .query_async::<_, String>(&mut conn)
            .await
            .map(|_| true)
            .map_err(|e| DbError::Cache(e.to_string()))
    }

    // ========== GET/SET ==========

    /// Récupérer value depuis cache
    pub async fn get<T: serde::de::DeserializeOwned>(&self, key: &str) -> DbResult<Option<T>> {
        debug!("Cache GET: {}", key);

        let mut conn = self.client.clone();
        let value: Option<String> = conn
            .get(key)
            .await
            .map_err(|e| DbError::Cache(e.to_string()))?;

        Ok(value.and_then(|v| serde_json::from_str(&v).ok()))
    }

    /// Stocker value dans le cache
    pub async fn set<T: serde::Serialize>(
        &self,
        key: &str,
        value: &T,
        ttl_secs: Option<u64>,
    ) -> DbResult<()> {
        debug!("Cache SET: {} (TTL: {:?})", key, ttl_secs);

        let json = serde_json::to_string(value)
            .map_err(|e| DbError::Cache(e.to_string()))?;

        let mut conn = self.client.clone();

        if let Some(ttl) = ttl_secs {
            redis::cmd("SETEX")
                .arg(key)
                .arg(ttl)
                .arg(json)
                .query_async::<_, ()>(&mut conn)
                .await
                .map_err(|e| DbError::Cache(e.to_string()))?;
        } else {
            conn.set::<_, _, ()>(key, json)
                .await
                .map_err(|e| DbError::Cache(e.to_string()))?;
        }

        Ok(())
    }

    /// Supprimer key du cache
    pub async fn delete(&self, key: &str) -> DbResult<()> {
        debug!("Cache DELETE: {}", key);

        let mut conn = self.client.clone();
        conn.del(key)
            .await
            .map_err(|e| DbError::Cache(e.to_string()))
    }

    /// Invalider un pattern (ex: "user:123:*")
    pub async fn invalidate_pattern(&self, pattern: &str) -> DbResult<usize> {
        debug!("Cache INVALIDATE: {}", pattern);

        let mut conn = self.client.clone();
        let keys: Vec<String> = conn
            .keys(pattern)
            .await
            .map_err(|e| DbError::Cache(e.to_string()))?;

        if keys.is_empty() {
            return Ok(0);
        }

        let count: usize = conn
            .del(keys)
            .await
            .map_err(|e| DbError::Cache(e.to_string()))?;

        info!("✅ Invalidated {} keys matching pattern: {}", count, pattern);
        Ok(count)
    }

    // ========== CACHE HELPERS ==========

    /// Cache avec fallback à fonction async
    pub async fn get_or_set<T, F>(
        &self,
        key: &str,
        ttl_secs: u64,
        fetch_fn: F,
    ) -> DbResult<T>
    where
        T: serde::Serialize + serde::de::DeserializeOwned,
        F: std::future::Future<Output = DbResult<T>>,
    {
        // Essayer de récupérer du cache
        if let Some(cached) = self.get::<T>(key).await? {
            debug!("Cache HIT: {}", key);
            return Ok(cached);
        }

        // Récupérer depuis la source
        debug!("Cache MISS: {}", key);
        let value = fetch_fn.await?;

        // Stocker dans le cache
        self.set(key, &value, Some(ttl_secs)).await?;

        Ok(value)
    }

    /// Incrémenter counter Redis
    pub async fn increment(&self, key: &str, amount: i32) -> DbResult<i64> {
        let mut conn = self.client.clone();
        redis::cmd("INCRBY")
            .arg(key)
            .arg(amount)
            .query_async::<_, i64>(&mut conn)
            .await
            .map_err(|e| DbError::Cache(e.to_string()))
    }

    /// Ajouter à set Redis
    pub async fn sadd(&self, key: &str, member: &str) -> DbResult<()> {
        let mut conn = self.client.clone();
        redis::cmd("SADD")
            .arg(key)
            .arg(member)
            .query_async::<_, ()>(&mut conn)
            .await
            .map_err(|e| DbError::Cache(e.to_string()))
    }

    /// Récupérer set Redis
    pub async fn smembers(&self, key: &str) -> DbResult<Vec<String>> {
        let mut conn = self.client.clone();
        conn.smembers(key)
            .await
            .map_err(|e| DbError::Cache(e.to_string()))
    }

    /// TTL d'une key
    pub async fn ttl(&self, key: &str) -> DbResult<Option<Duration>> {
        let mut conn = self.client.clone();
        let ttl: i64 = conn
            .ttl(key)
            .await
            .map_err(|e| DbError::Cache(e.to_string()))?;

        Ok(if ttl > 0 {
            Some(Duration::from_secs(ttl as u64))
        } else {
            None
        })
    }

    /// Flush all keys (développement uniquement!)
    pub async fn flush_all(&self) -> DbResult<()> {
        let mut conn = self.client.clone();
        redis::cmd("FLUSHALL")
            .query_async::<_, ()>(&mut conn)
            .await
            .map_err(|e| DbError::Cache(e.to_string()))
    }
}
