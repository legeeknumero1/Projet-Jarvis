use prometheus_client::encoding::text::encode;
use prometheus_client::metrics::counter::Counter;
use prometheus_client::metrics::gauge::Gauge;
use prometheus_client::metrics::histogram::{exponential_buckets, Histogram};
use prometheus_client::registry::Registry;
use std::sync::Arc;
use parking_lot::RwLock;

/// Metrics collector for jarvis-secretsd
#[derive(Clone)]
pub struct Metrics {
    pub registry: Arc<RwLock<Registry>>,

    // Request metrics
    pub http_requests_total: Counter,
    pub http_requests_success: Counter,
    pub http_requests_error: Counter,
    pub http_request_duration_seconds: Histogram,

    // Secret operations
    pub secrets_created: Counter,
    pub secrets_retrieved: Counter,
    pub secrets_rotated: Counter,
    pub secrets_total: Gauge,

    // RBAC metrics
    pub rbac_allowed: Counter,
    pub rbac_denied: Counter,

    // Crypto metrics
    pub encryption_ops: Counter,
    pub decryption_ops: Counter,
    pub decryption_errors: Counter,

    // Audit metrics
    pub audit_events: Counter,
    pub audit_errors: Counter,
}

impl Metrics {
    pub fn new() -> Self {
        let mut registry = Registry::default();

        // Request metrics
        let http_requests_total = Counter::default();
        registry.register(
            "http_requests_total",
            "Total HTTP requests received",
            http_requests_total.clone(),
        );

        let http_requests_success = Counter::default();
        registry.register(
            "http_requests_success",
            "Successful HTTP requests",
            http_requests_success.clone(),
        );

        let http_requests_error = Counter::default();
        registry.register(
            "http_requests_error",
            "Failed HTTP requests",
            http_requests_error.clone(),
        );

        let http_request_duration_seconds = Histogram::new(exponential_buckets(0.001, 2.0, 10));
        registry.register(
            "http_request_duration_seconds",
            "HTTP request duration in seconds",
            http_request_duration_seconds.clone(),
        );

        // Secret operations
        let secrets_created = Counter::default();
        registry.register(
            "secrets_created_total",
            "Total secrets created",
            secrets_created.clone(),
        );

        let secrets_retrieved = Counter::default();
        registry.register(
            "secrets_retrieved_total",
            "Total secrets retrieved",
            secrets_retrieved.clone(),
        );

        let secrets_rotated = Counter::default();
        registry.register(
            "secrets_rotated_total",
            "Total secrets rotated",
            secrets_rotated.clone(),
        );

        let secrets_total = Gauge::default();
        registry.register(
            "secrets_total",
            "Current number of secrets in vault",
            secrets_total.clone(),
        );

        // RBAC metrics
        let rbac_allowed = Counter::default();
        registry.register(
            "rbac_allowed_total",
            "RBAC policy checks that allowed access",
            rbac_allowed.clone(),
        );

        let rbac_denied = Counter::default();
        registry.register(
            "rbac_denied_total",
            "RBAC policy checks that denied access",
            rbac_denied.clone(),
        );

        // Crypto metrics
        let encryption_ops = Counter::default();
        registry.register(
            "encryption_ops_total",
            "Total encryption operations",
            encryption_ops.clone(),
        );

        let decryption_ops = Counter::default();
        registry.register(
            "decryption_ops_total",
            "Total decryption operations",
            decryption_ops.clone(),
        );

        let decryption_errors = Counter::default();
        registry.register(
            "decryption_errors_total",
            "Total decryption failures",
            decryption_errors.clone(),
        );

        // Audit metrics
        let audit_events = Counter::default();
        registry.register(
            "audit_events_total",
            "Total audit events logged",
            audit_events.clone(),
        );

        let audit_errors = Counter::default();
        registry.register(
            "audit_errors_total",
            "Total audit logging errors",
            audit_errors.clone(),
        );

        Metrics {
            registry: Arc::new(RwLock::new(registry)),
            http_requests_total,
            http_requests_success,
            http_requests_error,
            http_request_duration_seconds,
            secrets_created,
            secrets_retrieved,
            secrets_rotated,
            secrets_total,
            rbac_allowed,
            rbac_denied,
            encryption_ops,
            decryption_ops,
            decryption_errors,
            audit_events,
            audit_errors,
        }
    }

    /// Encode metrics in Prometheus text format
    pub fn encode(&self) -> String {
        let mut buffer = String::new();
        let registry = self.registry.read();
        encode(&mut buffer, &registry).unwrap();
        buffer
    }

    /// Update secrets_total gauge from vault stats
    pub fn update_secrets_total(&self, count: usize) {
        self.secrets_total.set(count as i64);
    }

    /// Record HTTP request
    pub fn record_http_request(&self, duration_seconds: f64, success: bool) {
        self.http_requests_total.inc();
        self.http_request_duration_seconds.observe(duration_seconds);

        if success {
            self.http_requests_success.inc();
        } else {
            self.http_requests_error.inc();
        }
    }

    /// Record RBAC decision
    pub fn record_rbac(&self, allowed: bool) {
        if allowed {
            self.rbac_allowed.inc();
        } else {
            self.rbac_denied.inc();
        }
    }
}

impl Default for Metrics {
    fn default() -> Self {
        Self::new()
    }
}
