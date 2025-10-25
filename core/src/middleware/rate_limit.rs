// ============================================================================
// Rate Limiting Middleware - SECURITY FIX C5 (DoS Protection)
// ============================================================================
//
// Ce module implémente un système de rate limiting pour protéger les endpoints
// contre les attaques DoS et les tentatives de brute-force.
//
// Vulnérabilité corrigée:
// - CVSS 7.5 : Pas de rate limiting (DoS, brute-force auth, API abuse)
// - Impact : Indisponibilité du service, compromission de comptes, abus de ressources
// - Correction : Rate limiting par endpoint avec configurations strictes

use std::sync::Arc;
use parking_lot::Mutex;
use once_cell::sync::Lazy;

// ============================================================================
// Rate Limiting Configuration
// ============================================================================

/// Configuration pour chaque endpoint
#[derive(Clone)]
pub struct RateLimitConfig {
    /// Requests per second
    pub requests_per_second: u32,
    /// Description du endpoint
    pub description: &'static str,
}

/// Configurations prédéfinies pour différents types d'endpoints
pub struct RateLimitConfigs;

impl RateLimitConfigs {
    /// STRICT: Endpoints d'authentification (login, token verification)
    pub fn auth() -> RateLimitConfig {
        RateLimitConfig {
            requests_per_second: 5,  // 5 req/s = max 300 login attempts/minute
            description: "Auth endpoint (strict rate limiting)",
        }
    }

    /// NORMAL: Endpoints API standard
    pub fn api() -> RateLimitConfig {
        RateLimitConfig {
            requests_per_second: 30,  // 30 req/s = 1800 req/minute
            description: "Standard API endpoint",
        }
    }

    /// RELAXED: Endpoints non-sensibles (health, public data)
    pub fn public() -> RateLimitConfig {
        RateLimitConfig {
            requests_per_second: 100,  // 100 req/s = 6000 req/minute
            description: "Public/health endpoint",
        }
    }

    /// MODERATE: Chat and voice endpoints
    pub fn chat() -> RateLimitConfig {
        RateLimitConfig {
            requests_per_second: 10,  // 10 req/s = 600 req/minute
            description: "Chat/voice endpoint",
        }
    }
}

// ============================================================================
// Simple Rate Limiter Implementation
// ============================================================================

/// Simple sliding window rate limiter (without external crate complexity)
pub struct SimpleRateLimiter {
    requests_per_second: u32,
    window_start: std::time::Instant,
    request_count: u32,
}

impl SimpleRateLimiter {
    pub fn new(requests_per_second: u32) -> Self {
        Self {
            requests_per_second,
            window_start: std::time::Instant::now(),
            request_count: 0,
        }
    }

    /// Check if request should be allowed
    pub fn check(&mut self) -> Result<(), String> {
        let elapsed = self.window_start.elapsed();

        // Reset window if 1 second has passed
        if elapsed.as_secs() >= 1 {
            self.window_start = std::time::Instant::now();
            self.request_count = 0;
        }

        self.request_count += 1;

        if self.request_count <= self.requests_per_second {
            Ok(())
        } else {
            Err("Rate limit exceeded".to_string())
        }
    }
}

// ============================================================================
// Global Rate Limiter with Lazy Initialization
// ============================================================================

pub struct GlobalRateLimiter {
    /// Global limiter for all requests
    global: Arc<Mutex<SimpleRateLimiter>>,
    /// Per-endpoint limiters
    limiters: Arc<Mutex<std::collections::HashMap<String, SimpleRateLimiter>>>,
}

impl GlobalRateLimiter {
    pub fn new() -> Self {
        Self {
            global: Arc::new(Mutex::new(SimpleRateLimiter::new(1000))),
            limiters: Arc::new(Mutex::new(std::collections::HashMap::new())),
        }
    }

