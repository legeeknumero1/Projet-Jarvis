# 🔌 Jarvis MQTT Automations - Phase 5

**Automation engine pour domotique avec MQTT + Home Assistant**

Orchestre les appareils IoT via MQTT et Home Assistant avec rule engine pour automations complexes.

---

## 🏠 Architecture

### Stack Technique

- **MQTT** : Message broker pour communication légère (rumqttc)
- **Home Assistant** : Plateforme domotique (API REST)
- **Rule Engine** : Évaluateur de conditions et actions
- **🦀 Rust** : Type-safe, résilience, zéro allocation

---

## 📋 Automations

Chaque automation contient :
- **Triggers** : Événements qui activent l'automation
- **Conditions** : Règles qui doivent être vraies
- **Actions** : Commandes à exécuter

### Exemple

```rust
let automation = Automation {
    id: "sunset_lights".to_string(),
    name: "Sunset Lights".to_string(),
    enabled: true,
    triggers: vec![
        Trigger::TimeOfDay { hour: 18, minute: 30 },
    ],
    conditions: vec![
        Condition::DayOfWeek {
            days: vec!["Mon".to_string(), "Tue".to_string(), /* ... */],
        },
    ],
    actions: vec![
        Action::TurnOnLight {
            entity_id: "light.salon".to_string(),
            brightness: Some(200),
        },
    ],
    created_at: Utc::now(),
};
```

---

## 🎯 Types de Triggers

```rust
// À une heure spécifique
Trigger::TimeOfDay { hour: 18, minute: 30 }

// Quand un entity change d'état
Trigger::StateChange {
    entity_id: "light.kitchen".to_string(),
    from: "off".to_string(),
    to: "on".to_string(),
}

// Détecteur de mouvement
Trigger::MotionDetected {
    entity_id: "binary_sensor.motion".to_string(),
}

// Ouverture de porte
Trigger::DoorOpened {
    entity_id: "binary_sensor.door".to_string(),
}

// Webhook externe
Trigger::Webhook {
    webhook_id: "webhook_id".to_string(),
}
```

---

## 📋 Types de Conditions

```rust
// État spécifique
Condition::StateEquals {
    entity_id: "light.kitchen".to_string(),
    state: "on".to_string(),
}

// Plage horaire
Condition::TimeRange {
    start: "18:00".to_string(),
    end: "23:00".to_string(),
}

// Température au-dessus d'un seuil
Condition::TemperatureAbove {
    sensor_id: "sensor.temp".to_string(),
    threshold: 25.0,
}

// Jour de la semaine
Condition::DayOfWeek {
    days: vec!["Sat".to_string(), "Sun".to_string()],
}
```

---

## 🎬 Types d'Actions

```rust
// Allumer/éteindre lumière
Action::TurnOnLight {
    entity_id: "light.salon".to_string(),
    brightness: Some(200),
}
Action::TurnOffLight {
    entity_id: "light.kitchen".to_string(),
}

// Thermostat
Action::SetTemperature {
    entity_id: "climate.thermostat".to_string(),
    temperature: 20.5,
}

// Notification
Action::SendNotification {
    title: "Jarvis".to_string(),
    message: "Message important".to_string(),
}

// Publier MQTT
Action::PublishMqtt {
    topic: "home/command".to_string(),
    payload: "action".to_string(),
}

// Délai
Action::Delay { seconds: 5 }
```

---

## 🔌 MQTT Client

### Publier

```rust
mqtt.publish("home/light/salon", "{\"power\": \"on\"}", 1).await?;

// Ou avec helper
let msg = MqttMessage::new(
    "home/light/salon".to_string(),
    "{\"power\": \"on\"}".to_string(),
).with_qos(1);
```

### S'abonner

```rust
mqtt.subscribe("home/+/status", 1).await?;
```

### Home Assistant MQTT

```rust
mqtt.send_ha_command("light.kitchen", "ON").await?;
```

---

## 🏠 Home Assistant Integration

```rust
// Vérifier la connexion
ha_client.health_check().await?;

// Allumer une lumière
ha_client.light_on("light.salon", Some(200)).await?;

// Éteindre
ha_client.light_off("light.kitchen").await?;

// Définir température
ha_client.set_temperature("climate.thermostat", 20.5).await?;

// Notification
ha_client.notify("Message", Some("Titre")).await?;

// État d'une entité
let state = ha_client.get_state("light.kitchen").await?;

// Lister tous les états
let states = ha_client.list_states().await?;
```

---

## ⚙️ Automation Engine

```rust
let engine = AutomationEngine::new();

// Ajouter automation
let automation = Automation::sunset_lights();
engine.add_automation(automation).await?;

// Récupérer
let auto = engine.get_automation("sunset_lights").await?;

// Lister
let automations = engine.list_automations().await?;

// Évaluer trigger
if engine.evaluate_trigger(&trigger, &event) {
    // Exécuter actions
}
```

---

## 🚀 Pre-built Automations

```rust
// Lumières au coucher de soleil
Automation::sunset_lights()

// Mode nuit automatique
Automation::night_mode()

// Alarme motion la nuit
Automation::motion_alarm()
```

---

## 📊 Performance

```
MQTT publish: ~1ms
Home Assistant API: ~100ms
Condition evaluation: <1ms
Action execution: ~50ms (dépend de l'action)
```

---

## 🔒 Sécurité

- **Bearer Token** pour Home Assistant
- **TLS/SSL** pour MQTT (optionnel)
- **Topic ACL** pour MQTT
- **Rate limiting** sur API Home Assistant

---

## 🤝 Intégration

**Phase 5 dans l'architecture :**
- 🦀 Phase 1: Rust Backend Core ✅
- ⚙️ Phase 2: C++ Audio Engine ✅
- 🐍 Phase 3: Python Bridges ✅
- 🗄️ Phase 4: Rust DB Layer ✅
- 🔌 Phase 5: **MQTT Automations** (YOU ARE HERE)
- 🐹 Phase 6: Go Monitoring
- 🌐 Phase 7: Frontend TypeScript
- 🧩 Phase 8: Lua Plugins
- ☁️ Phase 9: Elixir HA

---

**🔌 MQTT Automations - Home automation made simple**

*Architecture Polyglotte Phase 5 pour Jarvis*
