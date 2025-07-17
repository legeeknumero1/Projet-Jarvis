# 📋 Changelog - Projet Jarvis

## Format
- **[AJOUTÉ]** : Nouvelles fonctionnalités
- **[MODIFIÉ]** : Modifications de fonctionnalités existantes
- **[CORRIGÉ]** : Corrections de bugs
- **[SUPPRIMÉ]** : Fonctionnalités supprimées
- **[SÉCURITÉ]** : Améliorations de sécurité

---

## [1.0.0] - 2025-01-17

### [AJOUTÉ]
- **17:25** - Ajout des règles d'ingénieur expert dans CLAUDE_PARAMS.md
- **17:25** - Ajout du comportement de précision extrême et intolérance aux erreurs
- **17:25** - Ajout de l'auto-analyse et de la remise en question systématique
- **17:25** - Ajout de la mémoire contextuelle et de l'anticipation des besoins
- **17:25** - Ajout des protections de sécurité avancées (log complet, confirmation critique)
- **17:20** - Ajout des règles anti-duplication dans CLAUDE_PARAMS.md
- **17:20** - Ajout du système de détection et optimisation des doublons
- **17:20** - Ajout des règles de nommage cohérent des fichiers
- **17:15** - Création du fichier CLAUDE_PARAMS.md (PRIORITÉ ABSOLUE)
- **17:15** - Ajout du système de confirmation obligatoire pour suppressions
- **17:15** - Mise à jour du workflow avec CLAUDE_PARAMS.md en premier
- **17:10** - Création du système de documentation structuré dans `/docs/`
- **17:10** - Ajout du registre des bugs (BUGS.md) avec 3 bugs identifiés
- **17:10** - Ajout du changelog (CHANGELOG.md)
- **17:10** - Ajout de la documentation API (API.md)
- **17:10** - Création du fichier DOCUMENTATION.md à la racine
- **16:45** - Intégration client Ollama pour LLM local
- **16:30** - Configuration Docker Compose complète
- **16:20** - Installation Piper TTS (partielle)
- **16:00** - Installation dépendances Python de base
- **15:45** - Création architecture frontend React
- **15:30** - Configuration base de données PostgreSQL
- **15:15** - Création architecture backend FastAPI
- **15:00** - Initialisation du projet et structure des dossiers

### [MODIFIÉ]
- **17:15** - Mise à jour DOCUMENTATION.md avec référence prioritaire à CLAUDE_PARAMS.md
- **17:15** - Mise à jour CLAUDE.md avec CLAUDE_PARAMS.md en premier dans workflow
- **17:10** - Mise à jour CLAUDE.md avec workflow obligatoire incluant BUGS.md
- **17:10** - Déplacement des fichiers .md vers `/docs/`
- **16:30** - Mise à jour requirements.txt (suppression psycopg2-binary)
- **16:15** - Simplification des versions dans requirements.txt

### [CORRIGÉ]
- **17:35** - BUG-003 RÉSOLU : Piper TTS adapté pour module Python
- **17:32** - BUG-002 RÉSOLU : Ollama installé via Docker + LLaMA 3.1 fonctionnel
- **17:30** - BUG-001 RÉSOLU : Whisper installé depuis GitHub (Python 3.13 compatible)
- **16:30** - Contournement du problème psycopg2-binary
- **16:00** - Résolution des conflits de versions Python

### [PROBLÈMES CONNUS]
- ✅ ~~Installation Ollama requiert privilèges sudo~~ RÉSOLU
- ✅ ~~Piper TTS non accessible via PATH~~ RÉSOLU
- ✅ ~~Whisper non installé (compatibilité Python 3.13)~~ RÉSOLU

**Tous les problèmes critiques ont été résolus !**

---

## 🔄 Prochaines versions

### [1.1.0] - Planifié
- **[AJOUTÉ]** : Reconnaissance vocale Whisper fonctionnelle
- **[AJOUTÉ]** : Synthèse vocale Piper fonctionnelle
- **[AJOUTÉ]** : Intégration Ollama complète
- **[CORRIGÉ]** : Résolution des bugs d'installation

### [1.2.0] - Planifié
- **[AJOUTÉ]** : Intégration Home Assistant
- **[AJOUTÉ]** : Système de mémoire contextuelle
- **[AJOUTÉ]** : Interface domotique frontend

---

## 🔄 Dernière mise à jour
**Date** : 2025-01-17 - 17:00
**Par** : Claude
**Action** : Création du changelog initial