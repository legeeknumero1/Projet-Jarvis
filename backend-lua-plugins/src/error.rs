/// Plugin error types
use thiserror::Error;

#[derive(Error, Debug)]
pub enum PluginError {
    #[error("Plugin not found: {0}")]
    NotFound(String),

    #[error("Plugin load error: {0}")]
    LoadError(String),

    #[error("Plugin execution error: {0}")]
    ExecutionError(String),

    #[error("Sandbox violation: {0}")]
    SandboxViolation(String),

    #[error("Invalid plugin: {0}")]
    InvalidPlugin(String),

    #[error("Lua error: {0}")]
    LuaError(String),

    #[error("Serialization error: {0}")]
    SerializationError(#[from] serde_json::Error),

    #[error("IO error: {0}")]
    IoError(#[from] std::io::Error),

    #[error("Internal error: {0}")]
    Internal(String),
}

pub type PluginResult<T> = Result<T, PluginError>;

impl From<mlua::Error> for PluginError {
    fn from(err: mlua::Error) -> Self {
        PluginError::LuaError(err.to_string())
    }
}
