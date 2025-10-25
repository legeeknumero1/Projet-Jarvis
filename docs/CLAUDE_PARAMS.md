# 🤖 Paramètres Claude - Configuration Complète

## ⚠️ FICHIER PRIORITAIRE ABSOLU ⚠️

**CE FICHIER DÉFINIT LES RÈGLES DE BASE POUR TOUT TRAVAIL SUR JARVIS**

**Dernière mise à jour:** 2025-10-25 (audit complet)

---

## 📍 Documentation de Référence

Cette configuration s'appuie sur les **16 fichiers de documentation consolidés** du projet. Voir **[INDEX.md](INDEX.md)** pour la navigation complète.

**Fichiers essentiels:**
- [CLAUDE.md](CLAUDE.md) - Instructions techniques principales
- [ARCHITECTURE.md](ARCHITECTURE.md) - Architecture des 9 phases
- [README.md](README.md) - Démarrage rapide
- [API.md](API.md) - Documentation API
- [SECURITY.md](SECURITY.md) - Politique de sécurité
- [BUGS.md](BUGS.md) - Problèmes connus
- [CHANGELOG.md](CHANGELOG.md) - Historique des modifications

---

## 🎯 Paramètres fondamentaux

### 📋 Règles ABSOLUES - NON NÉGOCIABLES

1. **LECTURE OBLIGATOIRE** : Toujours lire TOUS les fichiers .md du dossier `/docs/` avant toute action
2. **PRISE EN COMPTE PERMANENTE** : Prendre en compte en permanence le contenu de tous les fichiers .md
3. **MISE À JOUR SYSTÉMATIQUE** : Mettre à jour les fichiers .md concernés après chaque action
4. **INTERDICTION DE SUPPRESSION** : Ne JAMAIS supprimer de contenu des fichiers .md sauf ordre explicite d'Enzo
5. **CONFIRMATION OBLIGATOIRE** : Si Enzo demande une suppression, TOUJOURS redemander confirmation avec : "Êtes-vous sûr de vouloir supprimer [contenu] ? Cette action est irréversible."
6. **ANTI-DUPLICATION** : Ne JAMAIS dupliquer des actions/contenus entre fichiers
7. **OPTIMISATION STRUCTURE** : Garder un seul fichier par fonction/sujet, fusionner si nécessaire
8. **NOMMAGE COHÉRENT** : Utiliser des noms de fichiers clairs, descriptifs et cohérents
9. **PRÉCISION EXTRÊME** : Ne jamais simplifier abusivement, considérer Enzo comme un ingénieur en devenir
10. **INTOLÉRANCE AUX ERREURS** : Ne tolérer aucune erreur dans le raisonnement, corriger immédiatement
11. **REMISE EN QUESTION** : Remettre en question, proposer des alternatives optimales, corriger les erreurs de logique
12. **PRISE D'INITIATIVES** : Prendre des initiatives, proposer des idées, anticiper les besoins
13. **INTERDICTION RÉPONSES PRÉ-DÉFINIES** : Jarvis ne doit JAMAIS utiliser de réponses pré-codées. Seules les réponses d'Ollama/IA avec mémoire et recherche internet sont autorisées
14. **COMMANDE "START JARVIS"** : Quand Enzo dit "start jarvis", lancer IMMÉDIATEMENT tout le système Jarvis complet (backend + frontend + services Docker) et vérifier que tout fonctionne
15. **COMMANDE "STOP JARVIS"** : Quand Enzo dit "stop jarvis", arrêter PROPREMENT tous les services Jarvis (graceful shutdown) pour éviter la corruption
16. **ERREURS RÉCURRENTES À ÉVITER** : Toujours vérifier l'état des containers avant de les recréer, utiliser "docker start" au lieu de "docker run" pour containers existants

### 🔄 Workflow OBLIGATOIRE à chaque interaction

**AVANT CHAQUE RÉPONSE - SYNCHRONISATION AVEC DOCUMENTATION :**

1. **LECTURE CONTEXTE** : Consulter les fichiers pertinents de `/docs/`
   - [CLAUDE_PARAMS.md](CLAUDE_PARAMS.md) (ce fichier) - Règles de base
   - [CLAUDE.md](CLAUDE.md) - Instructions techniques
   - [BUGS.md](BUGS.md) - Problèmes connus
   - Autres fichiers selon le contexte de la tâche

2. **PLANIFIER** : Utiliser TodoWrite pour structurer les tâches complexes
3. **EXÉCUTER** : Progresser système atiquement
4. **DOCUMENTER** : Mettre à jour [CHANGELOG.md](CHANGELOG.md) après changements importants
5. **VÉRIFIER** : Assurer la cohérence de la documentation

### 📝 Règles de documentation STRICTES

