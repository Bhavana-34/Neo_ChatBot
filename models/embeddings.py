import os
import sys
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.config import EMBEDDING_MODEL

logger = logging.getLogger(__name__)


def get_embedding_model():
    """Initialize and return the HuggingFace embedding model for RAG"""
    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings

        embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        logger.info(f"Embedding model loaded: {EMBEDDING_MODEL}")
        return embeddings

    except Exception as e:
        logger.error(f"Failed to initialize embedding model: {e}")
        return None
