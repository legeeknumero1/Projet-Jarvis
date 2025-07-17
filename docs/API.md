# 🔌 Documentation API - Jarvis

## 📡 Endpoints API

### Base URL
```
http://localhost:8000
```

### Authentification
*Pas d'authentification requise pour le moment (développement)*

---

## 🔄 Endpoints principaux

### GET /
**Description** : Message de bienvenue
**Réponse** :
```json
{
  "message": "Jarvis AI Assistant is running"
}
```

### GET /health
**Description** : Vérification du statut du système
**Réponse** :
```json
{
  "status": "healthy",
  "timestamp": "2025-01-17T17:00:00Z"
}
```

### POST /chat
**Description** : Envoie un message à Jarvis
**Body** :
```json
{
  "message": "string",
  "user_id": "string" // optionnel, défaut: "default"
}
```
**Réponse** :
```json
{
  "response": "string",
  "timestamp": "2025-01-17T17:00:00Z"
}
```

### WebSocket /ws
**Description** : Communication temps réel
**Messages envoyés** :
```json
{
  "message": "string",
  "user_id": "string",
  "timestamp": "2025-01-17T17:00:00Z"
}
```
**Messages reçus** :
```json
{
  "response": "string",
  "timestamp": "2025-01-17T17:00:00Z"
}
```

---

## 🔄 Endpoints futurs (planifiés)

### POST /voice/transcribe
**Description** : Transcription audio vers texte
**Body** : FormData avec fichier audio
**Réponse** :
```json
{
  "transcript": "string",
  "confidence": "float"
}
```

### POST /voice/synthesize
**Description** : Synthèse vocale
**Body** :
```json
{
  "text": "string",
  "voice": "string" // optionnel
}
```
**Réponse** : Fichier audio

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

## 🔄 Dernière mise à jour
**Date** : 2025-01-17 - 17:00
**Par** : Claude
**Action** : Création de la documentation API initiale