/// Plugin API - Rust to Lua interface
use serde::{Deserialize, Serialize};

/// Plugin hook input
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PluginInput {
    pub hook: String,
    pub plugin_id: String,
    pub data: serde_json::Value,
}

/// Plugin hook output
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PluginOutput {
    pub success: bool,
    pub result: serde_json::Value,
    pub error: Option<String>,
}

/// Plugin API for calling hooks
pub struct PluginAPI;

impl PluginAPI {
    /// Available hooks
    pub const HOOKS: &'static [&'static str] = &[
        "on_chat",        // Appelé quand message reçu
        "on_command",     // Appelé pour commandes personnalisées
        "on_automation",  // Appelé quand automation exécutée
        "on_startup",     // Appelé au démarrage
        "on_shutdown",    // Appelé à l'arrêt
        "filter_message", // Filtre les messages
        "filter_response",// Filtre les réponses IA
    ];

    /// Example plugin: welcome plugin
    pub fn example_welcome_plugin() -> String {
        r#"
-- @id welcome_plugin
-- @name Welcome Plugin
-- @version 1.0.0
-- @author Jarvis Team
-- @description Greet users on first message

local greeting_count = 0

function on_chat(message)
    greeting_count = greeting_count + 1

    if greeting_count == 1 then
        jarvis.log("👋 First message from user!")
        return {
            status = "success",
            action = "show_welcome"
        }
    end

    return {
        status = "ok"
    }
end

function filter_message(message)
    -- Convert to uppercase for fun
    message.content = string.upper(message.content)
    return message
end
"#.to_string()
    }

    /// Example plugin: command plugin
    pub fn example_command_plugin() -> String {
        r#"
-- @id command_plugin
-- @name Command Plugin
-- @version 1.0.0
-- @author Jarvis Team
-- @description Handle custom commands

function on_command(cmd)
    if cmd.name == "weather" then
        return {
            status = "success",
            response = "It's sunny today! 🌞"
        }
    end

    if cmd.name == "help" then
        return {
            status = "success",
            response = "Available commands: /weather, /help, /settings"
        }
    end

    return {
        status = "error",
        response = "Unknown command: " .. cmd.name
    }
end
"#.to_string()
    }

    /// Example plugin: automation plugin
    pub fn example_automation_plugin() -> String {
        r#"
-- @id automation_plugin
-- @name Automation Plugin
-- @version 1.0.0
-- @author Jarvis Team
-- @description Handle automations

local automation_log = {}

function on_automation(automation)
    table.insert(automation_log, {
        name = automation.name,
        timestamp = os.time(),
        status = "executed"
    })

    jarvis.log("🔄 Automation executed: " .. automation.name)

    return {
        status = "success",
        executed = true,
        logged = true
    }
end
"#.to_string()
    }
}

/// Hook types for documentation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum HookType {
    /// Called when chat message received
    OnChat,
    /// Called for custom commands
    OnCommand,
    /// Called when automation executed
    OnAutomation,
    /// Called at startup
    OnStartup,
    /// Called at shutdown
    OnShutdown,
    /// Filters messages before processing
    FilterMessage,
    /// Filters AI responses before sending
    FilterResponse,
}

impl HookType {
    pub fn name(&self) -> &str {
        match self {
            HookType::OnChat => "on_chat",
            HookType::OnCommand => "on_command",
            HookType::OnAutomation => "on_automation",
            HookType::OnStartup => "on_startup",
            HookType::OnShutdown => "on_shutdown",
            HookType::FilterMessage => "filter_message",
            HookType::FilterResponse => "filter_response",
        }
    }

    pub fn description(&self) -> &str {
        match self {
            HookType::OnChat => "Called when chat message received",
            HookType::OnCommand => "Called for custom commands",
            HookType::OnAutomation => "Called when automation executed",
            HookType::OnStartup => "Called at startup",
            HookType::OnShutdown => "Called at shutdown",
            HookType::FilterMessage => "Filters messages before processing",
            HookType::FilterResponse => "Filters AI responses before sending",
        }
    }
}
