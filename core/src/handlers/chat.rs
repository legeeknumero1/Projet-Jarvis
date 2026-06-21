use axum::{
    extract::{State, ws::{Message, WebSocket, WebSocketUpgrade}, Extension},
    http::StatusCode,
    response::IntoResponse,
    Json,
};
use serde::{Deserialize, Serialize};
use tokio::time::sleep;
use std::time::Duration;
use std::sync::Arc;
use tracing::{info, warn};

use crate::models::{AppState};




#[derive(Serialize)]
struct JarvisTelemetryFrame {
    speech_status: String,
    audio_amplitude: f32,
    widget_id: String,
    visible: bool,
    action: String,
}

pub async fn jarvis_ws_handler(
    ws: WebSocketUpgrade,
    axum::extract::Query(params): axum::extract::Query<std::collections::HashMap<String, String>>,
    State(state): State<Arc<AppState>>,
) -> impl IntoResponse {
    let token = params.get("token").cloned().unwrap_or_default();
    if let Err(e) = crate::middleware::auth::verify_token(&token, &state.jwt_secret) {
        tracing::warn!("Unauthorized WS connection attempt blocked: {:?}", e);
        return (StatusCode::UNAUTHORIZED, "Invalid or missing token").into_response();
    }
    ws.on_upgrade(move |socket| handle_socket(socket, state))
}

async fn handle_socket(mut socket: WebSocket, state: Arc<AppState>) {
    let mut counter = 0;
    loop {
        tokio::select! {
            _ = sleep(Duration::from_millis(150)) => {
                counter += 1;
                
                // Let's hook into your active state machine.
                // As a fallback since we don't have the AI state API yet, we simulate the state progression.
                let current_state = match counter % 30 {
                    0..=9 => "IDLE",
                    10..=19 => "THINKING",
                    _ => "SPEAKING",
                };

                // Hook into real DSP architecture
                let live_amplitude = state.audio_engine.get_peak_level();

                let telemetry = JarvisTelemetryFrame {
                    speech_status: current_state.to_string(),
                    audio_amplitude: live_amplitude,
                    widget_id: "spotify".to_string(),
                    visible: counter % 100 > 50,
                    action: "TOGGLE_WIDGET".to_string(),
                };

                if let Ok(payload) = serde_json::to_string(&telemetry) {
                    if socket.send(Message::Text(payload)).await.is_err() {
                        break; // Connection dropped, exit task safely
                    }
                }
            }
            msg = socket.recv() => {
                match msg {
                    Some(Ok(_)) => {}, // Drain message
                    Some(Err(_)) | None => break, // Connection closed or error
                }
            }
        }
    }
}

#[derive(Deserialize)]
pub struct UserMessage {
    pub message: String,
}


