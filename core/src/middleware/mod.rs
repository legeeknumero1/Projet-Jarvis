// Middleware pour traçage, CORS, rate limiting, etc.
// Sera implémenté dans les futures versions

pub struct RequestContext {
    pub request_id: String,
    pub user_id: Option<String>,
    pub timestamp: chrono::DateTime<chrono::Utc>,
}

impl RequestContext {
    pub fn new() -> Self {
        Self {
            request_id: uuid::Uuid::new_v4().to_string(),
            user_id: None,
            timestamp: chrono::Utc::now(),
        }
    }
}
