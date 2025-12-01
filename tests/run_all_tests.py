#!/usr/bin/env python3
"""
 SUITE COMPLÈTE DE TESTS - Système Mémoire Neuromorphique Jarvis
Script maître pour exécuter tous les tests et générer un rapport détaillé
"""

import sys
import os
import asyncio
import time
import json
import subprocess
from datetime import datetime
import traceback

# Ajouter le chemin backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

class TestReporter:
    """Générateur de rapports de tests"""
    
    def __init__(self):
        self.results = {
            'start_time': datetime.now().isoformat(),
            'tests': {},
            'summary': {},
            'errors': []
        }
    
    def add_test_result(self, test_name, success, duration, details=None, error=None):
        self.results['tests'][test_name] = {
            'success': success,
            'duration': duration,
            'details': details or {},
            'error': str(error) if error else None
        }
    
    def generate_report(self):
        self.results['end_time'] = datetime.now().isoformat()
        
        total_tests = len(self.results['tests'])
        successful_tests = sum(1 for t in self.results['tests'].values() if t['success'])
        failed_tests = total_tests - successful_tests
        
        total_duration = sum(t['duration'] for t in self.results['tests'].values())
        
        self.results['summary'] = {
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'failed_tests': failed_tests,
            'success_rate': (successful_tests / total_tests * 100) if total_tests > 0 else 0,
            'total_duration': total_duration
        }
        
        return self.results
    
    def save_report(self, filename="test_report.json"):
        report_path = os.path.join(os.path.dirname(__file__), filename)
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        return report_path

def test_file_existence():
    """Vérifier existence des fichiers critiques"""
    critical_files = [
        "/home/enzo/Documents/Projet Jarvis/docker-compose.yml",
        "/home/enzo/Documents/Projet Jarvis/backend/main.py",
        "/home/enzo/Documents/Projet Jarvis/backend/memory/brain_memory_system.py",
        "/home/enzo/Documents/Projet Jarvis/backend/memory/qdrant_adapter.py",
        "/home/enzo/Documents/Projet Jarvis/backend/requirements.txt",
        "/home/enzo/Documents/Projet Jarvis/config/qdrant_config.yaml",
        "/home/enzo/Documents/Projet Jarvis/backend/db/timescale_init.sql"
    ]
    
    missing_files = []
    for file_path in critical_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    return {
        'success': len(missing_files) == 0,
        'missing_files': missing_files,
        'total_files': len(critical_files)
    }

def test_python_syntax():
    """Tester syntaxe Python des fichiers critiques"""
    python_files = [
        "/home/enzo/Documents/Projet Jarvis/backend/main.py",
        "/home/enzo/Documents/Projet Jarvis/backend/memory/brain_memory_system.py",
        "/home/enzo/Documents/Projet Jarvis/backend/memory/qdrant_adapter.py"
    ]
    
    syntax_errors = []
    for file_path in python_files:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            compile(content, file_path, 'exec')
        except SyntaxError as e:
            syntax_errors.append(f"{file_path}: {e}")
        except Exception as e:
            syntax_errors.append(f"{file_path}: {e}")
    
    return {
        'success': len(syntax_errors) == 0,
        'syntax_errors': syntax_errors,
        'total_files': len(python_files)
    }

