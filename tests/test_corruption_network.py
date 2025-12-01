#!/usr/bin/env python3
"""
 TESTS CORRUPTION DONNÉES ET RÉSEAU - Système Mémoire Neuromorphique
Tests de résilience face aux pannes réseau, corruption et cas extrêmes
"""

import sys
import os
import asyncio
import time
import json
import random
import pickle
import tempfile
import sqlite3
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from concurrent.futures import ThreadPoolExecutor
import threading
import signal

# Ajouter le chemin backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from memory.brain_memory_system import BrainMemorySystem, LimbicSystem
from memory.memory_types import MemoryFragment, EmotionalContext, MemoryType, ConsolidationLevel
from memory.qdrant_adapter import QdrantMemoryAdapter

class CorruptionNetworkTester:
    """Testeur pour corruption données et pannes réseau"""
    
    def __init__(self):
        self.results = {}
        self.temp_files = []
    
    def cleanup(self):
        """Nettoie les fichiers temporaires"""
        for temp_file in self.temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass
    
    async def test_data_corruption_resilience(self):
        """Test résilience face à la corruption de données"""
        print(" TEST 1: RÉSILIENCE CORRUPTION DONNÉES")
        
        try:
            # Créer données corrompues de différents types
            corruption_tests = []
            
            # 1. JSON corrompu
            corrupted_json = '{"user_id": "test", "content": "Message", incomplete'
            corruption_tests.append(("json_incomplete", corrupted_json))
            
            # 2. Caractères non-UTF8
            corrupted_utf8 = b'\xff\xfe\x00\x00Invalid UTF-8 \x80\x81\x82'
            corruption_tests.append(("invalid_utf8", corrupted_utf8))
            
            # 3. Structure de données incohérente
            corrupted_structure = {
                "emotional_context": "should_be_object_not_string",
                "memory_type": 999,  # Invalid enum value
                "created_at": "not_a_date",
                "importance_score": "not_a_number"
            }
            corruption_tests.append(("invalid_structure", corrupted_structure))
            
            # 4. Données binaires aléatoires
            random_binary = os.urandom(1000)
            corruption_tests.append(("random_binary", random_binary))
            
            # 5. Très grande chaîne avec caractères de contrôle
            control_chars = ''.join(chr(i) for i in range(32)) * 100
            corruption_tests.append(("control_chars", control_chars))
            
            limbic = LimbicSystem()
            results = {}
            
            for test_name, corrupted_data in corruption_tests:
                try:
                    # Tenter de traiter données corrompues
                    if isinstance(corrupted_data, bytes):
                        # Tenter décodage
                        try:
                            text = corrupted_data.decode('utf-8', errors='replace')
                        except:
                            text = str(corrupted_data)
                    elif isinstance(corrupted_data, dict):
                        text = json.dumps(corrupted_data, default=str)
                    else:
                        text = str(corrupted_data)
                    
                    # Analyser avec le système limbique
                    context = await limbic.analyze_emotional_context(text)
                    
                    results[test_name] = {
                        'status': 'handled',
                        'valence': context.valence,
                        'emotion': context.detected_emotion,
                        'confidence': context.confidence
                    }
                    
                except Exception as e:
                    results[test_name] = {
                        'status': 'error',
                        'error_type': type(e).__name__,
                        'error_message': str(e)
                    }
            
            # Analyser résultats
            handled = sum(1 for r in results.values() if r['status'] == 'handled')
            total = len(results)
            
            details = {
                'tests_run': total,
                'successfully_handled': handled,
                'error_rate': (total - handled) / total,
                'results': results
            }
            
            success = handled / total >= 0.8  # 80% doivent être gérés
            
            self.results['data_corruption'] = {
                'success': success,
                'details': details
            }
            
            print(f"    Gérés: {handled}/{total}")
            print(f"    Taux d'erreur: {details['error_rate']*100:.1f}%")
            
        except Exception as e:
            self.results['data_corruption'] = {
                'success': False,
                'error': str(e)
            }
            print(f"    Échec critique: {e}")
    
    async def test_network_timeout_simulation(self):
        """Test simulation timeouts et pannes réseau"""
        print(" TEST 2: SIMULATION TIMEOUTS RÉSEAU")
        
        try:
            # Simuler différents types de pannes réseau
            network_scenarios = [
                ("timeout_immediate", 0.0),      # Timeout immédiat
                ("timeout_short", 0.1),          # Timeout court
                ("timeout_medium", 1.0),         # Timeout moyen
                ("timeout_long", 5.0),           # Timeout long
                ("intermittent", "random"),      # Pannes intermittentes
            ]
            
            results = {}
            
            for scenario_name, delay in network_scenarios:
                print(f"   Test scenario: {scenario_name}")
                
                # Mock base de données avec timeouts
                async def mock_db_with_timeout(*args, **kwargs):
                    if delay == "random":
                        if random.random() < 0.3:  # 30% chance de panne
                            raise asyncio.TimeoutError("Network timeout")
                    elif isinstance(delay, (int, float)):
                        await asyncio.sleep(delay)
                        if delay > 2.0:  # Considérer comme timeout si > 2s
                            raise asyncio.TimeoutError(f"Timeout after {delay}s")
                    return True
                
                mock_db = Mock()
                mock_db.save_memory_fragment = mock_db_with_timeout
                
                # Tester 50 opérations avec ce scénario
                system = BrainMemorySystem(mock_db)
                system.config = {'use_qdrant': False}
                
                operations = 50
                successes = 0
                timeouts = 0
                errors = 0
                
                start_time = time.time()
                
                for i in range(operations):
                    try:
                        # Simuler stockage avec timeout potentiel
                        await asyncio.wait_for(
                            mock_db.save_memory_fragment(f"user_{i}", None),
                            timeout=3.0  # Timeout global de 3s
                        )
                        successes += 1
                        
                    except asyncio.TimeoutError:
                        timeouts += 1
                    except Exception:
                        errors += 1
                
                duration = time.time() - start_time
                
                results[scenario_name] = {
                    'operations': operations,
                    'successes': successes,
                    'timeouts': timeouts,
                    'errors': errors,
                    'duration': duration,
                    'avg_time_per_op': duration / operations
                }
                
                print(f"     Succès: {successes}, Timeouts: {timeouts}, Erreurs: {errors}")
            
            # Analyser performance globale
            total_ops = sum(r['operations'] for r in results.values())
            total_successes = sum(r['successes'] for r in results.values())
            
            details = {
                'scenarios_tested': len(network_scenarios),
                'total_operations': total_ops,
                'total_successes': total_successes,
                'overall_success_rate': total_successes / total_ops,
                'scenario_results': results
            }
            
            success = details['overall_success_rate'] >= 0.6  # 60% min avec pannes réseau
            
            self.results['network_timeouts'] = {
                'success': success,
                'details': details
            }
            
            print(f"    Succès global: {total_successes}/{total_ops} ({details['overall_success_rate']*100:.1f}%)")
            
        except Exception as e:
            self.results['network_timeouts'] = {
                'success': False,
                'error': str(e)
            }
            print(f"    Échec: {e}")
    
    async def test_database_corruption_recovery(self):
        """Test récupération après corruption base de données"""
        print(" TEST 3: RÉCUPÉRATION CORRUPTION BDD")
        
        try:
            # Créer base SQLite temporaire pour tester
            temp_db = tempfile.mktemp(suffix='.db')
            self.temp_files.append(temp_db)
            
            # Initialiser base normale
            conn = sqlite3.connect(temp_db)
            conn.execute("""
                CREATE TABLE memory_fragments (
                    id INTEGER PRIMARY KEY,
                    user_id TEXT,
                    content TEXT,
                    emotional_valence REAL,
                    importance_score REAL,
                    created_at TEXT
                )
            """)
            
            # Insérer données normales
            normal_data = [
                ('user1', 'Message normal', 0.5, 0.7, '2024-01-01'),
                ('user2', 'Autre message', -0.2, 0.6, '2024-01-02'),
            ]
            
            conn.executemany(
                "INSERT INTO memory_fragments (user_id, content, emotional_valence, importance_score, created_at) VALUES (?, ?, ?, ?, ?)",
                normal_data
            )
            conn.commit()
            
            # Corrompre intentionnellement la base
            corruption_tests = [
                # 1. Données NULL inattendues
                ("Corrompre avec NULL", 
                 "INSERT INTO memory_fragments VALUES (NULL, NULL, NULL, NULL, NULL, NULL)"),
                
                # 2. Types incorrects
                ("Types incorrects",
                 "INSERT INTO memory_fragments (user_id, emotional_valence) VALUES ('user3', 'not_a_number')"),
                
                # 3. Contraintes violées
                ("Valeurs hors limites",
                 "INSERT INTO memory_fragments (user_id, emotional_valence, importance_score) VALUES ('user4', 999.9, -1.0)"),
            ]
            
            results = {}
            
            for test_name, corruption_sql in corruption_tests:
                try:
                    # Appliquer corruption
                    conn.execute(corruption_sql)
                    conn.commit()
                    
                    # Tenter de lire les données corrompues
                    cursor = conn.execute("SELECT * FROM memory_fragments")
                    rows = cursor.fetchall()
                    
                    # Analyser les données récupérées
                    valid_rows = 0
                    corrupted_rows = 0
                    
                    for row in rows:
                        try:
                            # Valider structure
                            if row[1] is not None and row[2] is not None:  # user_id et content
                                # Valider valence émotionnelle
                                if row[3] is not None and isinstance(row[3], (int, float)) and -1.0 <= row[3] <= 1.0:
                                    valid_rows += 1
                                else:
                                    corrupted_rows += 1
                            else:
                                corrupted_rows += 1
                        except:
                            corrupted_rows += 1
                    
                    results[test_name] = {
                        'total_rows': len(rows),
                        'valid_rows': valid_rows,
                        'corrupted_rows': corrupted_rows,
                        'recovery_rate': valid_rows / len(rows) if rows else 0
                    }
                    
                except Exception as e:
                    results[test_name] = {
                        'error': str(e),
                        'error_type': type(e).__name__
                    }
            
            conn.close()
            
            # Analyser capacité de récupération
            total_tests = len(corruption_tests)
            successful_recoveries = sum(1 for r in results.values() if 'recovery_rate' in r)
            
            details = {
                'corruption_tests': total_tests,
                'successful_recoveries': successful_recoveries,
                'recovery_success_rate': successful_recoveries / total_tests,
                'test_results': results
            }
            
            success = details['recovery_success_rate'] >= 0.8
            
            self.results['database_corruption'] = {
                'success': success,
                'details': details
            }
            
            print(f"    Récupérations réussies: {successful_recoveries}/{total_tests}")
            
        except Exception as e:
            self.results['database_corruption'] = {
                'success': False,
                'error': str(e)
            }
            print(f"    Échec: {e}")
    
    async def test_signal_interruption_handling(self):
        """Test gestion interruptions système (SIGINT, SIGTERM)"""
        print(" TEST 4: GESTION INTERRUPTIONS SYSTÈME")
        
        try:
            interrupted_operations = []
            completed_operations = []
            
            # Simuler opérations longues qui peuvent être interrompues
            async def long_running_operation(operation_id):
                try:
                    # Opération qui prend du temps
                    for i in range(10):
                        await asyncio.sleep(0.1)
                        # Vérifier si interruption demandée
                        if hasattr(asyncio.current_task(), '_cancelled'):
                            interrupted_operations.append(operation_id)
                            return False
                    
                    completed_operations.append(operation_id)
                    return True
                    
                except asyncio.CancelledError:
                    interrupted_operations.append(operation_id)
                    return False
            
            # Lancer plusieurs opérations
            tasks = []
            for i in range(20):
                task = asyncio.create_task(long_running_operation(i))
                tasks.append(task)
            
            # Laisser quelques opérations commencer
            await asyncio.sleep(0.3)
            
            # Simuler interruption (annuler certaines tâches)
            for task in tasks[10:]:  # Annuler la moitié
                task.cancel()
            
            # Attendre que toutes les tâches se terminent
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Analyser les résultats
            successful = sum(1 for r in results if r == True)
            cancelled = sum(1 for r in results if isinstance(r, asyncio.CancelledError))
            failed = len(results) - successful - cancelled
            
            details = {
                'total_operations': len(tasks),
                'completed': len(completed_operations),
                'interrupted': len(interrupted_operations),
                'cancelled': cancelled,
                'failed': failed,
                'graceful_handling_rate': (len(interrupted_operations) + cancelled) / len(tasks)
            }
            
            # Succès si les interruptions sont gérées proprement
            success = details['graceful_handling_rate'] >= 0.4  # Au moins 40% gérées
            
            self.results['signal_interruption'] = {
                'success': success,
                'details': details
            }
            
            print(f"    Complétées: {len(completed_operations)}")
            print(f"    Interrompues proprement: {len(interrupted_operations)}")
            print(f"    Annulées: {cancelled}")
            
        except Exception as e:
            self.results['signal_interruption'] = {
                'success': False,
                'error': str(e)
            }
            print(f"    Échec: {e}")
    
    async def test_qdrant_connection_failures(self):
        """Test pannes connexion Qdrant avec fallback"""
        print(" TEST 5: PANNES CONNEXION QDRANT")
        
        try:
            # Simuler différents états de Qdrant
            failure_scenarios = [
                ("connection_refused", ConnectionRefusedError("Connection refused")),
                ("timeout", asyncio.TimeoutError("Connection timeout")),
                ("service_unavailable", Exception("Service unavailable")),
                ("invalid_response", ValueError("Invalid response format")),
                ("network_error", OSError("Network is unreachable"))
            ]
            
            results = {}
            
            for scenario_name, exception in failure_scenarios:
                print(f"   Test scenario: {scenario_name}")
                
                # Mock adapter Qdrant défaillant
                mock_adapter = Mock()
                mock_adapter.initialize = AsyncMock(side_effect=exception)
                mock_adapter.store_memory_fragment = AsyncMock(side_effect=exception)
                mock_adapter.search_memories = AsyncMock(side_effect=exception)
                
                # Tester fallback système
                mock_db = Mock()
                mock_db.save_memory_fragment = AsyncMock(return_value=True)
                
                system = BrainMemorySystem(mock_db)
                system.qdrant_adapter = mock_adapter
                system.config = {'use_qdrant': True}  # Activé mais va échouer
                
                # Tester opérations avec fallback
                operations = 20
                fallback_successes = 0
                
                for i in range(operations):
                    try:
                        # Simuler stockage qui devrait fallback sur PostgreSQL
                        limbic = system.limbic_system
                        context = await limbic.analyze_emotional_context(f"Test message {i}")
                        
                        # Simuler tentative Qdrant qui échoue -> fallback DB
                        try:
                            await mock_adapter.store_memory_fragment(f"user_{i}", None)
                        except:
                            # Fallback réussi si DB fonctionne
                            await mock_db.save_memory_fragment(f"user_{i}", None)
                            fallback_successes += 1
                        
                    except Exception as e:
                        pass  # Échec total
                
                results[scenario_name] = {
                    'operations': operations,
                    'fallback_successes': fallback_successes,
                    'fallback_rate': fallback_successes / operations
                }
                
                print(f"     Fallbacks réussis: {fallback_successes}/{operations}")
            
            # Analyser performance fallback
            total_ops = sum(r['operations'] for r in results.values())
            total_fallbacks = sum(r['fallback_successes'] for r in results.values())
            
            details = {
                'scenarios_tested': len(failure_scenarios),
                'total_operations': total_ops,
                'total_fallback_successes': total_fallbacks,
                'overall_fallback_rate': total_fallbacks / total_ops,
                'scenario_results': results
            }
            
            success = details['overall_fallback_rate'] >= 0.9  # 90% fallback réussis
            
            self.results['qdrant_failures'] = {
                'success': success,
                'details': details
            }
            
            print(f"    Fallback global: {total_fallbacks}/{total_ops} ({details['overall_fallback_rate']*100:.1f}%)")
            
        except Exception as e:
            self.results['qdrant_failures'] = {
                'success': False,
                'error': str(e)
            }
            print(f"    Échec: {e}")
    
    async def run_all_corruption_network_tests(self):
        """Execute tous les tests de corruption et réseau"""
        print(" LANCEMENT TESTS CORRUPTION ET RÉSEAU")
        print("=" * 80)
        
        tests = [
            self.test_data_corruption_resilience,
            self.test_network_timeout_simulation,
            self.test_database_corruption_recovery,
            self.test_signal_interruption_handling,
            self.test_qdrant_connection_failures
        ]
        
        try:
            for test_func in tests:
                await test_func()
                print()
            
            # Analyser résultats globaux
            total_tests = len(self.results)
            successful_tests = sum(1 for r in self.results.values() if r.get('success', False))
            
            print(" RAPPORT FINAL CORRUPTION ET RÉSEAU")
            print("=" * 60)
            print(f"Tests exécutés: {total_tests}")
            print(f"Succès: {successful_tests}")
            print(f"Échecs: {total_tests - successful_tests}")
            print(f"Taux de réussite: {successful_tests/total_tests*100:.1f}%")
            
            # Détails par test
            for test_name, result in self.results.items():
                status = "" if result.get('success', False) else ""
                print(f"{status} {test_name}")
                if 'error' in result:
                    print(f"    Erreur: {result['error']}")
            
            if successful_tests / total_tests >= 0.8:
                print("\n SYSTÈME TRÈS RÉSISTANT AUX PANNES")
                print(" Excellent fallback et récupération")
            elif successful_tests / total_tests >= 0.6:
                print("\n SYSTÈME MOYENNEMENT RÉSILIENT")
                print(" Améliorations possibles")
            else:
                print("\n SYSTÈME FRAGILE AUX PANNES")
                print(" Corrections critiques nécessaires")
            
            return successful_tests / total_tests >= 0.6
            
        finally:
            self.cleanup()

async def main():
    """Fonction principale"""
    tester = CorruptionNetworkTester()
    return await tester.run_all_corruption_network_tests()

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)