pub async fn process_jarvis_command(
    _jwt: crate::middleware::auth::ValidatedJwt,
    State(state): State<Arc<AppState>>,
    Extension(gemini_client): Extension<Arc<crate::services::gemini_client::GeminiClient>>,
    Extension(ollama_client): Extension<Arc<crate::services::ollama_client::OllamaClient>>,
    Extension(haos_client): Extension<Arc<crate::services::home_assistant_client::HomeAssistantClient>>,
    Json(payload): Json<UserMessage>,
) -> Result<Json<serde_json::Value>, (StatusCode, String)> {

    // =========================================================================
    // TIER 1 : Cerveau Frontal (Ollama 1.5B) - Triage d'Entropie
    // =========================================================================
    let intent_class = ollama_client.classify_intent(&payload.message).await.unwrap_or_else(|_| "S".to_string());
    info!("Ollama Frontal Triage: Classified intent as '{}'", intent_class);

    // =========================================================================
    // TIER 2: Deterministic local routing with Ollama flavor
    // =========================================================================
    // We try local routing if it's explicitly classified as Local or if it matches anyway.
    if let Some(mut local_frame) = crate::services::LocalIntentRouter::try_route(&payload.message) {
        info!(
            intent = "LOCAL_ROUTED",
            command = %payload.message,
            "Intent resolved locally — cloud API bypassed"
        );
        
        let action = local_frame["action"].as_str().unwrap_or("");
        
        // Execute real Home Assistant commands
        if action == "EXEC_HAOS_SERVICE" {
            let domain = local_frame["haos_domain"].as_str().unwrap_or("light");
            let service = local_frame["haos_service"].as_str().unwrap_or("turn_on");
            let entity = local_frame["haos_entity"].as_str(); // Optional

            if let Err(e) = haos_client.call_service(domain, service, entity, None).await {
                warn!("HAos error executing {}/{}: {}", domain, service, e);
            }
        }

        let system_prompt = r#"Tu es J.A.R.V.I.S. L'action domotique/système vient d'être exécutée avec succès.
Formule une confirmation très brève (une seule phrase claire) de cette exécution pour l'utilisateur. 
Tu dois l'appeler "Monsieur". Sois flegmatique. N'ajoute AUCUN format JSON, juste le texte parlé."#;
        
        let ollama_prompt = format!("L'utilisateur a demandé : '{}'. L'action exécutée est : '{}'. Confirme-le oralement.", payload.message, local_frame["action"]);
        
        let system_json_prompt = format!("{}\n\nRenvoie UNIQUEMENT un objet JSON avec la clé 'reply_text' contenant ta phrase.", system_prompt);
        
        if let Ok(ollama_resp) = ollama_client.fallback_chat(&system_json_prompt, &ollama_prompt).await {
            if let Some(text) = ollama_resp["reply_text"].as_str() {
                local_frame["reply_text"] = serde_json::json!(text);
            } else {
                local_frame["reply_text"] = serde_json::json!("C'est fait, Monsieur.");
            }
        } else {
            local_frame["reply_text"] = serde_json::json!("Exécution confirmée, Monsieur.");
        }

        return Ok(Json(local_frame));
    }
    
    if intent_class == "L" {
        // Classifié Local mais le parseur strict n'a pas matché. On le passe à Gemini mais bridé à 60 tokens pour parser l'entité.
        info!("Intent classified as Local but LocalIntentRouter missed it. Falling back to Gemini as Short/Local.");
    }

    // =========================================================================
    // TIER 3: Gemini 2.5 Flash cloud reasoning (primary)
    // =========================================================================
    info!(
        intent = "CLOUD_ROUTED",
        command = %payload.message,
        "No local match — forwarding to Gemini AI Studio"
    );

    // Call the new context retrieval function
    // Retrieve context snippets but DO NOT alter system instructions (preserves Gemini caching)
    let mut context_snippets = state.memory_index.search_context(&payload.message, 3).await.unwrap_or_default();

    // INJECT LIVE AGENTS METRICS
    let agents_json = {
        let agents_lock = state.agents.read();
        serde_json::to_string(&*agents_lock).unwrap_or_default()
    };
    if !agents_json.is_empty() && agents_json != "{}" {
        context_snippets.push(format!("ÉTAT EN DIRECT DU MATÉRIEL (Daemons connectés) : {}", agents_json));
    }

    // Concurrently, dispatch a background task (tokio::spawn) to send the current user message to the indexing channel via MemoryCommand::AddDocument so it's archived for future queries.
    let memory_index_clone = state.memory_index.clone();
    let user_msg_clone = payload.message.clone();
    tokio::spawn(async move {
        let vector_id = uuid::Uuid::new_v4().to_string();
        let timestamp = chrono::Utc::now().timestamp();
        if let Err(e) = memory_index_clone.add_document(user_msg_clone, vector_id, timestamp).await {
            tracing::error!("Failed to queue user message for indexing: {:?}", e);
        }
    });

    let mut current_context = context_snippets;
    let mut iterations = 0;
    
    // Dynamic Token Allocator based on Triage
    let max_output_tokens = match intent_class.as_str() {
        "S" | "L" => {
            current_context.push("ATTENTION: Tu dois répondre de façon ULTRA-COURTE (1 phrase max).".to_string());
            60 // Very restrictive ceiling for facts or local fallbacks
        },
        _ => 800 // Complex/Agentic reasoning allowed
    };

    let mut hud_instruction_result = loop {
        iterations += 1;
        match gemini_client.analyze_intent(&payload.message, current_context.clone(), max_output_tokens).await {
            Ok(mut hud) => {
                // =========================================================================
                // THE "ASK" PROTOCOL (Multi-turn tool calling)
                // =========================================================================
                if let Some(action) = hud["action"].as_str() {
                    if action.starts_with("ASK_DAEMON:") && iterations < 3 {
                        let mut target_host = action.trim_start_matches("ASK_DAEMON:");
                        let mut query_params = "";
                        
                        if let Some(idx) = target_host.find('?') {
                            let parts = target_host.split_at(idx);
                            target_host = parts.0;
                            query_params = parts.1; // Includes the '?'
                        }
                        
                        tracing::info!("Jarvis requested metrics from Daemon: {} with query {}", target_host, query_params);
                        
                        // Find agent IP
                        let ip_opt = {
                            let agents_lock = state.agents.read();
                            if agents_lock.len() == 1 {
                                agents_lock.values().next().and_then(|a| a.ip_address.clone())
                            } else {
                                agents_lock.values().find(|a| {
                                    let h1 = a.hostname.to_lowercase();
                                    let h2 = target_host.to_lowercase();
                                    h1 == h2 || h1.contains(&h2) || h2.contains(&h1) || a.agent_id == target_host
                                }).and_then(|a| a.ip_address.clone())
                            }
                        };
                        
                        if let Some(ip) = ip_opt {
                            let daemon_url = format!("https://{}:8101/metrics{}", ip, query_params);
                            
                            // SECURITY FIX: MITM prevention (No danger_accept_invalid_certs) & DoS prevention (timeout)
                            let cert_path = std::env::var("TLS_CERT_PATH").unwrap_or_else(|_| "certs/server.crt".to_string());
                            let cert_pem = tokio::fs::read(&cert_path).await.unwrap_or_default();
                            let mut client_builder = reqwest::Client::builder()
                                .timeout(std::time::Duration::from_secs(3));
                            if let Ok(cert) = reqwest::Certificate::from_pem(&cert_pem) {
                                client_builder = client_builder.add_root_certificate(cert);
                            }
                            let client = client_builder.build().unwrap_or_default();
                                
                            match client.get(&daemon_url).send().await {
                                Ok(res) => {
                                    if let Ok(metrics_json) = res.text().await {
                                        current_context.push(format!("Données fraîches reçues du Daemon '{}' : {}", target_host, metrics_json));
                                        continue; // Loop back to Gemini with new context
                                    }
                                }
                                Err(e) => {
                                    current_context.push(format!("Impossible de contacter le Daemon '{}'. Erreur: {}", target_host, e));
                                    continue;
                                }
                            }
                        } else {
                            current_context.push(format!("Aucun Daemon trouvé avec le nom '{}'.", target_host));
                            continue;
                        }
                    }
                }
                
                break Ok(hud);
            }
            Err(e) => break Err(e),
        }
    };

    match hud_instruction_result {
        Ok(mut hud_instruction) => {
            // =========================================================================
            // ACTION INTERCEPTOR (Real Function Calling equivalent)
            // =========================================================================
            if let Some(action) = hud_instruction["action"].as_str() {
                if action.starts_with("MAC_CMD:") {
                    let cmd = action.trim_start_matches("MAC_CMD:");
                    
                    // SECURITY FIX: Strict allowlist and direct binary execution to prevent RCE via shell spawn
                    tracing::info!("Requested macOS command: {}", cmd);
                    match cmd {
                        "open -a Safari" => { let _ = std::process::Command::new("open").args(["-a", "Safari"]).spawn(); },
                        "open -a Mail" => { let _ = std::process::Command::new("open").args(["-a", "Mail"]).spawn(); },
                        "open -a Music" => { let _ = std::process::Command::new("open").args(["-a", "Music"]).spawn(); },
                        "pmset displaysleepnow" => { let _ = std::process::Command::new("pmset").arg("displaysleepnow").spawn(); },
                        _ => { tracing::warn!("SECURITY ALERT: Blocked unauthorized MAC_CMD attempt: {}", cmd); }
                    }
                }
            }

            if let Some(widget_id) = hud_instruction["widget_id"].as_str() {
                if widget_id.starts_with("weather_") {
                    let city = widget_id.trim_start_matches("weather_").replace('_', " ");
                    info!("Weather intent detected for city: {}", city);
                    
                    // Fetch real weather data from wttr.in (no API key required)
                    let weather_url = format!("https://wttr.in/{}?format=j1", urlencoding::encode(&city));
                    if let Ok(resp) = reqwest::get(&weather_url).await {
                        if let Ok(weather_json) = resp.json::<serde_json::Value>().await {
                            if let Some(current) = weather_json["current_condition"].as_array().and_then(|a| a.first()) {
                                let temp = current["temp_C"].as_str().unwrap_or("?");
                                let desc = current["lang_fr"].as_array()
                                    .and_then(|a| a.first())
                                    .and_then(|o| o["value"].as_str())
                                    .or_else(|| current["weatherDesc"].as_array().and_then(|a| a.first()).and_then(|o| o["value"].as_str()))
                                    .unwrap_or("Inconnu");
                                let wind = current["windspeedKmph"].as_str().unwrap_or("?");
                                let humidity = current["humidity"].as_str().unwrap_or("?");
                                
                                // Update Jarvis's vocal response with real data
                                hud_instruction["reply_text"] = serde_json::json!(format!(
                                    "La température actuelle à {} est de {} degrés Celsius, avec des conditions : {}.",
                                    city, temp, desc
                                ));
                                
                                // Inject real data for the React WidgetRenderer
                                hud_instruction["widget_data"] = serde_json::json!({
                                    "temp": temp,
                                    "desc": desc,
                                    "wind": wind,
                                    "humidity": humidity,
                                    "city": city
                                });
                                info!("Successfully fetched real weather for {}", city);
                            }
                        }
                    }
                }
            }

            return Ok(Json(hud_instruction));
        }
        Err(cloud_err) => {
            // =================================================================
            // ERROR HANDLING (NO OLLAMA FALLBACK)
            // =================================================================
            warn!(
                intent = "CLOUD_FAILED",
                error = %cloud_err,
                command = %payload.message,
                "Cloud API failure detected. User requested NO Ollama fallback for heavy LLM operations."
            );

            let error_hud = serde_json::json!({
                "speech_status": "CRITICAL",
                "audio_amplitude": 0.0,
                "widget_id": "error",
                "visible": true,
                "action": "NONE",
                "reply_text": "Pardonnez-moi Monsieur, la liaison avec mon centre de calcul principal a été interrompue. Je ne peux pas traiter de requêtes complexes pour le moment.",
                "widget_data": {
                    "error": cloud_err.to_string()
                }
            });
            
            return Ok(Json(error_hud));
        }
    }
}

