#!/bin/bash

# Locust Load Test Runner for Jarvis API
# Run Locust tests with Web UI or headless mode

set -e

API_URL="${API_URL:-http://localhost:8100}"
MODE="${MODE:-web}"  # web or headless
USERS="${USERS:-100}"
SPAWN_RATE="${SPAWN_RATE:-10}"
RUN_TIME="${RUN_TIME:-5m}"

echo "=========================================="
echo "Jarvis API Load Testing Suite (Locust)"
echo "=========================================="
echo "API URL: $API_URL"
echo "Mode: $MODE"
if [ "$MODE" = "headless" ]; then
    echo "Users: $USERS"
    echo "Spawn rate: $SPAWN_RATE users/s"
    echo "Run time: $RUN_TIME"
fi
echo ""

# Check if Locust is installed
if ! command -v locust &> /dev/null; then
    echo "ERROR: Locust is not installed!"
    echo "Install with: pip install locust"
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

# Select test file
echo "Select test to run:"
echo "  1) Chat API"
echo "  2) Voice API"
echo "  3) Both (sequential)"
echo ""
read -p "Enter choice [1-3]: " choice

case $choice in
    1)
        TEST_FILE="chat_api.py"
        TEST_NAME="Chat API"
        ;;
    2)
        TEST_FILE="voice_api.py"
        TEST_NAME="Voice API"
        ;;
    3)
        TEST_FILE="chat_api.py,voice_api.py"
        TEST_NAME="All APIs"
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "Running: $TEST_NAME"
echo "=========================================="
echo ""

if [ "$MODE" = "web" ]; then
    echo "Starting Locust Web UI..."
    echo "Access at: http://localhost:8089"
    echo ""
    locust -f "$TEST_FILE" --host="$API_URL"
else
    # Headless mode
    echo "Running in headless mode..."
    mkdir -p results

    TIMESTAMP=$(date +%Y%m%d-%H%M%S)
    locust -f "$TEST_FILE" \
        --host="$API_URL" \
        --headless \
        --users="$USERS" \
        --spawn-rate="$SPAWN_RATE" \
        --run-time="$RUN_TIME" \
        --html="results/locust-report-$TIMESTAMP.html" \
        --csv="results/locust-stats-$TIMESTAMP"

    echo ""
    echo "=========================================="
    echo "Test completed!"
    echo "=========================================="
    echo "Results:"
    echo "  - HTML report: results/locust-report-$TIMESTAMP.html"
    echo "  - CSV stats: results/locust-stats-$TIMESTAMP*.csv"
    echo ""
fi
