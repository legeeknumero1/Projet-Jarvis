//! Service de chat pour Jarvis Rust Backend
//! 
//! Orchestrateur principal pour les conversations avec l'IA
//! Gère la logique métier, mémoire contextuelle et coordination des services

use chrono::{DateTime, Utc};
use std::sync::Arc;
use uuid::Uuid;

use crate::{
    config::AppConfig,
    models::{
        GetHistoryResponse, Message, MessageRole, SendMessageRequest, SendMessageResponse,
        TokenUsage, Conversation,
    },
    services::{DatabaseService, LLMService, MemoryService, VoiceService},
};

/// Service de chat principal
#[derive(Clone)]
pub struct ChatService {
    config: Arc<AppConfig>,
    llm: Arc<LLMService>,
    memory: Arc<MemoryService>,
    voice: Arc<VoiceService>,
    database: Arc<DatabaseService>,
}

/// Erreurs spécifiques au service de chat
#[derive(Debug, thiserror::Error)]
pub enum ChatError {
    #[error("Timeout LLM: {0}s")]
    LLMTimeout(u64),
    
    #[error("Erreur LLM: {0}")]
    LLMError(String),
    
    #[error("Erreur mémoire: {0}")]
    MemoryError(String),
    
    #[error("Erreur base de données: {0}")]
    DatabaseError(String),
    
    #[error("Validation: {0}")]
    ValidationError(String),
}

impl ChatService {
    /// Initialise le service de chat
    pub async fn new(
        config: &AppConfig,
        llm: &Arc<LLMService>,
        memory: &Arc<MemoryService>,
        voice: &Arc<VoiceService>,
    ) -> anyhow::Result<Self> {
        // Note: DatabaseService sera injecté via AppServices
        Ok(Self {
            config: Arc::new(config.clone()),
            llm: llm.clone(),
            memory: memory.clone(),
            voice: voice.clone(),
            database: Arc::new(DatabaseService::new(config).await?), // Temporaire
        })
    }

    /// Traite un message utilisateur complet
    pub async fn process_message(
        &self,
        request: SendMessageRequest,
    ) -> anyhow::Result<SendMessageResponse> {
        let start_time = std::time::Instant::now();

        // Validation du message
        if request.message.trim().is_empty() {
            return Err(ChatError::ValidationError("Message vide".to_string()).into());
        }

        tracing::info!("💬 Traitement message: {} caractères", request.message.len());

        // 1. Obtenir ou créer une conversation
        let conversation_id = match request.conversation_id {
            Some(id) => {
                // Vérifier que la conversation existe
                match self.database.get_conversation(id).await? {
                    Some(_) => id,
                    None => {
                        tracing::warn!("Conversation {} introuvable, création d'une nouvelle", id);
                        self.database.create_conversation(None, None).await?.id
                    }
                }
            }
            None => {
                // Créer une nouvelle conversation
                self.database.create_conversation(None, None).await?.id
            }
        };

        // 2. Sauvegarder le message utilisateur
        let user_message = self.database.create_message(
            conversation_id,
            MessageRole::User,
            request.message.clone(),
            None,
        ).await.map_err(|e| ChatError::DatabaseError(e.to_string()))?;

        // 3. Récupérer le contexte de la conversation
        let context = self.build_conversation_context(conversation_id, &request.message).await?;

        // 4. Générer la réponse avec l'IA
        let llm_response = self.llm.generate(
            context,
            request.model,
            request.temperature,
            request.max_tokens,
        ).await.map_err(|e| ChatError::LLMError(e.to_string()))?;

        // 5. Sauvegarder la réponse de l'assistant
        let assistant_message = self.database.create_message(
            conversation_id,
            MessageRole::Assistant,
            llm_response.content.clone(),
            Some(serde_json::json!({
                "tokens_used": llm_response.usage.total_tokens,
                "response_time_ms": llm_response.response_time_ms,
                "model_name": llm_response.model,
                "temperature": request.temperature
            })),
        ).await.map_err(|e| ChatError::DatabaseError(e.to_string()))?;

        // 6. Mettre à jour la mémoire contextuelle
        self.update_memory(conversation_id, &request.message, &llm_response.content).await?;

        let total_response_time = start_time.elapsed().as_millis() as u64;

        tracing::info!(
            "✅ Message traité en {}ms - {} tokens",
            total_response_time,
            llm_response.usage.total_tokens
        );

        Ok(SendMessageResponse {
            message: assistant_message,
            conversation_id,
            usage: TokenUsage {
                prompt_tokens: llm_response.usage.prompt_tokens,
                completion_tokens: llm_response.usage.completion_tokens,
                total_tokens: llm_response.usage.total_tokens,
            },
            response_time_ms: total_response_time,
        })
    }

