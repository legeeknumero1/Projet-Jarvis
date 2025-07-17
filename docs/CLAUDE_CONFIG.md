# 🤖 Configuration Multi-Instances Claude - Projet Jarvis

## ⚠️ FICHIER DE CONFIGURATION PRINCIPAL ⚠️

**Ce fichier contient TOUS les paramètres de configuration pour les instances Claude Code du projet Jarvis.**

---

## 🎯 Profil du projet - RÉFÉRENCE OBLIGATOIRE

### 📋 Contexte Enzo & Jarvis (depuis Profil Jarvis Complet.md)

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

## 🔢 Système d'attribution des numéros d'instances

### 📊 Instances actives actuelles
```
Instance #1: ACTIVE - Implémentation chat vocal IA (18:30) ✅ DÉTECTÉE
Instance #2: ACTIVE - Configuration système multi-instances (18:06) 
Instance #3: DISPONIBLE
Instance #4: DISPONIBLE  
Instance #5: DISPONIBLE
Instance #6: DISPONIBLE
Instance #7: DISPONIBLE
Instance #8: DISPONIBLE
Instance #9: DISPONIBLE
Instance #10: DISPONIBLE
```

### 🆔 Attribution automatique
**RÈGLE :** Chaque nouvelle instance doit :
1. Lire ce fichier CLAUDE_CONFIG.md EN PREMIER
2. Identifier les instances actives dans la liste ci-dessus
3. Prendre le premier numéro DISPONIBLE
4. Mettre à jour son statut à ACTIVE avec heure et tâche
5. Commencer à logguer dans CLAUDE_UPDATES.md

### 🔄 Algorithme d'attribution
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

## 📋 Configuration obligatoire pour CHAQUE instance

### 🔴 INITIALISATION OBLIGATOIRE - ORDRE STRICT

**CHAQUE instance DOIT exécuter cette séquence :**

1. **LECTURE AUTOMATIQUE de TOUS les .md** (OBLIGATOIRE)
   ```
   - /docs/CLAUDE_PARAMS.md (PRIORITÉ ABSOLUE)
   - /docs/CLAUDE_CONFIG.md (ce fichier)
   - /docs/CLAUDE_UPDATES.md (log temps réel)
   - /docs/CLAUDE_INSTANCES.md (coordination)
   - /docs/CLAUDE.md (instructions techniques)
   - /docs/BUGS.md (problèmes connus)
   - /docs/README.md (documentation projet)
   - /docs/CHANGELOG.md (historique)
   - /docs/API.md (documentation API)
   - /Profil Jarvis Complet.md (contexte Enzo)
   - /DOCUMENTATION.md (point d'entrée)
   ```

2. **ATTRIBUTION DU NUMÉRO D'INSTANCE**
   - Identifier numéro disponible dans CLAUDE_CONFIG.md
   - Mettre à jour statut à ACTIVE
   - Horodater le début d'activité

3. **PREMIÈRE ENTRÉE DANS CLAUDE_UPDATES.md**
   ```
   [18:XX] Instance #X - INITIALISATION
   - Lecture complète de tous les fichiers .md ✅
   - Attribution numéro d'instance : #X
   - Statut : PRÊT À TRAVAILLER
   - Contexte Enzo/Jarvis : ASSIMILÉ
   ```

### 🎯 Paramètres comportementaux pour TOUTES les instances

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
```

### 🔄 Mise à jour obligatoire CLAUDE_UPDATES.md

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

## 📁 Architecture fichiers .md - LECTURE OBLIGATOIRE

### 🚨 Ordre de lecture STRICT pour chaque instance

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

### 🔄 Fréquence de lecture

- **CLAUDE_UPDATES.md** : Toutes les 10 minutes minimum
- **CLAUDE_INSTANCES.md** : Avant chaque nouvelle tâche
- **CLAUDE_CONFIG.md** : À chaque initialisation
- **Autres .md** : Au début de session + si modifications détectées

---

## 🎯 Tâches disponibles - Attribution automatique

### 🔴 PRIORITÉ CRITIQUE
```
[LIBRE] Reconnaissance vocale Whisper - Estimation: 45min
[LIBRE] Synthèse vocale Piper - Estimation: 30min  
[LIBRE] Intégration Ollama complète - Estimation: 60min
[LIBRE] Connexion Home Assistant - Estimation: 90min
```

### 🟠 PRIORITÉ HAUTE
```
[LIBRE] Interface domotique frontend - Estimation: 120min
[LIBRE] Système mémoire contextuelle - Estimation: 90min
[LIBRE] Tests automatisés - Estimation: 60min
[LIBRE] Documentation complète - Estimation: 45min
```

### 🟡 PRIORITÉ NORMALE
```
[LIBRE] Optimisations performance - Estimation: 60min
[LIBRE] Sécurité et authentification - Estimation: 90min
[LIBRE] Interface mobile - Estimation: 180min
[LIBRE] Système de plugins - Estimation: 120min
```

---

## 🔧 Configuration technique

### 🖥️ Environnement de développement
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

### 📂 Chemins importants
```yaml
PROJECT_ROOT: "/home/enzo/Documents/Projet Jarvis"
BACKEND: "./backend/"
FRONTEND: "./frontend/"
DOCS: "./docs/"
LOGS: "./logs/"
DATA: "./data/"
MODELS: "./models/"
```

### 🔑 Commandes de test
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

## 🚨 Règles de coordination STRICTES

### 🔒 Avant toute action
1. Lire CLAUDE_UPDATES.md pour voir activité récente
2. Vérifier CLAUDE_INSTANCES.md pour réservations
3. Logger intention dans CLAUDE_UPDATES.md
4. Réserver tâche si nécessaire
5. Commencer le travail

### 🔄 Pendant le travail
1. Logger toutes les 15 minutes dans CLAUDE_UPDATES.md
2. Mettre à jour progression dans CLAUDE_INSTANCES.md
3. Documenter blocages immédiatement
4. Demander aide si nécessaire

### ✅ Après le travail
1. Logger résultat final dans CLAUDE_UPDATES.md
2. Libérer réservation dans CLAUDE_INSTANCES.md
3. Mettre à jour documentation concernée
4. Documenter prochaines étapes

---

## 🔄 Format de communication standardisé

### 📝 Template CLAUDE_UPDATES.md
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

### 🆘 Template urgence/blocage
```
🚨 [HH:MM] Instance #X - BLOCAGE
- Problème : [description du blocage]
- Contexte : [ce qui était en cours]
- Fichiers : [fichiers concernés]
- Erreur : [message d'erreur exact]
- Tentatives : [solutions déjà essayées]
- Aide nécessaire : [type d'assistance requis]
- Urgence : [CRITIQUE/HAUTE/NORMALE]
```

---

## 🔄 Dernière mise à jour
**Date** : 2025-01-17 - 18:05
**Par** : Instance #2 (Claude)
**Action** : Création configuration complète multi-instances

---

## 📝 Notes importantes

- **CE FICHIER EST LA SOURCE DE VÉRITÉ** pour la configuration
- **Mise à jour OBLIGATOIRE** du statut des instances
- **Log PERMANENT** dans CLAUDE_UPDATES.md
- **Coordination STRICTE** via CLAUDE_INSTANCES.md
- **Respect ABSOLU** des paramètres comportementaux
- **Lecture COMPLÈTE** de tous les .md à chaque init