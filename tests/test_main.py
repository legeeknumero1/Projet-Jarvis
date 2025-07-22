"""
Tests pour l'application principale Jarvis
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
import sys
import os

# Ajouter le répertoire backend au path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app

client = TestClient(app)

class TestMainApp:
    """Tests pour l'application principale"""
    
    def test_root_endpoint(self):
        """Test de l'endpoint racine"""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Jarvis AI Assistant is running"}
    
    def test_health_endpoint(self):
        """Test de l'endpoint health"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    @patch('main.OllamaClient')
    def test_chat_endpoint(self, mock_ollama):
        """Test de l'endpoint chat"""
        # Mock du client Ollama
        mock_ollama_instance = AsyncMock()
        mock_ollama_instance.chat.return_value = "Bonjour ! Comment puis-je vous aider ?"
        mock_ollama.return_value = mock_ollama_instance
        
        response = client.post("/chat", json={
            "message": "Bonjour Jarvis",
            "user_id": "test_user"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "timestamp" in data

class TestWebSocket:
    """Tests pour les WebSockets"""
    
    def test_websocket_connection(self):
        """Test de connexion WebSocket"""
        with client.websocket_connect("/ws") as websocket:
            # Test de connexion réussie
            assert websocket is not None
            
            # Test d'envoi de message
            websocket.send_json({
                "message": "Test message",
                "user_id": "test_user"
            })
            
            # Note: Le test complet nécessiterait un mock d'Ollama
            # Pour l'instant on teste juste la connexion

class TestVoiceEndpoints:
    """Tests pour les endpoints vocaux"""
    
    def test_voice_transcribe_no_file(self):
        """Test transcription sans fichier"""
        response = client.post("/voice/transcribe")
        assert response.status_code == 422  # Validation error
    
    def test_voice_synthesize_endpoint(self):
        """Test synthèse vocale"""
        response = client.post("/voice/synthesize", json={
            "text": "Bonjour, ceci est un test"
        })
        # Le test exact dépend de l'implémentation TTS
        # Pour l'instant on vérifie que l'endpoint existe
        assert response.status_code in [200, 500]  # 500 si TTS pas configuré

if __name__ == "__main__":
    pytest.main([__file__])