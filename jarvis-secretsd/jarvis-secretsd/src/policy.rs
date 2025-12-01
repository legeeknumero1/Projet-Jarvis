use anyhow::{Context, Result};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs;
use std::path::Path;
use tracing::{info, warn};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Policy {
    #[serde(default)]
    pub clients: HashMap<String, ClientPolicy>,

    #[serde(default = "default_true")]
    pub default_deny: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ClientPolicy {
    #[serde(default)]
    pub allow: Vec<String>,

    #[serde(default)]
    pub deny: Vec<String>,
}

fn default_true() -> bool {
    true
}

impl Policy {
    /// Load policy from YAML file
    pub fn load(path: &str) -> Result<Self> {
        if !Path::new(path).exists() {
            warn!("  Policy file not found: {}, using default-deny", path);
            return Ok(Policy::default_deny());
        }

        let content = fs::read_to_string(path)
            .with_context(|| format!("failed to read policy file: {}", path))?;

        let policy: Policy = serde_yaml::from_str(&content)
            .with_context(|| format!("failed to parse policy YAML: {}", path))?;

        info!(" Loaded policy with {} client rules", policy.clients.len());

        Ok(policy)
    }

    /// Create default-deny policy
    pub fn default_deny() -> Self {
        Self {
            clients: HashMap::new(),
            default_deny: true,
        }
    }

    /// Check if client is allowed to access secret
    pub fn allowed(&self, client: &str, secret: &str) -> bool {
        if let Some(client_policy) = self.clients.get(client) {
            // Check deny list first (takes precedence)
            if client_policy.deny.contains(&secret.to_string()) {
                return false;
            }

            // Check allow list
            if client_policy.allow.contains(&secret.to_string()) {
                return true;
            }

            // Check wildcards
            if client_policy.allow.iter().any(|pattern| matches_pattern(pattern, secret)) {
                return true;
            }
        }

        // Default behavior
        !self.default_deny
    }

    /// List all secrets a client can access
    pub fn allowed_secrets(&self, client: &str) -> Vec<String> {
        if let Some(client_policy) = self.clients.get(client) {
            client_policy.allow.clone()
        } else {
            Vec::new()
        }
    }
}

/// Simple wildcard pattern matching (* only)
fn matches_pattern(pattern: &str, value: &str) -> bool {
    if pattern == "*" {
        return true;
    }

    if pattern.ends_with('*') {
        let prefix = &pattern[..pattern.len() - 1];
        return value.starts_with(prefix);
    }

    if pattern.starts_with('*') {
        let suffix = &pattern[1..];
        return value.ends_with(suffix);
    }

    pattern == value
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_default_deny() {
        let policy = Policy::default_deny();
        assert!(policy.default_deny);
        assert!(!policy.allowed("backend", "jwt_key"));
    }

    #[test]
    fn test_allow_list() {
        let mut policy = Policy::default_deny();
        let mut client = ClientPolicy {
            allow: vec!["jwt_key".to_string(), "api_key".to_string()],
            deny: Vec::new(),
        };

        policy.clients.insert("backend".to_string(), client);

        assert!(policy.allowed("backend", "jwt_key"));
        assert!(policy.allowed("backend", "api_key"));
        assert!(!policy.allowed("backend", "postgres_password"));
        assert!(!policy.allowed("stt", "jwt_key")); // Different client
    }

    #[test]
    fn test_deny_precedence() {
        let mut policy = Policy::default_deny();
        let client = ClientPolicy {
            allow: vec!["*".to_string()], // Allow all
            deny: vec!["secret_key".to_string()], // Except this
        };

        policy.clients.insert("backend".to_string(), client);

        assert!(policy.allowed("backend", "jwt_key"));
        assert!(!policy.allowed("backend", "secret_key")); // Denied
    }

    #[test]
    fn test_wildcard_matching() {
        assert!(matches_pattern("*", "anything"));
        assert!(matches_pattern("jwt_*", "jwt_key"));
        assert!(matches_pattern("jwt_*", "jwt_signing_key"));
        assert!(!matches_pattern("jwt_*", "api_key"));

        assert!(matches_pattern("*_password", "postgres_password"));
        assert!(matches_pattern("*_password", "redis_password"));
        assert!(!matches_pattern("*_password", "api_key"));
    }
}
