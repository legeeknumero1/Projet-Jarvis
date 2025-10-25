# ⚡ Fixes Rapides - Issues Critiques (Top 10)

**Temps total estimé: 18h de développement**

---

## 🔴 FIX #1: Upgrade sqlx (5 min) ⚡ IMMÉDIAT

**Fichier**: `backend-rust-db/Cargo.toml`

```diff
- sqlx = { version = "0.7", features = ["runtime-tokio-native-tls", "postgres", "uuid", "chrono", "json"] }
+ sqlx = { version = "0.8.1", features = ["runtime-tokio-native-tls", "postgres", "uuid", "chrono", "json"] }
```

**Commande**:
```bash
cd backend-rust-db
cargo update sqlx
```

---

## 🔴 FIX #2: Token Authentication → httpOnly Cookies (2h)

**Fichier**: `frontend-phase7/lib/api.ts`

```typescript
// Avant
const API = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8100',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

API.interceptors.request.use(
  (config) => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// Après
const API = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8100',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
  withCredentials: true, // ✅ Envoyer automatiquement les cookies
});

// Plus besoin de gérer le token - il est en cookie httpOnly maintenant!
// Le backend doit retourner: Set-Cookie: auth_token=...; HttpOnly; Secure; SameSite=Strict
```

**Côté backend (Rust)**:
```rust
// Dans la réponse de login
response.headers_mut().insert(
    "Set-Cookie",
    format!(
        "auth_token={}; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age={}",
        token, 3600
    ).parse()?,
);
```

---

## 🔴 FIX #3: Remplacer `any` par Types Spécifiques (3h)

**Fichier**: `frontend-phase7/lib/api.ts`

```typescript
// Avant
getHistory: async (conversationId: string, limit: number = 50): Promise<any> => {
  const response = await API.get(`/api/chat/history/${conversationId}`, {
    params: { limit },
  });
  return response.data;
}

// Après
getHistory: async (conversationId: string, limit: number = 50): Promise<ApiResponse<Message[]>> => {
  const response = await API.get<ApiResponse<Message[]>>(`/api/chat/history/${conversationId}`, {
    params: { limit },
  });
  return response.data;
}
```

**Autres occurrences à fixer**:
- Line 71: `createConversation` → `Promise<ApiResponse<Conversation>>`
- Line 79: `listConversations` → `Promise<PaginatedResponse<Conversation>>`
- Line 151: `login` → `Promise<AuthResponse>`
- Line 160: `register` → `Promise<AuthResponse>`

---

## 🔴 FIX #4: Timeout sur Exécution Lua (1h)

**Fichier**: `backend-lua-plugins/src/sandbox.rs`

```diff
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

-   // Call hook with timeout protection
-   match hook_fn.call::<_, mlua::Value>(lua_args) {
+   // Call hook with timeout
+   let timeout = tokio::time::timeout(
+       std::time::Duration::from_secs(5),
+       async {
+           hook_fn.call::<_, mlua::Value>(lua_args)
+       }
+   ).await;
+
+   match timeout {
+       Ok(Ok(result)) => {
            let json_result: serde_json::Value = lua.from_value(result)?;
            info!("✅ Hook executed: {}::{}", plugin_id, hook_name);
            Ok(json_result)
        }
+       Ok(Err(e)) => {
            Err(PluginError::ExecutionError(format!(
                "Hook execution failed: {}",
                e
            )))
        }
+       Err(_) => {
+           Err(PluginError::ExecutionError(format!(
+               "Hook execution timeout (>5s): {}::{}",
+               plugin_id, hook_name
+           )))
+       }
+   }
}
```

---

## 🔴 FIX #5: Isolation des Plugins Lua (4h)

**Fichier**: `backend-lua-plugins/src/sandbox.rs`

