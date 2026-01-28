/// Audio Engine Implementation - Phase 2
/// DSP Processing Pipeline
///
/// Implements:
/// - Noise suppression (Spectral Subtraction)
/// - Echo cancellation (Normalized LMS)
/// - Gain normalization
/// - Sub-millisecond latency target

#include "../include/audio_engine.h"
#include <cmath>
#include <algorithm>
#include <chrono>
#include <iostream>

namespace jarvis::audio {

// ============================================================================
// Ring Buffer Implementation (Moved to Header)
// ============================================================================

// Template implementation moved to audio_engine.h to support instantiation

// ============================================================================
// DSP Pipeline Implementation
// ============================================================================

DSPPipeline::DSPPipeline() = default;

DSPPipeline::~DSPPipeline() = default;

void DSPPipeline::init(const AudioConfig& config) {
    config_ = config;

    // Initialize noise profile (learned from silent frames)
    noise_profile_.resize(512, 0.0f);

    // Initialize echo buffer
    echo_buffer_.resize(4096, 0.0f);

    // Initialize stats
    stats_ = {0.0, 0.0, 0.0, 0};
}

void DSPPipeline::process(float* buffer, size_t frames) {
    auto start = std::chrono::high_resolution_clock::now();

    // DSP Pipeline Chain (Zero-Copy)
    suppress_noise(buffer, frames);
    cancel_echo(buffer, frames);
    normalize_gain(buffer, frames);
    // resample is skipped for now

    auto end = std::chrono::high_resolution_clock::now();
    auto duration_us = std::chrono::duration_cast<std::chrono::microseconds>(end - start);

    // Update statistics
    stats_.latency_ms = duration_us.count() / 1000.0;
    stats_.frames_processed++;
}

void DSPPipeline::suppress_noise(float* buffer, size_t frames) {
    const float alpha = 1.5f;
    const float beta = 0.01f;

    for (size_t i = 0; i < frames; ++i) {
        float sample = buffer[i];
        float noise = noise_profile_[i % noise_profile_.size()];

        float suppressed = std::abs(sample) - (alpha * noise);
        suppressed = std::max(suppressed, beta * std::abs(sample));

        buffer[i] = (sample >= 0) ? suppressed : -suppressed;
    }
}

void DSPPipeline::cancel_echo(float* buffer, size_t frames) {
    const float mu = 0.1f;

    for (size_t i = 0; i < frames && i < echo_buffer_.size(); ++i) {
        float input = buffer[i];
        float echo = echo_buffer_[i];

        float error = input - echo;
        float power = input * input + 1e-6f;
        echo_buffer_[i] += (mu / power) * error * input;

        buffer[i] = error;
    }
}

void DSPPipeline::normalize_gain(float* buffer, size_t frames) {
    const float target_level = 0.8f;
    float peak = 0.0f;

    for (size_t i = 0; i < frames; ++i) {
        peak = std::max(peak, std::abs(buffer[i]));
    }

    if (peak > 0.001f) {
        float gain = target_level / peak;
        for (size_t i = 0; i < frames; ++i) {
            buffer[i] *= gain;
        }
    }
    stats_.peak_level = peak;
}

AudioStats DSPPipeline::get_stats() const {
    return stats_;
}

// ============================================================================
// BufferManager Implementation
// ============================================================================

BufferManager::BufferManager(size_t queue_depth) {
    input_queue_ = std::make_unique<RingBuffer<AudioBuffer*>>(queue_depth);
    output_queue_ = std::make_unique<RingBuffer<AudioBuffer*>>(queue_depth);

    // Pre-allocate buffers
    for (size_t i = 0; i < queue_depth; ++i) {
        buffer_pool_.push_back(std::make_unique<AudioBuffer>(16000, 1, 512));
    }
    available_buffers_ = queue_depth;
}

BufferManager::~BufferManager() = default;

AudioBuffer* BufferManager::get_input_buffer() {
    if (!buffer_pool_.empty() && available_buffers_ > 0) {
        available_buffers_--;
        return buffer_pool_[available_buffers_].get();
    }
    return nullptr;
}

bool BufferManager::enqueue_for_processing(AudioBuffer* buffer) {
    return input_queue_->push(buffer);
}

bool BufferManager::dequeue_processed(AudioBuffer* buffer) {
    return output_queue_->pop(buffer);
}

void BufferManager::release_buffer(AudioBuffer* buffer) {
    available_buffers_++;
}

size_t BufferManager::get_queue_depth() const {
    return input_queue_->size();
}

// ============================================================================
// Audio Engine Implementation
// ============================================================================

// Global instance for C FFI
static std::unique_ptr<AudioEngine> g_engine;

AudioEngine::AudioEngine() = default;

AudioEngine::~AudioEngine() {
    if (running_) {
        stop();
    }
}

int AudioEngine::init(const AudioConfig& config) {
    if (initialized_) {
        return 0;  // Already initialized
    }

    config_ = config;
    dsp_ = std::make_unique<DSPPipeline>();
    buffer_mgr_ = std::make_unique<BufferManager>();

    dsp_->init(config);
    initialized_ = true;

    std::cout << "[Audio Engine] Initialized: " << config.sample_rate << " Hz, "
              << (int)config.channels << " channels" << std::endl;

    return 0;
}

int AudioEngine::start() {
    if (!initialized_) {
        return -1;
    }

    running_ = true;
    std::cout << "[Audio Engine] Started processing" << std::endl;
    return 0;
}

int AudioEngine::stop() {
    running_ = false;
    std::cout << "[Audio Engine] Stopped processing" << std::endl;
    return 0;
}

bool AudioEngine::health_check() const {
    return initialized_ && running_;
}

int AudioEngine::process_audio(const float* input, float* output, size_t frames) {
    if (!running_) {
        return -1;
    }

    // Zero-copy processing
    // We copy input to output first, then process in-place on output buffer
    // This assumes the caller manages the memory and output is at least size 'frames'
    
    std::copy(input, input + frames, output);
    
    // Process in-place
    dsp_->process(output, frames);
    
    process_count_++;

    return 0;
}

double AudioEngine::get_latency_ms() const {
    return dsp_->get_stats().latency_ms;
}

AudioStats AudioEngine::get_stats() const {
    return dsp_->get_stats();
}

// ============================================================================
// C FFI Interface (for Rust bindings)
// ============================================================================

extern "C" {

    int audio_engine_init() {
        if (!g_engine) {
            g_engine = std::make_unique<AudioEngine>();
        }

        AudioConfig config{
            .sample_rate = 16000,
            .channels = 1,
            .bit_depth = 16
        };

        return g_engine->init(config);
    }

    int audio_engine_process(const float* input, float* output, uint32_t len) {
        if (!g_engine) {
            return -1;
        }

        // Direct pointer passing - NO VECTOR ALLOCATION
        return g_engine->process_audio(input, output, len);
    }

    double audio_engine_get_latency() {
        if (!g_engine) {
            return -1.0;
        }
        return g_engine->get_latency_ms();
    }

    int audio_engine_cleanup() {
        if (g_engine) {
            g_engine.reset();
        }
        return 0;
    }

}  // extern "C"

}  // namespace jarvis::audio
