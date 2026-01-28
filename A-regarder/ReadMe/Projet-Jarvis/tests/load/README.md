# Load Testing Suite - Jarvis v1.9.0

Suite complète de tests de charge pour l'API Jarvis utilisant K6 et Locust.

## Vue d'ensemble

Ce répertoire contient des tests de charge pour:
- Chat API (POST /api/chat, conversations, memory)
- Voice API (TTS, STT)
- Workflows complets (combinaisons d'endpoints)

## Outils

### K6 (Recommandé pour CI/CD)
- **Avantages**: Rapide, scriptable en JavaScript, intégration Prometheus/Grafana
- **Cas d'usage**: Tests automatisés, CI/CD, monitoring continu
- **Installation**: https://k6.io/docs/get-started/installation/

### Locust (Recommandé pour tests interactifs)
- **Avantages**: Interface Web, Python, simulation réaliste d'utilisateurs
- **Cas d'usage**: Tests exploratoires, ajustement en temps réel
- **Installation**: `pip install locust`

## Structure

```
tests/load/
 k6/
    chat-api.js          # Test Chat API
    voice-api.js         # Test Voice API
    run-all-tests.sh     # Script pour lancer tous les tests K6
    results/             # Résultats JSON
 locust/
    chat_api.py          # Test Chat API
    voice_api.py         # Test Voice API
    run-locust.sh        # Script pour lancer Locust
    results/             # Rapports HTML/CSV
 README.md
```

## Quick Start

### Prérequis

1. **Démarrer l'API Jarvis**:
```bash
cd ../..
docker-compose up -d
```

2. **Vérifier que l'API répond**:
```bash
curl http://localhost:8100/health
```

### K6 Tests

#### Installation K6
```bash
# macOS
brew install k6

# Linux
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6

# Windows (via Chocolatey)
choco install k6
```

#### Lancer les tests K6

**Test Chat API uniquement**:
```bash
cd k6
k6 run chat-api.js
```

**Test Voice API uniquement**:
```bash
cd k6
k6 run voice-api.js
```

**Tous les tests K6**:
```bash
cd k6
chmod +x run-all-tests.sh
./run-all-tests.sh
```

**Personnaliser l'URL de l'API**:
```bash
export API_URL=http://production.example.com:8100
./run-all-tests.sh
```

#### Résultats K6

Les résultats sont sauvegardés dans `k6/results/`:
- `chat-api-YYYYMMDD-HHMMSS.json` - Données brutes
- `chat-api-summary-YYYYMMDD-HHMMSS.json` - Résumé

**Métriques K6**:
- `http_req_duration`: Latence des requêtes (p50, p95, p99)
- `http_req_failed`: Taux d'erreur
- `iterations`: Nombre d'itérations complétées
- `chat_latency`: Latence spécifique Chat API
- `tts_latency`: Latence Text-to-Speech
- `stt_latency`: Latence Speech-to-Text

### Locust Tests

#### Installation Locust
```bash
pip install locust
```

#### Lancer Locust

**Mode Web UI (interactif)**:
```bash
cd locust
chmod +x run-locust.sh
./run-locust.sh
# Sélectionner 1 (Chat API) ou 2 (Voice API)
# Ouvrir http://localhost:8089
```

**Mode Headless (automatique)**:
```bash
cd locust
MODE=headless USERS=100 SPAWN_RATE=10 RUN_TIME=5m ./run-locust.sh
```

**Lancer directement**:
```bash
cd locust
locust -f chat_api.py --host=http://localhost:8100
```

#### Résultats Locust

Les résultats sont sauvegardés dans `locust/results/`:
- `locust-report-YYYYMMDD-HHMMSS.html` - Rapport HTML avec graphiques
- `locust-stats-YYYYMMDD-HHMMSS_stats.csv` - Statistiques par endpoint
- `locust-stats-YYYYMMDD-HHMMSS_failures.csv` - Liste des erreurs

## Scénarios de Test

### K6 Chat API (chat-api.js)

**Profil de charge**:
- 0-30s: Montée à 10 utilisateurs
- 30s-1m30s: Montée à 50 utilisateurs
- 1m30s-3m30s: Maintien à 50 utilisateurs
- 3m30s-4m: Pic à 100 utilisateurs
- 4m-5m: Maintien à 100 utilisateurs
- 5m-5m30s: Descente à 0

**Tests effectués**:
1. Health check
2. Envoi message chat
3. Liste conversations
4. Recherche mémoire

**Seuils de succès**:
- p95 latency < 500ms
- p99 latency < 1000ms
- Taux d'erreur < 1%

### K6 Voice API (voice-api.js)

**Profil de charge**:
- 0-30s: Montée à 5 utilisateurs
- 30s-1m30s: Montée à 20 utilisateurs
- 1m30s-3m30s: Maintien à 20 utilisateurs
- 3m30s-4m: Descente à 0

**Tests effectués**:
1. Text-to-Speech (TTS)
2. Speech-to-Text (STT)

**Seuils de succès**:
- p95 TTS latency < 1500ms
- p95 STT latency < 2000ms
- Taux d'erreur < 5%

### Locust Chat API (chat_api.py)

**Tâches pondérées**:
- `send_chat_message`: Poids 5 (tâche la plus fréquente)
- `list_conversations`: Poids 3
- `search_memory`: Poids 2
- `create_conversation`: Poids 1
- `health_check`: Poids 1

**Vérifications**:
- Validation JSON response
- Vérification des champs obligatoires
- Alertes si latence > seuils

### Locust Voice API (voice_api.py)

**Tâches pondérées**:
- `synthesize_speech`: Poids 5 (TTS)
- `transcribe_speech`: Poids 3 (STT)
- `combined_voice_workflow`: Poids 1 (TTS → STT)

**Vérifications**:
- Validation audio_data base64
- Confiance STT > 50%
- Durée TTS/STT raisonnable

## Objectifs de Performance

| Endpoint | p95 Latency | p99 Latency | Taux Erreur | RPS (100 users) |
|----------|-------------|-------------|-------------|-----------------|
| POST /api/chat | < 300ms | < 500ms | < 1% | > 50 |
| GET /api/chat/conversations | < 100ms | < 200ms | < 1% | > 100 |
| GET /api/memory/search | < 200ms | < 400ms | < 2% | > 80 |
| POST /api/voice/synthesize | < 1500ms | < 2500ms | < 5% | > 10 |
| POST /api/voice/transcribe | < 2000ms | < 3000ms | < 5% | > 8 |

## Analyse des Résultats

### K6 - Ligne de commande

Les résultats sont affichés dans le terminal:

```
 http_req_duration..............: avg=250ms min=50ms med=200ms max=1.2s p(95)=450ms p(99)=800ms
 http_req_failed................: 0.5%  10  1990
 iterations.....................: 2000 (40/s)
```

### Locust - Interface Web

1. Ouvrir http://localhost:8089
2. Entrer nombre d'utilisateurs et spawn rate
3. Observer graphiques en temps réel:
   - Total Requests per Second
   - Response Times (ms)
   - Number of Users

### Grafana Dashboard (Avancé)

Importer les résultats K6 dans Prometheus/Grafana:

```bash
# Exporter vers InfluxDB
k6 run --out influxdb=http://localhost:8086/k6 chat-api.js

# Ou exporter vers format Prometheus
k6 run --out experimental-prometheus-rw chat-api.js
```

## Troubleshooting

### Erreur: "Cannot connect to API"

**Solution**:
```bash
# Vérifier que l'API est démarrée
docker-compose ps

# Vérifier santé
curl http://localhost:8100/health

# Redémarrer si nécessaire
docker-compose restart backend
```

### Erreur: "Rate limit exceeded"

**Solution**: Ajuster les rate limits dans `core/src/middleware/rate_limit.rs`:

```rust
const MAX_REQUESTS_PER_MINUTE: u32 = 100; // Augmenter cette valeur
```

### Performances dégradées

**Diagnostic**:
1. Vérifier les métriques Prometheus: http://localhost:9090
2. Vérifier les dashboards Grafana: http://localhost:3001
3. Vérifier les logs: `docker-compose logs -f backend`

**Solutions courantes**:
- Augmenter ressources Docker (CPU/RAM)
- Optimiser queries PostgreSQL (index, EXPLAIN ANALYZE)
- Augmenter pool de connexions Redis/PostgreSQL
- Activer cache pour endpoints fréquents

## Intégration CI/CD

### GitHub Actions

Ajouter à `.github/workflows/ci.yml`:

```yaml
load-test:
  name: Load Tests
  runs-on: ubuntu-latest
  needs: [deploy-staging]
  steps:
    - uses: actions/checkout@v4

    - name: Install K6
      run: |
        sudo gpg -k
        sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
        echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
        sudo apt-get update
        sudo apt-get install k6

    - name: Run Load Tests
      env:
        API_URL: https://staging.jarvis.example.com
      run: |
        cd tests/load/k6
        ./run-all-tests.sh

    - name: Upload Results
      uses: actions/upload-artifact@v3
      with:
        name: load-test-results
        path: tests/load/k6/results/
```

## Best Practices

1. **Démarrer petit**: Commencer avec 10 utilisateurs, augmenter progressivement
2. **Tester en staging**: Ne jamais lancer de tests de charge en production sans autorisation
3. **Surveiller les ressources**: Observer CPU/RAM/Disk pendant les tests
4. **Itérer**: Analyser résultats → optimiser → re-tester
5. **Documenter**: Noter les résultats et changements pour comparaison

## Ressources

- K6 Documentation: https://k6.io/docs/
- Locust Documentation: https://docs.locust.io/
- Performance Best Practices: https://k6.io/docs/testing-guides/performance-testing/
- Jarvis API Examples: `../../docs/API_EXAMPLES.md`

## Support

Pour toute question ou problème:
1. Consulter la documentation Jarvis: `../../docs/`
2. Vérifier les logs: `docker-compose logs`
3. Analyser les métriques Grafana: http://localhost:3001
