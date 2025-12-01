/// Test script for new modules: Tantivy, Redis, SeaORM
/// Run with: cargo run --example test_new_modules
use anyhow::Result;

#[tokio::main]
async fn main() -> Result<()> {
    // Load environment variables
    dotenv::dotenv().ok();

    println!("=== TESTING NEW JARVIS MODULES ===\n");

    // Test 1: Redis Cache
    println!("1. Testing Redis Cache...");
    match test_redis().await {
        Ok(_) => println!("    Redis cache working!"),
        Err(e) => println!("    Redis error: {}", e),
    }
    println!();

    // Test 2: Tantivy Search
    println!("2. Testing Tantivy Full-Text Search...");
    match test_tantivy().await {
        Ok(_) => println!("    Tantivy search working!"),
        Err(e) => println!("    Tantivy error: {}", e),
    }
    println!();

    // Test 3: SeaORM Database
    println!("3. Testing SeaORM Database...");
    match test_seaorm().await {
        Ok(_) => println!("    SeaORM database working!"),
        Err(e) => println!("    SeaORM error: {}", e),
    }
    println!();

    println!("=== ALL TESTS COMPLETE ===");
    Ok(())
}

async fn test_redis() -> Result<()> {
    use jarvis_core::services::CacheClient;
    use std::time::Duration;

    let redis_url = std::env::var("REDIS_URL")
        .unwrap_or_else(|_| "redis://localhost:6379".to_string());

    let mut cache = CacheClient::new(&redis_url).await?;

    // Test health check
    let healthy = cache.health_check().await?;
    println!("   Redis health: {}", healthy);

    // Test set/get
    cache.set("test:key", &"test_value", Some(Duration::from_secs(60))).await?;
    let value: Option<String> = cache.get("test:key").await?;
    println!("   Set/Get test: {:?}", value);

    // Test counter
    let count = cache.incr("test:counter").await?;
    println!("   Counter test: {}", count);

    // Cleanup
    cache.delete("test:key").await?;
    cache.delete("test:counter").await?;

    Ok(())
}

async fn test_tantivy() -> Result<()> {
    use jarvis_core::services::SearchIndex;
    use tempfile::TempDir;

    let temp_dir = TempDir::new()?;
    let mut index = SearchIndex::new(temp_dir.path())?;

    // Index some test documents
    index.index_message(
        "conv-test-1",
        "How do I install Rust?",
        "You can install Rust using rustup from https://rustup.rs",
        "2025-01-26T12:00:00Z",
    )?;

    index.index_message(
        "conv-test-2",
        "What is Tantivy?",
        "Tantivy is a full-text search engine library written in Rust",
        "2025-01-26T12:05:00Z",
    )?;

    index.index_message(
        "conv-test-3",
        "Tell me about Redis",
        "Redis is an in-memory data structure store used as a database and cache",
        "2025-01-26T12:10:00Z",
    )?;

    // Search
    let results = index.search("Rust", 10)?;
    println!("   Search 'Rust' found {} results", results.len());
    for (i, result) in results.iter().enumerate() {
        println!("     {}. [Score: {:.2}] {}", i + 1, result.score, result.user_message);
    }

    // Get stats
    let stats = index.stats()?;
    println!("   Index stats: {} documents, {} bytes", stats.num_documents, stats.index_size_bytes);

    Ok(())
}

async fn test_seaorm() -> Result<()> {
    use jarvis_core::services::DbService;

    let database_url = std::env::var("DATABASE_URL")
        .unwrap_or_else(|_| "postgresql://jarvis:password@localhost:5432/jarvis_db".to_string());

    println!("   Connecting to: {}", database_url.split('@').last().unwrap_or("database"));

    let db = DbService::new(&database_url).await?;

    // Test health check
    let healthy = db.health_check().await?;
    println!("   Database health: {}", healthy);

    // Note: Actual CRUD operations would require migrations to be run first
    // For now, just test connectivity

    Ok(())
}
