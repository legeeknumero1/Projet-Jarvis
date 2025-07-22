#!/usr/bin/env python3
"""
🐳 Tests d'Intégration Docker - Système Mémoire Neuromorphique Jarvis
Tests complets de l'architecture Docker et des services
"""

import pytest
import asyncio
import aiohttp
import docker
import time
import json
import psycopg2
from datetime import datetime
import subprocess
import os

class TestDockerServices:
    """Tests des services Docker et de leur intégration"""
    
    @pytest.fixture(scope="class")
    def docker_client(self):
        """Client Docker pour les tests"""
        try:
            client = docker.from_env()
            return client
        except Exception as e:
            pytest.skip(f"Docker non disponible: {e}")
    
    def test_docker_compose_syntax(self):
        """Test syntaxe du fichier docker-compose.yml"""
        compose_file = "/home/enzo/Documents/Projet Jarvis/docker-compose.yml"
        
        # Vérifier que le fichier existe
        assert os.path.exists(compose_file), "docker-compose.yml non trouvé"
        
        # Vérifier syntaxe YAML basique
        with open(compose_file, 'r') as f:
            content = f.read()
            assert 'version:' in content
            assert 'services:' in content
            assert 'networks:' in content
            assert 'jarvis_network:' in content
    
    def test_network_configuration(self):
        """Test configuration réseau Jarvis"""
        compose_file = "/home/enzo/Documents/Projet Jarvis/docker-compose.yml"
        
        with open(compose_file, 'r') as f:
            content = f.read()
            
        # Vérifier configuration réseau VLAN
        assert '172.20.0.0/16' in content
        assert '172.20.0.1' in content  # Gateway
        
        # Vérifier IPs services critiques
        assert '172.20.0.40' in content  # Backend
        assert '172.20.0.100' in content  # PostgreSQL
        assert '172.20.0.120' in content  # Qdrant
        assert '172.20.0.130' in content  # TimescaleDB
    
    def test_required_services_defined(self):
        """Test présence de tous les services requis"""
        compose_file = "/home/enzo/Documents/Projet Jarvis/docker-compose.yml"
        
        with open(compose_file, 'r') as f:
            content = f.read()
        
        required_services = [
            'backend:', 'postgres:', 'redis:',
            'qdrant:', 'timescale:', 'ollama:',
            'stt-api:', 'tts-api:', 'interface:'
        ]
        
        for service in required_services:
            assert service in content, f"Service {service} manquant"
    
    def test_environment_variables(self):
        """Test variables d'environnement critiques"""
        compose_file = "/home/enzo/Documents/Projet Jarvis/docker-compose.yml"
        
        with open(compose_file, 'r') as f:
            content = f.read()
        
        critical_env_vars = [
            'QDRANT_URL=http://172.20.0.120:6333',
            'TIMESCALE_URL=postgresql://jarvis:jarvis@172.20.0.130:5432/jarvis_timeseries',
            'BRAIN_MEMORY_ENABLED=true',
            'EMOTIONAL_ANALYSIS_ENABLED=true',
            'AUTO_CONSOLIDATION_ENABLED=true'
        ]
        
        for env_var in critical_env_vars:
            assert env_var in content, f"Variable d'environnement {env_var} manquante"

class TestQdrantIntegration:
    """Tests d'intégration Qdrant"""
    
    def test_qdrant_config_file(self):
        """Test fichier configuration Qdrant"""
        config_file = "/home/enzo/Documents/Projet Jarvis/config/qdrant_config.yaml"
        
        assert os.path.exists(config_file), "qdrant_config.yaml non trouvé"
        
        with open(config_file, 'r') as f:
            content = f.read()
            
        # Vérifier configuration de base
        assert 'service:' in content
        assert 'http_port: 6333' in content
        assert 'storage:' in content
        assert 'performance:' in content
    
    @pytest.mark.asyncio
    async def test_qdrant_connection_simulation(self):
        """Test simulation connexion Qdrant"""
        # Test sans vraie connexion - vérification logique
        from backend.memory.qdrant_adapter import QdrantMemoryAdapter
        
        adapter = QdrantMemoryAdapter("http://localhost:6333")
        
        # Vérifier configuration des collections
        assert len(adapter.collections) == 4
        assert 'episodic_memory' in adapter.collections
        assert 'semantic_memory' in adapter.collections
        assert 'procedural_memory' in adapter.collections
        assert 'emotional_memory' in adapter.collections
        
        # Vérifier configuration de recherche
        assert adapter.search_config['similarity_threshold'] == 0.7
        assert adapter.search_config['emotional_boost_factor'] == 0.3

class TestTimescaleDBIntegration:
    """Tests d'intégration TimescaleDB"""
    
    def test_timescale_init_script(self):
        """Test script d'initialisation TimescaleDB"""
        init_file = "/home/enzo/Documents/Projet Jarvis/backend/db/timescale_init.sql"
        
        assert os.path.exists(init_file), "timescale_init.sql non trouvé"
        
        with open(init_file, 'r') as f:
            content = f.read()
        
        # Vérifier création des tables essentielles
        required_tables = [
            'memory_metrics', 'jarvis_activity_logs',
            'emotional_timeline', 'behavior_patterns'
        ]
        
        for table in required_tables:
            assert f"CREATE TABLE IF NOT EXISTS {table}" in content
            assert f"create_hypertable('{table}'" in content
    
    def test_timescale_functions(self):
        """Test fonctions SQL TimescaleDB"""
        init_file = "/home/enzo/Documents/Projet Jarvis/backend/db/timescale_init.sql"
        
        with open(init_file, 'r') as f:
            content = f.read()
        
        # Vérifier fonctions critiques
        assert 'get_recent_emotional_profile' in content
        assert 'detect_behavior_pattern' in content
        assert 'cleanup_old_timeseries_data' in content
        
        # Vérifier vues matérialisées
        assert 'daily_emotional_summary' in content
        assert 'consolidation_patterns' in content

