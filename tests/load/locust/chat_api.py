"""
Locust load test for Jarvis Chat API
Run with: locust -f chat_api.py --host=http://localhost:8100
"""

from locust import HttpUser, task, between, events
import json
import time
from datetime import datetime

class JarvisUser(HttpUser):
    """
    Simulates a user interacting with Jarvis Chat API
    """
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

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

    @task(5)  # Weight: 5 (most common task)
    def send_chat_message(self):
        """Send a chat message"""
        if not self.token:
            return

        payload = {
            "content": f"Test message from user at {datetime.now().isoformat()}"
        }

        with self.client.post(
            "/api/chat",
            json=payload,
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "conversation_id" in data:
                    response.success()

                    # Record latency
                    latency = data.get("latency_ms", 0)
                    if latency > 1000:
                        response.failure(f"Latency too high: {latency}ms")
                else:
                    response.failure("Missing required fields in response")
            else:
                response.failure(f"Status code: {response.status_code}")

    @task(3)  # Weight: 3
    def list_conversations(self):
        """List all conversations"""
        if not self.token:
            return

        with self.client.get(
            "/api/chat/conversations",
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "conversations" in data:
                    response.success()
                else:
                    response.failure("Missing conversations field")
            else:
                response.failure(f"Status code: {response.status_code}")

    @task(2)  # Weight: 2
    def search_memory(self):
        """Search in memory"""
        if not self.token:
            return

        with self.client.get(
            "/api/memory/search?q=test&limit=10",
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "results" in data and "query_time_ms" in data:
                    query_time = data.get("query_time_ms", 0)
                    if query_time > 200:
                        response.failure(f"Search too slow: {query_time}ms")
                    else:
                        response.success()
                else:
                    response.failure("Missing required fields")
            else:
                response.failure(f"Status code: {response.status_code}")

    @task(1)  # Weight: 1
    def create_conversation(self):
        """Create a new conversation"""
        if not self.token:
            return

        payload = {
            "title": f"Test Conversation {time.time()}"
        }

        with self.client.post(
            "/api/chat/conversation",
            json=payload,
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "id" in data and "title" in data:
                    response.success()
                else:
                    response.failure("Missing required fields")
            else:
                response.failure(f"Status code: {response.status_code}")

    @task(1)  # Weight: 1
    def health_check(self):
        """Check API health"""
        with self.client.get(
            "/health",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    response.success()
                else:
                    response.failure(f"Unhealthy status: {data.get('status')}")
            else:
                response.failure(f"Status code: {response.status_code}")


# Event listeners for custom metrics
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("=" * 60)
    print("Starting Jarvis Chat API Load Test")
    print(f"Target: {environment.host}")
    print("=" * 60)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("=" * 60)
    print("Load test completed")
    print("=" * 60)
