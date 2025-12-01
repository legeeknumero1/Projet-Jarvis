#  Configuration Multi-Instances Claude - Projet Jarvis

##  FICHIER DE CONFIGURATION PRINCIPAL 

**Ce fichier contient TOUS les paramètres de configuration pour les instances Claude Code du projet Jarvis.**

---

##  Profil du projet - RÉFÉRENCE OBLIGATOIRE

###  Contexte Enzo & Jarvis (depuis Profil Jarvis Complet.md)

**Développeur :** Enzo, 21 ans, Perpignan  
**Objectif :** Assistant vocal intelligent local avec domotique  
**Stack :** FastAPI + React + PostgreSQL + Ollama + Docker  
**Matériel :** i9-14900KF, RTX 4080, 32GB RAM, réseau 10GbE  
**Environnement :** Arch Linux + Hyprland, auto-hébergement prioritaire  

**Caractéristiques d'Enzo :**
- Discipline, perfectionnisme, efficacité
- Hyperactif, passionné par l'apprentissage
- Soucieux de la vie privée, orienté auto-hébergement
- Futur ingénieur réseau/cybersécurité

---

##  Système d'attribution des numéros d'instances

###  Instances actives actuelles
```
Instance #1: TERMINÉE - Toutes tâches transférées à Instance #12
Instance #2: TERMINÉE - Toutes tâches transférées à Instance #12
Instance #3: TERMINÉE - Toutes tâches transférées à Instance #12
Instance #4: TERMINÉE - Toutes tâches transférées à Instance #12
Instance #5: TERMINÉE - Toutes tâches transférées à Instance #12
Instance #6: TERMINÉE - Toutes tâches transférées à Instance #12
Instance #7: TERMINÉE - Toutes tâches transférées à Instance #12
Instance #8: TERMINÉE - Toutes tâches transférées à Instance #12
Instance #9: TERMINÉE - Toutes tâches transférées à Instance #12
Instance #10: TERMINÉE - Toutes tâches transférées à Instance #12
Instance #11: TERMINÉE - Toutes tâches transférées à Instance #12
Instance #12: FERMÉE - Tâches transférées à Instance #13  
Instance #13: FERMÉE - Mission K8s terminée avec succès - Script deploy-jarvis-complete.sh livré (2025-07-21) 
Instance #14: FERMÉE - Audit complet terminé (2025-07-22 17:05) 
Instance #15: FERMÉE - Toutes tâches transférées à Instance #16
Instance #16: ACTIVE - Initialisation automatique (2025-07-23 10:05) 
Instance #17: FERMÉE - Corrections Phase 1 terminées (2025-07-23 20:02) 
Instance #18: FERMÉE - Toutes tâches transférées à Instance #20
Instance #19: FERMÉE - Audit exhaustif terminé (2025-07-24 10:15)   
Instance #20: ACTIVE - Initialisation automatique (2025-07-24 10:25) 
Instance #21: FERMÉE - Mission documentation migration Docker terminée (2025-07-31 16:05) 
Instance #22: ACTIVE - Initialisation automatique (2025-08-09 19:15) 
```

###  Attribution automatique
**RÈGLE :** Chaque nouvelle instance doit :
1. Lire ce fichier CLAUDE_CONFIG.md EN PREMIER
2. Identifier les instances actives dans la liste ci-dessus
3. Prendre le premier numéro DISPONIBLE
4. Mettre à jour son statut à ACTIVE avec heure et tâche
5. Commencer à logguer dans CLAUDE_UPDATES.md

###  Algorithme d'attribution
```
POUR chaque nouveau démarrage d'instance :
  LIRE CLAUDE_CONFIG.md
  PARCOURIR la liste des instances (1 à 10)
  TROUVER le premier statut "DISPONIBLE"
  PRENDRE ce numéro d'instance
  METTRE À JOUR le statut à "ACTIVE"
  DOCUMENTER dans CLAUDE_UPDATES.md
```

---

##  Configuration obligatoire pour CHAQUE instance

###  INITIALISATION OBLIGATOIRE - ORDRE STRICT

**CHAQUE instance DOIT exécuter cette séquence :**

1. **LECTURE AUTOMATIQUE de TOUS les .md** (OBLIGATOIRE à chaque interaction)
   ```
   AVANT CHAQUE RÉPONSE - LECTURE COMPLÈTE :
   - /docs/CLAUDE_PARAMS.md (PRIORITÉ ABSOLUE)
   - /docs/CLAUDE_CONFIG.md (ce fichier)
   - /docs/CLAUDE_UPDATES.md (log temps réel)
   - /docs/CLAUDE_THOUGHTS.md (réflexions partagées)
   - /docs/CLAUDE_INSTANCES.md (coordination)
   - /docs/CLAUDE.md (instructions techniques)
   - /docs/BUGS.md (problèmes connus)
   - /docs/ANALYSE_BUGS.md (analyse causes/solutions bugs - OBLIGATOIRE)
   - /docs/README.md (documentation projet)
   - /docs/CHANGELOG.md (historique)
   - /docs/API.md (documentation API)
   - /docs/PROFIL_JARVIS.md (contexte Enzo/projet)
   - /docs/DOCUMENTATION.md (structure générale)
   ```

