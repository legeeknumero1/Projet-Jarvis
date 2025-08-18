# 🤖 Paramètres Claude - Configuration Complète

## ⚠️ FICHIER PRIORITAIRE ABSOLU ⚠️

**CE FICHIER DOIT ÊTRE LU EN PREMIER AVANT TOUTE ACTION**

---

## 🚨 RÈGLE ABSOLUE - ARCHITECTURE DOCKER COMPLÈTE

### ⚡ ARCHITECTURE POUPÉE RUSSE OBLIGATOIRE

**L'architecture Jarvis DOIT contenir EXACTEMENT 7 containers Docker :**

1. **PostgreSQL** (172.20.0.100:5432) - Base de données ✅
2. **Redis** (172.20.0.110:6379) - Cache ✅  
3. **Ollama** (172.20.0.30:11434) - LLM Engine ✅
4. **STT API** (172.20.0.10:8003) - Speech-to-Text ✅
5. **TTS API** (172.20.0.20:8002) - Text-to-Speech ✅
6. **🚨 Backend API** (172.20.0.40:8000) - MANQUANT ❌
7. **🚨 Interface** (172.20.0.50:3000/8001) - MANQUANT ❌

### 📋 STATUT ACTUEL (MISE À JOUR 18:15)
```bash
# CONTAINERS ACTIFS (5/7)
docker ps
# ✅ jarvis_postgres - PostgreSQL (172.20.0.100:5432)
# ✅ jarvis_redis - Redis (172.20.0.110:6379)
# ✅ jarvis_ollama - Ollama (172.20.0.30:11434)
# ✅ jarvis_stt_api - STT API (172.20.0.10:8003) - HEALTHY
# ✅ jarvis_tts_api - TTS API (172.20.0.20:8002) - HEALTHY
# 🔄 jarvis_backend - Backend API (BUILD EN COURS avec Python 3.12 + setuptools)
# ❌ jarvis_interface - Interface (PRÊT À CONSTRUIRE)
```

### 🔧 CORRECTIONS APPLIQUÉES & PROBLÈME ESPACE DISQUE IDENTIFIÉ
- **Requirements restaurées** : Toutes dépendances Backend/STT/TTS complètes
- **Dockerfile amélioré** : Ajout build-essential, setuptools, wheel  
- **Build fixes** : Python 3.12 avec outils de compilation
- **Connectivité testée** : Communication inter-containers validée ✅
- **🚨 PROBLÈME CRITIQUE** : Partition root 120GB saturée par Docker
- **📋 SOLUTION PLANIFIÉE** : Migration Docker vers /home/jarvis-docker/
- **📄 PROCÉDURE** : Voir docs/MIGRATION_DOCKER_HOME.md

### 🎯 RÈGLES DE COMPLETION ABSOLUES

1. **BACKEND OBLIGATOIRE** : Le container `jarvis_backend` DOIT être construit et démarré
2. **INTERFACE OBLIGATOIRE** : Le container `jarvis_interface` DOIT être construit et démarré  
3. **RÉSEAU COMPLET** : Tous les 7 containers DOIVENT communiquer sur `jarvis_network`
4. **TESTS REQUIS** : Connectivité inter-containers DOIT être validée
5. **ARCHITECTURE FINALE** : AUCUN service ne peut être omis ou simplifié

### 🔧 ACTIONS IMMÉDIATES REQUISES

**🚨 PRIORITÉ ABSOLUE - MIGRATION DOCKER :**
1. **Exécuter migration Docker** vers /home (voir MIGRATION_DOCKER_HOME.md)
2. **Libérer espace disque** partition root (120GB → /home)
3. **Reconfigurer Docker daemon** avec nouveau data-root

**📋 APRÈS MIGRATION :**
4. **Terminer le build Backend** avec plus d'espace
5. **Démarrer le container jarvis_backend** 
6. **Construire l'image jarvis_interface**
7. **Démarrer le container jarvis_interface**
8. **Valider l'architecture complète 7/7**

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

### 🚨 RÈGLES TESTS ET DÉVELOPPEMENT - PRIORITÉ ABSOLUE

**⚠️ RÉFÉRENCE OBLIGATOIRE : `/docs/REGLE_ABSOLUE_TESTS.md`**

17. **JAMAIS DE FAUX TESTS** : INTERDICTION TOTALE de simuler des résultats, prétendre qu'un test fonctionne sans l'exécuter, approximer l'état d'un service. OBLIGATION d'exécuter RÉELLEMENT chaque test et montrer les résultats authentiques.