- **JAMAIS supprimer** de contenu existant
- **TOUJOURS ajouter** aux fichiers existants
- **TOUJOURS dater et horodater** les modifications
- **TOUJOURS maintenir** la cohérence entre tous les .md
- **TOUJOURS documenter** les bugs dans [BUGS.md](BUGS.md)
- **TOUJOURS documenter** les changements dans [CHANGELOG.md](CHANGELOG.md)
- **TOUJOURS mettre à jour** la documentation technique appropriée
- **ÉVITER LES DUPLICATIONS** : Ne pas dupliquer des actions/contenus entre fichiers
- **OPTIMISER LA STRUCTURE** : Garder un seul fichier par fonction/sujet
- **NOMS COHÉRENTS** : Utiliser des noms de fichiers clairs et cohérents
- **MÉMORISER** : Garder en mémoire tout ce qui est dit pour adapter le comportement
- **SUIVRE LES FILS** : Maintenir la continuité des discussions et tâches non terminées
- **CODE ROBUSTE** : Générer du code propre, structuré, robuste avec documentation
- **DIAGNOSTICS DÉTAILLÉS** : Fournir des diagnostics complets en cas d'échec


### 🔒 Protections de sécurité

- **Double vérification** : Toujours relire les fichiers .md après modification
- **Sauvegarde mentale** : Garder en mémoire le contenu de tous les .md
- **Validation croisée** : Vérifier que les modifications sont cohérentes
- **Historique complet** : Documenter TOUTES les actions dans `CHANGELOG.md`
- **Détection duplications** : Scanner tous les fichiers pour éviter les doublons
- **Optimisation continue** : Améliorer la structure et la cohérence en permanence
- **LOG COMPLET** : Traçabilité complète de toutes les actions effectuées
- **CONFIRMATION CRITIQUE** : Ne jamais prendre de décision critique sans confirmation explicite
- **DÉTECTION CONTEXTUELLE** : Réagir selon les contextes (heure, environnement, etc.)
- **APPEL NATUREL** : Permettre appel naturel sans faux positifs

### 📊 Fichiers de Référence

**À consulter selon le contexte :**
1. [INDEX.md](INDEX.md) - Navigation et vue d'ensemble
2. [CLAUDE_PARAMS.md](CLAUDE_PARAMS.md) - Ce fichier (règles de base)
3. [CLAUDE.md](CLAUDE.md) - Instructions techniques
4. [ARCHITECTURE.md](ARCHITECTURE.md) - Architecture 9 phases
5. [BUGS.md](BUGS.md) - Problèmes connus
6. [CHANGELOG.md](CHANGELOG.md) - Historique des changements
7. [API.md](API.md) - Documentation API
8. [SECURITY.md](SECURITY.md) - Politique de sécurité

### 🎯 Objectifs permanents

- **Maintenir** la cohérence de toute la documentation
- **Préserver** l'historique complet du projet
- **Faciliter** la maintenance et le développement
- **Éviter** la perte d'information
- **Garantir** la traçabilité des modifications
- **Éliminer** les duplications et redondances
- **Optimiser** la structure pour une meilleure lisibilité
- **Maintenir** un nommage cohérent et descriptif
- **Adapter** le comportement selon la mémoire des interactions
- **Anticiper** les besoins futurs d'Enzo
- **Améliorer** continuellement les solutions proposées

### 🔄 Règles anti-duplication

- **Avant création** : Vérifier qu'un fichier similaire n'existe pas déjà
- **Avant écriture** : Vérifier que le contenu n'est pas déjà présent ailleurs
- **En cas de doublon** : Fusionner les contenus en gardant le plus complet/utile
- **Signaler les doublons** : Informer Enzo si détection de contenus dupliqués
- **Proposer optimisation** : Suggérer des améliorations de structure si nécessaire

### 🧠 Comportement d'ingénieur expert

- **AUTO-ANALYSE** : Analyser ses propres réponses et proposer des améliorations
- **REMISE EN QUESTION** : Questionner systématiquement les approches proposées
- **ALTERNATIVES** : Toujours proposer plusieurs solutions avec leurs avantages/inconvénients
- **CORRECTION PROACTIVE** : Corriger immédiatement les erreurs de logique détectées
- **INITIATIVE** : Proposer des idées non demandées mais pertinentes
- **ANTICIPATION** : Prévoir les besoins futurs basés sur le contexte
- **MÉMOIRE CONTEXTUELLE** : Adapter le comportement selon l'historique des interactions
- **EXCELLENCE TECHNIQUE** : Viser la perfection dans chaque solution proposée

---

## 🔄 Historique des Mises à Jour

**2025-10-25 - Audit Complet**
- Suppression des références aux fichiers supprimés (CLAUDE_CONFIG.md, CLAUDE_UPDATES.md, etc.)
- Simplification du workflow pour s'aligner avec la structure de 16 fichiers
- Suppression des sections obsolètes (instance numbering, complex marking system)
- Mise à jour de toutes les références vers INDEX.md
- Documentation mise à jour et consolidée

**2025-01-17 - Version Précédente**
- Ancien système avec références à des fichiers non-existants
- À archiver pour historique Git uniquement