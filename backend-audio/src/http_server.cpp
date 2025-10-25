#include "audio_engine.hpp"
#include <httplib.h>
#include <nlohmann/json.hpp>
#include <iostream>
#include <memory>
#include <base64.h>

using json = nlohmann::json;

std::unique_ptr<jarvis::audio::AudioEngine> g_engine;

void setup_routes(httplib::Server& svr) {
    // Health check
    svr.Get("/health", [](const httplib::Request&, httplib::Response& res) {
        auto stats = g_engine->get_stats();
        json response = {
            {"status", g_engine->is_running() ? "healthy" : "unhealthy"},
            {"service", "audio-engine"},
            {"version", "1.3.0"},
            {"latency_ms", stats.latency_ms},
            {"cpu_usage_percent", stats.cpu_usage_percent},
            {"processed_frames", static_cast<double>(stats.processed_frames)},
            {"dropped_frames", static_cast<double>(stats.dropped_frames)}
        };
        res.set_content(response.dump(), "application/json");
    });

    // Ready check
    svr.Get("/ready", [](const httplib::Request&, httplib::Response& res) {
        json response = {
            {"status", g_engine->is_running() ? "ready" : "not_ready"},
            {"version", "1.3.0"},
            {"timestamp", json::object()}
        };
        res.set_content(response.dump(), "application/json");
    });

    // Transcription STT
    svr.Post("/transcribe", [](const httplib::Request& req, httplib::Response& res) {
        try {
            auto body = json::parse(req.body);

            // Décoder audio base64
            std::string audio_b64 = body.value("audio_data", "");
            std::string audio_decoded = base64_decode(audio_b64);

            // Convertir en float array
            std::vector<float> audio_samples;
            const float* float_data = reinterpret_cast<const float*>(audio_decoded.data());
            size_t sample_count = audio_decoded.size() / sizeof(float);
            audio_samples.assign(float_data, float_data + sample_count);

            // Transcription
            auto result = g_engine->transcribe(audio_samples);

            json response = {
                {"text", result.text},
                {"confidence", result.confidence},
                {"duration_ms", result.duration_ms},
                {"language", "fr"},
                {"words", json::array()}
            };

            for (const auto& [word, times] : result.words) {
                response["words"].push_back({
                    {"word", word},
                    {"start_time", times.first},
                    {"end_time", times.second}
                });
            }

            res.set_content(response.dump(), "application/json");
        } catch (const std::exception& e) {
            json error = {{"error", e.what()}};
            res.set_content(error.dump(), "application/json");
            res.status = 400;
        }
    });

    // Synthèse TTS
    svr.Post("/synthesize", [](const httplib::Request& req, httplib::Response& res) {
        try {
            auto body = json::parse(req.body);

            std::string text = body.value("text", "");
            std::string voice = body.value("voice", "fr_FR-upmc-medium");

            if (text.empty()) {
                res.status = 400;
                res.set_content(json{{"error", "text required"}}.dump(), "application/json");
                return;
            }

            // Synthèse
            auto result = g_engine->synthesize(text, voice);

            // Encoder audio en base64
            std::string audio_bytes(
                reinterpret_cast<const char*>(result.audio_samples.data()),
                result.audio_samples.size() * sizeof(float)
            );
            std::string audio_b64 = base64_encode(audio_bytes);

            json response = {
                {"audio_data", audio_b64},
                {"sample_rate", result.sample_rate},
                {"duration_ms", result.duration_ms},
                {"format", "wav"},
                {"voice", voice}
            };

            res.set_content(response.dump(), "application/json");
        } catch (const std::exception& e) {
            json error = {{"error", e.what()}};
            res.set_content(error.dump(), "application/json");
            res.status = 400;
        }
    });

    // Traitement temps réel
    svr.Post("/process", [](const httplib::Request& req, httplib::Response& res) {
        try {
            auto body = json::parse(req.body);

            // Décoder entrée
            std::string in_b64 = body.value("audio_data", "");
            std::string in_decoded = base64_decode(in_b64);
            const float* in_data = reinterpret_cast<const float*>(in_decoded.data());
            size_t frames = in_decoded.size() / sizeof(float);

            // Traiter
            std::vector<float> output(frames);
            g_engine->process_realtime(in_data, frames, output.data());

            // Encoder sortie
            std::string out_bytes(
                reinterpret_cast<const char*>(output.data()),
                output.size() * sizeof(float)
            );
            std::string out_b64 = base64_encode(out_bytes);

            json response = {
                {"audio_data", out_b64},
                {"frames", static_cast<int>(frames)},
                {"latency_ms", g_engine->get_stats().latency_ms}
            };

            res.set_content(response.dump(), "application/json");
        } catch (const std::exception& e) {
            json error = {{"error", e.what()}};
            res.set_content(error.dump(), "application/json");
            res.status = 400;
        }
    });

    // Statistiques
    svr.Get("/stats", [](const httplib::Request&, httplib::Response& res) {
        auto stats = g_engine->get_stats();
        json response = {
            {"latency_ms", stats.latency_ms},
            {"cpu_usage_percent", stats.cpu_usage_percent},
            {"processed_frames", static_cast<double>(stats.processed_frames)},
            {"dropped_frames", static_cast<double>(stats.dropped_frames)},
            {"input_level_db", 20.0f * std::log10(g_engine->get_input_level() + 1e-6f)},
            {"output_level_db", 20.0f * std::log10(g_engine->get_output_level() + 1e-6f)}
        };
        res.set_content(response.dump(), "application/json");
    });
}

int main(int argc, char* argv[]) {
    std::cout << "🎤 Jarvis Audio Engine v1.3.0\n";
    std::cout << "================================\n\n";

    // Configuration audio
    jarvis::audio::AudioConfig config;
    config.sample_rate = jarvis::audio::SampleRate::SR_16000;
    config.channels = 1;
    config.buffer_size = 512;  // ~32ms

    // Créer moteur
    g_engine = std::make_unique<jarvis::audio::AudioEngine>(config);
    g_engine->start();

    // Serveur HTTP
    httplib::Server svr;

    // CORS
    svr.set_post_routing_handler([](const httplib::Request&, httplib::Response& res) {
        res.set_header("Access-Control-Allow-Origin", "*");
        res.set_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
        res.set_header("Access-Control-Allow-Headers", "Content-Type");
    });

    svr.Options("/.*", [](const httplib::Request&, httplib::Response& res) {
        res.set_header("Access-Control-Allow-Origin", "*");
        res.status = 200;
    });

    setup_routes(svr);

    // Démarrer serveur
    std::string host = "0.0.0.0";
    int port = 8004;

    std::cout << "📡 Démarrage serveur HTTP...\n";
    std::cout << "🌐 Accès: http://" << host << ":" << port << "\n";
    std::cout << "🏥 Health: http://" << host << ":" << port << "/health\n\n";

    if (!svr.listen(host.c_str(), port)) {
        std::cerr << "❌ Erreur démarrage serveur\n";
        return 1;
    }

    return 0;
}