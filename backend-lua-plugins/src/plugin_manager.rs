/// Plugin Manager - Gestion du cycle de vie des plugins
use std::collections::HashMap;
use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};
use tracing::{info, debug};
use walkdir::WalkDir;
use std::path::Path;

use crate::error::{PluginError, PluginResult};

/// Plugin metadata
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PluginMetadata {
    pub id: String,
    pub name: String,
    pub version: String,
    pub author: String,
    pub description: String,
    pub enabled: bool,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

/// Plugin descriptor
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Plugin {
    pub metadata: PluginMetadata,
    pub path: String,
    pub hooks: Vec<String>,  // "on_chat", "on_command", etc
}

/// Plugin Manager
pub struct PluginManager {
    plugins_dir: String,
    plugins: HashMap<String, Plugin>,
}

impl PluginManager {
    /// Create new plugin manager
    pub async fn new(plugins_dir: &str) -> PluginResult<Self> {
        info!(" Loading plugins from: {}", plugins_dir);

        let mut plugins = HashMap::new();
        let mut manager = Self {
            plugins_dir: plugins_dir.to_string(),
            plugins,
        };

        manager.discover_plugins().await?;
        Ok(manager)
    }

    /// Discover plugins in directory
    async fn discover_plugins(&mut self) -> PluginResult<()> {
        let path = Path::new(&self.plugins_dir);

        if !path.exists() {
            debug!("Plugins directory does not exist, creating...");
            std::fs::create_dir_all(path)?;
            return Ok(());
        }

        for entry in WalkDir::new(path)
            .into_iter()
            .filter_map(|e| e.ok())
            .filter(|e| e.path().extension().map_or(false, |ext| ext == "lua"))
        {
            if let Ok(metadata) = self.load_plugin_metadata(entry.path()).await {
                let plugin = Plugin {
                    metadata: metadata.clone(),
                    path: entry.path().to_string_lossy().to_string(),
                    hooks: self.extract_hooks(entry.path()).await?,
                };

                self.plugins.insert(metadata.id, plugin);
                info!(" Discovered plugin: {}", metadata.name);
            }
        }

        Ok(())
    }

    /// Load plugin metadata from file
    async fn load_plugin_metadata(&self, path: &Path) -> PluginResult<PluginMetadata> {
        let content = tokio::fs::read_to_string(path).await?;

        // Parse Lua comments for metadata
        // Format: -- @id plugin_id
        //         -- @name Plugin Name
        //         -- @version 1.0.0
        //         -- @author Author Name
        //         -- @description Plugin description

        let mut id = String::new();
        let mut name = String::new();
        let mut version = String::new();
        let mut author = String::new();
        let mut description = String::new();

        for line in content.lines() {
            if let Some(rest) = line.strip_prefix("-- @id") {
                id = rest.trim().to_string();
            } else if let Some(rest) = line.strip_prefix("-- @name") {
                name = rest.trim().to_string();
            } else if let Some(rest) = line.strip_prefix("-- @version") {
                version = rest.trim().to_string();
            } else if let Some(rest) = line.strip_prefix("-- @author") {
                author = rest.trim().to_string();
            } else if let Some(rest) = line.strip_prefix("-- @description") {
                description = rest.trim().to_string();
            }
        }

        if id.is_empty() {
            return Err(PluginError::InvalidPlugin("Missing @id".to_string()));
        }

        Ok(PluginMetadata {
            id,
            name,
            version,
            author,
            description,
            enabled: true,
            created_at: Utc::now(),
            updated_at: Utc::now(),
        })
    }

    /// Extract hook names from plugin
    async fn extract_hooks(&self, path: &Path) -> PluginResult<Vec<String>> {
        let content = tokio::fs::read_to_string(path).await?;

        let mut hooks = Vec::new();

        // Look for function definitions: function on_chat(), function on_command(), etc
        for line in content.lines() {
            if let Some(name) = line.strip_prefix("function ").and_then(|s| s.split('(').next()) {
                if name.starts_with("on_") {
                    hooks.push(name.trim().to_string());
                }
            }
        }

        Ok(hooks)
    }

    /// Get all plugins
    pub fn list_plugins(&self) -> Vec<Plugin> {
        self.plugins.values().cloned().collect()
    }

    /// Get specific plugin
    pub fn get_plugin(&self, id: &str) -> Option<Plugin> {
        self.plugins.get(id).cloned()
    }

    /// Enable/disable plugin
    pub fn set_enabled(&mut self, id: &str, enabled: bool) -> PluginResult<()> {
        if let Some(plugin) = self.plugins.get_mut(id) {
            plugin.metadata.enabled = enabled;
            plugin.metadata.updated_at = Utc::now();
            info!("Plugin {} {}", id, if enabled { "enabled" } else { "disabled" });
            Ok(())
        } else {
            Err(PluginError::NotFound(id.to_string()))
        }
    }

    /// Unload plugin
    pub fn unload(&mut self, id: &str) -> PluginResult<()> {
        if self.plugins.remove(id).is_some() {
            info!("Plugin unloaded: {}", id);
            Ok(())
        } else {
            Err(PluginError::NotFound(id.to_string()))
        }
    }

    /// Health check
    pub async fn health_check(&self) -> PluginResult<bool> {
        Ok(self.plugins.len() > 0 || std::path::Path::new(&self.plugins_dir).exists())
    }

    /// Get plugin count
    pub fn count(&self) -> usize {
        self.plugins.len()
    }

    /// Get plugins by hook
    pub fn get_plugins_by_hook(&self, hook_name: &str) -> Vec<Plugin> {
        self.plugins
            .values()
            .filter(|p| p.metadata.enabled && p.hooks.contains(&hook_name.to_string()))
            .cloned()
            .collect()
    }
}
