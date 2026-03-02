"""
Configuration constants for the RAG system.
These are tunable parameters that affect retrieval quality and hallucination risk.
"""

# Chunking parameters
CHUNK_SIZE = 512          # Number of characters per chunk
CHUNK_OVERLAP = 50        # Overlap between chunks to preserve context

# Embedding model (runs locally via sentence-transformers)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Retrieval parameters
TOP_K = 5                         # Number of chunks to retrieve
SIMILARITY_THRESHOLD = 0.3        # Minimum similarity score (0-1). Below this = "I don't know"

# LLM parameters
OLLAMA_MODEL = "llama3.2"         # Or "mistral" - whatever you have downloaded
LLM_TEMPERATURE = 0.1             # Low temperature = less creative = fewer hallucinations

# Paths
VECTOR_STORE_PATH = "data/faiss_index"
DOCUMENTS_PATH = "data/sample_docs"