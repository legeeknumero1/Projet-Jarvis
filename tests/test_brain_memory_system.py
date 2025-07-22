#!/usr/bin/env python3
"""
🧠 Tests Unitaires Complets - Système de Mémoire Neuromorphique Jarvis
Tests exhaustifs pour tous les composants du système mémoire inspiré du cerveau humain
"""

import pytest
import asyncio
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
import json

# Ajouter le chemin backend pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Imports des composants à tester
from memory.brain_memory_system import (
    BrainMemorySystem, LimbicSystem, PrefrontalCortex, Hippocampus,
    MemoryFragment, EmotionalContext, MemoryType, ConsolidationLevel,
    EmotionalValence
)
from memory.qdrant_adapter import QdrantMemoryAdapter

class TestLimbicSystem:
    """Tests complets du système limbique - Analyse émotionnelle"""
    
    @pytest.fixture
    def limbic_system(self):
        return LimbicSystem()
    
    @pytest.mark.asyncio
    async def test_emotional_analysis_positive(self, limbic_system):
        """Test analyse émotionnelle - Texte positif"""
        text = "Je suis super content de ce projet génial ! C'est parfait et excellent !"
        
        result = await limbic_system.analyze_emotional_context(text)
        
        assert isinstance(result, EmotionalContext)
        assert result.valence > 0.5  # Doit être positif
        assert result.arousal > 0.3   # Doit avoir de l'intensité
        assert result.detected_emotion in ['joie', 'satisfaction', 'enthousiasme']
        assert 0.0 <= result.confidence <= 1.0
    
    @pytest.mark.asyncio
    async def test_emotional_analysis_negative(self, limbic_system):
        """Test analyse émotionnelle - Texte négatif"""
        text = "Je déteste ce problème horrible ! C'est nul et frustrant, je suis énervé."
        
        result = await limbic_system.analyze_emotional_context(text)
        
        assert result.valence < -0.3  # Doit être négatif
        assert result.arousal > 0.4   # Forte intensité émotionnelle
        assert result.detected_emotion in ['colère', 'frustration', 'déception']
        assert result.confidence > 0.5
    
    @pytest.mark.asyncio
    async def test_emotional_analysis_neutral(self, limbic_system):
        """Test analyse émotionnelle - Texte neutre"""
        text = "Voici une information factuelle sur le système."
        
        result = await limbic_system.analyze_emotional_context(text)
        
        assert -0.3 <= result.valence <= 0.3  # Neutre
        assert result.arousal < 0.5           # Faible intensité
        assert result.detected_emotion == 'neutre'
    
    @pytest.mark.asyncio
    async def test_emotional_weighting_calculation(self, limbic_system):
        """Test calcul pondération émotionnelle"""
        # Émotion forte positive
        strong_positive = EmotionalContext(
            valence=0.8, arousal=0.9, detected_emotion='joie', confidence=0.9
        )
        weight1 = limbic_system._calculate_emotional_weight(strong_positive)
        
        # Émotion faible neutre
        weak_neutral = EmotionalContext(
            valence=0.1, arousal=0.2, detected_emotion='neutre', confidence=0.6
        )
        weight2 = limbic_system._calculate_emotional_weight(weak_neutral)
        
        assert weight1 > weight2  # Émotion forte doit avoir plus de poids
        assert 0.0 <= weight1 <= 1.0
        assert 0.0 <= weight2 <= 1.0
    
    def test_keyword_detection(self, limbic_system):
        """Test détection mots-clés émotionnels"""
        # Test mots positifs
        positive_text = "J'adore ce projet magnifique et excellent"
        positive_score = limbic_system._calculate_textual_valence(positive_text)
        
        # Test mots négatifs
        negative_text = "Je déteste ce problème horrible et nul"
        negative_score = limbic_system._calculate_textual_valence(negative_text)
        
        assert positive_score > 0.3
        assert negative_score < -0.3
        assert positive_score > negative_score

