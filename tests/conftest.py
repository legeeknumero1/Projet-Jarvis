#!/usr/bin/env python3
"""
Configuration pytest pour les tests Jarvis
Instance #1 - EN_COURS - Configuration tests
"""

import pytest
import os
import sys
from pathlib import Path


# Ajouter le répertoire racine du projet au path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


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


@pytest.fixture(scope="function")
def mock_env_vars():
    """Mock des variables d'environnement pour les tests"""
    return {
        "DATABASE_URL": "postgresql://test:test@localhost:5432/test_db",
        "REDIS_URL": "redis://localhost:6379",
        "OLLAMA_BASE_URL": "http://localhost:11434",
        "ENVIRONMENT": "test"
    }


@pytest.fixture(scope="function")
def test_config(mock_env_vars):
    """Configuration de test"""
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