2. **ATTRIBUTION DU NUMÉRO D'INSTANCE**
   - Identifier numéro disponible dans CLAUDE_CONFIG.md
   - Mettre à jour statut à ACTIVE
   - Horodater le début d'activité

3. **VÉRIFICATION ANTI-CONFLIT**
   - Scanner CLAUDE_UPDATES.md pour actions récentes d'autres instances
   - Vérifier CLAUDE_THOUGHTS.md pour éviter doublons de réflexions
   - Scanner le code pour les marquages EN_COURS d'autres instances
   - Si conflit détecté → SKIP et chercher autre tâche

4. **PREMIÈRE ENTRÉE DANS CLAUDE_UPDATES.md**
   ```
   [18:XX] Instance #X - INITIALISATION
   - Lecture complète de tous les fichiers .md 
   - Attribution numéro d'instance : #X
   - Vérification anti-conflit : 
   - Statut : PRÊT À TRAVAILLER
   - Contexte Enzo/Jarvis : ASSIMILÉ
   ```

###  Paramètres comportementaux pour TOUTES les instances

```yaml
COMPORTEMENT_INSTANCE:
  precision: EXTRÊME
  tolerance_erreurs: ZÉRO
  auto_analyse: ACTIVÉE
  remise_en_question: SYSTÉMATIQUE
  alternatives: TOUJOURS_PROPOSER
  correction_proactive: OBLIGATOIRE
  initiatives: ENCOURAGÉES
  anticipation: MAXIMALE
  memoire_contextuelle: PERMANENTE
  
SYNCHRONISATION_OBLIGATOIRE:
  lecture_md_avant_reponse: OBLIGATOIRE
  verification_conflits: AUTOMATIQUE
  marquage_code: OBLIGATOIRE
  partage_reflexions: OBLIGATOIRE
  respect_en_cours: STRICT
  skip_si_conflit: AUTOMATIQUE
  demande_enzo_si_rien: OBLIGATOIRE
```

###  Mise à jour obligatoire CLAUDE_UPDATES.md

**CHAQUE action/pensée/décision DOIT être loggée :**

```
[HH:MM] Instance #X - TYPE_ACTION
- Action : [description précise]
- Fichiers : [fichiers concernés]
- Résultat : [succès/échec/partiel]
- Prochaine étape : [action suivante]
- Remarques : [notes importantes]
```

**Types d'actions à logger :**
- INITIALISATION
- LECTURE_FICHIER
- ANALYSE_CODE
- IMPLEMENTATION
- DEBUG
- DOCUMENTATION
- COORDINATION
- REFLEXION
- DECISION
- BLOCAGE
- RESOLUTION
- HANDOVER

---

##  Architecture fichiers .md - LECTURE OBLIGATOIRE

###  Ordre de lecture STRICT pour chaque instance

1. **CLAUDE_PARAMS.md** - Règles absolues non négociables
2. **CLAUDE_CONFIG.md** - Configuration instances (ce fichier)
3. **CLAUDE_UPDATES.md** - Log temps réel des actions
4. **CLAUDE_INSTANCES.md** - Coordination et réservations
5. **CLAUDE.md** - Instructions techniques permanentes
6. **BUGS.md** - Problèmes connus et solutions
7. **README.md** - Documentation complète du projet
8. **CHANGELOG.md** - Historique des modifications
9. **API.md** - Documentation endpoints
10. **Profil Jarvis Complet.md** - Contexte Enzo/Jarvis
11. **DOCUMENTATION.md** - Point d'entrée général

###  Fréquence de lecture

- **CLAUDE_UPDATES.md** : Toutes les 10 minutes minimum
- **CLAUDE_INSTANCES.md** : Avant chaque nouvelle tâche
- **CLAUDE_CONFIG.md** : À chaque initialisation
- **Autres .md** : Au début de session + si modifications détectées

---

##  Tâches disponibles - Attribution automatique

###  PRIORITÉ CRITIQUE
```
[LIBRE] Reconnaissance vocale Whisper - Estimation: 45min
[LIBRE] Synthèse vocale Piper - Estimation: 30min  
[LIBRE] Intégration Ollama complète - Estimation: 60min
[LIBRE] Connexion Home Assistant - Estimation: 90min
```

