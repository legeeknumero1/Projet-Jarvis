# 🤖 Coordination Multi-Instances Claude - Projet Jarvis

## ⚠️ SYSTÈME DE COORDINATION MULTI-INSTANCES ⚠️

**Ce fichier permet à plusieurs instances Claude Code de travailler simultanément sur le même projet sans conflits.**

---

## 🎯 État actuel du projet

### 📊 Instances actives
- **Instance #1** : ACTIVE - CONTRÔLE TOTAL UNIQUE ✅ (2025-07-21)
- **Instance #2-#11** : TERMINÉES - Toutes instances fermées et consolidées

### 🔄 Dernière synchronisation
**Date** : 2025-01-17 - 18:06
**Par** : Instance #2
**Action** : Détection et synchronisation avec Instance #1 - Chat vocal IA fonctionnel !

---

## 📋 Protocole de coordination OBLIGATOIRE

### 🔴 AVANT TOUTE ACTION - LECTURE OBLIGATOIRE

1. **LIRE** ce fichier `CLAUDE_INSTANCES.md` EN PREMIER
2. **VÉRIFIER** si une autre instance travaille déjà sur la même tâche
3. **DÉCLARER** son intention de travail dans la section "Réservations"
4. **ATTENDRE** 30 secondes avant de commencer (éviter conflits)
5. **METTRE À JOUR** ce fichier après chaque action importante

### 🎯 Règles de collaboration

1. **UNE TÂCHE = UNE INSTANCE** : Éviter le travail simultané sur le même fichier
2. **COMMUNICATION ASYNCHRONE** : Utiliser ce fichier pour communiquer
3. **MISE À JOUR OBLIGATOIRE** : Toujours mettre à jour après action
4. **RESPECT DES RÉSERVATIONS** : Ne pas travailler sur une tâche réservée
5. **HANDOVER PROPRE** : Documenter clairement quand on termine une tâche

---

## 🔒 Réservations de tâches

### Tâches en cours
```
[RÉSERVÉ] Instance #1 - Finalisation complète projet Jarvis - Début: 19:40
```

### Tâches restantes à terminer
```
[EN_COURS] Résolution bugs restants (BUG-020, BUG-021, BUG-023-026)
[EN_COURS] Tests unitaires complets
[EN_COURS] Documentation API mise à jour
[EN_COURS] Nettoyage code (imports, commentaires)
[EN_COURS] Finalisation V1 complète
```

---

## 📝 Réservation de tâche (TEMPLATE)

**Pour réserver une tâche, copier ce template :**

```
[RÉSERVÉ] Instance #X - [Nom de la tâche] - Début: HH:MM
Estimation: XX minutes
Fichiers concernés: [liste des fichiers]
```

**Quand terminé, remplacer par :**
```
[TERMINÉ] Instance #X - [Nom de la tâche] - Fini: HH:MM
Résultat: [Succès/Échec/Partiel]
Prochaine étape: [Action suivante recommandée]
```

---

## 🔄 Log d'activité temps réel

### 18:00 - Instance #2
- **Action** : Création CLAUDE_INSTANCES.md
- **Statut** : EN COURS
- **Fichiers** : docs/CLAUDE_INSTANCES.md

### [Template pour nouvelles entrées]
```
### HH:MM - Instance #X
- **Action** : [Description de l'action]
- **Statut** : [EN COURS/TERMINÉ/BLOQUÉ]
- **Fichiers** : [liste des fichiers modifiés]
- **Remarques** : [Notes importantes]
```

---

## 🛠️ Configuration Git (recommandée)

### Initialisation recommandée
```bash
# Si pas encore fait
git init
git add .
git commit -m "Initial commit - Base projet Jarvis"

# Création branche de développement
git checkout -b development
```

### Workflow multi-instances
```bash
# Avant de commencer à travailler
git pull origin development
git checkout -b feature/nom-instance-X

# Pendant le travail
git add .
git commit -m "Instance X: [description]"

# Après le travail
git push origin feature/nom-instance-X
# Puis merge via PR/MR
```

---

## 🔍 Détection de conflits

### Vérifications automatiques
- **Avant modification** : Vérifier si le fichier n'est pas réservé
- **Pendant travail** : Mettre à jour ce fichier toutes les 15 minutes
- **Après modification** : Documenter tous les changements

### Résolution de conflits
1. **Communication** : Documenter le conflit dans ce fichier
2. **Négociation** : Définir qui continue quelle tâche
3. **Merge intelligent** : Fusionner les modifications sans perte
4. **Test** : Vérifier que tout fonctionne après résolution

---

## 📊 État des composants

### Backend (FastAPI)
- **main.py** : ✅ Fonctionnel
- **config/** : ✅ Configuré
- **db/** : ✅ PostgreSQL opérationnel
- **memory/** : 🔄 En développement
- **speech/** : 🔄 En développement
- **integration/** : 🔄 En développement

### Frontend (React)
- **Structure** : ✅ Créée
- **Composants** : 🔄 En développement
- **Services** : 🔄 En développement

### Infrastructure
- **Docker** : ✅ Configuré
- **PostgreSQL** : ✅ Opérationnel
- **Ollama** : ✅ Fonctionnel (LLaMA 3.1)
- **Whisper** : ✅ Installé
- **Piper** : ✅ Installé

---

## 🎯 Priorités de développement

### P1 - CRITIQUE (à faire en premier)
1. Reconnaissance vocale Whisper
2. Synthèse vocale Piper
3. Intégration Ollama complète

### P2 - IMPORTANT
1. Connexion Home Assistant
2. Interface domotique frontend
3. Système de mémoire contextuelle

### P3 - NORMAL
1. Tests automatisés
2. Documentation complète
3. Optimisations performance

---

## 🔄 Handover entre instances

### Template de handover
```
### HANDOVER Instance #X → Instance #Y
**Tâche** : [Nom de la tâche]
**État** : [% completion]
**Fichiers modifiés** : [liste]
**Prochaines étapes** : [actions à faire]
**Blocages** : [problèmes rencontrés]
**Notes** : [informations importantes]
```

---

## 🚨 Urgences et blocages

### Signaler un blocage
```
🚨 BLOCAGE - Instance #X - HH:MM
Tâche: [nom]
Problème: [description]
Aide nécessaire: [type d'aide]
```

### Demander assistance
```
🆘 ASSISTANCE - Instance #X - HH:MM
Besoin: [description]
Expertise: [domaine requis]
Urgence: [haute/moyenne/basse]
```

---

## 🔄 Dernière mise à jour
**Date** : 2025-01-17 - 18:00
**Par** : Instance #2 (Claude)
**Action** : Création du système de coordination multi-instances

---

## 📝 Notes importantes

- **Ce fichier est la SOURCE DE VÉRITÉ** pour la coordination
- **Mettre à jour OBLIGATOIRE** après chaque action
- **Respecter les réservations** pour éviter les conflits
- **Communiquer clairement** via ce fichier
- **Tester avant de terminer** une tâche