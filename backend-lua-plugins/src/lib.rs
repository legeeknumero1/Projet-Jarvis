/// Jarvis Lua Plugins - Phase 8
/// Système de plugins embarqués avec sandbox Lua

pub mod plugin_manager;
pub mod sandbox;
pub mod error;
pub mod api;

pub use plugin_manager::PluginManager;
pub use sandbox::LuaSandbox;
pub use error::{PluginError, PluginResult};
pub use api::PluginAPI;

use std::sync::Arc;
use tracing::info;

/// Service container for Lua plugins
pub struct PluginServices {
    pub manager: Arc<PluginManager>,
    pub sandbox: Arc<LuaSandbox>,
}

impl PluginServices {
    pub async fn new(plugins_dir: &str) -> PluginResult<Self> {
        info!("🧩 Initializing Lua Plugin System");

        let sandbox = Arc::new(LuaSandbox::new().await?);
        let manager = Arc::new(PluginManager::new(plugins_dir).await?);

        info!("✅ Plugin System initialized with {} plugins", manager.list_plugins().len());

        Ok(PluginServices { manager, sandbox })
    }

    pub async fn health_check(&self) -> PluginResult<bool> {
        Ok(self.manager.health_check().await? && self.sandbox.health_check().await?)
    }

    pub async fn load_plugins(&self) -> PluginResult<()> {
        for plugin in self.manager.list_plugins() {
            self.sandbox.load_plugin(&plugin).await?;
        }
        Ok(())
    }
}
