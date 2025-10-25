#include "audio_engine.hpp"
#include <iostream>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <algorithm>
#include <cmath>

namespace jarvis::audio {

// Implémentation privée
class AudioEngine::Impl {
public:
    explicit Impl(const AudioConfig& config)
        : config(config),
          buffer(config.buffer_size * 100),  // 100 buffers de profondeur
          running(false),
          audio_thread(nullptr) {}

    AudioConfig config;
    AudioBuffer buffer;
    DSPPipeline dsp_pipeline{config};
    std::atomic<bool> running;
    std::thread audio_thread;

    AudioCallback transcription_cb;
    AudioCallback synthesis_cb;

    std::mutex mutex;
    std::condition_variable cv;

    // Timers de performance
    std::chrono::steady_clock::time_point last_process_time;
    float avg_latency_ms = 0.0f;
};

// Constructeur
AudioEngine::AudioEngine(const AudioConfig& config)
    : config_(config), pimpl_(std::make_unique<Impl>(config)) {
    std::cout << "[AudioEngine] Initialisation avec config:\n";
    std::cout << "  Sample Rate: " << static_cast<int>(config.sample_rate) << " Hz\n";
    std::cout << "  Channels: " << config.channels << "\n";
    std::cout << "  Buffer Size: " << config.buffer_size << " frames\n";
    std::cout << "  Latency: " << config.latency_ms() << "ms\n";
}

AudioEngine::~AudioEngine() {
    if (is_running()) {
        stop();
    }
}

void AudioEngine::start() {
    if (is_running()) return;

    pimpl_->running = true;
    std::cout << "[AudioEngine] Démarrage du moteur audio...\n";

    // Thread audio temps réel
    pimpl_->audio_thread = std::thread([this]() {
        // Priorité temps réel (best-effort)
        std::cout << "[AudioEngine] Thread audio started\n";

        while (pimpl_->running) {
            auto start = std::chrono::steady_clock::now();

            // Lire depuis le buffer d'entrée
            std::vector<float> input_buffer(config_.buffer_size);
            size_t frames_read = pimpl_->buffer.read(input_buffer.data(), config_.buffer_size);

            if (frames_read > 0) {
                std::vector<float> output_buffer(frames_read);

                // Pipeline DSP
                std::copy(input_buffer.begin(), input_buffer.begin() + frames_read,
                         output_buffer.begin());
                pimpl_->dsp_pipeline.process(output_buffer.data(), frames_read);

                // Callback transcription si disponible
                if (pimpl_->transcription_cb) {
                    pimpl_->transcription_cb(output_buffer.data(), frames_read,
                                           std::chrono::steady_clock::now().time_since_epoch().count());
                }

                stats_.processed_frames += frames_read;
            } else {
                stats_.dropped_frames++;
                std::this_thread::sleep_for(std::chrono::milliseconds(1));
            }

            // Mesure de latence
            auto end = std::chrono::steady_clock::now();
            auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
            pimpl_->avg_latency_ms = (pimpl_->avg_latency_ms * 0.9f) +
                                     (duration.count() / 1000.0f * 0.1f);
            stats_.latency_ms = pimpl_->avg_latency_ms;
        }
    });

    std::cout << "[AudioEngine] ✓ Moteur audio opérationnel\n";
}

void AudioEngine::stop() {
    if (!is_running()) return;

    std::cout << "[AudioEngine] Arrêt du moteur audio...\n";
    pimpl_->running = false;

    if (pimpl_->audio_thread.joinable()) {
        pimpl_->audio_thread.join();
    }

    std::cout << "[AudioEngine] ✓ Moteur audio arrêté\n";
}

bool AudioEngine::is_running() const {
    return pimpl_->running;
}

// STT - Transcription
AudioEngine::TranscriptionResult AudioEngine::transcribe(
    const std::vector<float>& audio_data) {

    auto start = std::chrono::steady_clock::now();

    TranscriptionResult result;
    result.confidence = 0.95f;  // Whisper ne donne pas de score
    result.duration_ms = static_cast<int>(
        (audio_data.size() * 1000) / static_cast<int>(config_.sample_rate));

    // Appel Whisper (via C binding whisper.cpp)
    // Note: Implémentation réelle nécessite whisper.cpp intégré
    result.text = "[STT] Transcription placeholder";

    auto end = std::chrono::steady_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);

    std::cout << "[STT] Transcription en " << duration.count() << "ms: "
              << result.text << "\n";

    return result;
}

// TTS - Synthèse
AudioEngine::SynthesisResult AudioEngine::synthesize(
    const std::string& text,
    const std::string& voice) {

    auto start = std::chrono::steady_clock::now();

    SynthesisResult result;
    result.sample_rate = static_cast<int>(config_.sample_rate);

    // Appel Piper (via C binding piper)
    // Note: Implémentation réelle nécessite piper intégré
    result.audio_samples.resize(config_.sample_rate);  // 1 seconde de silence
    std::fill(result.audio_samples.begin(), result.audio_samples.end(), 0.0f);

    auto end = std::chrono::steady_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);

    result.duration_ms = static_cast<int>(duration.count());

    std::cout << "[TTS] Synthèse en " << duration.count() << "ms, "
              << result.audio_samples.size() << " samples\n";

    return result;
}

