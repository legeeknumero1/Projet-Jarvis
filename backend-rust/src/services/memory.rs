//! Service de mémoire pour Jarvis Rust Backend
//! 
//! Gestion de la mémoire vectorielle avec Qdrant
//! Stockage et recherche sémantique des conversations

use reqwest::Client;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::Arc;
use uuid::Uuid;

use crate::{
    config::AppConfig,
    models::{MemoryEntry, MemoryMetadata, ContextType},
    services::DatabaseService,
};

/// Service de mémoire vectorielle
#[derive(Clone)]
pub struct MemoryService {
    client: Client,
    qdrant_url: String,
    collection_name: String,
    database: Arc<DatabaseService>,
}

/// Point de données pour Qdrant
#[derive(Debug, Serialize)]
struct QdrantPoint {
    id: String,
    vector: Vec<f32>,
    payload: HashMap<String, serde_json::Value>,
}

/// Requête de recherche Qdrant
#[derive(Debug, Serialize)]
struct QdrantSearchRequest {
    vector: Vec<f32>,
    limit: usize,
    with_payload: bool,
    score_threshold: Option<f32>,
}

/// Résultat de recherche Qdrant
#[derive(Debug, Deserialize)]
struct QdrantSearchResponse {
    result: Vec<QdrantSearchResult>,
}

#[derive(Debug, Deserialize)]
struct QdrantSearchResult {
    id: String,
    score: f32,
    payload: HashMap<String, serde_json::Value>,
}

/// Erreurs du service mémoire
#[derive(Debug, thiserror::Error)]
pub enum MemoryError {
    #[error("Erreur Qdrant: {0}")]
    QdrantError(String),
    
    #[error("Erreur génération embedding: {0}")]
    EmbeddingError(String),
    
    #[error("Collection non trouvée: {0}")]
    CollectionNotFound(String),
    
    #[error("Erreur réseau: {0}")]
    NetworkError(String),
}

impl MemoryService {
    /// Initialise le service de mémoire
    pub async fn new(
        config: &AppConfig,
        database: &Arc<DatabaseService>,
    ) -> anyhow::Result<Self> {
        let client = Client::new();
        let collection_name = "jarvis_memory".to_string();
        
        let service = Self {
            client,
            qdrant_url: config.external.qdrant_url.clone(),
            collection_name: collection_name.clone(),
            database: database.clone(),
        };

        // Initialiser la collection Qdrant si nécessaire
        service.ensure_collection_exists().await?;
        
        tracing::info!("✅ Service mémoire initialisé avec collection: {}", collection_name);
        Ok(service)
    }

    /// Vérifie si le service est prêt
    pub async fn is_ready(&self) -> anyhow::Result<()> {
        let url = format!("{}/collections/{}", self.qdrant_url, self.collection_name);
        
        let response = self.client.get(&url).send().await
            .map_err(|e| MemoryError::NetworkError(e.to_string()))?;
            
        if response.status().is_success() {
            Ok(())
        } else {
            Err(MemoryError::CollectionNotFound(self.collection_name.clone()).into())
        }
    }

    /// S'assure que la collection Qdrant existe
    async fn ensure_collection_exists(&self) -> anyhow::Result<()> {
        let url = format!("{}/collections/{}", self.qdrant_url, self.collection_name);
        
        // Vérifier si la collection existe
        let check_response = self.client.get(&url).send().await
            .map_err(|e| MemoryError::NetworkError(e.to_string()))?;
            
        if check_response.status().is_success() {
            tracing::debug!("✅ Collection Qdrant '{}' existe déjà", self.collection_name);
            return Ok(());
        }

        // Créer la collection
        tracing::info!("📚 Création collection Qdrant: {}", self.collection_name);
        
        let create_url = format!("{}/collections/{}", self.qdrant_url, self.collection_name);
        let create_body = serde_json::json!({
            "vectors": {
                "size": 384, // Dimension pour sentence-transformers/all-MiniLM-L6-v2
                "distance": "Cosine"
            }
        });

        let create_response = self.client
            .put(&create_url)
            .json(&create_body)
            .send()
            .await
            .map_err(|e| MemoryError::NetworkError(e.to_string()))?;

        if create_response.status().is_success() {
            tracing::info!("✅ Collection Qdrant créée avec succès");
            Ok(())
        } else {
            let error_text = create_response.text().await.unwrap_or_default();
            Err(MemoryError::QdrantError(error_text).into())
        }
    }

    /// Stocke un souvenir dans la mémoire vectorielle
    pub async fn store_memory(
        &self,
        content: String,
        conversation_id: Option<Uuid>,
        tags: Vec<String>,
        importance: f32,
    ) -> anyhow::Result<Uuid> {
        let memory_id = Uuid::new_v4();
        
        tracing::debug!("💾 Stockage mémoire: {} caractères", content.len());

        // Générer l'embedding du contenu
        let embedding = self.generate_embedding(&content).await?;

        // Créer les métadonnées
        let metadata = MemoryMetadata {
            source: "conversation".to_string(),
            conversation_id,
            tags: tags.clone(),
            importance,
            context_type: ContextType::Conversation,
        };

        // Créer le point Qdrant
        let mut payload = HashMap::new();
        payload.insert("content".to_string(), serde_json::Value::String(content.clone()));
        payload.insert("metadata".to_string(), serde_json::to_value(&metadata)?);
        payload.insert("created_at".to_string(), 
                      serde_json::Value::String(chrono::Utc::now().to_rfc3339()));

        let point = QdrantPoint {
            id: memory_id.to_string(),
            vector: embedding.clone(),
            payload,
        };

        // Stocker dans Qdrant
        let url = format!("{}/collections/{}/points", self.qdrant_url, self.collection_name);
        let body = serde_json::json!({
            "points": [point]
        });

        let response = self.client
            .put(&url)
            .json(&body)
            .send()
            .await
            .map_err(|e| MemoryError::NetworkError(e.to_string()))?;

        if !response.status().is_success() {
            let error_text = response.text().await.unwrap_or_default();
            return Err(MemoryError::QdrantError(error_text).into());
        }

        tracing::debug!("✅ Mémoire stockée avec ID: {}", memory_id);
        Ok(memory_id)
    }

