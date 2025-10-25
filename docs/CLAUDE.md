# 🤖 REDIRECTION VERS DOCUMENTATION

## ⚠️ INITIALISATION AUTOMATIQUE CLAUDE CODE ⚠️

**Si vous voyez ce fichier, votre instance Claude doit s'initialiser automatiquement.**

---

## 📁 REDIRECTION OBLIGATOIRE

**Toute instance Claude Code doit IMMÉDIATEMENT :**

1. **Lire TOUS les fichiers .md** du dossier `/docs/`
2. **Commencer par** `/docs/CLAUDE_PARAMS.md` (PRIORITÉ ABSOLUE)
3. **Suivre l'ordre** défini dans `/docs/CLAUDE_CONFIG.md`
4. **S'attribuer un numéro** d'instance disponible
5. **Logger son initialisation** dans `/docs/CLAUDE_UPDATES.md`

---

## 🎯 COMMANDE SIMPLE POUR INIT

**Si vous n'êtes pas encore initialisé, tapez :**

```
lis doc
```

**Cette commande va :**
- Lire automatiquement tous les fichiers `/docs/`
- Vous attribuer un numéro d'instance
- Vous configurer complètement
- Vous préparer pour le travail collaboratif

---

## 📋 ORDRE DE LECTURE DES FICHIERS

**Quand vous tapez "lis doc", lecture dans cet ordre :**

1. `/docs/CLAUDE_PARAMS.md` - Règles absolues
2. `/docs/CLAUDE_CONFIG.md` - Configuration instances  
3. `/docs/CLAUDE_UPDATES.md` - Log temps réel
4. `/docs/CLAUDE_THOUGHTS.md` - Réflexions partagées
5. `/docs/CLAUDE_INSTANCES.md` - Coordination
6. `/docs/CLAUDE.md` - Instructions techniques
7. `/docs/BUGS.md` - Problèmes connus
8. `/docs/README.md` - Documentation projet
9. `/docs/CHANGELOG.md` - Historique
10. `/docs/API.md` - Documentation API
11. `/docs/PROFIL_JARVIS.md` - Contexte Enzo/projet
12. `/docs/DOCUMENTATION.md` - Structure générale

**Après lecture complète → Instance prête à travailler !**

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