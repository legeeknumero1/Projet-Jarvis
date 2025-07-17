# 🐛 Registre des Bugs - Projet Jarvis

## 📋 Statut des bugs
- 🔴 **CRITIQUE** : Bloque le fonctionnement
- 🟠 **URGENT** : Doit être résolu rapidement
- 🟡 **NORMAL** : Peut attendre
- 🟢 **MINEUR** : Cosmétique ou amélioration
- ✅ **RÉSOLU** : Corrigé et testé
- ❌ **NON RÉSOLU** : En attente de correction

---

## 📊 Résumé actuel
- **Total bugs** : 6
- **Critiques** : 0
- **Urgents** : 0
- **Normaux** : 3
- **Résolus** : 3
- **En cours** : 3

---

## 🐛 Liste des bugs

### BUG-001 - Dépendances Python problématiques
**Statut** : 🟢 MINEUR ✅ RÉSOLU
**Découvert** : 2025-01-17 - 15:30
**Résolu** : 2025-01-17 - 17:30
**Description** : 
- `psycopg2-binary` ne s'installe pas (erreur pg_config)
- `openai-whisper` a des problèmes de compatibilité Python 3.13
- Solution temporaire : installation sans versions fixes

**Impact** : Bloque l'installation complète des dépendances
**Solution appliquée** : 
- Whisper installé depuis GitHub : `pip install git+https://github.com/openai/whisper.git`
- Utilisation d'asyncpg au lieu de psycopg2-binary
- Installation réussie avec toutes les dépendances CUDA

---

### BUG-002 - Ollama non installé
**Statut** : 🟢 MINEUR ✅ RÉSOLU
**Découvert** : 2025-01-17 - 16:45
**Résolu** : 2025-01-17 - 17:32
**Description** : 
- Ollama nécessite des privilèges sudo pour installation
- Script d'installation bloqué par l'authentification

**Impact** : Pas de LLM local disponible
**Solution appliquée** : 
- Lancement du conteneur Docker officiel Ollama
- Commande : `docker run -d -p 11434:11434 --name ollama ollama/ollama:latest`
- Téléchargement réussi du modèle LLaMA 3.1
- Test de génération fonctionnel

---

### BUG-003 - Piper TTS pas dans PATH
**Statut** : 🟢 MINEUR ✅ RÉSOLU
**Découvert** : 2025-01-17 - 16:20
**Résolu** : 2025-01-17 - 17:35
**Description** : 
- `piper-tts` installé via pip mais commande `piper` non trouvée
- Nécessite configuration du PATH ou utilisation du module Python

**Impact** : Synthèse vocale non fonctionnelle
**Solution appliquée** : 
- Modification de speech_manager.py pour utiliser PiperVoice directement
- Import du module : `from piper import PiperVoice`
- Implémentation de la synthèse via le module Python
- Gestion des modèles vocaux français

---

### BUG-004 - Dépendances audio manquantes
**Statut** : 🟡 NORMAL ❌ NON RÉSOLU
**Découvert** : 2025-01-17 - 18:30
**Résolu** : N/A
**Description** : 
- `soundfile` et `pydub` non installés dans l'environnement virtuel
- Fonctionnalités audio limitées (conversion, normalisation)
- TTS Piper partiellement fonctionnel

**Impact** : Fonctionnalités audio avancées non disponibles
**Solution** : Installer les dépendances manquantes : `pip install soundfile pydub`
**Prochaine étape** : Installation des packages audio complets

---

### BUG-005 - sentence-transformers manquant
**Statut** : 🟡 NORMAL ❌ NON RÉSOLU
**Découvert** : 2025-01-17 - 18:30
**Résolu** : N/A
**Description** : 
- Module `sentence-transformers` non installé
- Système d'embeddings désactivé temporairement
- Recherche de mémoire limitée au texte simple

**Impact** : Mémoire vectorielle non fonctionnelle
**Solution** : Installer sentence-transformers et réactiver les embeddings
**Prochaine étape** : `pip install sentence-transformers`

---

### BUG-006 - FastAPI deprecated warnings
**Statut** : 🟡 NORMAL ❌ NON RÉSOLU
**Découvert** : 2025-01-17 - 18:30
**Résolu** : N/A
**Description** : 
- Warnings de dépréciation `on_event` dans FastAPI
- Nouvelle API `lifespan` recommandée
- Fonctionnalité toujours opérationnelle

**Impact** : Cosmétique, pas d'impact fonctionnel
**Solution** : Migrer vers la nouvelle API lifespan de FastAPI
**Prochaine étape** : Refactoring des event handlers

---

## 📝 Template pour nouveaux bugs

```markdown
### BUG-XXX - Titre du bug
**Statut** : 🔴/🟠/🟡/🟢 NIVEAU ❌/✅ RÉSOLU/NON RÉSOLU
**Découvert** : YYYY-MM-DD - HH:MM
**Résolu** : YYYY-MM-DD - HH:MM ou N/A
**Description** : 
- Description détaillée du problème
- Étapes pour reproduire
- Environnement affecté

**Impact** : Impact sur le projet
**Solution** : Solution appliquée ou tentée
**Prochaine étape** : Action suivante à effectuer
```

---

## 📈 Historique des corrections

### 2025-01-17 - Session de résolution massive
- **17:30** - BUG-001 RÉSOLU : Whisper installé depuis GitHub, contournement Python 3.13
- **17:32** - BUG-002 RÉSOLU : Ollama déployé via Docker, LLaMA 3.1 fonctionnel
- **17:35** - BUG-003 RÉSOLU : Piper TTS adapté pour utilisation module Python
- **Taux de résolution** : 100% (3/3 bugs résolus)
- **Temps total** : 35 minutes

---

## 🔄 Dernière mise à jour
**Date** : 2025-01-17 - 18:30
**Par** : Claude
**Action** : Ajout de 3 nouveaux bugs non critiques - Système fonctionnel mais améliorations possibles