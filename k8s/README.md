# 🚀 Jarvis Kubernetes Deployment

Migration complète de Docker Compose vers Kubernetes pour Jarvis V1.4.0

## 🎯 Architecture Kubernetes

### Services déployés
- **Frontend Interface** (port 30100)
- **Backend API** (port 30000) 
- **WebSocket** (port 30001)
- **TTS API** (port 30002)
- **STT API** (port 30003)
- **PostgreSQL** (base de données principale)
- **Redis** (cache)
- **Ollama** (LLM local)
- **Qdrant** (base vectorielle)
- **TimescaleDB** (métriques temporelles)
- **Prometheus** (monitoring, port 30090)
- **Grafana** (visualisation, port 30300)

## 🚀 Déploiement rapide

```bash
# Déployer tout automatiquement
cd k8s
./deploy.sh
```

## 📁 Structure des manifests

```
k8s/
├── 00-namespace.yaml          # Namespace + quotas
├── 01-storage.yaml            # PersistentVolumes + PVCs
├── 02-configmap-secrets.yaml  # Configuration + secrets
├── 03-postgres.yaml           # Base de données principale
├── 04-redis.yaml              # Cache Redis
├── 05-qdrant.yaml             # Base vectorielle
├── 06-timescale.yaml          # Base temporelle
├── 07-ollama.yaml             # LLM local + setup
├── 08-stt-api.yaml            # Speech-to-Text API
├── 09-tts-api.yaml            # Text-to-Speech API
├── 10-backend.yaml            # API Backend principale
├── 11-interface.yaml          # Interface frontend
├── 12-ingress.yaml            # Routage (nginx-ingress)
├── 13-monitoring.yaml         # Prometheus + Grafana
├── deploy.sh                  # Script déploiement auto
└── README.md                  # Ce fichier
```

## 🔧 Déploiement manuel

### 1. Prérequis
```bash
# Vérifier kubectl
kubectl version --client

# Vérifier cluster
kubectl cluster-info

# Build des images Docker locales
cd ../backend && docker build -t jarvis-backend:latest .
cd ../services/tts && docker build -t jarvis-tts:latest .
cd ../services/stt && docker build -t jarvis-stt:latest .
cd ../services/interface && docker build -t jarvis-interface:latest .
```

### 2. Stockage
```bash
# Créer répertoires stockage
sudo mkdir -p /var/lib/jarvis/{postgres,redis,ollama,qdrant,timescale}
sudo chown -R $USER:$USER /var/lib/jarvis

# Déployer namespace et stockage
kubectl apply -f 00-namespace.yaml
kubectl apply -f 01-storage.yaml
kubectl apply -f 02-configmap-secrets.yaml
```

### 3. Services de données
```bash
# Bases de données
kubectl apply -f 03-postgres.yaml
kubectl apply -f 04-redis.yaml
kubectl apply -f 05-qdrant.yaml
kubectl apply -f 06-timescale.yaml

# Attendre que tout soit prêt
kubectl wait --for=condition=available --timeout=300s deployment/jarvis-postgres -n jarvis
kubectl wait --for=condition=available --timeout=180s deployment/jarvis-redis -n jarvis
```

### 4. Ollama LLM
```bash
kubectl apply -f 07-ollama.yaml

# Attendre démarrage
kubectl wait --for=condition=available --timeout=300s deployment/jarvis-ollama -n jarvis

# Vérifier téléchargement modèles
kubectl logs job/jarvis-ollama-setup -n jarvis
```

### 5. APIs Jarvis
```bash
# Services API
kubectl apply -f 08-stt-api.yaml
kubectl apply -f 09-tts-api.yaml
kubectl apply -f 10-backend.yaml

# Attendre démarrage
kubectl wait --for=condition=available --timeout=240s deployment/jarvis-backend -n jarvis
```

### 6. Interface
```bash
kubectl apply -f 11-interface.yaml
kubectl wait --for=condition=available --timeout=180s deployment/jarvis-interface -n jarvis
```

### 7. Réseau et monitoring (optionnel)
```bash
# Ingress (nécessite nginx-ingress)
kubectl apply -f 12-ingress.yaml

# Monitoring
kubectl apply -f 13-monitoring.yaml
```

## 🌐 Accès aux services

| Service | URL | Description |
|---------|-----|-------------|
| Interface Jarvis | http://localhost:30100 | Interface utilisateur principale |
| Backend API | http://localhost:30000 | API REST principale |
| WebSocket | ws://localhost:30001 | WebSocket temps réel |
| TTS API | http://localhost:30002 | Text-to-Speech |
| STT API | http://localhost:30003 | Speech-to-Text |
| Prometheus | http://localhost:30090 | Monitoring métriques |
| Grafana | http://localhost:30300 | Visualisation (admin/jarvis123) |

