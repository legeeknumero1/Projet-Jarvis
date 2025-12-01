#!/bin/bash

# K6 Load Test Runner for Jarvis API
# Run all K6 load tests with proper configuration

set -e

API_URL="${API_URL:-http://localhost:8100}"
RESULTS_DIR="./results"

echo "=========================================="
echo "Jarvis API Load Testing Suite (K6)"
echo "=========================================="
echo "API URL: $API_URL"
echo "Results directory: $RESULTS_DIR"
echo ""

# Create results directory
mkdir -p "$RESULTS_DIR"

# Check if K6 is installed
if ! command -v k6 &> /dev/null; then
    echo "ERROR: k6 is not installed!"
    echo "Install with: https://k6.io/docs/get-started/installation/"
    exit 1
fi

# Check if API is running
echo "Checking if API is available..."
if ! curl -s -f "$API_URL/health" > /dev/null; then
    echo "ERROR: API is not accessible at $API_URL"
    echo "Please start the API first: docker-compose up -d"
    exit 1
fi

echo " API is running"
echo ""

# Test 1: Chat API
echo "=========================================="
echo "Test 1: Chat API Load Test"
echo "=========================================="
k6 run \
    --out json="$RESULTS_DIR/chat-api-$(date +%Y%m%d-%H%M%S).json" \
    --summary-export="$RESULTS_DIR/chat-api-summary-$(date +%Y%m%d-%H%M%S).json" \
    -e API_URL="$API_URL" \
    chat-api.js

echo ""
echo " Chat API test completed"
echo ""

# Test 2: Voice API
echo "=========================================="
echo "Test 2: Voice API Load Test"
echo "=========================================="
k6 run \
    --out json="$RESULTS_DIR/voice-api-$(date +%Y%m%d-%H%M%S).json" \
    --summary-export="$RESULTS_DIR/voice-api-summary-$(date +%Y%m%d-%H%M%S).json" \
    -e API_URL="$API_URL" \
    voice-api.js

echo ""
echo " Voice API test completed"
echo ""

# Generate summary report
echo "=========================================="
echo "Load Test Summary"
echo "=========================================="
echo "All tests completed successfully!"
echo ""
echo "Results saved to: $RESULTS_DIR"
echo ""
echo "To view detailed results:"
echo "  - JSON files: $RESULTS_DIR/*.json"
echo "  - Import to Grafana for visualization"
echo ""
echo "Performance Thresholds:"
echo "  - Chat API p95 latency: < 500ms"
echo "  - Chat API p99 latency: < 1000ms"
echo "  - Voice API p95 latency: < 2000ms"
echo "  - Error rate: < 1%"
echo ""
echo "=========================================="
