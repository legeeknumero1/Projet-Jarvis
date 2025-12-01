"""
Tests for PyO3 Rust-Python bridge
"""
import jarvis_bridge
import time

def test_audio_processing():
    """Test audio processing function"""
    print("Testing audio processing...")

    # Create test audio samples
    samples = [0.1, 0.5, 1.0, 0.5, 0.1] * 100
    sample_rate = 44100

    # Process audio
    result = jarvis_bridge.process_audio(samples, sample_rate)

    assert result.sample_rate == sample_rate
    assert len(result.samples) > 0
    assert result.latency_ms >= 0

    print(f"  Processed {len(result.samples)} samples")
    print(f"  Latency: {result.latency_ms:.2f}ms")
    print("   Audio processing test PASSED")

def test_cache_operations():
    """Test Rust cache operations"""
    print("\nTesting cache operations...")

    cache = jarvis_bridge.RustCache()

    # Test set/get
    cache.set("test_key", "test_value")
    value = cache.get("test_key")
    assert value == "test_value"

    # Test counter
    cache.incr("counter")
    cache.incr("counter")
    count = cache.get_counter("counter")
    assert count == 2

    print("   Cache operations test PASSED")

def test_performance():
    """Test performance benchmarks"""
    print("\nTesting performance...")

    # Benchmark audio processing
    samples = [0.5] * 10000
    iterations = 100

    start = time.time()
    for _ in range(iterations):
        result = jarvis_bridge.process_audio(samples, 44100)
    elapsed = time.time() - start

    avg_latency = (elapsed / iterations) * 1000
    print(f"  Average latency: {avg_latency:.2f}ms per call")
    print(f"  Throughput: {iterations / elapsed:.1f} calls/sec")

    assert avg_latency < 10, "Latency should be <10ms"
    print("   Performance test PASSED")

if __name__ == "__main__":
    print("=== PyO3 Bridge Tests ===\n")

    try:
        test_audio_processing()
        test_cache_operations()
        test_performance()

        print("\n=== ALL TESTS PASSED ===")
    except Exception as e:
        print(f"\n TEST FAILED: {e}")
        raise
