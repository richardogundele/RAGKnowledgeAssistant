"""
Embedding service.
Converts text into dense vectors for semantic similarity search.

Why local embeddings:
- No API calls = lower latency and cost
- Works offline for privacy-sensitive environments
- all-MiniLM-L6-v2 is fast and good quality for general text
"""

from sentence_transformers import SentenceTransformer
import numpy as np

from config import EMBEDDING_MODEL
from models.schemas import DocumentChunk


# Load model once at module level (singleton pattern)
# This avoids reloading the model on every request
_model = None


def get_model() -> SentenceTransformer:
    """
    Lazy-load the embedding model.
    Model is cached after first load for performance.
    """
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def embed_texts(texts: list[str]) -> np.ndarray:
    """
    Convert a list of texts into embeddings.
    Returns numpy array of shape (n_texts, embedding_dim).
    
    Batching is handled internally by sentence-transformers.
    """
    model = get_model()
    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,  # Normalize for cosine similarity
        show_progress_bar=False
    )
    return embeddings


def embed_chunks(chunks: list[DocumentChunk]) -> np.ndarray:
    """
    Embed a list of document chunks.
    Convenience wrapper that extracts text from chunks.
    """
    texts = [chunk.content for chunk in chunks]
    return embed_texts(texts)


def embed_query(query: str) -> np.ndarray:
    """
    Embed a single query string.
    Returns 1D array of shape (embedding_dim,).
    """
    model = get_model()
    embedding = model.encode(
        query,
        convert_to_numpy=True,
        normalize_embeddings=True
    )
    return embedding