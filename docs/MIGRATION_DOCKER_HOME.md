# 🚚 Migration Docker vers /home - Procédure Complète

## ⚠️ PROBLÈME IDENTIFIÉ
- **Root partition** : 120GB seulement → **SATURÉ** par Docker
- **Docker data** : `/var/lib/docker` sur partition root
- **Solution** : Migrer Docker vers `/home` (plus d'espace)

---

## 🎯 OBJECTIF
Déplacer toutes les données Docker de `/var/lib/docker` vers `/home/enzo/jarvis-docker/`

---

## 📋 PROCÉDURE DE MIGRATION (à exécuter par Enzo)

### 1. Arrêter Docker complètement
```bash
# Arrêter tous les containers
docker stop $(docker ps -aq)

# Arrêter le service Docker
sudo systemctl stop docker
sudo systemctl stop docker.socket
```

### 2. Vérifier l'espace utilisé
```bash
# Voir l'espace total Docker
sudo du -sh /var/lib/docker

# Voir l'espace libre sur /home
df -h /home
```

### 3. Créer le nouveau répertoire Docker
```bash
# Créer le dossier de destination
sudo mkdir -p /home/enzo/jarvis-docker
sudo chown enzo:enzo /home/enzo/jarvis-docker
```

### 4. Déplacer les données Docker
```bash
# Copier toutes les données Docker
sudo rsync -aP /var/lib/docker/ /home/enzo/jarvis-docker/

# Vérifier la copie
sudo du -sh /home/enzo/jarvis-docker
```

### 5. Configurer Docker pour le nouveau chemin
```bash
# Créer/éditer le fichier de configuration Docker
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json << EOF
{
  "data-root": "/home/enzo/jarvis-docker",
  "storage-driver": "overlay2"
}
EOF
```

### 6. Sauvegarder l'ancien répertoire (sécurité)
```bash
# Renommer l'ancien répertoire (ne pas supprimer tout de suite)
sudo mv /var/lib/docker /var/lib/docker.backup
```

### 7. Redémarrer Docker
```bash
# Redémarrer le service Docker
sudo systemctl start docker
sudo systemctl enable docker

# Vérifier que Docker utilise le nouveau chemin
docker info | grep "Docker Root Dir"
```

### 8. Vérifier que tout fonctionne
```bash
# Lister les images (doivent être présentes)
docker images

# Lister les volumes (doivent être présents)
docker volume ls

# Lister les réseaux
docker network ls
```

### 9. Reconstruire l'architecture Jarvis
```bash
cd "/home/enzo/Documents/Projet Jarvis"

# Rebuilder avec plus d'espace
docker build -t jarvis_backend ./backend
docker build -t jarvis_interface ./services/interface

# Relancer l'architecture complète
./start_jarvis_docker.sh
```

### 10. Nettoyage final (APRÈS VÉRIFICATION)
```bash
# Une fois que tout fonctionne, supprimer l'ancien répertoire
sudo rm -rf /var/lib/docker.backup
```

---

## 🔧 AVANTAGES DE CETTE MIGRATION

### Espace disque
- **Avant** : Docker limité à 120GB (root partition)
- **Après** : Docker sur partition /home (plus d'espace)
- **Gain** : Place pour tous les modèles IA + containers

### Performance
- **Meilleure gestion** de l'espace disque
- **Évite la saturation** de la partition root
- **Builds Docker** plus rapides

### Maintenance
- **Sauvegarde facile** du dossier `/home/enzo/jarvis-docker`
- **Gestion centralisée** des données Jarvis
- **Moins de risques** de corruption système

---

## 🚨 POINTS D'ATTENTION

### Permissions
- S'assurer que `enzo` a les bonnes permissions sur `/home/enzo/jarvis-docker`
- Docker daemon doit pouvoir écrire dans le nouveau répertoire

### Espace disque
- Vérifier qu'il y a assez d'espace sur `/home` avant la migration
- Prévoir 2x l'espace Docker actuel (copie + original temporaire)

### Sécurité
- Ne PAS supprimer `/var/lib/docker.backup` avant validation complète
- Tester tous les containers après migration

---

## 📊 ESTIMATION TEMPS & ESPACE

### Temps de migration
- **Arrêt Docker** : 1 minute
- **Copie données** : 10-30 minutes (selon taille)
- **Configuration** : 5 minutes
- **Tests** : 10 minutes
- **TOTAL** : ~1 heure

### Espace requis
- **Docker actuel** : ~15-20GB estimé
- **Espace libre nécessaire** : 40GB minimum sur /home
- **Après nettoyage** : Libération complète de la partition root

---

## ✅ VALIDATION FINALE

### Checklist post-migration
- [ ] `docker info` montre le nouveau chemin
- [ ] Tous les containers redémarrent
- [ ] Architecture Jarvis 7/7 opérationnelle
- [ ] Espace libéré sur partition root
- [ ] Builds Docker réussissent

---

**📝 Créé par Instance #21 - 2025-07-31 15:45**
**🎯 Procédure critique pour débloquer l'architecture Docker complète**