#!/bin/bash
# Script de démarrage production pour Jarvis Rust Backend

set -e

echo "🦀 Démarrage Jarvis Rust Backend - Mode Production"
echo "=================================================="

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Vérifications sécurité production
echo -e "${BLUE}🔒 Vérifications sécurité production...${NC}"

# Vérifier variables d'environnement critiques
if [ -z "$JWT_SECRET_KEY" ] || [ ${#JWT_SECRET_KEY} -lt 32 ]; then
    echo -e "${RED}❌ JWT_SECRET_KEY manquante ou trop courte (min 32 chars)${NC}"
    exit 1
fi

if [ -z "$ENCRYPTION_KEY" ] || [ ${#ENCRYPTION_KEY} -ne 32 ]; then
    echo -e "${RED}❌ ENCRYPTION_KEY manquante ou incorrecte (exactement 32 chars)${NC}"
    exit 1
fi

if [ "$RUST_ENV" != "production" ]; then
    echo -e "${YELLOW}⚠️ RUST_ENV n'est pas défini sur 'production'${NC}"
fi

echo -e "${GREEN}✅ Variables de sécurité validées${NC}"

# Vérifier connectivité base de données
echo -e "${BLUE}🗄️ Vérification base de données...${NC}"
if [ -z "$DATABASE_URL" ]; then
    echo -e "${RED}❌ DATABASE_URL non définie${NC}"
    exit 1
fi

# Test connexion BDD
if ! sqlx migrate info > /dev/null 2>&1; then
    echo -e "${RED}❌ Impossible de se connecter à la base de données${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Base de données accessible${NC}"

# Appliquer les migrations si nécessaire
echo -e "${BLUE}📊 Vérification migrations...${NC}"
sqlx migrate run

# Compilation optimisée
echo -e "${BLUE}🔨 Compilation optimisée pour la production...${NC}"
export RUSTFLAGS="-C target-cpu=native -C lto=fat -C codegen-units=1"
cargo build --release

# Vérifier que le binaire existe
if [ ! -f "target/release/jarvis-core" ]; then
    echo -e "${RED}❌ Binaire de production non trouvé${NC}"
    exit 1
fi

# Configuration production
export RUST_LOG=${RUST_LOG:-"jarvis_core=info,tower_http=warn"}
export RUST_BACKTRACE=${RUST_BACKTRACE:-"0"}

# Test de sanité rapide
echo -e "${BLUE}🏥 Test de sanité du binaire...${NC}"
timeout 10s ./target/release/jarvis-core --version || {
    echo -e "${RED}❌ Le binaire ne répond pas correctement${NC}"
    exit 1
}

# Informations de démarrage
echo -e "${GREEN}🚀 Démarrage du serveur de production...${NC}"
echo -e "${BLUE}📊 Port: ${PORT:-8000}${NC}"
echo -e "${BLUE}🔧 Workers: ${WORKERS:-$(nproc)}${NC}"
echo -e "${BLUE}💾 Memory limit: ${MEMORY_LIMIT:-"512MB"}${NC}"
echo -e "${BLUE}🔒 Environment: ${RUST_ENV:-"production"}${NC}"
echo ""

# Créer un PID file
PID_FILE="/var/run/jarvis-rust.pid"
if [ -w "/var/run" ]; then
    echo $$ > $PID_FILE
    echo -e "${GREEN}📝 PID file créé: $PID_FILE${NC}"
fi

# Handler de signal pour arrêt propre
trap 'echo -e "\n${YELLOW}🛑 Arrêt du serveur...${NC}"; [ -f "$PID_FILE" ] && rm -f "$PID_FILE"; exit 0' SIGTERM SIGINT

# Démarrage avec gestion d'erreur
echo -e "${GREEN}✅ Jarvis Rust Backend démarré avec succès${NC}"
echo -e "${BLUE}📱 Health check: http://localhost:${PORT:-8000}/health${NC}"
echo ""

# Exécuter le binaire avec gestion d'erreur
./target/release/jarvis-core || {
    exit_code=$?
    echo -e "${RED}❌ Le serveur s'est arrêté avec le code: $exit_code${NC}"
    [ -f "$PID_FILE" ] && rm -f "$PID_FILE"
    exit $exit_code
}