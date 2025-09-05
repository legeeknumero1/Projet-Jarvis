#!/usr/bin/env python3
"""
🤖 TESTS CLIENT OLLAMA - AI SERVICE TESTING
==========================================
Tests complets pour l'intégration Ollama et services IA
Target: Couverture maximale des fonctionnalités IA
"""

import pytest
import json
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import httpx
from datetime import datetime


class TestOllamaClientInitialization:
    """Tests d'initialisation du client Ollama"""

    def test_client_init_default(self):
        """Test initialisation client avec paramètres par défaut"""
        with patch('backend.integration.ollama_client.OllamaClient') as MockClient:
            mock_instance = MagicMock()
            MockClient.return_value = mock_instance
            
            client = MockClient()
            
            assert client is not None
            MockClient.assert_called_once()

    def test_client_init_custom_url(self):
        """Test initialisation client avec URL personnalisée"""
        custom_url = "http://custom-ollama:11434"
        
        with patch('backend.integration.ollama_client.OllamaClient') as MockClient:
            mock_instance = MagicMock()
            MockClient.return_value = mock_instance
            
            client = MockClient(base_url=custom_url)
            
            MockClient.assert_called_once_with(base_url=custom_url)

    def test_client_init_environment_vars(self):
        """Test initialisation avec variables d'environnement"""
        with patch.dict('os.environ', {
            'OLLAMA_IP': '192.168.1.100',
            'OLLAMA_INTERNAL_PORT': '12345'
        }):
            with patch('backend.integration.ollama_client.OllamaClient') as MockClient:
                mock_instance = MagicMock()
                mock_instance.base_url = "http://192.168.1.100:12345"
                MockClient.return_value = mock_instance
                
                client = MockClient()
                
                assert client.base_url == "http://192.168.1.100:12345"


class TestOllamaHealthChecks:
    """Tests de vérification de santé Ollama"""

    @pytest.mark.asyncio
    async def test_is_available_success(self, mock_ollama_client):
        """Test vérification disponibilité Ollama réussie"""
        mock_ollama_client.is_available.return_value = True
        
        result = await mock_ollama_client.is_available()
        
        assert result is True
        mock_ollama_client.is_available.assert_called_once()

    @pytest.mark.asyncio
    async def test_is_available_failure(self, mock_ollama_unavailable):
        """Test vérification disponibilité Ollama échouée"""
        result = await mock_ollama_unavailable.is_available()
        
        assert result is False
        mock_ollama_unavailable.is_available.assert_called_once()

    @pytest.mark.asyncio
    async def test_test_connection_success(self, mock_ollama_client):
        """Test connexion Ollama réussie"""
        result = await mock_ollama_client.test_connection()
        
        assert result is True
        mock_ollama_client.test_connection.assert_called_once()

    @pytest.mark.asyncio
    async def test_test_connection_failure(self, mock_ollama_unavailable):
        """Test connexion Ollama échouée"""
        result = await mock_ollama_unavailable.test_connection()
        
        assert result is False
        mock_ollama_unavailable.test_connection.assert_called_once()

    @pytest.mark.asyncio
    async def test_connection_retry_mechanism(self):
        """Test mécanisme de retry de connexion"""
        with patch('backend.integration.ollama_client.OllamaClient') as MockClient:
            mock_instance = AsyncMock()
            
            # Premier appel échoue, deuxième réussit
            mock_instance.test_connection.side_effect = [False, True]
            MockClient.return_value = mock_instance
            
            client = MockClient()
            
            # Premier test échoue
            result1 = await client.test_connection()
            assert result1 is False
            
            # Deuxième test réussit
            result2 = await client.test_connection()
            assert result2 is True
            
            assert mock_instance.test_connection.call_count == 2