18. **JAMAIS DE SIMPLIFICATION** : INTERDICTION de simplifier les problèmes complexes, omettre des détails techniques, présenter une version édulcorée. OBLIGATION d'analyser TOUS les aspects et diagnostiquer jusqu'à la cause racine.

19. **TOUJOURS RECHERCHER INTERNET** : INTERDICTION de se baser uniquement sur connaissances internes. OBLIGATION de rechercher SYSTÉMATIQUEMENT les meilleures pratiques actuelles, vérifier les dernières versions/vulnérabilités.

20. **JAMAIS RIEN HARDCODER** : INTERDICTION absolue de valeurs fixes, chemins absolus, URLs/ports/IPs hardcodés, mots de passe en dur. OBLIGATION d'utiliser variables d'environnement et configuration externalisée.

**CES RÈGLES SONT APPLIQUÉES EN PERMANENCE - AUCUNE EXCEPTION**

### 🤖 AUTO-INITIALISATION OBLIGATOIRE

**🚨 DÉCLENCHEMENT AUTOMATIQUE À L'OUVERTURE DU PROJET :**

**Quand Claude Code s'ouvre dans le répertoire du projet Jarvis :**
1. **DÉTECTION AUTOMATIQUE** : Présence de `/CLAUDE.md` à la racine
2. **LECTURE IMMÉDIATE** : Tous les fichiers .md de `/docs/` (liste ci-dessous)
3. **ATTRIBUTION AUTOMATIQUE** : Numéro d'instance disponible
4. **INITIALISATION SILENCIEUSE** : Configuration complète sans interaction
5. **LOGGING AUTOMATIQUE** : Première entrée dans CLAUDE_UPDATES.md
6. **PRÊT IMMÉDIATEMENT** : Instance opérationnelle en quelques secondes

**Si auto-init échoue → Afficher : "Tapez 'lis doc' pour initialiser"**

### 🔄 Workflow OBLIGATOIRE à chaque interaction

**🚨 AVANT CHAQUE RÉPONSE - SYNCHRONISATION AUTOMATIQUE OBLIGATOIRE :**

1. **LECTURE AUTOMATIQUE COMPLÈTE** de TOUS les fichiers .md du projet :
   - `/docs/CLAUDE_PARAMS.md` (ce fichier) EN PREMIER
   - `/docs/CLAUDE_CONFIG.md` pour statut instances
   - `/docs/CLAUDE_UPDATES.md` pour actions récentes
   - `/docs/CLAUDE_INSTANCES.md` pour réservations
   - `/docs/CLAUDE_THOUGHTS.md` pour réflexions partagées
   - `/docs/CLAUDE.md` pour instructions techniques
   - `/docs/BUGS.md` pour problèmes connus
   - `/docs/ANALYSE_BUGS.md` pour analyse causes/solutions bugs (OBLIGATOIRE)
   - `/docs/README.md` pour contexte projet
   - `/docs/CHANGELOG.md` pour historique
   - `/docs/API.md` pour documentation
   - `/docs/DOCUMENTATION.md` pour structure générale
   - `/docs/PROFIL_JARVIS.md` pour contexte Enzo/projet

2. **VÉRIFICATION CONFLITS** : Scanner si une autre instance travaille déjà sur la demande
3. **MISE À JOUR STATUS** : Mettre à jour statut dans CLAUDE_CONFIG.md si nécessaire
4. **RECHERCHER** sur internet les meilleures pratiques
5. **PLANIFIER** avec TodoWrite
6. **EXÉCUTER** la tâche avec marquage EN_COURS
7. **METTRE À JOUR** tous les fichiers .md concernés avec marquage FINI
8. **LOGGER** dans CLAUDE_UPDATES.md
9. **VÉRIFIER** la cohérence entre tous les fichiers .md
10. **CONTRÔLER DUPLICATIONS** : Vérifier qu'il n'y a pas de doublons entre fichiers
11. **OPTIMISER SI NÉCESSAIRE** : Fusionner contenus dupliqués en gardant le plus utile

### 📝 Règles de documentation STRICTES

