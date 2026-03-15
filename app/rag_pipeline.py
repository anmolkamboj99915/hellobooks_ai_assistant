import logging
from typing import List

from .embedder import Embedder
from .retriever import Retriever
from .llm import LLMClient


# --------------------------------------------------
# Logging Configuration
# --------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --------------------------------------------------
# RAG Pipeline
# --------------------------------------------------

class RAGPipeline:
    """
    Orchestrates the Retrieval-Augmented Generation workflow.
    """

    def __init__(self):
        try:
            logger.info("Initializing RAG pipeline components...")

            self.embedder = Embedder()
            self.retriever = Retriever()
            self.llm = LLMClient()

            logger.info("RAG pipeline initialized successfully.")

        except Exception as e:
            logger.error(f"Failed to initialize RAG pipeline: {e}")
            raise RuntimeError(f"Pipeline initialization error: {e}")

    # --------------------------------------------------

    def ask(self, question: str) -> str:
        """
        Processes a user question through the RAG pipeline.
        """

        # ------------------------------
        # Input validation
        # ------------------------------

        if not isinstance(question, str) or not question.strip():
            raise ValueError("Question must be a non-empty string.")

        try:

            # ------------------------------
            # Step 1: Embed question
            # ------------------------------

            logger.info("Embedding user question...")
            query_embedding = self.embedder.embed_text(question)

            if not query_embedding or not isinstance(query_embedding, list):
                raise RuntimeError("Embedding generation returned invalid result.")

            # ------------------------------
            # Step 2: Retrieve documents
            # ------------------------------

            logger.info("Retrieving relevant documents...")
            retrieved_docs = self.retriever.search(query_embedding)

            if not retrieved_docs:
                logger.warning("No documents retrieved for query.")
                return "I could not find relevant information in the knowledge base."

            if not isinstance(retrieved_docs, list):
                raise RuntimeError("Retriever returned invalid document format.")

            # ------------------------------
            # Step 3: Generate answer
            # ------------------------------

            logger.info("Generating response from LLM...")
            answer = self.llm.generate_answer(question, retrieved_docs)

            if not answer or not isinstance(answer, str):
                raise RuntimeError("LLM returned an invalid response.")

            return answer.strip()

        except Exception as e:
            logger.error(f"Error in RAG pipeline: {e}")
            raise RuntimeError(f"Failed to process question: {e}")