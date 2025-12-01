import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';
import encoding from 'k6/encoding';

// Custom metrics
const errorRate = new Rate('voice_errors');
const ttsLatency = new Trend('tts_latency');
const sttLatency = new Trend('stt_latency');

// Test configuration
export const options = {
  stages: [
    { duration: '30s', target: 5 },   // Ramp-up to 5 users
    { duration: '1m', target: 20 },   // Ramp-up to 20 users
    { duration: '2m', target: 20 },   // Stay at 20 users
    { duration: '30s', target: 0 },   // Ramp-down
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'],  // Voice APIs can be slower
    http_req_failed: ['rate<0.05'],     // Error rate < 5%
    tts_latency: ['p(95)<1500'],        // TTS 95% < 1.5s
    stt_latency: ['p(95)<2000'],        // STT 95% < 2s
  },
};

const BASE_URL = __ENV.API_URL || 'http://localhost:8100';

// Sample base64 audio (very short WAV)
const SAMPLE_AUDIO_BASE64 = 'UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA=';

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

export default function (data) {
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${data.token}`,
  };

  // Test 1: Text-to-Speech (TTS)
  const ttsPayload = JSON.stringify({
    text: `Bonjour, test de synthèse vocale numéro ${__VU}-${__ITER}`,
    language: 'fr',
  });

  const ttsStart = Date.now();
  const ttsRes = http.post(`${BASE_URL}/api/voice/synthesize`, ttsPayload, { headers });
  const ttsDuration = Date.now() - ttsStart;

  ttsLatency.add(ttsDuration);

  const ttsSuccess = check(ttsRes, {
    'TTS status is 200': (r) => r.status === 200,
    'TTS has audio_data': (r) => r.json('audio_data') !== undefined,
    'TTS has format': (r) => r.json('format') !== undefined,
    'TTS duration reasonable': (r) => r.json('duration_ms') > 0,
  });

  errorRate.add(!ttsSuccess);

  sleep(1);

  // Test 2: Speech-to-Text (STT)
  const sttPayload = JSON.stringify({
    audio_data: SAMPLE_AUDIO_BASE64,
  });

  const sttStart = Date.now();
  const sttRes = http.post(`${BASE_URL}/api/voice/transcribe`, sttPayload, { headers });
  const sttDuration = Date.now() - sttStart;

  sttLatency.add(sttDuration);

  const sttSuccess = check(sttRes, {
    'STT status is 200': (r) => r.status === 200,
    'STT has text': (r) => r.json('text') !== undefined,
    'STT has confidence': (r) => r.json('confidence') !== undefined,
  });

  errorRate.add(!sttSuccess);

  sleep(2);
}

export function teardown(data) {
  console.log('Voice API load test completed');
}
