# JARVIS SYSTEM MAP & ARCHITECTURE STATUS
Date: 30 Janvier 2026
État: EN COURS DE RÉPARATION (Phase 1)

Ce document décrit l'architecture **réelle** du système, incluant les composants fonctionnels, les bouchons (stubs) et le code mort.

---

## 1. VUE D'ENSEMBLE (Microservices)

L'architecture est centrée sur `jarvis-backend` (le Core) qui orchestre les services IA et BDD.

```ascii
[Utilisateur] <--> [Open-WebUI] (Port 3000)
                        |
                        v
                 [Jarvis Core] (Rust / Port 8100)
                 /      |      \       \
                /       |       \       \
     [Ollama] (LLM)  [Qdrant] [Postgres] [Jarvis-Secretsd]
     (Port 11434)    (Vector)  (SQL)      (Vault / 8081)
```

---

## 2. DÉTAILS DES COMPOSANTS (Qui fait quoi ?)

### A. LE CERVEAU : `core/` (Rust)
*Status: PARTIELLEMENT FONCTIONNEL*
C'est le serveur API principal (Axum).

| Module | Responsabilité | État Actuel | Dépendance |
|--------|---------------|-------------|------------|
| `handlers/chat.rs` | Endpoint `/api/chat`. Gère la conversation. | ⚠️ **DÉGRADÉ** (Pas de mémoire/RAG) | Postgres, Ollama |
| `handlers/memory.rs` | Endpoint `/api/memory`. Stockage vectoriel. | 🔴 **FAKE** (Bouchon statique) | (Devrait être Qdrant) |
| `handlers/stt.rs` | Transcription Voix -> Texte. | 🔴 **FAKE** (Renvoie texte fixe) | (Devrait être Whisper) |
| `handlers/tts.rs` | Synthèse Texte -> Voix. | 🔴 **FAKE** (Renvoie faux audio) | (Devrait être Piper/Onnx) |
| `handlers/web_search.rs` | Recherche Internet. | 🟢 **FONCTIONNEL** | API Brave Search |
| `middleware/auth.rs` | Vérification JWT & Droits. | 🟠 **CRITIQUE** (Backdoors présentes) | - |
| `services/ollama.rs` | Client HTTP vers Ollama. | 🟢 **FONCTIONNEL** | Conteneur Ollama |
| `services/qdrant.rs` | Client HTTP vers Qdrant. | 🟢 **FONCTIONNEL** (Mais non utilisé) | Conteneur Qdrant |

### B. LE COFFRE-FORT : `jarvis-secretsd/` (Rust)
*Status: ROBUSTE*
Service de gestion des secrets.

*   **Rôle** : Fournit les clés API et mots de passe DB aux autres services au démarrage.
*   **Sécurité** : Utilise `mlock` (RAM verrouillée), `HKDF` (lien matériel) et mTLS.
*   **État** : Fonctionnel, mais le fallback HTTP doit être désactivé en prod.

### C. LES SERVICES DE DONNÉES

| Service | Technologie | Rôle | État |
|---------|------------|------|------|
| **Postgres** | PostgreSQL 16 | Stocke l'historique des chats et les users. | 🟢 OK |
| **Qdrant** | Qdrant | Stocke les vecteurs (mémoire long terme). | 🟢 OK (Mais vide) |
| **Redis** | Redis 7 | Cache (non utilisé par le Core actuellement). | 🟢 OK |
| **Ollama** | Llama 3 / Mistral | Moteur d'inférence IA local. | 🟢 OK |

---

## 3. FLUX DE DONNÉES (Data Flow)

### Flux de Conversation (Actuel vs Cible)

**ACTUEL (Amnésique) :**
1. User envoie message -> `handlers/chat`
2. Core sauvegarde User Msg -> Postgres
3. Core envoie Msg brut -> Ollama
4. Ollama répond -> Core sauvegarde IA Msg -> Postgres
5. Core répond au User.

**CIBLE (RAG - Retrieval Augmented Generation) :**
1. User envoie message -> `handlers/chat`
2. **Core vectorise message -> Qdrant (Search)**
3. **Qdrant renvoie contexte pertinent**
4. Core construit prompt : "Contexte: ... Question: ..."
5. Core envoie Prompt enrichi -> Ollama
6. ... suite identique.

### Flux de Mémorisation

**ACTUEL :**
1. User envoie "Souviens-toi que..." -> `handlers/memory`
2. Core répond "OK" (mais ne fait rien).

**CIBLE :**
1. User envoie "Souviens-toi que..." -> `handlers/memory`
2. Core vectorise le contenu -> Qdrant (Add Point)
3. Core confirme l'écriture.

---

## 4. CODE MORT ("Zombies")

Ces dossiers sont présents dans le projet mais **ne sont pas utilisés** par le système actif.

1.  `backend-rust-audio/` : Ancienne librairie DSP. Le Core utilise `whisper-rs` et `ort` (OnnxRuntime) directement.
2.  `backend-rust-mqtt/` : Moteur domotique non branché.
3.  `clustering-elixir/` : Expérimentation distribuée abandonnée.
4.  `monitoring-go/` : Faux dashboard de monitoring.

---

## 5. PLAN DE RÉPARATION

1.  **Phase 1 : Cerveau (Core)**
    *   Connecter `handlers/memory.rs` -> `services/qdrant.rs`
    *   Connecter `handlers/chat.rs` -> `services/qdrant.rs` (RAG)
2.  **Phase 2 : Sécurité**
    *   Nettoyer `middleware/auth.rs` (Supprimer Backdoors).
    *   Sécuriser `docker-compose.yml` (Ports, Secrets).
3.  **Phase 3 : Sens (Audio)**
    *   Activer Whisper (STT) et Piper/Onnx (TTS) dans les handlers.
