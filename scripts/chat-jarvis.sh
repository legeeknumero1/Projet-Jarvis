#!/bin/bash

# Script simple pour chatter avec Jarvis
# Usage: ./chat-jarvis.sh "votre question"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE} Chat avec Jarvis${NC}"
echo "================================="

if [ $# -eq 0 ]; then
    echo "Usage: $0 \"votre question\""
    echo "Exemple: $0 \"Bonjour Jarvis, comment ça va?\""
    exit 1
fi

QUESTION="$1"

echo -e "${BLUE}Vous:${NC} $QUESTION"
echo -e "${GREEN}Jarvis:${NC}"

curl -s -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d "{\"model\": \"llama3.2:1b\", \"prompt\": \"$QUESTION\", \"stream\": false}" \
  | jq -r '.response' 2>/dev/null || echo "Erreur: Jarvis n'est pas disponible ou jq n'est pas installé"

echo ""