import requests
import subprocess
import time
import pytest
import os

# Port sur lequel le serveur core écoutera
CORE_PORT = 8000
BASE_URL = f"http://127.0.0.1:{CORE_PORT}"

@pytest.fixture(scope="module")
def core_server():
    """Fixture pour démarrer et arrêter le serveur jarvis-core."""
    
    # Compiler le binaire core en mode release
    compile_process = subprocess.run(
        ["cargo", "build", "--release", "--bin", "jarvis-core"],
        cwd="../core",
        capture_output=True,
        text=True
    )
    assert compile_process.returncode == 0, f"La compilation de jarvis-core a échoué: {compile_process.stderr}"
    
    core_executable = "../core/target/release/jarvis-core"
    
    # Créer un environnement pour le serveur avec un JWT_SECRET valide
    server_env = os.environ.copy()
    server_env["JWT_SECRET"] = "a-secure-secret-key-for-testing-purposes-only"
    server_env["DATABASE_URL"] = "postgres://user:password@localhost/testdb"
    
    # Démarrer le serveur en arrière-plan avec l'environnement
    server_process = subprocess.Popen([core_executable], env=server_env)
    
    # Laisser le temps au serveur de démarrer
    time.sleep(3)
    
    # Vérifier que le processus est bien en cours
    assert server_process.poll() is None, "Le serveur core n'a pas pu démarrer."
    
    # "yield" pour permettre l'exécution des tests
    yield
    
    # Après les tests, arrêter le serveur
    server_process.terminate()
    server_process.wait()

def test_health_check(core_server):
    """
    Teste l'endpoint /health pour vérifier que le serveur est en ligne.
    """
    try:
        response = requests.get(f"{BASE_URL}/health")
        
        # Vérifier le code de statut
        assert response.status_code == 200
        
        # Vérifier le contenu de la réponse
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data
        assert "uptime" in data
        
        print(f"\n[SUCCESS] Health check passed: {data}")

    except requests.exceptions.ConnectionError as e:
        pytest.fail(f"La connexion au serveur core a échoué: {e}")