class TestBackendIntegration:
    """Tests d'intégration backend FastAPI"""
    
    def test_backend_imports(self):
        """Test imports backend critiques"""
        backend_main = "/home/enzo/Documents/Projet Jarvis/backend/main.py"
        
        with open(backend_main, 'r') as f:
            content = f.read()
        
        # Vérifier imports neuromorphiques
        assert 'from memory.brain_memory_system import BrainMemorySystem' in content
        assert 'brain_memory_system = BrainMemorySystem(db)' in content
    
    def test_backend_neuromorphic_integration(self):
        """Test intégration système neuromorphique dans backend"""
        backend_main = "/home/enzo/Documents/Projet Jarvis/backend/main.py"
        
        with open(backend_main, 'r') as f:
            content = f.read()
        
        # Vérifier utilisation du système neuromorphique
        assert 'get_contextual_memories' in content
        assert 'store_interaction' in content
        assert 'SYSTÈME MÉMOIRE NEUROMORPHIQUE ACTIF' in content
    
    def test_requirements_dependencies(self):
        """Test dépendances requirements.txt"""
        requirements_file = "/home/enzo/Documents/Projet Jarvis/backend/requirements.txt"
        
        with open(requirements_file, 'r') as f:
            content = f.read()
        
        # Vérifier dépendances critiques
        assert 'qdrant-client' in content
        assert 'sqlalchemy' in content
        assert 'asyncpg' in content
        assert 'sentence-transformers' in content

class TestMemorySystemLogic:
    """Tests logique système mémoire sans dépendances externes"""
    
    def test_memory_fragment_creation(self):
        """Test création fragments mémoire"""
        from backend.memory.brain_memory_system import (
            MemoryFragment, EmotionalContext, MemoryType, ConsolidationLevel
        )
        
        emotional_context = EmotionalContext(
            valence=0.7,
            arousal=0.6,
            detected_emotion='satisfaction',
            confidence=0.8
        )
        
        memory = MemoryFragment(
            content="Test mémoire importante",
            memory_type=MemoryType.EPISODIC,
            emotional_context=emotional_context,
            importance_score=0.8,
            consolidation_level=ConsolidationLevel.VOLATILE,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            access_count=1
        )
        
        assert memory.content == "Test mémoire importante"
        assert memory.memory_type == MemoryType.EPISODIC
        assert memory.emotional_context.valence == 0.7
        assert memory.importance_score == 0.8
    
    def test_emotional_valence_enum(self):
        """Test énumération valence émotionnelle"""
        from backend.memory.brain_memory_system import EmotionalValence
        
        assert EmotionalValence.VERY_NEGATIVE.value == -1.0
        assert EmotionalValence.NEGATIVE.value == -0.5
        assert EmotionalValence.NEUTRAL.value == 0.0
        assert EmotionalValence.POSITIVE.value == 0.5
        assert EmotionalValence.VERY_POSITIVE.value == 1.0
    
    def test_memory_types_completeness(self):
        """Test complétude types de mémoire"""
        from backend.memory.brain_memory_system import MemoryType
        
        # Vérifier tous les types neuromorphiques
        assert MemoryType.WORKING.value == "working"
        assert MemoryType.EPISODIC.value == "episodic"
        assert MemoryType.SEMANTIC.value == "semantic"
        assert MemoryType.PROCEDURAL.value == "procedural"
    
    def test_consolidation_levels(self):
        """Test niveaux de consolidation"""
        from backend.memory.brain_memory_system import ConsolidationLevel
        
        assert ConsolidationLevel.VOLATILE.value == "volatile"
        assert ConsolidationLevel.CONSOLIDATING.value == "consolidating"
        assert ConsolidationLevel.CONSOLIDATED.value == "consolidated"
        assert ConsolidationLevel.ARCHIVED.value == "archived"

def run_integration_tests():
    """Exécute tous les tests d'intégration"""
    print("🐳 LANCEMENT TESTS D'INTÉGRATION DOCKER + SERVICES")
    print("=" * 70)
    
    test_args = [
        __file__,
        "-v",
        "--tb=short",
        "--color=yes",
        "-x"
    ]
    
    try:
        result = pytest.main(test_args)
        if result == 0:
            print("\n✅ TOUS LES TESTS D'INTÉGRATION PASSÉS !")
        else:
            print(f"\n❌ TESTS D'INTÉGRATION ÉCHOUÉS (Code: {result})")
        return result
    except Exception as e:
        print(f"\n💥 ERREUR TESTS D'INTÉGRATION: {e}")
        return -1

if __name__ == "__main__":
    exit_code = run_integration_tests()
    exit(exit_code)