    /// Construit le contexte de conversation pour l'IA
    async fn build_conversation_context(
        &self,
        conversation_id: Uuid,
        current_message: &str,
    ) -> anyhow::Result<String> {
        // 1. Récupérer l'historique récent de la conversation
        let recent_messages = self.database.get_messages(
            conversation_id,
            10, // Derniers 10 messages pour le contexte
            0,
            None,
        ).await.map_err(|e| ChatError::DatabaseError(e.to_string()))?;

        // 2. Récupérer la mémoire contextuelle pertinente
        let relevant_memories = self.memory.search_relevant_context(
            current_message,
            5, // Top 5 souvenirs pertinents
        ).await.map_err(|e| ChatError::MemoryError(e.to_string()))?;

        // 3. Construire le prompt avec contexte
        let mut context = String::new();
        
        // Instructions système
        context.push_str("Tu es Jarvis, un assistant IA personnel intelligent et serviable. ");
        context.push_str("Tu réponds en français de manière naturelle et conversationnelle.\n\n");

        // Ajouter la mémoire contextuelle si disponible
        if !relevant_memories.is_empty() {
            context.push_str("Contexte pertinent de nos conversations précédentes:\n");
            for memory in relevant_memories {
                context.push_str(&format!("- {}\n", memory.content));
            }
            context.push_str("\n");
        }

        // Ajouter l'historique de conversation
        if !recent_messages.is_empty() {
            context.push_str("Historique de la conversation:\n");
            for message in recent_messages {
                let role = match message.role {
                    MessageRole::User => "Utilisateur",
                    MessageRole::Assistant => "Jarvis",
                    MessageRole::System => "Système",
                };
                context.push_str(&format!("{}: {}\n", role, message.content));
            }
            context.push_str("\n");
        }

        // Message actuel
        context.push_str(&format!("Utilisateur: {}\nJarvis:", current_message));

        tracing::debug!("📝 Contexte construit: {} caractères", context.len());
        Ok(context)
    }

    /// Met à jour la mémoire contextuelle
    async fn update_memory(
        &self,
        conversation_id: Uuid,
        user_message: &str,
        assistant_response: &str,
    ) -> anyhow::Result<()> {
        // Stocker l'échange complet dans la mémoire vectorielle
        let exchange = format!("Utilisateur: {}\nJarvis: {}", user_message, assistant_response);
        
        self.memory.store_memory(
            exchange,
            Some(conversation_id),
            vec!["conversation".to_string()],
            0.8, // Importance élevée pour les conversations récentes
        ).await.map_err(|e| ChatError::MemoryError(e.to_string()))?;

        Ok(())
    }

    /// Récupère l'historique d'une conversation
    pub async fn get_conversation_history(
        &self,
        conversation_id: Option<Uuid>,
        limit: u32,
        offset: u32,
        since: Option<DateTime<Utc>>,
    ) -> anyhow::Result<GetHistoryResponse> {
        match conversation_id {
            Some(id) => {
                // Historique d'une conversation spécifique
                let messages = self.database.get_messages(id, limit, offset, since)
                    .await.map_err(|e| ChatError::DatabaseError(e.to_string()))?;
                
                let conversation = self.database.get_conversation(id)
                    .await.map_err(|e| ChatError::DatabaseError(e.to_string()))?;
                
                let total_count = self.database.count_messages(id)
                    .await.map_err(|e| ChatError::DatabaseError(e.to_string()))?;
                
                Ok(GetHistoryResponse {
                    messages,
                    conversation,
                    total_count,
                    has_more: total_count > (offset as u64 + limit as u64),
                })
            }
            None => {
                // Pas d'historique global pour l'instant
                Ok(GetHistoryResponse {
                    messages: vec![],
                    conversation: None,
                    total_count: 0,
                    has_more: false,
                })
            }
        }
    }

    /// Supprime une conversation
    pub async fn delete_conversation(&self, conversation_id: Uuid) -> anyhow::Result<u64> {
        self.database.delete_conversation(conversation_id)
            .await.map_err(|e| ChatError::DatabaseError(e.to_string()).into())
    }

    /// Liste toutes les conversations
    pub async fn list_conversations(
        &self,
        limit: u32,
        offset: u32,
    ) -> anyhow::Result<Vec<Conversation>> {
        self.database.list_conversations(limit, offset)
            .await.map_err(|e| ChatError::DatabaseError(e.to_string()).into())
    }
}