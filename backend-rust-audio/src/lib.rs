pub mod dsp;

use dsp::{AudioConfig, DspPipeline};
use std::sync::{Arc, Mutex};

pub struct AudioEngine {
    pipeline: Arc<Mutex<DspPipeline>>,
    is_running: bool,
}

impl AudioEngine {
    pub fn new(sample_rate: u32, channels: u16) -> Self {
        let config = AudioConfig { sample_rate, channels };
        Self {
            pipeline: Arc::new(Mutex::new(DspPipeline::new(config))),
            is_running: false,
        }
    }

    pub fn start(&mut self) {
        self.is_running = true;
    }

    pub fn stop(&mut self) {
        self.is_running = false;
    }

    pub fn process(&self, buffer: &mut [f32]) -> Result<(), String> {
        if !self.is_running {
            return Err("Audio engine is not running".to_string());
        }

        let mut pipeline = self.pipeline.lock().map_err(|e| e.to_string())?;
        pipeline.process(buffer);
        Ok(())
    }

    pub fn get_health(&self) -> bool {
        self.is_running
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_engine_initialization() {
        let engine = AudioEngine::new(16000, 1);
        assert!(!engine.get_health());
    }

    #[test]
    fn test_processing_flow() {
        let mut engine = AudioEngine::new(16000, 1);
        engine.start();
        
        let mut buffer = vec![0.5; 1024];
        let result = engine.process(&mut buffer);
        
        assert!(result.is_ok());
        // Le gain devrait avoir normalisé à 0.8 (TARGET_LEVEL dans dsp.rs)
        assert!((buffer[0].abs() - 0.8).abs() < 1e-6);
    }
}