class TestPrefrontalCortex:
    """Tests complets du cortex préfrontal - Raisonnement et décision"""
    
    @pytest.fixture
    def prefrontal_cortex(self):
        mock_db = Mock()
        return PrefrontalCortex(mock_db)
    
    @pytest.mark.asyncio
    async def test_importance_scoring(self, prefrontal_cortex):
        """Test calcul score d'importance"""
        # Mémoire très importante
        important_memory = MemoryFragment(
            content="Rendez-vous médical urgent demain à 14h",
            memory_type=MemoryType.EPISODIC,
            emotional_context=EmotionalContext(0.2, 0.8, 'urgence', 0.9),
            importance_score=0.0,  # À calculer
            consolidation_level=ConsolidationLevel.VOLATILE,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            access_count=0
        )
        
        score = await prefrontal_cortex.calculate_importance_score(important_memory)
        
        assert score > 0.7  # Doit être très important
        assert 0.0 <= score <= 1.0
    
    @pytest.mark.asyncio
    async def test_importance_scoring_routine(self, prefrontal_cortex):
        """Test score importance - Information routinière"""
        routine_memory = MemoryFragment(
            content="Il fait beau aujourd'hui",
            memory_type=MemoryType.EPISODIC,
            emotional_context=EmotionalContext(0.1, 0.2, 'neutre', 0.6),
            importance_score=0.0,
            consolidation_level=ConsolidationLevel.VOLATILE,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            access_count=0
        )
        
        score = await prefrontal_cortex.calculate_importance_score(routine_memory)
        
        assert score < 0.4  # Doit être peu important
    
    @pytest.mark.asyncio
    async def test_memory_retrieval_strategy(self, prefrontal_cortex):
        """Test stratégie récupération mémoire"""
        query = "Qu'est-ce qui s'est passé hier ?"
        
        # Mock des mémoires disponibles
        mock_memories = [
            {'content': 'Réunion importante hier', 'importance_score': 0.8, 'created_at': '2024-01-19'},
            {'content': 'Déjeuner hier', 'importance_score': 0.3, 'created_at': '2024-01-19'},
            {'content': 'Événement la semaine dernière', 'importance_score': 0.9, 'created_at': '2024-01-15'}
        ]
        
        strategy = await prefrontal_cortex.determine_retrieval_strategy(query, mock_memories)
        
        assert 'temporal' in strategy or 'importance' in strategy
        assert isinstance(strategy, dict)
        assert 'filters' in strategy
    
    @pytest.mark.asyncio
    async def test_consolidation_decision(self, prefrontal_cortex):
        """Test décision consolidation"""
        # Mémoire candidate à la consolidation
        memory = MemoryFragment(
            content="Information importante répétée plusieurs fois",
            memory_type=MemoryType.EPISODIC,
            emotional_context=EmotionalContext(0.6, 0.7, 'satisfaction', 0.8),
            importance_score=0.8,
            consolidation_level=ConsolidationLevel.VOLATILE,
            created_at=datetime.now() - timedelta(hours=2),
            last_accessed=datetime.now(),
            access_count=5
        )
        
        should_consolidate = await prefrontal_cortex.should_consolidate_memory(memory)
        
        assert isinstance(should_consolidate, bool)
        # Avec ces critères, devrait être consolidée
        assert should_consolidate == True

class TestHippocampus:
    """Tests complets de l'hippocampe - Consolidation mémoire"""
    
    @pytest.fixture
    def hippocampus(self):
        mock_db = Mock()
        return Hippocampus(mock_db)
    
    @pytest.mark.asyncio
    async def test_memory_consolidation_process(self, hippocampus):
        """Test processus complet de consolidation"""
        volatile_memories = [
            MemoryFragment(
                content="Information importante à retenir",
                memory_type=MemoryType.EPISODIC,
                emotional_context=EmotionalContext(0.7, 0.6, 'satisfaction', 0.8),
                importance_score=0.8,
                consolidation_level=ConsolidationLevel.VOLATILE,
                created_at=datetime.now() - timedelta(hours=1),
                last_accessed=datetime.now(),
                access_count=3
            ),
            MemoryFragment(
                content="Détail sans importance",
                memory_type=MemoryType.EPISODIC,
                emotional_context=EmotionalContext(0.0, 0.1, 'neutre', 0.5),
                importance_score=0.2,
                consolidation_level=ConsolidationLevel.VOLATILE,
                created_at=datetime.now() - timedelta(minutes=30),
                last_accessed=datetime.now(),
                access_count=1
            )
        ]
        
        # Mock de la database
        hippocampus.db.get_volatile_memories = AsyncMock(return_value=volatile_memories)
        hippocampus.db.update_memory_consolidation = AsyncMock(return_value=True)
        
        results = await hippocampus.consolidate_memories("test_user")
        
        assert isinstance(results, dict)
        assert 'consolidated_count' in results
        assert 'total_processed' in results
        assert results['total_processed'] == 2
        # Au moins la mémoire importante devrait être consolidée
        assert results['consolidated_count'] >= 1
    
    @pytest.mark.asyncio
    async def test_forgetting_process(self, hippocampus):
        """Test processus d'oubli"""
        old_memories = [
            MemoryFragment(
                content="Vieille information peu importante",
                memory_type=MemoryType.EPISODIC,
                emotional_context=EmotionalContext(0.0, 0.1, 'neutre', 0.5),
                importance_score=0.1,
                consolidation_level=ConsolidationLevel.VOLATILE,
                created_at=datetime.now() - timedelta(days=7),
                last_accessed=datetime.now() - timedelta(days=5),
                access_count=1
            )
        ]
        
        hippocampus.db.get_old_low_importance_memories = AsyncMock(return_value=old_memories)
        hippocampus.db.delete_memory = AsyncMock(return_value=True)
        
        forgotten_count = await hippocampus.forget_irrelevant_memories("test_user")
        
        assert isinstance(forgotten_count, int)
        assert forgotten_count >= 0
    
    @pytest.mark.asyncio
    async def test_pattern_detection(self, hippocampus):
        """Test détection de patterns comportementaux"""
        user_memories = [
            {'content': 'Café le matin', 'created_at': '2024-01-19 08:00:00'},
            {'content': 'Café le matin', 'created_at': '2024-01-18 08:15:00'},
            {'content': 'Café le matin', 'created_at': '2024-01-17 07:45:00'},
        ]
        
        hippocampus.db.get_user_memories_pattern = AsyncMock(return_value=user_memories)
        
        patterns = await hippocampus.detect_behavioral_patterns("test_user")
        
        assert isinstance(patterns, list)
        if patterns:  # Si des patterns détectés
            pattern = patterns[0]
            assert 'pattern_type' in pattern
            assert 'frequency' in pattern
            assert 'confidence' in pattern

