use whisper_rs::{WhisperContext, WhisperContextParameters, FullParams, SamplingStrategy};
use anyhow::{Result, Context};
use std::path::Path;
use tracing::{info, error};

pub struct SttNativeService {
    ctx: Option<WhisperContext>,
}

impl SttNativeService {
    pub fn new(model_path: &str) -> Result<Self> {
        if !Path::new(model_path).exists() {
            anyhow::bail!("Whisper model file not found at: {}", model_path);
        }

        info!(" Loading native Whisper model from: {}", model_path);
        let ctx = WhisperContext::new_with_params(
            model_path,
            WhisperContextParameters::default()
        ).context("Failed to load Whisper context")?;

        Ok(Self { ctx: Some(ctx) })
    }

    pub fn new_dummy() -> Self {
        Self { ctx: None }
    }

    pub fn transcribe(&self, audio_data: &[f32]) -> Result<String> {
        let ctx = self.ctx.as_ref().context("STT service not initialized (model missing)")?;

        let mut params = FullParams::new(SamplingStrategy::Greedy { best_of: 1 });
        
        params.set_language(Some("fr"));
        params.set_suppress_non_speech_tokens(true);
        params.set_print_special(false);
        params.set_print_progress(false);
        params.set_print_realtime(false);
        params.set_print_timestamps(false);

        let mut state = ctx.create_state().context("Failed to create state")?;
        
        state.full(params, audio_data).context("Failed to run transcription")?;

        let mut result = String::new();
        let num_segments = state.full_n_segments().context("Failed to get segments")?;

        for i in 0..num_segments {
            if let Ok(segment) = state.full_get_segment_text(i) {
                // Filter out common hallucinations
                let cleaned = segment.replace("[Musique]", "")
                                    .replace("[musique]", "")
                                    .replace("[SILENCE]", "")
                                    .trim()
                                    .to_string();
                if !cleaned.is_empty() {
                    result.push_str(&cleaned);
                    result.push(' ');
                }
            }
        }

        let final_text = result.trim().to_string();
        if final_text.is_empty() {
            Ok("".to_string())
        } else {
            Ok(final_text)
        }
    }
}
