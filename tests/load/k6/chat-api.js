import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const chatLatency = new Trend('chat_latency');

// Test configuration
export const options = {
  stages: [
    { duration: '30s', target: 10 },  // Ramp-up to 10 users
    { duration: '1m', target: 50 },   // Ramp-up to 50 users
    { duration: '2m', target: 50 },   // Stay at 50 users
    { duration: '30s', target: 100 }, // Spike to 100 users
    { duration: '1m', target: 100 },  // Stay at 100 users
    { duration: '30s', target: 0 },   // Ramp-down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'], // 95% < 500ms, 99% < 1s
    http_req_failed: ['rate<0.01'],                  // Error rate < 1%
    errors: ['rate<0.05'],                           // Custom error rate < 5%
    chat_latency: ['p(95)<300'],                     // Chat API 95% < 300ms
  },
};

const BASE_URL = __ENV.API_URL || 'http://localhost:8100';

// Setup: Login and get token
export function setup() {
  const loginRes = http.post(`${BASE_URL}/auth/login`, JSON.stringify({
    username: 'admin',
    password: 'admin123',
  }), {
    headers: { 'Content-Type': 'application/json' },
  });

  const token = loginRes.json('token');
  return { token };
}

// Main test function
export default function (data) {
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${data.token}`,
  };

  // Test 1: Health check
  const healthRes = http.get(`${BASE_URL}/health`);
  check(healthRes, {
    'health check status is 200': (r) => r.status === 200,
    'health check has status field': (r) => r.json('status') !== undefined,
  });

  sleep(0.5);

  // Test 2: Chat API - Send message
  const chatPayload = JSON.stringify({
    content: `Test message ${__VU}-${__ITER}`,
  });

  const chatStart = Date.now();
  const chatRes = http.post(`${BASE_URL}/api/chat`, chatPayload, { headers });
  const chatDuration = Date.now() - chatStart;

  chatLatency.add(chatDuration);

  const chatSuccess = check(chatRes, {
    'chat status is 200': (r) => r.status === 200,
    'chat has message': (r) => r.json('message') !== undefined,
    'chat has conversation_id': (r) => r.json('conversation_id') !== undefined,
    'chat latency < 1s': (r) => r.timings.duration < 1000,
  });

  errorRate.add(!chatSuccess);

  sleep(1);

  // Test 3: Get conversations
  const conversationsRes = http.get(`${BASE_URL}/api/chat/conversations`, { headers });
  check(conversationsRes, {
    'conversations status is 200': (r) => r.status === 200,
    'conversations has array': (r) => Array.isArray(r.json('conversations')),
  });

  sleep(0.5);

  // Test 4: Memory search (if conversation exists)
  const searchRes = http.get(`${BASE_URL}/api/memory/search?q=test&limit=5`, { headers });
  check(searchRes, {
    'search status is 200': (r) => r.status === 200,
    'search has results': (r) => r.json('results') !== undefined,
  });

  sleep(1);
}

// Teardown
export function teardown(data) {
  console.log('Load test completed');
}
