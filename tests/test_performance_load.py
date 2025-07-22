#!/usr/bin/env python3
"""
⚡ Tests de Performance et Charge - Système Mémoire Neuromorphique Jarvis
Tests exhaustifs de performance, charge et robustesse
"""

import asyncio
import time
import sys
import os
import json
import statistics
import concurrent.futures
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock
import psutil
import tracemalloc

# Ajouter le chemin backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from memory.brain_memory_system import (
    BrainMemorySystem, LimbicSystem, PrefrontalCortex, Hippocampus,
    MemoryFragment, EmotionalContext, MemoryType, ConsolidationLevel
)

class PerformanceMonitor:
    """Moniteur de performance pour les tests"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.start_time = None
        self.end_time = None
        self.memory_usage = []
        self.cpu_usage = []
        tracemalloc.start()
    
    def start_monitoring(self):
        self.start_time = time.time()
        self.memory_usage.append(psutil.Process().memory_info().rss / 1024 / 1024)  # MB
        self.cpu_usage.append(psutil.cpu_percent())
    
    def stop_monitoring(self):
        self.end_time = time.time()
        self.memory_usage.append(psutil.Process().memory_info().rss / 1024 / 1024)
        self.cpu_usage.append(psutil.cpu_percent())
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        return {
            'duration': self.end_time - self.start_time,
            'memory_start_mb': self.memory_usage[0],
            'memory_end_mb': self.memory_usage[-1],
            'memory_peak_mb': peak / 1024 / 1024,
            'cpu_avg': statistics.mean(self.cpu_usage) if self.cpu_usage else 0
        }

class TestLimbicSystemPerformance:
    """Tests de performance du système limbique"""
    
    def setup_method(self):
        self.limbic = LimbicSystem()
        self.monitor = PerformanceMonitor()
    
    async def test_emotional_analysis_speed(self):
        """Test vitesse analyse émotionnelle"""
        test_texts = [
            "Je suis super content de ce projet génial !",
            "C'est horrible, je déteste ça !",
            "Information neutre sans émotion particulière.",
            "Urgent ! Rendez-vous médical important demain.",
            "Magnifique journée ensoleillée, parfait pour sortir."
        ] * 100  # 500 analyses
        
        self.monitor.start_monitoring()
        
        results = []
        for text in test_texts:
            result = await self.limbic.analyze_emotional_context(text)
            results.append(result)
        
        perf_stats = self.monitor.stop_monitoring()
        
        # Vérifications performance
        assert perf_stats['duration'] < 10.0  # Moins de 10 secondes pour 500 analyses
        assert len(results) == 500
        assert all(isinstance(r, EmotionalContext) for r in results)
        
        print(f"🧠 Analyse émotionnelle - 500 textes en {perf_stats['duration']:.2f}s")
        print(f"   Vitesse: {len(test_texts)/perf_stats['duration']:.1f} analyses/seconde")
        print(f"   Mémoire pic: {perf_stats['memory_peak_mb']:.1f} MB")
    
    async def test_emotional_weight_calculation_batch(self):
        """Test calcul pondération émotionnelle en lot"""
        emotions = [
            EmotionalContext(0.8, 0.9, 'joie', 0.9),
            EmotionalContext(-0.7, 0.8, 'colère', 0.8),
            EmotionalContext(0.1, 0.2, 'neutre', 0.6),
            EmotionalContext(0.6, 0.7, 'satisfaction', 0.8),
            EmotionalContext(-0.5, 0.6, 'tristesse', 0.7)
        ] * 200  # 1000 calculs
        
        self.monitor.start_monitoring()
        
        weights = []
        for emotion in emotions:
            weight = self.limbic._calculate_emotional_weight(emotion)
            weights.append(weight)
        
        perf_stats = self.monitor.stop_monitoring()
        
        assert perf_stats['duration'] < 1.0  # Moins d'1 seconde
        assert len(weights) == 1000
        assert all(0.0 <= w <= 1.0 for w in weights)
        
        print(f"🎯 Pondération émotionnelle - 1000 calculs en {perf_stats['duration']:.3f}s")

class TestPrefrontalCortexPerformance:
    """Tests de performance du cortex préfrontal"""
    
    def setup_method(self):
        self.prefrontal = PrefrontalCortex(Mock())
        self.monitor = PerformanceMonitor()
    
    async def test_importance_scoring_speed(self):
        """Test vitesse calcul importance"""
        memories = []
        for i in range(100):
            memory = MemoryFragment(
                content=f"Mémoire test numéro {i}",
                memory_type=MemoryType.EPISODIC,
                emotional_context=EmotionalContext(0.5, 0.5, 'neutre', 0.7),
                importance_score=0.0,
                consolidation_level=ConsolidationLevel.VOLATILE,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                access_count=1
            )
            memories.append(memory)
        
        self.monitor.start_monitoring()
        
        scores = []
        for memory in memories:
            score = await self.prefrontal.calculate_importance_score(memory)
            scores.append(score)
        
        perf_stats = self.monitor.stop_monitoring()
        
        assert perf_stats['duration'] < 5.0  # Moins de 5 secondes
        assert len(scores) == 100
        assert all(0.0 <= s <= 1.0 for s in scores)
        
        print(f"🧮 Scoring importance - 100 mémoires en {perf_stats['duration']:.2f}s")

class TestHippocampusPerformance:
    """Tests de performance de l'hippocampe"""
    
    def setup_method(self):
        mock_db = Mock()
        self.hippocampus = Hippocampus(mock_db)
        self.monitor = PerformanceMonitor()
    
    async def test_consolidation_batch_performance(self):
        """Test performance consolidation en lot"""
        # Simuler 1000 mémoires volatiles
        volatile_memories = []
        for i in range(1000):
            memory = MemoryFragment(
                content=f"Mémoire volatile {i}",
                memory_type=MemoryType.EPISODIC,
                emotional_context=EmotionalContext(0.3, 0.4, 'neutre', 0.6),
                importance_score=0.3 + (i % 7) * 0.1,  # Scores variés
                consolidation_level=ConsolidationLevel.VOLATILE,
                created_at=datetime.now() - timedelta(hours=i % 24),
                last_accessed=datetime.now(),
                access_count=i % 10
            )
            volatile_memories.append(memory)
        
        # Mock de la base de données
        self.hippocampus.db.get_volatile_memories = AsyncMock(return_value=volatile_memories)
        self.hippocampus.db.update_memory_consolidation = AsyncMock(return_value=True)
        
        self.monitor.start_monitoring()
        
        result = await self.hippocampus.consolidate_memories("test_user")
        
        perf_stats = self.monitor.stop_monitoring()
        
        assert perf_stats['duration'] < 30.0  # Moins de 30 secondes
        assert result['total_processed'] == 1000
        
        print(f"🏛️ Consolidation - 1000 mémoires en {perf_stats['duration']:.2f}s")
        print(f"   Consolidées: {result['consolidated_count']}")

