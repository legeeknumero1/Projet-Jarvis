/// Search Service - Full-text search avec Tantivy
use tantivy::schema::*;
use tantivy::{Index, Term};
use tracing::{info, debug};

use crate::models::*;
use crate::error::{DbError, DbResult};

pub struct SearchService {
    index: Index,
    schema: Schema,
}

impl SearchService {
    /// Créer nouveau service search
    pub async fn new() -> DbResult<Self> {
        info!(" Initializing Tantivy search index");

        // Créer schema
        let mut schema_builder = Schema::builder();
        schema_builder.add_text_field("id", STRING | STORED);
        schema_builder.add_text_field("content", TEXT | STORED);
        schema_builder.add_text_field("source", STRING | STORED);
        schema_builder.add_text_field("source_id", STRING | STORED);
        schema_builder.add_i64_field("created_at", STORED);

        let schema = schema_builder.build();

        // Créer index en mémoire
        let index = Index::create_in_ram(schema.clone());

        info!(" Tantivy index initialized");

        Ok(Self { index, schema })
    }

    /// Vérifier la santé
    pub async fn health_check(&self) -> DbResult<bool> {
        // Tantivy est en-mémoire, donc toujours healthy
        Ok(true)
    }

    // ========== INDEXING ==========

    /// Indexer un chunk de texte
    pub async fn index_chunk(&self, chunk: TextChunk) -> DbResult<()> {
        debug!("Indexing chunk: {}", chunk.id);

        let mut index_writer = self.index
            .writer(50_000_000)
            .map_err(|e| DbError::Search(e.to_string()))?;

        let mut document = tantivy::TantivyDocument::new();
        let id_field = self.schema.get_field("id").unwrap();
        let content_field = self.schema.get_field("content").unwrap();
        let source_field = self.schema.get_field("source").unwrap();
        let source_id_field = self.schema.get_field("source_id").unwrap();
        let created_at_field = self.schema.get_field("created_at").unwrap();

        document.add_text(id_field, &chunk.id);
        document.add_text(content_field, &chunk.content);
        document.add_text(source_field, &chunk.source);
        document.add_text(source_id_field, &chunk.source_id);
        document.add_i64(created_at_field, chunk.created_at.timestamp());

        index_writer.add_document(document)
            .map_err(|e| DbError::Search(e.to_string()))?;

        index_writer.commit()
            .map_err(|e| DbError::Search(e.to_string()))?;

        info!(" Chunk indexed: {}", chunk.id);
        Ok(())
    }

    /// Indexer plusieurs chunks en batch
    pub async fn index_batch(&self, chunks: Vec<TextChunk>) -> DbResult<usize> {
        debug!("Batch indexing {} chunks", chunks.len());

        let mut index_writer = self.index
            .writer(50_000_000)
            .map_err(|e| DbError::Search(e.to_string()))?;

        let id_field = self.schema.get_field("id").unwrap();
        let content_field = self.schema.get_field("content").unwrap();
        let source_field = self.schema.get_field("source").unwrap();
        let source_id_field = self.schema.get_field("source_id").unwrap();
        let created_at_field = self.schema.get_field("created_at").unwrap();

        for chunk in chunks.iter() {
            let mut document = tantivy::TantivyDocument::new();
            document.add_text(id_field, &chunk.id);
            document.add_text(content_field, &chunk.content);
            document.add_text(source_field, &chunk.source);
            document.add_text(source_id_field, &chunk.source_id);
            document.add_i64(created_at_field, chunk.created_at.timestamp());

            index_writer.add_document(document)
                .map_err(|e| DbError::Search(e.to_string()))?;
        }

        index_writer.commit()
            .map_err(|e| DbError::Search(e.to_string()))?;

        info!(" Batch indexed chunks");
        Ok(chunks.len())
    }

    // ========== SEARCHING ==========

    /// Rechercher par texte
    pub async fn search(&self, query_str: &str, limit: usize) -> DbResult<Vec<SearchResult>> {
        debug!("Searching for: {}", query_str);

        let searcher = self.index
            .reader()
            .map_err(|e| DbError::Search(e.to_string()))?
            .searcher();

        let query_parser = tantivy::query::QueryParser::for_index(
            &self.index,
            vec![
                self.schema.get_field("content").unwrap(),
                self.schema.get_field("source").unwrap(),
            ],
        );

        let query = query_parser
            .parse_query(query_str)
            .map_err(|e| DbError::Search(e.to_string()))?;

        let top_docs = searcher
            .search(&query, &tantivy::collector::TopDocs::with_limit(limit))
            .map_err(|e| DbError::Search(e.to_string()))?;

        let id_field = self.schema.get_field("id").unwrap();
        let content_field = self.schema.get_field("content").unwrap();
        let source_field = self.schema.get_field("source").unwrap();

        let mut results = Vec::new();

        for (_score, doc_address) in top_docs {
            let retrieved_doc: tantivy::TantivyDocument = searcher
                .doc(doc_address)
                .map_err(|e| DbError::Search(e.to_string()))?;

            let id = retrieved_doc
                .get_first(id_field)
                .and_then(|f| f.as_str().map(String::from))
                .unwrap_or_default();

            let content = retrieved_doc
                .get_first(content_field)
                .and_then(|f| f.as_str().map(String::from))
                .unwrap_or_default();

            let source = retrieved_doc
                .get_first(source_field)
                .and_then(|f| f.as_str().map(String::from))
                .unwrap_or_default();

            results.push(SearchResult {
                id,
                content,
                score: 0.0,  // Tantivy ne donne pas de score normalisé
                source,
                created_at: chrono::Utc::now(),
                metadata: None,
            });
        }

        info!(" Found {} results", results.len());
        Ok(results)
    }

    /// Supprimer un document du index
    pub async fn delete(&self, id: &str) -> DbResult<()> {
        debug!("Deleting document: {}", id);

        let mut index_writer = self.index
            .writer::<tantivy::TantivyDocument>(50_000_000)
            .map_err(|e| DbError::Search(e.to_string()))?;

        let id_field = self.schema.get_field("id").unwrap();
        let term = Term::from_field_text(id_field, id);
        index_writer.delete_term(term);

        index_writer.commit()
            .map_err(|e| DbError::Search(e.to_string()))?;

        info!(" Document deleted: {}", id);
        Ok(())
    }

    /// Compter les documents dans l'index
    pub async fn count(&self) -> DbResult<u64> {
        let searcher = self.index
            .reader()
            .map_err(|e| DbError::Search(e.to_string()))?
            .searcher();

        let query = tantivy::query::AllQuery;
        let count: usize = searcher
            .search(&query, &tantivy::collector::Count)
            .map_err(|e| DbError::Search(e.to_string()))?;

        Ok(count as u64)
    }

    /// Clear tous les documents
    pub async fn clear(&self) -> DbResult<()> {
        let mut index_writer = self.index
            .writer::<tantivy::TantivyDocument>(50_000_000)
            .map_err(|e| DbError::Search(e.to_string()))?;

        index_writer.delete_all_documents()
            .map_err(|e| DbError::Search(e.to_string()))?;

        index_writer.commit()
            .map_err(|e| DbError::Search(e.to_string()))?;

        info!(" Index cleared");
        Ok(())
    }
}
