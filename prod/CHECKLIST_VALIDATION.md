#  Checklist Validation Production Jarvis v1.3

> Guide de test pour valider le graceful shutdown et la robustesse production

##  Tests SIGTERM / Graceful Shutdown

### 1. Test Docker Compose Down
```bash
# Terminal 1 - Démarrer en mode attach
docker-compose -f docker-compose.prod.yml up

# Terminal 2 - Envoyer SIGTERM
docker-compose -f docker-compose.prod.yml down
```

** Logs attendus :**
```
 [SHUTDOWN] Arrêt graceful services...
 [SHUTDOWN] Mode drain activé - nouvelles connexions refusées
 [WS_MGR] Fermeture de X connexions...
 [WS_MGR] Fermeture terminée - Succès: X, Erreurs: 0
 [SHUTDOWN] Services arrêtés proprement
```

### 2. Test Refus Nouvelles Connexions (Mode Drain)
```bash
# Terminal 1 - WebSocket connecté
websocat ws://localhost/ws

# Terminal 2 - Déclencher shutdown
docker-compose down

# Terminal 3 - Tenter nouvelle connexion (doit échouer)
websocat ws://localhost/ws
# Attendu: Connexion fermée avec code 1013
```

** Comportement attendu :**
- Connexions existantes : reçoivent code `1001` (Going Away)
- Nouvelles connexions : reçoivent code `1013` (Try Again Later)

### 3. Test Annulation Tâches Background
```bash
# Se connecter et envoyer message long (génération LLM)
echo '{"message":"Écris un long poème de 500 mots sur l'IA","user_id":"test"}' | websocat ws://localhost/ws &

# Pendant le traitement, déclencher shutdown
docker-compose down
```

** Logs attendus :**
```
 [WS] client_123 Annulation de 1 tâches actives...
 [WS] client_123 Tâche de traitement annulée  
 [WS] client_123 Tâches annulées proprement
```

##  Anti-Patterns (ce qui NE doit PAS arriver)

###  Erreurs à éviter
- `RuntimeError: Event loop is closed`
- `RuntimeError: cannot schedule new futures after shutdown`
- `websocket.receive_text() after close`
- `upstream prematurely closed connection` (Nginx)

###  Fuites mémoire
- Compteur `ws_active_connections` reste > 0 après shutdown
- Tâches `asyncio` non terminées
- Connexions HTTP/TCP ouvertes (netstat/ss)

##  Tests de Robustesse

### 1. Test Rate Limiting
```bash
# Spam API chat (doit être limité à 30/min)
for i in {1..50}; do
  curl -X POST http://localhost/chat \
    -H "Content-Type: application/json" \
    -d '{"message":"test'$i'","user_id":"spam"}' &
done
```

** Attendu :** Status `429` après 30 requêtes

### 2. Test Taille Messages
```bash
# Message trop long (> 4096 chars)
python3 -c "
import json, requests
msg = 'A' * 5000
r = requests.post('http://localhost/chat', json={'message': msg, 'user_id': 'test'})
print(f'Status: {r.status_code}, Response: {r.text}')
"
```

** Attendu :** Status `413` (Payload Too Large)

### 3. Test Timeouts Services
```bash
# Arrêter Ollama pour tester timeout/retry
docker-compose stop ollama

# Essayer requête (doit timeout proprement)
curl -X POST http://localhost/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"test avec ollama down","user_id":"test"}'
```

** Attendu :** Status `503` avec message explicite

##  Vérifications Métriques

### 1. WebSocket Connections Gauge
```bash
curl http://localhost/metrics | grep ws_active_connections
```

** Attendu :** Valeur correspond au nombre réel de connexions

### 2. Health vs Readiness
```bash
# Liveness (toujours OK si processus vivant)
curl http://localhost/health
# {"status": "healthy", "timestamp": "...", "version": "1.2.0-hardened"}

# Readiness (dépend services externes)  
curl http://localhost/ready
# {"ready": true, "services": {"llm": true, "voice": true, "memory": true}}
```

### 3. Nginx Rate Limiting
```bash
# Vérifier logs Nginx pour rate limiting
docker logs jarvis_proxy 2>&1 | grep "limiting requests"
```

##  Debugging Tools

### 1. Connexions actives
```bash
# Compter connexions TCP sur port 8000
ss -tln sport = :8000 | wc -l

# WebSocket connections (si exposé)
curl http://localhost/metrics | grep ws_connections
```

### 2. Processus et signaux
```bash
# Vérifier handlers SIGTERM
kill -TERM $(docker-compose ps -q backend)

# Logs détaillés
docker logs -f jarvis_backend
```

### 3. Memory leaks
```bash
# Avant test
docker stats --no-stream jarvis_backend

# Après cycles connexion/déconnexion
# → Mémoire ne doit pas augmenter indéfiniment
```

##  Checklist Finale

- [ ] **SIGTERM** : Logs `draining=true` → connexions `0` → services fermés
- [ ] **WebSocket** : Code `1001` existants, `1013` nouvelles connexions
- [ ] **Tasks** : Aucune exception `CancelledError` non gérée
- [ ] **Métriques** : `ws_active_connections` revient à `0`
- [ ] **Rate Limit** : `429` après seuils dépassés
- [ ] **Taille** : `413` pour messages > 4096 chars  
- [ ] **Timeouts** : Services indisponibles → retry → `503`
- [ ] **Nginx** : Pas d'erreurs `upstream closed` en cascade
- [ ] **Memory** : Pas de fuites après cycles connect/disconnect
- [ ] **Logs** : JSON structurés avec request-id (si implémenté)

---

**Status** :  PRODUCTION READY quand tous les points sont validés