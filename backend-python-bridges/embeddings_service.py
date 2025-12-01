"""
Service Embeddings - Phase 3 Python Bridges
Vectorisation texte pour mémoire sémantique Qdrant
"""

import numpy as np
from typing import List, Optional
from dataclasses import dataclass
from loguru import logger


@dataclass
class Embedding:
    """Résultat d'embedding"""
    text: str
    vector: np.ndarray  # Array float32
    dimension: int


class EmbeddingsService:
    """Service d'embeddings avec Sentence Transformers"""

    def __init__(self, model_name: str = "distiluse-base-multilingual-cased-v2"):
        """
        Initialiser le service embeddings

        Args:
            model_name: Modèle Sentence Transformers à utiliser
                        - distiluse-base-multilingual-cased-v2 (multilingue, rapide)
                        - all-MiniLM-L6-v2 (compact, anglais)
                        - all-mpnet-base-v2 (meilleure qualité, plus lent)
        """
        self.model_name = model_name
        logger.info(f" Loading embeddings model: {model_name}")

        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
            self.dimension = self.model.get_sentence_embedding_dimension()
            logger.info(f" Embeddings model loaded: {self.dimension}D vectors")
        except ImportError:
            logger.error(" sentence-transformers not installed")
            self.model = None
            self.dimension = 384

    def embed_text(self, text: str) -> Embedding:
        """
        Vectoriser un texte

        Args:
            text: Texte à vectoriser

        Returns:
            Embedding avec vecteur et métadonnées
        """
        if not self.model:
            logger.error(" Embeddings model not available")
            return Embedding(
                text=text,
                vector=np.zeros(self.dimension, dtype=np.float32),
                dimension=self.dimension
            )

        try:
            # Vectoriser
            embedding = self.model.encode(text, convert_to_numpy=True)

            return Embedding(
                text=text,
                vector=embedding.astype(np.float32),
                dimension=len(embedding)
            )

        except Exception as e:
            logger.error(f" Embedding error: {e}")
            return Embedding(
                text=text,
                vector=np.zeros(self.dimension, dtype=np.float32),
                dimension=self.dimension
            )

    def embed_texts(self, texts: List[str]) -> List[Embedding]:
        """
        Vectoriser plusieurs textes (batch)

        Args:
            texts: Liste de textes

        Returns:
            Liste d'Embeddings
        """
        if not self.model:
            logger.error(" Embeddings model not available")
            return [
                Embedding(
                    text=text,
                    vector=np.zeros(self.dimension, dtype=np.float32),
                    dimension=self.dimension
                )
                for text in texts
            ]

        try:
            logger.debug(f" Embedding {len(texts)} texts")

            # Vectoriser batch
            embeddings = self.model.encode(texts, convert_to_numpy=True)

            results = [
                Embedding(
                    text=text,
                    vector=embedding.astype(np.float32),
                    dimension=len(embedding)
                )
                for text, embedding in zip(texts, embeddings)
            ]

            logger.debug(f" Embedded {len(results)} texts")
            return results

        except Exception as e:
            logger.error(f" Batch embedding error: {e}")
            return [
                Embedding(
                    text=text,
                    vector=np.zeros(self.dimension, dtype=np.float32),
                    dimension=self.dimension
                )
                for text in texts
            ]

    def similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculer similarité cosinus entre deux vecteurs

        Args:
            vec1, vec2: Vecteurs d'embeddings

        Returns:
            Score similarité (0.0 à 1.0)
        """
        try:
            # Normaliser
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            # Similarité cosinus
            similarity = np.dot(vec1, vec2) / (norm1 * norm2)
            return float(similarity)

        except Exception as e:
            logger.error(f" Similarity calculation error: {e}")
            return 0.0


# Instance globale
_embeddings_service: Optional[EmbeddingsService] = None


def get_embeddings_service(model_name: str = "distiluse-base-multilingual-cased-v2") -> EmbeddingsService:
    """Obtenir instance singleton"""
    global _embeddings_service
    if _embeddings_service is None:
        _embeddings_service = EmbeddingsService(model_name=model_name)
    return _embeddings_service


def init_embeddings(model_name: str = "distiluse-base-multilingual-cased-v2"):
    """Initialiser avec modèle personnalisé"""
    global _embeddings_service
    _embeddings_service = EmbeddingsService(model_name=model_name)
