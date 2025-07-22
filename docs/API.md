# 🔌 Documentation API - Jarvis V1.1.0

## 📡 Endpoints API - MISE À JOUR COMPLÈTE

### Base URL
```
http://localhost:8000
```

### Authentification
*Pas d'authentification requise pour le moment (développement)*

---

## 🔄 Endpoints principaux ACTIFS

### GET /
**Description** : Message de bienvenue de l'API Jarvis
**URL** : `http://localhost:8000/`
**Méthode** : GET
**Réponse** :
```json
{
  "message": "Jarvis AI Assistant is running",
  "version": "1.1.0",
  "status": "operational"
}
```

### GET /health
**Description** : Vérification complète du statut du système
**URL** : `http://localhost:8000/health`
**Méthode** : GET
**Réponse** :
```json
{
  "status": "healthy",
  "timestamp": "2025-07-19T19:45:00Z",
  "services": {
    "database": "connected",
    "ollama": "running",
    "memory": "initialized",
    "speech": "ready"
  },
  "uptime": "2h 15m 30s"
}
```

### POST /chat
**Description** : Envoi de message textuel à Jarvis avec IA Ollama
**URL** : `http://localhost:8000/chat`
**Méthode** : POST
**Headers** : `Content-Type: application/json`
**Body** :
```json
{
  "message": "string",                    // Message utilisateur
  "user_id": "string",                   // optionnel, défaut: "default"  
  "context": "string",                   // optionnel, contexte conversation
  "save_memory": "boolean"               // optionnel, sauvegarder en mémoire
}
```
**Réponse** :
```json
{
  "response": "string",                  // Réponse de l'IA
  "timestamp": "2025-07-19T19:45:00Z",
  "user_id": "string",
  "model": "llama3.2:1b",
  "memory_saved": "boolean",
  "conversation_id": "uuid"
}
```

### WebSocket /ws
**Description** : Communication temps réel bidirectionnelle
**URL** : `ws://localhost:8000/ws`
**Protocole** : WebSocket
**Messages envoyés** :
```json
{
  "type": "message",
  "message": "string",
  "user_id": "string",
  "timestamp": "2025-07-19T19:45:00Z"
}
```
**Messages reçus** :
```json
{
  "type": "response",
  "response": "string",
  "timestamp": "2025-07-19T19:45:00Z",
  "user_id": "string",
  "conversation_id": "uuid"
}
```

---

## 🎤 Endpoints Vocaux OPÉRATIONNELS

### POST /voice/transcribe
**Description** : Transcription audio vers texte avec Whisper
**URL** : `http://localhost:8000/voice/transcribe`
**Méthode** : POST
**Headers** : `Content-Type: multipart/form-data`
**Body** : FormData avec fichier audio
```
audio: File (formats supportés: wav, mp3, m4a, ogg)
language: string (optionnel, défaut: "fr")
user_id: string (optionnel)
```
**Réponse** :
```json
{
  "transcript": "string",               // Texte transcrit
  "confidence": 0.95,                  // Score de confiance
  "language": "fr",                    // Langue détectée
  "duration": 3.2,                     // Durée audio en secondes
  "timestamp": "2025-07-19T19:45:00Z",
  "user_id": "string"
}
```

### POST /voice/synthesize
**Description** : Synthèse vocale français avec Piper TTS
**URL** : `http://localhost:8000/voice/synthesize`
**Méthode** : POST
**Headers** : `Content-Type: application/json`
**Body** :
```json
{
  "text": "string",                      // Texte à synthétiser
  "voice": "string",                  // optionnel, modèle voix
  "speed": 1.0,                      // optionnel, vitesse lecture
  "user_id": "string"                // optionnel
}
```
**Réponse** : Fichier audio WAV
**Headers de réponse** :
```
Content-Type: audio/wav
Content-Disposition: attachment; filename="synthesis.wav"
```

---

## 🧠 Endpoints Mémoire OPÉRATIONNELS

