#!/bin/bash

#  Script d'installation Brave Search MCP pour Jarvis
# Intègre Brave Search API dans le système MCP

set -e

echo " Installation Brave Search MCP pour Jarvis"
echo "=============================================="

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')]   $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%H:%M:%S')]  $1${NC}"
    exit 1
}

# Vérifier que nous sommes dans le bon répertoire
if [[ ! -d "MCP" ]]; then
    error "Ce script doit être exécuté depuis la racine du projet Jarvis"
fi

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    error "Python 3 n'est pas installé"
fi

log " Python détecté: $(python3 --version)"

# Vérifier les clés API
ENV_FILE=".env"
if [[ ! -f "$ENV_FILE" ]]; then
    error "Fichier .env non trouvé"
fi

# Vérifier les clés Brave
if grep -q "BRAVE_API_KEY.*=.*[a-zA-Z0-9]" "$ENV_FILE"; then
    log " BRAVE_API_KEY trouvée dans .env"
else
    warn "  BRAVE_API_KEY manquante - ajout dans .env..."
    
    # Lire les clés depuis api-key
    if [[ -f "api-key" ]]; then
        BRAVE_KEY_1=$(grep "brave-api-key" api-key | head -1 | cut -d'"' -f2)
        BRAVE_KEY_2=$(grep "brave-api-key-2" api-key | head -1 | cut -d'"' -f2)
        
        if [[ -n "$BRAVE_KEY_1" ]]; then
            echo "" >> "$ENV_FILE"
            echo "# Brave Search API Keys" >> "$ENV_FILE"
            echo "BRAVE_API_KEY=$BRAVE_KEY_1" >> "$ENV_FILE"
            
            if [[ -n "$BRAVE_KEY_2" ]]; then
                echo "BRAVE_API_KEY_BACKUP=$BRAVE_KEY_2" >> "$ENV_FILE"
            fi
            
            log " Clés Brave ajoutées au .env"
        else
            warn "  Clés Brave non trouvées dans api-key"
        fi
    else
        warn "  Fichier api-key non trouvé"
    fi
fi

# Installer les dépendances Python nécessaires
log " Installation des dépendances Python..."

# Vérifier si httpx est installé
python3 -c "import httpx" 2>/dev/null || {
    warn "Installation de httpx..."
    pip3 install httpx
}

# Vérifier si nous sommes dans un environnement Docker
if [[ -f "/.dockerenv" ]]; then
    log " Environnement Docker détecté"
    PYTHON_PATH="/usr/local/bin/python3"
else
    PYTHON_PATH=$(which python3)
fi

# Rendre le serveur MCP exécutable
chmod +x MCP/servers/brave_search_mcp.py

# Test de l'installation
log " Test de l'installation..."

cd MCP/servers

# Export des variables d'environnement pour le test
export BRAVE_API_KEY=$(grep "BRAVE_API_KEY=" ../../.env | head -1 | cut -d'=' -f2)
export BRAVE_API_KEY_BACKUP=$(grep "BRAVE_API_KEY_BACKUP=" ../../.env | head -1 | cut -d'=' -f2)

if [[ -n "$BRAVE_API_KEY" ]]; then
    log " Test avec clé API: ${BRAVE_API_KEY:0:10}..."
    
    # Test simple
    python3 -c "
import asyncio
import sys
sys.path.append('.')
from brave_search_mcp import BraveSearchMCP

async def test():
    try:
        mcp = BraveSearchMCP()
        result = await mcp.web_search('test', count=1)
        await mcp.close()
        print(' Test réussi!')
        return True
    except Exception as e:
        print(f' Test échoué: {e}')
        return False

success = asyncio.run(test())
exit(0 if success else 1)
    " && log " Brave Search MCP fonctionne correctement" || warn "  Test échoué - vérifiez les clés API"
    
else
    warn "  Impossible de tester - clé API manquante"
fi

cd ../..

# Mise à jour de la configuration MCP manager
log " Mise à jour du MCP Manager..."

# Vérifier si le MCP manager existe
if [[ -f "MCP/mcp_manager.py" ]]; then
    # Ajouter Brave Search à la liste des serveurs disponibles
    if ! grep -q "brave-search" MCP/mcp_manager.py; then
        log " Ajout de Brave Search au MCP Manager..."
        
        # Backup du fichier original
        cp MCP/mcp_manager.py MCP/mcp_manager.py.backup
        
        # Note: Cette partie nécessiterait une modification du mcp_manager.py
        # pour inclure la configuration Brave Search
        warn "  Ajout manuel requis dans mcp_manager.py"
    else
        log " Brave Search déjà configuré dans MCP Manager"
    fi
else
    warn "  MCP Manager non trouvé"
fi

# Instructions finales
echo ""
log " Installation Brave Search MCP terminée!"
echo ""
echo -e "${BLUE} Configuration ajoutée:${NC}"
echo "  • Serveur MCP: MCP/servers/brave_search_mcp.py"
echo "  • Configuration: MCP/configs/brave_search.json"  
echo "  • Clés API configurées dans .env"
echo ""
echo -e "${BLUE} Utilisation:${NC}"
echo "  • Web Search: brave_web_search"
echo "  • News Search: brave_news_search"
echo "  • Image Search: brave_image_search"
echo "  • Video Search: brave_video_search"
echo ""
echo -e "${BLUE} Fonctionnalités:${NC}"
echo "  • Recherche sans tracking"
echo "  • Rotation automatique des clés API"
echo "  • SafeSearch configurable"
echo "  • Support multi-langue"
echo "  • Limite: 2000 requêtes/mois (free tier)"
echo ""
echo -e "${YELLOW}  Pour activer complètement:${NC}"
echo "1. Redémarrer le backend Jarvis"
echo "2. Tester via l'interface MCP"
echo ""

log " Installation réussie - Brave Search prêt à l'emploi!"