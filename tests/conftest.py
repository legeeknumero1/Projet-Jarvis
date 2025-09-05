#!/usr/bin/env python3
"""
🧪 PYTEST ENTERPRISE CONFIGURATION - JARVIS V1.3.2
===================================================
Instance #1 - EN_COURS - Configuration tests enterprise grade
Target: 85% test coverage with comprehensive fixtures
"""

import asyncio
import pytest
import pytest_asyncio
import os
import sys
from pathlib import Path
from typing import AsyncGenerator, Dict, Any, Optional, List
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
import jwt
import json
import httpx
from fastapi.testclient import TestClient

# Ajouter le répertoire racine du projet au path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configuration asyncio pour tests async
pytest_plugins = ('pytest_asyncio',)

# ===========================================
# 🔧 PATH FIXTURES - PROJET STRUCTURE
# ===========================================

@pytest.fixture(scope="session")
def project_root_path():
    """Retourne le chemin racine du projet"""
    return Path(__file__).parent.parent

@pytest.fixture(scope="session")
def backend_path(project_root_path):
    """Retourne le chemin du backend"""
    return project_root_path / "backend"

@pytest.fixture(scope="session")
def frontend_path(project_root_path):
    """Retourne le chemin du frontend"""
    return project_root_path / "frontend"

@pytest.fixture(scope="session")
def services_path(project_root_path):
    """Retourne le chemin des services"""
    return project_root_path / "services"

@pytest.fixture(scope="session")
def docs_path(project_root_path):
    """Retourne le chemin de la documentation"""
    return project_root_path / "docs"

# ===========================================
# 🌐 ENVIRONMENT FIXTURES - CONFIGURATION
# ===========================================

@pytest.fixture(scope="function")
def mock_env_vars():
    """Variables d'environnement pour tests avec sécurité enterprise"""
    return {
        "ENVIRONMENT": "testing",
        "DEBUG": "true",
        "LOG_LEVEL": "DEBUG",
        "JARVIS_SECRET_KEY": "test-secret-key-32-chars-long-123456",
        "JWT_ALGORITHM": "HS256",
        "JWT_EXPIRE_MINUTES": "30",
        "DATABASE_URL": "sqlite+aiosqlite:///:memory:",
        "REDIS_URL": "redis://localhost:6379",
        "OLLAMA_BASE_URL": "http://localhost:11434",
        "CORS_ORIGINS": "http://localhost:3000,http://localhost:3001",
        "TRUSTED_HOSTS": "localhost,127.0.0.1"
    }

@pytest.fixture(scope="function")
def test_config(mock_env_vars):
    """Configuration de test avec isolation environnement"""
    # Sauvegarder les variables existantes
    original_env = {}
    for key, value in mock_env_vars.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value
    
    yield mock_env_vars
    
    # Restaurer les variables originales
    for key, value in original_env.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value

# ===========================================
# 📊 DATABASE FIXTURES - TESTING ISOLATION
# ===========================================

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_db_session():
    """Mock database session for isolated testing"""
    from unittest.mock import AsyncMock
    
    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.refresh = AsyncMock()
    mock_session.close = AsyncMock()
    mock_session.execute = AsyncMock()
    mock_session.scalars = AsyncMock()
    
    return mock_session

# ===========================================
# 🔐 AUTHENTICATION FIXTURES - JWT SECURITY
# ===========================================

@pytest.fixture
def test_user_data() -> Dict[str, Any]:
    """Test user data following security patterns"""
    return {
        "id": 1,
        "username": "test_user",
        "email": "test@jarvis.local",
        "full_name": "Test User",
        "is_active": True,
        "is_superuser": False,
        "created_at": datetime.utcnow(),
        "last_login": datetime.utcnow()
    }

@pytest.fixture
def test_admin_user_data() -> Dict[str, Any]:
    """Test admin user data for privileged operations"""
    return {
        "id": 2,
        "username": "admin_user", 
        "email": "admin@jarvis.local",
        "full_name": "Admin User",
        "is_active": True,
        "is_superuser": True,
        "created_at": datetime.utcnow(),
        "last_login": datetime.utcnow()
    }