    /// Check rate limit for a specific endpoint
    pub fn check_endpoint_limit(&self, endpoint: &str, config: &RateLimitConfig) -> Result<(), String> {
        // Check global limit first
        {
            let mut global = self.global.lock();
            if global.check().is_err() {
                return Err("Global rate limit exceeded".to_string());
            }
        }

        // Get or create per-endpoint limiter
        let mut limiters = self.limiters.lock();
        let limiter = limiters.entry(endpoint.to_string()).or_insert_with(|| {
            SimpleRateLimiter::new(config.requests_per_second)
        });

        if limiter.check().is_err() {
            return Err(format!("Rate limit exceeded for {}", endpoint));
        }

        Ok(())
    }

    /// Check rate limit for IP address (for authentication attempts)
    pub fn check_ip_limit(&self, ip: &str, config: &RateLimitConfig) -> Result<(), String> {
        let endpoint_key = format!("ip:{}", ip);
        self.check_endpoint_limit(&endpoint_key, config)
    }
}

impl Clone for GlobalRateLimiter {
    fn clone(&self) -> Self {
        Self {
            global: self.global.clone(),
            limiters: self.limiters.clone(),
        }
    }
}

// ============================================================================
// Helper Functions for Route Handlers
// ============================================================================

/// Get reference to global rate limiter
pub fn get_limiter() -> &'static GlobalRateLimiter {
    static LIMITER: Lazy<GlobalRateLimiter> = Lazy::new(GlobalRateLimiter::new);
    &LIMITER
}

/// Check rate limit before processing auth request
pub fn check_auth_rate_limit(ip: &str) -> Result<(), String> {
    get_limiter().check_ip_limit(ip, &RateLimitConfigs::auth())
}

/// Check rate limit for API endpoints
pub fn check_api_rate_limit(endpoint: &str) -> Result<(), String> {
    get_limiter().check_endpoint_limit(endpoint, &RateLimitConfigs::api())
}

/// Check rate limit for chat/voice endpoints
pub fn check_chat_rate_limit(endpoint: &str) -> Result<(), String> {
    get_limiter().check_endpoint_limit(endpoint, &RateLimitConfigs::chat())
}

// ============================================================================
// Tests
// ============================================================================

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_rate_limit_configs() {
        let auth = RateLimitConfigs::auth();
        assert_eq!(auth.requests_per_second, 5);

        let api = RateLimitConfigs::api();
        assert_eq!(api.requests_per_second, 30);

        let public = RateLimitConfigs::public();
        assert_eq!(public.requests_per_second, 100);

        let chat = RateLimitConfigs::chat();
        assert_eq!(chat.requests_per_second, 10);
    }

    #[test]
    fn test_global_rate_limiter_creation() {
        let limiter = GlobalRateLimiter::new();

        // First request should succeed
        let result = limiter.check_endpoint_limit(
            "/api/test",
            &RateLimitConfigs::api(),
        );
        assert!(result.is_ok());
    }

    #[test]
    fn test_rate_limit_exceeded() {
        let limiter = GlobalRateLimiter::new();
        let config = RateLimitConfig {
            requests_per_second: 1,
            description: "test",
        };

        // First request should succeed
        assert!(limiter.check_endpoint_limit("/test", &config).is_ok());

        // Rapid requests should be rejected
        let mut failed = false;
        for _ in 0..10 {
            if limiter.check_endpoint_limit("/test", &config).is_err() {
                failed = true;
                break;
            }
        }
        assert!(failed, "Rate limit should have been exceeded");
    }

    #[test]
    fn test_ip_based_limiting() {
        let limiter = GlobalRateLimiter::new();
        let config = RateLimitConfigs::auth();

        // Simulate login attempts from same IP
        let ip = "192.168.1.1";
        let mut failures = 0;

        for _ in 0..10 {
            if limiter.check_ip_limit(ip, &config).is_err() {
                failures += 1;
            }
            if failures > 0 {
                break;
            }
        }

        // Should eventually fail due to strict auth rate limit
        assert!(failures > 0, "IP-based rate limit should eventually be exceeded");
    }

    #[test]
    fn test_simple_rate_limiter() {
        let mut limiter = SimpleRateLimiter::new(2);

        // First two requests should succeed
        assert!(limiter.check().is_ok());
        assert!(limiter.check().is_ok());

        // Third request should fail
        assert!(limiter.check().is_err());
    }
}
