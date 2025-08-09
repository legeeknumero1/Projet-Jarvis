# 👤 Guide Utilisateur - Jarvis

## 🎯 Qu'est-ce que Jarvis ?

Jarvis est votre assistant personnel intelligent qui peut :
- 🎤 Vous écouter et vous répondre par la voix
- 🏠 Contrôler votre domotique (lumières, chauffage, etc.)
- 🤖 Discuter intelligemment grâce à l'IA locale
- 📝 Se souvenir de vos préférences et conversations

## 🚀 Premier Démarrage

### 1. Installation
```bash
git clone https://github.com/username/Projet-Jarvis.git
cd Projet-Jarvis
./start_jarvis_docker.sh
```

### 2. Accès
- **Interface web** : `http://localhost:3000`
- **API** : `http://localhost:8000`

### 3. Premier test
1. Ouvrez `http://localhost:3000`
2. Tapez "Bonjour Jarvis" dans le chat
3. Cliquez sur 🎤 pour parler à Jarvis

## 💬 Comment Utiliser Jarvis

### Chat Textuel
- **Tapez** votre message dans la zone de texte
- **Appuyez** sur Entrée ou cliquez "Envoyer"  
- **Jarvis répond** instantanément

### Chat Vocal  
- **Cliquez** sur l'icône 🎤 microphone
- **Parlez** clairement votre question
- **Le texte** s'affiche automatiquement
- **Jarvis** vous répond par écrit et (bientôt) par la voix

### Exemples de Questions

#### 💭 Discussion Générale
- "Bonjour Jarvis, comment ça va ?"
- "Explique-moi le machine learning"  
- "Raconte-moi une blague"
- "Quel temps fait-il ?"

#### 🏠 Commandes Domotique *(à venir)*
- "Allume la lumière du salon"
- "Éteins toutes les lumières"
- "Règle la température à 20°C"
- "Active le mode nuit"

#### 📅 Gestion Personnelle *(à venir)*
- "Rappelle-moi RDV dentiste demain 15h"
- "Quels sont mes rendez-vous ?"
- "Ajoute lait à ma liste de courses"

## 🧠 Mémoire de Jarvis

Jarvis se souvient :
- ✅ **Vos conversations** précédentes
- ✅ **Vos préférences** personnelles  
- ✅ **Informations importantes** que vous partagez
- ✅ **Contexte** de vos discussions

### Gérer la Mémoire
- **"Oublie ce que j'ai dit"** - Effacer contexte récent
- **"Dis-moi ce dont tu te souviens"** - Lister souvenirs
- **"Sauvegarde ça en mémoire"** - Mémoriser info importante

## 🔧 Problèmes Courants

### Jarvis ne répond pas
1. ✅ Vérifiez `http://localhost:8000/health`
2. ✅ Rechargez la page `http://localhost:3000`  
3. ✅ Redémarrez : `docker-compose restart`

### Microphone ne marche pas
1. ✅ Autorisez le microphone dans votre navigateur
2. ✅ Vérifiez que votre micro fonctionne
3. ✅ Utilisez Chrome/Firefox (Safari non testé)

### Réponses lentes
1. ✅ Normal au premier démarrage (modèles qui chargent)
2. ✅ Attendez 1-2 minutes puis re-essayez
3. ✅ Vérifiez RAM disponible (8GB minimum)

### "Container non démarré"
1. ✅ Exécutez la migration Docker :
```bash
sudo systemctl stop docker
sudo rsync -aP /var/lib/docker/ /home/$USER/jarvis-docker/
# Voir docs/MIGRATION_DOCKER_HOME.md pour procédure complète
```

## ⚙️ Configuration

### Variables Utilisateur
Éditez le fichier `.env` pour :
- Changer le nom d'utilisateur par défaut
- Configurer Home Assistant (URL + token)  
- Ajuster modèles IA utilisés

### Home Assistant *(optionnel)*
1. Récupérez votre token Home Assistant
2. Ajoutez dans `.env` :
   ```
   HOME_ASSISTANT_URL=http://votre-ip:8123
   HOME_ASSISTANT_TOKEN=votre_token
   ```
3. Redémarrez Jarvis

## 🎛️ Interface Web

### Zones Principales
- **💬 Chat** : Zone de conversation  
- **🎤 Micro** : Activation reconnaissance vocale
- **⚙️ Paramètres** : Configuration utilisateur
- **📊 Statut** : État des services Jarvis

### Raccourcis Clavier
- **Entrée** : Envoyer message
- **Ctrl+/** : Activer/désactiver micro  
- **Échap** : Effacer message en cours

## 🆘 Support

### Documentation Technique  
- **[Architecture](ARCHITECTURE_DOCKER.md)** - Comment ça marche
- **[API](API.md)** - Endpoints développeur  
- **[Bugs](BUGS.md)** - Problèmes connus

### Dépannage Avancé
```bash
# Logs détaillés
docker logs jarvis_backend
docker logs jarvis_interface

# État des services  
docker ps
curl http://localhost:8000/health

# Redémarrage complet
docker-compose down && docker-compose up -d
```

---

## 🎉 Profitez de Jarvis !

Jarvis apprend de vos interactions et devient plus utile avec le temps. N'hésitez pas à lui parler naturellement et à explorer ses capacités !

**Questions ? Consultez la [documentation technique](DOCUMENTATION.md) ou [signalez un bug](BUGS.md)**

---

**Dernière mise à jour** : Instance #22 - 2025-08-09