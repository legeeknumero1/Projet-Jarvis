use axum::{extract::State, http::StatusCode, Json};
use std::sync::Arc;
use std::time::SystemTime;

use crate::models::{AppState, HealthStatus, Metrics, ServiceStatus};

static STARTUP_TIME: std::sync::OnceLock<SystemTime> = std::sync::OnceLock::new();

/// Health check endpoint
#[utoipa::path(
    get,
    path = "/health",
    responses(
        (status = 200, description = "Service is healthy", body = HealthStatus)
    )
)]
pub async fn health_check(State(_state): State<Arc<AppState>>) -> (StatusCode, Json<HealthStatus>) {
    let startup = STARTUP_TIME.get_or_init(SystemTime::now);
    let uptime = startup.elapsed().unwrap_or_default().as_secs();

    let health = HealthStatus {
        status: "healthy".to_string(),
        version: "1.9.0".to_string(),
        uptime_secs: uptime,
        services: ServiceStatus {
            database: "healthy".to_string(),
            python_bridges: "healthy".to_string(),
            audio_engine: "healthy".to_string(),
        },
    };

    (StatusCode::OK, Json(health))
}

/// Readiness check endpoint
#[utoipa::path(
    get,
    path = "/ready",
    responses(
        (status = 200, description = "Service is ready")
    )
)]
pub async fn readiness_check() -> (StatusCode, Json<serde_json::Value>) {
    let response = serde_json::json!({
        "status": "ready",
        "version": "1.9.0"
    });

    (StatusCode::OK, Json(response))
}

/// Metrics endpoint (Phase 6 Go Monitoring will scrape here)
pub async fn metrics() -> (StatusCode, Json<Metrics>) {
    let metrics = Metrics {
        requests_total: 0,
        chat_requests: 0,
        stt_requests: 0,
        tts_requests: 0,
        memory_searches: 0,
        avg_latency_ms: 0.0,
    };

    (StatusCode::OK, Json(metrics))
}
