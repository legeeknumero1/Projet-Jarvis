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
#include <atomic>

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
// Ring Buffer (SPSC Lock-free)
// ============================================================================

template<typename T>
class RingBuffer {
public:
    explicit RingBuffer(size_t capacity) {
        // Round up to next power of 2
        size_t real_cap = 1;
        while (real_cap < capacity) real_cap <<= 1;
        capacity_ = real_cap;
        mask_ = real_cap - 1;
        buffer_.resize(real_cap);
    }

    ~RingBuffer() = default;

    bool push(const T& item) {
        const size_t head = head_.load(std::memory_order_relaxed);
        const size_t next_head = (head + 1) & mask_;
        
        if (next_head == tail_.load(std::memory_order_acquire)) {
            return false;
        }
        
        buffer_[head] = item;
        head_.store(next_head, std::memory_order_release);
        return true;
    }

    bool pop(T& item) {
        const size_t tail = tail_.load(std::memory_order_relaxed);
        
        if (tail == head_.load(std::memory_order_acquire)) {
            return false;
        }
        
        item = buffer_[tail];
        tail_.store((tail + 1) & mask_, std::memory_order_release);
        return true;
    }

    size_t size() const {
        size_t head = head_.load(std::memory_order_relaxed);
        size_t tail = tail_.load(std::memory_order_relaxed);
        return (head - tail) & mask_;
    }

    bool empty() const {
        return head_.load(std::memory_order_relaxed) == tail_.load(std::memory_order_relaxed);
    }

    bool full() const {
        size_t next_head = (head_.load(std::memory_order_relaxed) + 1) & mask_;
        return next_head == tail_.load(std::memory_order_relaxed);
    }

private:
    std::vector<T> buffer_;
    size_t capacity_;
    size_t mask_;
    std::atomic<size_t> head_{0};
    std::atomic<size_t> tail_{0};
};

// ============================================================================
// DSP Pipeline
// ============================================================================

class DSPPipeline {
public:
    DSPPipeline();
    ~DSPPipeline();

    void init(const AudioConfig& config);

    /// Process audio frame (Zero-Copy)
    void process(float* buffer, size_t frames);

    AudioStats get_stats() const;

private:
    void suppress_noise(float* buffer, size_t frames);
    void cancel_echo(float* buffer, size_t frames);
    void normalize_gain(float* buffer, size_t frames);

    AudioConfig config_;
    AudioStats stats_;

    std::vector<float> noise_profile_;
    std::vector<float> echo_buffer_;
    float lms_step_size_{0.01f};
    float peak_level_{0.0f};
};

// ============================================================================
// Buffer Manager
// ============================================================================

class BufferManager {
public:
    BufferManager(size_t queue_depth = 16);
    ~BufferManager();

    AudioBuffer* get_input_buffer();
    bool enqueue_for_processing(AudioBuffer* buffer);
    bool dequeue_processed(AudioBuffer* buffer);
    void release_buffer(AudioBuffer* buffer);
    size_t get_queue_depth() const;

private:
    std::unique_ptr<RingBuffer<AudioBuffer*>> input_queue_;
    std::unique_ptr<RingBuffer<AudioBuffer*>> output_queue_;

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

    int init(const AudioConfig& config);
    int start();
    int stop();
    bool health_check() const;

    /// Process audio frame (Zero-Copy)
    int process_audio(const float* input, float* output, size_t frames);

    double get_latency_ms() const;
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
