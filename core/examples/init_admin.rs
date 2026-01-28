// ============================================================================
// Admin User Initialization
// ============================================================================
// Creates the initial admin user with a secure random password
// Password is hashed with bcrypt and stored in PostgreSQL
// Plaintext password is stored in jarvis-secretsd for secure retrieval
//
// Usage: cargo run --example init_admin
// ============================================================================

use rand::Rng;
use sqlx::postgres::PgPoolOptions;
use std::io::{self, Write};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("🔐 Jarvis Admin User Initialization");
    println!("====================================");
    println!();

    // Load environment variables
    dotenvy::dotenv().ok();

    let database_url = std::env::var("DATABASE_URL")
        .expect("DATABASE_URL must be set (load from jarvis-secretsd or .env)");

    let secretsd_url = std::env::var("SECRETSD_URL")
        .unwrap_or_else(|_| "http://localhost:8081".to_string());

    let admin_username = std::env::var("ADMIN_USERNAME")
        .unwrap_or_else(|_| "admin".to_string());

    // Connect to database
    println!("📡 Connecting to PostgreSQL database...");
    let db_pool = PgPoolOptions::new()
        .max_connections(5)
        .connect(&database_url)
        .await?;

    println!("✅ Database connection established");
    println!();

    // Check if admin user already exists
    println!("🔍 Checking if admin user already exists...");
    let user_exists: Option<(String,)> = sqlx::query_as(
        "SELECT username FROM users WHERE username = $1"
    )
    .bind(&admin_username)
    .fetch_optional(&db_pool)
    .await?;

    if let Some(_) = user_exists {
        println!("⚠️  WARNING: Admin user '{}' already exists!", admin_username);
        println!();
        print!("Do you want to reset the password? (yes/no): ");
        io::stdout().flush()?;

        let mut input = String::new();
        io::stdin().read_line(&mut input)?;

        if input.trim().to_lowercase() != "yes" {
            println!("❌ Aborted by user");
            return Ok(());
        }

        println!();
    }

    // Generate secure random password (32 characters)
    println!("📝 Generating secure random password...");
    let admin_password = generate_secure_password(32);
    println!("✅ Password generated: {}****************************", &admin_password[..4]);
    println!();

    // Hash password with bcrypt
    println!("🔒 Hashing password with bcrypt (cost=12)...");
    let password_hash = bcrypt::hash(&admin_password, 12)?;
    println!("✅ Password hashed successfully");
    println!();

    // Create or update admin user
    if user_exists.is_some() {
        println!("🔄 Resetting password for admin user...");
        sqlx::query(
            "UPDATE users
             SET password_hash = $1,
                 updated_at = CURRENT_TIMESTAMP,
                 is_active = true,
                 is_admin = true
             WHERE username = $2"
        )
        .bind(&password_hash)
        .bind(&admin_username)
        .execute(&db_pool)
        .await?;

        println!("✅ Admin password reset successfully");
    } else {
        println!("📝 Creating admin user in database...");
        sqlx::query(
            "INSERT INTO users (username, password_hash, email, full_name, is_active, is_admin)
             VALUES ($1, $2, $3, $4, true, true)"
        )
        .bind(&admin_username)
        .bind(&password_hash)
        .bind("admin@jarvis.local")
        .bind("Jarvis Administrator")
        .execute(&db_pool)
        .await?;

        println!("✅ Admin user created successfully");
    }

    println!();

    // Store password in jarvis-secretsd
    println!("🔐 Storing admin password in jarvis-secretsd...");
    let client = reqwest::Client::new();
    let response = client
        .post(format!("{}/secret", secretsd_url))
        .header("X-Jarvis-Client", "admin")
        .header("Content-Type", "application/json")
        .json(&serde_json::json!({
            "name": "admin_password",
            "value": admin_password
        }))
        .send()
        .await;

    match response {
        Ok(resp) => {
            if resp.status().is_success() {
                println!("✅ Admin password stored in jarvis-secretsd");
            } else {
                let status = resp.status();
                let error = resp.text().await.unwrap_or_else(|_| "Unknown error".to_string());
                println!("⚠️  WARNING: Failed to store password in jarvis-secretsd");
                println!("   Status: {}", status);
                println!("   Error: {}", error);
            }
        }
        Err(e) => {
            println!("⚠️  WARNING: Failed to connect to jarvis-secretsd: {}", e);
            println!("   Make sure jarvis-secretsd is running at {}", secretsd_url);
        }
    }

    println!();
    println!("============================================");
    println!("✅ Admin User Initialization Complete!");
    println!("============================================");
    println!();
    println!("Username: {}", admin_username);
    println!("Password: {}", admin_password);
    println!();
    println!("⚠️  IMPORTANT: Save this password securely!");
    println!("   This is the only time it will be displayed in plaintext.");
    println!("   The password is also stored in jarvis-secretsd under 'admin_password'");
    println!();
    println!("You can retrieve it later with:");
    println!("  curl -H \"X-Jarvis-Client: admin\" {}/secret/admin_password", secretsd_url);
    println!();

    Ok(())
}

/// Generate a cryptographically secure random password
fn generate_secure_password(length: usize) -> String {
    const CHARSET: &[u8] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZ\
                            abcdefghijklmnopqrstuvwxyz\
                            0123456789\
                            !@#$%^&*-_=+";

    let mut rng = rand::thread_rng();

    (0..length)
        .map(|_| {
            let idx = rng.gen_range(0..CHARSET.len());
            CHARSET[idx] as char
        })
        .collect()
}
