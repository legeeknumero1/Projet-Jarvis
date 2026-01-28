use axum::{
    extract::{Query, State},
    http::StatusCode,
    Json,
};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use utoipa::{IntoParams, ToSchema};

use crate::middleware::ValidatedJwt;
use crate::models::AppState;

#[derive(Debug, Deserialize, IntoParams)]
pub struct SearchQuery {
    /// La requête de recherche
    pub q: String,
    /// Nombre de résultats (max 20)
    #[serde(default = "default_count")]
    pub count: u8,
    /// Langue de recherche (fr, en, etc.)
    #[serde(default = "default_lang")]
    pub search_lang: String,
}

fn default_count() -> u8 {
    10
}

fn default_lang() -> String {
    "fr".to_string()
}

#[derive(Debug, Serialize, ToSchema)]
pub struct SearchResult {
    pub title: String,
    pub url: String,
    pub description: String,
}

#[derive(Debug, Serialize, ToSchema)]
pub struct SearchResponse {
    pub query: String,
    pub results: Vec<SearchResult>,
    pub total: usize,
}

/// Recherche web via Brave Search API
///
/// Effectue une recherche sur Internet en utilisant l'API Brave Search.
/// La clé API est chargée de manière sécurisée depuis jarvis-secretsd.
#[utoipa::path(
    get,
    path = "/api/v1/search",
    params(SearchQuery),
    responses(
        (status = 200, description = "Résultats de recherche", body = SearchResponse),
        (status = 400, description = "Requête invalide"),
        (status = 500, description = "Erreur serveur")
    ),
    tag = "Web Search",
    security(
        ("bearer_auth" = [])
    )
)]
pub async fn web_search(
    ValidatedJwt(_claims): ValidatedJwt,
    State(_state): State<Arc<AppState>>,
    Query(params): Query<SearchQuery>,
) -> Result<Json<SearchResponse>, (StatusCode, String)> {
    // Récupérer la clé API Brave depuis l'environnement (chargée par jarvis-secretsd)
    let brave_api_key = std::env::var("BRAVE_API_KEY")
        .map_err(|_| (StatusCode::INTERNAL_SERVER_ERROR, "BRAVE_API_KEY not configured".to_string()))?;

    if brave_api_key.is_empty() {
        return Err((
            StatusCode::INTERNAL_SERVER_ERROR,
            "BRAVE_API_KEY is empty".to_string(),
        ));
    }

    // Limiter le nombre de résultats
    let count = params.count.min(20);

    // Construire l'URL de requête
    let url = format!(
        "https://api.search.brave.com/res/v1/web/search?q={}&count={}&search_lang={}",
        urlencoding::encode(&params.q),
        count,
        params.search_lang
    );

    // Créer le client HTTP
    let client = reqwest::Client::new();

    // Faire la requête vers Brave Search API
    let response = client
        .get(&url)
        .header("Accept", "application/json")
        .header("X-Subscription-Token", &brave_api_key)
        .send()
        .await
        .map_err(|e| {
            tracing::error!("Brave Search API request failed: {}", e);
            (
                StatusCode::BAD_GATEWAY,
                format!("Search API request failed: {}", e),
            )
        })?;

    // Vérifier le statut de la réponse
    if !response.status().is_success() {
        let status = response.status();
        let error_text = response.text().await.unwrap_or_else(|_| "Unknown error".to_string());
        tracing::error!("Brave Search API error {}: {}", status, error_text);
        return Err((
            StatusCode::BAD_GATEWAY,
            format!("Search API error: {} - {}", status, error_text),
        ));
    }

    // Parser la réponse JSON
    let brave_response: serde_json::Value = response.json().await.map_err(|e| {
        tracing::error!("Failed to parse Brave Search response: {}", e);
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            format!("Failed to parse search results: {}", e),
        )
    })?;

    // Extraire les résultats web
    let results: Vec<SearchResult> = brave_response["web"]["results"]
        .as_array()
        .unwrap_or(&vec![])
        .iter()
        .filter_map(|item| {
            Some(SearchResult {
                title: item["title"].as_str()?.to_string(),
                url: item["url"].as_str()?.to_string(),
                description: item["description"].as_str().unwrap_or("").to_string(),
            })
        })
        .collect();

    let total = results.len();

    tracing::info!("Web search completed: query='{}', results={}", params.q, total);

    Ok(Json(SearchResponse {
        query: params.q,
        results,
        total,
    }))
}
