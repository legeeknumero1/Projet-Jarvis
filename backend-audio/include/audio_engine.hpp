#pragma once

#include <cstdint>
#include <vector>
#include <memory>
#include <string>
#include <functional>
#include <chrono>

namespace jarvis::audio {

// Types d'audio
enum class AudioFormat {
    FLOAT32,
    FLOAT64,
    INT16,
    INT32
};

enum class SampleRate {
    SR_16000 = 16000,
    SR_44100 = 44100,
    SR_48000 = 48000,
    SR_96000 = 96000
};

// Configuration audio
struct AudioConfig {
    SampleRate sample_rate = SampleRate::SR_16000;
    uint32_t channels = 1;
    AudioFormat format = AudioFormat::FLOAT32;
    uint32_t buffer_size = 512;  // < 32ms à 16kHz

    float latency_ms() const {
        return (buffer_size * 1000.0f) / static_cast<float>(sample_rate);
    }
};

// Callback pour traitement audio
using AudioCallback = std::function<void(const float*, size_t frames, int64_t timestamp)>;

// Statistiques temps réel
struct AudioStats {
    float cpu_usage_percent = 0.0f;
    float latency_ms = 0.0f;
    uint64_t processed_frames = 0;
    uint64_t dropped_frames = 0;
    std::chrono::steady_clock::time_point last_update;
};

// Moteur audio principal
class AudioEngine {
public:
    explicit AudioEngine(const AudioConfig& config);
    ~AudioEngine();

    // Cycle de vie
    void start();
    void stop();
    bool is_running() const;

    // STT (Speech-to-Text)
    struct TranscriptionResult {
        std::string text;
        float confidence = 0.0f;
        std::vector<std::pair<std::string, std::pair<float, float>>> words;  // word, (start, end)
        int64_t duration_ms = 0;
    };

    TranscriptionResult transcribe(const std::vector<float>& audio_data);

    // TTS (Text-to-Speech)
    struct SynthesisResult {
        std::vector<float> audio_samples;
        int sample_rate = 0;
        int duration_ms = 0;
    };

    SynthesisResult synthesize(const std::string& text, const std::string& voice = "fr_FR-upmc-medium");

    // Traitement audio temps réel
    void process_realtime(const float* input, size_t frames, float* output);

    // Callbacks
    void set_transcription_callback(AudioCallback cb);
    void set_synthesis_callback(AudioCallback cb);

    // Configuration
    const AudioConfig& get_config() const { return config_; }
    void set_config(const AudioConfig& cfg);

    // Monitoring
    const AudioStats& get_stats() const { return stats_; }
    void reset_stats();

    // Audio I/O
    void enable_microphone(bool enable);
    void enable_speaker(bool enable);
    float get_input_level() const;
    float get_output_level() const;

private:
    AudioConfig config_;
    AudioStats stats_;

    class Impl;
    std::unique_ptr<Impl> pimpl_;

    void update_stats_();
    void process_pipeline_(const float* input, size_t frames, float* output);
};

// DSP Pipeline (filtrage, normalisation, etc)
class DSPPipeline {
public:
    explicit DSPPipeline(const AudioConfig& config);

    void process(float* data, size_t frames);

    // Filtres
    void enable_noise_suppression(bool enable);
    void enable_echo_cancellation(bool enable);
    void enable_normalization(bool enable);
    void set_gain_db(float db);

private:
    AudioConfig config_;
    bool ns_enabled_ = false;
    bool ec_enabled_ = false;
    bool norm_enabled_ = false;
    float gain_linear_ = 1.0f;

    void apply_hpf_(float* data, size_t frames);
    void apply_agc_(float* data, size_t frames);
};

// Gestionnaire de buffer circulaire (ultra-rapide)
class AudioBuffer {
public:
    explicit AudioBuffer(size_t capacity);

    size_t write(const float* data, size_t frames);
    size_t read(float* data, size_t frames);
    size_t available_read() const;
    size_t available_write() const;

    void clear();

private:
    std::vector<float> buffer_;
    size_t write_pos_ = 0;
    size_t read_pos_ = 0;
    size_t fill_count_ = 0;
};

}  // namespace jarvis::audio

// Interface C pour FFI Rust
extern "C" {
    typedef struct {
        uint32_t sample_rate;
        uint32_t channels;
        uint32_t buffer_size;
    } AudioConfigC;

    typedef struct {
        const char* text;
        float confidence;
        int64_t duration_ms;
    } TranscriptionResultC;

    // Opaque handle
    typedef void* AudioEngineHandle;

    // API C
    AudioEngineHandle audio_engine_create(AudioConfigC config);
    void audio_engine_destroy(AudioEngineHandle handle);
    void audio_engine_start(AudioEngineHandle handle);
    void audio_engine_stop(AudioEngineHandle handle);

    TranscriptionResultC audio_engine_transcribe(AudioEngineHandle handle, const float* data, size_t frames);
    float* audio_engine_synthesize(AudioEngineHandle handle, const char* text, int* out_frames);
    void audio_engine_process_realtime(AudioEngineHandle handle, const float* input, size_t frames, float* output);
}