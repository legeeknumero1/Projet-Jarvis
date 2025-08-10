#!/bin/bash

# 🧠 Jarvis avec mémoire simple - Solution temporaire
# Usage: ./jarvis-with-memory.sh "votre message" [user_id]

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

MEMORY_FILE="/tmp/jarvis_memory_$(whoami).json"
USER_ID="${2:-enzo}"
MESSAGE="$1"

if [ -z "$MESSAGE" ]; then
    echo "Usage: $0 \"votre message\" [user_id]"
    echo "Exemple: $0 \"Salut, je m'appelle Enzo\" enzo"
    exit 1
fi

echo -e "${BLUE}🧠 Jarvis avec Mémoire${NC}"
echo "================================="

# Initialiser le fichier mémoire s'il n'existe pas
if [ ! -f "$MEMORY_FILE" ]; then
    echo '{}' > "$MEMORY_FILE"
    echo -e "${YELLOW}📝 Fichier mémoire initialisé: $MEMORY_FILE${NC}"
fi

# Récupérer l'historique de l'utilisateur
USER_HISTORY=$(jq -r --arg uid "$USER_ID" '.[$uid] // []' "$MEMORY_FILE" 2>/dev/null || echo "[]")

# Construire le contexte
CONTEXT=""
if [ "$USER_HISTORY" != "[]" ]; then
    CONTEXT=$(echo "$USER_HISTORY" | jq -r '.[-5:] | map("- " + .) | join("\n")' 2>/dev/null)
fi

# Construire le prompt avec contexte
SYSTEM_PROMPT="Tu es Jarvis, l'assistant IA personnel d'Enzo (21 ans, Perpignan).

MÉMOIRE CONVERSATIONNELLE :
$CONTEXT

RÈGLES :
- Utilise TOUJOURS les informations de la mémoire ci-dessus si pertinentes
- Réponds en français naturel
- Sois concis et amical avec Enzo
- Si tu te souviens d'informations précédentes, référence-les"

FULL_PROMPT="$SYSTEM_PROMPT

Question: $MESSAGE"

echo -e "${BLUE}Vous (${USER_ID}):${NC} $MESSAGE"
echo -e "${GREEN}Jarvis:${NC}"

# Appel à Ollama avec contexte
RESPONSE=$(curl -s -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d "{\"model\": \"llama3.2:1b\", \"prompt\": $(echo "$FULL_PROMPT" | jq -R -s .), \"stream\": false}" \
  | jq -r '.response' 2>/dev/null)

if [ -z "$RESPONSE" ] || [ "$RESPONSE" = "null" ]; then
    echo "❌ Erreur: Jarvis n'est pas disponible"
    exit 1
fi

echo "$RESPONSE"

# Sauvegarder dans la mémoire
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
NEW_MEMORY="[$TIMESTAMP] Utilisateur: $MESSAGE | Jarvis: ${RESPONSE:0:100}..."

# Mettre à jour le fichier mémoire
jq --arg uid "$USER_ID" --arg mem "$NEW_MEMORY" \
   '.[$uid] = ((.[$uid] // []) + [$mem])[-10:]' \
   "$MEMORY_FILE" > "${MEMORY_FILE}.tmp" && mv "${MEMORY_FILE}.tmp" "$MEMORY_FILE"

echo ""
echo -e "${YELLOW}💾 Conversation sauvegardée en mémoire${NC}"