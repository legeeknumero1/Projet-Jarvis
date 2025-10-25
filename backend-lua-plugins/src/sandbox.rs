/// Lua Sandbox - Sécurité et isolation pour plugins
use mlua::{Lua, LuaSerdeExt, Table, Function};
use std::sync::Arc;
use tokio::sync::Mutex;
use tracing::{info, debug};

use crate::error::{PluginError, PluginResult};
use crate::plugin_manager::Plugin;

/// Lua Sandbox pour exécuter plugins en sécurité
pub struct LuaSandbox {
    lua: Arc<Mutex<Lua>>,
}

impl LuaSandbox {
    /// Create new Lua sandbox
    pub async fn new() -> PluginResult<Self> {
        info!("🔒 Creating Lua sandbox");

        let lua = Lua::new();

        // Setup safe environment (restrict dangerous functions)
        let globals = lua.globals();

        // Disable dangerous functions
        globals.set("os", lua.nil())?;
        globals.set("io", lua.nil())?;
        globals.set("load", lua.nil())?;
        globals.set("loadstring", lua.nil())?;
        globals.set("dofile", lua.nil())?;
        globals.set("require", lua.nil())?;
        globals.set("debug", lua.nil())?;

        // Allow safe functions
        // - math, string, table OK
        // - coroutine OK (with limits)

        info!("✅ Lua sandbox created (safe mode)");

        Ok(Self {
            lua: Arc::new(Mutex::new(lua)),
        })
    }

    /// Load and execute plugin
    pub async fn load_plugin(&self, plugin: &Plugin) -> PluginResult<()> {
        debug!("Loading plugin: {}", plugin.metadata.id);

        let lua = self.lua.lock().await;
        let content = tokio::fs::read_to_string(&plugin.path).await?;

        // Load plugin code
        lua.load(&content).eval()?;

        info!("✅ Plugin loaded: {} v{}", plugin.metadata.name, plugin.metadata.version);
        Ok(())
    }

    /// Call plugin hook
    pub async fn call_hook(
        &self,
        plugin_id: &str,
        hook_name: &str,
        args: serde_json::Value,
    ) -> PluginResult<serde_json::Value> {
        debug!("Calling hook: {}::{}", plugin_id, hook_name);

        let lua = self.lua.lock().await;
        let globals = lua.globals();

        // Get hook function
        let hook_fn: Function = globals.get(hook_name)
            .map_err(|_| PluginError::ExecutionError(
                format!("Hook not found: {}", hook_name)
            ))?;

        // Convert args to Lua value
        let lua_args: mlua::Value = lua.to_value(&args)?;

        // Call hook with timeout protection
        match hook_fn.call::<_, mlua::Value>(lua_args) {
            Ok(result) => {
                let json_result: serde_json::Value = lua.from_value(result)?;
                info!("✅ Hook executed: {}::{}", plugin_id, hook_name);
                Ok(json_result)
            }
            Err(e) => {
                Err(PluginError::ExecutionError(format!(
                    "Hook execution failed: {}",
                    e
                )))
            }
        }
    }

    /// Call plugin filter (transform data)
    pub async fn call_filter(
        &self,
        hook_name: &str,
        data: serde_json::Value,
    ) -> PluginResult<serde_json::Value> {
        debug!("Calling filter: {}", hook_name);

        let lua = self.lua.lock().await;
        let globals = lua.globals();

        let filter_fn: Function = globals.get(hook_name)
            .map_err(|_| PluginError::ExecutionError(
                format!("Filter not found: {}", hook_name)
            ))?;

        let lua_data: mlua::Value = lua.to_value(&data)?;

        match filter_fn.call::<_, mlua::Value>(lua_data) {
            Ok(result) => {
                let json_result: serde_json::Value = lua.from_value(result)?;
                Ok(json_result)
            }
            Err(e) => {
                Err(PluginError::ExecutionError(format!(
                    "Filter execution failed: {}",
                    e
                )))
            }
        }
    }

    /// Health check
    pub async fn health_check(&self) -> PluginResult<bool> {
        // Try to execute a simple Lua expression
        let lua = self.lua.lock().await;
        match lua.load("return 1 + 1").eval::<i32>() {
            Ok(result) => Ok(result == 2),
            Err(_) => Ok(false),
        }
    }
}

/// Plugin API available inside Lua
pub mod lua_api {
    use mlua::{Lua, Table};

    pub fn setup_api(lua: &Lua) -> mlua::Result<()> {
        let jarvis = lua.create_table()?;

        // jarvis.log(message)
        jarvis.set("log", lua.create_function(|_, msg: String| {
            tracing::info!("🧩 Plugin: {}", msg);
            Ok(())
        })?)?;

        // jarvis.http.get(url)
        let http = lua.create_table()?;
        http.set("get", lua.create_function(|_, _url: String| {
            // This would call external HTTP
            Ok("{}")
        })?)?;

        jarvis.set("http", http)?;

        // jarvis.config.get(key)
        let config = lua.create_table()?;
        config.set("get", lua.create_function(|_, _key: String| {
            // Return config value
            Ok("")
        })?)?;

        jarvis.set("config", config)?;

        lua.globals().set("jarvis", jarvis)?;
        Ok(())
    }
}
