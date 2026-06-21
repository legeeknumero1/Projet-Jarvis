use axum::{
    extract::{ConnectInfo, State},
    http::StatusCode,
    Json,
};
use serde::{Deserialize, Serialize};
use std::{net::SocketAddr, sync::Arc};
use crate::models::{AppState, AgentInfo};
use chrono::Utc;

#[derive(Deserialize)]
pub struct RegisterAgentPayload {
    pub agent_id: String,
    pub hostname: String,
    pub os_name: String,
    pub os_version: String,
    pub kernel_version: String,
    pub architecture: String,
    pub total_memory_mb: u64,
    pub total_swap_mb: u64,
    pub total_disk_mb: u64,
    pub cpu_cores: usize,
    pub cpu_brand: String,
    pub cpu_frequency_mhz: u64,
    pub uptime_seconds: u64,
    pub load_average: (f64, f64, f64),
    pub mac_addresses: Vec<String>,
}

#[derive(Serialize)]
pub struct RegisterAgentResponse {
    pub status: String,
    pub message: String,
}

fn secure_eq(a: &str, b: &str) -> bool {
    let a_bytes = a.as_bytes();
    let b_bytes = b.as_bytes();
    
    // We intentionally allow length leakage here as the token length is a fixed known size.
    if a_bytes.len() != b_bytes.len() { return false; }
    
    let mut result = 0;
    for (x, y) in a_bytes.iter().zip(b_bytes.iter()) {
        result |= std::hint::black_box(*x) ^ std::hint::black_box(*y);
    }
    std::hint::black_box(result) == 0
}

/// Endpoint for an agent to register or update its heartbeat
pub async fn register_agent(
    headers: axum::http::HeaderMap,
    State(state): State<Arc<AppState>>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
    Json(payload): Json<RegisterAgentPayload>,
) -> Result<Json<RegisterAgentResponse>, (StatusCode, String)> {
    let expected_token = std::env::var("DAEMON_TOKEN").unwrap_or_default();
    if expected_token.is_empty() {
        return Err((StatusCode::INTERNAL_SERVER_ERROR, "DAEMON_TOKEN not configured".to_string()));
    }
    
    let auth_header = headers.get("authorization").and_then(|h| h.to_str().ok());
    let expected_auth = format!("Bearer {}", expected_token);
    
    if !auth_header.map(|h| secure_eq(h, &expected_auth)).unwrap_or(false) {
        tracing::error!("Unauthorized agent registration attempt from {:?}", addr);
        return Err((StatusCode::UNAUTHORIZED, "Invalid daemon token".to_string()));
    }
    let mut agents = state.agents.write();

    let agent_info = AgentInfo {
        agent_id: payload.agent_id.clone(),
        hostname: payload.hostname.clone(),
        os_name: payload.os_name.clone(),
        os_version: payload.os_version.clone(),
        kernel_version: payload.kernel_version.clone(),
        architecture: payload.architecture.clone(),
        total_memory_mb: payload.total_memory_mb,
        total_swap_mb: payload.total_swap_mb,
        total_disk_mb: payload.total_disk_mb,
        cpu_cores: payload.cpu_cores,
        cpu_brand: payload.cpu_brand.clone(),
        cpu_frequency_mhz: payload.cpu_frequency_mhz,
        uptime_seconds: payload.uptime_seconds,
        load_average: payload.load_average,
        mac_addresses: payload.mac_addresses.clone(),
        last_seen: Utc::now().timestamp(),
        ip_address: Some(addr.ip().to_string()),
    };

    let is_new = !agents.contains_key(&payload.agent_id);
    agents.insert(payload.agent_id.clone(), agent_info);

    let message = if is_new {
        format!("Agent {} registered successfully", payload.hostname)
    } else {
        format!("Agent {} heartbeat updated", payload.hostname)
    };

    Ok(Json(RegisterAgentResponse {
        status: "success".to_string(),
        message,
    }))
}

#[derive(Serialize)]
pub struct ListAgentsResponse {
    pub count: usize,
    pub agents: Vec<AgentInfo>,
}

/// Endpoint for the UI or Jarvis to list all known agents
pub async fn list_agents(
    _jwt: crate::middleware::auth::ValidatedJwt,
    State(state): State<Arc<AppState>>,
) -> Result<Json<ListAgentsResponse>, (StatusCode, String)> {
    let agents_lock = state.agents.read();
    let mut agent_list: Vec<AgentInfo> = agents_lock.values().cloned().collect();
    
    // Sort by last seen, newest first
    agent_list.sort_by(|a, b| b.last_seen.cmp(&a.last_seen));

    Ok(Json(ListAgentsResponse {
        count: agent_list.len(),
        agents: agent_list,
    }))
}
