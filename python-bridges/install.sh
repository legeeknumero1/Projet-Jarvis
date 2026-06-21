#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "=============================================="
echo " Jarvis Voice - F5-TTS Installation (macOS MPS)"
echo "=============================================="

echo "[1/4] Création de l'environnement virtuel Python..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

echo "[2/4] Mise à jour de pip..."
pip install --upgrade pip

echo "[3/4] Installation de PyTorch, FastAPI et dépendances audio..."
# Installation de PyTorch avec support MPS
pip install torch torchaudio torchvision
pip install fastapi uvicorn soundfile

echo "[4/4] Installation de F5-TTS (modèle de clonage)..."
pip install f5-tts

echo "=============================================="
echo " Installation terminée !"
echo " Pour lancer le moteur vocal, exécutez :"
echo " source venv/bin/activate"
echo " python app.py"
echo "=============================================="
