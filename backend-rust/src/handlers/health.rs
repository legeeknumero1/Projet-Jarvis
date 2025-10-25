//! Handlers de santé système pour Jarvis Rust Backend
//! 
//! Endpoints équivalents aux routes health.py Python

use axum::{extract::State, http::StatusCode, response::IntoResponse, Json};
use serde_json::json;

use crate::{models::HealthStatus, ApiResponse, AppState};

/// GET /health - Vérification de santé globale du système
/// 
/// Endpoint principal pour vérifier que tous les services sont opérationnels.
/// Utilisé par les load balancers et monitoring externe.
pub async fn health_check(State(state): State<AppState>) -> impl IntoResponse {
    match state.services.health.check_all_services().await {
        Ok(health_status) => {
            let status_code = match health_status.status {
                crate::models::ServiceStatus::Healthy => StatusCode::OK,
                crate::models::ServiceStatus::Degraded => StatusCode::OK, // Toujours 200 mais signal dégradé
                crate::models::ServiceStatus::Unhealthy => StatusCode::SERVICE_UNAVAILABLE,
            };

            (status_code, Json(ApiResponse::ok(health_status)))
        }
        Err(e) => {
            tracing::error!("Erreur lors du health check: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(ApiResponse::<()>::error(format!("Erreur health check: {}", e))),
            )
        }
    }
}

/// GET /ready - Vérification de disponibilité pour Kubernetes
/// 
/// Endpoint de readiness probe pour orchestrateurs.
/// Vérifie que l'application est prête à recevoir du trafic.
pub async fn readiness_check(State(state): State<AppState>) -> impl IntoResponse {
    // Vérifications critiques pour la disponibilité
    let checks = vec![
        ("database", state.services.database.is_ready().await),
        ("llm", state.services.llm.is_ready().await),
        ("memory", state.services.memory.is_ready().await),
    ];

    let mut ready = true;
    let mut failed_checks = Vec::new();

    for (service, check_result) in checks {
        if let Err(e) = check_result {
            ready = false;
            failed_checks.push(format!("{}: {}", service, e));
            tracing::warn!("Service {} not ready: {}", service, e);
        }
    }

    if ready {
        (
            StatusCode::OK,
            Json(json!({
                "status": "ready",
                "version": env!("CARGO_PKG_VERSION"),
                "timestamp": chrono::Utc::now()
            })),
        )
    } else {
        (
            StatusCode::SERVICE_UNAVAILABLE,
            Json(json!({
                "status": "not_ready",
                "failed_checks": failed_checks,
                "timestamp": chrono::Utc::now()
            })),
        )
    }
}

/// GET /metrics - Métriques Prometheus (futur)
/// 
/// Endpoint pour exposition des métriques au format Prometheus.
/// Sera implémenté dans une version ultérieure.
pub async fn metrics(_state: State<AppState>) -> impl IntoResponse {
    // TODO: Implémenter les métriques Prometheus
    (
        StatusCode::NOT_IMPLEMENTED,
        "# Métriques Prometheus - À implémenter\n# TYPE jarvis_requests_total counter\n",
    )
}