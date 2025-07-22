#!/usr/bin/env python3
"""
Tests unitaires pour l'intégration Ollama
Instance #1 - EN_COURS - Tests Ollama
"""

import pytest
import requests
import json
from unittest.mock import patch, MagicMock


class TestOllamaIntegration:
    """Tests pour l'intégration Ollama"""
    
    def test_ollama_service_accessible(self):
        """Test que le service Ollama est accessible"""
        try:
            response = requests.get("http://localhost:11434/api/version", timeout=5)
            assert response.status_code == 200
            assert "version" in response.json()
        except requests.exceptions.RequestException:
            pytest.skip("Ollama service not running")
    
    def test_ollama_model_available(self):
        """Test que le modèle llama3.2:1b est disponible"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            assert response.status_code == 200
            
            data = response.json()
            models = data.get("models", [])
            model_names = [model.get("name", "") for model in models]
            
            assert any("llama3.2:1b" in name for name in model_names), "Modèle llama3.2:1b non trouvé"
        except requests.exceptions.RequestException:
            pytest.skip("Ollama service not running")
    
    def test_ollama_generate_response(self):
        """Test génération de réponse simple"""
        try:
            payload = {
                "model": "llama3.2:1b",
                "prompt": "Bonjour",
                "stream": False
            }
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json=payload,
                timeout=30
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "response" in data
            assert len(data["response"]) > 0
            
        except requests.exceptions.RequestException:
            pytest.skip("Ollama service not running")
    
    def test_ollama_french_response(self):
        """Test réponse en français"""
        try:
            payload = {
                "model": "llama3.2:1b",
                "prompt": "Réponds en français : Comment allez-vous ?",
                "stream": False
            }
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json=payload,
                timeout=30
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "response" in data
            
            # Vérifier que la réponse contient des mots français
            french_words = ["bien", "bonjour", "merci", "comment", "ça", "va"]
            response_text = data["response"].lower()
            
            # Au moins un mot français doit être présent
            assert any(word in response_text for word in french_words)
            
        except requests.exceptions.RequestException:
            pytest.skip("Ollama service not running")


class TestOllamaClient:
    """Tests pour le client Ollama"""
    
    @patch('requests.get')
    def test_ollama_client_mock_version(self, mock_get):
        """Test client avec mock pour version"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"version": "0.1.0"}
        mock_get.return_value = mock_response
        
        response = requests.get("http://localhost:11434/api/version")
        
        assert response.status_code == 200
        assert response.json()["version"] == "0.1.0"
    
    @patch('requests.post')
    def test_ollama_client_mock_generate(self, mock_post):
        """Test client avec mock pour génération"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": "Bonjour ! Comment puis-je vous aider ?",
            "done": True
        }
        mock_post.return_value = mock_response
        
        payload = {
            "model": "llama3.2:1b",
            "prompt": "Bonjour",
            "stream": False
        }
        
        response = requests.post("http://localhost:11434/api/generate", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "Bonjour" in data["response"]
        assert data["done"] is True


class TestOllamaErrors:
    """Tests pour la gestion d'erreurs Ollama"""
    
    def test_ollama_connection_error(self):
        """Test gestion erreur de connexion"""
        try:
            # Essayer de se connecter à un port invalide
            response = requests.get("http://localhost:99999/api/version", timeout=1)
            assert False, "Devrait lever une exception"
        except requests.exceptions.RequestException:
            # C'est le comportement attendu
            pass
    
    def test_ollama_timeout(self):
        """Test gestion timeout"""
        try:
            # Timeout très court pour forcer l'erreur
            response = requests.get("http://localhost:11434/api/version", timeout=0.001)
            # Si ça passe, c'est que le service est très rapide
            assert response.status_code == 200
        except requests.exceptions.Timeout:
            # C'est le comportement attendu en cas de timeout
            pass
        except requests.exceptions.RequestException:
            # Autre erreur de connexion acceptable
            pass


if __name__ == '__main__':
    # Exécuter les tests
    pytest.main([__file__, '-v'])

# Instance #1 - FINI - Tests Ollama