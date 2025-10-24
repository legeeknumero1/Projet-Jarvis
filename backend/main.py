# Instance #22 - FINI - Shim main.py pour compatibilité uvicorn
"""
Shim de compatibilité pour uvicorn main:app
Architecture v1.2.0 : Point d'entrée principal = backend.app:create_app
"""
import sys
import os

# Ajouter le répertoire parent au path pour les imports absolus
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from app import create_app

# Compatibilité uvicorn main:app
app = create_app()