### Avec Ingress (si configuré)
- https://jarvis.local - Interface principale
- https://api.jarvis.local - API backend
- https://qdrant.jarvis.local - Base vectorielle
- https://ollama.jarvis.local - LLM Ollama

## 📊 Monitoring et debugging

### État des pods
```bash
kubectl get pods -n jarvis -o wide
kubectl get svc -n jarvis
kubectl get pvc -n jarvis
```

### Logs en temps réel
```bash
# Backend
kubectl logs -f deployment/jarvis-backend -n jarvis

# Interface
kubectl logs -f deployment/jarvis-interface -n jarvis

# TTS/STT
kubectl logs -f deployment/jarvis-tts -n jarvis
kubectl logs -f deployment/jarvis-stt -n jarvis
```

### Shell dans un pod
```bash
kubectl exec -it deployment/jarvis-backend -n jarvis -- /bin/bash
```

### Monitoring continu
```bash
kubectl get pods -n jarvis -w
```

## 🔄 Configuration

### Variables d'environnement
Modifiez `02-configmap-secrets.yaml` pour ajuster :
- URLs des services
- Configuration Ollama
- Paramètres mémoire
- Credentials base de données

### Ressources
Ajustez les limites dans chaque manifest :
```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "2Gi"
    cpu: "1000m"
```

### Stockage
Modifiez `01-storage.yaml` pour ajuster :
- Taille des volumes
- Type de stockage (local/NFS/cloud)
- Chemins de stockage

## 🛠️ Scaling

### Augmenter replicas
```bash
kubectl scale deployment jarvis-backend --replicas=3 -n jarvis
kubectl scale deployment jarvis-interface --replicas=2 -n jarvis
```

### Horizontal Pod Autoscaler
```bash
kubectl autoscale deployment jarvis-backend --cpu-percent=70 --min=1 --max=5 -n jarvis
```

## 🧹 Nettoyage

### Arrêt temporaire
```bash
kubectl scale deployment --replicas=0 --all -n jarvis
```

### Suppression complète
```bash
kubectl delete namespace jarvis
sudo rm -rf /var/lib/jarvis
```

### Suppression images Docker
```bash
docker rmi jarvis-backend:latest
docker rmi jarvis-tts:latest  
docker rmi jarvis-stt:latest
docker rmi jarvis-interface:latest
```

## 🔧 Troubleshooting

### Pod en erreur
```bash
kubectl describe pod <pod-name> -n jarvis
kubectl logs <pod-name> -n jarvis --previous
```

### Service non accessible
```bash
kubectl get endpoints -n jarvis
kubectl port-forward svc/jarvis-backend 8000:8000 -n jarvis
```

### Stockage
```bash
kubectl get pv,pvc -n jarvis
kubectl describe pvc jarvis-postgres-pvc -n jarvis
```

### Réseau
```bash
kubectl get ingress -n jarvis
kubectl describe ingress jarvis-ingress -n jarvis
```

## 🆕 Mise à jour

### Nouvelles images
```bash
# Rebuild images
docker build -t jarvis-backend:v1.4.1 backend/

# Mise à jour deployment
kubectl set image deployment/jarvis-backend backend-api=jarvis-backend:v1.4.1 -n jarvis

# Rolling update automatique
kubectl rollout status deployment/jarvis-backend -n jarvis
```

### Configuration
```bash
# Mise à jour ConfigMap
kubectl apply -f 02-configmap-secrets.yaml

# Redémarrer deployments pour prendre en compte
kubectl rollout restart deployment/jarvis-backend -n jarvis
```

## 📈 Performance

- **CPU** : Optimisé pour 4-8 cœurs
- **RAM** : ~8-16GB selon charge
- **Stockage** : ~50GB minimum
- **Réseau** : Communication interne cluster optimisée

## 🔒 Sécurité

- Namespaces isolés
- Secrets chiffrés
- RBAC configuré
- Network policies (optionnel)
- TLS via cert-manager (optionnel)

## ✅ Tests de validation

```bash
# Test health checks
curl http://localhost:30000/health
curl http://localhost:30002/health
curl http://localhost:30003/health

# Test API complète
curl -X POST http://localhost:30000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Bonjour Jarvis"}'
```

## 📞 Support

- Logs : `kubectl logs -f deployment/jarvis-backend -n jarvis`
- Status : `kubectl get all -n jarvis`
- Events : `kubectl get events -n jarvis --sort-by=.metadata.creationTimestamp`