#!/usr/bin/env python3

import os
import sys
import logging

# Créer le dossier logs s'il n'existe pas
os.makedirs('/app/logs', exist_ok=True)

# Configuration du logging simplifiée
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/jarvis.log'),
        logging.StreamHandler()
    ]
)

# Maintenant importer et lancer main
if __name__ == "__main__":
    import uvicorn
    from main import app
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)