class TestBrainMemorySystemLoad:
    """Tests de charge système mémoire complet"""
    
    def setup_method(self):
        self.brain_system = BrainMemorySystem(Mock())
        self.monitor = PerformanceMonitor()
    
    async def test_concurrent_interactions(self):
        """Test interactions simultanées"""
        async def simulate_interaction(user_id, interaction_num):
            return await self.brain_system.store_interaction(
                f"user_{user_id}",
                f"Message {interaction_num} de l'utilisateur {user_id}",
                f"Réponse {interaction_num} pour l'utilisateur {user_id}"
            )
        
        # Mock des composants
        self.brain_system.limbic_system.analyze_emotional_context = AsyncMock(
            return_value=EmotionalContext(0.5, 0.5, 'neutre', 0.7)
        )
        self.brain_system.prefrontal_cortex.calculate_importance_score = AsyncMock(
            return_value=0.6
        )
        self.brain_system.db.save_memory_fragment = AsyncMock(return_value=True)
        
        self.monitor.start_monitoring()
        
        # Simuler 50 utilisateurs avec 10 interactions chacun
        tasks = []
        for user_id in range(50):
            for interaction_num in range(10):
                task = simulate_interaction(user_id, interaction_num)
                tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        perf_stats = self.monitor.stop_monitoring()
        
        assert len(results) == 500
        assert all(result for result in results)
        assert perf_stats['duration'] < 60.0  # Moins d'1 minute
        
        print(f"🚀 Charge système - 500 interactions en {perf_stats['duration']:.2f}s")
        print(f"   Débit: {len(results)/perf_stats['duration']:.1f} interactions/seconde")
    
    async def test_memory_search_performance(self):
        """Test performance recherche mémoire"""
        # Mock de mémoires contextuelles
        mock_memories = [
            {
                'content': f'Mémoire contextuelle numéro {i}',
                'importance_score': 0.5 + (i % 5) * 0.1,
                'emotional_context': {
                    'valence': 0.3, 'arousal': 0.4,
                    'detected_emotion': 'neutre', 'confidence': 0.7
                },
                'created_at': datetime.now().isoformat(),
                'memory_type': 'episodic'
            }
            for i in range(1000)
        ]
        
        self.brain_system.db.search_memories_hybrid = AsyncMock(
            return_value=mock_memories[:10]  # Retourner top 10
        )
        
        queries = [
            "Qu'est-ce qui s'est passé hier ?",
            "Rappelle-moi mes rendez-vous",
            "Informations importantes récentes",
            "Conversations sur le projet"
        ] * 25  # 100 requêtes
        
        self.monitor.start_monitoring()
        
        results = []
        for query in queries:
            result = await self.brain_system.get_contextual_memories("test_user", query)
            results.append(result)
        
        perf_stats = self.monitor.stop_monitoring()
        
        assert len(results) == 100
        assert perf_stats['duration'] < 20.0  # Moins de 20 secondes
        
        print(f"🔍 Recherche mémoire - 100 requêtes en {perf_stats['duration']:.2f}s")
        print(f"   Vitesse: {len(queries)/perf_stats['duration']:.1f} recherches/seconde")

