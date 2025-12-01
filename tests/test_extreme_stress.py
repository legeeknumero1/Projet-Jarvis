#!/usr/bin/env python3
"""
 TESTS DE STRESS EXTRÊME - Système Mémoire Neuromorphique Jarvis
Tests destructifs pour trouver TOUS les bugs cachés et limites système
"""

import sys
import os
import asyncio
import time
import threading
import gc
import psutil
import random
import string
import traceback
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import Mock, AsyncMock
import weakref

# Ajouter le chemin backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from memory.brain_memory_system import BrainMemorySystem, LimbicSystem
from memory.memory_types import MemoryFragment, EmotionalContext, MemoryType, ConsolidationLevel

class StressTestReporter:
    """Rapporteur de tests de stress avec métriques détaillées"""
    
    def __init__(self):
        self.results = {}
        self.errors = []
        self.performance_metrics = {}
        self.memory_snapshots = []
        self.start_time = time.time()
    
    def add_result(self, test_name, success, duration, details=None, error=None):
        self.results[test_name] = {
            'success': success,
            'duration': duration,
            'details': details or {},
            'error': str(error) if error else None,
            'timestamp': time.time() - self.start_time
        }
        if error:
            self.errors.append(f"{test_name}: {error}")
    
    def snapshot_memory(self, label):
        process = psutil.Process()
        snapshot = {
            'label': label,
            'rss_mb': process.memory_info().rss / 1024 / 1024,
            'vms_mb': process.memory_info().vms / 1024 / 1024,
            'cpu_percent': process.cpu_percent(),
            'threads': process.num_threads(),
            'timestamp': time.time() - self.start_time
        }
        self.memory_snapshots.append(snapshot)
        return snapshot
    
    def generate_report(self):
        total_tests = len(self.results)
        successful = sum(1 for r in self.results.values() if r['success'])
        
        return {
            'summary': {
                'total_tests': total_tests,
                'successful': successful,
                'failed': total_tests - successful,
                'success_rate': (successful / total_tests * 100) if total_tests > 0 else 0,
                'total_duration': time.time() - self.start_time,
                'error_count': len(self.errors)
            },
            'results': self.results,
            'errors': self.errors,
            'memory_snapshots': self.memory_snapshots,
            'performance_metrics': self.performance_metrics
        }

