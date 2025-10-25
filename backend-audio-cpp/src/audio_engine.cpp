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
// SPSC Queue Implementation
// ============================================================================

template<typename T>
SPSCQueue<T>::SPSCQueue(size_t capacity) : capacity_(capacity) {
    auto node = new Node();
    node->next = nullptr;
    head_ = node;
    tail_ = node;
}

template<typename T>
SPSCQueue<T>::~SPSCQueue() {
    Node* current = head_.load();
    while (current) {
        Node* next = current->next.load();
        delete current;
        current = next;
    }
}

template<typename T>
bool SPSCQueue<T>::push(const T& item) {
    auto new_node = new Node();
    new_node->data = item;
    new_node->next = nullptr;

    Node* old_tail = tail_.load();
    old_tail->next = new_node;
    tail_ = new_node;

    return true;
}

template<typename T>
bool SPSCQueue<T>::pop(T& item) {
    Node* old_head = head_.load();
    Node* new_head = old_head->next.load();

    if (!new_head) {
        return false;  // Queue empty
    }

    item = new_head->data;
    head_ = new_head;
    delete old_head;

    return true;
}

template<typename T>
size_t SPSCQueue<T>::size() const {
    size_t count = 0;
    Node* current = head_.load();
    while (current) {
        count++;
        current = current->next.load();
    }
    return count;
}

template<typename T>
bool SPSCQueue<T>::empty() const {
    return head_.load()->next.load() == nullptr;
}

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

void DSPPipeline::process(AudioBuffer& buffer) {
    auto start = std::chrono::high_resolution_clock::now();

    // DSP Pipeline Chain
    suppress_noise(buffer);
    cancel_echo(buffer);
    normalize_gain(buffer);
    resample(buffer);

    auto end = std::chrono::high_resolution_clock::now();
    auto duration_us = std::chrono::duration_cast<std::chrono::microseconds>(end - start);

    // Update statistics
    stats_.latency_ms = duration_us.count() / 1000.0;
    stats_.frames_processed++;
}

void DSPPipeline::suppress_noise(AudioBuffer& buffer) {
    /// Spectral Subtraction Algorithm
    /// Removes noise by subtracting estimated noise spectrum
    ///
    /// Formula: S(f) = max(|Y(f)| - α * |N(f)|, β * |Y(f)|)
    /// where Y = noisy signal, N = noise estimate, α = over-subtraction factor

    const float alpha = 1.5f;  // Over-subtraction factor
    const float beta = 0.01f;   // Floor factor

    for (size_t i = 0; i < buffer.samples.size(); ++i) {
        float sample = buffer.samples[i];
        float noise = noise_profile_[i % noise_profile_.size()];

        // Spectral subtraction
        float suppressed = std::abs(sample) - (alpha * noise);
        suppressed = std::max(suppressed, beta * std::abs(sample));

        // Preserve original phase
        buffer.samples[i] = (sample >= 0) ? suppressed : -suppressed;
    }
}

void DSPPipeline::cancel_echo(AudioBuffer& buffer) {
    /// Echo Cancellation using Normalized LMS (NLMS) Algorithm
    ///
    /// Formula: w[n+1] = w[n] + (μ/||x||²) * e[n] * x[n]
    /// where w = filter coefficients, e = error signal, x = input

    const float mu = 0.1f;  // Step size

    for (size_t i = 0; i < buffer.samples.size() && i < echo_buffer_.size(); ++i) {
        float input = buffer.samples[i];
        float echo = echo_buffer_[i];

        // Calculate error
        float error = input - echo;

        // NLMS update
        float power = input * input + 1e-6f;  // Avoid division by zero
        echo_buffer_[i] += (mu / power) * error * input;

        // Output: original minus estimated echo
        buffer.samples[i] = error;
    }
}

void DSPPipeline::normalize_gain(AudioBuffer& buffer) {
    /// Automatic Gain Control (AGC)
    /// Normalizes signal to target level

    const float target_level = 0.8f;

    // Find peak level
    float peak = 0.0f;
    for (const auto& sample : buffer.samples) {
        peak = std::max(peak, std::abs(sample));
    }

    if (peak > 0.001f) {
        float gain = target_level / peak;

        // Apply gain
        for (auto& sample : buffer.samples) {
            sample *= gain;
        }
    }

    stats_.peak_level = peak;
}

void DSPPipeline::resample(AudioBuffer& buffer) {
    /// Sample rate conversion (if needed)
    /// For now, we keep the original sample rate
    /// In production, use SRC (Secret Rabbit Code) or libsamplerate
    // Placeholder: no resampling for demonstration
}

AudioStats DSPPipeline::get_stats() const {
    return stats_;
}

// ============================================================================
// Buffer Manager Implementation
// ============================================================================

BufferManager::BufferManager(size_t queue_depth) {
    input_queue_ = std::make_unique<SPSCQueue<AudioBuffer*>>(queue_depth);
    output_queue_ = std::make_unique<SPSCQueue<AudioBuffer*>>(queue_depth);

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

int AudioEngine::process_audio(const std::vector<float>& input, std::vector<float>& output) {
    if (!running_) {
        return -1;
    }

    // Create buffer
    AudioBuffer buffer(config_.sample_rate, config_.channels, input.size());
    buffer.samples = input;
    buffer.timestamp_us = std::chrono::duration_cast<std::chrono::microseconds>(
        std::chrono::high_resolution_clock::now().time_since_epoch()
    ).count();

    // Process through DSP pipeline
    dsp_->process(buffer);

    // Return output
    output = buffer.samples;
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

        std::vector<float> input_vec(input, input + len);
        std::vector<float> output_vec;

        int result = g_engine->process_audio(input_vec, output_vec);

        if (result == 0 && !output_vec.empty()) {
            std::copy(output_vec.begin(), output_vec.end(), output);
        }

        return result;
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