```rust
use std::collections::HashMap;

pub struct LuaSandbox {
    // Avant: lua: Arc<Mutex<Lua>>
    // Après:
    instances: Arc<Mutex<HashMap<String, Arc<Mutex<Lua>>>>>,
}

impl LuaSandbox {
    pub async fn new() -> PluginResult<Self> {
        info!("🔒 Creating Lua sandbox");
        Ok(Self {
            instances: Arc::new(Mutex::new(HashMap::new())),
        })
    }

    pub async fn load_plugin(&self, plugin: &Plugin) -> PluginResult<()> {
        debug!("Loading plugin: {}", plugin.metadata.id);

        let lua = Lua::new();

        // Setup safe environment
        let globals = lua.globals();
        globals.set("os", lua.nil())?;
        globals.set("io", lua.nil())?;
        globals.set("load", lua.nil())?;
        globals.set("loadstring", lua.nil())?;
        globals.set("dofile", lua.nil())?;
        globals.set("require", lua.nil())?;
        globals.set("debug", lua.nil())?;

        // Load plugin code
        let content = tokio::fs::read_to_string(&plugin.path).await?;
        lua.load(&content).eval()?;

        // Store in isolated instance
        self.instances.lock().await.insert(
            plugin.metadata.id.clone(),
            Arc::new(Mutex::new(lua)),
        );

        info!("✅ Plugin loaded: {} v{}", plugin.metadata.name, plugin.metadata.version);
        Ok(())
    }

    pub async fn call_hook(
        &self,
        plugin_id: &str,
        hook_name: &str,
        args: serde_json::Value,
    ) -> PluginResult<serde_json::Value> {
        // Get specific plugin instance
        let instances = self.instances.lock().await;
        let lua_instance = instances
            .get(plugin_id)
            .ok_or_else(|| PluginError::ExecutionError(
                format!("Plugin not found: {}", plugin_id)
            ))?;

        let lua = lua_instance.lock().await;
        // ... rest of implementation
    }
}
```

---

## 🔴 FIX #6: Memory Limits pour Lua (2h)

**Fichier**: `backend-lua-plugins/Cargo.toml`

```diff
[dependencies]
# ... autres deps ...
+ sandkiste_lua = "0.1"
```

**Dans sandbox.rs**:

```rust
use sandkiste_lua::LuaLimits;

pub async fn new() -> PluginResult<Self> {
    // Créer Lua avec limites
    let lua = Lua::new_with_limits(
        LuaLimits {
            memory_limit: Some(10_000_000), // 10MB par plugin
            instruction_limit: Some(1_000_000), // 1M instructions
            ..Default::default()
        }
    );

    // ... setup sandbox ...
}
```

---

## 🟡 FIX #7: Validation URLs Frontend (1.5h)

**Fichier**: `frontend-phase7/lib/api.ts`

```typescript
import { z } from 'zod';

// Ajouter schemas de validation
const ConversationIdSchema = z.string().uuid();
const MessageContentSchema = z.string().min(1).max(10000);

export const chatApi = {
  sendMessage: async (conversationId: string, content: string): Promise<ApiResponse<any>> => {
    // Valider les inputs
    const validConvId = ConversationIdSchema.parse(conversationId);
    const validContent = MessageContentSchema.parse(content);

    const response = await API.post('/api/chat/message', {
      conversationId: validConvId,
      content: validContent,
    });
    return response.data;
  },

  deleteConversation: async (conversationId: string): Promise<ApiResponse<any>> => {
    const validId = ConversationIdSchema.parse(conversationId);
    const response = await API.delete(
      `/api/chat/conversation/${encodeURIComponent(validId)}`
    );
    return response.data;
  },
  // ... autres endpoints
};
```

---

## 🟡 FIX #8: Dépendances useCallback (1h)

**Fichier**: `frontend-phase7/hooks/useChat.ts`

```typescript
// Avant
const sendMessage = useCallback(async (content: string) => {
  if (!state.currentConversationId) {
    // ...
  }
  // ...
}, []); // ❌ Dépendances manquantes

// Après
const sendMessage = useCallback(async (content: string) => {
  if (!state.currentConversationId) {
    // ...
  }
  // ...
}, [state.currentConversationId]); // ✅ Ajoutée

const loadHistory = useCallback(async (conversationId: string) => {
  // ...
}, [state.currentConversationId]); // ✅ Dépendance ajoutée
```

---

## 🟡 FIX #9: Fallback Clustering Strategy (30 min)

