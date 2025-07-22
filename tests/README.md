# 🧪 Tests Jarvis

## Description

Suite de tests automatisés pour le projet Jarvis, couvrant :
- Tests unitaires des composants principaux
- Tests d'intégration avec Ollama
- Tests de configuration
- Tests de structure du projet

## Installation

```bash
# Installer les dépendances de test
pip install -r tests/requirements.txt
```

## Exécution

```bash
# Tous les tests
pytest tests/

# Tests unitaires uniquement
pytest tests/ -m unit

# Tests d'intégration (requiert Ollama)
pytest tests/ -m integration

# Tests avec couverture
pytest tests/ --cov=backend --cov-report=html

# Tests verbeux
pytest tests/ -v

# Tests rapides (exclure les lents)
pytest tests/ -m "not slow"
```

## Structure

- `conftest.py` : Configuration pytest et fixtures
- `test_config.py` : Tests de configuration
- `test_ollama.py` : Tests d'intégration Ollama
- `requirements.txt` : Dépendances de test

## Markers

- `@pytest.mark.unit` : Tests unitaires
- `@pytest.mark.integration` : Tests d'intégration
- `@pytest.mark.slow` : Tests lents
- `@pytest.mark.ollama` : Tests nécessitant Ollama

## Créé par

Instance #1 - 2025-07-18 19:05