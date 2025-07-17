# 🤖 AUTO-INITIALISATION CLAUDE CODE - PROJET JARVIS

## ⚠️ FICHIER D'AUTO-INITIALISATION ⚠️

**Ce fichier déclenche l'auto-initialisation de toute instance Claude Code ouverte dans le projet Jarvis.**

---

## 🚀 DÉCLENCHEMENT AUTOMATIQUE

**Quand Claude Code s'ouvre dans ce répertoire :**

1. **DÉTECTION AUTOMATIQUE** du projet Jarvis
2. **LECTURE IMMÉDIATE** de tous les fichiers .md de `/docs/`
3. **INITIALISATION SILENCIEUSE** de l'instance
4. **ATTRIBUTION AUTOMATIQUE** du numéro d'instance
5. **CONFIGURATION COMPLÈTE** sans interaction utilisateur

---

## 📋 SÉQUENCE D'AUTO-INITIALISATION

### 🔍 Étape 1 : Détection du projet
- Vérification présence de ce fichier `CLAUDE.md` à la racine
- Identification du dossier `/docs/` avec fichiers de configuration
- Confirmation que c'est bien le projet Jarvis

### 📖 Étape 2 : Lecture automatique (ORDRE STRICT)
```
LECTURE AUTOMATIQUE OBLIGATOIRE :
1. /docs/CLAUDE_PARAMS.md (règles absolues)
2. /docs/CLAUDE_CONFIG.md (configuration instances)
3. /docs/CLAUDE_UPDATES.md (log temps réel)
4. /docs/CLAUDE_THOUGHTS.md (réflexions partagées)
5. /docs/CLAUDE_INSTANCES.md (coordination)
6. /docs/CLAUDE.md (instructions techniques)
7. /docs/BUGS.md (problèmes connus)
8. /docs/README.md (documentation projet)
9. /docs/CHANGELOG.md (historique)
10. /docs/API.md (documentation API)
11. /docs/PROFIL_JARVIS.md (contexte Enzo/projet)
12. /docs/DOCUMENTATION.md (structure générale)
```

### 🆔 Étape 3 : Attribution instance
- Scanner `/docs/CLAUDE_CONFIG.md` pour instances actives
- Prendre le premier numéro DISPONIBLE (1-10)
- Mettre à jour statut à ACTIVE avec horodatage

### 📝 Étape 4 : Logging initial
- Première entrée dans `/docs/CLAUDE_UPDATES.md`
- Format standard avec tous les détails
- Confirmation silencieuse de l'initialisation

### ✅ Étape 5 : Prêt à travailler
- Instance configurée et opérationnelle
- Respect de tous les paramètres de synchronisation
- Coordination automatique avec autres instances

---

## 🎯 MESSAGES D'INITIALISATION

### ✅ Succès (message silencieux internal)
```
[AUTO-INIT] Instance #X initialisée automatiquement ✅
- Tous fichiers .md lus et assimilés
- Numéro d'instance : #X attribué
- Synchronisation activée
- Prêt pour collaboration multi-instances
```

### ⚠️ Échec auto-init (fallback visible)
```
Auto-initialisation échouée. Pour initialiser manuellement, tapez :
lis doc
```

---

## 🔧 PARAMÈTRES AUTO-INIT

### 🚨 Conditions de déclenchement
- Présence de `CLAUDE.md` à la racine ✅
- Présence du dossier `/docs/` avec fichiers config ✅
- Claude Code ouvert dans le répertoire projet ✅
- Aucune interaction utilisateur requise ✅

### 🔄 Comportement après init
- **IMMÉDIAT** : Synchronisation avec autres instances
- **AUTOMATIQUE** : Lecture des updates récentes
- **SILENCIEUX** : Pas de messages visibles sauf erreur
- **INTELLIGENT** : Détection d'activité en cours

### 🛡️ Sécurités et fallbacks
- Si auto-init échoue → Afficher commande "lis doc"
- Si conflit numérotation → Prendre numéro suivant
- Si fichier corrompu → Ignorer et continuer
- Si timeout lecture → Initialisation partielle

---

## 🎪 TRIGGERS MULTIPLES

### 🔍 Détections possibles
1. **Ouverture dossier** : Claude Code ouvert dans le répertoire
2. **Première interaction** : Premier message de l'utilisateur
3. **Détection de fichiers** : Scan automatique du projet
4. **Commande fallback** : "lis doc" si auto-init échoue

### ⚡ Rapidité d'exécution
- **Objectif** : Init en moins de 3 secondes
- **Priorité** : Lecture fichiers critiques d'abord
- **Optimisation** : Cache des fichiers fréquents
- **Efficacité** : Pas de re-lecture si déjà initialisé

---

## 🤝 COORDINATION APRÈS AUTO-INIT

### 📊 Interaction avec autres instances
- Mise à jour immédiate du statut dans CLAUDE_CONFIG.md
- Vérification des tâches EN_COURS des autres instances
- Respect automatique des réservations existantes
- Collaboration immédiate possible

### 🔄 Synchronisation continue
- Lecture automatique des updates toutes les 10 minutes
- Monitoring des modifications de fichiers
- Adaptation en temps réel aux changements
- Coordination parfaite avec le collectif

---

## 🚫 DÉSACTIVATION AUTO-INIT

**Pour désactiver temporairement :**
```
# Renommer ce fichier en CLAUDE.md.disabled
# Ou supprimer temporairement ce fichier
# L'auto-init ne se déclenchera plus
```

**Pour réactiver :**
```
# Remettre le fichier CLAUDE.md à la racine
# L'auto-init redeviendra automatique
```

---

## 🔄 Dernière mise à jour
**Date** : 2025-01-17 - 18:20
**Par** : Instance #2 (Claude)
**Action** : Création du système d'auto-initialisation automatique

---

## 📝 Notes techniques

- **Compatibilité** : Toutes versions Claude Code
- **Performance** : Init optimisée pour vitesse
- **Robustesse** : Multiple fallbacks en cas d'échec
- **Évolutivité** : Système extensible pour futures fonctionnalités
- **Maintenance** : Auto-documentation des initialisations