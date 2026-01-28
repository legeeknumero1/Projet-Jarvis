# Jarvis PyO3 Bridge

High-performance Rust-Python integration for Jarvis AI Assistant.

## Features

- **Audio Processing**: Native Rust DSP pipeline exposed to Python
- **LLM Client**: Fast Ollama HTTP client via Rust reqwest
- **Text Processing**: Optimized text analysis (word count, similarity, keywords)
- **Vector Operations**: Fast vector math (dot product, cosine similarity, normalize)
- **Rust Cache**: Thread-safe HashMap cache accessible from Python

## Installation

```bash
# Install maturin
pip install maturin

# Build and install the extension
cd backend-pyo3-bridge
maturin develop --release
```

## Usage

```python
import jarvis_bridge

# Audio processing
audio = jarvis_bridge.process_audio([0.1, 0.2, 0.3], sample_rate=48000)
print(audio.latency_ms)

# LLM call
response = jarvis_bridge.call_ollama("Hello!", "llama2")
print(response)

# Text processing
text_proc = jarvis_bridge.TextProcessor()
word_count = text_proc.count_words("Hello world from Rust")
keywords = text_proc.extract_keywords("machine learning AI deep learning", top_n=3)

# Vector operations
vec_ops = jarvis_bridge.VectorOps()
similarity = vec_ops.cosine_similarity([1.0, 2.0, 3.0], [1.0, 2.0, 3.0])

# Rust cache
cache = jarvis_bridge.RustCache()
cache.set("key", "value")
print(cache.get("key"))
```

## Performance Benefits

- **10-100x faster** than pure Python for numerical operations
- **Sub-millisecond latency** for audio processing
- **Zero-copy** data transfer where possible
- **Thread-safe** cache without GIL limitations

## Building for Production

```bash
# Build optimized wheel
maturin build --release

# Install wheel
pip install target/wheels/jarvis_bridge-*.whl
```
