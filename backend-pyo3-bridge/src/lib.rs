/// PyO3 Bridge - High-performance Rust-Python integration
/// Provides native Python bindings for Jarvis core functionality
use pyo3::prelude::*;
use pyo3::exceptions::PyRuntimeError;
use serde::{Deserialize, Serialize};

/// Audio processing results
#[pyclass]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct AudioResult {
    #[pyo3(get, set)]
    pub samples: Vec<f32>,
    #[pyo3(get, set)]
    pub sample_rate: u32,
    #[pyo3(get, set)]
    pub latency_ms: f64,
}

#[pymethods]
impl AudioResult {
    #[new]
    fn new(samples: Vec<f32>, sample_rate: u32, latency_ms: f64) -> Self {
        Self {
            samples,
            sample_rate,
            latency_ms,
        }
    }

    fn __repr__(&self) -> String {
        format!(
            "AudioResult(samples={}, sample_rate={}, latency_ms={:.2})",
            self.samples.len(),
            self.sample_rate,
            self.latency_ms
        )
    }
}

/// Process audio through Rust DSP pipeline
#[pyfunction]
fn process_audio(samples: Vec<f32>, sample_rate: u32) -> PyResult<AudioResult> {
    // Simulate DSP processing (in real implementation, call C++ audio engine)
    let start = std::time::Instant::now();

    // Simple gain normalization
    let max_val = samples.iter().fold(0.0f32, |a, &b| a.max(b.abs()));
    let processed: Vec<f32> = if max_val > 0.0 {
        samples.iter().map(|&s| s / max_val * 0.8).collect()
    } else {
        samples
    };

    let latency_ms = start.elapsed().as_secs_f64() * 1000.0;

    Ok(AudioResult {
        samples: processed,
        sample_rate,
        latency_ms,
    })
}

/// Call Ollama LLM via Rust HTTP client
#[pyfunction]
fn call_ollama(prompt: String, model: String) -> PyResult<String> {
    // Use blocking reqwest for synchronous Python API
    let client = reqwest::blocking::Client::new();

    let payload = serde_json::json!({
        "model": model,
        "prompt": prompt,
        "stream": false,
    });

    let response = client
        .post("http://localhost:11434/api/generate")
        .json(&payload)
        .send()
        .map_err(|e| PyRuntimeError::new_err(format!("HTTP error: {}", e)))?;

    let result: serde_json::Value = response
        .json()
        .map_err(|e| PyRuntimeError::new_err(format!("JSON error: {}", e)))?;

    let text = result["response"]
        .as_str()
        .unwrap_or("")
        .to_string();

    Ok(text)
}

/// Fast text processing utilities
#[pyclass]
pub struct TextProcessor;

#[pymethods]
impl TextProcessor {
    #[new]
    fn new() -> Self {
        Self
    }

    /// Count words (faster than Python split)
    fn count_words(&self, text: &str) -> usize {
        text.split_whitespace().count()
    }

    /// Calculate text similarity (basic implementation)
    fn similarity(&self, text1: &str, text2: &str) -> f32 {
        let words1: std::collections::HashSet<&str> = text1.split_whitespace().collect();
        let words2: std::collections::HashSet<&str> = text2.split_whitespace().collect();

        let intersection = words1.intersection(&words2).count();
        let union = words1.union(&words2).count();

        if union == 0 {
            0.0
        } else {
            intersection as f32 / union as f32
        }
    }

    /// Extract keywords (simple frequency-based)
    fn extract_keywords(&self, text: &str, top_n: usize) -> Vec<String> {
        let mut word_counts: std::collections::HashMap<String, usize> =
            std::collections::HashMap::new();

        for word in text.split_whitespace() {
            let word_lower = word.to_lowercase();
            if word_lower.len() > 3 {
                *word_counts.entry(word_lower).or_insert(0) += 1;
            }
        }

        let mut sorted: Vec<_> = word_counts.into_iter().collect();
        sorted.sort_by(|a, b| b.1.cmp(&a.1));

        sorted
            .into_iter()
            .take(top_n)
            .map(|(word, _)| word)
            .collect()
    }
}

/// Vector operations (faster than NumPy for small vectors)
#[pyclass]
pub struct VectorOps;

#[pymethods]
impl VectorOps {
    #[new]
    fn new() -> Self {
        Self
    }

    /// Dot product
    fn dot(&self, a: Vec<f32>, b: Vec<f32>) -> PyResult<f32> {
        if a.len() != b.len() {
            return Err(PyRuntimeError::new_err("Vectors must have same length"));
        }

        Ok(a.iter().zip(b.iter()).map(|(x, y)| x * y).sum())
    }

    /// Cosine similarity
    fn cosine_similarity(&self, a: Vec<f32>, b: Vec<f32>) -> PyResult<f32> {
        if a.len() != b.len() {
            return Err(PyRuntimeError::new_err("Vectors must have same length"));
        }

        let dot: f32 = a.iter().zip(b.iter()).map(|(x, y)| x * y).sum();
        let norm_a: f32 = a.iter().map(|x| x * x).sum::<f32>().sqrt();
        let norm_b: f32 = b.iter().map(|x| x * x).sum::<f32>().sqrt();

        if norm_a == 0.0 || norm_b == 0.0 {
            Ok(0.0)
        } else {
            Ok(dot / (norm_a * norm_b))
        }
    }

    /// Normalize vector to unit length
    fn normalize(&self, vec: Vec<f32>) -> Vec<f32> {
        let norm: f32 = vec.iter().map(|x| x * x).sum::<f32>().sqrt();

        if norm == 0.0 {
            vec
        } else {
            vec.iter().map(|x| x / norm).collect()
        }
    }
}

/// Cache manager using Rust HashMap (thread-safe)
#[pyclass]
pub struct RustCache {
    cache: std::sync::Arc<std::sync::Mutex<std::collections::HashMap<String, String>>>,
}

#[pymethods]
impl RustCache {
    #[new]
    fn new() -> Self {
        Self {
            cache: std::sync::Arc::new(std::sync::Mutex::new(std::collections::HashMap::new())),
        }
    }

    fn set(&self, key: String, value: String) {
        let mut cache = self.cache.lock().unwrap();
        cache.insert(key, value);
    }

    fn get(&self, key: String) -> Option<String> {
        let cache = self.cache.lock().unwrap();
        cache.get(&key).cloned()
    }

    fn delete(&self, key: String) -> bool {
        let mut cache = self.cache.lock().unwrap();
        cache.remove(&key).is_some()
    }

    fn clear(&self) {
        let mut cache = self.cache.lock().unwrap();
        cache.clear();
    }

    fn size(&self) -> usize {
        let cache = self.cache.lock().unwrap();
        cache.len()
    }
}

/// PyO3 module definition
#[pymodule]
fn jarvis_bridge(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<AudioResult>()?;
    m.add_class::<TextProcessor>()?;
    m.add_class::<VectorOps>()?;
    m.add_class::<RustCache>()?;
    m.add_function(wrap_pyfunction!(process_audio, m)?)?;
    m.add_function(wrap_pyfunction!(call_ollama, m)?)?;
    Ok(())
}