def test_docker_compose_config():
    """Tester configuration Docker Compose"""
    compose_file = "/home/enzo/Documents/Projet Jarvis/docker-compose.yml"
    
    try:
        with open(compose_file, 'r') as f:
            content = f.read()
        
        # Vérifications critiques
        checks = {
            'version_defined': 'version:' in content,
            'services_defined': 'services:' in content,
            'networks_defined': 'networks:' in content,
            'jarvis_network': 'jarvis_network:' in content,
            'backend_service': 'backend:' in content,
            'qdrant_service': 'qdrant:' in content,
            'timescale_service': 'timescale:' in content,
            'postgres_service': 'postgres:' in content,
            'correct_subnet': '172.20.0.0/16' in content,
            'qdrant_url_env': 'QDRANT_URL=http://172.20.0.120:6333' in content,
            'timescale_url_env': 'TIMESCALE_URL=postgresql://jarvis:jarvis@172.20.0.130:5432/jarvis_timeseries' in content,
            'brain_memory_enabled': 'BRAIN_MEMORY_ENABLED=true' in content
        }
        
        passed_checks = sum(1 for v in checks.values() if v)
        total_checks = len(checks)
        
        return {
            'success': passed_checks == total_checks,
            'passed_checks': passed_checks,
            'total_checks': total_checks,
            'failed_checks': [k for k, v in checks.items() if not v]
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def test_requirements_dependencies():
    """Tester dépendances requirements.txt"""
    req_file = "/home/enzo/Documents/Projet Jarvis/backend/requirements.txt"
    
    try:
        with open(req_file, 'r') as f:
            content = f.read()
        
        critical_deps = [
            'qdrant-client', 'sqlalchemy', 'asyncpg', 'fastapi',
            'uvicorn', 'pydantic', 'sentence-transformers', 'redis'
        ]
        
        missing_deps = []
        for dep in critical_deps:
            if dep not in content:
                missing_deps.append(dep)
        
        return {
            'success': len(missing_deps) == 0,
            'missing_dependencies': missing_deps,
            'total_dependencies': len(critical_deps)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

async def test_memory_system_imports():
    """Tester imports du système mémoire"""
    import_tests = []
    
    try:
        from memory.brain_memory_system import (
            BrainMemorySystem, LimbicSystem, PrefrontalCortex, Hippocampus,
            MemoryFragment, EmotionalContext, MemoryType, ConsolidationLevel
        )
        import_tests.append(('brain_memory_system', True, None))
    except Exception as e:
        import_tests.append(('brain_memory_system', False, str(e)))
    
    try:
        from memory.qdrant_adapter import QdrantMemoryAdapter
        import_tests.append(('qdrant_adapter', True, None))
    except Exception as e:
        import_tests.append(('qdrant_adapter', False, str(e)))
    
    successful_imports = sum(1 for _, success, _ in import_tests if success)
    total_imports = len(import_tests)
    
    return {
        'success': successful_imports == total_imports,
        'successful_imports': successful_imports,
        'total_imports': total_imports,
        'import_details': import_tests
    }

async def test_basic_functionality():
    """Tester fonctionnalité de base du système"""
    try:
        from memory.brain_memory_system import (
            LimbicSystem, EmotionalContext, MemoryFragment, MemoryType, ConsolidationLevel
        )
        from datetime import datetime
        
        # Test système limbique
        limbic = LimbicSystem()
        emotional_result = await limbic.analyze_emotional_context("Je suis très content !")
        
        # Vérifications
        checks = {
            'emotional_context_created': isinstance(emotional_result, EmotionalContext),
            'valence_in_range': -1.0 <= emotional_result.valence <= 1.0,
            'arousal_in_range': 0.0 <= emotional_result.arousal <= 1.0,
            'confidence_in_range': 0.0 <= emotional_result.confidence <= 1.0,
            'emotion_detected': len(emotional_result.detected_emotion) > 0
        }
        
        # Test création fragment mémoire
        memory_fragment = MemoryFragment(
            content="Test mémoire",
            memory_type=MemoryType.EPISODIC,
            emotional_context=emotional_result,
            importance_score=0.7,
            consolidation_level=ConsolidationLevel.VOLATILE,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            access_count=1
        )
        
        checks['memory_fragment_created'] = isinstance(memory_fragment, MemoryFragment)
        
        passed_checks = sum(1 for v in checks.values() if v)
        total_checks = len(checks)
        
        return {
            'success': passed_checks == total_checks,
            'passed_checks': passed_checks,
            'total_checks': total_checks,
            'emotional_valence': emotional_result.valence,
            'detected_emotion': emotional_result.detected_emotion
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

async def run_unit_tests():
    """Exécuter tests unitaires avec pytest"""
    test_file = "/home/enzo/Documents/Projet Jarvis/tests/test_brain_memory_system.py"
    
    if not os.path.exists(test_file):
        return {
            'success': False,
            'error': 'Fichier de tests unitaires non trouvé'
        }
    
    try:
        # Tenter d'exécuter pytest
        result = subprocess.run([
            'python3', '-m', 'pytest', test_file, '-v', '--tb=short'
        ], capture_output=True, text=True, timeout=60)
        
        return {
            'success': result.returncode == 0,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
        
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Tests unitaires timeout (>60s)'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Erreur exécution pytest: {e}'
        }

async def run_integration_tests():
    """Exécuter tests d'intégration"""
    test_file = "/home/enzo/Documents/Projet Jarvis/tests/test_docker_integration.py"
    
    if not os.path.exists(test_file):
        return {
            'success': False,
            'error': 'Fichier de tests d\'intégration non trouvé'
        }
    
    try:
        result = subprocess.run([
            'python3', '-m', 'pytest', test_file, '-v', '--tb=short'
        ], capture_output=True, text=True, timeout=120)
        
        return {
            'success': result.returncode == 0,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
        
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Tests d\'intégration timeout (>120s)'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Erreur exécution tests intégration: {e}'
        }

async def run_performance_tests():
    """Exécuter tests de performance"""
    test_file = "/home/enzo/Documents/Projet Jarvis/tests/test_performance_load.py"
    
    if not os.path.exists(test_file):
        return {
            'success': False,
            'error': 'Fichier de tests de performance non trouvé'
        }
    
    try:
        # Exécuter directement le module de performance
        result = subprocess.run([
            'python3', test_file
        ], capture_output=True, text=True, timeout=300)  # 5 minutes max
        
        return {
            'success': result.returncode == 0,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
        
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Tests de performance timeout (>300s)'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Erreur exécution tests performance: {e}'
        }

async def main():
    """Fonction principale - Exécuter tous les tests"""
    print(" SUITE COMPLÈTE DE TESTS - SYSTÈME MÉMOIRE NEUROMORPHIQUE JARVIS")
    print("=" * 80)
    print(f" Début des tests: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    reporter = TestReporter()
    
    # Tests séquentiels avec chronométrage
    tests = [
        ("Existence des fichiers", test_file_existence),
        ("Syntaxe Python", test_python_syntax),
        ("Configuration Docker Compose", test_docker_compose_config),
        ("Dépendances Requirements", test_requirements_dependencies),
        ("Imports système mémoire", test_memory_system_imports),
        ("Fonctionnalité de base", test_basic_functionality),
        ("Tests unitaires", run_unit_tests),
        ("Tests d'intégration", run_integration_tests),
        ("Tests de performance", run_performance_tests)
    ]
    
    for test_name, test_func in tests:
        print(f" Exécution: {test_name}")
        print("-" * 50)
        
        start_time = time.time()
        
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            duration = time.time() - start_time
            
            if result['success']:
                print(f" {test_name} - SUCCÈS ({duration:.2f}s)")
                if 'details' in result:
                    for key, value in result.items():
                        if key not in ['success', 'details']:
                            print(f"   {key}: {value}")
            else:
                print(f" {test_name} - ÉCHEC ({duration:.2f}s)")
                if 'error' in result:
                    print(f"   Erreur: {result['error']}")
                for key, value in result.items():
                    if key not in ['success', 'error']:
                        print(f"   {key}: {value}")
            
            reporter.add_test_result(test_name, result['success'], duration, result)
            
        except Exception as e:
            duration = time.time() - start_time
            print(f" {test_name} - ERREUR CRITIQUE ({duration:.2f}s)")
            print(f"   Exception: {e}")
            traceback.print_exc()
            
            reporter.add_test_result(test_name, False, duration, {}, e)
        
        print()
    
    # Générer rapport final
    print(" GÉNÉRATION DU RAPPORT FINAL")
    print("=" * 50)
    
    report = reporter.generate_report()
    report_path = reporter.save_report()
    
    summary = report['summary']
    print(f" Résultats des tests:")
    print(f"   Tests totaux: {summary['total_tests']}")
    print(f"   Tests réussis: {summary['successful_tests']}")
    print(f"   Tests échoués: {summary['failed_tests']}")
    print(f"   Taux de réussite: {summary['success_rate']:.1f}%")
    print(f"   Durée totale: {summary['total_duration']:.2f}s")
    print(f" Rapport sauvegardé: {report_path}")
    
    # Verdict final
    print("\n" + "=" * 80)
    if summary['success_rate'] >= 90:
        print(" SYSTÈME MÉMOIRE NEUROMORPHIQUE - TESTS EXCELLENTS!")
        print(" Le système est prêt pour le déploiement")
    elif summary['success_rate'] >= 70:
        print(" SYSTÈME MÉMOIRE NEUROMORPHIQUE - TESTS SATISFAISANTS")
        print(" Quelques ajustements recommandés")
    else:
        print(" SYSTÈME MÉMOIRE NEUROMORPHIQUE - TESTS INSUFFISANTS")
        print(" Corrections majeures requises avant déploiement")
    
    print(f" Fin des tests: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return summary['success_rate'] >= 70

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)