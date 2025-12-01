#  JARVIS AI - GUIDE DE SÉCURITÉ

##  AVERTISSEMENT DE SÉCURITÉ

Ce projet utilise des **clés de chiffrement 512 bits** et des **mots de passe sécurisés**. 
**JAMAIS** de données sensibles hardcodées dans le code !

---

##  CHECKLIST DE SÉCURITÉ

###  Configuration des Variables d'Environnement

1. **Copiez le template** :
   ```bash
   cp .env.example .env
   ```

2. **Générez des clés sécurisées** :
   ```bash
   # Clé de chiffrement principale (512 bits)
   openssl rand -hex 64
   
   # Clé JWT (256 bits)  
   openssl rand -hex 32
   
   # Mots de passe base de données (256 bits)
   openssl rand -hex 32
   ```

3. **Remplissez le fichier `.env`** avec les vraies valeurs

###  Clés de Sécurité Requises

| Variable | Taille minimale | Usage |
|----------|----------------|--------|
| `JARVIS_ENCRYPTION_KEY` | 512 bits (128 hex) | Chiffrement principal |
| `JWT_SECRET_KEY` | 256 bits (64 hex) | Tokens d'authentification |
| `BACKUP_ENCRYPTION_KEY` | 512 bits (128 hex) | Chiffrement des sauvegardes |
| `POSTGRES_PASSWORD` | 256 bits (64 hex) | Base de données principale |
| `TIMESCALE_PASSWORD` | 256 bits (64 hex) | Base de données TimescaleDB |

###  Validation Automatique

Le système valide automatiquement :
-  Longueur minimale des clés de chiffrement
-  Absence de mots de passe faibles (`123`, `password`, `admin`, etc.)
-  Format des variables d'environnement
-  Présence des variables critiques

---

##  SÉCURITÉ RÉSEAU

### Pare-feu et Ports

```yaml
# Ports exposés (docker-compose.yml)
- 3000:3000   # Interface web (HTTPS en production)
- 8100:8100   # API Backend (JWT requis)
- 8001:8001   # WebSocket (authentifié)
- 8002:8002   # TTS API (réseau interne)
- 8003:8003   # STT API (réseau interne) 
- 6333:6333   # Qdrant (réseau interne)
- 11434:11434 # Ollama (réseau interne)
```

### CORS et Origines Autorisées

```env
# Production : utiliser HTTPS uniquement
ALLOWED_ORIGINS=https://jarvis.votre-domaine.com,https://api.votre-domaine.com

# Développement local
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8001
```

### Rate Limiting

```env
RATE_LIMIT_REQUESTS=100  # Requêtes par minute
RATE_LIMIT_WINDOW=60     # Fenêtre en secondes
MAX_REQUEST_SIZE=10485760 # 10MB maximum
```

---

##  CHIFFREMENT DES DONNÉES

### Données Chiffrées

-  **Conversations utilisateur** : Chiffrées avec `JARVIS_ENCRYPTION_KEY`
-  **Mémoire contextuelle** : Chiffrée au repos
-  **Logs sensibles** : Chiffrés avec rotation automatique
-  **Sauvegardes** : Chiffrées avec `BACKUP_ENCRYPTION_KEY`
-  **Tokens JWT** : Signés avec `JWT_SECRET_KEY`

### Algorithmes Utilisés

- **Chiffrement symétrique** : AES-256-GCM
- **Hachage** : PBKDF2 avec SHA-256
- **JWT** : HS256 (HMAC-SHA256)
- **Clés** : Génération cryptographiquement sécurisée

---

##  DONNÉES INTERDITES

###  Ne JAMAIS stocker en clair :

- Mots de passe
- Clés API externes
- Tokens d'authentification
- Informations personnelles sensibles
- Clés de chiffrement

###  Ne JAMAIS committer :

- Fichier `.env`
- Dossier `logs/` avec données personnelles
- Dossier `memory/` avec conversations
- Fichiers `*.key`, `*.pem`, `*.cert`

---

##  ROTATION DES CLÉS

### Planification

1. **Clés de chiffrement** : Rotation tous les 6 mois
2. **JWT secrets** : Rotation tous les 3 mois
3. **Mots de passe DB** : Rotation annuelle
4. **Clés API externes** : Selon fournisseur

### Procédure de Rotation

```bash
# 1. Générer nouvelles clés
openssl rand -hex 64 > new-encryption.key
openssl rand -hex 32 > new-jwt.key

# 2. Sauvegarder données avec ancienne clé
docker exec jarvis_backend python -m scripts.backup_before_rotation

# 3. Mettre à jour .env
# 4. Redémarrer services
docker-compose restart

# 5. Vérifier fonctionnement
docker-compose logs -f backend
```

---

##  OUTILS DE SÉCURITÉ

### Commandes Utiles

```bash
# Vérifier force des clés
python -c "
import os
key = os.getenv('JARVIS_ENCRYPTION_KEY')
print(f'Longueur clé: {len(key)} caractères')
print(f'Entropie: {len(key) * 4} bits')
print(' OK' if len(key) >= 128 else ' TROP COURTE')
"

# Audit sécurité
docker run --rm -v $(pwd):/app securecodewarrior/docker-security-benchmark

# Test pénétration léger
nmap -p 3000,8000,8001 localhost
```

### Monitoring des Logs

```bash
# Surveiller tentatives d'authentification
docker logs jarvis_backend | grep "AUTH"

# Détecter activité suspecte
docker logs jarvis_backend | grep -E "(ERROR|WARNING|SECURITY)"
```

---

##  CONTACTS SÉCURITÉ

En cas d'incident de sécurité :

1. **Immédiatement** : Arrêter les services
   ```bash
   docker-compose down
   ```

2. **Analyser** : Examiner les logs
3. **Changer** : Toutes les clés compromises  
4. **Signaler** : Documenter l'incident

---

##  CONFORMITÉ

### Standards Respectés

-  **OWASP Top 10** : Protection contre vulnérabilités courantes
-  **GDPR/RGPD** : Chiffrement et droit à l'oubli
-  **ISO 27001** : Gestion sécurité information
-  **NIST** : Framework cybersécurité

### Audits Recommandés

- **Mensuel** : Scan vulnérabilités automatisé
- **Trimestriel** : Audit configuration sécurité
- **Annuel** : Test intrusion complet

---

Last Updated: 2025-10-25
*Version : 1.9.0*