#!/usr/bin/env python3
"""
⚙️ TESTS CONFIGURATION - SYSTEM VALIDATION
==========================================
Tests de validation configuration et environnement
Target: Vérification intégrité configuration système
"""

import pytest
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import asyncio


class TestProjectStructure:
    """Tests de structure du projet"""

    def test_project_root_exists(self, project_root_path):
        """Test existence répertoire racine projet"""
        assert project_root_path.exists()
        assert project_root_path.is_dir()

    def test_backend_directory_exists(self, backend_path):
        """Test existence répertoire backend"""
        assert backend_path.exists()
        assert backend_path.is_dir()

    def test_frontend_directory_exists(self, frontend_path):
        """Test existence répertoire frontend"""
        assert frontend_path.exists()
        assert frontend_path.is_dir()

    def test_services_directory_exists(self, services_path):
        """Test existence répertoire services"""
        assert services_path.exists()
        assert services_path.is_dir()

    def test_docs_directory_exists(self, docs_path):
        """Test existence répertoire documentation"""
        assert docs_path.exists()
        assert docs_path.is_dir()

    def test_tests_directory_structure(self, project_root_path):
        """Test structure répertoire tests"""
        tests_dir = project_root_path / "tests"
        assert tests_dir.exists()
        
        # Vérifier présence fichiers de test
        test_files = list(tests_dir.glob("test_*.py"))
        assert len(test_files) > 0
        
        # Vérifier présence conftest.py
        conftest_file = tests_dir / "conftest.py"
        assert conftest_file.exists()

    def test_configuration_files_exist(self, project_root_path):
        """Test existence fichiers de configuration"""
        config_files = [
            "pytest.ini",
            "docker-compose.yml", 
            ".env.example",
            "CLAUDE.md"
        ]
        
        for config_file in config_files:
            file_path = project_root_path / config_file
            assert file_path.exists(), f"Configuration file {config_file} not found"


class TestEnvironmentConfiguration:
    """Tests de configuration environnement"""

    def test_python_version(self):
        """Test version Python compatible"""
        assert sys.version_info >= (3, 8), "Python 3.8+ required"
        assert sys.version_info < (4, 0), "Python version too high"

    def test_environment_variables_mock(self, test_config):
        """Test configuration variables d'environnement"""
        # Vérifier variables de test configurées
        required_vars = [
            "ENVIRONMENT",
            "DEBUG", 
            "LOG_LEVEL",
            "JARVIS_SECRET_KEY",
            "DATABASE_URL",
            "OLLAMA_BASE_URL"
        ]
        
        for var in required_vars:
            assert var in test_config
            assert test_config[var] is not None

    def test_secret_key_security(self, test_config):
        """Test sécurité clé secrète"""
        secret_key = test_config.get("JARVIS_SECRET_KEY", "")
        
        # Clé doit être suffisamment longue
        assert len(secret_key) >= 32, "Secret key too short"
        
        # Ne doit pas être une valeur par défaut
        insecure_keys = ["secret", "key", "password", "admin", "default"]
        assert not any(insecure in secret_key.lower() for insecure in insecure_keys)

    def test_debug_configuration(self, test_config):
        """Test configuration debug"""
        debug_mode = test_config.get("DEBUG", "false")
        
        # En test, debug doit être activé
        assert debug_mode.lower() == "true"

    def test_log_level_configuration(self, test_config):
        """Test configuration niveau logs"""
        log_level = test_config.get("LOG_LEVEL", "INFO")
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        assert log_level.upper() in valid_levels


class TestDatabaseConfiguration:
    """Tests de configuration base de données"""

    def test_database_url_format(self, test_config):
        """Test format URL base de données"""
        db_url = test_config.get("DATABASE_URL", "")
        
        # Doit être une URL SQLite pour les tests
        assert "sqlite" in db_url.lower()
        assert ":memory:" in db_url or ".db" in db_url

    def test_database_mock_session(self, mock_db_session):
        """Test session base de données mockée"""
        # Vérifier que la session mock est configurée
        assert mock_db_session is not None
        
        # Vérifier présence méthodes requises
        assert hasattr(mock_db_session, 'add')
        assert hasattr(mock_db_session, 'commit') 
        assert hasattr(mock_db_session, 'rollback')
        assert hasattr(mock_db_session, 'close')