### GET /memory/{user_id}
**Description** : Récupération des mémoires utilisateur
**URL** : `http://localhost:8000/memory/{user_id}`
**Méthode** : GET
**Paramètres** :
- `user_id` : Identifiant utilisateur
- `limit` : Nombre max de mémoires (optionnel, défaut: 50)
- `category` : Catégorie de mémoire (optionnel)
**Réponse** :
```json
{
  "memories": [
    {
      "id": "uuid",
      "content": "string",
      "category": "conversation|fact|preference|reminder",
      "importance": 5,
      "created_at": "2025-07-19T19:45:00Z",
      "accessed_at": "2025-07-19T19:45:00Z",
      "access_count": 3
    }
  ],
  "total": 150,
  "user_id": "string"
}
```

### POST /memory/store
**Description** : Stockage d'une nouvelle mémoire
**URL** : `http://localhost:8000/memory/store`
**Méthode** : POST
**Body** :
```json
{
  "content": "string",                  // Contenu de la mémoire
  "user_id": "string",               // Identifiant utilisateur
  "category": "conversation",         // conversation|fact|preference|reminder
  "importance": 5,                   // 1-10, niveau d'importance
  "metadata": {}                     // optionnel, métadonnées additionnelles
}
```
**Réponse** :
```json
{
  "id": "uuid",
  "status": "stored",
  "embedding_created": true,
  "timestamp": "2025-07-19T19:45:00Z"
}
```

### POST /memory/search
**Description** : Recherche sémantique dans les mémoires
**URL** : `http://localhost:8000/memory/search`
**Méthode** : POST
**Body** :
```json
{
  "query": "string",                 // Requête de recherche
  "user_id": "string",              // Identifiant utilisateur
  "limit": 10,                      // Nombre max de résultats
  "threshold": 0.7,                 // Seuil de similarité
  "category": "string"              // optionnel, filtrer par catégorie
}
```
**Réponse** :
```json
{
  "results": [
    {
      "memory": {
        "id": "uuid",
        "content": "string",
        "category": "string",
        "importance": 5,
        "created_at": "datetime"
      },
      "similarity": 0.89,           // Score de similarité
      "relevance": "high"           // high|medium|low
    }
  ],
  "query": "string",
  "total_found": 5
}
```

---

## 🤖 Endpoints Ollama OPÉRATIONNELS

### POST /ollama/chat
**Description** : Communication directe avec Ollama avec mémoire contextuelle
**URL** : `http://localhost:8000/ollama/chat`
**Méthode** : POST
**Body** :
```json
{
  "message": "string",               // Message utilisateur
  "user_id": "string",              // Identifiant utilisateur
  "include_memory": true,           // Inclure mémoire contextuelle
  "model": "llama3.2:1b",          // optionnel, modèle à utiliser
  "system_prompt": "string",        // optionnel, prompt système
  "temperature": 0.7                // optionnel, créativité réponse
}
```
**Réponse** :
```json
{
  "response": "string",             // Réponse de l'IA
  "model": "llama3.2:1b",          // Modèle utilisé
  "timestamp": "2025-07-19T19:45:00Z",
  "memory_used": true,              // Mémoire utilisée
  "context_tokens": 156,            // Tokens de contexte
  "response_tokens": 89,            // Tokens de réponse
  "generation_time": 1.2            // Temps génération (secondes)
}
```

### GET /ollama/models
**Description** : Liste des modèles Ollama disponibles
**URL** : `http://localhost:8000/ollama/models`
**Méthode** : GET
**Réponse** :
```json
{
  "models": [
    {
      "name": "llama3.2:1b",
      "size": "1.3GB",
      "modified_at": "2025-07-19T15:30:00Z",
      "digest": "sha256:abc123...",
      "details": {
        "family": "llama",
        "parameter_size": "1B",
        "quantization_level": "Q4_0"
      }
    }
  ],
  "total": 1,
  "default_model": "llama3.2:1b"
}
```

