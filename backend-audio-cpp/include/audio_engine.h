/// Audio Engine Header - Phase 2
/// DSP/FFmpeg/PortAudio + SPSC Lock-free Queues
///
/// Purpose: Sub-millisecond audio processing
/// - Noise suppression
/// - Echo cancellation
/// - Gain normalization
/// - Sample rate conversion

#ifndef AUDIO_ENGINE_H
#define AUDIO_ENGINE_H

#include <cstdint>
#include <vector>
#include <memory>

namespace jarvis::audio {

// ============================================================================
// Audio Buffer Structures
// ============================================================================

/// Audio frame configuration
struct AudioConfig {
    uint32_t sample_rate;      // 16000, 48000, etc.
    uint16_t channels;          // 1 (mono), 2 (stereo)
    uint16_t bit_depth;         // 16, 24, 32 bit
};

/// Audio buffer for processing
struct AudioBuffer {
    std::vector<float> samples;
    uint32_t sample_rate;
    uint16_t channels;
    uint64_t timestamp_us;      // Microseconds (latency tracking)

    AudioBuffer() = default;
    AudioBuffer(uint32_t sr, uint16_t ch, size_t num_samples)
        : sample_rate(sr), channels(ch), timestamp_us(0) {
        samples.reserve(num_samples);
    }
};

/// DSP processing statistics
struct AudioStats {
    double latency_ms;          // Processing latency in milliseconds
    double peak_level;          // Peak signal level
    double avg_level;           // Average signal level
    uint64_t frames_processed;
};

// ============================================================================
// SPSC (Single Producer Single Consumer) Lock-free Queue
// ============================================================================

template<typename T>
class SPSCQueue {
public:
    explicit SPSCQueue(size_t capacity = 128);
    ~SPSCQueue();

    /// Try to push item (returns false if queue full - non-blocking)
    bool push(const T& item);

    /// Try to pop item (returns false if queue empty - non-blocking)
    bool pop(T& item);

    /// Get approximate queue size
    size_t size() const;

    /// Check if queue is empty
    bool empty() const;

private:
    struct Node {
        T data;
        std::atomic<Node*> next{nullptr};
    };

    std::atomic<Node*> head_;
    std::atomic<Node*> tail_;
    size_t capacity_;
};

// ============================================================================
// DSP Pipeline
// ============================================================================

class DSPPipeline {
public:
    DSPPipeline();
    ~DSPPipeline();

    /// Initialize DSP pipeline with audio config
    void init(const AudioConfig& config);

    /// Process audio frame through DSP chain
    /// Order: Noise Suppression -> Echo Cancellation -> Gain -> Resample
    void process(AudioBuffer& buffer);

    /// Get processing statistics
    AudioStats get_stats() const;

private:
    /// Noise suppression (Spectral Subtraction)
    void suppress_noise(AudioBuffer& buffer);

    /// Echo cancellation (Normalized LMS algorithm)
    void cancel_echo(AudioBuffer& buffer);

    /// Gain normalization (Peak detection + normalization)
    void normalize_gain(AudioBuffer& buffer);

    /// Sample rate conversion (if needed)
    void resample(AudioBuffer& buffer);

    AudioConfig config_;
    AudioStats stats_;

    // DSP state
    std::vector<float> noise_profile_;
    std::vector<float> echo_buffer_;
    float lms_step_size_{0.01f};
    float peak_level_{0.0f};
};

// ============================================================================
// Buffer Manager (using SPSC queues)
// ============================================================================

class BufferManager {
public:
    BufferManager(size_t queue_depth = 16);
    ~BufferManager();

    /// Get input buffer for recording
    AudioBuffer* get_input_buffer();

    /// Submit buffer to processing queue
    bool enqueue_for_processing(AudioBuffer* buffer);

    /// Get processed buffer
    bool dequeue_processed(AudioBuffer* buffer);

    /// Release buffer back to pool
    void release_buffer(AudioBuffer* buffer);

    /// Get queue statistics
    size_t get_queue_depth() const;

private:
    std::unique_ptr<SPSCQueue<AudioBuffer*>> input_queue_;
    std::unique_ptr<SPSCQueue<AudioBuffer*>> output_queue_;

    std::vector<std::unique_ptr<AudioBuffer>> buffer_pool_;
    std::atomic<size_t> available_buffers_;
};

// ============================================================================
// Audio Engine (main interface)
// ============================================================================

class AudioEngine {
public:
    AudioEngine();
    ~AudioEngine();

    /// Initialize audio engine with configuration
    int init(const AudioConfig& config);

    /// Start audio processing
    int start();

    /// Stop audio processing
    int stop();

    /// Health check
    bool health_check() const;

    /// Process audio frame
    int process_audio(const std::vector<float>& input, std::vector<float>& output);

    /// Get latency in milliseconds
    double get_latency_ms() const;

    /// Get statistics
    AudioStats get_stats() const;

private:
    AudioConfig config_;
    std::unique_ptr<DSPPipeline> dsp_;
    std::unique_ptr<BufferManager> buffer_mgr_;

    bool initialized_{false};
    bool running_{false};

    uint64_t process_count_{0};
};

// ============================================================================
// C FFI Exports (for Rust integration)
// ============================================================================

extern "C" {
    // Initialize audio engine
    int audio_engine_init();

    // Process frame (input/output as float pointers)
    int audio_engine_process(const float* input, float* output, uint32_t len);

    // Get latency in milliseconds
    double audio_engine_get_latency();

    // Cleanup
    int audio_engine_cleanup();
}

} // namespace jarvis::audio

#endif // AUDIO_ENGINE_H
