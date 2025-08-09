# 📋 Tâches Actives - Projet Jarvis

## 🚨 **PRIORITÉ IMMÉDIATE - Migration Docker**

### **TÂCHE-DOCKER-001** : Exécuter migration Docker vers /home
**Statut** : 🚨 **CRITIQUE - BLOQUANT**  
**Description** : Partition root saturée, impossible de build Backend/Interface  
**Procédure** : `docs/MIGRATION_DOCKER_HOME.md`  
**Impact** : Architecture 5/7 → 7/7 containers  
**Estimé** : 30 minutes

---

## ⚠️ **PRIORITÉ HAUTE - Finalisation Architecture**

### **TÂCHE-TTS-001** : Finaliser Piper TTS natif
**Statut** : 🔄 **EN COURS**  
**Description** : Remplacer placeholder sinusoïdal par vraie synthèse  
**Fichier** : `backend/speech/speech_manager.py`  
**Estimé** : 2 heures

### **TÂCHE-HA-001** : Réactiver Home Assistant
**Statut** : 🔄 **EN COURS**  
**Description** : Intégration domotique temporairement désactivée  
**Fichier** : `backend/integration/home_assistant.py`  
**Estimé** : 3 heures

### **TÂCHE-WS-001** : WebSocket audio bridge complet
**Statut** : 📋 **PLANIFIÉE**  
**Description** : Pont audio temps réel frontend ↔ STT/TTS  
**Fichier** : `services/interface/audio_bridge.py`  
**Estimé** : 6 heures

---

## 🟡 **PRIORITÉ NORMALE - Refactoring**

### **TÂCHE-MAIN-001** : Refactoring backend/main.py
**Statut** : 🔄 **EN COURS** - Instance #22  
**Description** : 697 lignes → structure modulaire routers/services  
**Estimé** : 4 heures

### **TÂCHE-FRONT-001** : Refactoring MassiveInterface.js  
**Statut** : 📋 **PLANIFIÉE**  
**Description** : 691 lignes → composants React atomiques  
**Estimé** : 3 heures

### **TÂCHE-TEST-001** : Factoriser tests redondants
**Statut** : 📋 **PLANIFIÉE**  
**Description** : Créer utils communs, réduire duplication  
**Estimé** : 2 heures

---

## 📊 **État Actuel (Post-Nettoyage)**

- **Documentation** : ✅ **NETTOYÉE** (-77% verbosité)
- **Architecture Docker** : 5/7 containers (migration requise)  
- **Code principal** : 697+691 lignes à refactorer
- **Tests** : Fonctionnels mais redondants

---

## 🔧 **Workflow Tâches**

### Créer une tâche
```markdown
### **TÂCHE-XXX-001** : Titre court
**Statut** : 🚨/⚠️/🟡/✅  
**Description** : Explication claire
**Fichier** : Localisation
**Estimé** : Temps prévu
```

### Statuts
- 🚨 **CRITIQUE** - Bloquant
- ⚠️ **IMPORTANT** - Impact majeur  
- 🟡 **NORMAL** - Amélioration
- 🔄 **EN COURS** - Travail actif
- 📋 **PLANIFIÉE** - Prêt à démarrer
- ✅ **TERMINÉE** - Fini et testé

---

## 📚 **Archives**

**Historique complet** : `archive/TACHES_A_FAIRE_COMPLETE.md` (2089 lignes)

**Dernière mise à jour** : Instance #22 - 2025-08-09