### GET /ollama/status
**Description** : Statut détaillé du service Ollama
**URL** : `http://localhost:8000/ollama/status`
**Méthode** : GET
**Réponse** :
```json
{
  "status": "running",              // running|stopped|error
  "model_loaded": "llama3.2:1b",   // Modèle actuellement chargé
  "memory_usage": "2.1GB",         // Utilisation mémoire
  "gpu_usage": "45%",              // Utilisation GPU (si applicable)
  "uptime": "5h 23m",              // Temps de fonctionnement
  "version": "0.1.17",             // Version Ollama
  "available": true                // Service disponible
}
```

### GET /memory/{user_id}
**Description** : Récupération des mémoires utilisateur
**Réponse** :
```json
{
  "memories": [
    {
      "content": "string",
      "category": "string",
      "importance": "integer",
      "created_at": "datetime"
    }
  ]
}
```

### POST /memory/search
**Description** : Recherche dans les mémoires
**Body** :
```json
{
  "query": "string",
  "user_id": "string",
  "limit": "integer"
}
```

### GET /homeassistant/entities
**Description** : Liste des entités Home Assistant
**Réponse** :
```json
{
  "entities": [
    {
      "entity_id": "string",
      "state": "string",
      "attributes": "object"
    }
  ]
}
```

### POST /homeassistant/control
**Description** : Contrôle des appareils domotiques
**Body** :
```json
{
  "entity_id": "string",
  "action": "string",
  "value": "any" // optionnel
}
```

---

## 🔄 Codes d'erreur

### 400 - Bad Request
```json
{
  "detail": "Message d'erreur détaillé"
}
```

### 500 - Internal Server Error
```json
{
  "detail": "Erreur interne du serveur"
}
```

### 503 - Service Unavailable
```json
{
  "detail": "Service temporairement indisponible"
}
```

---

## 🔧 Endpoints Ollama

### POST /ollama/chat
**Description** : Communication directe avec Ollama avec mémoire
**Body** :
```json
{
  "message": "string",
  "user_id": "string",
  "include_memory": "boolean"
}
```
**Réponse** :
```json
{
  "response": "string",
  "model": "string",
  "timestamp": "2025-01-17T17:00:00Z",
  "memory_used": "boolean"
}
```

### GET /ollama/models
**Description** : Liste des modèles Ollama disponibles
**Réponse** :
```json
{
  "models": [
    {
      "name": "string",
      "size": "string",
      "modified_at": "datetime"
    }
  ]
}
```

### GET /ollama/status
**Description** : Statut du service Ollama
**Réponse** :
```json
{
  "status": "running|stopped|error",
  "model_loaded": "string",
  "memory_usage": "string"
}
```

---

## 🧠 Endpoints Mémoire

### POST /memory/store
**Description** : Stockage d'une nouvelle mémoire
**Body** :
```json
{
  "content": "string",
  "user_id": "string",
  "category": "conversation|fact|preference|reminder",
  "importance": "integer"
}
```

### GET /memory/stats/{user_id}
**Description** : Statistiques de mémoire utilisateur
**Réponse** :
```json
{
  "total_memories": "integer",
  "categories": "object",
  "oldest_memory": "datetime",
  "newest_memory": "datetime"
}
```

---

## 🎛️ Endpoints Services

### GET /services/status
**Description** : Statut de tous les services
**Réponse** :
```json
{
  "database": "healthy|unhealthy",
  "redis": "healthy|unhealthy", 
  "ollama": "healthy|unhealthy",
  "hybrid_server": "running|stopped"
}
```

### POST /services/restart/{service_name}
**Description** : Redémarrage d'un service spécifique
**Paramètres** : service_name (database|redis|ollama|hybrid_server)

---

## 🔄 Dernière mise à jour
**Date** : 2025-01-18 - 14:30
**Par** : Instance #1 (Claude)
**Action** : Ajout endpoints Ollama, mémoire et services