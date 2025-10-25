//! Handlers HTTP pour l'API Jarvis Rust
//! 
//! Handlers Axum équivalents aux routes FastAPI Python
//! avec validation stricte et gestion d'erreurs

pub mod chat;
pub mod health;
pub mod voice;

// Ré-exports pour faciliter l'utilisation
pub use chat::*;
pub use health::*;
pub use voice::*;