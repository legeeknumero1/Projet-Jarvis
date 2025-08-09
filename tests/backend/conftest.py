"""Configuration des tests backend avec fake services"""
import pytest
from fastapi.testclient import TestClient
from backend.app import create_app
from backend.config import Settings


class FakeLLMService:
    """Fake LLM service pour tests"""
    
    def __init__(self, settings):
        self.settings = settings
    
    async def initialize(self):
        pass
    
    async def close(self):
        pass
    
    def is_available(self) -> bool:
        return True
    
    async def generate_response(self, message: str, context: dict, user_id: str = "default") -> str:
        # Réponse déterministe pour tests
        return f"ACK::{message}"


class FakeMemoryService:
    """Fake Memory service pour tests"""
    
    def __init__(self, settings):
        self.settings = settings
        self.log = []  # Pour vérifier les interactions
    
    async def initialize(self, database):
        pass
    
    def is_available(self) -> bool:
        return True
    
    async def get_contextual_memories(self, user_id: str, message: str, limit: int = 5) -> list:
        # Pas de souvenirs pour les tests simples
        return []
    
    async def store_interaction(self, user_id: str, user_message: str, assistant_response: str) -> bool:
        # Log pour vérification dans les tests
        self.log.append((user_id, user_message, assistant_response))
        return True
    
    def format_context_summary(self, memories: list, max_memories: int = 3) -> str:
        return ""


class FakeVoiceService:
    """Fake Voice service pour tests"""
    
    def __init__(self, settings):
        self.settings = settings
    
    async def initialize(self):
        pass
    
    def is_available(self) -> bool:
        return True
    
    async def speech_to_text(self, audio_data: bytes):
        from backend.schemas.voice import TranscriptionResponse
        return TranscriptionResponse(
            transcript="voix transcrite",
            confidence=0.95
        )
    
    async def text_to_speech(self, request):
        # Retourne des données audio fake
        return b"FAKE_WAV_DATA"


class FakeWeatherService:
    """Fake Weather service pour tests"""
    
    def __init__(self, settings):
        self.settings = settings
    
    async def initialize(self):
        pass
    
    def is_available(self) -> bool:
        return True
    
    async def get_weather(self, city: str = "Perpignan") -> dict:
        return {"temp": 20, "humidity": 60, "wind": 10}
    
    def format_weather_info(self, weather_data: dict, city: str = "Perpignan") -> str:
        return f"\\nMETEO {city}: 20°C\\n"
    
    def detect_weather_request(self, message: str) -> bool:
        return "météo" in message.lower()
    
    def extract_city(self, message: str) -> str:
        return "Perpignan"


class FakeHomeAssistantService:
    """Fake HomeAssistant service pour tests"""
    
    def __init__(self, settings):
        self.settings = settings
    
    async def initialize(self):
        pass
    
    async def close(self):
        pass
    
    def is_available(self) -> bool:
        return True


@pytest.fixture
def test_settings():
    """Settings de test"""
    return Settings(
        api_key="test-api-key",
        allowed_origins=["http://testserver"],
        log_level="INFO",
        log_file=None  # Pas de fichier log en test
    )


@pytest.fixture
def app(test_settings):
    """Application FastAPI avec fake services"""
    app = create_app(test_settings)
    
    # Override des services par des fakes
    app.state.llm = FakeLLMService(test_settings)
    app.state.memory = FakeMemoryService(test_settings) 
    app.state.voice = FakeVoiceService(test_settings)
    app.state.weather = FakeWeatherService(test_settings)
    app.state.home_assistant = FakeHomeAssistantService(test_settings)
    
    return app


@pytest.fixture
def client(app):
    """Client de test FastAPI"""
    return TestClient(app)


@pytest.fixture
def auth_headers(test_settings):
    """Headers d'authentification pour tests"""
    return {"X-API-Key": test_settings.api_key}