- **JAMAIS supprimer** de contenu existant
- **TOUJOURS ajouter** aux fichiers existants
- **TOUJOURS dater et horodater** les modifications
- **TOUJOURS maintenir** la cohérence entre tous les .md
- **TOUJOURS documenter** les bugs dans `BUGS.md`
- **TOUJOURS analyser** causes/solutions bugs dans `ANALYSE_BUGS.md`
- **TOUJOURS documenter** les changements dans `CHANGELOG.md`
- **TOUJOURS documenter** les réflexions dans `CLAUDE_THOUGHTS.md`
- **TOUJOURS tenir à jour** la documentation technique
- **ÉVITER LES DUPLICATIONS** : Ne pas dupliquer des actions/contenus entre fichiers
- **OPTIMISER LA STRUCTURE** : Garder un seul fichier par fonction/sujet
- **NOMS COHÉRENTS** : Utiliser des noms de fichiers clairs et cohérents
- **MÉMORISER** : Garder en mémoire tout ce qui est dit pour adapter le comportement
- **SUIVRE LES FILS** : Maintenir la continuité des discussions et tâches non terminées
- **CODE ROBUSTE** : Générer du code propre, structuré, robuste avec documentation
- **DIAGNOSTICS DÉTAILLÉS** : Fournir des diagnostics complets en cas d'échec

### 🏷️ Règles de marquage dans le code OBLIGATOIRES

**TOUT code modifié DOIT être marqué avec commentaires :**

**Format OBLIGATOIRE :**
```python
# Instance #X - EN_COURS - [Description de la modification]
[CODE EN COURS DE MODIFICATION]
# Instance #X - FINI - [Description de ce qui a été fait]
```

**Exemples :**
```python
# Instance #2 - EN_COURS - Ajout fonction de chat vocal
def chat_vocal():
    # Nouvelle implémentation par Instance #2
    pass
# Instance #2 - FINI - Fonction chat vocal opérationnelle

# Instance #1 - EN_COURS - Optimisation algorithme reconnaissance
# ... code ...
# Instance #1 - FINI - Algorithme optimisé +30% performance
```

**Règles de marquage :**
- **EN_COURS** : Instance travaille actuellement dessus - AUTRES INSTANCES DOIVENT SKIP
- **FINI** : Modification terminée - AUTRES INSTANCES PEUVENT TRAVAILLER DESSUS
- **BESOIN_AIDE** : Instance bloquée - AUTRES INSTANCES PEUVENT AIDER
- **REVIEW_DEMANDÉE** : Instance demande relecture - COLLABORATION SOUHAITÉE

### 🎯 Commande spéciale "lis doc" - INITIALISATION INSTANCE

**Si l'utilisateur tape "lis doc" :**

1. **EXÉCUTER IMMÉDIATEMENT** la séquence d'initialisation complète :
   - Lire TOUS les fichiers .md de `/docs/` dans l'ordre de priorité
   - Attribuer automatiquement un numéro d'instance disponible
   - Mettre à jour CLAUDE_CONFIG.md avec le statut ACTIVE
   - Logger l'initialisation dans CLAUDE_UPDATES.md
   - Confirmer à l'utilisateur : "Instance #X initialisée et prête ✅"

2. **RÉPONDRE** avec un résumé de l'état du projet et du statut de l'instance

### 🚨 Confirmation de suppression

Format OBLIGATOIRE si Enzo demande une suppression :

```
⚠️ CONFIRMATION DE SUPPRESSION REQUISE ⚠️

Vous demandez la suppression de :
[CONTENU À SUPPRIMER]

Dans le fichier : [FICHIER]

Êtes-vous absolument sûr de vouloir supprimer ce contenu ? 
Cette action est IRRÉVERSIBLE.

Tapez "OUI SUPPRIMER" pour confirmer ou "ANNULER" pour annuler.
```

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

### 📊 Priorités de fichiers .md

1. **CLAUDE_PARAMS.md** (ce fichier) - PRIORITÉ ABSOLUE
2. **CLAUDE.md** - Instructions techniques principales
3. **BUGS.md** - Problèmes connus et solutions
4. **README.md** - Documentation projet
5. **CHANGELOG.md** - Historique des modifications
6. **API.md** - Documentation technique
7. Autres fichiers .md selon le contexte

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

## 🔄 Dernière mise à jour
**Date** : 2025-01-17 - 18:12
**Par** : Instance #2 (Claude)
**Action** : Système de synchronisation automatique révolutionnaire : lecture tous .md avant chaque réponse, marquage EN_COURS/FINI, partage réflexions, skip automatique conflits