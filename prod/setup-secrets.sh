#!/bin/bash
# Setup production secrets pour Jarvis

set -euo pipefail

echo "🔐 Configuration secrets production Jarvis"

# Créer dossier secrets
mkdir -p secrets

# Générer clé API sécurisée si n'existe pas
if [[ ! -f secrets/api_key.txt ]]; then
    echo "Génération clé API sécurisée..."
    openssl rand -hex 32 > secrets/api_key.txt
    echo "✅ Clé API générée dans secrets/api_key.txt"
fi

# Générer mot de passe DB si n'existe pas  
if [[ ! -f secrets/db_password.txt ]]; then
    echo "Génération mot de passe DB..."
    openssl rand -base64 32 > secrets/db_password.txt
    echo "✅ Mot de passe DB générée dans secrets/db_password.txt"
fi

# Permissions restrictives
chmod 600 secrets/*.txt

echo "
🎯 Prochaines étapes:

1. Configurer certificats TLS:
   mkdir -p ssl
   # Utiliser Certbot pour Let's Encrypt:
   # certbot certonly --webroot -w /tmp -d jarvis.example.com

2. Adapter nginx.conf avec votre domain:
   sed -i 's/jarvis.example.com/your-domain.com/g' nginx.conf

3. Build frontend optimisé:
   cd ../frontend && npm run build

4. Démarrer stack production:
   docker-compose -f docker-compose.prod.yml up -d

5. Test smoke:
   curl https://your-domain.com/health
"