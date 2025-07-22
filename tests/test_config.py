#!/usr/bin/env python3
"""
Tests unitaires pour la configuration Jarvis
Instance #1 - EN_COURS - Tests configuration
"""

import pytest
import os
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.config.config import Config


class TestConfig:
    """Tests pour la classe Config"""
    
    def test_config_creation(self):
        """Test création basique de la configuration"""
        config = Config()
        assert config is not None
        
    def test_database_url_exists(self):
        """Test que DATABASE_URL est définie"""
        config = Config()
        assert hasattr(config, 'database_url')
        assert config.database_url is not None
        
    def test_redis_url_exists(self):
        """Test que REDIS_URL est définie"""
        config = Config()
        assert hasattr(config, 'redis_url')
        assert config.redis_url is not None
        
    def test_ollama_url_exists(self):
        """Test que OLLAMA_BASE_URL est définie"""
        config = Config()
        assert hasattr(config, 'ollama_base_url')
        assert config.ollama_base_url is not None
        
    def test_config_values_are_strings(self):
        """Test que les valeurs de config sont des chaînes"""
        config = Config()
        assert isinstance(config.database_url, str)
        assert isinstance(config.redis_url, str)
        assert isinstance(config.ollama_base_url, str)
        
    def test_config_values_not_empty(self):
        """Test que les valeurs ne sont pas vides"""
        config = Config()
        assert len(config.database_url) > 0
        assert len(config.redis_url) > 0
        assert len(config.ollama_base_url) > 0


class TestEnvironmentVariables:
    """Tests pour les variables d'environnement"""
    
    def test_env_file_exists(self):
        """Test que le fichier .env existe"""
        env_path = Path(__file__).parent.parent / '.env'
        assert env_path.exists(), "Fichier .env manquant"
        
    def test_env_file_readable(self):
        """Test que le fichier .env est lisible"""
        env_path = Path(__file__).parent.parent / '.env'
        if env_path.exists():
            with open(env_path, 'r') as f:
                content = f.read()
                assert len(content) > 0, "Fichier .env vide"


class TestDirectoryStructure:
    """Tests pour la structure des répertoires"""
    
    def test_backend_directory_exists(self):
        """Test que le répertoire backend existe"""
        backend_path = Path(__file__).parent.parent / 'backend'
        assert backend_path.exists(), "Répertoire backend manquant"
        
    def test_services_directory_exists(self):
        """Test que le répertoire services existe"""
        services_path = Path(__file__).parent.parent / 'services'
        assert services_path.exists(), "Répertoire services manquant"
        
    def test_frontend_directory_exists(self):
        """Test que le répertoire frontend existe"""
        frontend_path = Path(__file__).parent.parent / 'frontend'
        assert frontend_path.exists(), "Répertoire frontend manquant"
        
    def test_docs_directory_exists(self):
        """Test que le répertoire docs existe"""
        docs_path = Path(__file__).parent.parent / 'docs'
        assert docs_path.exists(), "Répertoire docs manquant"
        
    def test_logs_directory_exists(self):
        """Test que le répertoire logs existe"""
        logs_path = Path(__file__).parent.parent / 'logs'
        assert logs_path.exists(), "Répertoire logs manquant"


class TestRequiredFiles:
    """Tests pour les fichiers requis"""
    
    def test_docker_compose_exists(self):
        """Test que docker-compose.yml existe"""
        compose_path = Path(__file__).parent.parent / 'docker-compose.yml'
        assert compose_path.exists(), "docker-compose.yml manquant"
        
    def test_main_py_exists(self):
        """Test que main.py existe"""
        main_path = Path(__file__).parent.parent / 'backend' / 'main.py'
        assert main_path.exists(), "backend/main.py manquant"
        
    def test_package_json_exists(self):
        """Test que package.json existe"""
        package_path = Path(__file__).parent.parent / 'frontend' / 'package.json'
        assert package_path.exists(), "frontend/package.json manquant"
        
    def test_requirements_txt_exists(self):
        """Test que requirements.txt existe"""
        req_path = Path(__file__).parent.parent / 'backend' / 'requirements.txt'
        assert req_path.exists(), "backend/requirements.txt manquant"


if __name__ == '__main__':
    # Exécuter les tests
    pytest.main([__file__, '-v'])

# Instance #1 - FINI - Tests configuration