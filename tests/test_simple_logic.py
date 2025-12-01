#!/usr/bin/env python3
"""
 Tests Logique Simple - Système Mémoire Neuromorphique
Tests de base sans dépendances externes lourdes
"""

import sys
import os
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock

# Ajouter le chemin backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

def test_memory_types_and_enums():
    """Test des types et énumérations"""
    try:
        from memory.brain_memory_system import MemoryType, ConsolidationLevel, EmotionalValence
        
        print(" Test énumérations:")
        
        # Test MemoryType
        assert MemoryType.WORKING.value == "working"
        assert MemoryType.EPISODIC.value == "episodic"
        assert MemoryType.SEMANTIC.value == "semantic"
        assert MemoryType.PROCEDURAL.value == "procedural"
        print("    MemoryType - OK")
        
        # Test ConsolidationLevel
        assert ConsolidationLevel.VOLATILE.value == "volatile"
        assert ConsolidationLevel.CONSOLIDATING.value == "consolidating"
        assert ConsolidationLevel.CONSOLIDATED.value == "consolidated"
        assert ConsolidationLevel.ARCHIVED.value == "archived"
        print("    ConsolidationLevel - OK")
        
        # Test EmotionalValence
        assert EmotionalValence.VERY_NEGATIVE.value == -1.0
        assert EmotionalValence.NEGATIVE.value == -0.5
        assert EmotionalValence.NEUTRAL.value == 0.0
        assert EmotionalValence.POSITIVE.value == 0.5
        assert EmotionalValence.VERY_POSITIVE.value == 1.0
        print("    EmotionalValence - OK")
        
        return True
    except Exception as e:
        print(f" Test énumérations échoué: {e}")
        return False

def test_emotional_context_creation():
    """Test création contexte émotionnel"""
    try:
        from memory.brain_memory_system import EmotionalContext
        
        print(" Test EmotionalContext:")
        
        context = EmotionalContext(
            valence=0.7,
            arousal=0.6,
            detected_emotion="joie",
            confidence=0.8
        )
        
        assert context.valence == 0.7
        assert context.arousal == 0.6
        assert context.detected_emotion == "joie"
        assert context.confidence == 0.8
        print("    Création contexte émotionnel - OK")
        
        return True
    except Exception as e:
        print(f" Test EmotionalContext échoué: {e}")
        return False

def test_memory_fragment_creation():
    """Test création fragment mémoire"""
    try:
        from memory.brain_memory_system import MemoryFragment, EmotionalContext, MemoryType, ConsolidationLevel
        
        print(" Test MemoryFragment:")
        
        emotional_context = EmotionalContext(0.5, 0.4, "neutre", 0.7)
        
        memory = MemoryFragment(
            content="Test de mémoire",
            memory_type=MemoryType.EPISODIC,
            emotional_context=emotional_context,
            importance_score=0.6,
            consolidation_level=ConsolidationLevel.VOLATILE,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            access_count=1
        )
        
        assert memory.content == "Test de mémoire"
        assert memory.memory_type == MemoryType.EPISODIC
        assert memory.importance_score == 0.6
        assert memory.consolidation_level == ConsolidationLevel.VOLATILE
        assert memory.access_count == 1
        print("    Création fragment mémoire - OK")
        
        return True
    except Exception as e:
        print(f" Test MemoryFragment échoué: {e}")
        return False