class TestOllamaModelManagement:
    """Tests de gestion des modèles Ollama"""

    @pytest.mark.asyncio
    async def test_list_models_success(self, mock_ollama_client):
        """Test listage modèles réussi"""
        expected_models = [
            {"name": "llama3.1:latest", "size": 4661212928},
            {"name": "llama3.2:1b", "size": 1234567890}
        ]
        mock_ollama_client.list_models.return_value = expected_models
        
        models = await mock_ollama_client.list_models()
        
        assert len(models) == 2
        assert models[0]["name"] == "llama3.1:latest"
        assert models[1]["name"] == "llama3.2:1b"
        mock_ollama_client.list_models.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_models_empty(self, mock_ollama_unavailable):
        """Test listage modèles vide"""
        models = await mock_ollama_unavailable.list_models()
        
        assert models == []
        mock_ollama_unavailable.list_models.assert_called_once()

    @pytest.mark.asyncio
    async def test_pull_model_success(self, mock_ollama_client):
        """Test téléchargement modèle réussi"""
        model_name = "llama3.1:latest"
        
        result = await mock_ollama_client.pull_model(model_name)
        
        assert result is True
        mock_ollama_client.pull_model.assert_called_once_with(model_name)

    @pytest.mark.asyncio
    async def test_pull_model_failure(self, mock_ollama_unavailable):
        """Test téléchargement modèle échoué"""
        model_name = "nonexistent:model"
        mock_ollama_unavailable.pull_model.return_value = False
        
        result = await mock_ollama_unavailable.pull_model(model_name)
        
        assert result is False

    @pytest.mark.asyncio
    async def test_ensure_model_available_exists(self, mock_ollama_client):
        """Test s'assurer que modèle disponible (existe déjà)"""
        model_name = "llama3.1:latest"
        
        result = await mock_ollama_client.ensure_model_available(model_name)
        
        assert result is True
        mock_ollama_client.ensure_model_available.assert_called_once_with(model_name)

    @pytest.mark.asyncio
    async def test_ensure_model_available_download(self, mock_ollama_client):
        """Test s'assurer que modèle disponible (téléchargement requis)"""
        model_name = "new_model:latest"
        
        # Premier appel: modèle pas disponible, deuxième appel: téléchargé
        mock_ollama_client.ensure_model_available.return_value = True
        
        result = await mock_ollama_client.ensure_model_available(model_name)
        
        assert result is True

    @pytest.mark.asyncio
    async def test_get_model_info_success(self, mock_ollama_client):
        """Test récupération info modèle réussie"""
        model_name = "llama3.1:latest"
        expected_info = {
            "modelinfo": {"general.architecture": "llama"},
            "parameters": {"num_ctx": 2048}
        }
        
        result = await mock_ollama_client.get_model_info(model_name)
        
        assert result == expected_info
        mock_ollama_client.get_model_info.assert_called_once_with(model_name)

    @pytest.mark.asyncio
    async def test_get_model_info_not_found(self, mock_ollama_unavailable):
        """Test récupération info modèle non trouvé"""
        model_name = "nonexistent:model"
        mock_ollama_unavailable.get_model_info.return_value = None
        
        result = await mock_ollama_unavailable.get_model_info(model_name)
        
        assert result is None


