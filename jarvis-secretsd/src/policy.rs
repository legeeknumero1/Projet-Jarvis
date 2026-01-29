use serde::Deserialize;
use std::collections::HashMap;
use std::fs;
use anyhow::{Context, Result};
use tracing::info;

#[derive(Debug, Deserialize, Clone, PartialEq)]
#[serde(rename_all = "lowercase")]
pub enum Permission {
    Read,
    Write,
    Rotate,
    List,
    Delete,
    Admin,
}

#[derive(Debug, Deserialize, Clone)]
pub struct ClientRule {
    pub allow: Vec<String>, // Pattern de secrets (ex: "jwt_*", "postgres_password")
    pub permissions: Vec<Permission>,
}

#[derive(Debug, Deserialize, Clone)]
pub struct Policy {
    pub clients: HashMap<String, ClientRule>,
    pub default_deny: bool,
}

impl Policy {
    pub fn load(path: &str) -> Result<Self> {
        let content = fs::read_to_string(path)
            .with_context(|| format!("failed to read policy file at {}", path))?;
        let policy: Policy = serde_yaml::from_str(&content)
            .context("failed to parse policy YAML")?;
        
        info!(" Policy loaded: {} clients defined", policy.clients.len());
        Ok(policy)
    }

    /// Check if a client is allowed to perform an action on a secret
    pub fn is_authorized(&self, client_id: &str, secret_name: &str, action: Permission) -> bool {
        let rule = match self.clients.get(client_id) {
            Some(r) => r,
            None => return !self.default_deny,
        };

        // Admin has all permissions on all secrets
        if rule.permissions.contains(&Permission::Admin) {
            return true;
        }

        // Check if action is allowed for this client
        if !rule.permissions.contains(&action) {
            return false;
        }

        // Check secret name match (simple wildcard support)
        for pattern in &rule.allow {
            if pattern == "*" {
                return true;
            }
            if pattern.ends_with('*') {
                let prefix = &pattern[..pattern.len() - 1];
                if secret_name.starts_with(prefix) {
                    return true;
                }
            }
            if pattern == secret_name {
                return true;
            }
        }

        false
    }
}