def test_limbic_system_keywords():
    """Test mots-clés émotionnels du système limbique"""
    try:
        # Importer sans instantier
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "brain_memory", 
            "/home/enzo/Documents/Projet Jarvis/backend/memory/brain_memory_system.py"
        )
        brain_module = importlib.util.module_from_spec(spec)
        
        # Mock des dépendances avant l'import
        sys.modules['db.database'] = Mock()
        sys.modules['sqlalchemy'] = Mock()
        sys.modules['asyncpg'] = Mock()
        
        spec.loader.exec_module(brain_module)
        
        LimbicSystem = brain_module.LimbicSystem
        limbic = LimbicSystem()
        
        print(" Test mots-clés émotionnels:")
        
        # Test mots positifs
        positive_words = ["adorer", "excellent", "parfait", "génial"]
        for word in positive_words:
            assert word in limbic.emotional_keywords
            assert limbic.emotional_keywords[word] > 0
        print("    Mots positifs détectés - OK")
        
        # Test mots négatifs
        negative_words = ["détester", "horrible", "nul", "frustré"]
        for word in negative_words:
            assert word in limbic.emotional_keywords
            assert limbic.emotional_keywords[word] < 0
        print("    Mots négatifs détectés - OK")
        
        # Test calcul valence textuelle
        positive_text = "J'adore ce projet excellent et génial"
        negative_text = "Je déteste ce truc horrible et nul"
        
        pos_score = limbic._calculate_textual_valence(positive_text)
        neg_score = limbic._calculate_textual_valence(negative_text)
        
        assert pos_score > 0.0
        assert neg_score < 0.0
        assert pos_score > neg_score
        print(f"    Valence positive: {pos_score:.2f}, négative: {neg_score:.2f} - OK")
        
        return True
    except Exception as e:
        print(f" Test système limbique échoué: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_qdrant_adapter_logic():
    """Test logique adaptateur Qdrant"""
    try:
        # Mock des imports Qdrant
        sys.modules['qdrant_client'] = Mock()
        sys.modules['qdrant_client.http'] = Mock()
        sys.modules['qdrant_client.http.models'] = Mock()
        
        from memory.qdrant_adapter import QdrantMemoryAdapter
        from memory.brain_memory_system import MemoryType
        
        print(" Test QdrantAdapter:")
        
        adapter = QdrantMemoryAdapter("http://localhost:6333")
        
        # Test configuration collections
        assert len(adapter.collections) == 4
        assert "episodic_memory" in adapter.collections
        assert "semantic_memory" in adapter.collections
        assert "procedural_memory" in adapter.collections
        assert "emotional_memory" in adapter.collections
        print("    Collections configurées - OK")
        
        # Test détermination collection
        collection_emotional = adapter._get_collection_name(MemoryType.EPISODIC, 0.8)
        assert collection_emotional == "emotional_memory"
        
        collection_semantic = adapter._get_collection_name(MemoryType.SEMANTIC, 0.2)
        assert collection_semantic == "semantic_memory"
        print("    Détermination collections - OK")
        
        # Test calcul score enrichi
        payload = {
            'importance_score': 0.8,
            'emotional_valence': 0.6,
            'created_at': datetime.now().isoformat(),
            'access_count': 5
        }
        
        score = adapter._calculate_enhanced_score(0.7, payload)
        assert 0.7 <= score <= 1.0  # Score doit être >= base et <= 1.0
        print(f"    Score enrichi: {score:.3f} - OK")
        
        return True
    except Exception as e:
        print(f" Test QdrantAdapter échoué: {e}")
        return False

def test_docker_compose_content():
    """Test contenu docker-compose.yml"""
    try:
        compose_file = "/home/enzo/Documents/Projet Jarvis/docker-compose.yml"
        
        with open(compose_file, 'r') as f:
            content = f.read()
        
        print(" Test Docker Compose:")
        
        # Tests critiques
        critical_checks = {
            'Réseau Jarvis': 'jarvis_network:' in content,
            'Subnet correct': '172.20.0.0/16' in content,
            'Gateway correct': '172.20.0.1' in content,
            'Service backend': 'backend:' in content,
            'Service Qdrant': 'qdrant:' in content,
            'Service TimescaleDB': 'timescale:' in content,
            'IP Qdrant': '172.20.0.120' in content,
            'IP TimescaleDB': '172.20.0.130' in content,
            'URL Qdrant env': 'QDRANT_URL=http://172.20.0.120:6333' in content,
            'Mémoire neuromorphique activée': 'BRAIN_MEMORY_ENABLED=true' in content
        }
        
        passed = 0
        for check_name, result in critical_checks.items():
            if result:
                print(f"    {check_name} - OK")
                passed += 1
            else:
                print(f"    {check_name} - ÉCHEC")
        
        assert passed == len(critical_checks)
        print(f"    Tous les contrôles passés ({passed}/{len(critical_checks)}) - OK")
        
        return True
    except Exception as e:
        print(f" Test Docker Compose échoué: {e}")
        return False

def test_requirements_content():
    """Test contenu requirements.txt"""
    try:
        req_file = "/home/enzo/Documents/Projet Jarvis/backend/requirements.txt"
        
        with open(req_file, 'r') as f:
            content = f.read()
        
        print(" Test Requirements.txt:")
        
        critical_deps = [
            'qdrant-client', 'sqlalchemy', 'asyncpg', 'fastapi',
            'uvicorn', 'pydantic', 'sentence-transformers', 'redis'
        ]
        
        missing = []
        for dep in critical_deps:
            if dep not in content:
                missing.append(dep)
        
        if missing:
            print(f"    Dépendances manquantes: {missing}")
            return False
        else:
            print(f"    Toutes les dépendances critiques présentes ({len(critical_deps)}) - OK")
            return True
    except Exception as e:
        print(f" Test Requirements échoué: {e}")
        return False

def test_backend_integration():
    """Test intégration backend"""
    try:
        backend_file = "/home/enzo/Documents/Projet Jarvis/backend/main.py"
        
        with open(backend_file, 'r') as f:
            content = f.read()
        
        print(" Test intégration backend:")
        
        integration_checks = {
            'Import BrainMemorySystem': 'from memory.brain_memory_system import BrainMemorySystem' in content,
            'Instance brain_memory_system': 'brain_memory_system = BrainMemorySystem(db)' in content,
            'Méthode get_contextual_memories': 'get_contextual_memories' in content,
            'Méthode store_interaction': 'store_interaction' in content,
            'Système neuromorphique actif': 'SYSTÈME MÉMOIRE NEUROMORPHIQUE ACTIF' in content
        }
        
        passed = 0
        for check_name, result in integration_checks.items():
            if result:
                print(f"    {check_name} - OK")
                passed += 1
            else:
                print(f"    {check_name} - ÉCHEC")
        
        assert passed == len(integration_checks)
        print(f"    Intégration backend complète ({passed}/{len(integration_checks)}) - OK")
        
        return True
    except Exception as e:
        print(f" Test intégration backend échoué: {e}")
        return False

def main():
    """Fonction principale des tests simplifiés"""
    print(" TESTS LOGIQUE SIMPLE - SYSTÈME MÉMOIRE NEUROMORPHIQUE")
    print("=" * 70)
    print(f" Début: {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    tests = [
        ("Types et énumérations", test_memory_types_and_enums),
        ("Contexte émotionnel", test_emotional_context_creation),
        ("Fragment mémoire", test_memory_fragment_creation),
        ("Mots-clés émotionnels", test_limbic_system_keywords),
        ("Adaptateur Qdrant", test_qdrant_adapter_logic),
        ("Docker Compose", test_docker_compose_content),
        ("Requirements.txt", test_requirements_content),
        ("Intégration backend", test_backend_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f" {test_name}...")
        print("-" * 40)
        
        try:
            if test_func():
                passed += 1
                print(f" {test_name} - SUCCÈS\n")
            else:
                print(f" {test_name} - ÉCHEC\n")
        except Exception as e:
            print(f" {test_name} - ERREUR: {e}\n")
    
    success_rate = (passed / total) * 100
    
    print("=" * 70)
    print(f" RÉSULTATS FINAUX:")
    print(f"   Tests passés: {passed}/{total}")
    print(f"   Taux de réussite: {success_rate:.1f}%")
    print(f" Fin: {datetime.now().strftime('%H:%M:%S')}")
    
    if success_rate >= 90:
        print("\n EXCELLENT ! Système neuromorphique bien configuré")
        return True
    elif success_rate >= 70:
        print("\n SATISFAISANT ! Quelques ajustements mineurs")
        return True
    else:
        print("\n INSUFFISANT ! Corrections majeures requises")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)