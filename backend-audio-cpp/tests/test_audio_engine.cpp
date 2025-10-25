/// Test Suite for Audio Engine (Phase 2)
/// Tests:
/// - Initialization
/// - SPSC queue lock-free behavior
/// - DSP pipeline processing
/// - Latency measurement

#include "../include/audio_engine.h"
#include <iostream>
#include <cassert>
#include <vector>
#include <chrono>

using namespace jarvis::audio;

void test_initialization() {
    std::cout << "\n[TEST] Initialization..." << std::endl;

    AudioEngine engine;
    AudioConfig config{16000, 1, 16};

    int result = engine.init(config);
    assert(result == 0 && "Engine should initialize successfully");

    result = engine.start();
    assert(result == 0 && "Engine should start successfully");

    assert(engine.health_check() && "Engine should report healthy");

    engine.stop();
    std::cout << "[PASS] Initialization" << std::endl;
}

void test_audio_processing() {
    std::cout << "\n[TEST] Audio Processing..." << std::endl;

    AudioEngine engine;
    AudioConfig config{16000, 1, 16};

    engine.init(config);
    engine.start();

    // Create test signal (1000 Hz sine wave)
    const size_t num_samples = 16000;  // 1 second at 16kHz
    std::vector<float> input(num_samples);

    for (size_t i = 0; i < num_samples; ++i) {
        float t = static_cast<float>(i) / 16000.0f;
        float freq = 1000.0f;  // 1 kHz
        input[i] = 0.5f * std::sin(2.0f * 3.14159f * freq * t);
    }

    // Process audio
    std::vector<float> output;
    int result = engine.process_audio(input, output);

    assert(result == 0 && "Audio processing should succeed");
    assert(output.size() > 0 && "Output should not be empty");
    assert(output.size() == input.size() && "Output size should match input");

    // Check latency
    double latency = engine.get_latency_ms();
    std::cout << "  Processing latency: " << latency << " ms" << std::endl;
    assert(latency < 10.0 && "Latency should be <10ms");

    engine.stop();
    std::cout << "[PASS] Audio Processing" << std::endl;
}

void test_lock_free_queue() {
    std::cout << "\n[TEST] Lock-free SPSC Queue..." << std::endl;

    SPSCQueue<int> queue(10);

    // Test push/pop
    assert(queue.empty() && "Queue should start empty");

    queue.push(42);
    assert(!queue.empty() && "Queue should not be empty after push");

    int value;
    assert(queue.pop(value) && "Pop should succeed");
    assert(value == 42 && "Value should be correct");
    assert(queue.empty() && "Queue should be empty after pop");

    // Stress test
    for (int i = 0; i < 100; ++i) {
        queue.push(i);
    }

    for (int i = 0; i < 100; ++i) {
        assert(queue.pop(value) && "Pop should succeed");
        assert(value == i && "Values should be in order");
    }

    std::cout << "[PASS] Lock-free SPSC Queue" << std::endl;
}

void test_latency_measurement() {
    std::cout << "\n[TEST] Latency Measurement..." << std::endl;

    AudioEngine engine;
    AudioConfig config{16000, 1, 16};

    engine.init(config);
    engine.start();

    std::vector<float> input(512);
    std::vector<float> output;

    // Warm up
    for (int i = 0; i < 10; ++i) {
        engine.process_audio(input, output);
    }

    // Measure
    auto start = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < 1000; ++i) {
        engine.process_audio(input, output);
    }
    auto end = std::chrono::high_resolution_clock::now();

    auto total_us = std::chrono::duration_cast<std::chrono::microseconds>(end - start).count();
    double avg_latency_ms = (total_us / 1000.0) / 1000.0;

    std::cout << "  Average latency: " << avg_latency_ms << " ms" << std::endl;
    std::cout << "  Target: <1ms for sub-millisecond processing" << std::endl;

    engine.stop();
    std::cout << "[PASS] Latency Measurement" << std::endl;
}

int main() {
    std::cout << "==============================================================" << std::endl;
    std::cout << "  Audio Engine Test Suite (Phase 2)" << std::endl;
    std::cout << "  DSP/FFmpeg/PortAudio + SPSC Lock-free Queues" << std::endl;
    std::cout << "==============================================================" << std::endl;

    try {
        test_initialization();
        test_lock_free_queue();
        test_audio_processing();
        test_latency_measurement();

        std::cout << "\n==============================================================" << std::endl;
        std::cout << "  ALL TESTS PASSED! ✅" << std::endl;
        std::cout << "==============================================================" << std::endl;

        return 0;
    } catch (const std::exception& e) {
        std::cerr << "\n[ERROR] Test failed: " << e.what() << std::endl;
        return 1;
    }
}
