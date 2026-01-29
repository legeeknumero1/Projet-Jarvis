use jarvis_audio::AudioEngine;
use std::sync::{Arc, Mutex};

pub struct AudioEngineClient {
    engine: Arc<Mutex<AudioEngine>>,
}

impl AudioEngineClient {
    pub fn new() -> Self {
        let mut engine = AudioEngine::new(16000, 1);
        engine.start();
        Self {
            engine: Arc::new(Mutex::new(engine)),
        }
    }

    pub async fn health_check(&self) -> Result<serde_json::Value, String> {
        let engine = self.engine.lock().map_err(|e| e.to_string())?;
        Ok(serde_json::json!({
            "status": if engine.get_health() { "healthy" } else { "stopped" },
            "engine": "rust-native-v2"
        }))
    }

    pub async fn process_audio_samples(&self, samples: &mut [f32]) -> Result<(), String> {
        let engine = self.engine.lock().map_err(|e| e.to_string())?;
        engine.process(samples)
    }
}