@pytest.fixture
def valid_jwt_token(test_user_data: Dict[str, Any]) -> str:
    """Generate valid JWT token for authentication tests"""
    # Mock JWT creation for testing
    payload = {
        "sub": str(test_user_data["id"]),
        "exp": datetime.utcnow() + timedelta(minutes=30),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, "test-secret-key-32-chars-long-123456", algorithm="HS256")

@pytest.fixture
def expired_jwt_token(test_user_data: Dict[str, Any]) -> str:
    """Generate expired JWT token for security tests"""
    payload = {
        "sub": str(test_user_data["id"]),
        "exp": datetime.utcnow() - timedelta(minutes=30),  # Already expired
        "iat": datetime.utcnow() - timedelta(minutes=60)
    }
    return jwt.encode(payload, "test-secret-key-32-chars-long-123456", algorithm="HS256")

@pytest.fixture
def invalid_jwt_token() -> str:
    """Generate invalid JWT token for security tests"""
    return "invalid.jwt.token.for.testing"

@pytest.fixture
def auth_headers(valid_jwt_token: str) -> Dict[str, str]:
    """Authentication headers with valid JWT"""
    return {"Authorization": f"Bearer {valid_jwt_token}"}

@pytest.fixture
def admin_auth_headers(test_admin_user_data: Dict[str, Any]) -> Dict[str, str]:
    """Admin authentication headers"""
    payload = {
        "sub": str(test_admin_user_data["id"]),
        "exp": datetime.utcnow() + timedelta(minutes=30),
        "iat": datetime.utcnow()
    }
    token = jwt.encode(payload, "test-secret-key-32-chars-long-123456", algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}

# ===========================================
# 🌐 HTTP CLIENT FIXTURES - API TESTING
# ===========================================

@pytest.fixture
def mock_test_client():
    """Mock FastAPI test client pour tests isolés"""
    mock_client = MagicMock(spec=TestClient)
    
    # Configure mock responses
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"message": "success", "data": {}}
    mock_response.text = "success"
    
    mock_client.get.return_value = mock_response
    mock_client.post.return_value = mock_response
    mock_client.put.return_value = mock_response
    mock_client.delete.return_value = mock_response
    
    return mock_client

@pytest.fixture
async def mock_async_client():
    """Mock async HTTP client pour WebSocket et streaming tests"""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    
    # Configure mock responses
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"message": "success", "data": {}}
    mock_response.text = "success"
    
    mock_client.get.return_value = mock_response
    mock_client.post.return_value = mock_response
    mock_client.put.return_value = mock_response
    mock_client.delete.return_value = mock_response
    
    return mock_client

# ===========================================
# 🤖 OLLAMA MOCKING - AI SERVICE SIMULATION
# ===========================================

@pytest.fixture
def mock_ollama_client():
    """Mock Ollama client for AI service testing"""
    mock_client = AsyncMock()
    
    # Configure successful responses
    mock_client.is_available.return_value = True
    mock_client.list_models.return_value = [
        {"name": "llama3.1:latest", "size": 4661212928, "modified_at": "2024-01-15T10:00:00Z"},
        {"name": "llama3.2:1b", "size": 1234567890, "modified_at": "2024-01-15T10:00:00Z"}
    ]
    mock_client.generate.return_value = "Mocked AI response for testing"
    mock_client.chat.return_value = "Mocked chat response"
    mock_client.pull_model.return_value = True
    mock_client.ensure_model_available.return_value = True
    mock_client.test_connection.return_value = True
    mock_client.get_model_info.return_value = {
        "modelinfo": {"general.architecture": "llama"},
        "parameters": {"num_ctx": 2048}
    }
    
    # Mock streaming response
    async def mock_stream_generate(*args, **kwargs):
        responses = ["Mocked ", "streaming ", "AI ", "response"]
        for response in responses:
            yield response
    
    mock_client.stream_generate = mock_stream_generate
    
    return mock_client

