#!/bin/bash
# Script de démarrage développement pour Jarvis Rust Backend

set -e

echo "🦀 Démarrage Jarvis Rust Backend - Mode Développement"
echo "======================================================"

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Vérifier que nous sommes dans le bon répertoire
if [ ! -f "Cargo.toml" ]; then
    echo -e "${RED}❌ Erreur: Ce script doit être exécuté depuis le répertoire backend-rust${NC}"
    exit 1
fi

# Vérifier Rust
echo -e "${BLUE}🔍 Vérification de Rust...${NC}"
if ! command -v cargo &> /dev/null; then
    echo -e "${RED}❌ Erreur: Rust/Cargo non installé${NC}"
    echo -e "${YELLOW}💡 Installer Rust: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Rust version: $(rustc --version)${NC}"

# Vérifier le fichier .env
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️ Fichier .env manquant, copie depuis .env.example${NC}"
    cp .env.example .env
    echo -e "${YELLOW}💡 N'oubliez pas d'éditer .env avec vos paramètres${NC}"
fi

# Vérifier PostgreSQL
echo -e "${BLUE}🗄️ Vérification PostgreSQL...${NC}"
source .env
DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')

if ! nc -z $DB_HOST $DB_PORT 2>/dev/null; then
    echo -e "${RED}❌ PostgreSQL non accessible sur $DB_HOST:$DB_PORT${NC}"
    echo -e "${YELLOW}💡 Démarrer avec: docker run -d --name postgres-jarvis -e POSTGRES_DB=jarvis_db -e POSTGRES_USER=jarvis -e POSTGRES_PASSWORD=jarvis123 -p 5432:5432 postgres:15-alpine${NC}"
    exit 1
fi

echo -e "${GREEN}✅ PostgreSQL accessible${NC}"

# Installer sqlx-cli si nécessaire
if ! command -v sqlx &> /dev/null; then
    echo -e "${YELLOW}🔧 Installation de sqlx-cli...${NC}"
    cargo install sqlx-cli --no-default-features --features postgres
fi

# Appliquer les migrations
echo -e "${BLUE}📊 Application des migrations...${NC}"
sqlx migrate run

# Vérifier les services externes (optionnel)
echo -e "${BLUE}🔍 Vérification services externes...${NC}"

# Ollama
OLLAMA_URL=${OLLAMA_URL:-"http://localhost:11434"}
if curl -s "$OLLAMA_URL/api/version" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Ollama accessible${NC}"
else
    echo -e "${YELLOW}⚠️ Ollama non accessible ($OLLAMA_URL)${NC}"
fi

# Redis
REDIS_HOST=$(echo $REDIS_URL | sed -n 's/redis:\/\/\([^:]*\):.*/\1/p')
REDIS_PORT=$(echo $REDIS_URL | sed -n 's/redis:\/\/[^:]*:\([0-9]*\)/\1/p')
if nc -z $REDIS_HOST $REDIS_PORT 2>/dev/null; then
    echo -e "${GREEN}✅ Redis accessible${NC}"
else
    echo -e "${YELLOW}⚠️ Redis non accessible ($REDIS_HOST:$REDIS_PORT)${NC}"
fi

# Compilation et lancement
echo -e "${BLUE}🔨 Compilation en mode debug...${NC}"
export RUST_LOG=${RUST_LOG:-"jarvis_core=debug,tower_http=info"}
export RUST_BACKTRACE=1

echo -e "${GREEN}🚀 Démarrage du serveur...${NC}"
echo -e "${BLUE}📱 Interface web: http://localhost:3000${NC}"
echo -e "${BLUE}🔌 API Rust: http://localhost:${PORT:-8000}${NC}"
echo -e "${BLUE}💻 Health check: http://localhost:${PORT:-8000}/health${NC}"
echo ""
echo -e "${YELLOW}💡 Pour arrêter: Ctrl+C${NC}"
echo ""

# Lancer avec hot-reload si cargo-watch est installé
if command -v cargo-watch &> /dev/null; then
    echo -e "${GREEN}🔄 Mode hot-reload activé (cargo-watch)${NC}"
    cargo watch -x run
else
    echo -e "${YELLOW}💡 Pour le hot-reload: cargo install cargo-watch${NC}"
    cargo run
fi