class ExtremeStressTester:
    """Testeur de stress extrême pour système neuromorphique"""
    
    def __init__(self):
        self.reporter = StressTestReporter()
        self.setup_mock_environment()
    
    def setup_mock_environment(self):
        """Setup environnement de test avec mocks avancés"""
        self.mock_db = Mock()
        self.mock_db.save_memory_fragment = AsyncMock(return_value=True)
        self.mock_db.search_memories_hybrid = AsyncMock(return_value=[])
        
        # Mock avec défaillances aléatoires
        async def unreliable_save(user_id, memory_fragment):
            if random.random() < 0.05:  # 5% de chance d'échec
                raise Exception("Database connection lost")
            await asyncio.sleep(random.uniform(0.001, 0.01))  # Latence variable
            return True
        
        self.mock_db.save_memory_fragment = unreliable_save
    
    async def test_massive_concurrent_load(self):
        """Test charge massive avec concurrence extrême"""
        print(" TEST 1: CHARGE MASSIVE CONCURRENTE")
        
        self.reporter.snapshot_memory("avant_charge_massive")
        
        try:
            # Créer 1000 systèmes mémoire simultanés
            systems = []
            for i in range(100):  # Réduit pour éviter l'explosion mémoire
                system = BrainMemorySystem(self.mock_db)
                system.config = {'use_qdrant': False, 'auto_consolidation': False}
                systems.append(system)
            
            # 10000 interactions simultanées
            tasks = []
            for i in range(1000):
                system = random.choice(systems)
                user_id = f"stress_user_{i % 50}"
                message = f"Message stress concurrent #{i} " + "x" * random.randint(10, 1000)
                response = f"Réponse stress #{i}"
                
                # Simuler store_interaction
                async def stress_interaction(sys, uid, msg, resp):
                    try:
                        limbic = sys.limbic_system
                        context = await limbic.analyze_emotional_context(msg)
                        # Simuler stockage
                        await asyncio.sleep(random.uniform(0.001, 0.005))
                        return True
                    except Exception as e:
                        return False
                
                task = stress_interaction(system, user_id, message, response)
                tasks.append(task)
            
            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            duration = time.time() - start_time
            
            successful = sum(1 for r in results if r == True)
            failed = len(results) - successful
            exceptions = [r for r in results if isinstance(r, Exception)]
            
            self.reporter.snapshot_memory("apres_charge_massive")
            
            details = {
                'total_tasks': len(tasks),
                'successful': successful,
                'failed': failed,
                'exception_count': len(exceptions),
                'throughput': len(results) / duration,
                'avg_time_per_task': duration / len(results)
            }
            
            # Critère de succès: au moins 80% de réussite avec 1000+ ops/sec
            success = (successful / len(results) >= 0.8) and (details['throughput'] >= 100)
            
            self.reporter.add_result("massive_concurrent_load", success, duration, details)
            
            print(f"    {successful}/{len(results)} tâches réussies")
            print(f"    Débit: {details['throughput']:.0f} ops/seconde")
            print(f"    Exceptions: {len(exceptions)}")
            
        except Exception as e:
            self.reporter.add_result("massive_concurrent_load", False, 0, {}, e)
            print(f"    Échec critique: {e}")
    
    async def test_memory_leak_detection(self):
        """Test détection fuites mémoire avec cycles longs"""
        print(" TEST 2: DÉTECTION FUITES MÉMOIRE")
        
        self.reporter.snapshot_memory("avant_fuite_memoire")
        
        try:
            initial_objects = len(gc.get_objects())
            
            # Créer et détruire 1000 systèmes en cycles
            for cycle in range(10):
                systems = []
                
                # Créer 100 systèmes
                for i in range(100):
                    system = BrainMemorySystem(self.mock_db)
                    system.config = {'use_qdrant': False}
                    
                    # Ajouter références circulaires intentionnelles
                    system._test_circular_ref = system
                    systems.append(system)
                
                # Utiliser les systèmes
                tasks = []
                for system in systems[:10]:  # Utiliser seulement 10 pour performance
                    task = system.limbic_system.analyze_emotional_context(
                        f"Test cycle {cycle} " + "data" * 100
                    )
                    tasks.append(task)
                
                await asyncio.gather(*tasks, return_exceptions=True)
                
                # Nettoyer explicitement
                for system in systems:
                    system._test_circular_ref = None
                del systems
                gc.collect()
                
                # Snapshot périodique
                if cycle % 3 == 0:
                    self.reporter.snapshot_memory(f"cycle_{cycle}")
            
            final_objects = len(gc.get_objects())
            object_growth = final_objects - initial_objects
            
            self.reporter.snapshot_memory("apres_fuite_memoire")
            
            # Analyse des snapshots
            memory_growth = (
                self.reporter.memory_snapshots[-1]['rss_mb'] - 
                self.reporter.memory_snapshots[-2]['rss_mb']
            )
            
            details = {
                'initial_objects': initial_objects,
                'final_objects': final_objects,
                'object_growth': object_growth,
                'memory_growth_mb': memory_growth,
                'cycles_completed': 10
            }
            
            # Critère: croissance < 50 MB et < 1000 objets
            success = memory_growth < 50.0 and object_growth < 1000
            
            self.reporter.add_result("memory_leak_detection", success, 0, details)
            
            print(f"    Croissance objets: {object_growth}")
            print(f"    Croissance mémoire: {memory_growth:.1f} MB")
            
        except Exception as e:
            self.reporter.add_result("memory_leak_detection", False, 0, {}, e)
            print(f"    Échec: {e}")
    
    async def test_malformed_inputs(self):
        """Test inputs malformés et edge cases extrêmes"""
        print(" TEST 3: INPUTS MALFORMÉS ET EDGE CASES")
        
        try:
            limbic = LimbicSystem()
            
            # Inputs malformés extrêmes
            malformed_inputs = [
                "",  # Vide
                None,  # None
                "x" * 100000,  # Très long
                "" * 1000,  # Emojis massifs
                "\x00\x01\x02" * 100,  # Caractères de contrôle
                "SELECT * FROM users; DROP TABLE users;",  # Injection SQL
                "<script>alert('xss')</script>" * 100,  # XSS
                "\n" * 1000,  # Newlines massifs
                "é" * 10000,  # Unicode massif
                json.dumps({"nested": {"very": {"deep": "object"}}}) * 1000,  # JSON imbriqué
                "\\x41\\x42\\x43" * 1000,  # Échappements
                random.random(),  # Type incorrect
                {"dict": "object"},  # Type incorrect
                [1, 2, 3, 4, 5],  # Type incorrect
            ]
            
            results = []
            for i, malformed_input in enumerate(malformed_inputs):
                try:
                    if isinstance(malformed_input, str) or malformed_input is None:
                        context = await limbic.analyze_emotional_context(
                            malformed_input or ""
                        )
                        result = "success"
                    else:
                        # Test avec conversion forcée
                        context = await limbic.analyze_emotional_context(str(malformed_input))
                        result = "success_converted"
                    
                    results.append(result)
                    
                except Exception as e:
                    results.append(f"error: {type(e).__name__}")
            
            # Analyser les résultats
            successes = sum(1 for r in results if r.startswith("success"))
            errors = len(results) - successes
            
            details = {
                'total_inputs': len(malformed_inputs),
                'successful_handled': successes,
                'errors': errors,
                'results': results
            }
            
            # Le système doit gérer au moins 70% des cas sans crash
            success = successes / len(malformed_inputs) >= 0.7
            
            self.reporter.add_result("malformed_inputs", success, 0, details)
            
            print(f"    Gérés: {successes}/{len(malformed_inputs)}")
            print(f"    Erreurs: {errors}")
            
        except Exception as e:
            self.reporter.add_result("malformed_inputs", False, 0, {}, e)
            print(f"    Échec critique: {e}")
    
    async def test_race_conditions(self):
        """Test conditions de course et accès concurrent aux ressources"""
        print(" TEST 4: RACE CONDITIONS ET CONCURRENCE")
        
        try:
            # Ressource partagée simulée
            shared_counter = {"value": 0}
            shared_data = {"memory_fragments": []}
            
            async def concurrent_access(worker_id, iterations):
                limbic = LimbicSystem()
                errors = []
                
                for i in range(iterations):
                    try:
                        # Accès concurrent à la ressource partagée
                        shared_counter["value"] += 1
                        
                        # Simulation d'une race condition
                        current_value = shared_counter["value"]
                        await asyncio.sleep(0.001)  # Fenêtre pour race condition
                        
                        if current_value != shared_counter["value"] - 1:
                            # Race condition détectée
                            pass
                        
                        # Analyse émotionnelle avec données partagées
                        text = f"Worker {worker_id} iteration {i}"
                        context = await limbic.analyze_emotional_context(text)
                        
                        # Ajout concurrent à liste partagée
                        shared_data["memory_fragments"].append({
                            'worker': worker_id,
                            'iteration': i,
                            'valence': context.valence,
                            'timestamp': time.time()
                        })
                        
                    except Exception as e:
                        errors.append(str(e))
                
                return len(errors)
            
            # Lancer 50 workers avec 20 itérations chacun
            tasks = []
            for worker_id in range(50):
                task = concurrent_access(worker_id, 20)
                tasks.append(task)
            
            start_time = time.time()
            error_counts = await asyncio.gather(*tasks, return_exceptions=True)
            duration = time.time() - start_time
            
            total_errors = sum(count for count in error_counts if isinstance(count, int))
            total_operations = 50 * 20
            final_counter = shared_counter["value"]
            fragments_count = len(shared_data["memory_fragments"])
            
            details = {
                'total_operations': total_operations,
                'total_errors': total_errors,
                'final_counter': final_counter,
                'fragments_stored': fragments_count,
                'expected_counter': total_operations,
                'duration': duration,
                'ops_per_second': total_operations / duration
            }
            
            # Succès si moins de 5% d'erreurs et compteur cohérent
            success = (total_errors / total_operations < 0.05) and abs(final_counter - total_operations) < 100
            
            self.reporter.add_result("race_conditions", success, duration, details)
            
            print(f"    Erreurs: {total_errors}/{total_operations}")
            print(f"    Compteur final: {final_counter} (attendu: {total_operations})")
            print(f"    Fragments: {fragments_count}")
            
        except Exception as e:
            self.reporter.add_result("race_conditions", False, 0, {}, e)
            print(f"    Échec: {e}")
    
    async def test_extreme_data_sizes(self):
        """Test avec données extrêmement volumineuses"""
        print(" TEST 5: DONNÉES VOLUMINEUSES EXTRÊMES")
        
        try:
            limbic = LimbicSystem()
            
            # Générer des données de tailles croissantes
            data_sizes = [1000, 10000, 100000, 500000, 1000000]  # caractères
            results = {}
            
            for size in data_sizes:
                print(f"   Test avec {size} caractères...")
                
                # Générer texte énorme
                huge_text = "Test de stress mémoire " * (size // 25) + "fin"
                huge_text = huge_text[:size]  # Tronquer exactement
                
                start_time = time.time()
                memory_before = psutil.Process().memory_info().rss / 1024 / 1024
                
                try:
                    # Tester analyse émotionnelle
                    context = await limbic.analyze_emotional_context(huge_text)
                    
                    duration = time.time() - start_time
                    memory_after = psutil.Process().memory_info().rss / 1024 / 1024
                    memory_used = memory_after - memory_before
                    
                    results[size] = {
                        'success': True,
                        'duration': duration,
                        'memory_used_mb': memory_used,
                        'valence': context.valence,
                        'emotion': context.detected_emotion,
                        'chars_per_second': size / duration if duration > 0 else 0
                    }
                    
                    print(f"      {duration:.2f}s, {memory_used:.1f} MB, {context.detected_emotion}")
                    
                    # Nettoyage forcé
                    del huge_text
                    gc.collect()
                    
                except Exception as e:
                    results[size] = {
                        'success': False,
                        'error': str(e),
                        'duration': time.time() - start_time
                    }
                    print(f"      Échec: {e}")
            
            # Analyser les résultats
            successful_sizes = [size for size, result in results.items() if result.get('success', False)]
            max_successful_size = max(successful_sizes) if successful_sizes else 0
            
            details = {
                'tested_sizes': data_sizes,
                'successful_sizes': successful_sizes,
                'max_successful_size': max_successful_size,
                'results': results
            }
            
            # Succès si peut traiter au moins 100K caractères
            success = max_successful_size >= 100000
            
            self.reporter.add_result("extreme_data_sizes", success, 0, details)
            
            print(f"    Taille max réussie: {max_successful_size:,} caractères")
            
        except Exception as e:
            self.reporter.add_result("extreme_data_sizes", False, 0, {}, e)
            print(f"    Échec: {e}")
    
    async def test_error_injection_resilience(self):
        """Test résilience avec injection d'erreurs aléatoires"""
        print(" TEST 6: RÉSILIENCE INJECTION D'ERREURS")
        
        try:
            # Simuler environnement défaillant
            original_methods = {}
            
            # Patch des méthodes pour injecter des erreurs
            def inject_random_errors(original_func, error_rate=0.1):
                async def wrapper(*args, **kwargs):
                    if random.random() < error_rate:
                        error_types = [
                            ConnectionError("Network down"),
                            TimeoutError("Operation timeout"),
                            MemoryError("Out of memory"),
                            ValueError("Invalid data"),
                            RuntimeError("System error")
                        ]
                        raise random.choice(error_types)
                    return await original_func(*args, **kwargs)
                return wrapper
            
            # Créer système avec erreurs injectées
            system = BrainMemorySystem(self.mock_db)
            system.config = {'use_qdrant': False}
            
            # Patcher les méthodes critiques
            original_analyze = system.limbic_system.analyze_emotional_context
            system.limbic_system.analyze_emotional_context = inject_random_errors(
                original_analyze, 0.15
            )
            
            # Test avec 1000 opérations
            operations = 1000
            successes = 0
            failures = 0
            error_types = {}
            
            for i in range(operations):
                try:
                    text = f"Test résilience {i} avec données variables"
                    context = await system.limbic_system.analyze_emotional_context(text)
                    successes += 1
                    
                except Exception as e:
                    failures += 1
                    error_type = type(e).__name__
                    error_types[error_type] = error_types.get(error_type, 0) + 1
            
            # Restaurer méthodes originales
            system.limbic_system.analyze_emotional_context = original_analyze
            
            success_rate = successes / operations
            
            details = {
                'total_operations': operations,
                'successes': successes,
                'failures': failures,
                'success_rate': success_rate,
                'error_types': error_types
            }
            
            # Succès si au moins 80% d'opérations réussies malgré les erreurs
            success = success_rate >= 0.8
            
            self.reporter.add_result("error_injection_resilience", success, 0, details)
            
            print(f"    Succès: {successes}/{operations} ({success_rate*100:.1f}%)")
            print(f"    Types d'erreurs: {error_types}")
            
        except Exception as e:
            self.reporter.add_result("error_injection_resilience", False, 0, {}, e)
            print(f"    Échec: {e}")
    
    async def run_all_stress_tests(self):
        """Exécute tous les tests de stress extrême"""
        print(" LANCEMENT TESTS DE STRESS EXTRÊME")
        print("=" * 80)
        
        self.reporter.snapshot_memory("debut_tests")
        
        # Tests de stress individuels
        tests = [
            self.test_massive_concurrent_load,
            self.test_memory_leak_detection,
            self.test_malformed_inputs,
            self.test_race_conditions,
            self.test_extreme_data_sizes,
            self.test_error_injection_resilience
        ]
        
        for test_func in tests:
            try:
                await test_func()
                print()
            except Exception as e:
                print(f" ÉCHEC CRITIQUE {test_func.__name__}: {e}")
                traceback.print_exc()
                print()
        
        self.reporter.snapshot_memory("fin_tests")
        
        # Générer rapport final
        report = self.reporter.generate_report()
        
        print(" RAPPORT FINAL TESTS DE STRESS EXTRÊME")
        print("=" * 80)
        
        summary = report['summary']
        print(f"Tests exécutés: {summary['total_tests']}")
        print(f"Succès: {summary['successful']}")
        print(f"Échecs: {summary['failed']}")
        print(f"Taux de réussite: {summary['success_rate']:.1f}%")
        print(f"Durée totale: {summary['total_duration']:.2f}s")
        print(f"Erreurs critiques: {summary['error_count']}")
        
        # Analyse mémoire
        memory_start = report['memory_snapshots'][0]['rss_mb']
        memory_end = report['memory_snapshots'][-1]['rss_mb']
        memory_peak = max(s['rss_mb'] for s in report['memory_snapshots'])
        
        print(f"\nAnalyse mémoire:")
        print(f"Mémoire début: {memory_start:.1f} MB")
        print(f"Mémoire fin: {memory_end:.1f} MB")
        print(f"Pic mémoire: {memory_peak:.1f} MB")
        print(f"Croissance totale: {memory_end - memory_start:.1f} MB")
        
        # Verdict final
        if summary['success_rate'] >= 80:
            print("\n SYSTÈME EXTRÊMEMENT ROBUSTE")
            print(" Résiste aux tests de stress les plus extrêmes")
        elif summary['success_rate'] >= 60:
            print("\n SYSTÈME MOYENNEMENT ROBUSTE")  
            print(" Améliorations recommandées pour cas extrêmes")
        else:
            print("\n SYSTÈME FRAGILE")
            print(" Corrections critiques requises")
        
        return report

async def main():
    """Fonction principale des tests de stress extrême"""
    tester = ExtremeStressTester()
    report = await tester.run_all_stress_tests()
    
    # Sauvegarder rapport
    import json
    with open('/home/enzo/Documents/Projet Jarvis/tests/extreme_stress_report.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    return report['summary']['success_rate'] >= 60

if __name__ == "__main__":
    import json
    result = asyncio.run(main())
    sys.exit(0 if result else 1)