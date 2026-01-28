/// Full-Text Search using Tantivy
/// Indexes conversation memory for fast semantic search
use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::path::Path;
use tantivy::collector::TopDocs;
use tantivy::query::QueryParser;
use tantivy::schema::*;
use tantivy::{doc, Index, IndexWriter, ReloadPolicy, TantivyDocument};
use tracing::info;

/// Search index for conversation memory
pub struct SearchIndex {
    index: Index,
    writer: IndexWriter,
    schema: Schema,
    conversation_id: Field,
    user_message: Field,
    bot_response: Field,
    timestamp: Field,
}

/// Search result document
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SearchResult {
    pub conversation_id: String,
    pub user_message: String,
    pub bot_response: String,
    pub timestamp: String,
    pub score: f32,
}

impl SearchIndex {
    /// Create or open search index
    pub fn new<P: AsRef<Path>>(index_path: P) -> Result<Self> {
        // Define schema
        let mut schema_builder = Schema::builder();

        let conversation_id = schema_builder.add_text_field("conversation_id", STRING | STORED);
        let user_message = schema_builder.add_text_field("user_message", TEXT | STORED);
        let bot_response = schema_builder.add_text_field("bot_response", TEXT | STORED);
        let timestamp = schema_builder.add_text_field("timestamp", STRING | STORED);

        let schema = schema_builder.build();

        // Create or open index
        let meta_path = index_path.as_ref().join("meta.json");
        let index = if meta_path.exists() {
            info!("Opening existing search index at {:?}", index_path.as_ref());
            Index::open_in_dir(index_path)?
        } else {
            info!("Creating new search index at {:?}", index_path.as_ref());
            std::fs::create_dir_all(&index_path)?;
            Index::create_in_dir(index_path, schema.clone())?
        };

        // Create index writer (50 MB buffer)
        let writer = index.writer(50_000_000)?;

        info!("Search index initialized successfully");

        Ok(Self {
            index,
            writer,
            schema,
            conversation_id,
            user_message,
            bot_response,
            timestamp,
        })
    }

    /// Index a conversation message
    pub fn index_message(
        &mut self,
        conversation_id: &str,
        user_msg: &str,
        bot_resp: &str,
        timestamp: &str,
    ) -> Result<()> {
        let doc = doc!(
            self.conversation_id => conversation_id,
            self.user_message => user_msg,
            self.bot_response => bot_resp,
            self.timestamp => timestamp,
        );

        self.writer.add_document(doc)?;
        self.writer.commit()?;

        Ok(())
    }

    /// Search conversations
    pub fn search(&self, query_text: &str, limit: usize) -> Result<Vec<SearchResult>> {
        let reader = self.index
            .reader_builder()
            .reload_policy(ReloadPolicy::OnCommitWithDelay)
            .try_into()?;

        let searcher = reader.searcher();

        // Parse query across user_message and bot_response fields
        let query_parser = QueryParser::for_index(
            &self.index,
            vec![self.user_message, self.bot_response],
        );

        let query = query_parser.parse_query(query_text)?;

        // Search and collect top results
        let top_docs = searcher.search(&query, &TopDocs::with_limit(limit))?;

        let mut results = Vec::new();

        for (_score, doc_address) in top_docs {
            let retrieved_doc = searcher.doc::<TantivyDocument>(doc_address)?;

            let conversation_id = retrieved_doc
                .get_first(self.conversation_id)
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string();

            let user_message = retrieved_doc
                .get_first(self.user_message)
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string();

            let bot_response = retrieved_doc
                .get_first(self.bot_response)
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string();

            let timestamp = retrieved_doc
                .get_first(self.timestamp)
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string();

            results.push(SearchResult {
                conversation_id,
                user_message,
                bot_response,
                timestamp,
                score: _score,
            });
        }

        Ok(results)
    }

    /// Delete all documents for a conversation
    pub fn delete_conversation(&mut self, conversation_id: &str) -> Result<()> {
        let term = Term::from_field_text(self.conversation_id, conversation_id);
        self.writer.delete_term(term);
        self.writer.commit()?;
        Ok(())
    }

    /// Get index statistics
    pub fn stats(&self) -> Result<IndexStats> {
        let reader = self.index
            .reader_builder()
            .reload_policy(ReloadPolicy::OnCommitWithDelay)
            .try_into()?;

        let searcher = reader.searcher();
        let num_docs = searcher.num_docs() as u64;

        Ok(IndexStats {
            num_documents: num_docs,
            index_size_bytes: 0, // Tantivy 0.25 doesn't expose cache_info directly
        })
    }
}

/// Index statistics
#[derive(Debug, Serialize)]
pub struct IndexStats {
    pub num_documents: u64,
    pub index_size_bytes: usize,
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::TempDir;

    #[test]
    fn test_search_index() {
        let temp_dir = TempDir::new().unwrap();
        let mut index = SearchIndex::new(temp_dir.path()).unwrap();

        // Index some test messages
        index.index_message(
            "conv-1",
            "What is the weather today?",
            "The weather is sunny and 25 degrees.",
            "2025-01-26T10:00:00Z",
        ).unwrap();

        index.index_message(
            "conv-2",
            "Tell me a joke",
            "Why did the chicken cross the road? To get to the other side!",
            "2025-01-26T11:00:00Z",
        ).unwrap();

        // Search
        let results = index.search("weather", 10).unwrap();
        assert_eq!(results.len(), 1);
        assert_eq!(results[0].conversation_id, "conv-1");

        // Stats
        let stats = index.stats().unwrap();
        assert_eq!(stats.num_documents, 2);
    }
}
