"""
Text chunking service.
Splits documents into overlapping chunks for embedding and retrieval.

Why chunking matters:
- Embedding models have token limits (typically 512 tokens)
- Smaller chunks = more precise retrieval
- Overlap ensures context isn't lost at boundaries
"""

from models.schemas import DocumentChunk
from config import CHUNK_SIZE, CHUNK_OVERLAP


def chunk_documents(documents: list[dict]) -> list[DocumentChunk]:
    """
    Split documents into overlapping chunks.
    Preserves source metadata for each chunk.
    """
    all_chunks = []
    
    for doc in documents:
        chunks = _create_chunks(
            text=doc["content"],
            source=doc["source"],
            page_number=doc.get("page_number")
        )
        all_chunks.extend(chunks)
    
    return all_chunks


def _create_chunks(
    text: str, 
    source: str, 
    page_number: int | None
) -> list[DocumentChunk]:
    """
    Split text into overlapping chunks.
    
    Strategy: Fixed-size chunks with overlap.
    - Simple and predictable
    - Overlap prevents losing context at chunk boundaries
    
    Interview note: More sophisticated approaches exist (semantic chunking,
    sentence-boundary chunking) but fixed-size is reliable and explainable.
    """
    chunks = []
    start = 0
    chunk_index = 0
    
    while start < len(text):
        # Calculate end position
        end = start + CHUNK_SIZE
        
        # Extract chunk text
        chunk_text = text[start:end]
        
        # Only create chunk if it has meaningful content
        if chunk_text.strip():
            chunks.append(DocumentChunk(
                content=chunk_text.strip(),
                source=source,
                page_number=page_number,
                chunk_index=chunk_index
            ))
            chunk_index += 1
        
        # Move start position (with overlap)
        start = end - CHUNK_OVERLAP
        
        # Prevent infinite loop on very small texts
        if start >= len(text) - CHUNK_OVERLAP:
            break
    
    return chunks


def get_chunk_stats(chunks: list[DocumentChunk]) -> dict:
    """
    Return statistics about chunking for debugging/logging.
    Useful for tuning chunk parameters.
    """
    if not chunks:
        return {"count": 0, "avg_length": 0, "sources": []}
    
    lengths = [len(c.content) for c in chunks]
    sources = list(set(c.source for c in chunks))
    
    return {
        "count": len(chunks),
        "avg_length": sum(lengths) // len(lengths),
        "min_length": min(lengths),
        "max_length": max(lengths),
        "sources": sources
    }