    /// Recherche dans la mémoire contextuelle
    pub async fn search_relevant_context(
        &self,
        query: &str,
        limit: usize,
    ) -> anyhow::Result<Vec<MemoryEntry>> {
        tracing::debug!("🔍 Recherche mémoire: '{}' (limit: {})", query, limit);

        // Générer l'embedding de la requête
        let query_embedding = self.generate_embedding(query).await?;

        // Rechercher dans Qdrant
        let search_request = QdrantSearchRequest {
            vector: query_embedding,
            limit,
            with_payload: true,
            score_threshold: Some(0.5), // Seuil de similarité
        };

        let url = format!("{}/collections/{}/points/search", self.qdrant_url, self.collection_name);
        
        let response = self.client
            .post(&url)
            .json(&search_request)
            .send()
            .await
            .map_err(|e| MemoryError::NetworkError(e.to_string()))?;

        if !response.status().is_success() {
            let error_text = response.text().await.unwrap_or_default();
            return Err(MemoryError::QdrantError(error_text).into());
        }

        let search_response: QdrantSearchResponse = response.json().await
            .map_err(|e| MemoryError::QdrantError(e.to_string()))?;

        // Convertir les résultats en MemoryEntry
        let mut memories = Vec::new();
        for result in search_response.result {
            if let (Some(content), Some(metadata_value)) = (
                result.payload.get("content").and_then(|v| v.as_str()),
                result.payload.get("metadata")
            ) {
                let metadata: MemoryMetadata = serde_json::from_value(metadata_value.clone())
                    .unwrap_or_else(|_| MemoryMetadata {
                        source: "unknown".to_string(),
                        conversation_id: None,
                        tags: vec![],
                        importance: 0.5,
                        context_type: ContextType::Conversation,
                    });

                let memory = MemoryEntry {
                    id: Uuid::parse_str(&result.id).unwrap_or_else(|_| Uuid::new_v4()),
                    content: content.to_string(),
                    embedding: vec![], // Pas besoin de retourner l'embedding
                    metadata,
                    relevance_score: Some(result.score),
                    created_at: chrono::Utc::now(), // TODO: Parser depuis payload
                };

                memories.push(memory);
            }
        }

        tracing::debug!("✅ {} souvenirs trouvés", memories.len());
        Ok(memories)
    }

    /// Génère un embedding pour un texte
    async fn generate_embedding(&self, text: &str) -> anyhow::Result<Vec<f32>> {
        // Pour le moment, on utilise un embedding factice
        // TODO: Intégrer un service d'embedding (sentence-transformers, OpenAI, etc.)
        
        tracing::debug!("🧮 Génération embedding pour: {} caractères", text.len());
        
        // Embedding factice de dimension 384
        let mut embedding = vec![0.0; 384];
        
        // Générer un embedding simple basé sur le hash du texte
        let hash = self.simple_text_hash(text);
        for (i, byte) in hash.iter().enumerate() {
            if i < 384 {
                embedding[i] = (*byte as f32 - 128.0) / 128.0; // Normaliser entre -1 et 1
            }
        }

        Ok(embedding)
    }

    /// Hash simple pour générer des embeddings reproductibles
    fn simple_text_hash(&self, text: &str) -> Vec<u8> {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};
        
        let mut hasher = DefaultHasher::new();
        text.hash(&mut hasher);
        let hash = hasher.finish();
        
        // Étendre le hash à 48 bytes (384 bits / 8)
        let mut result = Vec::new();
        for i in 0..48 {
            result.push(((hash >> (i % 8)) & 0xFF) as u8);
        }
        result
    }

    /// Nettoie les anciens souvenirs
    pub async fn cleanup_old_memories(&self, days: i32) -> anyhow::Result<u64> {
        tracing::info!("🧹 Nettoyage mémoire: souvenirs de plus de {} jours", days);
        
        // TODO: Implémenter le nettoyage basé sur la date
        // Pour l'instant, on retourne 0
        Ok(0)
    }

    /// Statistiques de la mémoire
    pub async fn get_memory_stats(&self) -> anyhow::Result<serde_json::Value> {
        let url = format!("{}/collections/{}", self.qdrant_url, self.collection_name);
        
        let response = self.client.get(&url).send().await
            .map_err(|e| MemoryError::NetworkError(e.to_string()))?;

        if response.status().is_success() {
            let collection_info: serde_json::Value = response.json().await
                .map_err(|e| MemoryError::QdrantError(e.to_string()))?;
            
            Ok(serde_json::json!({
                "status": "healthy",
                "collection": self.collection_name,
                "info": collection_info
            }))
        } else {
            Ok(serde_json::json!({
                "status": "unhealthy",
                "error": "Collection non accessible"
            }))
        }
    }
}