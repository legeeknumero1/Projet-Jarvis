use anyhow::{Context, Result};
use clap::{Parser, Subcommand};
use serde::{Deserialize, Serialize};
use tabled::{Table, Tabled};

const DEFAULT_URL: &str = "http://127.0.0.1:8081";

#[derive(Parser)]
#[command(name = "jarvis-secrets")]
#[command(about = "CLI tool for managing jarvis-secretsd secrets", long_about = None)]
struct Cli {
    #[arg(short, long, default_value = DEFAULT_URL)]
    url: String,

    #[arg(short, long, default_value = "admin")]
    client: String,

    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// List all secrets
    List,

    /// Get a secret value
    Get {
        /// Secret name
        name: String,
    },

    /// Create or update a secret
    Set {
        /// Secret name
        name: String,

        /// Secret value (if not provided, reads from stdin)
        #[arg(short, long)]
        value: Option<String>,
    },

    /// Rotate a secret
    Rotate {
        /// Secret name(s) to rotate
        names: Vec<String>,
    },

    /// Show health status
    Health,

    /// Show Prometheus metrics
    Metrics,
}

#[derive(Deserialize)]
struct HealthResponse {
    status: String,
    version: String,
    uptime_secs: u64,
    secrets_count: usize,
}

#[derive(Deserialize, Tabled)]
struct SecretMetadata {
    name: String,
    kid: String,
    #[tabled(display_with = "display_iso_date")]
    created_at: String,
    #[tabled(display_with = "display_opt_iso_date")]
    expires_at: Option<String>,
    is_expired: bool,
}

#[derive(Deserialize)]
struct ListResponse {
    secrets: Vec<SecretMetadata>,
}

#[derive(Deserialize)]
struct GetSecretResponse {
    name: String,
    value: String,
    kid: String,
    expires_at: Option<String>,
}

#[derive(Serialize)]
struct CreateSecretRequest {
    name: String,
    value: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    metadata: Option<serde_json::Value>,
}

#[derive(Serialize)]
struct RotateRequest {
    names: Vec<String>,
}

#[derive(Deserialize)]
struct RotateResponse {
    rotated_count: usize,
    rotated: Vec<String>,
}

fn display_iso_date(date: &String) -> String {
    date.chars().take(19).collect()
}

fn display_opt_iso_date(date: &Option<String>) -> String {
    date.as_ref()
        .map(|d| d.chars().take(19).collect())
        .unwrap_or_else(|| "N/A".to_string())
}

fn main() -> Result<()> {
    let cli = Cli::parse();

    let client = reqwest::blocking::Client::new();

    match cli.command {
        Commands::List => {
            let url = format!("{}/secrets", cli.url);
            let response = client
                .get(&url)
                .header("X-Jarvis-Client", &cli.client)
                .send()
                .context("Failed to send request")?;

            if !response.status().is_success() {
                anyhow::bail!("Request failed: {}", response.status());
            }

            let list: ListResponse = response.json().context("Failed to parse response")?;

            if list.secrets.is_empty() {
                println!("No secrets found");
            } else {
                let table = Table::new(list.secrets);
                println!("{}", table);
            }
        }

        Commands::Get { name } => {
            let url = format!("{}/secret/{}", cli.url, name);
            let response = client
                .get(&url)
                .header("X-Jarvis-Client", &cli.client)
                .send()
                .context("Failed to send request")?;

            if !response.status().is_success() {
                anyhow::bail!("Request failed: {}", response.status());
            }

            let secret: GetSecretResponse = response.json().context("Failed to parse response")?;

            println!("Name: {}", secret.name);
            println!("Value: {}", secret.value);
            println!("KID: {}", secret.kid);
            if let Some(exp) = secret.expires_at {
                println!("Expires: {}", exp);
            }
        }

        Commands::Set { name, value } => {
            let secret_value = match value {
                Some(v) => v,
                None => {
                    use std::io::Read;
                    let mut buffer = String::new();
                    std::io::stdin()
                        .read_to_string(&mut buffer)
                        .context("Failed to read from stdin")?;
                    buffer.trim().to_string()
                }
            };

            let url = format!("{}/secret", cli.url);
            let request = CreateSecretRequest {
                name: name.clone(),
                value: secret_value,
                metadata: None,
            };

            let response = client
                .post(&url)
                .header("X-Jarvis-Client", &cli.client)
                .header("Content-Type", "application/json")
                .json(&request)
                .send()
                .context("Failed to send request")?;

            if !response.status().is_success() {
                anyhow::bail!("Request failed: {}", response.status());
            }

            println!("✓ Secret '{}' created/updated successfully", name);
        }

        Commands::Rotate { names } => {
            let url = format!("{}/rotate", cli.url);
            let request = RotateRequest { names: names.clone() };

            let response = client
                .post(&url)
                .header("X-Jarvis-Client", &cli.client)
                .header("Content-Type", "application/json")
                .json(&request)
                .send()
                .context("Failed to send request")?;

            if !response.status().is_success() {
                anyhow::bail!("Request failed: {}", response.status());
            }

            let result: RotateResponse = response.json().context("Failed to parse response")?;

            println!("✓ Rotated {} secret(s):", result.rotated_count);
            for name in result.rotated {
                println!("  - {}", name);
            }
        }

        Commands::Health => {
            let url = format!("{}/healthz", cli.url);
            let response = client
                .get(&url)
                .send()
                .context("Failed to send request")?;

            if !response.status().is_success() {
                anyhow::bail!("Request failed: {}", response.status());
            }

            let health: HealthResponse = response.json().context("Failed to parse response")?;

            println!("Status: {}", health.status);
            println!("Version: {}", health.version);
            println!("Uptime: {} seconds", health.uptime_secs);
            println!("Secrets: {}", health.secrets_count);
        }

        Commands::Metrics => {
            let url = format!("{}/metrics", cli.url);
            let response = client
                .get(&url)
                .send()
                .context("Failed to send request")?;

            if !response.status().is_success() {
                anyhow::bail!("Request failed: {}", response.status());
            }

            let metrics = response.text().context("Failed to read response")?;
            println!("{}", metrics);
        }
    }

    Ok(())
}