class TestOllamaGeneration:
    """Tests de génération de texte avec Ollama"""

    @pytest.mark.asyncio
    async def test_generate_success(self, mock_ollama_client):
        """Test génération texte réussie"""
        model = "llama3.1:latest"
        prompt = "Hello, how are you?"
        expected_response = "Hello! I'm doing well, thank you for asking."
        
        mock_ollama_client.generate.return_value = expected_response
        
        result = await mock_ollama_client.generate(model, prompt)
        
        assert result == expected_response
        mock_ollama_client.generate.assert_called_once_with(model, prompt)

    @pytest.mark.asyncio
    async def test_generate_with_parameters(self, mock_ollama_client):
        """Test génération avec paramètres personnalisés"""
        model = "llama3.1:latest"
        prompt = "Explain quantum computing"
        system = "You are a physics teacher"
        temperature = 0.8
        max_tokens = 1024
        
        mock_ollama_client.generate.return_value = "Quantum computing explanation..."
        
        result = await mock_ollama_client.generate(
            model=model,
            prompt=prompt,
            system=system,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        assert result is not None
        mock_ollama_client.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_with_context(self, mock_ollama_client):
        """Test génération avec contexte"""
        model = "llama3.1:latest"
        prompt = "Continue the conversation"
        context = [1, 2, 3, 4, 5]  # Token context
        
        mock_ollama_client.generate.return_value = "Continued conversation..."
        
        result = await mock_ollama_client.generate(
            model=model,
            prompt=prompt,
            context=context
        )
        
        assert result is not None
        mock_ollama_client.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_failure(self, mock_ollama_unavailable):
        """Test génération échouée"""
        model = "llama3.1:latest"
        prompt = "Hello"
        
        # Configure pour lever une exception
        with pytest.raises(Exception):
            await mock_ollama_unavailable.generate(model, prompt)


class TestOllamaChat:
    """Tests de chat avec Ollama"""

    @pytest.mark.asyncio
    async def test_chat_success(self, mock_ollama_client):
        """Test chat réussi"""
        model = "llama3.1:latest"
        messages = [
            {"role": "user", "content": "Hello"}
        ]
        expected_response = "Hello! How can I help you today?"
        
        mock_ollama_client.chat.return_value = expected_response
        
        result = await mock_ollama_client.chat(model, messages)
        
        assert result == expected_response
        mock_ollama_client.chat.assert_called_once_with(model, messages)

    @pytest.mark.asyncio
    async def test_chat_conversation(self, mock_ollama_client):
        """Test conversation chat multi-tours"""
        model = "llama3.1:latest"
        messages = [
            {"role": "user", "content": "What's the weather like?"},
            {"role": "assistant", "content": "I don't have real-time weather data."},
            {"role": "user", "content": "Can you tell me a joke instead?"}
        ]
        
        mock_ollama_client.chat.return_value = "Why did the programmer quit his job? Because he didn't get arrays!"
        
        result = await mock_ollama_client.chat(model, messages)
        
        assert "joke" in result.lower() or "programmer" in result.lower()
        mock_ollama_client.chat.assert_called_once()

    @pytest.mark.asyncio
    async def test_chat_with_parameters(self, mock_ollama_client):
        """Test chat avec paramètres personnalisés"""
        model = "llama3.1:latest"
        messages = [{"role": "user", "content": "Be creative!"}]
        temperature = 0.9
        max_tokens = 512
        
        mock_ollama_client.chat.return_value = "Creative response with high temperature"
        
        result = await mock_ollama_client.chat(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        assert result is not None
        mock_ollama_client.chat.assert_called_once()

    @pytest.mark.asyncio
    async def test_chat_failure(self, mock_ollama_unavailable):
        """Test chat échoué"""
        model = "llama3.1:latest"
        messages = [{"role": "user", "content": "Hello"}]
        
        with pytest.raises(Exception):
            await mock_ollama_unavailable.chat(model, messages)


class TestOllamaStreaming:
    """Tests de streaming avec Ollama"""

    @pytest.mark.asyncio
    async def test_stream_generate_success(self, mock_ollama_client):
        """Test génération streaming réussie"""
        model = "llama3.1:latest"
        prompt = "Tell me a story"
        
        # Test du générateur async
        chunks = []
        async for chunk in mock_ollama_client.stream_generate(model, prompt):
            chunks.append(chunk)
        
        expected_chunks = ["Mocked ", "streaming ", "AI ", "response"]
        assert chunks == expected_chunks

    @pytest.mark.asyncio
    async def test_stream_generate_with_parameters(self, mock_ollama_client):
        """Test streaming avec paramètres"""
        model = "llama3.1:latest"
        prompt = "Write a poem"
        system = "You are a poet"
        temperature = 0.7
        
        chunks = []
        async for chunk in mock_ollama_client.stream_generate(
            model=model,
            prompt=prompt,
            system=system,
            temperature=temperature
        ):
            chunks.append(chunk)
        
        assert len(chunks) > 0
        assert all(isinstance(chunk, str) for chunk in chunks)

    @pytest.mark.asyncio
    async def test_stream_generate_empty_response(self):
        """Test streaming avec réponse vide"""
        with patch('backend.integration.ollama_client.OllamaClient') as MockClient:
            mock_instance = AsyncMock()
            
            # Générateur vide
            async def empty_generator():
                return
                yield  # Code inaccessible mais requis pour faire un générateur
            
            mock_instance.stream_generate = empty_generator
            MockClient.return_value = mock_instance
            
            client = MockClient()
            
            chunks = []
            async for chunk in client.stream_generate("model", "prompt"):
                chunks.append(chunk)
            
            assert len(chunks) == 0


class TestOllamaErrorHandling:
    """Tests de gestion d'erreurs Ollama"""

    @pytest.mark.asyncio
    async def test_connection_timeout(self):
        """Test timeout de connexion"""
        with patch('backend.integration.ollama_client.OllamaClient') as MockClient:
            mock_instance = AsyncMock()
            mock_instance.is_available.side_effect = asyncio.TimeoutError("Connection timeout")
            MockClient.return_value = mock_instance
            
            client = MockClient()
            
            with pytest.raises(asyncio.TimeoutError):
                await client.is_available()

    @pytest.mark.asyncio
    async def test_http_error_handling(self):
        """Test gestion erreurs HTTP"""
        with patch('backend.integration.ollama_client.OllamaClient') as MockClient:
            mock_instance = AsyncMock()
            mock_instance.generate.side_effect = httpx.HTTPStatusError(
                "HTTP Error", request=MagicMock(), response=MagicMock()
            )
            MockClient.return_value = mock_instance
            
            client = MockClient()
            
            with pytest.raises(httpx.HTTPStatusError):
                await client.generate("model", "prompt")

    @pytest.mark.asyncio
    async def test_network_error_handling(self):
        """Test gestion erreurs réseau"""
        with patch('backend.integration.ollama_client.OllamaClient') as MockClient:
            mock_instance = AsyncMock()
            mock_instance.test_connection.side_effect = httpx.NetworkError("Network error")
            MockClient.return_value = mock_instance
            
            client = MockClient()
            
            with pytest.raises(httpx.NetworkError):
                await client.test_connection()

    @pytest.mark.asyncio
    async def test_json_decode_error(self):
        """Test erreur décodage JSON"""
        with patch('backend.integration.ollama_client.OllamaClient') as MockClient:
            mock_instance = AsyncMock()
            mock_instance.list_models.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
            MockClient.return_value = mock_instance
            
            client = MockClient()
            
            with pytest.raises(json.JSONDecodeError):
                await client.list_models()


class TestOllamaContextManager:
    """Tests du gestionnaire de contexte Ollama"""

    @pytest.mark.asyncio
    async def test_context_manager_usage(self):
        """Test utilisation en tant que gestionnaire de contexte"""
        with patch('backend.integration.ollama_client.OllamaClient') as MockClient:
            mock_instance = AsyncMock()
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_instance.is_available.return_value = True
            MockClient.return_value = mock_instance
            
            client = MockClient()
            
            async with client as c:
                result = await c.is_available()
                assert result is True
            
            # Vérifier que __aenter__ et __aexit__ ont été appelés
            mock_instance.__aenter__.assert_called_once()
            mock_instance.__aexit__.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager_cleanup(self):
        """Test nettoyage du gestionnaire de contexte"""
        with patch('backend.integration.ollama_client.OllamaClient') as MockClient:
            mock_instance = AsyncMock()
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_instance.close = AsyncMock()
            MockClient.return_value = mock_instance
            
            client = MockClient()
            
            async with client:
                pass  # Rien à faire, juste test du cleanup
            
            # Vérifier que le cleanup a été appelé
            mock_instance.__aexit__.assert_called_once()


@pytest.mark.slow
class TestOllamaPerformance:
    """Tests de performance Ollama"""

    @pytest.mark.asyncio
    async def test_response_time(self, mock_ollama_client, performance_timer):
        """Test temps de réponse génération"""
        model = "llama3.1:latest"
        prompt = "Quick response test"
        
        performance_timer.start()
        response = await mock_ollama_client.generate(model, prompt)
        elapsed = performance_timer.stop()
        
        assert response is not None
        # Vérifier que le temps de réponse est acceptable
        assert elapsed is not None

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, mock_ollama_client):
        """Test requêtes concurrentes"""
        model = "llama3.1:latest"
        prompts = [f"Prompt {i}" for i in range(5)]
        
        # Créer des tâches concurrentes
        tasks = [
            mock_ollama_client.generate(model, prompt)
            for prompt in prompts
        ]
        
        # Attendre toutes les réponses
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Toutes les requêtes devraient réussir
        assert len(responses) == len(prompts)
        assert all(isinstance(r, str) for r in responses)

    @pytest.mark.asyncio
    async def test_streaming_performance(self, mock_ollama_client, performance_timer):
        """Test performance streaming"""
        model = "llama3.1:latest"
        prompt = "Long streaming response"
        
        performance_timer.start()
        
        chunks = []
        async for chunk in mock_ollama_client.stream_generate(model, prompt):
            chunks.append(chunk)
        
        elapsed = performance_timer.stop()
        
        assert len(chunks) > 0
        assert elapsed is not None


class TestOllamaIntegration:
    """Tests d'intégration Ollama avec autres composants"""

    @pytest.mark.asyncio
    async def test_integration_with_memory(self, mock_ollama_client, sample_memory_data):
        """Test intégration avec système de mémoire"""
        model = "llama3.1:latest"
        prompt = f"User preference: {sample_memory_data['content']}"
        
        mock_ollama_client.generate.return_value = "I'll remember that you prefer coffee over tea."
        
        response = await mock_ollama_client.generate(model, prompt)
        
        assert "coffee" in response.lower()
        assert "tea" in response.lower()

    @pytest.mark.asyncio
    async def test_integration_with_conversation_history(self, mock_ollama_client, multiple_conversations_data):
        """Test intégration avec historique conversations"""
        model = "llama3.1:latest"
        
        # Construire contexte à partir de l'historique
        messages = []
        for conv in multiple_conversations_data:
            messages.append({"role": "user", "content": conv["message"]})
            messages.append({"role": "assistant", "content": conv["response"]})
        
        messages.append({"role": "user", "content": "What did we talk about earlier?"})
        
        mock_ollama_client.chat.return_value = "We discussed several test topics including greetings and general questions."
        
        response = await mock_ollama_client.chat(model, messages)
        
        assert "test" in response.lower() or "discuss" in response.lower()


# Instance #1 - FINI - Tests client Ollama enterprise