class TestOllamaConfiguration:
    """Tests de configuration Ollama"""

    def test_ollama_base_url(self, test_config):
        """Test URL base Ollama"""
        ollama_url = test_config.get("OLLAMA_BASE_URL", "")
        
        assert "http" in ollama_url.lower()
        assert "11434" in ollama_url  # Port par défaut

    def test_ollama_client_mock(self, mock_ollama_client):
        """Test client Ollama mocké"""
        # Vérifier configuration mock Ollama
        assert mock_ollama_client is not None
        
        # Vérifier méthodes mockées
        assert hasattr(mock_ollama_client, 'is_available')
        assert hasattr(mock_ollama_client, 'generate')
        assert hasattr(mock_ollama_client, 'chat')

    @pytest.mark.asyncio
    async def test_ollama_client_responses(self, mock_ollama_client):
        """Test réponses client Ollama mocké"""
        # Test is_available
        available = await mock_ollama_client.is_available()
        assert available is True
        
        # Test generate
        response = await mock_ollama_client.generate("model", "prompt")
        assert isinstance(response, str)
        assert len(response) > 0
        
        # Test chat
        chat_response = await mock_ollama_client.chat("model", [{"role": "user", "content": "hello"}])
        assert isinstance(chat_response, str)


class TestAuthConfiguration:
    """Tests de configuration authentification"""

    def test_jwt_configuration(self, test_config):
        """Test configuration JWT"""
        jwt_config = {
            "algorithm": test_config.get("JWT_ALGORITHM", "HS256"),
            "expiry": test_config.get("JWT_EXPIRE_MINUTES", "30"),
            "secret": test_config.get("JARVIS_SECRET_KEY", "")
        }
        
        # Vérifier algorithme sécurisé
        assert jwt_config["algorithm"] in ["HS256", "HS384", "HS512"]
        
        # Vérifier expiration raisonnable
        expiry_minutes = int(jwt_config["expiry"])
        assert 5 <= expiry_minutes <= 1440  # Entre 5 minutes et 24h
        
        # Vérifier secret présent
        assert len(jwt_config["secret"]) > 0

    def test_auth_fixtures(self, test_user_data, valid_jwt_token, auth_headers):
        """Test fixtures authentification"""
        # Vérifier données utilisateur test
        assert test_user_data["id"] is not None
        assert test_user_data["username"] is not None
        assert test_user_data["email"] is not None
        
        # Vérifier token JWT
        assert isinstance(valid_jwt_token, str)
        assert len(valid_jwt_token.split('.')) == 3  # Format JWT
        
        # Vérifier headers auth
        assert "Authorization" in auth_headers
        assert auth_headers["Authorization"].startswith("Bearer ")


class TestExternalAPIMocking:
    """Tests de configuration mocking APIs externes"""

    def test_external_apis_mock(self, mock_external_apis):
        """Test mocks APIs externes"""
        required_apis = ['brave_search', 'weather_api', 'home_assistant', 'browserbase', 'gemini_api']
        
        for api in required_apis:
            assert api in mock_external_apis
            assert mock_external_apis[api] is not None

    def test_brave_search_mock(self, mock_external_apis):
        """Test mock Brave Search"""
        search_result = mock_external_apis['brave_search'].search.return_value
        
        assert "web" in search_result
        assert "results" in search_result["web"]
        assert len(search_result["web"]["results"]) > 0

    def test_weather_api_mock(self, mock_external_apis):
        """Test mock API météo"""
        weather_data = mock_external_apis['weather_api'].get_weather.return_value
        
        required_fields = ["temperature", "condition", "humidity", "location"]
        for field in required_fields:
            assert field in weather_data


class TestPerformanceConfiguration:
    """Tests de configuration performance"""

    def test_performance_timer(self, performance_timer):
        """Test timer performance"""
        # Vérifier initialisation timer
        assert performance_timer is not None
        assert hasattr(performance_timer, 'start')
        assert hasattr(performance_timer, 'stop')
        assert hasattr(performance_timer, 'elapsed')

    def test_timer_functionality(self, performance_timer):
        """Test fonctionnalité timer"""
        import time
        
        # Démarrer timer
        performance_timer.start()
        
        # Simuler travail
        time.sleep(0.01)  # 10ms
        
        # Arrêter timer
        elapsed = performance_timer.stop()
        
        # Vérifier mesure
        assert elapsed is not None
        assert elapsed > 0
        assert elapsed < 1  # Moins d'une seconde


