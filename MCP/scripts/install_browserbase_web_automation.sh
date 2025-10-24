#!/bin/bash
# Installation et configuration du serveur MCP Browserbase pour Jarvis

set -e

echo "🔌 Installation du serveur MCP Browserbase..."

# Variables
MCP_DIR="/home/enzo/Projet-Jarvis/MCP"
BROWSERBASE_DIR="${MCP_DIR}/servers/browserbase_web_automation"
ENV_FILE="/home/enzo/Projet-Jarvis/.env"

# Créer le serveur si nécessaire
if [ ! -d "$BROWSERBASE_DIR" ]; then
    echo "📁 Création du dossier serveur..."
    mkdir -p "$BROWSERBASE_DIR"
fi

# Se déplacer dans le dossier du serveur
cd "$BROWSERBASE_DIR"

# Initialiser le projet Node.js si nécessaire
if [ ! -f "package.json" ]; then
    echo "📦 Initialisation du projet Node.js..."
    npm init -y
    
    # Installer le serveur MCP Browserbase
    echo "📦 Installation du serveur MCP Browserbase..."
    npm install @browserbasehq/mcp-server-browserbase
    
    # Créer le fichier CLI
    mkdir -p dist
    cat > dist/cli.js << 'EOF'
#!/usr/bin/env node
const { BrowserbaseWebAutomationServer } = require('@browserbasehq/mcp-server-browserbase');
const server = new BrowserbaseWebAutomationServer();
server.serve();
EOF
    chmod +x dist/cli.js
fi

# Installer les dépendances si nécessaire
if [ ! -d "node_modules" ]; then
    echo "📦 Installation des dépendances..."
    npm install
fi

# Vérifier que le fichier CLI existe
if [ ! -f "dist/cli.js" ]; then
    echo "❌ Fichier CLI non trouvé"
    echo "🔨 Création du fichier CLI..."
    mkdir -p dist
    cat > dist/cli.js << 'EOF'
#!/usr/bin/env node
const { BrowserbaseWebAutomationServer } = require('@browserbasehq/mcp-server-browserbase');
const server = new BrowserbaseWebAutomationServer();
server.serve();
EOF
    chmod +x dist/cli.js
fi

# Rendre le fichier exécutable
chmod +x dist/cli.js

echo "✅ Serveur MCP Browserbase installé avec succès"
echo "📍 Chemin: $BROWSERBASE_DIR/dist/cli.js"

# Vérifier les variables d'environnement
echo ""
echo "🔧 Vérification de la configuration..."

if grep -q "BROWSERBASE_API_KEY" "$ENV_FILE"; then
    echo "✅ BROWSERBASE_API_KEY trouvée dans .env"
else
    echo "⚠️  BROWSERBASE_API_KEY manquante - ajout dans .env..."
    echo "" >> "$ENV_FILE"
    echo "# Browserbase MCP Server" >> "$ENV_FILE"
    echo "BROWSERBASE_API_KEY=" >> "$ENV_FILE"
    echo "BROWSERBASE_PROJECT_ID=" >> "$ENV_FILE"
    echo "GEMINI_API_KEY=" >> "$ENV_FILE"
fi

echo ""
echo "🎉 Installation terminée !"
echo "📝 N'oubliez pas de configurer vos clés API dans le fichier .env"
echo "🔗 Créer un compte sur https://www.browserbase.com/"