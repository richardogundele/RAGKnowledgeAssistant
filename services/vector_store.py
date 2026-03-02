"""
Vector store service using FAISS.
Handles storing, searching, and persisting document embeddings.

Why FAISS:
- Extremely fast similarity search (millions of vectors in milliseconds)
- Works offline, no external service needed
- Battle-tested by Meta, used in production at scale
"""

import os
import json
import faiss
import numpy as np
from pathlib import Path

from config import VECTOR_STORE_PATH, TOP_K
from models.schemas import DocumentChunk


class VectorStore:
    """
    FAISS-based vector store with metadata persistence.
    
    We store two things:
    1. FAISS index (the vectors)
    2. Metadata JSON (the chunk content/source info)
    
    FAISS only stores vectors, so we maintain a parallel list of chunks.
    """
    
    def __init__(self):
        self.index = None
        self.chunks: list[DocumentChunk] = []
        self.dimension = None
    
    def add_chunks(self, chunks: list[DocumentChunk], embeddings: np.ndarray):
        """
        Add chunks and their embeddings to the store.
        
        Creates a new index if none exists, otherwise adds to existing.
        """
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")
        
        # Get embedding dimension from first vector
        self.dimension = embeddings.shape[1]
        
        # Create index if it doesn't exist
        if self.index is None:
            # IndexFlatIP = Inner Product (dot product) - fast for normalized vectors
            self.index = faiss.IndexFlatIP(self.dimension)
        
        # Add vectors to FAISS
        self.index.add(embeddings.astype(np.float32))
        
        # Store chunk metadata
        self.chunks.extend(chunks)
    
    def search(self, query_embedding: np.ndarray, top_k: int = TOP_K) -> list[tuple[DocumentChunk, float]]:
        """
        Search for most similar chunks to a query.
        
        Returns list of (chunk, similarity_score) tuples, sorted by relevance.
        """
        if self.index is None or self.index.ntotal == 0:
            return []
        
        # Reshape query to 2D array (FAISS requirement)
        query_vector = query_embedding.reshape(1, -1).astype(np.float32)
        
        # Search FAISS index
        # D = distances (similarity scores), I = indices
        scores, indices = self.index.search(query_vector, min(top_k, self.index.ntotal))
        
        # Build results with chunk and score
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0:  # FAISS returns -1 for empty slots
                results.append((self.chunks[idx], float(score)))
        
        return results
    
    def save(self, path: str = VECTOR_STORE_PATH):
        """
        Persist index and metadata to disk.
        Allows reloading without re-embedding all documents.
        """
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        if self.index is not None:
            faiss.write_index(self.index, str(path / "index.faiss"))
        
        # Save chunk metadata as JSON
        chunks_data = [chunk.model_dump() for chunk in self.chunks]
        with open(path / "chunks.json", "w", encoding="utf-8") as f:
            json.dump(chunks_data, f, indent=2)
    
    def load(self, path: str = VECTOR_STORE_PATH) -> bool:
        """
        Load index and metadata from disk.
        Returns True if successful, False if no saved index exists.
        """
        path = Path(path)
        index_path = path / "index.faiss"
        chunks_path = path / "chunks.json"
        
        if not index_path.exists() or not chunks_path.exists():
            return False
        
        # Load FAISS index
        self.index = faiss.read_index(str(index_path))
        
        # Load chunk metadata
        with open(chunks_path, "r", encoding="utf-8") as f:
            chunks_data = json.load(f)
        
        self.chunks = [DocumentChunk(**chunk) for chunk in chunks_data]
        
        return True
    
    def clear(self):
        """
        Clear all data from the store.
        """
        self.index = None
        self.chunks = []
    
    @property
    def count(self) -> int:
        """Number of chunks in the store."""
        return len(self.chunks)


# Global instance for convenience
_store = None


def get_vector_store() -> VectorStore:
    """
    Get or create the global vector store instance.
    """
    global _store
    if _store is None:
        _store = VectorStore()
        # Try to load existing index
        _store.load()
    return _store