###  PRIORITÉ HAUTE
```
[LIBRE] Interface domotique frontend - Estimation: 120min
[LIBRE] Système mémoire contextuelle - Estimation: 90min
[LIBRE] Tests automatisés - Estimation: 60min
[LIBRE] Documentation complète - Estimation: 45min
```

###  PRIORITÉ NORMALE
```
[LIBRE] Optimisations performance - Estimation: 60min
[LIBRE] Sécurité et authentification - Estimation: 90min
[LIBRE] Interface mobile - Estimation: 180min
[LIBRE] Système de plugins - Estimation: 120min
```

---

##  Configuration technique

###  Environnement de développement
```yaml
OS: Arch Linux + Hyprland
Terminal: Kitty
Editor: VS Code
Python: 3.13
Node: 18+
Docker: Compose v2
Database: PostgreSQL
AI: Ollama (LLaMA 3.1)
```

###  Chemins importants
```yaml
PROJECT_ROOT: "./Projet Jarvis"
BACKEND: "./backend/"
FRONTEND: "./frontend/"
DOCS: "./docs/"
LOGS: "./logs/"
DATA: "./data/"
MODELS: "./models/"
```

###  Commandes de test
```bash
# Backend
cd backend && source venv/bin/activate && python -m uvicorn main:app --reload

# Frontend  
cd frontend && npm start

# Docker
docker-compose up -d

# Base de données
docker exec -it jarvis_postgres psql -U jarvis -d jarvis_db

# Git
git status && git add . && git commit -m "Instance #X: [description]"
```

---

##  Règles de coordination STRICTES

###  Avant toute action
1. **LECTURE COMPLÈTE** : Lire TOUS les .md (liste ci-dessus)
2. **SCAN CONFLITS** : Vérifier marquages EN_COURS dans le code
3. **VÉRIFICATION RÉFLEXIONS** : Checker CLAUDE_THOUGHTS.md pour doublons
4. **RÉSERVATION** : Logger intention dans CLAUDE_UPDATES.md
5. **MARQUAGE CODE** : Marquer "EN_COURS" si modification code
6. **SI CONFLIT DÉTECTÉ** : SKIP automatiquement et chercher autre tâche

###  Pendant le travail
1. Logger toutes les 15 minutes dans CLAUDE_UPDATES.md
2. Maintenir marquage "EN_COURS" dans le code
3. Partager réflexions importantes dans CLAUDE_THOUGHTS.md
4. Documenter blocages immédiatement
5. Demander aide si nécessaire avec marquage "BESOIN_AIDE"

###  Après le travail
1. **MARQUER "FINI"** dans le code
2. Logger résultat final dans CLAUDE_UPDATES.md
3. Libérer réservation dans CLAUDE_INSTANCES.md
4. Mettre à jour documentation concernée
5. Partager solutions dans CLAUDE_THOUGHTS.md

###  Si rien à faire
1. **SCANNER** tous les .md pour nouvelles tâches
2. **VÉRIFIER** s'il y a des "BESOIN_AIDE" à traiter
3. **CHERCHER** tâches "FINI" à améliorer
4. **SI VRAIMENT RIEN** : Demander à Enzo "Que puis-je faire ?"

---

##  Format de communication standardisé

###  Template CLAUDE_UPDATES.md
```
[HH:MM] Instance #X - TYPE_ACTION
- Action : [description précise de l'action]
- Contexte : [pourquoi cette action]
- Fichiers : [liste des fichiers concernés]
- Statut : [EN_COURS/TERMINÉ/BLOQUÉ/ÉCHEC]
- Résultat : [ce qui a été accompli]
- Problèmes : [difficultés rencontrées]
- Solutions : [comment résolu ou à résoudre]
- Prochaine étape : [action suivante recommandée]
- Temps estimé : [durée prévue]
- Notes : [informations importantes]
```

###  Template urgence/blocage
```
 [HH:MM] Instance #X - BLOCAGE
- Problème : [description du blocage]
- Contexte : [ce qui était en cours]
- Fichiers : [fichiers concernés]
- Erreur : [message d'erreur exact]
- Tentatives : [solutions déjà essayées]
- Aide nécessaire : [type d'assistance requis]
- Urgence : [CRITIQUE/HAUTE/NORMALE]
```

---

##  Dernière mise à jour
**Date** : 2025-01-17 - 18:12
**Par** : Instance #2 (Claude)
**Action** : Ajout synchronisation automatique complète - Lecture tous .md avant chaque réponse + marquage code obligatoire

---

##  Notes importantes

- **CE FICHIER EST LA SOURCE DE VÉRITÉ** pour la configuration
- **Mise à jour OBLIGATOIRE** du statut des instances
- **Log PERMANENT** dans CLAUDE_UPDATES.md
- **Coordination STRICTE** via CLAUDE_INSTANCES.md
- **Respect ABSOLU** des paramètres comportementaux
- **Lecture COMPLÈTE** de tous les .md à chaque init