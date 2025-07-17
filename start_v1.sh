#!/bin/bash

# Script de lancement Jarvis V1 - Interface de démonstration

echo "🚀 Démarrage de Jarvis V1 - Interface de démonstration"
echo "========================================================"

# Vérification des dépendances
echo "📦 Vérification des dépendances..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ Node.js/npm n'est pas installé"
    exit 1
fi

# Installation des dépendances Python
echo "🐍 Installation des dépendances Python..."
pip3 install websockets asyncio

# Installation des dépendances Node.js
echo "📦 Installation des dépendances Node.js..."
cd frontend
npm install

# Démarrage du serveur WebSocket simple
echo "🔧 Démarrage du serveur WebSocket..."
cd ../services/interface
python3 simple_server.py &
SERVER_PID=$!

# Attendre que le serveur soit prêt
sleep 2

# Démarrage du frontend React
echo "🌐 Démarrage de l'interface React..."
cd ../../frontend
npm start &
FRONTEND_PID=$!

echo ""
echo "✅ Jarvis V1 est maintenant en cours d'exécution !"
echo "📱 Interface web: http://localhost:3000"
echo "🔌 WebSocket: ws://localhost:8000"
echo ""
echo "Pour arrêter Jarvis V1, appuyez sur Ctrl+C"
echo ""

# Fonction de nettoyage
cleanup() {
    echo ""
    echo "🛑 Arrêt de Jarvis V1..."
    kill $SERVER_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Jarvis V1 arrêté proprement"
    exit 0
}

# Capture des signaux d'arrêt
trap cleanup SIGINT SIGTERM

# Attendre indéfiniment
wait