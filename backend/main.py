# Instance #22 - FINI - Shim main.py pour compatibilité uvicorn
"""
Shim de compatibilité pour uvicorn main:app
Architecture v1.2.0 : Point d'entrée principal = backend.app:create_app
"""
from .app import create_app

# Compatibilité uvicorn main:app
app = create_app()