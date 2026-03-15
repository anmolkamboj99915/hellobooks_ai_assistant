import os
from pathlib import Path
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# --------------------------------------------------
# Base Directory
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

ENV_FILE = BASE_DIR / ".env"

if ENV_FILE.exists():
    load_dotenv(ENV_FILE)
    logger.info(".env configuration loaded.")
else:
    raise FileNotFoundError(
        f".env file not found at expected location: {ENV_FILE}"
    )

# --------------------------------------------------
# API Configuration
# --------------------------------------------------

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    logger.warning(
        "OPENAI_API_KEY not found. OpenAI provider disabled. "
        "Fallback providers may be used."
    )

# --------------------------------------------------
# Project Paths
# --------------------------------------------------

KNOWLEDGE_BASE_PATH = BASE_DIR / "knowledge_base"
VECTOR_STORE_PATH = BASE_DIR / "vector_store"

# Validate knowledge base
if not KNOWLEDGE_BASE_PATH.exists():
    raise FileNotFoundError(
        f"Knowledge base directory not found: {KNOWLEDGE_BASE_PATH}"
    )

# Ensure vector store exists
VECTOR_STORE_PATH.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# Model Configuration
# --------------------------------------------------

# Embedding model for document vectors
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# LLM model for answering questions
LLM_MODEL_NAME = "gpt-4o-mini"

# Number of retrieved documents
TOP_K_RESULTS = 3

# --------------------------------------------------
# Debug / Info Helper
# --------------------------------------------------

def print_config_summary():
    """
    Prints configuration summary for debugging.
    """

    print("\n----- Configuration Loaded -----")
    print(f"Base Directory: {BASE_DIR}")
    print(f"Knowledge Base Path: {KNOWLEDGE_BASE_PATH}")
    print(f"Vector Store Path: {VECTOR_STORE_PATH}")
    print(f"Embedding Model: {EMBEDDING_MODEL_NAME}")
    print(f"LLM Model: {LLM_MODEL_NAME}")
    print(f"Top K Retrieval: {TOP_K_RESULTS}")
    print("--------------------------------\n")