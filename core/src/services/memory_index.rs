use anyhow::Result;
use std::thread;
use tantivy::schema::*;
use tantivy::{doc, Index, IndexWriter};
use tokio::sync::mpsc;
use tracing::{error, info};

pub enum MemoryCommand {
    AddDocument {
        content: String,
        vector_id: String,
        timestamp: i64,
    },
    #[allow(dead_code)]
    Commit,
}

#[derive(Clone)]
pub struct AsyncMemoryIndex {
    sender: mpsc::Sender<MemoryCommand>,
    index: Index,
    reader: tantivy::IndexReader,
    ollama_client: std::sync::Arc<crate::services::ollama_client::OllamaClient>,
}

impl AsyncMemoryIndex {
    pub fn new<P: AsRef<std::path::Path>>(
        index_path: P,
        ollama_client: std::sync::Arc<crate::services::ollama_client::OllamaClient>,
    ) -> Result<Self> {
        let path = index_path.as_ref();
        let mut schema_builder = Schema::builder();
        let content_field_def = schema_builder.add_text_field("content", TEXT | STORED);
        let vector_id_field_def = schema_builder.add_text_field("vector_id", STRING | STORED);
        let timestamp_field_def = schema_builder.add_i64_field("timestamp", INDEXED | STORED);
        let _schema = schema_builder.build();

        std::fs::create_dir_all(path)?;
        let index = if path.join("meta.json").exists() {
            Index::open_in_dir(path)?
        } else {
            Index::create_in_dir(path, _schema.clone())?
        };

        let schema = index.schema();
        let content_field = schema.get_field("content").unwrap_or(content_field_def);
        let vector_id_field = schema.get_field("vector_id").unwrap_or(vector_id_field_def);
        let timestamp_field = schema.get_field("timestamp").unwrap_or(timestamp_field_def);

        let reader = index
            .reader_builder()
            .reload_policy(tantivy::ReloadPolicy::OnCommitWithDelay)
            .try_into()?;

        let mut writer = index.writer(50_000_000)?;
        let (sender, mut receiver) = mpsc::channel(1024);

        let sender_clone = sender.clone();
        tokio::spawn(async move {
            let mut interval = tokio::time::interval(std::time::Duration::from_secs(5));
            loop {
                interval.tick().await;
                match sender_clone.try_send(MemoryCommand::Commit) {
                    Err(tokio::sync::mpsc::error::TrySendError::Closed(_)) => break,
                    Err(tokio::sync::mpsc::error::TrySendError::Full(_)) => {
                        tracing::warn!("Tantivy channel full: skipping background commit");
                    }
                    Ok(_) => {}
                }
            }
        });

        // The background worker loop must strictly operate inside a blocking context:
        thread::spawn(move || {
            info!("Tantivy MemoryIndex actor started");
            let mut pending_docs = 0;
            while let Some(command) = receiver.blocking_recv() {
                match command {
                    MemoryCommand::AddDocument { content, vector_id, timestamp } => {
                        // Safely catch any panic during doc creation/tokenization
                        let document_result = std::panic::catch_unwind(|| {
                            doc!(
                                content_field => content,
                                vector_id_field => vector_id,
                                timestamp_field => timestamp,
                            )
                        });

                        match document_result {
                            Ok(document) => {
                                if let Err(e) = writer.add_document(document) {
                                    error!("Failed to add document to Tantivy index: {:?}", e);
                                } else {
                                    pending_docs += 1;
                                }
                            }
                            Err(panic_err) => {
                                error!("Panic caught during document building: {:?}", panic_err);
                            }
                        }
                    }
                    MemoryCommand::Commit => {
                        if pending_docs > 0 {
                            if let Err(e) = writer.commit() {
                                error!("Tantivy commit failure: {:?}", e);
                            } else {
                                info!("Tantivy batch commit successful. {} documents committed.", pending_docs);
                                pending_docs = 0;
                            }
                        }
                    }
                }
            }
            info!("Tantivy MemoryIndex actor shut down");
        });

        Ok(Self {
            sender,
            index,
            reader,
            ollama_client,
        })
    }

    pub async fn add_document(&self, content: String, vector_id: String, timestamp: i64) -> Result<()> {
        tokio::time::timeout(
            std::time::Duration::from_secs(2),
            self.sender.send(MemoryCommand::AddDocument {
                content,
                vector_id,
                timestamp,
            })
        )
        .await
        .map_err(|_| anyhow::anyhow!("Timeout: Tantivy Actor queue full"))?
        .map_err(|_| anyhow::anyhow!("Tantivy Actor channel closed"))?;
        Ok(())
    }

    #[allow(dead_code)]
    pub async fn commit(&self) -> Result<()> {
        tokio::time::timeout(
            std::time::Duration::from_secs(2),
            self.sender.send(MemoryCommand::Commit)
        )
        .await
        .map_err(|_| anyhow::anyhow!("Timeout: Tantivy Actor queue full"))?
        .map_err(|_| anyhow::anyhow!("Tantivy Actor channel closed"))?;
        Ok(())
    }

    pub async fn search_context(
        &self,
        query: &str,
        limit: usize,
    ) -> Result<Vec<String>, Box<dyn std::error::Error + Send + Sync>> {
        // Use Tantivy IndexReader to perform a fast top-K full-text search over the historical archive
        info!("Searching local memory index for query: {}", query);
        
        let reader = self.reader.clone();
        let index = self.index.clone();
        let query_owned = query.to_string();
        
        tokio::task::spawn_blocking(move || {
            let searcher = reader.searcher();
            let schema = index.schema();
            let content_field = schema
                .get_field("content")
                .map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)?;
            let timestamp_field = schema
                .get_field("timestamp")
                .map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)?;
                
            let query_parser = tantivy::query::QueryParser::for_index(&index, vec![content_field]);
            let parsed_query = query_parser
                .parse_query(&query_owned)
                .map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)?;
                
            let top_docs = searcher
                .search(&parsed_query, &tantivy::collector::TopDocs::with_limit(limit))
                .map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)?;
                
            let mut results = Vec::new();
            for (_score, doc_address) in top_docs {
                let retrieved_doc = searcher
                    .doc::<tantivy::TantivyDocument>(doc_address)
                    .map_err(|e| Box::new(e) as Box<dyn std::error::Error + Send + Sync>)?;
                    
                let content_str = retrieved_doc
                    .get_first(content_field)
                    .and_then(|v| v.as_str())
                    .unwrap_or("");
                    
                let ts = retrieved_doc
                    .get_first(timestamp_field)
                    .and_then(|v| v.as_i64())
                    .unwrap_or(0);

                use chrono::TimeZone;
                let datetime = chrono::Utc.timestamp_opt(ts, 0).single().unwrap_or_else(chrono::Utc::now);
                let formatted_date = datetime.format("%Y-%m-%d %H:%M").to_string();

                if !content_str.is_empty() {
                    results.push(format!("[{}] {}", formatted_date, content_str));
                }
            }
            
            info!(
                results_count = results.len(),
                "Semantic context retrieval completed successfully"
            );
            
            Ok(results)
        }).await.unwrap_or_else(|e| Err(Box::new(e) as Box<dyn std::error::Error + Send + Sync>))
    }
}
