/// Jarvis DB Layer - Phase 4
/// Couche base de données type-safe avec sqlx + tantivy + Redis
///
/// Modules:
/// - models: Structures de données
/// - database: PostgreSQL avec sqlx
/// - search: Full-text search avec tantivy
/// - cache: Redis caching layer

pub mod models;
pub mod database;
pub mod search;
pub mod cache;
pub mod error;

pub use database::DatabaseService;
pub use search::SearchService;
pub use cache::CacheService;
pub use error::{DbError, DbResult};

use std::sync::Arc;

/// Service container for DB layer
pub struct DbServices {
    pub database: Arc<DatabaseService>,
    pub search: Arc<SearchService>,
    pub cache: Arc<CacheService>,
}

impl DbServices {
    pub async fn new(
        database_url: &str,
        redis_url: &str,
    ) -> DbResult<Self> {
        let database = Arc::new(DatabaseService::new(database_url).await?);
        let cache = Arc::new(CacheService::new(redis_url).await?);
        let search = Arc::new(SearchService::new().await?);

        Ok(DbServices {
            database,
            search,
            cache,
        })
    }

    pub async fn health_check(&self) -> DbResult<bool> {
        Ok(
            self.database.health_check().await? &&
            self.cache.health_check().await? &&
            self.search.health_check().await?
        )
    }
}
