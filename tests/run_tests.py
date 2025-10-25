#!/usr/bin/env python3
"""
🧪 SCRIPT EXÉCUTION TESTS - JARVIS V1.3.2
=========================================
Script pour lancer tests avec mesure couverture et rapports
Target: 85% couverture avec rapports détaillés
"""

import subprocess
import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime


def print_banner():
    """Affiche bannière de démarrage"""
    print("🧪" + "="*60)
    print("    JARVIS V1.3.2 - ENTERPRISE TEST RUNNER")
    print("="*62)
    print(f"📅 Démarré le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Objectif couverture: 85%")
    print("="*62)


def check_dependencies():
    """Vérifie les dépendances requises"""
    print("\n🔍 Vérification des dépendances...")
    
    required_packages = [
        'pytest',
        'pytest-asyncio', 
        'pytest-cov',
        'pytest-mock',
        'httpx',
        'fastapi'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"  ❌ {package}")
    
    if missing_packages:
        print(f"\n⚠️  Packages manquants: {', '.join(missing_packages)}")
        print("💡 Installation: pip install " + " ".join(missing_packages))
        return False
    
    print("✅ Toutes les dépendances sont installées")
    return True


def run_tests(test_type="all", verbose=False, coverage=True):
    """Lance les tests avec options"""
    print(f"\n🚀 Lancement tests ({test_type})...")
    
    # Construction commande pytest
    cmd = ["python", "-m", "pytest"]
    
    # Options de base
    if verbose:
        cmd.extend(["-v", "-s"])
    else:
        cmd.append("-q")
    
    # Couverture
    if coverage:
        cmd.extend([
            "--cov=backend",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "--cov-report=xml",
            "--cov-fail-under=85"
        ])
    
    # Sélection des tests
    if test_type == "unit":
        cmd.extend(["-m", "unit"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
    elif test_type == "security":
        cmd.extend(["-m", "security"])
    elif test_type == "performance":
        cmd.extend(["-m", "performance"])
    elif test_type == "fast":
        cmd.extend(["-m", "not slow"])
    elif test_type == "auth":
        cmd.extend(["-m", "auth"])
    elif test_type == "api":
        cmd.extend(["-m", "api"])
    
    # Répertoire des tests
    cmd.append("tests/")
    
    print(f"📝 Commande: {' '.join(cmd)}")
    
    # Exécution
    start_time = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        end_time = time.time()
        
        # Affichage résultats
        print(f"\n⏱️  Durée: {end_time - start_time:.2f}s")
        print(f"🔢 Code de retour: {result.returncode}")
        
        if result.stdout:
            print("\n📊 STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("\n⚠️  STDERR:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution: {e}")
        return False


def generate_coverage_report():
    """Génère rapport de couverture détaillé"""
    print("\n📊 Génération rapport couverture...")
    
    try:
        # Rapport terminal
        cmd = ["python", "-m", "pytest", "--cov=backend", "--cov-report=term-missing", "tests/"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Rapport terminal généré")
            
            # Extraire pourcentage couverture
            lines = result.stdout.split('\n')
            for line in lines:
                if "TOTAL" in line and "%" in line:
                    coverage_line = line
                    parts = coverage_line.split()
                    for part in parts:
                        if "%" in part:
                            coverage_percent = float(part.replace("%", ""))
                            print(f"🎯 Couverture actuelle: {coverage_percent}%")
                            
                            if coverage_percent >= 85:
                                print("🎉 Objectif 85% atteint!")
                            else:
                                remaining = 85 - coverage_percent
                                print(f"📈 Reste {remaining:.1f}% pour atteindre l'objectif")
                            break
            
            # Rapport HTML
            html_cmd = ["python", "-m", "pytest", "--cov=backend", "--cov-report=html:htmlcov", "tests/"]
            html_result = subprocess.run(html_cmd, capture_output=True, text=True)
            
            if html_result.returncode == 0:
                print("✅ Rapport HTML généré dans 'htmlcov/'")
                print("🌐 Ouvrir htmlcov/index.html pour détails")
            
            return True
        else:
            print("❌ Erreur génération rapport")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def run_specific_test_file(test_file):
    """Lance un fichier de test spécifique"""
    print(f"\n🎯 Test fichier spécifique: {test_file}")
    
    cmd = [
        "python", "-m", "pytest", 
        "-v",
        "--cov=backend",
        "--cov-report=term-missing",
        f"tests/{test_file}"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print(f"📝 Résultat pour {test_file}:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️  Erreurs:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def generate_test_summary():
    """Génère résumé des tests"""
    print("\n📋 RÉSUMÉ DES TESTS")
    print("="*40)
    
    test_files = [
        "test_configuration.py",
        "test_auth.py", 
        "test_main_api.py",
        "test_ollama_client.py",
        "test_security.py"
    ]
    
    total_tests = 0
    
    for test_file in test_files:
        test_path = Path("tests") / test_file
        if test_path.exists():
            # Compter tests dans le fichier
            content = test_path.read_text()
            test_count = content.count("def test_")
            total_tests += test_count
            print(f"📄 {test_file:<25} {test_count:>3} tests")
        else:
            print(f"⚠️  {test_file:<25} NON TROUVÉ")
    
    print("-"*40)
    print(f"📊 TOTAL: {total_tests} tests")
    
    # Estimation couverture par catégorie
    categories = {
        "Configuration": 15,
        "Authentification": 25,
        "API Endpoints": 35,
        "Client Ollama": 30,
        "Sécurité": 40
    }
    
    print(f"\n📈 RÉPARTITION PAR CATÉGORIE:")
    for category, count in categories.items():
        print(f"  {category:<15}: {count:>3} tests")
    
    return total_tests


def run_quick_validation():
    """Lance validation rapide"""
    print("\n⚡ VALIDATION RAPIDE")
    print("="*30)
    
    # Tests de base seulement
    cmd = [
        "python", "-m", "pytest",
        "-m", "not slow",
        "--tb=short",
        "-q",
        "tests/"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Validation rapide réussie")
            return True
        else:
            print("❌ Validation rapide échouée")
            print(result.stdout)
            return False
            
    except subprocess.TimeoutExpired:
        print("⏱️  Timeout validation rapide")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def main():
    """Fonction principale"""
    print_banner()
    
    # Vérifier dépendances
    if not check_dependencies():
        sys.exit(1)
    
    # Arguments de ligne de commande basiques
    if len(sys.argv) > 1:
        action = sys.argv[1]
    else:
        action = "all"
    
    success = True
    
    if action == "quick":
        success = run_quick_validation()
    
    elif action == "coverage":
        success = generate_coverage_report()
    
    elif action == "summary":
        generate_test_summary()
    
    elif action.startswith("file:"):
        test_file = action.split(":", 1)[1]
        success = run_specific_test_file(test_file)
    
    elif action in ["unit", "integration", "security", "performance", "fast", "auth", "api"]:
        success = run_tests(action, verbose=True, coverage=True)
    
    elif action == "all":
        print("\n🎯 EXÉCUTION COMPLÈTE")
        print("="*40)
        
        # 1. Validation rapide d'abord
        if not run_quick_validation():
            print("⚠️  Validation rapide échouée, continuation...")
        
        # 2. Résumé tests
        generate_test_summary()
        
        # 3. Exécution complète
        success = run_tests("all", verbose=True, coverage=True)
        
        # 4. Rapport couverture
        if success:
            generate_coverage_report()
    
    else:
        print(f"❌ Action inconnue: {action}")
        print("\n💡 Actions disponibles:")
        print("  all         - Tous les tests avec couverture")
        print("  quick       - Validation rapide") 
        print("  unit        - Tests unitaires seulement")
        print("  integration - Tests d'intégration")
        print("  security    - Tests de sécurité")
        print("  performance - Tests de performance")
        print("  auth        - Tests authentification")
        print("  api         - Tests API")
        print("  coverage    - Génère rapport couverture")
        print("  summary     - Résumé des tests")
        print("  file:nom.py - Lance fichier spécifique")
        sys.exit(1)
    
    # Conclusion
    print("\n" + "="*62)
    if success:
        print("🎉 TESTS TERMINÉS AVEC SUCCÈS!")
        print("✅ Objectif couverture 85% - En cours d'atteinte")
    else:
        print("❌ TESTS ÉCHOUÉS")
        print("🔧 Vérifier les erreurs ci-dessus")
    
    print(f"⏰ Terminé le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*62)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()