class TestMemoryLeaksAndStability:
    """Tests de fuites mémoire et stabilité"""
    
    def setup_method(self):
        self.brain_system = BrainMemorySystem(Mock())
        self.monitor = PerformanceMonitor()
    
    async def test_memory_leak_detection(self):
        """Test détection fuites mémoire"""
        # Mock simple
        self.brain_system.limbic_system.analyze_emotional_context = AsyncMock(
            return_value=EmotionalContext(0.5, 0.5, 'neutre', 0.7)
        )
        self.brain_system.prefrontal_cortex.calculate_importance_score = AsyncMock(
            return_value=0.6
        )
        self.brain_system.db.save_memory_fragment = AsyncMock(return_value=True)
        
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        # Exécuter de nombreuses opérations
        for batch in range(10):  # 10 lots de 100 opérations
            tasks = []
            for i in range(100):
                task = self.brain_system.store_interaction(
                    "test_user",
                    f"Message {batch}-{i}",
                    f"Réponse {batch}-{i}"
                )
                tasks.append(task)
            
            await asyncio.gather(*tasks)
            
            # Forcer garbage collection
            import gc
            gc.collect()
        
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_growth = final_memory - initial_memory
        
        print(f"💾 Test fuite mémoire:")
        print(f"   Mémoire initiale: {initial_memory:.1f} MB")
        print(f"   Mémoire finale: {final_memory:.1f} MB")
        print(f"   Croissance: {memory_growth:.1f} MB")
        
        # Vérifier que la croissance reste raisonnable
        assert memory_growth < 50.0  # Moins de 50 MB de croissance
    
    async def test_error_handling_resilience(self):
        """Test résilience gestion d'erreurs"""
        # Simuler erreurs dans différents composants
        error_scenarios = [
            "db_error", "qdrant_error", "limbic_error", "prefrontal_error"
        ]
        
        successful_operations = 0
        failed_operations = 0
        
        for scenario in error_scenarios * 25:  # 100 tests d'erreurs
            try:
                if scenario == "db_error":
                    self.brain_system.db.save_memory_fragment = AsyncMock(
                        side_effect=Exception("DB Error")
                    )
                elif scenario == "limbic_error":
                    self.brain_system.limbic_system.analyze_emotional_context = AsyncMock(
                        side_effect=Exception("Limbic Error")
                    )
                
                result = await self.brain_system.store_interaction(
                    "test_user", "Test message", "Test response"
                )
                
                if result:
                    successful_operations += 1
                else:
                    failed_operations += 1
                    
            except Exception:
                failed_operations += 1
        
        print(f"🛡️ Résilience erreurs:")
        print(f"   Opérations réussies: {successful_operations}")
        print(f"   Opérations échouées: {failed_operations}")
        
        # Le système doit survivre aux erreurs
        assert successful_operations + failed_operations == 100

async def run_performance_tests():
    """Exécute tous les tests de performance"""
    print("⚡ LANCEMENT TESTS DE PERFORMANCE ET CHARGE")
    print("=" * 70)
    
    test_classes = [
        TestLimbicSystemPerformance(),
        TestPrefrontalCortexPerformance(),
        TestHippocampusPerformance(),
        TestBrainMemorySystemLoad(),
        TestMemoryLeaksAndStability()
    ]
    
    total_start = time.time()
    
    for test_class in test_classes:
        class_name = test_class.__class__.__name__
        print(f"\n🔥 {class_name}")
        print("-" * 50)
        
        # Exécuter tous les tests de la classe
        for method_name in dir(test_class):
            if method_name.startswith('test_'):
                print(f"   Exécution {method_name}...")
                test_method = getattr(test_class, method_name)
                
                try:
                    if hasattr(test_class, 'setup_method'):
                        test_class.setup_method()
                    
                    await test_method()
                    print(f"   ✅ {method_name} - SUCCÈS")
                    
                except Exception as e:
                    print(f"   ❌ {method_name} - ÉCHEC: {e}")
                    import traceback
                    traceback.print_exc()
    
    total_duration = time.time() - total_start
    print(f"\n🎯 TESTS DE PERFORMANCE TERMINÉS en {total_duration:.2f}s")

if __name__ == "__main__":
    asyncio.run(run_performance_tests())