@pytest.fixture
def mock_ollama_unavailable():
    """Mock Ollama client when service is unavailable"""
    mock_client = AsyncMock()
    
    # Configure unavailable responses
    mock_client.is_available.return_value = False
    mock_client.test_connection.return_value = False
    mock_client.generate.side_effect = Exception("Ollama service unavailable")
    mock_client.chat.side_effect = Exception("Ollama service unavailable")
    mock_client.list_models.return_value = []
    
    return mock_client

# ===========================================
# 📊 DATA FIXTURES - TEST DATA GENERATION
# ===========================================

@pytest.fixture
def sample_conversation_data() -> Dict[str, Any]:
    """Sample conversation data for testing"""
    return {
        "user_id": 1,
        "message": "Hello Jarvis, how are you today?",
        "response": "Hello! I'm functioning well and ready to assist you.",
        "timestamp": datetime.utcnow(),
        "model_used": "llama3.1:latest",
        "response_time": 1.25,
        "tokens_used": 45,
        "context_data": {"mood": "friendly", "topic": "greeting"}
    }

@pytest.fixture
def sample_memory_data() -> Dict[str, Any]:
    """Sample memory data for testing"""
    return {
        "user_id": 1,
        "memory_type": "personal",
        "content": "User prefers coffee over tea",
        "importance_score": 0.7,
        "created_at": datetime.utcnow(),
        "last_accessed": datetime.utcnow(),
        "tags": ["preferences", "beverages"],
        "metadata": {"confidence": 0.85, "source": "conversation"}
    }

@pytest.fixture
def multiple_conversations_data() -> List[Dict[str, Any]]:
    """Multiple conversations for bulk testing"""
    conversations = []
    for i in range(5):
        conversations.append({
            "user_id": 1,
            "message": f"Test message {i+1}",
            "response": f"Test response {i+1}",
            "timestamp": datetime.utcnow() - timedelta(hours=i),
            "model_used": "llama3.1:latest",
            "response_time": 1.0 + (i * 0.1),
            "tokens_used": 20 + (i * 5)
        })
    return conversations

# ===========================================
# 🌐 EXTERNAL API MOCKING - ISOLATION
# ===========================================

@pytest.fixture
def mock_external_apis():
    """Mock all external API calls for isolated testing"""
    mocks = {
        'brave_search': MagicMock(),
        'weather_api': MagicMock(),
        'home_assistant': MagicMock(),
        'browserbase': MagicMock(),
        'gemini_api': MagicMock()
    }
    
    # Configure mock responses
    mocks['brave_search'].search.return_value = {
        "web": {"results": [{"title": "Test Result", "url": "https://test.com", "description": "Test description"}]}
    }
    
    mocks['weather_api'].get_weather.return_value = {
        "temperature": 22.5,
        "condition": "sunny",
        "humidity": 65,
        "location": "Test City"
    }
    
    mocks['home_assistant'].get_state.return_value = {"state": "on", "attributes": {}}
    mocks['browserbase'].navigate.return_value = {"status": "success", "content": "Page content"}
    mocks['gemini_api'].generate.return_value = "Gemini AI response"
    
    return mocks

# ===========================================
# ⚡ PERFORMANCE FIXTURES - LOAD TESTING
# ===========================================