class TestQdrantAdapter:
    """Tests complets de l'adaptateur Qdrant"""
    
    @pytest.fixture
    def qdrant_adapter(self):
        return QdrantMemoryAdapter("http://localhost:6333")
    
    def test_collection_name_determination(self, qdrant_adapter):
        """Test détermination nom collection"""
        # Test mémoire émotionnelle forte
        collection_emotional = qdrant_adapter._get_collection_name(
            MemoryType.EPISODIC, emotional_weight=0.8
        )
        assert collection_emotional == "emotional_memory"
        
        # Test mémoire sémantique normale
        collection_semantic = qdrant_adapter._get_collection_name(
            MemoryType.SEMANTIC, emotional_weight=0.2
        )
        assert collection_semantic == "semantic_memory"
        
        # Test mémoire procédurale
        collection_procedural = qdrant_adapter._get_collection_name(
            MemoryType.PROCEDURAL, emotional_weight=0.1
        )
        assert collection_procedural == "procedural_memory"
    
    def test_enhanced_score_calculation(self, qdrant_adapter):
        """Test calcul score enrichi"""
        base_score = 0.7
        payload = {
            'importance_score': 0.8,
            'emotional_valence': 0.6,
            'created_at': datetime.now().isoformat(),
            'access_count': 5
        }
        
        enhanced_score = qdrant_adapter._calculate_enhanced_score(
            base_score, payload, "test query"
        )
        
        assert enhanced_score >= base_score  # Score doit être amélioré
        assert enhanced_score <= 1.0  # Limité à 1.0
        assert isinstance(enhanced_score, float)
    
    def test_score_recency_boost(self, qdrant_adapter):
        """Test boost de récence"""
        # Mémoire récente
        recent_payload = {
            'importance_score': 0.5,
            'emotional_valence': 0.0,
            'created_at': datetime.now().isoformat(),
            'access_count': 1
        }
        
        # Mémoire ancienne
        old_payload = {
            'importance_score': 0.5,
            'emotional_valence': 0.0,
            'created_at': (datetime.now() - timedelta(days=30)).isoformat(),
            'access_count': 1
        }
        
        recent_score = qdrant_adapter._calculate_enhanced_score(0.7, recent_payload)
        old_score = qdrant_adapter._calculate_enhanced_score(0.7, old_payload)
        
        assert recent_score > old_score  # Récent doit avoir meilleur score