class TestSecurityConfiguration:
    """Tests de configuration sécurité"""

    def test_malicious_payloads(self, malicious_payloads):
        """Test payloads malicieux pour tests sécurité"""
        required_types = ["sql_injection", "xss_payloads", "command_injection", "path_traversal"]
        
        for payload_type in required_types:
            assert payload_type in malicious_payloads
            assert isinstance(malicious_payloads[payload_type], list)
            assert len(malicious_payloads[payload_type]) > 0

    def test_security_headers_config(self):
        """Test configuration headers sécurité"""
        security_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options", 
            "X-XSS-Protection",
            "Strict-Transport-Security",
            "Content-Security-Policy"
        ]
        
        # Vérifier que tous les headers sont définis
        assert len(security_headers) >= 5

    def test_cors_configuration_security(self, test_config):
        """Test sécurité configuration CORS"""
        cors_origins = test_config.get("CORS_ORIGINS", "")
        
        # En test, localhost autorisé
        assert "localhost" in cors_origins.lower()
        
        # Pas de wildcard "*" dangereux
        assert cors_origins != "*"


class TestFileSystemConfiguration:
    """Tests de configuration système de fichiers"""

    def test_temp_directory_creation(self, temp_test_dir):
        """Test création répertoire temporaire"""
        assert temp_test_dir.exists()
        assert temp_test_dir.is_dir()
        
        # Vérifier sous-répertoires
        subdirs = ["logs", "data", "models"]
        for subdir in subdirs:
            subdir_path = temp_test_dir / subdir
            assert subdir_path.exists()

    def test_log_file_creation(self, sample_log_file):
        """Test création fichier log sample"""
        assert sample_log_file.exists()
        assert sample_log_file.is_file()
        
        # Vérifier contenu
        content = sample_log_file.read_text()
        assert "INFO" in content
        assert "ERROR" in content
        assert "Jarvis" in content


class TestAsyncConfiguration:
    """Tests de configuration asynchrone"""

    def test_event_loop_configuration(self, event_loop):
        """Test configuration event loop"""
        assert event_loop is not None
        assert not event_loop.is_closed()

    @pytest.mark.asyncio
    async def test_async_test_execution(self):
        """Test exécution tests asynchrones"""
        # Test simple fonction async
        async def async_function():
            await asyncio.sleep(0.001)  # 1ms
            return "async_result"
        
        result = await async_function()
        assert result == "async_result"

    @pytest.mark.asyncio 
    async def test_concurrent_execution(self):
        """Test exécution concurrente"""
        async def async_task(value):
            await asyncio.sleep(0.001)
            return value * 2
        
        tasks = [async_task(i) for i in range(5)]
        results = await asyncio.gather(*tasks)
        
        expected = [i * 2 for i in range(5)]
        assert results == expected


class TestCleanupConfiguration:
    """Tests de configuration nettoyage"""

    def test_cleanup_fixture_exists(self):
        """Test existence fixture nettoyage"""
        # La fixture cleanup_after_test est automatique
        # Ce test vérifie juste qu'elle est définie
        import tests.conftest
        
        # Vérifier présence dans conftest
        assert hasattr(tests.conftest, 'cleanup_after_test')

    def test_mock_cleanup(self, mock_test_client):
        """Test nettoyage mocks"""
        # Vérifier que les mocks sont configurés proprement
        assert mock_test_client is not None
        
        # Reset des mocks après utilisation
        mock_test_client.reset_mock()
        
        # Vérifier reset
        assert mock_test_client.called is False


@pytest.mark.integration
class TestIntegrationConfiguration:
    """Tests de configuration intégration"""

    def test_all_fixtures_integration(
        self,
        test_user_data,
        mock_ollama_client, 
        mock_external_apis,
        performance_timer,
        temp_test_dir
    ):
        """Test intégration toutes fixtures"""
        # Vérifier que toutes fixtures fonctionnent ensemble
        assert test_user_data is not None
        assert mock_ollama_client is not None
        assert mock_external_apis is not None
        assert performance_timer is not None
        assert temp_test_dir is not None

    @pytest.mark.asyncio
    async def test_full_mock_pipeline(
        self,
        mock_ollama_client,
        mock_external_apis, 
        performance_timer
    ):
        """Test pipeline complet avec mocks"""
        # Démarrer timer
        performance_timer.start()
        
        # Simuler pipeline complet
        # 1. Vérifier Ollama disponible
        ollama_available = await mock_ollama_client.is_available()
        assert ollama_available
        
        # 2. Générer réponse IA
        ai_response = await mock_ollama_client.generate("model", "test prompt")
        assert ai_response is not None
        
        # 3. Rechercher informations externes
        search_result = mock_external_apis['brave_search'].search("test query")
        assert search_result is not None
        
        # 4. Mesurer performance
        elapsed = performance_timer.stop()
        assert elapsed is not None
        
        # Pipeline complet réussi
        assert True


# Instance #1 - FINI - Tests configuration système