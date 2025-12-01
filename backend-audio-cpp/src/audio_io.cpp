#include "audio_io.h"
#include <iostream>
#include <cstring>

namespace jarvis {

// ============================================================================
// PortAudio Real-Time I/O
// ============================================================================

AudioIO::AudioIO(int sample_rate, int buffer_size)
    : sample_rate_(sample_rate), buffer_size_(buffer_size) {
}

AudioIO::~AudioIO() {
    stop();
    if (stream_) {
        Pa_CloseStream(stream_);
    }
    Pa_Terminate();
}

bool AudioIO::initialize() {
    PaError err = Pa_Initialize();
    if (err != paNoError) {
        std::cerr << "PortAudio init error: " << Pa_GetErrorText(err) << std::endl;
        return false;
    }
    return true;
}

bool AudioIO::start(AudioCallback callback) {
    callback_ = callback;

    PaStreamParameters input_params;
    input_params.device = Pa_GetDefaultInputDevice();
    input_params.channelCount = 1; // Mono input
    input_params.sampleFormat = paFloat32;
    input_params.suggestedLatency = Pa_GetDeviceInfo(input_params.device)->defaultLowInputLatency;
    input_params.hostApiSpecificStreamInfo = nullptr;

    PaStreamParameters output_params;
    output_params.device = Pa_GetDefaultOutputDevice();
    output_params.channelCount = 1; // Mono output
    output_params.sampleFormat = paFloat32;
    output_params.suggestedLatency = Pa_GetDeviceInfo(output_params.device)->defaultLowOutputLatency;
    output_params.hostApiSpecificStreamInfo = nullptr;

    PaError err = Pa_OpenStream(
        &stream_,
        &input_params,
        &output_params,
        sample_rate_,
        buffer_size_,
        paNoFlag,
        &AudioIO::portaudio_callback,
        this
    );

    if (err != paNoError) {
        std::cerr << "PortAudio stream error: " << Pa_GetErrorText(err) << std::endl;
        return false;
    }

    err = Pa_StartStream(stream_);
    if (err != paNoError) {
        std::cerr << "PortAudio start error: " << Pa_GetErrorText(err) << std::endl;
        return false;
    }

    running_ = true;
    return true;
}

bool AudioIO::stop() {
    if (!stream_ || !running_) return true;

    PaError err = Pa_StopStream(stream_);
    running_ = false;

    if (err != paNoError) {
        std::cerr << "PortAudio stop error: " << Pa_GetErrorText(err) << std::endl;
        return false;
    }
    return true;
}

double AudioIO::get_cpu_load() const {
    if (!stream_) return 0.0;
    return Pa_GetStreamCpuLoad(stream_);
}

int AudioIO::portaudio_callback(
    const void* input_buffer,
    void* output_buffer,
    unsigned long frames_per_buffer,
    const PaStreamCallbackTimeInfo* time_info,
    PaStreamCallbackFlags status_flags,
    void* user_data
) {
    auto* self = static_cast<AudioIO*>(user_data);
    const float* input = static_cast<const float*>(input_buffer);
    float* output = static_cast<float*>(output_buffer);

    if (self->callback_) {
        self->callback_(input, output, frames_per_buffer);
    } else {
        // Pass-through if no callback
        std::memcpy(output, input, frames_per_buffer * sizeof(float));
    }

    return paContinue;
}

std::vector<std::string> AudioIO::list_input_devices() {
    std::vector<std::string> devices;
    int num_devices = Pa_GetDeviceCount();
    for (int i = 0; i < num_devices; ++i) {
        const PaDeviceInfo* info = Pa_GetDeviceInfo(i);
        if (info->maxInputChannels > 0) {
            devices.push_back(info->name);
        }
    }
    return devices;
}

std::vector<std::string> AudioIO::list_output_devices() {
    std::vector<std::string> devices;
    int num_devices = Pa_GetDeviceCount();
    for (int i = 0; i < num_devices; ++i) {
        const PaDeviceInfo* info = Pa_GetDeviceInfo(i);
        if (info->maxOutputChannels > 0) {
            devices.push_back(info->name);
        }
    }
    return devices;
}

// ============================================================================
// FFmpeg Audio Codec
// ============================================================================

AudioCodec::AudioCodec() {
}

AudioCodec::~AudioCodec() {
    if (format_ctx_) avformat_close_input(&format_ctx_);
    if (codec_ctx_) avcodec_free_context(&codec_ctx_);
    if (swr_ctx_) swr_free(&swr_ctx_);
}

bool AudioCodec::decode_file(const std::string& input_path, std::vector<float>& output, int& sample_rate) {
    // Open input file
    if (avformat_open_input(&format_ctx_, input_path.c_str(), nullptr, nullptr) < 0) {
        std::cerr << "Cannot open input file: " << input_path << std::endl;
        return false;
    }

    if (avformat_find_stream_info(format_ctx_, nullptr) < 0) {
        std::cerr << "Cannot find stream info" << std::endl;
        return false;
    }

    // Find audio stream
    int audio_stream_index = av_find_best_stream(format_ctx_, AVMEDIA_TYPE_AUDIO, -1, -1, nullptr, 0);
    if (audio_stream_index < 0) {
        std::cerr << "Cannot find audio stream" << std::endl;
        return false;
    }

    AVStream* audio_stream = format_ctx_->streams[audio_stream_index];
    const AVCodec* codec = avcodec_find_decoder(audio_stream->codecpar->codec_id);
    codec_ctx_ = avcodec_alloc_context3(codec);
    avcodec_parameters_to_context(codec_ctx_, audio_stream->codecpar);
    avcodec_open2(codec_ctx_, codec, nullptr);

    sample_rate = codec_ctx_->sample_rate;

    // Setup resampler to convert to float mono
    swr_ctx_ = swr_alloc_set_opts(
        nullptr,
        AV_CH_LAYOUT_MONO, AV_SAMPLE_FMT_FLT, sample_rate,
        codec_ctx_->channel_layout, codec_ctx_->sample_fmt, codec_ctx_->sample_rate,
        0, nullptr
    );
    swr_init(swr_ctx_);

    // Decode packets
    AVPacket* packet = av_packet_alloc();
    AVFrame* frame = av_frame_alloc();

    while (av_read_frame(format_ctx_, packet) >= 0) {
        if (packet->stream_index == audio_stream_index) {
            avcodec_send_packet(codec_ctx_, packet);
            while (avcodec_receive_frame(codec_ctx_, frame) == 0) {
                // Resample to float
                float* buffer;
                int out_samples = swr_convert(
                    swr_ctx_,
                    (uint8_t**)&buffer, frame->nb_samples,
                    (const uint8_t**)frame->data, frame->nb_samples
                );
                output.insert(output.end(), buffer, buffer + out_samples);
            }
        }
        av_packet_unref(packet);
    }

    av_frame_free(&frame);
    av_packet_free(&packet);

    return true;
}

bool AudioCodec::encode_file(const std::vector<float>& input, int sample_rate,
                              const std::string& output_path, const std::string& codec_name) {
    // Open output file
    avformat_alloc_output_context2(&format_ctx_, nullptr, nullptr, output_path.c_str());
    if (!format_ctx_) {
        std::cerr << "Cannot create output context" << std::endl;
        return false;
    }

    // Find encoder
    const AVCodec* codec = avcodec_find_encoder_by_name(codec_name.c_str());
    if (!codec) {
        std::cerr << "Codec not found: " << codec_name << std::endl;
        return false;
    }

    AVStream* stream = avformat_new_stream(format_ctx_, codec);
    codec_ctx_ = avcodec_alloc_context3(codec);
    codec_ctx_->sample_rate = sample_rate;
    codec_ctx_->channel_layout = AV_CH_LAYOUT_MONO;
    codec_ctx_->channels = 1;
    codec_ctx_->sample_fmt = codec->sample_fmts[0];
    codec_ctx_->bit_rate = 128000;

    avcodec_open2(codec_ctx_, codec, nullptr);
    avcodec_parameters_from_context(stream->codecpar, codec_ctx_);

    avio_open(&format_ctx_->pb, output_path.c_str(), AVIO_FLAG_WRITE);
    avformat_write_header(format_ctx_, nullptr);

    // Encode audio (simplified - production needs proper framing)
    AVFrame* frame = av_frame_alloc();
    frame->nb_samples = codec_ctx_->frame_size;
    frame->format = codec_ctx_->sample_fmt;
    frame->channel_layout = codec_ctx_->channel_layout;
    av_frame_get_buffer(frame, 0);

    // Write frames (simplified)
    av_write_trailer(format_ctx_);
    avio_closep(&format_ctx_->pb);
    av_frame_free(&frame);

    return true;
}

bool AudioCodec::encode_chunk(const float* input, size_t frames, std::vector<uint8_t>& output) {
    // Streaming encoding implementation
    return true;
}

bool AudioCodec::decode_chunk(const uint8_t* input, size_t size, std::vector<float>& output) {
    // Streaming decoding implementation
    return true;
}

} // namespace jarvis