void AudioEngine::process_realtime(const float* input, size_t frames, float* output) {
    if (!is_running()) return;

    auto start = std::chrono::steady_clock::now();

    // Écrire dans le buffer circulaire
    pimpl_->buffer.write(input, frames);

    // Traitement immédiat
    std::vector<float> temp_buffer(frames);
    pimpl_->buffer.read(temp_buffer.data(), frames);
    pimpl_->dsp_pipeline.process(temp_buffer.data(), frames);

    // Copier vers output
    std::copy(temp_buffer.begin(), temp_buffer.end(), output);

    auto end = std::chrono::steady_clock::now();
    auto latency = std::chrono::duration_cast<std::chrono::microseconds>(end - start);

    stats_.latency_ms = latency.count() / 1000.0f;
    stats_.processed_frames += frames;
}

void AudioEngine::set_transcription_callback(AudioCallback cb) {
    pimpl_->transcription_cb = cb;
}

void AudioEngine::set_synthesis_callback(AudioCallback cb) {
    pimpl_->synthesis_cb = cb;
}

void AudioEngine::set_config(const AudioConfig& cfg) {
    config_ = cfg;
    pimpl_->config = cfg;
    pimpl_->dsp_pipeline = DSPPipeline(cfg);
}

void AudioEngine::enable_microphone(bool enable) {
    std::cout << "[AudioEngine] Micro: " << (enable ? "ON" : "OFF") << "\n";
}

void AudioEngine::enable_speaker(bool enable) {
    std::cout << "[AudioEngine] Speaker: " << (enable ? "ON" : "OFF") << "\n";
}

float AudioEngine::get_input_level() const {
    return 0.5f;  // Placeholder
}

float AudioEngine::get_output_level() const {
    return 0.5f;  // Placeholder
}

void AudioEngine::reset_stats() {
    stats_.processed_frames = 0;
    stats_.dropped_frames = 0;
    stats_.latency_ms = 0.0f;
}

// DSP Pipeline
DSPPipeline::DSPPipeline(const AudioConfig& config)
    : config_(config) {}

void DSPPipeline::process(float* data, size_t frames) {
    if (ns_enabled_) {
        apply_hpf_(data, frames);
    }

    if (norm_enabled_) {
        apply_agc_(data, frames);
    }

    // Appliquer gain
    for (size_t i = 0; i < frames; ++i) {
        data[i] *= gain_linear_;
        // Clipping
        data[i] = std::max(-1.0f, std::min(1.0f, data[i]));
    }
}

void DSPPipeline::enable_noise_suppression(bool enable) {
    ns_enabled_ = enable;
}

void DSPPipeline::enable_echo_cancellation(bool enable) {
    ec_enabled_ = enable;
}

void DSPPipeline::enable_normalization(bool enable) {
    norm_enabled_ = enable;
}

void DSPPipeline::set_gain_db(float db) {
    gain_linear_ = std::pow(10.0f, db / 20.0f);
}

void DSPPipeline::apply_hpf_(float* data, size_t frames) {
    // Simple high-pass filter (1st order)
    static float prev_in = 0.0f, prev_out = 0.0f;
    const float alpha = 0.95f;  // Cutoff ~100Hz @ 16kHz

    for (size_t i = 0; i < frames; ++i) {
        float out = alpha * (prev_out + data[i] - prev_in);
        prev_in = data[i];
        prev_out = out;
        data[i] = out;
    }
}

void DSPPipeline::apply_agc_(float* data, size_t frames) {
    // Automatic Gain Control simple
    float max_val = 0.0f;
    for (size_t i = 0; i < frames; ++i) {
        max_val = std::max(max_val, std::abs(data[i]));
    }

    if (max_val > 0.0f && max_val < 1.0f) {
        float scale = 0.95f / max_val;
        for (size_t i = 0; i < frames; ++i) {
            data[i] *= scale;
        }
    }
}

// Audio Buffer
AudioBuffer::AudioBuffer(size_t capacity)
    : buffer_(capacity) {}

size_t AudioBuffer::write(const float* data, size_t frames) {
    std::lock_guard<std::mutex> lock(mutex);

    size_t available = available_write();
    size_t to_write = std::min(frames, available);

    for (size_t i = 0; i < to_write; ++i) {
        buffer_[(write_pos_ + i) % buffer_.size()] = data[i];
    }

    write_pos_ = (write_pos_ + to_write) % buffer_.size();
    fill_count_ += to_write;

    return to_write;
}

size_t AudioBuffer::read(float* data, size_t frames) {
    std::lock_guard<std::mutex> lock(mutex);

    size_t available = available_read();
    size_t to_read = std::min(frames, available);

    for (size_t i = 0; i < to_read; ++i) {
        data[i] = buffer_[(read_pos_ + i) % buffer_.size()];
    }

    read_pos_ = (read_pos_ + to_read) % buffer_.size();
    fill_count_ -= to_read;

    return to_read;
}

size_t AudioBuffer::available_read() const {
    return fill_count_;
}

size_t AudioBuffer::available_write() const {
    return buffer_.size() - fill_count_;
}

void AudioBuffer::clear() {
    std::lock_guard<std::mutex> lock(mutex);
    write_pos_ = read_pos_ = 0;
    fill_count_ = 0;
}

}  // namespace jarvis::audio