@pytest.fixture
def performance_timer():
    """Timer fixture for performance testing"""
    import time
    
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.perf_counter()
        
        def stop(self):
            self.end_time = time.perf_counter()
            return self.elapsed
        
        @property
        def elapsed(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None
    
    return Timer()

# ===========================================
# 📁 FILE SYSTEM FIXTURES - I/O TESTING
# ===========================================

@pytest.fixture
def temp_test_dir(tmp_path):
    """Create temporary directory for file system tests"""
    test_dir = tmp_path / "jarvis_test"
    test_dir.mkdir()
    
    # Create subdirectories
    (test_dir / "logs").mkdir()
    (test_dir / "data").mkdir()
    (test_dir / "models").mkdir()
    
    yield test_dir

@pytest.fixture
def sample_log_file(temp_test_dir):
    """Create sample log file for testing"""
    log_file = temp_test_dir / "logs" / "test.log"
    log_content = """2025-01-17 10:00:00 INFO Starting Jarvis backend
2025-01-17 10:00:01 DEBUG Database connection established
2025-01-17 10:00:02 WARNING Ollama service not responding
2025-01-17 10:00:03 ERROR Failed to load model: llama3.1:latest
2025-01-17 10:00:04 INFO Retrying Ollama connection
2025-01-17 10:00:05 INFO Successfully connected to Ollama
"""
    log_file.write_text(log_content)
    return log_file

# ===========================================
# 🔒 SECURITY FIXTURES - PENETRATION TESTING
# ===========================================

@pytest.fixture
def malicious_payloads():
    """Common attack payloads for security testing"""
    return {
        "sql_injection": [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM users --"
        ],
        "xss_payloads": [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>"
        ],
        "command_injection": [
            "; ls -la",
            "| whoami",
            "$(cat /etc/passwd)",
            "`rm -rf /`"
        ],
        "path_traversal": [
            "../../../etc/passwd",
            "..\\\\..\\\\..\\\\windows\\\\system32\\\\config\\\\sam",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "....//....//....//etc/passwd"
        ]
    }

# ===========================================
# 📊 METRICS FIXTURES - MONITORING TESTING
# ===========================================

@pytest.fixture
def mock_prometheus_metrics():
    """Mock Prometheus metrics for monitoring tests"""
    mock_metrics = MagicMock()
    mock_metrics.request_count = MagicMock()
    mock_metrics.request_duration = MagicMock()
    mock_metrics.active_connections = MagicMock()
    mock_metrics.ai_response_time = MagicMock()
    mock_metrics.error_count = MagicMock()
    
    # Configure metric methods
    mock_metrics.request_count.inc = MagicMock()
    mock_metrics.request_duration.observe = MagicMock()
    mock_metrics.active_connections.set = MagicMock()
    mock_metrics.ai_response_time.observe = MagicMock()
    mock_metrics.error_count.inc = MagicMock()
    
    return mock_metrics

# ===========================================
# 🏗️ CLEANUP AND TEARDOWN FIXTURES
# ===========================================

@pytest.fixture(scope="function", autouse=True)
async def cleanup_after_test():
    """Automatic cleanup after each test"""
    yield
    
    # Clear any global state
    # Reset singletons if any
    # Clean up temporary files
    # Close any remaining connections
    pass

# ===========================================
# 🛠️ UTILITY FUNCTIONS FOR TESTS
# ===========================================

def assert_response_time(elapsed_time: float, max_time: float = 1.0):
    """Assert API response time is within acceptable limits"""
    assert elapsed_time <= max_time, f"Response too slow: {elapsed_time}s > {max_time}s"

def assert_jwt_structure(token: str):
    """Assert JWT token has valid structure"""
    parts = token.split('.')
    assert len(parts) == 3, "JWT must have 3 parts separated by dots"
    
    # Verify each part is base64 encoded
    import base64
    try:
        for part in parts[:2]:  # Header and payload
            base64.urlsafe_b64decode(part + '==')  # Add padding
    except Exception:
        pytest.fail("JWT parts must be valid base64")

def create_test_websocket_message(message_type: str, data: Dict[str, Any]) -> str:
    """Create test WebSocket message in expected format"""
    return json.dumps({
        "type": message_type,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    })

def pytest_configure(config):
    """Configuration globale pytest"""
    # Ajouter des markers personnalisés
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "ollama: marks tests that require Ollama service"
    )


def pytest_collection_modifyitems(config, items):
    """Modifier les items de collection pour ajouter des markers"""
    for item in items:
        # Ajouter le marker 'slow' pour les tests qui prennent du temps
        if "ollama" in item.name or "integration" in item.name:
            item.add_marker(pytest.mark.slow)
        
        # Ajouter le marker 'integration' pour les tests d'intégration
        if "integration" in item.name or "ollama" in item.name:
            item.add_marker(pytest.mark.integration)
        else:
            item.add_marker(pytest.mark.unit)


# Instance #1 - FINI - Configuration tests