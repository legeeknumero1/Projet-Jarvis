#ifndef JARVIS_AUDIO_IO_H
#define JARVIS_AUDIO_IO_H

#include <portaudio.h>
#include <string>
#include <functional>
#include <vector>

extern "C" {
#include <libavformat/avformat.h>
#include <libavcodec/avcodec.h>
#include <libavutil/opt.h>
#include <libswresample/swresample.h>
}

namespace jarvis {

/**
 * PortAudio Real-Time Audio I/O
 * Sub-millisecond latency for live audio processing
 */
class AudioIO {
public:
    using AudioCallback = std::function<void(const float* input, float* output, size_t frames)>;

    AudioIO(int sample_rate = 48000, int buffer_size = 256);
    ~AudioIO();

    bool initialize();
    bool start(AudioCallback callback);
    bool stop();

    bool is_running() const { return running_; }
    double get_cpu_load() const;

    // Device enumeration
    static std::vector<std::string> list_input_devices();
    static std::vector<std::string> list_output_devices();

private:
    static int portaudio_callback(
        const void* input_buffer,
        void* output_buffer,
        unsigned long frames_per_buffer,
        const PaStreamCallbackTimeInfo* time_info,
        PaStreamCallbackFlags status_flags,
        void* user_data
    );

    int sample_rate_;
    int buffer_size_;
    PaStream* stream_ = nullptr;
    AudioCallback callback_;
    bool running_ = false;
};

/**
 * FFmpeg Audio Codec Support
 * Encode/decode MP3, AAC, Opus, FLAC, etc.
 */
class AudioCodec {
public:
    AudioCodec();
    ~AudioCodec();

    // Decode audio file to PCM
    bool decode_file(const std::string& input_path, std::vector<float>& output, int& sample_rate);

    // Encode PCM to audio file
    bool encode_file(const std::vector<float>& input, int sample_rate,
                     const std::string& output_path, const std::string& codec = "libmp3lame");

    // Stream encoding/decoding
    bool encode_chunk(const float* input, size_t frames, std::vector<uint8_t>& output);
    bool decode_chunk(const uint8_t* input, size_t size, std::vector<float>& output);

private:
    AVFormatContext* format_ctx_ = nullptr;
    AVCodecContext* codec_ctx_ = nullptr;
    SwrContext* swr_ctx_ = nullptr;
};

} // namespace jarvis

#endif // JARVIS_AUDIO_IO_H
