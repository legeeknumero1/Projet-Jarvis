# 🐛 Bugs Actifs - Jarvis

## 📊 État Actuel
- **Bugs critiques** : 0 ✅ **TOUS RÉSOLUS**
- **Bugs importants** : 23 ⚠️
- **Bugs mineurs** : 12 ℹ️
- **Total actif** : 35 bugs

## 🚨 PROBLÈME CRITIQUE PRINCIPAL

### **BUG-DOCKER-001** - Partition root saturée 
**Priorité** : 🚨 **CRITIQUE**  
**Statut** : 📋 **SOLUTION DISPONIBLE**  
**Impact** : Backend/Interface ne peuvent pas build  
**Solution** : Migration Docker vers /home  
**Procédure** : Voir `docs/MIGRATION_DOCKER_HOME.md`
```bash
sudo systemctl stop docker
sudo rsync -aP /var/lib/docker/ /home/$USER/jarvis-docker/
# ... voir procédure complète
```

---

## ⚠️ BUGS IMPORTANTS ACTIFS

### **BUG-TTS-001** - Piper TTS non fonctionnel
**Priorité** : ⚠️ **IMPORTANT**  
**Statut** : 🔄 **EN COURS**  
**Description** : Placeholder sinusoïdal au lieu de vraie synthèse  
**Fichier** : `backend/speech/speech_manager.py`  
**Action** : Finaliser implémentation Piper native

### **BUG-HA-001** - Home Assistant désactivé  
**Priorité** : ⚠️ **IMPORTANT**  
**Statut** : 🔄 **EN COURS**  
**Description** : Intégration domotique temporairement désactivée  
**Fichier** : `backend/integration/home_assistant.py`  
**Action** : Réactiver et tester connectivité

### **BUG-WSS-001** - WebSocket audio bridge incomplet
**Priorité** : ⚠️ **IMPORTANT**  
**Statut** : 📋 **PLANIFIÉ**  
**Description** : Pont audio temps réel non finalisé  
**Action** : Implémenter WebSocket audio complet

### **BUG-API-001** - Duplication endpoints STT/TTS
**Priorité** : ⚠️ **IMPORTANT**  
**Statut** : 🔍 **IDENTIFIÉ**  
**Description** : Backend + microservices font même chose  
**Action** : Factoriser ou déléguer aux microservices

### **BUG-MAIN-001** - main.py trop volumineux  
**Priorité** : ⚠️ **IMPORTANT**  
**Statut** : 🔍 **IDENTIFIÉ**  
**Description** : Plus de 700 lignes dans fichier principal  
**Action** : Séparer en routers FastAPI (/memory, /voice, /chat)

---

## ℹ️ BUGS MINEURS

### **BUG-LOG-001** - Mélange langues logs
**Priorité** : ℹ️ **MINEUR**  
**Action** : Uniformiser français/anglais

### **BUG-DEP-001** - Dépendances non utilisées
**Priorité** : ℹ️ **MINEUR**  
**Action** : Nettoyer requirements.txt

### **BUG-DOC-001** - Documentation verbosité  
**Priorité** : ℹ️ **MINEUR**  
**Action** : ✅ **EN COURS** - Nettoyage par Instance #22

---

## 🔧 Workflow Bugs

### Signaler un bug
1. **Identifier** le problème précisément
2. **Tester** reproduction du bug  
3. **Documenter** dans ce fichier avec format :
   ```markdown
   ### **BUG-XXX-000** - Titre court
   **Priorité** : 🚨/⚠️/ℹ️  
   **Statut** : 📋/🔄/🔍/✅  
   **Description** : Explication claire
   **Fichier** : Localisation du problème
   **Action** : Solution proposée
   ```

### Résoudre un bug
1. **Marquer** statut 🔄 **EN COURS**
2. **Implémenter** la correction
3. **Tester** que c'est résolu
4. **Marquer** ✅ **RÉSOLU** avec détails

---

## 📋 Actions Prioritaires

1. **🚨 IMMÉDIAT** : Exécuter migration Docker
2. **⚠️ COURT TERME** : Finaliser TTS Piper + Home Assistant  
3. **⚠️ MOYEN TERME** : Refactoring main.py + factorisation APIs
4. **ℹ️ LONG TERME** : Nettoyage code + optimisations

---

## 📚 Archives

**Historique complet** : `ai_assistants/BUGS_ARCHIVE.md` (286 bugs historiques)

**Dernière mise à jour** : Instance #22 - 2025-08-09