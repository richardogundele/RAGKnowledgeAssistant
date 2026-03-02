"""
Pydantic models for request/response validation.
These define the contract between API and internal services.
"""

from pydantic import BaseModel, Field
from typing import Optional


class DocumentChunk(BaseModel):
    """
    A chunk of text extracted from a document.
    Stores both content and provenance (where it came from).
    """
    content: str                          # The actual text
    source: str                           # Filename it came from
    page_number: Optional[int] = None     # Page number (for PDFs)
    chunk_index: int                      # Position in the document


class RetrievedContext(BaseModel):
    """
    A chunk that was retrieved as relevant to a query.
    Includes similarity score for confidence assessment.
    """
    chunk: DocumentChunk
    similarity_score: float               # How relevant (0-1)


class QueryRequest(BaseModel):
    """
    Incoming query from the user.
    """
    question: str = Field(..., min_length=3, description="The user's question")


class QueryResponse(BaseModel):
    """
    Full response including answer, sources, and confidence metadata.
    This transparency is key for hallucination reduction.
    """
    answer: str                           # The generated answer
    sources: list[RetrievedContext]       # What context was used
    confidence: str                       # "high", "medium", "low", or "insufficient"
    retrieval_count: int                  # How many chunks were retrieved
    is_grounded: bool                     # Did we have enough context to answer?


class IngestResponse(BaseModel):
    """
    Response after document ingestion.
    """
    documents_processed: int
    chunks_created: int
    status: str