class TestBrainMemorySystemIntegration:
    """Tests d'intégration complets du système mémoire neuromorphique"""
    
    @pytest.fixture
    def brain_memory_system(self):
        mock_db = Mock()
        return BrainMemorySystem(mock_db)
    
    @pytest.mark.asyncio
    async def test_complete_memory_storage_workflow(self, brain_memory_system):
        """Test workflow complet stockage mémoire"""
        user_id = "test_user"
        interaction_text = "J'ai adoré cette réunion productive ! Très satisfait du résultat."
        response_text = "Ravi que la réunion se soit bien passée !"
        
        # Mock des composants internes
        brain_memory_system.limbic_system.analyze_emotional_context = AsyncMock(
            return_value=EmotionalContext(0.7, 0.6, 'satisfaction', 0.8)
        )
        brain_memory_system.prefrontal_cortex.calculate_importance_score = AsyncMock(
            return_value=0.7
        )
        brain_memory_system.db.save_memory_fragment = AsyncMock(return_value=True)
        
        result = await brain_memory_system.store_interaction(
            user_id, interaction_text, response_text
        )
        
        assert isinstance(result, bool)
        assert result == True
        
        # Vérifier que les composants ont été appelés
        brain_memory_system.limbic_system.analyze_emotional_context.assert_called()
        brain_memory_system.prefrontal_cortex.calculate_importance_score.assert_called()
    
    @pytest.mark.asyncio
    async def test_contextual_memory_retrieval(self, brain_memory_system):
        """Test récupération mémoires contextuelles"""
        user_id = "test_user"
        query = "Qu'est-ce qui s'est passé lors de la dernière réunion ?"
        
        # Mock des mémoires contextuelles
        mock_memories = [
            {
                'content': 'Réunion très productive avec décisions importantes',
                'importance_score': 0.8,
                'emotional_context': {
                    'valence': 0.7,
                    'arousal': 0.6,
                    'detected_emotion': 'satisfaction',
                    'confidence': 0.8
                },
                'created_at': datetime.now().isoformat(),
                'memory_type': 'episodic'
            }
        ]
        
        # Mock de la recherche hybride
        brain_memory_system.db.search_memories_hybrid = AsyncMock(
            return_value=mock_memories
        )
        brain_memory_system.qdrant_adapter = Mock()
        brain_memory_system.qdrant_adapter.search_memories = AsyncMock(
            return_value=mock_memories
        )
        
        results = await brain_memory_system.get_contextual_memories(user_id, query)
        
        assert isinstance(results, list)
        assert len(results) > 0
        assert all('content' in memory for memory in results)
    
    @pytest.mark.asyncio
    async def test_periodic_consolidation(self, brain_memory_system):
        """Test consolidation périodique"""
        user_id = "test_user"
        
        # Mock du processus de consolidation
        brain_memory_system.hippocampus.consolidate_memories = AsyncMock(
            return_value={'consolidated_count': 3, 'total_processed': 10}
        )
        brain_memory_system.hippocampus.forget_irrelevant_memories = AsyncMock(
            return_value=2
        )
        
        result = await brain_memory_system.perform_periodic_consolidation(user_id)
        
        assert isinstance(result, dict)
        assert 'consolidation_results' in result
        assert 'forgotten_count' in result
        assert result['consolidation_results']['consolidated_count'] == 3
        assert result['forgotten_count'] == 2
    
    @pytest.mark.asyncio
    async def test_initialization_process(self, brain_memory_system):
        """Test processus d'initialisation complet"""
        # Mock de l'initialisation des composants
        brain_memory_system.db.connect = AsyncMock(return_value=True)
        brain_memory_system.qdrant_adapter = Mock()
        brain_memory_system.qdrant_adapter.initialize = AsyncMock(return_value=True)
        
        # Test avec Qdrant activé
        brain_memory_system.config = {"use_qdrant": True}
        
        result = await brain_memory_system.initialize()
        
        assert isinstance(result, bool)
        assert result == True
        
        # Vérifier initialisation des composants
        brain_memory_system.db.connect.assert_called_once()
        brain_memory_system.qdrant_adapter.initialize.assert_called_once()

def run_all_tests():
    """Exécute tous les tests unitaires"""
    print("🧠 LANCEMENT TESTS UNITAIRES SYSTÈME MÉMOIRE NEUROMORPHIQUE")
    print("=" * 70)
    
    # Configuration pytest
    test_args = [
        __file__,
        "-v",           # Mode verbose
        "--tb=short",   # Traceback court
        "--color=yes",  # Couleurs
        "-x"            # Stop au premier échec
    ]
    
    try:
        result = pytest.main(test_args)
        if result == 0:
            print("\n✅ TOUS LES TESTS UNITAIRES PASSÉS AVEC SUCCÈS !")
        else:
            print(f"\n❌ TESTS ÉCHOUÉS (Code: {result})")
        return result
    except Exception as e:
        print(f"\n💥 ERREUR LORS DE L'EXÉCUTION DES TESTS: {e}")
        return -1

if __name__ == "__main__":
    # Exécution directe pour tests rapides
    exit_code = run_all_tests()
    exit(exit_code)