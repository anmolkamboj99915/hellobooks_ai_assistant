import pickle
import logging
import numpy as np
import faiss
from typing import List

from .config import VECTOR_STORE_PATH, TOP_K_RESULTS


# --------------------------------------------------
# Logging
# --------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --------------------------------------------------
# Retriever Class
# --------------------------------------------------

class Retriever:
    """
    Handles similarity search using FAISS.
    """

    def __init__(self):
        try:
            self.index_path = VECTOR_STORE_PATH / "faiss_index.bin"
            self.metadata_path = VECTOR_STORE_PATH / "documents.pkl"

            # Validate index file
            if not self.index_path.exists():
                raise FileNotFoundError(
                    f"FAISS index not found at {self.index_path}. "
                    "Run the indexing script first."
                )

            # Validate metadata file
            if not self.metadata_path.exists():
                raise FileNotFoundError(
                    f"Document metadata not found at {self.metadata_path}. "
                    "Run the indexing script first."
                )

            logger.info("Loading FAISS index...")
            self.index = faiss.read_index(str(self.index_path))

            logger.info("Loading document metadata...")
            with open(self.metadata_path, "rb") as f:
                self.documents = pickle.load(f)

            if not isinstance(self.documents, list):
                raise RuntimeError("Invalid metadata format: documents must be a list.")

            logger.info("Retriever initialized successfully.")

        except Exception as e:
            logger.error(f"Failed to initialize retriever: {e}")
            raise RuntimeError(f"Retriever initialization failed: {e}")

    # --------------------------------------------------

    def search(self, query_embedding: List[float]) -> List[str]:
        """
        Perform similarity search using FAISS.
        """

        if not query_embedding or not isinstance(query_embedding, list):
            raise ValueError("Query embedding must be a non-empty list.")

        try:

            # Convert query to FAISS compatible format
            query_vector = np.array([query_embedding], dtype="float32")

            if query_vector.ndim != 2:
                raise ValueError("Invalid query embedding shape.")

            distances, indices = self.index.search(query_vector, TOP_K_RESULTS)

            results = []

            for idx in indices[0]:

                # Skip invalid FAISS indices
                if idx < 0:
                    continue

                if idx < len(self.documents):
                    results.append(self.documents[idx])

            return results

        except Exception as e:
            logger.error(f"Error during vector search: {e}")
            raise RuntimeError(f"Vector search failed: {e}")