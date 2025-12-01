"""
Locust load test for Jarvis Voice API (TTS/STT)
Run with: locust -f voice_api.py --host=http://localhost:8100
"""

from locust import HttpUser, task, between, events
import json
import base64
from datetime import datetime

# Sample base64 WAV audio (minimal valid WAV file)
SAMPLE_AUDIO_BASE64 = "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA="

class VoiceAPIUser(HttpUser):
    """
    Simulates a user interacting with Jarvis Voice API
    """
    wait_time = between(2, 5)  # Voice operations need more time

    def on_start(self):
        """Login and get JWT token"""
        response = self.client.post("/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })

        if response.status_code == 200:
            data = response.json()
            self.token = data.get("token")
            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
        else:
            self.token = None
            self.headers = {}

    @task(5)  # Weight: 5 (TTS is common)
    def synthesize_speech(self):
        """Text-to-Speech synthesis"""
        if not self.token:
            return

        texts = [
            "Bonjour, je suis Jarvis.",
            "Comment puis-je vous aider aujourd'hui?",
            "Test de synthèse vocale.",
            "La météo est belle aujourd'hui.",
            "Jarvis à votre service."
        ]

        import random
        text = random.choice(texts)

        payload = {
            "text": text,
            "language": "fr"
        }

        with self.client.post(
            "/api/voice/synthesize",
            json=payload,
            headers=self.headers,
            catch_response=True,
            name="/api/voice/synthesize"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "audio_data" in data and "format" in data:
                    duration_ms = data.get("duration_ms", 0)

                    # Check if synthesis time is reasonable
                    if duration_ms > 5000:
                        response.failure(f"TTS took too long: {duration_ms}ms")
                    else:
                        response.success()
                else:
                    response.failure("Missing required fields in TTS response")
            else:
                response.failure(f"TTS failed with status: {response.status_code}")

    @task(3)  # Weight: 3 (STT is less common)
    def transcribe_speech(self):
        """Speech-to-Text transcription"""
        if not self.token:
            return

        payload = {
            "audio_data": SAMPLE_AUDIO_BASE64
        }

        with self.client.post(
            "/api/voice/transcribe",
            json=payload,
            headers=self.headers,
            catch_response=True,
            name="/api/voice/transcribe"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "text" in data and "confidence" in data:
                    confidence = data.get("confidence", 0)
                    duration_ms = data.get("duration_ms", 0)

                    # Check transcription quality
                    if confidence < 0.5:
                        response.failure(f"Low confidence: {confidence}")
                    elif duration_ms > 5000:
                        response.failure(f"STT took too long: {duration_ms}ms")
                    else:
                        response.success()
                else:
                    response.failure("Missing required fields in STT response")
            else:
                response.failure(f"STT failed with status: {response.status_code}")

    @task(1)  # Weight: 1
    def combined_voice_workflow(self):
        """Combined TTS + STT workflow"""
        if not self.token:
            return

        # Step 1: Generate speech
        tts_payload = {
            "text": f"Test workflow at {datetime.now().isoformat()}",
            "language": "fr"
        }

        tts_response = self.client.post(
            "/api/voice/synthesize",
            json=tts_payload,
            headers=self.headers,
            name="/api/voice/synthesize [workflow]"
        )

        if tts_response.status_code != 200:
            return

        # Step 2: Transcribe the generated audio
        audio_data = tts_response.json().get("audio_data")
        if not audio_data:
            return

        stt_payload = {
            "audio_data": audio_data
        }

        with self.client.post(
            "/api/voice/transcribe",
            json=stt_payload,
            headers=self.headers,
            catch_response=True,
            name="/api/voice/transcribe [workflow]"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Workflow STT failed: {response.status_code}")


# Event listeners
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("=" * 60)
    print("Starting Jarvis Voice API Load Test")
    print(f"Target: {environment.host}")
    print("Testing TTS and STT endpoints")
    print("=" * 60)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("=" * 60)
    print("Voice API load test completed")
    print("=" * 60)
