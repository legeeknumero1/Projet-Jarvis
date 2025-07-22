#!/bin/bash
# Script d'initialisation Ollama pour Jarvis
# Instance #1 - EN_COURS - Script auto-téléchargement modèle Ollama

echo "🚀 Initialisation Ollama pour Jarvis..."

# Vérifier si Docker est installé
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé. Veuillez installer Docker d'abord."
    exit 1
fi

# Vérifier si le conteneur Ollama existe
if ! docker ps -a --format "table {{.Names}}" | grep -q "ollama"; then
    echo "📦 Démarrage du conteneur Ollama..."
    docker run -d \
        --name ollama \
        -p 11434:11434 \
        -v ollama_data:/root/.ollama \
        -e OLLAMA_ORIGINS="*" \
        -e OLLAMA_HOST="0.0.0.0" \
        --restart unless-stopped \
        ollama/ollama:latest
    
    echo "⏳ Attente du démarrage d'Ollama..."
    sleep 10
else
    echo "📦 Démarrage du conteneur Ollama existant..."
    docker start ollama
    sleep 5
fi

# Vérifier qu'Ollama répond
echo "🔍 Vérification de la disponibilité d'Ollama..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:11434/api/version > /dev/null 2>&1; then
        echo "✅ Ollama est disponible"
        break
    fi
    
    echo "⏳ Attente de la disponibilité d'Ollama... ($((attempt + 1))/$max_attempts)"
    sleep 2
    ((attempt++))
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Ollama n'est pas disponible après $max_attempts tentatives"
    exit 1
fi

# Vérifier si le modèle est déjà téléchargé
echo "🔍 Vérification du modèle llama3.2:1b..."
if docker exec ollama ollama list | grep -q "llama3.2:1b"; then
    echo "✅ Le modèle llama3.2:1b est déjà téléchargé"
else
    echo "📥 Téléchargement du modèle llama3.2:1b..."
    echo "⚠️  Cela peut prendre plusieurs minutes selon votre connexion..."
    
    # Télécharger le modèle avec affichage du progrès
    docker exec ollama ollama pull llama3.2:1b
    
    if [ $? -eq 0 ]; then
        echo "✅ Modèle llama3.2:1b téléchargé avec succès"
    else
        echo "❌ Erreur lors du téléchargement du modèle"
        exit 1
    fi
fi

# Test du modèle
echo "🧪 Test du modèle..."
test_response=$(docker exec ollama ollama run llama3.2:1b "Bonjour, réponds juste 'Test réussi'" 2>/dev/null)

if echo "$test_response" | grep -q -i "test"; then
    echo "✅ Test du modèle réussi"
else
    echo "⚠️  Test du modèle incertain, mais le téléchargement semble OK"
fi

# Afficher les modèles disponibles
echo "📋 Modèles disponibles dans Ollama:"
docker exec ollama ollama list

echo ""
echo "🎉 Configuration Ollama terminée !"
echo "🔗 Ollama est accessible sur : http://localhost:11434"
echo "🤖 Modèle prêt : llama3.2:1b"
echo ""
echo "Pour tester manuellement :"
echo "  curl -X POST http://localhost:11434/api/generate -d '{\"model\": \"llama3.2:1b\", \"prompt\": \"Bonjour\", \"stream\": false}'"

# Instance #1 - FINI - Script auto-téléchargement modèle Ollama