**Fichier**: `clustering-elixir/lib/jarvis_ha/application.ex`

```elixir
# Avant
defp libcluster_topologies do
  case System.get_env("CLUSTER_STRATEGY", "static") do
    "static" ->
      [strategy: Cluster.Strategy.Static, config: [...]]
    "kubernetes" ->
      [strategy: Cluster.Strategy.Kubernetes, config: [...]]
    "epmd" ->
      [strategy: Cluster.Strategy.Epmd, config: [...]]
    _ -> []  # ❌ Silencieusement pas de clustering!
  end
end

# Après
defp libcluster_topologies do
  strategy = System.get_env("CLUSTER_STRATEGY", "static")

  case strategy do
    "static" ->
      [strategy: Cluster.Strategy.Static, config: [...]]
    "kubernetes" ->
      [strategy: Cluster.Strategy.Kubernetes, config: [...]]
    "epmd" ->
      [strategy: Cluster.Strategy.Epmd, config: [...]]
    invalid ->
      require Logger
      Logger.error("Invalid CLUSTER_STRATEGY: #{invalid}. Using 'static'")
      [strategy: Cluster.Strategy.Static, config: [nodes: ["jarvis@127.0.0.1"]]]
  end
end
```

---

## 🟡 FIX #10: MQTT Reconnection (1.5h)

**Fichier**: `backend-rust-mqtt/src/mqtt_client.rs`

```rust
pub struct MqttService {
    client: Arc<Mutex<AsyncClient>>,
    broker_url: String,
    connected: Arc<Mutex<bool>>,
    max_retries: u32,        // ✅ Nouvelle
    retry_delay_ms: u64,     // ✅ Nouvelle
}

impl MqttService {
    pub async fn new(broker_url: &str) -> MqttResult<Self> {
        let service = Self {
            client: Arc::new(Mutex::new(AsyncClient::new()?)),
            broker_url: broker_url.to_string(),
            connected: Arc::new(Mutex::new(false)),
            max_retries: 5,
            retry_delay_ms: 1000,
        };

        service.connect_with_retry().await?;
        Ok(service)
    }

    async fn connect_with_retry(&self) -> MqttResult<()> {
        for attempt in 0..self.max_retries {
            match self.connect().await {
                Ok(_) => {
                    *self.connected.lock().await = true;
                    info!("✅ MQTT connected");
                    return Ok(());
                }
                Err(e) if attempt < self.max_retries - 1 => {
                    let delay = self.retry_delay_ms * 2_u64.pow(attempt as u32);
                    warn!("⚠️ MQTT connection failed, retrying in {}ms: {}", delay, e);
                    tokio::time::sleep(Duration::from_millis(delay)).await;
                }
                Err(e) => {
                    error!("❌ MQTT connection failed after {} attempts: {}", self.max_retries, e);
                    return Err(e);
                }
            }
        }
        Ok(())
    }
}
```

---

## 📋 Plan d'Implémentation

**Jour 1 (8h)**:
1. ✅ FIX #1: Upgrade sqlx (5 min)
2. ✅ FIX #4: Lua timeout (1h)
3. ✅ FIX #9: Elixir clustering (30 min)
4. ✅ FIX #8: useCallback deps (1h)
5. ✅ FIX #10: MQTT retry (1.5h)
6. ✅ FIX #7: URL validation (1.5h)
7. ✅ FIX #3: Type safety (2h)

**Jour 2 (10h)**:
1. ✅ FIX #2: Auth cookies (2h)
2. ✅ FIX #5: Lua isolation (4h)
3. ✅ FIX #6: Memory limits (2h)
4. ✅ Tests et vérification (2h)

---

## ✅ Validation Checklist

- [ ] Tous les tests passent
- [ ] Pas d'avertissements TypeScript
- [ ] Pas d'avertissements Rust
- [ ] Audit de sécurité dans CI/CD
- [ ] Performance metrics avant/après

---

**Total: ~18 heures de développement**
**Complexité: Moyenne**
**Impact Sécurité: CRITIQUE**

Commencer par les FIX #1, #4, #9 qui prennent peu de temps mais ont un grand impact.
