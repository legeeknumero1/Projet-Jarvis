/// Lua Sandbox - Sécurité et isolation pour plugins
use mlua::{Lua, LuaSerdeExt, Table, Function};
use std::sync::Arc;
use std::time::{Duration, Instant};
use tokio::sync::Mutex;
use tracing::{info, debug, warn};

use crate::error::{PluginError, PluginResult};
use crate::plugin_manager::Plugin;

/// Resource limits for Lua sandbox
#[derive(Debug, Clone)]
pub struct ResourceLimits {
    /// Maximum memory in bytes (default: 50 MB)
    pub max_memory_bytes: usize,
    /// Maximum execution time per hook call (default: 5 seconds)
    pub max_execution_time: Duration,
    /// Maximum instructions before timeout (default: 1 million)
    pub max_instructions: u64,
}

impl Default for ResourceLimits {
    fn default() -> Self {
        Self {
            max_memory_bytes: 50 * 1024 * 1024, // 50 MB
            max_execution_time: Duration::from_secs(5), // 5 seconds
            max_instructions: 1_000_000, // 1 million instructions
        }
    }
}

/// Lua Sandbox pour exécuter plugins en sécurité
pub struct LuaSandbox {
    lua: Arc<Mutex<Lua>>,
    limits: ResourceLimits,
    instruction_count: std::sync::Arc<std::sync::atomic::AtomicU64>,
}

impl LuaSandbox {
    /// Create new Lua sandbox with default limits
    pub async fn new() -> PluginResult<Self> {
        Self::with_limits(ResourceLimits::default()).await
    }

    /// Create new Lua sandbox with custom resource limits
    pub async fn with_limits(limits: ResourceLimits) -> PluginResult<Self> {
        info!("Creating Lua sandbox with limits: {:?}", limits);

        let lua = Lua::new();

        // Set memory limit
        lua.set_memory_limit(Some(limits.max_memory_bytes))?;

        // Set CPU limit via instruction hook
        let max_instructions = limits.max_instructions;
        let instruction_count = std::sync::Arc::new(std::sync::atomic::AtomicU64::new(0));
        let instruction_count_clone = instruction_count.clone();
        lua.set_hook(mlua::HookTriggers {
            every_nth_instruction: Some(10000), // Check every 10k instructions
            ..Default::default()
        }, move |_lua, _debug| {
            let current = instruction_count_clone.fetch_add(10000, std::sync::atomic::Ordering::Relaxed);
            if current + 10000 >= max_instructions {
                instruction_count_clone.store(0, std::sync::atomic::Ordering::Relaxed);
                return Err(mlua::Error::RuntimeError(
                    format!("CPU limit exceeded: {} instructions", max_instructions)
                ));
            }
            Ok(())
        })?;

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
        globals.set("package", lua.nil())?;
        globals.set("coroutine", lua.nil())?;

        // Allow safe functions
        // - math, string, table OK
        // - coroutine DISABLED (security vulnerability: bypasses instruction hook)

        info!("Lua sandbox created (safe mode with resource limits)");

        Ok(Self {
            lua: Arc::new(Mutex::new(lua)),
            limits,
            instruction_count,
        })
    }

    /// Load and execute plugin
    pub async fn load_plugin(&self, plugin: &Plugin) -> PluginResult<()> {
        debug!("Loading plugin: {}", plugin.metadata.id);

        self.instruction_count.store(0, std::sync::atomic::Ordering::Relaxed);

        let lua = self.lua.lock().await;
        let content = tokio::fs::read_to_string(&plugin.path).await?;

        // Load plugin code
        lua.load(&content).eval()?;

        info!(" Plugin loaded: {} v{}", plugin.metadata.name, plugin.metadata.version);
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

        self.instruction_count.store(0, std::sync::atomic::Ordering::Relaxed);
        let timeout_duration = self.limits.max_execution_time;

        // Execute hook with timeout enforcement
        let result = tokio::time::timeout(timeout_duration, async {
            let lua = self.lua.lock().await;
            let globals = lua.globals();

            // Get hook function
            let hook_fn: Function = globals.get(hook_name)
                .map_err(|_| PluginError::ExecutionError(
                    format!("Hook not found: {}", hook_name)
                ))?;

            // Convert args to Lua value
            let lua_args: mlua::Value = lua.to_value(&args)?;

            // Call hook
            match hook_fn.call::<_, mlua::Value>(lua_args) {
                Ok(result) => {
                    let json_result: serde_json::Value = lua.from_value(result)?;
                    info!("Hook executed: {}::{}", plugin_id, hook_name);
                    Ok(json_result)
                }
                Err(e) => {
                    Err(PluginError::ExecutionError(format!(
                        "Hook execution failed: {}",
                        e
                    )))
                }
            }
        }).await;

        match result {
            Ok(inner_result) => inner_result,
            Err(_) => Err(PluginError::ExecutionError(format!(
                "Hook execution timeout after {:?}",
                timeout_duration
            )))
        }
    }

    /// Call plugin filter (transform data)
    pub async fn call_filter(
        &self,
        hook_name: &str,
        data: serde_json::Value,
    ) -> PluginResult<serde_json::Value> {
        debug!("Calling filter: {}", hook_name);

        self.instruction_count.store(0, std::sync::atomic::Ordering::Relaxed);
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
            tracing::info!(" Plugin: {}", msg);
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
