# 🧩 Jarvis Lua Plugins - Phase 8

**Système de plugins embarqués en Lua pour extensibilité sans recompilation**

Framework de plugins sécurisé avec sandbox Lua, hot-reload, et hooks système.

---

## 🎯 Architecture

### Stack Technique

- **Lua 5.4** : Langage de scripting rapide et léger
- **mlua** : Rust ↔ Lua FFI
- **Sandbox** : Environnement sécurisé (no os/io/debug)
- **Hot-reload** : Changer plugins sans redémarrer
- **Hook system** : Events lifecycle

---

## 📂 Plugin Directory

```
plugins/
├── welcome_plugin.lua       # Greeting plugin
├── command_plugin.lua       # Custom commands
├── automation_plugin.lua    # Automation hooks
├── filter_plugin.lua        # Message/response filters
└── custom_plugin.lua        # Your plugin here
```

---

## 🔌 Plugin Hooks

### Available Hooks

```lua
-- Called when chat message received
function on_chat(message)
    -- message = {
    --   id: string,
    --   role: "user" | "assistant",
    --   content: string,
    --   timestamp: datetime
    -- }
    return { status = "ok" }
end

-- Called for custom commands
function on_command(cmd)
    -- cmd = {
    --   name: string,
    --   args: table
    -- }
    if cmd.name == "weather" then
        return { response = "Sunny ☀️" }
    end
end

-- Called when automation executed
function on_automation(automation)
    -- automation = {
    --   name: string,
    --   type: string,
    --   status: string
    -- }
    return { success = true }
end

-- Called at startup
function on_startup()
    jarvis.log("Plugin started!")
    return { ready = true }
end

-- Called at shutdown
function on_shutdown()
    jarvis.log("Plugin shutting down")
    return { ok = true }
end

-- Filter messages before processing
function filter_message(message)
    -- Modify message before Jarvis sees it
    message.content = string.trim(message.content)
    return message
end

-- Filter AI responses before sending
function filter_response(response)
    -- Modify response before sending to user
    response.content = string.upper(response.content)
    return response
end
```

---

## 💾 Plugin Metadata

Chaque plugin doit inclure un header:

```lua
-- @id unique_plugin_id
-- @name Plugin Display Name
-- @version 1.0.0
-- @author Your Name
-- @description What this plugin does

-- Rest of plugin code...
```

---

## 🌐 Plugin API

### Available inside Lua

```lua
-- Logging
jarvis.log("Message")  -- Log to console

-- HTTP calls
jarvis.http.get(url)
jarvis.http.post(url, data)

-- Configuration
jarvis.config.get(key)
jarvis.config.set(key, value)

-- State persistence
jarvis.state.set(key, value)
jarvis.state.get(key)

-- Broadcast events
jarvis.events.emit(event_name, data)
jarvis.events.on(event_name, callback)
```

---

## 📝 Example Plugins

### Welcome Plugin
```lua
-- @id welcome
-- @name Welcome
-- @version 1.0.0
-- @author Team
-- @description Greet new users

function on_chat(message)
    if message.role == "user" then
        jarvis.log("👋 User message: " .. message.content)
        return { greeting_sent = true }
    end
    return { ok = true }
end
```

### Command Plugin
```lua
-- @id commands
-- @name Commands
-- @version 1.0.0
-- @author Team
-- @description Custom commands

function on_command(cmd)
    if cmd.name == "help" then
        return {
            response = "Commands: /help, /status, /about"
        }
    end

    if cmd.name == "status" then
        return {
            response = "Jarvis is running! ✅"
        }
    end
end
```

### Filter Plugin
```lua
-- @id filters
-- @name Filters
-- @version 1.0.0
-- @author Team
-- @description Message/response filters

function filter_message(message)
    -- Convert to lowercase
    message.content = string.lower(message.content)

    -- Remove extra spaces
    message.content = string.gsub(message.content, "%s+", " ")

    return message
end

function filter_response(response)
    -- Add emoji to responses
    response.content = response.content .. " 🤖"
    return response
end
```

---

## 🔒 Security

### Sandbox Features

✅ Allowed:
- math, string, table functions
- Basic Lua operations
- Registered jarvis API calls

❌ Blocked:
- `os` module (system calls)
- `io` module (file I/O)
- `load`/`loadstring` (code injection)
- `require` (external modules)
- `debug` module

### Safe Execution

```
User Input
    ↓
Plugin Filter
    ↓
Sandbox Lua Execution
    ↓
Result Validation
    ↓
System Update
```

---

## 🔄 Plugin Lifecycle

### Loading
```
1. Scan plugins directory
2. Read metadata from Lua comments
3. Validate plugin structure
4. Load into Lua sandbox
5. Emit on_startup hook
6. Plugin ready
```

### Unloading
```
1. Emit on_shutdown hook
2. Clear plugin state
3. Remove from registry
4. Free Lua memory
```

### Hot Reload
```
1. Unload existing plugin
2. Re-read from disk
3. Load new version
4. No restart needed!
```

---

## 📊 Performance

```
Plugin loading:       <50ms each
Hook execution:       <5ms average
Lua -> Rust calls:    <1ms roundtrip
Memory per plugin:    ~100KB
```

---

## 🚀 Usage

### Register Plugin
```rust
let manager = PluginManager::new("./plugins").await?;

for plugin in manager.list_plugins() {
    sandbox.load_plugin(&plugin).await?;
}
```

### Call Hook
```rust
let result = sandbox.call_hook(
    "plugin_id",
    "on_chat",
    json!({ "content": "Hello" })
).await?;
```

### Reload Plugin
```rust
manager.unload("plugin_id")?;

// Modify plugin.lua...

let plugin = manager.get_plugin("plugin_id")?;
sandbox.load_plugin(&plugin).await?;
```

---

## 🤝 Intégration Architecture

**Phase 8 dans l'architecture :**
- ✅ Phase 1-7: Core + DB + MQTT + Monitor + Frontend
- 🧩 Phase 8: **Lua Plugins** (YOU ARE HERE)
- ☁️ Phase 9: Elixir HA

**Phase 8 apporte :**
- ✅ Extensibilité sans recompilation
- ✅ Hot-reload de plugins
- ✅ Sandbox sécurisé Lua
- ✅ System hooks pour intégration complète

---

**🧩 Jarvis Plugins - Extensibility without recompilation**

*Architecture Polyglotte Phase 8*
