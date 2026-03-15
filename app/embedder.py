from sentence_transformers import SentenceTransformer
from typing import List
import logging
import numpy as np

from .config import EMBEDDING_MODEL_NAME

# --------------------------------------------------
# Logging Configuration
# --------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --------------------------------------------------
# Embedder Class
# --------------------------------------------------

class Embedder:
    """
    Handles text embedding generation using SentenceTransformers.
    Ensures embeddings are FAISS compatible (float32).
    """

    def __init__(self):
        try:
            logger.info(f"Loading embedding model: {EMBEDDING_MODEL_NAME}")
            self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        except Exception as e:
            logger.error("Failed to load embedding model.")
            raise RuntimeError(f"Embedding model initialization failed: {e}")

    # --------------------------------------------------

    def embed_text(self, text: str) -> List[float]:
        """
        Convert a single text string into an embedding vector.
        """

        if not isinstance(text, str) or not text.strip():
            raise ValueError("Input text must be a non-empty string.")

        try:

            embedding = self.model.encode(
                text,
                convert_to_numpy=True
            )

            # Ensure FAISS compatible dtype
            embedding = embedding.astype("float32")

            return embedding.tolist()

        except Exception as e:
            logger.error("Error generating embedding for text.")
            raise RuntimeError(f"Embedding generation failed: {e}")

    # --------------------------------------------------

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple documents.
        """

        if not documents:
            raise ValueError("Document list cannot be empty.")

        if not all(isinstance(doc, str) and doc.strip() for doc in documents):
            raise ValueError("All documents must be valid non-empty strings.")

        try:

            embeddings = self.model.encode(
                documents,
                convert_to_numpy=True,
                batch_size=32,
                show_progress_bar=False
            )

            # Ensure FAISS compatible dtype
            embeddings = embeddings.astype("float32")

            return embeddings.tolist()

        except Exception as e:
            logger.error("Error generating embeddings for document batch.")
            raise RuntimeError(f"Batch embedding failed: {e}")